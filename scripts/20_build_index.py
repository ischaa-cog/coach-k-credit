#!/usr/bin/env /usr/bin/python3
"""
Build kb/index/kb.sqlite3 (member+team) and kb/index/staff.sqlite3 (staff only)
from kb/corpus/, using SQLite FTS5 + BM25. No external dependencies.

Two hard properties:
  * Quarantined documents are NEVER inserted. Exclusion is a property of the
    artifact, not a query-time filter someone can forget to apply.
  * Staff documents go into a physically separate database that the member
    search never opens.
"""
import json, re, sqlite3, sys, unicodedata
from pathlib import Path

import yaml

ROOT     = Path(__file__).resolve().parent.parent
CORPUS   = ROOT / "kb" / "corpus"
INDEX    = ROOT / "kb" / "index"
MANIFEST = ROOT / "kb" / "manifest.yaml"

# Tier weights: Coach K must outrank a 2007 ebook on a tie, and volatile vendor
# lists must sink below both.
TIER_WEIGHT = {1: 3.0, 2: 1.0}
VOLATILE_WEIGHT = 0.6

SCHEMA = """
PRAGMA journal_mode = WAL;

CREATE TABLE docs (
    doc_id        TEXT PRIMARY KEY,
    title         TEXT,
    author        TEXT,
    tier          INTEGER,
    domain        TEXT,
    content_date  TEXT,
    volatility    TEXT,
    audience      TEXT,
    canonize      INTEGER,
    page_count    INTEGER,
    license       TEXT,
    pagination    TEXT,
    page_prefix   TEXT,
    weight        REAL,
    notes         TEXT
);

CREATE VIRTUAL TABLE pages USING fts5(
    doc_id   UNINDEXED,
    page     UNINDEXED,
    chapter  UNINDEXED,
    tier     UNINDEXED,
    domain   UNINDEXED,
    body,
    tokenize = 'porter unicode61'
);

CREATE TABLE links (
    doc_id TEXT,
    page   INTEGER,
    url    TEXT
);
CREATE INDEX links_doc ON links(doc_id);
"""


def normalize(text):
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"(\w)[-‐‑]\n(\w)", r"\1\2", text)
    return re.sub(r"\s+", " ", text).strip()


def chapter_for(page_no, chapters):
    if not chapters:
        return None
    for ch, rng in chapters.items():
        lo, hi = rng
        if lo <= page_no <= hi:
            return int(ch)
    return None


def weight_for(meta):
    w = TIER_WEIGHT.get(meta.get("tier"), 1.0)
    if meta.get("volatility") == "volatile":
        w *= VOLATILE_WEIGHT
    return w


def build(db_path, metas):
    if db_path.exists():
        db_path.unlink()
    for suffix in ("-wal", "-shm"):
        p = db_path.with_name(db_path.name + suffix)
        if p.exists():
            p.unlink()

    con = sqlite3.connect(db_path)
    con.executescript(SCHEMA)

    n_pages = n_links = 0
    for meta in metas:
        doc_id = meta["doc_id"]
        con.execute(
            "INSERT INTO docs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (doc_id, meta.get("title"), meta.get("author"), meta.get("tier"),
             meta.get("domain"), str(meta.get("content_date")), meta.get("volatility"),
             meta.get("audience"), int(bool(meta.get("canonize"))),
             meta.get("pages_extracted"), meta.get("license"), meta.get("pagination"),
             meta.get("page_prefix"), weight_for(meta), meta.get("notes")),
        )

        chapters = meta.get("chapters") or {}
        for page_file in sorted((CORPUS / doc_id / "pages").glob("*.txt")):
            page_no = int(re.sub(r"\D", "", page_file.stem))
            body = normalize(page_file.read_text(errors="replace"))
            if not body:
                continue
            con.execute(
                "INSERT INTO pages (doc_id, page, chapter, tier, domain, body) "
                "VALUES (?,?,?,?,?,?)",
                (doc_id, page_no, chapter_for(page_no, chapters),
                 meta.get("tier"), meta.get("domain"), body),
            )
            n_pages += 1

        lt = CORPUS / doc_id / "links.tsv"
        if lt.exists():
            for line in lt.read_text().splitlines():
                if "\t" not in line:
                    continue
                pg, url = line.split("\t", 1)
                con.execute("INSERT INTO links VALUES (?,?,?)", (doc_id, int(pg), url))
                n_links += 1

    con.commit()
    con.execute("INSERT INTO pages(pages) VALUES('optimize')")
    con.commit()
    con.close()
    return n_pages, n_links


def main():
    mf = yaml.safe_load(MANIFEST.read_text())
    quarantined = set(mf.get("quarantine") or {}) | set(mf.get("market_intel") or {})
    INDEX.mkdir(parents=True, exist_ok=True)

    metas = json.loads((CORPUS / "_index.json").read_text())

    # Gate: a quarantined doc-id must never reach the index.
    leaked = [m["doc_id"] for m in metas if m["doc_id"] in quarantined
              or m["doc_id"].startswith("x-")]
    if leaked:
        print(f"FATAL: quarantined doc-ids reached the corpus: {leaked}", file=sys.stderr)
        return 1

    member = [m for m in metas if m.get("audience") != "staff"]
    staff  = [m for m in metas if m.get("audience") == "staff"]

    mp, ml = build(INDEX / "kb.sqlite3", member)
    print(f"kb.sqlite3    {len(member):>3} docs | {mp:>5} pages | {ml:>5} links")
    sp, sl = build(INDEX / "staff.sqlite3", staff)
    print(f"staff.sqlite3 {len(staff):>3} docs | {sp:>5} pages | {sl:>5} links")

    # Gate: no staff doc may appear in the member index.
    con = sqlite3.connect(INDEX / "kb.sqlite3")
    bad = con.execute("SELECT doc_id FROM docs WHERE audience='staff'").fetchall()
    con.close()
    if bad:
        print(f"FATAL: staff docs in member index: {bad}", file=sys.stderr)
        return 1

    print("\nBy domain / tier:")
    con = sqlite3.connect(INDEX / "kb.sqlite3")
    for row in con.execute(
        "SELECT domain, tier, COUNT(*), SUM(page_count) FROM docs GROUP BY domain, tier"
    ):
        print(f"  {row[0]:<12} tier {row[1]}  {row[2]:>2} docs  {row[3]:>5} pages")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
