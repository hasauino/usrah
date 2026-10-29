# أسرة (usrah): design decisions

A modern, kid-friendly re-imagining of **مجموعة برامج الأسرة** (Sakhr Software, 1994–96): a living room you explore, where each object opens a learning game, hosted by a friendly robot.

The research behind these decisions lives in `reference/`. That folder is local only and gitignored, because it holds Sakhr's copyrighted material:
- `reference/videos-and-web.md`: what the original looked like and how each program played.
- `reference/original-catalog.md`: the disc contents and the extracted content banks.

Decided in the design interview, 2026-10-25 to 2026-10-29.

## Product

| # | Decision | Choice |
|---|---|---|
| Q1 | Audience | Our own family first, and a free public release. Everything that ships is new; the original is reference only. |
| Q2 | Ages | 4–10. Each game is tagged **young** (voice- and picture-led, almost no reading) or **older** (reading, quizzes). |
| Q4 | Language | Arabic only for v1. The code is localisation-ready from day one (RTL layout, all strings in tables). |
| Q5 | Faithfulness | Keep the soul: the explorable room, the host, and the mechanics that still work. Modernise the rest. |
| Q6 | Office tools | Dropped. Kids' learning programs and games only. |
| Q15 | Scope | **Slice 1:** room + host + **حروف وأرقام**, shipped end to end as a PWA. **Then:** حيوانات مرحة and احسب والعب. **Later:** تعلم الصلاة, اختبر معلوماتك, كلمات ومعاني, and an original submarine game on the console. No TV/demo catalogue. |
| Q24 | Numerals | Eastern Arabic digits (١٢٣) by default; a parent setting switches to 0–9. |
| Q25 | Privacy | No accounts and no data collection; nothing leaves the device. Up to 4 local kid profiles shown as avatars. A parent gate protects settings. |

## Content and voice

| # | Decision | Choice |
|---|---|---|
| Q12 | Content | Use the original's banks (quiz, words, animals, letters) for **structure and coverage only**. Write new items, plus public-domain proverbs. Everything is reviewed by Hassan, and religious content gets extra care. |
| Q13 | Voice | AI Arabic TTS placeholders during development, replaced with real recordings before release. Simple Modern Standard Arabic (فصحى مبسطة). |

## Characters and art

| # | Decision | Choice |
|---|---|---|
| Q11 | Cast | A host, two kids and a pet, reused across games. |
| Q18 | Identity | **نبيه** (robot host), **سارة** (girl, 8), **يوسف** (boy, 5), a small **cat**. No hijab on Sara by default; modest clothing. |
| Q18b | Host look | Keeps the original's recognisable traits (blue cap, round glasses, keypad chest, rolls in as a ball and unfolds) in a fresh design. |
| Q17 | Setting | A contemporary Arab family home with tasteful cultural cues (mashrabiya, majlis cushions, dallah, calligraphy, Arabic books). |
| Q16 | Style exploration | (a) soft vinyl toy, (b) wooden toy / Montessori, (c) a mix: vinyl characters in a wooden dollhouse room. |
| Q7 | Pipeline | Asset first: **concepts → Blender → Unity**. |
| Q8 | Concepts | AI image model (Gemini) driven by a written visual brief, plus a vector room-layout sketch (exact hotspot placement). |
| Q19 | Image API | Gemini API key in a local `.env`. Claude generates and iterates. |
| Q26 | Review | One review page per concept batch. Picked images are committed to `art/concepts/<batch>/picked/`. |
| Q10 | Modelling | Claude builds **all** models (props, environment and characters) with Blender Python scripts, renders them and checks the renders. |
| Q22 | Rigs | Rigid, segmented, toy-like parts on a simple armature (no skin deformation). Faces are swappable eye and mouth textures. Mouth shapes drive lip movement. A shared animation clip library (idle, wave, cheer, think, point, walk, sit, roll-in). |

## Technology

| # | Decision | Choice |
|---|---|---|
| Q3 | Engine and platforms | **Unity 6** (editor 6000.6.7f1). The first release is a **WebGL PWA**; iOS and Android come later. Touch-first, tablet-first. |
| Q9 | Rendering | Hybrid: the room and characters are **real-time 3D** (URP, low-poly, baked light). Mini-games are mostly **2D UI screens** that reuse the 3D characters. |
| Q27 | UI | **UI Toolkit**, which does native Arabic shaping and RTL (HarfBuzz/ICU, opt-in since Unity 6.0). Text on 3D props is baked into textures in Blender. Fallback if ever needed: RTLTMPro (MIT). |
| Q20 | Repo and hosting | `github.com/hasauino/usrah` (public), Git LFS for binaries. Hosted on **GitHub Pages**. |
| Q28 | Build and deploy | GitHub Actions + GameCI (`unity-builder` ≥ v6, image `unityci/editor:ubuntu-6000.6.7f1-webgl-*`) on push to `main` → Pages. Library and LFS caches. Secrets: `UNITY_LICENSE`, `UNITY_EMAIL`, `UNITY_PASSWORD`. Brotli compression with **Decompression Fallback** (Pages can't set `Content-Encoding`). Built-in PWA template; **the version is bumped per build** so the service-worker cache refreshes. **Addressables**: the room + host load first, and each game downloads on first open and is then available offline. Local builds until CI is set up. |
| Q23 | Licence | Code under MIT. Art, audio, characters and names all rights reserved (see `LICENSE`). |

## Technical constraints to respect

- **iPad Safari memory.** Keep the initial download small. Set Initial Memory near typical heap usage with Geometric growth. Use ASTC textures for mobile and DXT for desktop (two builds, chosen by the template).
- **Polygon and texture budgets** are set per asset class in `docs/art/pipeline.md`, written before the first model.
- **WebGPU is not targeted yet.** WebGL2 stays the default.
- **Git LFS quota:** the free plan gives 10 GiB of storage and 10 GiB of bandwidth a month, and CI checkouts count. Cache LFS in Actions, and don't commit unpicked concept candidates (`art/concepts/*/raw/` is ignored).

## Original → new room map (proposal; finalised with the room layout concept)

| Room object | Opens | Status |
|---|---|---|
| Letter cube (أ ١) | حروف وأرقام | Slice 1 |
| Camel toy | حيوانات مرحة | Next |
| Abacus | احسب والعب | Next |
| Calligraphy frame | تعلم الصلاة | Later |
| Trophy | اختبر معلوماتك | Later |
| Big Ben model | كلمات ومعاني | Later |
| Game console | Submarine game (original) | Later |
| Host نبيه | Greeting / tour / help | Slice 1 |
| Family photo frame | Kid profile picker | Slice 1 |
| Door | Parents' area (behind the parent gate) | Slice 1 |
| Clock, Hijri calendar, window | Ambient: real time and date; light follows the time of day | Slice 1 |
| Cat, plant, curtains, dallah | Ambient tap reactions | Slice 1 |

Objects for later games are present from the start but "asleep" (a gentle "coming soon" reaction from نبيه), so the room never changes layout.
