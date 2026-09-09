#!/bin/bash
# Build the uploadable skill zip.
#
# The workspace uploader caps a skill at 200 files, so this ships the runtime
# surface only: SKILL.md and its references, the canon notes, the FTS index, and
# one pages.txt bundle per document. The extraction tree (kb/corpus/*/pages/,
# search.txt, meta.json), the source PDFs in kb/sources/, the quarantine, and the
# build scripts stay in the repo; nothing at answer time reads them.
#
#   scripts/40_package.sh [output.zip]

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/../../../coach-k-credit-skill.zip}"
MAX_FILES=200

cd "$ROOT"

# pages.txt is generated, so a stale bundle would ship stale text.
/usr/bin/python3 scripts/30_bundle_pages.py >/dev/null

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
DEST="$STAGE/coach-k-credit"
mkdir -p "$DEST"

copy() { mkdir -p "$DEST/$(dirname "$1")"; cp "$1" "$DEST/$1"; }

for f in SKILL.md README.md SETUP.md NOTICE.md \
         references/*.md docs/*.md frontend/*.html \
         scripts/kbsearch.py scripts/ckpage.py \
         kb/manifest.yaml kb/index/kb.sqlite3 kb/index/staff.sqlite3; do
    copy "$f"
done

find kb/canon -name '*.md' -print0 | while IFS= read -r -d '' f; do copy "$f"; done
for b in kb/corpus/*/pages.txt; do copy "$b"; done

# Gates. A zip that trips one of these is a failed upload, so fail here instead.
[ -f "$DEST/SKILL.md" ] || { echo "FATAL: no SKILL.md in the package" >&2; exit 1; }

/usr/bin/python3 - "$DEST/SKILL.md" <<'PY'
import re, sys, yaml
src = open(sys.argv[1]).read()
m = re.match(r"^---\n(.*?)\n---\n", src, re.S)
if not m:
    sys.exit("FATAL: SKILL.md has no YAML frontmatter")
raw = m.group(1)
fm = yaml.safe_load(raw) or {}
for key in ("name", "description"):
    val = fm.get(key)
    if not isinstance(val, str) or not val.strip():
        sys.exit(f"FATAL: SKILL.md frontmatter has no usable {key}")
    # The uploader reads the frontmatter line by line, so a block scalar reads as
    # absent even though PyYAML folds it into a perfectly good string. Check the
    # raw source, not the parsed value.
    line = re.search(rf"^{key}:(.*)$", raw, re.M)
    if not line or not line.group(1).strip() or line.group(1).lstrip()[0] in "|>":
        sys.exit(f"FATAL: {key} is a block scalar or empty on its own line; "
                 f"put the whole value on the {key}: line")
print(f"  frontmatter  name={fm['name']}  description={len(fm['description'])} chars")
PY

# Quarantined and x- material must never reach an uploaded artifact.
if find "$DEST" \( -path '*_quarantine*' -o -name 'x-*' \) | grep -q .; then
    echo "FATAL: quarantined material staged for upload" >&2; exit 1
fi

N=$(find "$DEST" -type f | wc -l | tr -d ' ')
if [ "$N" -gt "$MAX_FILES" ]; then
    echo "FATAL: $N files, uploader allows $MAX_FILES" >&2; exit 1
fi

rm -f "$OUT"
# -D: no directory entries, they count against the file cap.
(cd "$STAGE" && zip -q -r -D -X "$OUT" coach-k-credit)

echo "  files        $N / $MAX_FILES"
echo "  size         $(du -h "$OUT" | cut -f1)"
echo "  wrote        $OUT"
