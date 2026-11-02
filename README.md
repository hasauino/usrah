# أسرة: برامج الأسرة

A modern, kid-friendly re-imagining of the 90s Arabic family edutainment collection **مجموعة برامج الأسرة** (Sakhr Software). It is a cozy 3D living room where every object opens a learning game, hosted by **نبيه**, a little robot.

For ages 4–10, in Arabic. It is built with Unity 6 and ships first as a web app (PWA).

## Status

Concept phase: the asset-first pipeline goes **concepts → Blender → Unity**.

## Layout

| Path | What |
|---|---|
| `docs/DESIGN.md` | Every product, art and tech decision |
| `docs/art/visual-brief.md` | The art brief that concept prompts are written against |
| `art/concepts/` | Room layout and concept batches (`<batch>/prompts.json`, `<batch>/picked/`) |
| `tools/blender/` | Scripted models (cast, room), material kits and concept renders |
| `tools/concepts/generate.py` | Optional Gemini image generation (not used; needs prepaid API credit) |

## Setup

```sh
brew install git-lfs && git lfs install
tools/blender/render_batch.sh     # renders concepts to art/concepts/batch-01/raw/ (needs Blender 4.5)
```

## Licence

Code is MIT. Art, audio and characters are all rights reserved. See [LICENSE](LICENSE).
