#!/usr/bin/env python3
"""Synchronize Hugo Markdown content to a Dify knowledge base."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
import yaml
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = PROJECT_ROOT / "content"
STATE_PATH = PROJECT_ROOT / ".rag-sync-state.json"
REQUEST_TIMEOUT_SECONDS = 30
PAGE_SIZE = 100

# Dify Cloud's Sandbox plan allows 10 knowledge base requests per minute.
# When that limit is hit, wait for the window to reset and try again.
RATE_LIMIT_WAIT_SECONDS = 60
MAX_RATE_LIMIT_RETRIES = 3

# Paths are relative to content/. Add exact paths here, or extend is_excluded()
# with another rule when more content types should be omitted.
EXCLUDED_PATHS: set[str] = set()
EXCLUDED_FILENAMES = {"_index.md"}

# Chapter navigation (the numbered links at the top and the Previous/Next
# buttons at the bottom) only means something on the web page. In the
# knowledge base it is noise that the model can mix into the wrong answer.
NAVIGATION_BLOCK = re.compile(
    r'<div class="exam-portfolio-(?:nav|pagination)"[^>]*>.*?</div>[ \t]*\n?',
    re.DOTALL,
)


class DifyApiError(RuntimeError):
    """An error returned by, or encountered while calling, the Dify API."""

    def __init__(self, status: int | None, message: str) -> None:
        super().__init__(message)
        self.status = status


@dataclass(frozen=True)
class LocalDocument:
    path: Path
    name: str


@dataclass
class SyncCounts:
    created: int = 0
    updated: int = 0
    skipped: int = 0
    failed: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync Hugo Markdown files in content/ to a Dify knowledge base."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Determine CREATE/UPDATE/SKIP actions without changing Dify or state.",
    )
    return parser.parse_args()


def split_front_matter(markdown: str) -> tuple[dict[str, Any], str]:
    """Split a document into its YAML front matter (as a dict) and its body."""
    if markdown.startswith("\ufeff"):
        markdown = markdown[1:]

    lines = markdown.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return {}, markdown

    for index, line in enumerate(lines[1:], start=1):
        if line.rstrip("\r\n") == "---":
            body = "".join(lines[index + 1 :]).lstrip("\r\n")
            try:
                metadata = yaml.safe_load("".join(lines[1:index]))
            except yaml.YAMLError:
                metadata = None
            return (metadata if isinstance(metadata, dict) else {}), body

    # An unclosed delimiter is ordinary content, not valid front matter.
    return {}, markdown


def strip_yaml_front_matter(markdown: str) -> str:
    """Remove a YAML front matter block only when it starts the document."""
    return split_front_matter(markdown)[1]


def remove_navigation_blocks(body: str) -> str:
    """Remove chapter navigation HTML that only makes sense on the website."""
    cleaned = NAVIGATION_BLOCK.sub("", body)
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip("\n") + "\n"


def section_titles(relative_path: Path, content_root: Path) -> list[str]:
    """Titles of the _index.md pages above a document, outermost first."""
    titles: list[str] = []
    for folder in reversed(relative_path.parents):
        if folder == Path("."):
            continue  # The home page is not a section.
        index_file = content_root / folder / "_index.md"
        if not index_file.is_file():
            continue
        try:
            metadata, _ = split_front_matter(index_file.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError):
            continue
        title = metadata.get("title")
        if isinstance(title, str) and title.strip():
            titles.append(title.strip())
    return titles


def build_document_text(
    metadata: dict[str, Any], body: str, sections: list[str]
) -> str:
    """Put a short context header on top of the body.

    The front matter is stripped before upload, so without this header a chunk
    would not know which page or project it came from.
    """
    header: list[str] = []
    title = metadata.get("title")
    if isinstance(title, str) and title.strip():
        header.append(f"Title: {title.strip()}")
    if sections:
        header.append(f"Section: {' > '.join(sections)}")
    tags = metadata.get("tags")
    if isinstance(tags, str):
        tags = [tags]
    if isinstance(tags, list):
        tag_names = [str(tag).strip() for tag in tags if str(tag).strip()]
        if tag_names:
            header.append(f"Tags: {', '.join(tag_names)}")

    if not header:
        return body
    return "\n".join(header) + "\n\n" + body


def is_excluded(relative_path: Path) -> bool:
    name = relative_path.as_posix()
    return name in EXCLUDED_PATHS or relative_path.name in EXCLUDED_FILENAMES


def find_markdown_files() -> tuple[list[LocalDocument], list[LocalDocument]]:
    included: list[LocalDocument] = []
    excluded: list[LocalDocument] = []

    for path in sorted(CONTENT_ROOT.rglob("*.md")):
        relative = path.relative_to(CONTENT_ROOT)
        document = LocalDocument(path=path, name=relative.as_posix())
        (excluded if is_excluded(relative) else included).append(document)

    return included, excluded


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {"version": 1, "documents": {}}

    try:
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"WARNING: Ignoring invalid {STATE_PATH.name}: {error}")
        return {"version": 1, "documents": {}}

    if state.get("version") != 1 or not isinstance(state.get("documents"), dict):
        print(f"WARNING: Ignoring unsupported {STATE_PATH.name} format.")
        return {"version": 1, "documents": {}}
    return state


def save_state(state: dict[str, Any]) -> None:
    serialized = json.dumps(state, indent=2, sort_keys=True) + "\n"
    temporary_path = STATE_PATH.with_suffix(STATE_PATH.suffix + ".tmp")
    temporary_path.write_text(serialized, encoding="utf-8")
    temporary_path.replace(STATE_PATH)


def api_base_url(base_url: str) -> str:
    normalized = base_url.strip().rstrip("/")
    if normalized.endswith("/v1"):
        return normalized
    return f"{normalized}/v1"


def is_rate_limited(status: int, message: str) -> bool:
    """Dify Cloud answers 403 (not 429) when the knowledge base limit is hit."""
    return status == 429 or (status == 403 and "rate limit" in message.lower())


def response_error_message(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        payload = None

    if isinstance(payload, dict):
        message = payload.get("message") or payload.get("error") or payload.get("code")
        if message:
            return str(message)

    text = response.text.strip()
    return text[:500] if text else response.reason or "Unknown Dify API error"


class DifyClient:
    def __init__(self, base_url: str, dataset_id: str, api_key: str) -> None:
        self.base_url = api_base_url(base_url)
        self.dataset_id = dataset_id
        self.sleep = time.sleep
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        attempt = 0
        while True:
            try:
                response = self.session.request(
                    method,
                    f"{self.base_url}{path}",
                    timeout=REQUEST_TIMEOUT_SECONDS,
                    **kwargs,
                )
            except requests.RequestException as error:
                raise DifyApiError(None, str(error)) from error

            if response.ok:
                break

            message = response_error_message(response)
            if (
                is_rate_limited(response.status_code, message)
                and attempt < MAX_RATE_LIMIT_RETRIES
            ):
                attempt += 1
                print(
                    f"WAIT rate limit reached, retrying in {RATE_LIMIT_WAIT_SECONDS} s "
                    f"(attempt {attempt}/{MAX_RATE_LIMIT_RETRIES})"
                )
                self.sleep(RATE_LIMIT_WAIT_SECONDS)
                continue

            raise DifyApiError(response.status_code, message)

        try:
            payload = response.json()
        except ValueError as error:
            raise DifyApiError(
                response.status_code, "Dify returned a non-JSON success response."
            ) from error

        if not isinstance(payload, dict):
            raise DifyApiError(response.status_code, "Dify returned an invalid response.")
        return payload

    def list_documents(self) -> dict[str, dict[str, Any]]:
        documents_by_name: dict[str, dict[str, Any]] = {}
        page = 1

        while True:
            payload = self._request(
                "GET",
                f"/datasets/{self.dataset_id}/documents",
                params={"page": page, "limit": PAGE_SIZE},
            )
            documents = payload.get("data")
            if not isinstance(documents, list):
                raise DifyApiError(200, "Document list response has no valid data array.")

            for document in documents:
                if not isinstance(document, dict):
                    continue
                name = document.get("name")
                document_id = document.get("id")
                if not isinstance(name, str) or not isinstance(document_id, str):
                    continue
                if name in documents_by_name:
                    print(
                        f"WARNING: Dify already contains duplicate documents named {name}; "
                        "using the first one."
                    )
                    continue
                documents_by_name[name] = document

            if not payload.get("has_more"):
                break
            page += 1

        return documents_by_name

    def create_document(self, name: str, content: str) -> str:
        payload = self._request(
            "POST",
            f"/datasets/{self.dataset_id}/document/create-by-text",
            json={
                "name": name,
                "text": content,
                "indexing_technique": "high_quality",
                "doc_form": "text_model",
                "process_rule": {"mode": "automatic"},
            },
        )
        document = payload.get("document")
        document_id = document.get("id") if isinstance(document, dict) else None
        if not isinstance(document_id, str):
            raise DifyApiError(200, "Create response did not include a document ID.")
        return document_id

    def update_document(self, document_id: str, name: str, content: str) -> None:
        self._request(
            "POST",
            f"/datasets/{self.dataset_id}/documents/{document_id}/update-by-text",
            json={
                "name": name,
                "text": content,
                "doc_form": "text_model",
                "process_rule": {"mode": "automatic"},
            },
        )


def required_environment() -> tuple[str, str, str]:
    load_dotenv(PROJECT_ROOT / ".env")
    names = ("DIFY_BASE_URL", "DIFY_DATASET_ID", "DIFY_API_KEY")
    values = tuple(os.getenv(name, "").strip() for name in names)
    missing = [name for name, value in zip(names, values) if not value]
    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")
    return values  # type: ignore[return-value]


def print_api_error(name: str, error: DifyApiError) -> None:
    status = str(error.status) if error.status is not None else "network error"
    print(f"FAIL {name} - HTTP {status}: {error}")


def run(dry_run: bool) -> int:
    try:
        base_url, dataset_id, api_key = required_environment()
    except ValueError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 2

    print("Scanning content...\n")
    included, excluded = find_markdown_files()
    print(f"Found {len(included) + len(excluded)} Markdown files.\n")

    counts = SyncCounts(skipped=len(excluded))
    for document in excluded:
        print(f"SKIP {document.name} (excluded)")

    client = DifyClient(base_url, dataset_id, api_key)
    try:
        remote_documents = client.list_documents()
    except DifyApiError as error:
        print_api_error("Dify document list", error)
        return 1

    state = load_state()
    state_documents = state["documents"]
    state_changed = False

    for document in included:
        try:
            markdown = document.path.read_text(encoding="utf-8-sig")
            metadata, body = split_front_matter(markdown)
            body = remove_navigation_blocks(body)
        except (OSError, UnicodeError) as error:
            counts.failed += 1
            print(f"FAIL {document.name} - file error: {error}")
            continue

        if not body.strip():
            counts.skipped += 1
            print(f"SKIP {document.name} (empty after cleaning)")
            continue

        sections = section_titles(document.path.relative_to(CONTENT_ROOT), CONTENT_ROOT)
        cleaned = build_document_text(metadata, body, sections)

        remote = remote_documents.get(document.name)
        digest = content_hash(cleaned)
        previous = state_documents.get(document.name, {})
        remote_id = remote.get("id") if remote else None
        unchanged = (
            isinstance(previous, dict)
            and previous.get("sha256") == digest
            and previous.get("document_id") == remote_id
        )

        if remote and unchanged:
            counts.skipped += 1
            print(f"SKIP {document.name} (unchanged)")
            continue

        action = "UPDATE" if remote else "CREATE"
        suffix = " (dry-run)" if dry_run else ""
        print(f"{action} {document.name}{suffix}")
        if dry_run:
            if remote:
                counts.updated += 1
            else:
                counts.created += 1
            continue

        try:
            if remote:
                assert isinstance(remote_id, str)
                client.update_document(remote_id, document.name, cleaned)
                document_id = remote_id
                counts.updated += 1
            else:
                document_id = client.create_document(document.name, cleaned)
                remote_documents[document.name] = {
                    "id": document_id,
                    "name": document.name,
                }
                counts.created += 1
        except DifyApiError as error:
            counts.failed += 1
            print_api_error(document.name, error)
            continue

        state_documents[document.name] = {
            "document_id": document_id,
            "sha256": digest,
        }
        state_changed = True

    if state_changed and not dry_run:
        try:
            save_state(state)
        except OSError as error:
            print(f"WARNING: Could not save {STATE_PATH.name}: {error}")

    print("\nSync complete.")
    print(f"Created: {counts.created}")
    print(f"Updated: {counts.updated}")
    print(f"Skipped: {counts.skipped}")
    print(f"Failed: {counts.failed}")
    return 1 if counts.failed else 0


def main() -> int:
    return run(parse_args().dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
