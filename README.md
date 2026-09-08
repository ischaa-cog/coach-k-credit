# coach-k-credit

A Claude Code skill that drafts answers to Business & Grant Community member questions about
**personal credit, business credit, funding, and grants** — grounded in Coach K's own
material, with a citation on every answer.

> **Private repository.** Read [NOTICE.md](NOTICE.md) before sharing, forking, or changing
> visibility. It contains Coach K's paid products and third-party copyrighted reference
> material, and must not be made public.

## What it does

Ask a question in Claude Code and get back a draft in Coach K's voice — roughly 250 words for
a definition, 500 for a procedure — ending in a source line like
`— Master Blueprint, Ch. 2 & Ch. 19`. You review it and post it.

It refuses, and explains why, on CPNs, credit sweeps, credit card fraud, "guaranteed"
anything, and the "Section 609 loophole" — anchored to Coach K's own Chapter 22 scam-warning
list, so a refusal reads as enforcing her teaching rather than overriding it.

## Install on another machine

The repository **is** the skill directory, so it clones straight into place.

**Available in every project on that machine:**

```bash
git clone https://github.com/ischaa-cog/coach-k-credit.git \
  ~/.claude/skills/coach-k-credit
```

**Or scoped to one project:**

```bash
git clone https://github.com/ischaa-cog/coach-k-credit.git \
  /path/to/project/.claude/skills/coach-k-credit
```

Then build the search index — it is generated, not committed:

```bash
/usr/bin/python3 ~/.claude/skills/coach-k-credit/scripts/20_build_index.py
```

Restart Claude Code. Ask a credit or grant question; the skill activates on its description.

### Requirements

- macOS with `pdftotext` (`brew install poppler`) — only needed to re-extract sources
- `/usr/bin/python3` with `pypdf` and `PyYAML`:
  `/usr/bin/python3 -m pip install --user pypdf pyyaml`
- `sqlite3` with FTS5 — the macOS system build has it
- **No OCR.** Scanned PDFs fail the yield gate rather than silently producing empty pages.

The original source PDFs are not committed (see NOTICE.md). You do not need them to run the
skill — `kb/corpus/` holds the extracted text and `kb/index/` rebuilds from it. You only need
them to re-run extraction.

## How it is built

Three layers, joined by one manifest. **`kb/canon/` is the only member-facing surface;
`kb/corpus/` exists to be cited and searched, never quoted.** That single rule is what keeps
copyright, staleness, and source tiering under control at once.

| Layer | What it is |
|---|---|
| `kb/corpus/` | Extracted page text, one file per page. The citation unit. Committed, so page numbers stay stable. |
| `kb/index/` | SQLite FTS5 + BM25, weighted so tier-1 outranks a 2007 ebook, filterable by domain. Generated. |
| `kb/canon/` | Hand-written answer notes in Coach K's voice, with frontmatter and citations. The product. |
| `kb/manifest.yaml` | Source of truth: 36 documents with tier, domain, volatility, page-range scoping, and the hand-verified chapter map. |

`SKILL.md` holds no content — only routing, voice rules, and refusal triggers. That is why the
same knowledge base can later drive a member-facing web page with no rework.

## Searching by hand

```bash
CK="$HOME/.claude/skills/coach-k-credit"
/usr/bin/python3 "$CK/scripts/kbsearch.py" "utilization statement closing date"
/usr/bin/python3 "$CK/scripts/kbsearch.py" "needs statement" --domain grants --limit 5
/usr/bin/python3 "$CK/scripts/kbsearch.py" "cancel premium" --staff
```

Each hit prints a citation plus the absolute path of the page behind it. Read that page before
using the claim — the snippet is a locator, not a source.

## Adding or updating sources

Add an entry to `kb/manifest.yaml` **first** — a source not in the manifest fails the build by
design. Then:

```bash
bash "$CK/scripts/00_stage_local.sh"              # unpack + md5-dedupe
/usr/bin/python3 "$CK/scripts/10_extract.py"      # extract to kb/corpus/
/usr/bin/python3 "$CK/scripts/20_build_index.py"  # rebuild both indexes
```

Set `fraud_screen: yes` on anything third-party; the extractor greps every page for CPN,
sweep, 609 and stated-income language and reports hits for review before you trust the source.

Google Drive material is pulled by file id through the MCP connector in-session — there is no
local Drive credential and no crawl. `docs/DRIVE-MANIFEST.md` records every id that was
pulled, deferred, or excluded as partner IP or PII.

Full detail in [SETUP.md](SETUP.md).

## Current state

Working: the pipeline, 36 documents / 1,596 pages indexed across credit and grants,
tier-weighted search, staff/member index isolation, and four canon notes —
`utilization`, `grantors-and-credit`, `write-a-grant-proposal`, and
`refusals-and-corrections`.

Anything without a canon note falls back to tier-weighted search, and the skill says plainly
when a topic is not yet in Coach K's written material.

Not yet done: `scripts/30_verify.py` (the gate that checks every canon citation resolves to a
real page and that no canon file has drifted into pasting tier-2 text verbatim), the remaining
~35 canon notes, and the Phase 2 member-facing page.

## For the team

Members should not clone this — it needs Claude Code. The member-facing surface is the Phase 2
web page, built from the same `kb/canon/` files. This repository is for the people drafting
answers.
