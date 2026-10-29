#!/usr/bin/env python3
"""Generate concept images with the Gemini API from a batch prompt file.

Usage:
  python3 tools/concepts/generate.py art/concepts/batch-01            # all jobs
  python3 tools/concepts/generate.py art/concepts/batch-01 --only room-a cast-a
  python3 tools/concepts/generate.py --list-models

A batch dir holds prompts.json:
  {
    "blocks": {"<name>": "<text>", ...},           # reusable prompt fragments
    "jobs": [{
      "id": "room-a",
      "compose": ["style_a", "room", "constraints"],  # blocks joined in order
      "aspect": "16:9",                              # optional
      "refs": ["refs/room-layout-ref.png"],          # optional, relative to batch dir
      "count": 2                                     # optional, default 1
    }]
  }

Outputs go to <batch>/raw/<job-id>/<n>.png plus <n>.json (prompt, model, refs).
raw/ is gitignored; picked images are copied to <batch>/picked/ by hand or by review.

Reads GEMINI_API_KEY (required) and GEMINI_IMAGE_MODEL (optional) from the
environment or from the repo-root .env file.
"""
import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
API = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemini-2.5-flash-image"


def load_env():
    env_file = REPO / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def request(method, path, key, body=None):
    req = urllib.request.Request(
        f"{API}/{path}",
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} from {path}: {e.read().decode(errors='replace')[:2000]}")


def list_models(key):
    models = request("GET", "models?pageSize=1000", key)["models"]
    for m in models:
        if "image" in m["name"] or "imagen" in m["name"]:
            print(m["name"], "|", m.get("displayName", ""), "|", ",".join(m.get("supportedGenerationMethods", [])))


def image_part(path):
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return {"inline_data": {"mime_type": mime, "data": base64.b64encode(path.read_bytes()).decode()}}


def run_job(job, blocks, batch_dir, model, key):
    prompt = "\n\n".join(blocks[name] for name in job["compose"])
    refs = [batch_dir / r for r in job.get("refs", [])]
    parts = [{"text": prompt}] + [image_part(r) for r in refs]
    config = {"responseModalities": ["TEXT", "IMAGE"]}
    if job.get("aspect"):
        config["imageConfig"] = {"aspectRatio": job["aspect"]}

    out_dir = batch_dir / "raw" / job["id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    start = len(list(out_dir.glob("*.png")))

    for i in range(start, start + job.get("count", 1)):
        t0 = time.time()
        resp = request("POST", f"models/{model}:generateContent", key,
                       {"contents": [{"parts": parts}], "generationConfig": config})
        cand_parts = (resp.get("candidates") or [{}])[0].get("content", {}).get("parts", [])
        images = [p["inlineData"] for p in cand_parts if "inlineData" in p]
        notes = " ".join(p["text"] for p in cand_parts if "text" in p).strip()
        if not images:
            print(f"  {job['id']} #{i}: no image returned. {notes or json.dumps(resp)[:500]}")
            continue
        img_path = out_dir / f"{i:02d}.png"
        img_path.write_bytes(base64.b64decode(images[0]["data"]))
        (out_dir / f"{i:02d}.json").write_text(json.dumps({
            "job": job["id"], "model": model, "prompt": prompt,
            "refs": [str(r.relative_to(REPO)) for r in refs], "model_notes": notes,
        }, ensure_ascii=False, indent=2))
        print(f"  {img_path.relative_to(REPO)}  ({time.time() - t0:.0f}s)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", nargs="?", type=Path)
    ap.add_argument("--only", nargs="*", help="job ids to run")
    ap.add_argument("--count", type=int, help="override images per job")
    ap.add_argument("--list-models", action="store_true")
    args = ap.parse_args()

    load_env()
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY is not set (add it to .env at the repo root)")
    if args.list_models:
        return list_models(key)
    if not args.batch:
        ap.error("batch dir required")

    batch_dir = args.batch.resolve()
    spec = json.loads((batch_dir / "prompts.json").read_text())
    model = os.environ.get("GEMINI_IMAGE_MODEL", DEFAULT_MODEL)
    jobs = [j for j in spec["jobs"] if not args.only or j["id"] in args.only]
    for job in jobs:
        if args.count:
            job["count"] = args.count
        print(f"{job['id']} × {job.get('count', 1)}  [{model}]")
        run_job(job, spec["blocks"], batch_dir, model, key)


if __name__ == "__main__":
    main()
