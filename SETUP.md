# coach-k-credit — setup and maintenance

This skill is **self-contained**. Everything it needs — the knowledge base, the search index,
the build scripts, and the documentation — lives inside this directory. Nothing outside it is
required at answer time, and no script depends on the shell's working directory.

```
coach-k-credit/
├── SKILL.md            what Claude loads: routing, voice rules, refusal triggers
├── SETUP.md            this file
├── references/         loaded on demand (voice spec, citation rules)
├── kb/
│   ├── manifest.yaml   SOURCE OF TRUTH — tiers, domains, exclusions, chapter map
│   ├── canon/          hand-written answer notes (the product)
│   ├── corpus/         extracted page text, one file per page (the citation unit)
│   ├── index/          kb.sqlite3 (member) + staff.sqlite3 (staff only, separate)
│   ├── sources/        original documents, named by doc-id
│   ├── staff/          internal ops, never member-facing
│   └── _quarantine/    excluded documents — never extracted, never indexed
├── scripts/            pipeline + search
└── docs/               DRIVE-MANIFEST.md and other build documentation
```

## Using it

Nothing to run. Open Claude Code anywhere in this project and ask a credit or grant question;
the skill activates on its description. Restart Claude Code after any change to `SKILL.md`.

To search the knowledge base by hand:

```bash
CK=".claude/skills/coach-k-credit"                     # or the absolute path
/usr/bin/python3 "$CK/scripts/kbsearch.py" "utilization statement closing date"
/usr/bin/python3 "$CK/scripts/kbsearch.py" "needs statement" --domain grants --limit 5
/usr/bin/python3 "$CK/scripts/kbsearch.py" "cancel premium" --staff
```

Every hit prints a citation plus the **absolute path** of the page behind it, so it is
readable from any working directory.

## Moving or sharing it

Copy the whole `coach-k-credit/` directory. It works from anywhere a skill can live:

- `<project>/.claude/skills/coach-k-credit/` — project-scoped (current setup)
- `~/.claude/skills/coach-k-credit/` — available in every project on this machine

The scripts resolve their own location, so no paths need editing after a move. The one thing
to update is `$CK` in whatever shell command you run by hand.

**Requirements:** macOS with `pdftotext` (poppler) and `/usr/bin/python3` carrying `pypdf` and
`PyYAML`. `sqlite3` needs FTS5, which the system build has. There is **no OCR** on this
machine — scanned PDFs will fail the yield gate rather than silently producing empty pages.

## Rebuilding after you add or change sources

```bash
CK=".claude/skills/coach-k-credit"
bash "$CK/scripts/00_stage_local.sh"                   # unpack + dedupe local documents
# optional: SRC="/path/to/other/folder" bash "$CK/scripts/00_stage_local.sh"
/usr/bin/python3 "$CK/scripts/10_extract.py"           # extract to corpus/
/usr/bin/python3 "$CK/scripts/20_build_index.py"       # rebuild both indexes
```

`10_extract.py` fails the build if a source is missing from `manifest.yaml`, if a PDF's page
count disagrees with what was extracted, if a document yields under 400 characters per page,
or if a quarantined doc-id reaches the corpus. Those gates are the point — do not route around
them.

**Adding a document** means adding an entry to `kb/manifest.yaml` first. Give it a doc-id, a
tier (1 = Coach K's own, 2 = third-party), a domain, and a `canonize` flag. Set
`fraud_screen: yes` on anything third-party; the extractor greps each page for CPN, sweep,
609, and stated-income language and reports what it finds for review.

**Google Drive sources** are pulled by file id through the MCP connector in-session, not by a
script — there is no local Drive credential. `docs/DRIVE-MANIFEST.md` records every file id,
what was deferred, and what was excluded as partner IP or PII. Pull by id, never by folder
crawl; a crawl is how other coaches' material and client contact data would drift in.

## Maintenance that actually matters

- **Volatile lists rot.** `list-bank-funding` already names BlockFi (bankrupt) and Marcus
  (exited consumer cards). Anything marked `volatility: volatile` needs a `verified_on` date
  and a re-check.
- **Re-extraction can move page numbers.** `manifest.yaml` pins the `pdftotext` version for
  this reason. If you upgrade poppler, treat the corpus diff as a reviewed change, because
  citations point at page numbers.
- **Canon is the product.** Four notes exist. The rest of a question either falls back to
  search or gets answered honestly as "not in Coach K's written material yet". Write new canon
  notes in the order members actually ask.
