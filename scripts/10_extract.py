#!/usr/bin/env /usr/bin/python3
"""
Extract kb/sources/* into kb/corpus/<doc-id>/ per kb/manifest.yaml.

Per document, emits:
  meta.json         provenance + extraction stats
  full.txt          boilerplate-stripped, -layout preserved (human / Read)
  pages/pNNN.txt    per-page text -- THE CITATION UNIT
  search.txt        whitespace-normalized, dehyphenated (indexed, never displayed)
  links.tsv         page <TAB> url, from the PDF annotation layer

Two passes per PDF because neither tool alone suffices: pdftotext discards every
hyperlink, and pypdf's text extraction mangles the table layouts.

Idempotent. Regenerates corpus/ from sources/ on every run.
"""
import json, os, re, shutil, subprocess, sys, unicodedata
from pathlib import Path

import yaml

ROOT     = Path(__file__).resolve().parent.parent
SOURCES  = ROOT / "kb" / "sources"
STAGING  = SOURCES / "_staging"
CORPUS   = ROOT / "kb" / "corpus"
QUAR     = ROOT / "kb" / "_quarantine"
MANIFEST = ROOT / "kb" / "manifest.yaml"

MIN_CHARS_PER_PAGE = 400          # below this: probably an image scan, and we have no OCR
BOILERPLATE_RATIO  = 0.60         # a line on >60% of pages is furniture, not content

# Page-level fraud screen. Hits are REPORTED for review, never silently ingested.
FRAUD_PATTERNS = {
    "cpn":            r"\b(?:cpn|credit privacy number|credit profile number|secondary credit number|scn)\b",
    "sweep":          r"\bcredit sweep|\bsweep(?:s|ing)?\b(?=.{0,40}\b(?:credit|report|bureau))",
    "s609":           r"\bsection\s*609\b|\b609\s*(?:letter|loophole|dispute)",
    "stated_income":  r"stated[- ]income",
    "au_purchase":    r"(?:buy|purchase|rent|paid)\s+(?:a\s+)?(?:seasoned\s+)?(?:au\s+|authorized[- ]user\s+)?tradeline",
    "fullz":          r"\bfullz\b|\bdumps?\b(?=.{0,30}\bcard)",
    "guaranteed":     r"guaranteed\s+(?:removal|deletion|approval)",
}

log_lines, failures = [], []


def log(msg):
    print(msg)
    log_lines.append(msg)


def fail(doc_id, msg):
    failures.append(f"{doc_id}: {msg}")
    log(f"    !! GATE FAIL: {msg}")


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, errors="replace", **kw)


def pdf_page_count(path):
    out = run(["pdfinfo", str(path)]).stdout
    m = re.search(r"^Pages:\s+(\d+)", out, re.M)
    return int(m.group(1)) if m else None


def pdf_pages_text(path):
    """pdftotext -layout, split on the form feed it emits between pages."""
    r = run(["pdftotext", "-layout", "-enc", "UTF-8", str(path), "-"])
    if r.returncode != 0:
        return None, r.stderr.strip()
    pages = r.stdout.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()                    # trailing FF after the last page
    return pages, None


def pdf_links(path):
    """URLs live only in the annotation layer; pdftotext throws them away."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return []
    out = []
    try:
        reader = PdfReader(str(path))
        for i, page in enumerate(reader.pages, 1):
            for annot in (page.get("/Annots") or []):
                try:
                    obj = annot.get_object()
                    uri = obj.get("/A", {}).get("/URI")
                except Exception:
                    continue
                if uri:
                    out.append((i, str(uri)))
    except Exception as e:
        log(f"    (link pass failed: {e})")
    return out


def office_text(path):
    """textutil handles both legacy .doc and .docx on macOS."""
    r = run(["textutil", "-convert", "txt", "-encoding", "UTF-8", "-stdout", str(path)])
    return (r.stdout, None) if r.returncode == 0 else (None, r.stderr.strip())


HEADING = re.compile(r"^(?:[A-Z][A-Z0-9 ,''&/().:-]{6,80}|(?:CHAPTER|SECTION|STEP|PART|MODULE|LETTER)\b.{0,60})$")


def synthetic_sections(text, target=3000):
    """
    .doc/.docx have no pages, so invent a stable citation unit: split on
    heading-shaped lines, then pack to ~target chars so sections stay citable.
    """
    blocks, cur = [], []
    for line in text.splitlines():
        if HEADING.match(line.strip()) and sum(len(x) for x in cur) > 500:
            blocks.append("\n".join(cur)); cur = [line]
        else:
            cur.append(line)
    if cur:
        blocks.append("\n".join(cur))

    packed, buf = [], ""
    for b in blocks:
        if len(buf) + len(b) > target and buf:
            packed.append(buf); buf = b
        else:
            buf = f"{buf}\n{b}" if buf else b
    if buf:
        packed.append(buf)
    return packed or [text]


def find_boilerplate(pages, extra_patterns):
    """Any line appearing on >60% of pages is a header/footer, not content."""
    if len(pages) < 5:
        drop = set()
    else:
        counts = {}
        for p in pages:
            for line in {l.strip() for l in p.splitlines() if len(l.strip()) > 3}:
                counts[line] = counts.get(line, 0) + 1
        threshold = len(pages) * BOILERPLATE_RATIO
        drop = {l for l, c in counts.items() if c > threshold}
    regexes = [re.compile(p, re.I) for p in (extra_patterns or [])]
    return drop, regexes


def strip_boilerplate(page, drop, regexes):
    keep = []
    for line in page.splitlines():
        s = line.strip()
        if s in drop:
            continue
        if any(r.search(s) for r in regexes):
            continue
        keep.append(line)
    return "\n".join(keep)


def normalize_for_search(text):
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"(\w)[-‐‑]\n(\w)", r"\1\2", text)   # de-hyphenate line breaks
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def screen_fraud(pages):
    hits = {}
    for i, page in enumerate(pages, 1):
        low = page.lower()
        for name, pat in FRAUD_PATTERNS.items():
            if re.search(pat, low, re.I):
                hits.setdefault(name, []).append(i)
    return hits


def place_sources(mf):
    """Move staged files to sources/<doc-id>.<ext>; quarantined ones out of reach."""
    moved = 0
    for section, dest_dir in (("docs", SOURCES),
                              ("quarantine", QUAR),
                              ("market_intel", QUAR / "market-intel")):
        for doc_id, spec in (mf.get(section) or {}).items():
            src = STAGING / spec["source_file"]
            ext = Path(spec["source_file"]).suffix
            dst = dest_dir / f"{doc_id}{ext}"
            dest_dir.mkdir(parents=True, exist_ok=True)
            if src.exists():
                shutil.move(str(src), str(dst))
                moved += 1
            elif not dst.exists():
                fail(doc_id, f"source missing from staging and sources: {spec['source_file']}")
    return moved


def extract_one(doc_id, spec):
    ext = Path(spec["source_file"]).suffix.lower()
    src = SOURCES / f"{doc_id}{ext}"
    if not src.exists():
        fail(doc_id, "source file not found"); return None

    out = CORPUS / doc_id
    if out.exists():
        shutil.rmtree(out)
    (out / "pages").mkdir(parents=True)

    synthetic = spec.get("pagination") == "synthetic"
    links = []

    if ext == ".pdf":
        pages, err = pdf_pages_text(src)
        if pages is None:
            fail(doc_id, f"pdftotext failed: {err}"); return None
        declared = spec.get("pages")
        actual = pdf_page_count(src)
        if declared and actual and declared != actual:
            fail(doc_id, f"manifest says {declared} pages, pdfinfo says {actual}")
        if actual and len(pages) != actual:
            fail(doc_id, f"pdfinfo says {actual} pages, pdftotext produced {len(pages)}")
        links = pdf_links(src)
    elif ext in (".doc", ".docx"):
        text, err = office_text(src)
        if text is None:
            fail(doc_id, f"textutil failed: {err}"); return None
        pages, synthetic = synthetic_sections(text), True
    elif ext == ".txt":
        pages, synthetic = synthetic_sections(src.read_text(errors="replace")), True
    else:
        fail(doc_id, f"unhandled extension {ext}"); return None

    # Honour page-range scoping (partner-speaker IP inside a Coach K document).
    include = spec.get("include_pages")
    exclude = set(spec.get("exclude_pages") or [])
    scoped = []
    for i, page in enumerate(pages, 1):
        if include and i not in include:
            continue
        if i in exclude:
            continue
        scoped.append((i, page))
    if include or exclude:
        log(f"    page scope: keeping {len(scoped)}/{len(pages)} pages")

    drop, regexes = find_boilerplate([p for _, p in scoped], spec.get("boilerplate_extra"))
    prefix = "s" if synthetic else "p"

    cleaned, chars = [], 0
    for idx, page in scoped:
        text = strip_boilerplate(page, drop, regexes)
        (out / "pages" / f"{prefix}{idx:03d}.txt").write_text(text)
        cleaned.append(text)
        chars += len(text.strip())

    full = "\n\f\n".join(cleaned)
    (out / "full.txt").write_text(full)
    (out / "search.txt").write_text(normalize_for_search(full))

    if links:
        (out / "links.tsv").write_text(
            "".join(f"{p}\t{u}\n" for p, u in links))

    per_page = chars / max(len(cleaned), 1)
    if per_page < MIN_CHARS_PER_PAGE:
        fail(doc_id, f"only {per_page:.0f} chars/page — likely an image scan, and no OCR is available")

    fs = spec.get("fraud_screen")
    fraud = screen_fraud(cleaned) if fs else {}
    # "reviewed-clear" means a human read the hits and cleared them; keep the hits in
    # meta.json for the audit trail but stop nagging about them in the summary.
    fraud_status = "reviewed-clear" if fs == "reviewed-clear" else ("pending" if fraud else "clean")

    meta = {
        "doc_id": doc_id,
        "title": spec.get("title"),
        "author": spec.get("author"),
        "tier": spec.get("tier"),
        "domain": spec.get("domain"),
        "content_date": spec.get("content_date"),
        "volatility": spec.get("volatility"),
        "audience": spec.get("audience"),
        "canonize": bool(spec.get("canonize")),
        "license": spec.get("license"),
        "source_file": spec["source_file"],
        "pagination": "synthetic" if synthetic else "pdf-page",
        "page_prefix": prefix,
        "pages_extracted": len(cleaned),
        "pages_in_source": len(pages),
        "chars": chars,
        "chars_per_page": round(per_page, 1),
        "boilerplate_lines_dropped": len(drop),
        "links": len(links),
        "fraud_screen_hits": fraud,
        "fraud_screen_status": fraud_status,
        "chapters": spec.get("chapters"),
        "notes": spec.get("notes"),
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2))

    flag = f"  [fraud-screen: {', '.join(fraud)}]" if fraud and fraud_status == "pending" else ""
    log(f"    {len(cleaned):>4} pages | {per_page:>6.0f} ch/pg | {len(links):>3} links | "
        f"{len(drop):>2} boilerplate{flag}")
    return meta


def main():
    mf = yaml.safe_load(MANIFEST.read_text())
    CORPUS.mkdir(parents=True, exist_ok=True)

    # Prune corpus dirs for doc-ids no longer in the manifest (e.g. newly quarantined),
    # so a stale extraction can never be indexed or cited.
    known = set(mf["docs"])
    for d in sorted(CORPUS.iterdir()):
        if d.is_dir() and d.name not in known:
            shutil.rmtree(d)
            log(f"    pruned stale corpus dir: {d.name}")

    log("==> Placing sources by doc-id")
    log(f"    moved {place_sources(mf)} files out of staging")

    log("==> Extracting")
    metas = []
    for doc_id, spec in mf["docs"].items():
        log(f"  {doc_id}")
        m = extract_one(doc_id, spec)
        if m:
            metas.append(m)

    (CORPUS / "_index.json").write_text(json.dumps(metas, indent=2))

    log("")
    log(f"Extracted {len(metas)}/{len(mf['docs'])} documents")
    log(f"Total pages: {sum(m['pages_extracted'] for m in metas)}")
    log(f"Total chars: {sum(m['chars'] for m in metas):,}")
    screened = {m['doc_id']: list(m['fraud_screen_hits'])
                for m in metas if m.get('fraud_screen_status') == 'pending'}
    if screened:
        log("")
        log("FRAUD SCREEN — UNREVIEWED hits, review before these are trusted:")
        for d, names in screened.items():
            log(f"  {d}: {', '.join(names)}")
    if failures:
        log("")
        log(f"GATE FAILURES ({len(failures)}):")
        for f in failures:
            log(f"  {f}")

    (ROOT / "kb" / "corpus" / "_extract.log").write_text("\n".join(log_lines) + "\n")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
