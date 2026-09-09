# coach-k-credit

A Claude Code skill that answers Business & Grant Community member questions about
**personal credit, business credit, funding, and grants** — grounded in Coach K's own
material, with a citation on every answer.

> **Private repository.** Read [NOTICE.md](NOTICE.md) before sharing, forking, or changing
> visibility. It contains Coach K's paid products and third-party copyrighted reference
> material, and must not be made public.

## What it does

Ask a question in Claude Code and get back the answer in Coach K's voice, spoken directly to
the member, roughly 250 words for a definition and 500 for a procedure, formatted to be scanned
on a phone (bolded lead answer, short sections, no em dashes) and ending in a source line like
`Source: Master Blueprint, Ch. 2 & Ch. 19`.

On the first question of a conversation it also prints a short **What you can ask** block with
five sample questions, so a new user can see the shape of what the skill answers:

1. My cards are at 60% utilization. What do I pay down first to move my score fastest?
2. Do grant funders check my personal credit?
3. How do I start building business credit under my EIN while my personal credit is still rough?
4. What goes in the needs statement of a grant proposal?
5. Someone is offering to sell me a tradeline to boost my score fast. Should I do it?

It refuses, and explains why, on CPNs, credit sweeps, credit card fraud, "guaranteed"
anything, and the "Section 609 loophole" — anchored to Coach K's own Chapter 22 scam-warning
list, so a refusal reads as enforcing her teaching rather than overriding it.

## The member-facing page

`frontend/ask-coach-k.html` is an ask console in the Coach K brand (black and gold, Archivo
and IBM Plex), published as a Claude Artifact. A member types a question and gets the answer
in her voice, in the same format the skill produces in Claude Code.

It cannot read `kb/` at runtime, so the skill is compiled into the prompt it sends: the
refusal protocol as a hard first step, the voice and format rules, the confabulation traps,
and all four `kb/canon/` notes verbatim, about 25 KB against a 64 KB cap. When a question
falls outside that canon the page says so rather than filling the gap. Widening its coverage
means writing more canon notes, not editing the page.

Publishing it needs the `sample` capability, which spends the *viewer's* Claude usage and
asks their permission on the first question:

```
Artifact(file_path="frontend/ask-coach-k.html", capabilities={"sample": {}})
```

Two known limits. The Drive links in the source line resolve only for accounts with access to
the folder, so a member sees a link they cannot open. And the page carries no `kb/staff/`
material by construction.

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
bash "$CK/scripts/00_stage_local.sh"                # unpack + md5-dedupe
/usr/bin/python3 "$CK/scripts/10_extract.py"        # extract to kb/corpus/
/usr/bin/python3 "$CK/scripts/20_build_index.py"    # rebuild both indexes
/usr/bin/python3 "$CK/scripts/30_bundle_pages.py"   # bundle pages for packaging
```

Set `fraud_screen: yes` on anything third-party; the extractor greps every page for CPN,
sweep, 609 and stated-income language and reports hits for review before you trust the source.

Google Drive material is pulled by file id through the MCP connector in-session — there is no
local Drive credential and no crawl. `docs/DRIVE-MANIFEST.md` records every id that was
pulled, deferred, or excluded as partner IP or PII.

### Packaging it for a workspace upload

```bash
bash "$CK/scripts/40_package.sh"                  # -> coach-k-credit-skill.zip
```

The workspace skill uploader caps an upload at **200 files**, and the extraction tree is about
1,650 page files on its own. The package therefore ships the runtime surface only: `SKILL.md`
and its references, the canon notes, the FTS index, and one `pages.txt` bundle per document
instead of a directory of pages. That is 53 files, and `ckpage.py` reads a page out of a
bundle exactly as it reads one out of `pages/`, so retrieval behaves identically either way.

`40_package.sh` refuses to write a zip that breaks the upload: no `SKILL.md`, frontmatter
missing a usable single-line `name` or `description`, quarantined material staged, or more
than 200 files. The source PDFs, the quarantine, the extraction tree and the build scripts
stay in the repo, because nothing at answer time reads them.

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

The skill answers the member directly, in Coach K's voice, wherever it runs: a team member
using it in Claude Code on someone's behalf, or a member using it themselves. It is not a
drafting tool with a reviewer in the loop, so `kb/staff/` stays out of every answer. The
Phase 2 web page is the wider member-facing surface, built from the same `kb/canon/` files.

The repository itself stays private regardless of who is asking the questions. See
[NOTICE.md](NOTICE.md).
