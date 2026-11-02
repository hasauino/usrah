"""Rounded-primitive modelling kit. Every asset in the game is built from these.

All meshes are built at real size (no object scale), with characters facing -Y.
Objects created inside a `group(...)` block are parented to that group's empty,
so a model can be placed as a unit and its parts stay addressable for rigging.
"""
import math
from contextlib import contextmanager

import bmesh
import bpy
from mathutils import Euler, Quaternion, Vector

_parents = []
_offsets = []  # Per parent: world-style point its children's coordinates are measured from

# Mesh density. 1.0 is for renders; game exports use less. Multiplies circle segments.
detail = 1.0


def _seg(n):
    return max(6, int(n * detail) // 2 * 2)


def clear_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)


@contextmanager
def group(name, loc=(0, 0, 0), rot=(0, 0, 0), pivot=None):
    """Parent everything created in the block to a new empty.

    With `pivot` the empty sits at that point (a joint, in the same coordinates the parts
    use) while the parts keep their positions, so the group rotates around the joint.
    """
    empty = bpy.data.objects.new(name, None)
    _link(empty, pivot if pivot else loc, rot)
    _parents.append(empty)
    _offsets.append(Vector(pivot) if pivot else Vector())
    try:
        yield empty
    finally:
        _parents.pop()
        _offsets.pop()


def _link(ob, loc, rot):
    bpy.context.collection.objects.link(ob)
    if _parents:
        ob.parent = _parents[-1]
    ob.location = Vector(loc) - (_offsets[-1] if _offsets else Vector())
    if isinstance(rot, Quaternion):
        ob.rotation_mode = "QUATERNION"
        ob.rotation_quaternion = rot
    else:
        ob.rotation_euler = Euler([math.radians(a) for a in rot])
    return ob


def _finish(name, bm, mat, loc, rot, weighted=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    if mat:
        me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    if weighted:
        ob.modifiers.new("weighted", "WEIGHTED_NORMAL")
    return _link(ob, loc, rot)


def _radii(r):
    return (r, r, r) if isinstance(r, (int, float)) else r


def sphere(name, r, mat, loc=(0, 0, 0), rot=(0, 0, 0), clip=None, seg=48):
    """Ellipsoid. `clip` = (plane_co, plane_no), in the same space as `loc`, removes the
    side the normal points at."""
    bm = bmesh.new()
    seg = _seg(seg)
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(4, seg * 2 // 3), radius=1)
    rx, ry, rz = _radii(r)
    for v in bm.verts:
        v.co = Vector((v.co.x * rx, v.co.y * ry, v.co.z * rz))
    if clip:
        co, no = clip
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                               plane_co=Vector(co) - Vector(loc), plane_no=no, clear_outer=True)
    return _finish(name, bm, mat, loc, rot)


def rbox(name, size, r, mat, loc=(0, 0, 0), rot=(0, 0, 0), seg=4):
    """Box with rounded edges. `size` is full extents."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    bmesh.ops.bevel(bm, geom=bm.verts[:] + bm.edges[:], offset=r, segments=max(1, round(seg * detail)),
                    profile=0.5, affect="EDGES", clamp_overlap=True)
    return _finish(name, bm, mat, loc, rot, weighted=True)


def chaikin(points, iterations=2):
    """Round off a coarse profile, keeping its end points."""
    for _ in range(iterations):
        out = [points[0]]
        for a, b in zip(points, points[1:]):
            out.append((a[0] * .75 + b[0] * .25, a[1] * .75 + b[1] * .25))
            out.append((a[0] * .25 + b[0] * .75, a[1] * .25 + b[1] * .75))
        out.append(points[-1])
        points = out
    return points


def lathe(name, profile, mat, loc=(0, 0, 0), rot=(0, 0, 0), seg=48, smooth=2):
    """Spin a (radius, z) profile, bottom to top, around Z. Like a turned wooden toy."""
    profile = chaikin(profile, smooth) if smooth else profile
    # A 4-sided lathe is a deliberate pyramid, so it keeps its sides
    seg = seg if seg <= 8 else _seg(seg)
    bm = bmesh.new()
    rings = []
    for pr, pz in profile:
        if pr < 1e-5:
            rings.append([bm.verts.new((0, 0, pz))])
        else:
            rings.append([bm.verts.new((pr * math.cos(2 * math.pi * i / seg),
                                        pr * math.sin(2 * math.pi * i / seg), pz))
                          for i in range(seg)])
    for a, b in zip(rings, rings[1:]):
        for i in range(seg):
            j = (i + 1) % seg
            if len(a) == 1:
                bm.faces.new((a[0], b[i], b[j]))
            elif len(b) == 1:
                bm.faces.new((a[i], a[j], b[0]))
            else:
                bm.faces.new((a[i], a[j], b[j], b[i]))
    return _finish(name, bm, mat, loc, rot, weighted=True)


def cyl(name, r, h, mat, loc=(0, 0, 0), rot=(0, 0, 0), bevel=None, seg=48):
    """Cylinder with softened rims, centred on `loc`."""
    b = min(bevel if bevel is not None else min(r, h) * .2, r * .95, h * .49)
    arc = [(r - b + b * math.sin(a * math.pi / 8), -h / 2 + b - b * math.cos(a * math.pi / 8))
           for a in range(5)]
    profile = [(0, -h / 2)] + arc + [(pr, -pz) for pr, pz in reversed(arc)] + [(0, h / 2)]
    return lathe(name, profile, mat, loc, rot, seg=seg, smooth=0)


def torus(name, major, minor, mat, loc=(0, 0, 0), rot=(0, 0, 0), seg=64, tube_seg=16):
    seg, tube_seg = _seg(seg), _seg(tube_seg)
    bm = bmesh.new()
    rings = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        ring = []
        for j in range(tube_seg):
            b = 2 * math.pi * j / tube_seg
            rad = major + minor * math.cos(b)
            ring.append(bm.verts.new((rad * math.cos(a), rad * math.sin(a), minor * math.sin(b))))
        rings.append(ring)
    for i in range(seg):
        a, c = rings[i], rings[(i + 1) % seg]
        for j in range(tube_seg):
            k = (j + 1) % tube_seg
            bm.faces.new((a[j], c[j], c[k], a[k]))
    return _finish(name, bm, mat, loc, rot)


def ring(name, a, b, major, minor, mat):
    """Torus at point b, its axis along a -> b. For cuffs and collars on limbs."""
    turn = Vector((0, 0, 1)).rotation_difference((Vector(b) - Vector(a)).normalized())
    return torus(name, major, minor, mat, b, turn, seg=40, tube_seg=12)


def tube(name, points, radius, mat, loc=(0, 0, 0), rot=(0, 0, 0), caps=True):
    """Smooth tube through 3D points. `radius` is one value or one per point."""
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 1
    curve.bevel_resolution = max(1, int(6 * detail))
    curve.resolution_u = max(3, int(18 * detail))
    curve.use_fill_caps = True
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    radii = [radius] * len(points) if isinstance(radius, (int, float)) else radius
    for bp, co, rad in zip(spline.bezier_points, points, radii):
        bp.co = co
        bp.radius = rad
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    if mat:
        curve.materials.append(mat)
    ob = _link(bpy.data.objects.new(name, curve), loc, rot)
    if caps:
        # The caps use the tube's own space, which is where its points are
        _parents.append(ob)
        _offsets.append(Vector())
        sphere(name + "_a", radii[0], mat, points[0], seg=24)
        sphere(name + "_b", radii[-1], mat, points[-1], seg=24)
        _parents.pop()
        _offsets.pop()
    return ob


def capsule(name, a, b, r, mat, r2=None):
    """Tapered limb from point a to point b."""
    r2 = r if r2 is None else r2
    a, b = Vector(a), Vector(b)
    mid = (a + b) / 2
    half = (b - a).length / 2
    rot = Vector((0, 0, 1)).rotation_difference((b - a).normalized())
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=_seg(32), v_segments=max(4, _seg(24)), radius=1)
    for v in bm.verts:
        rad = r2 if v.co.z >= 0 else r
        v.co = Vector((v.co.x * rad, v.co.y * rad,
                       v.co.z * rad + (half if v.co.z >= 0 else -half)))
    return _finish(name, bm, mat, mid, rot)


def poly(name, points, depth, mat, loc=(0, 0, 0), rot=(0, 0, 0), bevel=.004):
    """Extrude a CCW 2D outline along +Z, softening its edges."""
    bm = bmesh.new()
    face = bm.faces.new([bm.verts.new((x, y, 0)) for x, y in points])
    region = bmesh.ops.extrude_face_region(bm, geom=[face])
    top = [g for g in region["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=(0, 0, depth))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if bevel:
        bmesh.ops.bevel(bm, geom=bm.verts[:] + bm.edges[:], offset=bevel, segments=3,
                        profile=0.5, affect="EDGES", clamp_overlap=True)
    return _finish(name, bm, mat, loc, rot, weighted=True)


def star_points(n, outer, inner, turn=0.0):
    pts = []
    for i in range(n * 2):
        a = math.pi * i / n + turn
        rad = outer if i % 2 == 0 else inner
        pts.append((rad * math.cos(a), rad * math.sin(a)))
    return pts


def glyph(name, char, size, depth, mat, loc=(0, 0, 0), rot=(0, 0, 0),
          font="/System/Library/Fonts/Supplemental/Arial Bold.ttf"):
    """A single extruded character. Blender doesn't shape Arabic, so isolated glyphs only."""
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = char
    curve.font = bpy.data.fonts.load(font, check_existing=True)
    curve.size = size
    curve.extrude = depth
    curve.bevel_depth = depth * .25
    curve.bevel_resolution = 2
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    if mat:
        curve.materials.append(mat)
    return _link(bpy.data.objects.new(name, curve), loc, rot)


class Surface:
    """An ellipsoid that face parts and emblems are glued onto, addressed by yaw/pitch degrees.

    Yaw 0, pitch 0 is the front (-Y). Positive yaw goes to +X, positive pitch goes up.
    """

    def __init__(self, center, radii):
        self.c = Vector(center)
        self.r = _radii(radii)

    def point(self, yaw, pitch, lift=0.0):
        y, p = math.radians(yaw), math.radians(pitch)
        d = Vector((math.sin(y) * math.cos(p), -math.cos(y) * math.cos(p), math.sin(p)))
        at = self.c + Vector((self.r[0] * d.x, self.r[1] * d.y, self.r[2] * d.z))
        no = Vector((d.x / self.r[0], d.y / self.r[1], d.z / self.r[2])).normalized()
        return at + no * lift

    def facing(self, yaw, pitch, roll=0.0):
        """Rotation taking local -Y (front) to the outward direction at yaw/pitch."""
        return (Quaternion((0, 0, 1), math.radians(yaw))
                @ Quaternion((1, 0, 0), math.radians(-pitch))
                @ Quaternion((0, 1, 0), math.radians(roll)))

    def patch(self, name, yaw, pitch, w, h, thick, mat, roll=0.0, lift=0.0):
        """A flattened dome, like paint or a printed mark."""
        return sphere(name, (w, thick, h), mat, self.point(yaw, pitch, lift),
                      self.facing(yaw, pitch, roll), seg=24)

    def stroke(self, name, spots, radius, mat, lift=0.0):
        """A tube following the surface through (yaw, pitch) spots."""
        return tube(name, [tuple(self.point(y, p, lift)) for y, p in spots], radius, mat)

    def emblem(self, name, points, depth, mat, yaw, pitch, lift=0.0, bevel=.002):
        """Extruded outline standing out of the surface."""
        turn = self.facing(yaw, pitch) @ Quaternion((1, 0, 0), math.radians(90))
        return poly(name, points, depth, mat, self.point(yaw, pitch, lift), turn, bevel=bevel)
