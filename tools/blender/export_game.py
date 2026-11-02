"""Export the game's models from the scripted sources into the Unity project as FBX.

  blender -b --factory-startup -P tools/blender/export_game.py

Writes unity/Assets/Art/Models/{room,nabeeh,cat,sara,yusuf}.fbx and prints triangle counts.
Curves and text become meshes; hierarchy and object names are kept, because the game finds
hotspots and joints by name. Art direction is the locked vinyl style.
"""
import shutil
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))

from usrah import cast, room, rug_art, shapes  # noqa: E402
from usrah.materials import kits  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "unity/Assets/Art/Models"
ROOM_DETAIL = .42
CHARACTER_DETAIL = .6


def bake_curves_to_meshes():
    """Replace every curve and text object with a mesh, keeping parents and children."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for ob in [o for o in bpy.data.objects if o.type in {"CURVE", "FONT"}]:
        mesh = bpy.data.meshes.new_from_object(ob.evaluated_get(depsgraph))
        new = bpy.data.objects.new(ob.name, mesh)
        ob.name += "_old"
        new.name = new.name.removesuffix(".001")
        bpy.context.collection.objects.link(new)
        new.parent = ob.parent
        new.matrix_parent_inverse = ob.matrix_parent_inverse
        new.rotation_mode = ob.rotation_mode
        new.location = ob.location
        new.rotation_euler = ob.rotation_euler
        new.rotation_quaternion = ob.rotation_quaternion
        new.scale = ob.scale
        for child in list(ob.children):
            child.parent = new
        bpy.data.objects.remove(ob)


def triangles():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for ob in bpy.data.objects:
        if ob.type == "MESH":
            total += sum(len(p.vertices) - 2 for p in ob.evaluated_get(depsgraph).data.polygons)
    return total


def export(name, build, detail):
    shapes.clear_scene()
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for item in list(block):
            block.remove(item)
    shapes.detail = detail
    ckit, rkit = kits("a")
    build(ckit, rkit)
    for ob in [o for o in bpy.data.objects if o.type in {"CAMERA", "LIGHT"}]:
        bpy.data.objects.remove(ob)
    bake_curves_to_meshes()
    # Unity reads each material's colour back from its name, so colours arrive exact
    for mat in bpy.data.materials:
        mat.name = mat.name.replace(" #", "_")
    tris = triangles()
    objects = sum(1 for o in bpy.data.objects if o.type == "MESH")
    bpy.ops.export_scene.fbx(
        filepath=str(OUT / f"{name}.fbx"), use_selection=False, object_types={"EMPTY", "MESH"},
        apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS", use_mesh_modifiers=True,
        mesh_smooth_type="OFF", bake_space_transform=False, axis_forward="-Z", axis_up="Y",
        add_leaf_bones=False, bake_anim=False, path_mode="STRIP", embed_textures=False)
    print(f"EXPORT {name}: {tris} triangles, {objects} meshes, {len(bpy.data.materials)} materials")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    textures = ROOT / "unity/Assets/Art/Textures"
    textures.mkdir(parents=True, exist_ok=True)
    shutil.copy(rug_art.ensure_texture(), textures / "rug.png")
    export("room", lambda c, r: room.build(c, r, characters=False, lights=False), ROOM_DETAIL)
    export("nabeeh", lambda c, r: cast.nabeeh(c, pose="sit"), CHARACTER_DETAIL)
    export("cat", lambda c, r: cast.cat(c, pose="sleep"), CHARACTER_DETAIL)
    export("sara", lambda c, r: cast.sara(c), CHARACTER_DETAIL)
    export("yusuf", lambda c, r: cast.yusuf(c), CHARACTER_DETAIL)


if __name__ == "__main__":
    main()
