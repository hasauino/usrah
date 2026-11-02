#!/usr/bin/env python3
"""Placeholder Arabic voice from the macOS "Majed" voice, one WAV per line of content.

  python3 tools/voice/generate.py

Reads unity/Assets/Resources/Content/letters.json and writes unity/Assets/Resources/Voice/, which
is gitignored: this is for development only. Real recordings replace it before release.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTENT = json.loads((ROOT / "unity/Assets/Resources/Content/letters.json").read_text())
OUT = ROOT / "unity/Assets/Resources/Voice"


def speak(key, text):
    wav = OUT / f"{key}.wav"
    if wav.exists():
        return
    aiff = OUT / f"{key}.aiff"
    subprocess.run(["say", "-v", "Majed", "-r", "150", "-o", str(aiff), text], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(aiff), "-ac", "1", "-ar", "22050", str(wav)], check=True)
    aiff.unlink()


OUT.mkdir(parents=True, exist_ok=True)
for i, item in enumerate(CONTENT["letters"]):
    speak(f"letter_{i}", item["name"])
    speak(f"word_{i}", item["word"])
for i, word in enumerate(CONTENT["numbers"]):
    speak(f"number_{i + 1}", word)
for line in CONTENT["lines"]:
    speak(line["key"], line["text"])
print(len(list(OUT.glob("*.wav"))), "clips")
