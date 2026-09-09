#!/usr/bin/env /usr/bin/python3
"""
Print one page of a knowledge-base document, exactly as extracted.

kbsearch.py gives you a citation and a locator; this gives you the page behind it.
Read the page before you use the claim.

    ckpage.py ck-part1 8            # one page
    ckpage.py ck-part1 8-11         # a range, page markers kept between them
    ckpage.py ck-part1 p008         # the page name works too

It resolves against kb/corpus/<doc>/pages.txt (the shipped bundle) and falls back
to kb/corpus/<doc>/pages/<name>.txt when the full extraction tree is present, so
the same command works in the source repo and in the packaged skill.
"""
import argparse, re, sys
from pathlib import Path

ROOT   = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "kb" / "corpus"

MARKER = re.compile(r"\f([A-Za-z]?\d+)\n")


def load_bundle(doc_dir):
    """Return {page-name: text} from pages.txt, or None when there is no bundle."""
    bundle = doc_dir / "pages.txt"
    if not bundle.exists():
        return None
    raw = bundle.read_text(errors="replace")
    parts = MARKER.split(raw)
    # split() -> ['', name, body, name, body, ...]; anything before the first
    # marker is not a page.
    return {parts[i]: parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def page_names(spec, available):
    """Expand '8', 'p008' or '8-11' into page names that exist for this doc."""
    def norm(token):
        digits = re.sub(r"\D", "", token)
        if not digits:
            sys.exit(f"not a page number: {token}")
        return int(digits)

    if "-" in spec.strip("-"):
        lo, hi = (norm(t) for t in spec.split("-", 1))
        wanted = range(lo, hi + 1)
    else:
        wanted = [norm(spec)]

    by_number = {int(re.sub(r"\D", "", name)): name for name in available}
    return [by_number[n] for n in wanted if n in by_number], list(wanted)


def main():
    ap = argparse.ArgumentParser(description="Print a knowledge-base page.")
    ap.add_argument("doc_id", help="e.g. ck-part1")
    ap.add_argument("pages", help="page number, page name, or range (8, p008, 8-11)")
    ap.add_argument("--no-header", action="store_true",
                    help="page text only, no [doc page] header line")
    args = ap.parse_args()

    doc_dir = CORPUS / args.doc_id
    if not doc_dir.is_dir():
        have = ", ".join(sorted(d.name for d in CORPUS.iterdir() if d.is_dir()))
        sys.exit(f"no such doc-id: {args.doc_id}\navailable: {have}")

    pages = load_bundle(doc_dir)
    if pages is None:
        loose = sorted((doc_dir / "pages").glob("*.txt"))
        if not loose:
            sys.exit(f"{args.doc_id} has neither pages.txt nor pages/ "
                     f"(run scripts/30_bundle_pages.py)")
        pages = {p.stem: p.read_text(errors="replace") for p in loose}

    names, wanted = page_names(args.pages, pages)
    if not names:
        lo, hi = min(pages, key=len), max(pages)
        sys.exit(f"{args.doc_id} has no page {args.pages} "
                 f"({len(pages)} pages: {sorted(pages)[0]} to {sorted(pages)[-1]})")

    missing = set(wanted) - {int(re.sub(r"\D", "", n)) for n in names}
    for name in names:
        if not args.no_header:
            print(f"[{args.doc_id} {name}]")
        print(pages[name].rstrip("\n"))
    if missing:
        print(f"\n(no page {', '.join(str(m) for m in sorted(missing))} "
              f"in {args.doc_id})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
