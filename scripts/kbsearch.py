#!/usr/bin/env /usr/bin/python3
"""
Search the knowledge base. BM25 ranked, tier-weighted, citation-shaped output.

    kbsearch.py "utilization statement closing date"
    kbsearch.py "PAYDEX three tradelines" --domain credit --limit 5
    kbsearch.py "needs statement" --domain grants
    kbsearch.py "cancel premium" --staff          # separate index, staff only

Output lines are the citation you paste into a canon note, plus the command that
prints the page behind it:
    [ck-part1 ch2 p8]  T1  ...paying the balance before the statement closing date...
                       -> scripts/ckpage.py ck-part1 8

Run that before you use the claim. The snippet is a locator, not a source.
"""
import argparse, re, sqlite3, sys
from pathlib import Path

ROOT   = Path(__file__).resolve().parent.parent
INDEX  = ROOT / "kb" / "index"
READER = ROOT / "scripts" / "ckpage.py"

FTS_OPERATORS = re.compile(r'[":*()^]|\b(?:AND|OR|NOT|NEAR)\b')


def build_matches(query, raw=False):
    """
    Yield progressively looser FTS5 queries.

    Strict AND is too brittle on this corpus: a search for "PAYDEX three
    tradelines" misses Ch.17, which writes "trade lines" as two words. So try
    AND, then OR, and report which mode actually answered.
    """
    if raw:
        return [("raw", query)]
    tokens = re.findall(r"[\w']+", query)
    if not tokens:
        sys.exit("no searchable terms in query")
    quoted = [f'"{t}"' for t in tokens]
    out = [("all terms", " ".join(quoted))]
    if len(quoted) > 1:
        out.append(("any term", " OR ".join(quoted)))
    return out


def main():
    ap = argparse.ArgumentParser(description="Search the Coach K knowledge base.")
    ap.add_argument("query")
    ap.add_argument("--domain", choices=["credit", "grants", "crosscutting"],
                    help="restrict to one subject domain")
    ap.add_argument("--tier", type=int, choices=[1, 2], help="restrict to a tier")
    ap.add_argument("--doc", help="restrict to one doc-id")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--chars", type=int, default=200, help="snippet width")
    ap.add_argument("--raw", action="store_true", help="pass the query to FTS5 verbatim")
    ap.add_argument("--staff", action="store_true", help="search the staff index instead")
    ap.add_argument("--paths", action="store_true",
                    help="print bare 'doc-id page' pairs only")
    args = ap.parse_args()

    db = INDEX / ("staff.sqlite3" if args.staff else "kb.sqlite3")
    if not db.exists():
        sys.exit(f"index not built: {db}\nrun scripts/20_build_index.py")

    filters, fparams = [], []
    if args.domain:
        filters.append("pages.domain = ?"); fparams.append(args.domain)
    if args.tier:
        filters.append("pages.tier = ?"); fparams.append(args.tier)
    if args.doc:
        filters.append("pages.doc_id = ?"); fparams.append(args.doc)

    sql_t = """
        SELECT pages.doc_id, pages.page, pages.chapter, pages.tier,
               docs.content_date, docs.volatility, docs.page_prefix, docs.title,
               snippet(pages, 5, '', '', '…', 24) AS snip,
               -bm25(pages) * docs.weight AS score
          FROM pages JOIN docs ON docs.doc_id = pages.doc_id
         WHERE {where}
         ORDER BY score DESC
         LIMIT ?
    """

    con = sqlite3.connect(db)
    rows, mode = [], None
    for label, match in build_matches(args.query, args.raw):
        where = " AND ".join(["pages MATCH ?"] + filters)
        try:
            rows = con.execute(sql_t.format(where=where),
                               [match] + fparams + [args.limit]).fetchall()
        except sqlite3.OperationalError as e:
            con.close()
            sys.exit(f"query error: {e}\n(try --raw, or simplify the query)")
        if rows:
            mode = label
            break
    con.close()

    if not rows:
        print("no matches")
        return 0
    if mode and mode != "all terms" and not args.paths:
        print(f"# matched on '{mode}' (no page contained every term)")

    for doc_id, page, chapter, tier, date, volatility, prefix, title, snip, score in rows:
        if args.paths:
            print(f"{doc_id} {page}")
            continue
        # Absolute, so the caller can run it regardless of working directory.
        reader = f'/usr/bin/python3 "{READER}" {doc_id} {page}'
        cite = f"[{doc_id}" + (f" ch{chapter}" if chapter else "") + f" {prefix}{page}]"
        stamp = f" {date}" if volatility == "volatile" and date not in (None, "unknown") else ""
        snip = re.sub(r"\s+", " ", snip).strip()[: args.chars]
        print(f"{cite:<34} T{tier}{stamp}  {snip}")
        print(f"{'':<34} -> {reader}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
