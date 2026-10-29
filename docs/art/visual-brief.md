# Visual brief: concept batch 1

The single source every concept prompt is written against, and the standard every concept is judged by. The decisions behind it are in `docs/DESIGN.md`.

## What we are making

A warm, toy-like 3D world for Arab children aged 4–10: a family living room where every object is a doorway to a game, hosted by **نبيه**, a small robot. It should feel like **a toy you want to pick up**: soft, chunky, tactile, bright but not loud.

**Mood words:** cozy · playful · tactile · safe · curious · sunlit · handmade-modern.

**Not:** glossy-plastic noisy (casino-style UI, neon), realistic, sharp-edged, dark, cluttered, generic-Western, stereotyped "Arabian Nights".

## Hard constraint: everything must be buildable by script in Blender

Every model is built from **simple rounded primitives** (spheres, capsules, rounded boxes, cylinders, tori, bevelled extrusions) with flat or gently textured materials. Concepts must respect this or they can't be built:

- **Shapes:** chunky, rounded, generously bevelled. No fine sculpted detail, wrinkles, hair strands or cloth folds.
- **Characters:** like designer toys or peg dolls. Heads are big (about 1/2 to 2/5 of body height), with simple stub limbs and mitten or ball hands.
- **Faces:** **flat, graphic** eyes, brows and mouth, as if painted or printed on the surface, so they can be swapped as textures. No sculpted noses (a small bump at most).
- **Hair:** solid sculpted shapes, like a toy's moulded hair. Clothing is simple shapes with a seam or trim line.
- **Text:** **no words or letters in concept images.** Image models garble Arabic. Text is added later as baked decals.

## Style directions to explore

| | (a) Soft vinyl toy | (b) Wooden toy / Montessori | (c) Mix: vinyl characters in a wooden dollhouse |
|---|---|---|---|
| **Feel** | Collectible designer toys, Toca Boca-style 3D, Animal Crossing | Hand-painted beech toys, peg dolls, felt, a dollhouse | (a)'s characters in (b)'s room |
| **Materials** | Soft matte-satin plastic, subtle subsurface | Visible wood grain, painted wood, felt, cotton | Satin vinyl figures; wood, felt and fabric room |
| **Shapes** | Inflated, pillowy | Turned (lathe) shapes, dowels, blocks | Both |
| **Palette** | Pastel-bright | Natural wood + muted primaries | Warm woods + pastel characters |

### Shared palette anchors (all directions)

| Role | Colour |
|---|---|
| Warm cream wall | `#F6E9CF` |
| Honey wood | `#D9A05B` |
| Sage / olive green | `#8DB580`, a nod to the original's green carpet |
| Teal (curtains, accents) | `#2F9C95` |
| Terracotta (cushions) | `#D9734E` |
| Sky blue (نبيه's cap) | `#3D7BD9` |
| Sunflower yellow (highlights) | `#F4C542` |

Blacks are never pure. Shadows go warm brown-violet.

### Lighting

Late-afternoon sun through a **mashrabiya screen**, casting soft geometric light patterns on the floor and wall. Soft ambient fill and gentle ambient occlusion. No harsh speculars.

## The room

**Camera:** front-on, slightly elevated, about 35mm. A stage-like "dollhouse" view: three walls visible (back wall full, side walls angled), like the original's front-on room but in 3D.

**Aspect:**
- Compose for **16:9**, with every important object inside the **central 4:3** area (iPad).
- The extra width on wide phones is decorative only.

**Contents** (position is given in `art/concepts/room-layout.svg`; that layout wins over the image model):

- **Back wall:** a large window with a wooden mashrabiya screen and teal curtains; a framed abstract calligraphy piece (a swirl of strokes, no legible text); a round clock; a wall calendar; a family photo frame.
- **Left:** a bookshelf with chunky books, a Big Ben model, a trophy and an abacus; a potted plant.
- **Right:** a low wooden cabinet with a small TV and a game console; the room door at the far right.
- **Floor:**
  - A patterned rug (geometric, sage and terracotta).
  - A **majlis corner**: floor cushions and a tray with a dallah and small cups.
  - A low table holding a big **letter cube** and a **camel toy**.
  - **نبيه's bench** at the lower right.
  - The **cat** napping on a cushion.

**Do:** tasteful, contemporary, lived-in.

**Don't:** palace arches everywhere, lanterns overload, magic carpets, camels outdoors.

## The cast

### نبيه (Nabeeh), the robot host

A redesign of the original host that keeps his recognisable traits:

- **Body:** a round, silver-white robot about knee-height to an adult. A **big round head** (about 45% of height) on a **round ball body**, so he can **curl into a ball and roll**.
- **Cap and glasses:** a **sky-blue baseball cap** with a small sunflower-yellow eight-point-star emblem, and **big round glasses** (thick frames, flat lenses).
- **Face:** on a dark screen-like face plate, shown as glowing simple shapes, which suits a robot and is easy to texture-swap. Alternatively, painted eyes on a light face.
- **Chest:** a small **keypad panel** of 3×3 rounded buttons in pastel colours.
- **Limbs:** short stubby arms with white mitten hands; short legs with **blue-and-white sneakers**.
- **Personality:** warm, curious, a bit of a bookworm. He always carries a small red book.

### سارة (Sara), girl, 8

- Confident, kind older sister; the "explainer".
- Dark brown moulded hair in a high ponytail with a teal hair band.
- A long-sleeved terracotta top, sage trousers and simple shoes.
- No hijab; modest clothing.

### يوسف (Yusuf), boy, 5

- Energetic, funny little brother.
- Short black moulded hair with a small cowlick.
- A sunflower-yellow T-shirt with a simple star, denim shorts and big sneakers.
- A slightly rounder, shorter body than Sara.

### The cat (قطة)

- A small, chubby cream-and-ginger cat, with a round head, tiny ears and a long curled tail.
- Sleepy and curious. It reacts when tapped.

### Proportions lineup

The four stand side by side. Sara is tallest, Yusuf is about 80% of her height, and نبيه is about 60% of Sara's height.

## What batch 1 must answer

1. Which style direction (a / b / c)?
2. نبيه: which variant of the face (screen face vs painted eyes) and body?
3. The kids and the cat: are the proportions and outfits right?
4. The room: does the mood, density and palette feel like "home"?

## Prompt conventions (for `tools/concepts`)

Every prompt is composed as **[style block for a/b/c] + [subject block] + [shared constraints block]**. The shared constraints repeat the hard rules: simple rounded primitives, flat graphic faces, no text, a clean background for character sheets, and a soft studio or room light.
