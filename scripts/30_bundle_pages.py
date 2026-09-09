#!/usr/bin/env /usr/bin/python3
"""
Collapse kb/corpus/<doc>/pages/*.txt into a single kb/corpus/<doc>/pages.txt bundle.

The workspace skill uploader caps a .skill/.zip at 200 files, and the per-page
layout is ~1650 files on its own. The bundle carries the same page text, byte for
byte, behind an explicit marker line per page, so ckpage.py can hand back one page
without the packaged skill shipping one file per page.

Bundle format, repeated once per page:

    \f<page-name>
    <page text>

The marker is a form feed, then the page file's stem (p008, s003), then a newline.
Page text is stored verbatim; pdftotext never puts a form feed inside a page, so
the marker cannot collide with content.

    scripts/30_bundle_pages.py            # rebuild every bundle
    scripts/30_bundle_pages.py ck-part1   # rebuild one doc
"""
import sys
from pathlib import Path

ROOT   = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "kb" / "corpus"


def bundle(doc_dir):
    pages = sorted((doc_dir / "pages").glob("*.txt"))
    if not pages:
        return None
    out = []
    for page in pages:
        out.append(f"\f{page.stem}\n")
        out.append(page.read_text(errors="replace"))
        out.append("\n")
    (doc_dir / "pages.txt").write_text("".join(out))
    return len(pages)


def main(argv):
    wanted = set(argv)
    total_docs = total_pages = 0
    for doc_dir in sorted(d for d in CORPUS.iterdir() if d.is_dir()):
        if wanted and doc_dir.name not in wanted:
            continue
        n = bundle(doc_dir)
        if n is None:
            print(f"  skip  {doc_dir.name} (no pages/)")
            continue
        print(f"  {doc_dir.name:<34} {n:>4} pages -> pages.txt")
        total_docs += 1
        total_pages += n
    print(f"\n{total_docs} bundles | {total_pages} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
