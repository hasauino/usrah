"""Render the toy pictures for حروف وأرقام, and portraits for the kid profiles.

  blender -b --factory-startup -P tools/blender/render_words.py -- [only ...]

Writes transparent PNGs to art/words/ and art/portraits/, and copies them into Unity Resources.
"""
import math
import shutil
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))

from usrah import cast, shapes, stage, words  # noqa: E402
from usrah.materials import Vinyl  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SIZE = 512


def frame_all(margin=1.12, elevation=12, yaw=18):
    """Point an orthographic camera at everything in the scene, turned a little for depth."""
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    pts = []
    for ob in bpy.data.objects:
        if ob.type in {"MESH", "CURVE", "FONT"}:
            mat = ob.matrix_world
            pts += [mat @ Vector(c) for c in ob.evaluated_get(deps).bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    centre = (lo + hi) / 2
    size = max(hi.x - lo.x, hi.y - lo.y, hi.z - lo.z) * margin * 1.08
    y, e = math.radians(yaw), math.radians(elevation)
    away = Vector((math.sin(y) * math.cos(e), -math.cos(y) * math.cos(e), math.sin(e)))
    cam = stage.camera(centre + away * 8, centre, lens=50)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = size


def lights(world_strength=.8):
    stage.world("#FFF8EE", world_strength)
    stage.area_light("key", (-3, -5, 6), (0, 0, .5), (6, 6), 520, "#FFF3E2")
    stage.area_light("fill", (5, -4, 2), (0, 0, .5), (5, 5), 160, "#EEF3FF")
    stage.area_light("rim", (1, 5, 5), (0, 0, .6), (5, 3), 220, "#FFFFFF")


def render(name, folder, build, **frame):
    shapes.clear_scene()
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for item in list(block):
            block.remove(item)
    out = ROOT / "art" / folder / f"{name}.png"
    scene = stage.setup_render(out, SIZE, SIZE, 96)
    scene.render.film_transparent = True
    scene.render.image_settings.color_mode = "RGBA"
    kit = Vinyl()
    build(kit)
    lights()
    frame_all(**frame)
    bpy.ops.render.render(write_still=True)
    target = ROOT / "unity/Assets/Resources" / folder.capitalize()
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy(out, target / out.name)


PORTRAITS = [("sara", lambda k: cast.sara(k, wave=False), {"elevation": 4, "yaw": 8}),
             ("yusuf", lambda k: cast.yusuf(k), {"elevation": 4, "yaw": 8}),
             ("nabeeh", lambda k: cast.nabeeh(k), {"elevation": 4, "yaw": 8}),
             ("cat", lambda k: cast.cat(k), {"elevation": 4, "yaw": 8})]


def main():
    only = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    for name, build in words.WORDS:
        if not only or name in only:
            render(name, "words", build)
    for name, build, frame in PORTRAITS:
        if not only or f"p:{name}" in only:
            render(name, "portraits", build, **frame)


if __name__ == "__main__":
    main()
