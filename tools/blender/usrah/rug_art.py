"""Paints the rug's pattern (rings and eight-point stars) into one texture.

A single textured disc lightmaps cleanly; stacked ring meshes didn't take the sun in the bake.
"""
import math
from pathlib import Path

import bpy
import numpy as np

from .materials import linear

RX, RY = 1.62, 1.1
SIZE = 2048
OUT = Path(__file__).resolve().parents[3] / "art" / "textures" / "rug.png"

CREAM = "#F6E9CF"
TERRACOTTA = "#D9734E"
GREEN = "#6E9D6D"
SUN = "#F4C542"
TEAL = "#2F9C95"

# Outer to inner: x radius, y radius, colour
RINGS = ((1.62, 1.1, TERRACOTTA), (1.52, 1.02, CREAM), (1.42, .94, GREEN), (.84, .56, CREAM), (.76, .5, TERRACOTTA))


def _rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return np.array([int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4)])


def _in_star(x, y, cx, cy, outer, inner):
    """Eight-point star test: radius limit varies with angle between the points."""
    angle = np.arctan2(y - cy, x - cx)
    radius = np.hypot(x - cx, y - cy)
    sector = np.abs(((angle + math.pi / 8) % (math.pi / 4)) - math.pi / 8) / (math.pi / 8)
    # Straight edges between point and notch, in polar form
    a = np.radians(22.5)
    edge = outer * inner * np.sin(a) / (outer * np.sin(sector * a) + inner * np.sin(a - sector * a))
    return radius <= edge


def paint():
    """Returns an RGBA float array in sRGB, with row 0 at the bottom. Supersampled for clean edges."""
    n = SIZE * 2
    xs = (np.arange(n) + .5) / n * 2 * RX - RX
    ys = (np.arange(n) + .5) / n * 2 * RY - RY
    x, y = np.meshgrid(xs, ys)
    image = np.tile(_rgb(TERRACOTTA), (n, n, 1))
    for rx, ry, color in RINGS:
        image[(x / rx) ** 2 + (y / ry) ** 2 <= 1] = _rgb(color)
    for i in range(8):
        a = math.pi * 2 * i / 8 + math.pi / 8
        image[_in_star(x, y, math.cos(a) * 1.2, math.sin(a) * .8, .1, .065)] = _rgb(SUN)
    image[_in_star(x, y, 0, 0, .4, .26)] = _rgb(CREAM)
    image[_in_star(x, y, 0, 0, .2, .13)] = _rgb(TEAL)
    small = (image[::2, ::2] + image[1::2, ::2] + image[::2, 1::2] + image[1::2, 1::2]) / 4
    return np.dstack((small, np.ones((SIZE, SIZE))))


def ensure_texture():
    """Writes art/textures/rug.png if it's missing, and returns its path."""
    if not OUT.exists():
        OUT.parent.mkdir(parents=True, exist_ok=True)
        image = bpy.data.images.new("rug_paint", SIZE, SIZE, alpha=True)
        image.colorspace_settings.name = "sRGB"
        image.pixels.foreach_set(paint().astype(np.float32).ravel())
        image.filepath_raw = str(OUT)
        image.file_format = "PNG"
        image.save()
        bpy.data.images.remove(image)
    return OUT


def material():
    """Material named `rug`: the game swaps it for its own, using the same texture."""
    mat = bpy.data.materials.get("rug")
    if mat is None:
        mat = bpy.data.materials.new("rug")
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        bsdf = nodes["Principled BSDF"]
        bsdf.inputs["Roughness"].default_value = .7
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(str(ensure_texture()), check_existing=True)
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


def add_uvs(ob):
    """Planar UVs from the disc's own x and y."""
    mesh = ob.data
    layer = mesh.uv_layers.new(name="uv")
    for loop in mesh.loops:
        co = mesh.vertices[loop.vertex_index].co
        layer.data[loop.index].uv = (co.x / (2 * RX) + .5, co.y / (2 * RY) + .5)
