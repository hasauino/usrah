#!/usr/bin/env bash
# Render the concept images for a batch: style, subject, output name per line.
# Usage: tools/blender/render_batch.sh [out_dir] [samples]
set -euo pipefail

BLENDER="${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${1:-$ROOT/art/concepts/batch-01/raw}"
SAMPLES="${2:-192}"
mkdir -p "$OUT"

while read -r style subject name; do
  [ -z "$style" ] && continue
  "$BLENDER" -b --factory-startup -P "$ROOT/tools/blender/concept.py" -- \
    --style "$style" --subject "$subject" --out "$OUT/$name.png" --samples "$SAMPLES" 2>&1 \
    | grep -E 'Error|error:|Traceback|File "|Saved' | sed "s#$ROOT/##"
done <<'JOBS'
a cast cast-vinyl
b cast cast-wood
a faces nabeeh-faces
a room room-a
b room room-b
c room room-c
JOBS
