---
title: "02 - Keeping Chip up to date"
date: 2026-10-13
weight: 2
tags: ["aida", "chip", "rag", "automation", "python"]
showWordCount: true
showReadingTime: true
---

<div class="exam-portfolio-nav">
  <a class="exam-portfolio-nav__link" href="../">Overview</a>
  <a class="exam-portfolio-nav__link" href="../anatomy-of-chip/">01</a>
  <a class="exam-portfolio-nav__link exam-portfolio-nav__link--current" href="../keeping-chip-up-to-date/">02</a>
  <a class="exam-portfolio-nav__link" href="../interrogating-chip/">03</a>
  <a class="exam-portfolio-nav__link" href="../delegating-the-code-not-the-theory/">04</a>
  <a class="exam-portfolio-nav__link" href="../grill-me/">05</a>
  <a class="exam-portfolio-nav__link" href="../figma-make-process/">06</a>
  <a class="exam-portfolio-nav__link" href="../security-and-ethics/">07</a>
</div>

## A quality-of-life script

Chip only knows what's in its knowledge base in Dify. A new page is invisible to Chip until it's uploaded, and a changed page keeps its old version in Dify until it's uploaded again. Uploading by hand works for a few pages, but I wouldn't keep doing it, and Chip would slowly drift away from what the site says.

The answer is `scripts/rag_sync.py`. It goes through every Markdown page in `content/`, works out which ones are new or changed, and sends only those to Dify's Knowledge API.

For each page, the script:

1. It cleans the page. It removes the front matter and the chapter navigation (the numbered links at the top and the Previous/Next buttons at the bottom). Section index files (`_index.md`) are skipped.
2. It adds a header with the page's title, section and tags.
3. It makes a **SHA-256 hash** of the text, a kind of fingerprint. The same text always gives the same hash, and changing one character gives a completely different one.
4. It compares with last time. A **state file**, `.rag-sync-state.json`, remembers each page's hash and the ID Dify gave the document. If both match, the page is skipped.
5. It creates or updates the document in Dify. The new hash is only written to the state file if the upload succeeded.

```python
# scripts/rag_sync.py
remote = remote_documents.get(document.name)
digest = content_hash(cleaned)
previous = state_documents.get(document.name, {})
remote_id = remote.get("id") if remote else None
unchanged = (
    isinstance(previous, dict)
    and previous.get("sha256") == digest
    and previous.get("document_id") == remote_id
)
```

Both conditions are needed. If a document is deleted in Dify and recreated with a new ID, the hash still matches, but the page should be uploaded again.

{{< mermaid >}}
flowchart LR
  P["A page"] --> D{"Already in Dify?"}
  D -- no --> C["Create"]
  D -- yes --> S{"Same hash and same ID<br/>as last time?"}
  S -- yes --> K["Skip"]
  S -- no --> U["Update"]
{{< /mermaid >}}

The hash is calculated after the front matter is removed. So if I change a setting like `layout`, nothing is uploaded, because the text a visitor reads is the same. A new title or new tags are uploaded, because they're part of the header.

## Moving to Dify Cloud

Until recently, Dify ran on my laptop, so Chip only worked on my own machine. To put Chip on the live site, I moved it to Dify Cloud and pointed the script at a new, empty knowledge base.

The first run created ten pages and failed on the last five:

```text
FAIL projects/eru-project/frontend-process/beyond-the-frontend/index.md - HTTP 403: Sorry, you have reached the knowledge base request rate limit of your subscription.
...
Created: 10
Updated: 0
Skipped: 6
Failed: 5
```

The free plan allows **ten knowledge base requests per minute**. A minute later I ran the script again. The ten pages that were already there were skipped as unchanged, and only the five missing ones were created.

I don't want to have to run it twice, so the script now waits and tries again when it hits the limit. Dify answers with 403 instead of the usual 429, so the check looks at the message too:

```python
# scripts/rag_sync.py
def is_rate_limited(status: int, message: str) -> bool:
    """Dify Cloud answers 403 (not 429) when the knowledge base limit is hit."""
    return status == 429 or (status == 403 and "rate limit" in message.lower())
```

It waits 60 seconds and tries up to three times. Other errors, like a wrong API key, fail straight away, because waiting won't fix them. The next full run waited once and finished without failures:

```text
WAIT rate limit reached, retrying in 60 s (attempt 1/3)
...
Created: 0
Updated: 15
Skipped: 6
Failed: 0
```

## Two things Chip got wrong

After the move I asked Chip about AIDA. It said it couldn't find anything, even though my AIDA page was listed as one of its sources. The page was found, but its text never mentioned AIDA. The word was only in the tags, and the script removed them with the front matter. That's why the script now adds the **header**.

The next answer got the section right but said the AIDA chapter came after "JPA Basics and Relations" and before "REST API". Those are eru pages. The text came from the Previous/Next buttons on an eru page, which had been uploaded along with everything else. The script now removes them. On the next run, 14 pages were updated, and the contact page was skipped because it has no chapter navigation, so its text hadn't changed.

I also changed the section title to "AI-Driven Applications (AIDA)". Until then, nothing on the site said what the abbreviation stood for.

I noticed the wrong answers when I tested Chip. I had Claude find the cause in the script and write the three changes, and I reviewed them before I ran the script and checked Chip's answers again.

## Tests

I had Claude write the script. I understood the general idea before I understood all of the syntax, and I went through it step by step with Claude afterwards.

It has **18 unit tests**, and they pass. They cover the edges of the cleaning (byte-order marks, Windows line endings, a `---` in the middle of a page), the requests sent to Dify, the header, the navigation removal, and the retry: that it waits after a rate limit, gives up after three attempts, and doesn't retry other errors. The waiting is faked, so the tests run instantly.

They don't test the skip, update or create decision shown above, and they never touch a real knowledge base.

> That decision is the most important part of the script, and it has no test.

What I relied on instead were the real runs, where I could see what was created, updated and skipped.

## Running it on every push

At first I ran the script by hand, which is easy to forget. Now it runs in **GitHub Actions** on every push to `main` that changes something in `content/` (`.github/workflows/rag-sync.yml`). Claude wrote the workflow, and I added the API key as a GitHub secret. It runs the 18 tests first and only syncs if they pass.

The state file isn't in git, so the workflow keeps it in the **GitHub Actions cache** between runs. A cache that hasn't been used for a week is deleted, and then the script simply updates every page once. That costs a few extra uploads, but nothing breaks.

It still has gaps. It **never deletes**, so a page I remove from the site stays in Dify until I delete it there by hand. Renaming a page creates a duplicate, because documents are matched by path. The header only reaches the first chunk of a long page, and the text on the front page is skipped, because all `_index.md` files are excluded.

<div class="exam-portfolio-pagination">
  <a role="button" href="../anatomy-of-chip/">Previous Chapter</a>
  <a role="button" href="../interrogating-chip/">Next Chapter</a>
</div>
