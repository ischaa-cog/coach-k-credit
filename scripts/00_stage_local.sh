#!/bin/bash
# Stage local source documents: unpack archives, dedupe by md5, inventory.
# Idempotent — safe to re-run. Writes nothing outside $ROOT.
set -euo pipefail

# Resolve the skill root from this script's own location, so the skill works
# no matter what the shell's working directory is.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Source documents. Override with: SRC=/path/to/docs bash 00_stage_local.sh
SRC="${SRC:-${1:-$HOME/Desktop/Coach K Credit bot material}}"
STAGING="$ROOT/kb/sources/_staging"
REPORT="$ROOT/kb/sources/_inventory.tsv"
DEDUPE="$ROOT/kb/sources/_dedupe-report.tsv"

[ -d "$SRC" ] || { echo "FATAL: source folder not found: $SRC" >&2; exit 1; }

rm -rf "$STAGING"
mkdir -p "$STAGING"
mkdir -p "$ROOT/kb/sources" "$ROOT/kb/corpus" "$ROOT/kb/index"
mkdir -p "$ROOT/kb/_quarantine/partner-ip" "$ROOT/kb/_quarantine/pii" \
         "$ROOT/kb/_quarantine/market-intel"

echo "==> Copying loose documents"
find "$SRC" -maxdepth 1 -type f \
     \( -name '*.pdf' -o -name '*.doc' -o -name '*.docx' -o -name '*.txt' \) \
     -exec cp -p {} "$STAGING/" \;

echo "==> Unpacking archives"
for z in "$SRC"/*.zip; do
  [ -e "$z" ] || continue
  echo "    $(basename "$z")"
  unzip -o -q -j "$z" -d "$STAGING/" -x '__MACOSX/*' '.DS_Store' || true
done
rm -rf "$STAGING/__MACOSX" "$STAGING/.DS_Store" 2>/dev/null || true

echo "==> Deduplicating by md5 (keeping first occurrence, alphabetical)"
# bash 3.2 on macOS has no associative arrays; use a sorted md5 list instead.
: > "$DEDUPE"
HASHES=$(mktemp)
find "$STAGING" -type f | sort | while IFS= read -r f; do
  printf '%s\t%s\n' "$(md5 -q "$f")" "$f"
done > "$HASHES"

awk -F'\t' '{ if (seen[$1] != "") print $1 "\t" $2 "\t" seen[$1]; else seen[$1]=$2 }' \
    "$HASHES" | while IFS=$'\t' read -r h dup orig; do
  printf 'DUPLICATE\t%s\t%s\t%s\n' "$h" "$(basename "$dup")" "$(basename "$orig")" >> "$DEDUPE"
  rm -f "$dup"
done
rm -f "$HASHES"

echo "==> Building inventory"
printf 'md5\tbytes\tpages\text\tfilename\n' > "$REPORT"
while IFS= read -r f; do
  h=$(md5 -q "$f")
  b=$(stat -f%z "$f")
  ext="${f##*.}"
  pages=""
  if [ "$ext" = "pdf" ]; then
    pages=$(pdfinfo "$f" 2>/dev/null | awk '/^Pages:/{print $2}') || pages=""
  fi
  printf '%s\t%s\t%s\t%s\t%s\n' "$h" "$b" "${pages:-NA}" "$ext" "$(basename "$f")" >> "$REPORT"
done < <(find "$STAGING" -type f | sort)

echo
echo "Staged:     $(find "$STAGING" -type f | wc -l | tr -d ' ') unique files"
echo "Duplicates: $(wc -l < "$DEDUPE" | tr -d ' ') removed"
echo "Inventory:  $REPORT"
echo "Dupes:      $DEDUPE"
