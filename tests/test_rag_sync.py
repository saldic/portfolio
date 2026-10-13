import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, call

from scripts.rag_sync import (
    MAX_RATE_LIMIT_RETRIES,
    RATE_LIMIT_WAIT_SECONDS,
    DifyApiError,
    DifyClient,
    api_base_url,
    build_document_text,
    remove_navigation_blocks,
    section_titles,
    split_front_matter,
    strip_yaml_front_matter,
)


class StripYamlFrontMatterTests(unittest.TestCase):
    def test_removes_front_matter_at_start(self) -> None:
        markdown = '---\ntitle: "ERU"\ntags:\n  - AI\n---\n\n# What is ERU?\n'

        self.assertEqual(strip_yaml_front_matter(markdown), "# What is ERU?\n")

    def test_preserves_horizontal_rule_in_body(self) -> None:
        markdown = "# Heading\n\nIntro\n\n---\n\nMore text\n"

        self.assertEqual(strip_yaml_front_matter(markdown), markdown)

    def test_preserves_unclosed_front_matter_delimiter(self) -> None:
        markdown = "---\nThis is ordinary content without a closing delimiter.\n"

        self.assertEqual(strip_yaml_front_matter(markdown), markdown)

    def test_supports_utf8_bom_and_crlf(self) -> None:
        markdown = "\ufeff---\r\ntitle: ERU\r\n---\r\n\r\nBody\r\n"

        self.assertEqual(strip_yaml_front_matter(markdown), "Body\r\n")


class ApiBaseUrlTests(unittest.TestCase):
    def test_appends_api_version(self) -> None:
        self.assertEqual(api_base_url("http://localhost/"), "http://localhost/v1")

    def test_does_not_duplicate_api_version(self) -> None:
        self.assertEqual(api_base_url("http://localhost/v1"), "http://localhost/v1")


class DifyClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = DifyClient("http://localhost", "dataset-id", "secret-key")
        self.client._request = Mock()  # type: ignore[method-assign]

    def test_lists_all_document_pages(self) -> None:
        self.client._request.side_effect = [
            {
                "data": [{"id": "document-1", "name": "projects/eru.md"}],
                "has_more": True,
            },
            {
                "data": [{"id": "document-2", "name": "about.md"}],
                "has_more": False,
            },
        ]

        documents = self.client.list_documents()

        self.assertEqual(set(documents), {"projects/eru.md", "about.md"})
        self.assertEqual(
            self.client._request.call_args_list,
            [
                call(
                    "GET",
                    "/datasets/dataset-id/documents",
                    params={"page": 1, "limit": 100},
                ),
                call(
                    "GET",
                    "/datasets/dataset-id/documents",
                    params={"page": 2, "limit": 100},
                ),
            ],
        )

    def test_create_uses_text_high_quality_and_automatic_processing(self) -> None:
        self.client._request.return_value = {"document": {"id": "new-id"}}

        document_id = self.client.create_document("projects/eru.md", "# ERU\n")

        self.assertEqual(document_id, "new-id")
        self.client._request.assert_called_once_with(
            "POST",
            "/datasets/dataset-id/document/create-by-text",
            json={
                "name": "projects/eru.md",
                "text": "# ERU\n",
                "indexing_technique": "high_quality",
                "doc_form": "text_model",
                "process_rule": {"mode": "automatic"},
            },
        )

    def test_update_uses_document_id_and_automatic_processing(self) -> None:
        self.client._request.return_value = {"document": {"id": "document-id"}}

        self.client.update_document("document-id", "projects/eru.md", "# ERU\n")

        self.client._request.assert_called_once_with(
            "POST",
            "/datasets/dataset-id/documents/document-id/update-by-text",
            json={
                "name": "projects/eru.md",
                "text": "# ERU\n",
                "doc_form": "text_model",
                "process_rule": {"mode": "automatic"},
            },
        )


class ContextHeaderTests(unittest.TestCase):
    def test_reads_title_and_tags_from_front_matter(self) -> None:
        markdown = '---\ntitle: "01 - Page"\ntags: ["aida", "naur"]\n---\n\nBody\n'

        metadata, body = split_front_matter(markdown)

        self.assertEqual(metadata["title"], "01 - Page")
        self.assertEqual(metadata["tags"], ["aida", "naur"])
        self.assertEqual(body, "Body\n")

    def test_builds_header_with_title_section_and_tags(self) -> None:
        text = build_document_text(
            {"title": "01 - Page", "tags": ["aida", "naur"]},
            "Body\n",
            ["Projects", "AI-Driven Applications"],
        )

        self.assertEqual(
            text,
            "Title: 01 - Page\n"
            "Section: Projects > AI-Driven Applications\n"
            "Tags: aida, naur\n\n"
            "Body\n",
        )

    def test_returns_body_unchanged_without_metadata(self) -> None:
        self.assertEqual(build_document_text({}, "Body\n", []), "Body\n")

    def test_finds_section_titles_from_parent_index_files(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "_index.md").write_text('---\ntitle: "Home"\n---\n')
            (root / "projects" / "aida" / "page").mkdir(parents=True)
            (root / "projects" / "_index.md").write_text('---\ntitle: "Projects"\n---\n')
            (root / "projects" / "aida" / "_index.md").write_text(
                '---\ntitle: "AI-Driven Applications"\n---\n'
            )

            titles = section_titles(Path("projects/aida/page/index.md"), root)

        self.assertEqual(titles, ["Projects", "AI-Driven Applications"])


class NavigationBlockTests(unittest.TestCase):
    def test_removes_chapter_navigation_and_pagination(self) -> None:
        body = (
            '<div class="exam-portfolio-nav">\n'
            '  <a class="exam-portfolio-nav__link" href="../">Overview</a>\n'
            "</div>\n\n"
            "## Overview\n\nText about the chapter.\n\n"
            '<div class="exam-portfolio-pagination">\n'
            '  <a role="button" href="../rest-api/">Next Chapter</a>\n'
            "</div>\n"
        )

        self.assertEqual(
            remove_navigation_blocks(body),
            "## Overview\n\nText about the chapter.\n",
        )

    def test_keeps_other_html(self) -> None:
        body = '## Demo\n\n<div class="video">Clip</div>\n'

        self.assertEqual(remove_navigation_blocks(body), body)


def fake_response(status: int, payload: dict) -> Mock:
    response = Mock()
    response.ok = 200 <= status < 300
    response.status_code = status
    response.json.return_value = payload
    response.text = ""
    response.reason = ""
    return response


class RateLimitRetryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = DifyClient("http://localhost", "dataset-id", "secret-key")
        self.client.session = Mock()
        self.client.sleep = Mock()  # type: ignore[method-assign]
        self.rate_limited = fake_response(
            403,
            {"message": "Sorry, you have reached the knowledge base request rate limit of your subscription."},
        )

    def test_waits_and_retries_after_rate_limit(self) -> None:
        self.client.session.request.side_effect = [
            self.rate_limited,
            fake_response(200, {"document": {"id": "new-id"}}),
        ]

        document_id = self.client.create_document("page.md", "Body")

        self.assertEqual(document_id, "new-id")
        self.client.sleep.assert_called_once_with(RATE_LIMIT_WAIT_SECONDS)
        self.assertEqual(self.client.session.request.call_count, 2)

    def test_gives_up_after_max_retries(self) -> None:
        self.client.session.request.return_value = self.rate_limited

        with self.assertRaises(DifyApiError) as context:
            self.client.create_document("page.md", "Body")

        self.assertEqual(context.exception.status, 403)
        self.assertEqual(self.client.sleep.call_count, MAX_RATE_LIMIT_RETRIES)
        self.assertEqual(
            self.client.session.request.call_count, MAX_RATE_LIMIT_RETRIES + 1
        )

    def test_does_not_retry_other_errors(self) -> None:
        self.client.session.request.return_value = fake_response(
            403, {"message": "Access token is invalid"}
        )

        with self.assertRaises(DifyApiError):
            self.client.create_document("page.md", "Body")

        self.client.sleep.assert_not_called()
        self.assertEqual(self.client.session.request.call_count, 1)


if __name__ == "__main__":
    unittest.main()
