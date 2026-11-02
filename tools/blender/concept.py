"""Render a concept image from the scripted models.

  blender -b --factory-startup -P tools/blender/concept.py -- \
      --style a --subject cast --out art/concepts/batch-01/raw/cast-a.png

Subjects: cast, faces (نبيه's two face options), room.
Styles: a = soft vinyl, b = wooden toy, c = vinyl characters in a wooden room.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from usrah import cast, shapes, stage  # noqa: E402
from usrah.materials import kits  # noqa: E402


def render_cast(ckit, rkit):
    stage.studio(rkit.ink("#EADFCD"))
    cast.sara(ckit, (-.95, 0, 0), (0, 0, 8))
    cast.yusuf(ckit, (-.15, -.15, 0), (0, 0, 4))
    cast.nabeeh(ckit, (.55, -.2, 0), (0, 0, -6))
    cast.cat(ckit, (1.15, -.3, 0), (0, 0, -14))
    stage.camera((0, -6.2, 1.15), (.05, 0, .63), lens=70)


def render_faces(ckit, rkit):
    stage.studio(rkit.ink("#EADFCD"))
    cast.nabeeh(ckit, (-.42, 0, 0), (0, 0, 6), face="screen")
    cast.nabeeh(ckit, (.42, 0, 0), (0, 0, -6), face="painted")
    stage.camera((0, -4.1, .75), (0, 0, .42), lens=70)


def render_room(ckit, rkit):
    from usrah import room
    room.build(ckit, rkit)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--style", choices="abc", required=True)
    ap.add_argument("--subject", choices=["cast", "faces", "room"], required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--samples", type=int, default=128)
    args = ap.parse_args(argv)

    shapes.clear_scene()
    stage.setup_render(args.out.resolve(), args.width, args.width * 9 // 16, args.samples)
    ckit, rkit = kits(args.style)
    {"cast": render_cast, "faces": render_faces, "room": render_room}[args.subject](ckit, rkit)

    import bpy
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
