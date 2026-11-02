"""The home room, placed from art/concepts/room-layout.svg.

The layout's pixel coordinates are mapped to the world by wall() and floor(), so the
3D room and the hotspot sketch stay in register. Tappable objects are named groups.
"""
import math
from pathlib import Path

import bpy

from . import cast, stage
from .materials import linear
from .shapes import (cyl, glyph, group, lathe, poly, rbox, sphere, star_points, torus,
                     tube)

# Room and camera. Camera looks along +Y with lens shift, so verticals stay straight.
WIDTH = 6.0
HEIGHT = 2.78
BACK_Y = 4.0
CAM_DIST = 8.64
CAM_H = 2.3
LENS = 35.0
PX_W = 1600
FOCAL_PX = PX_W * LENS / 36
HORIZON_PX = 560 - FOCAL_PX * CAM_H / CAM_DIST
PX_TO_M = WIDTH / 1080

CREAM = "#F6E9CF"
HONEY = "#D9A05B"
PALE_WOOD = "#E7C793"
DARK_WOOD = "#A9713C"
SAGE = "#8DB580"
TEAL = "#2F9C95"
TERRACOTTA = "#D9734E"
SKY = "#3D7BD9"
SUN = "#F4C542"
BRASS = "#D6A83F"
RED = "#C43D3D"
AMIRI = Path(__file__).resolve().parents[3] / "fonts" / "Amiri-Bold.ttf"
BOOK_COLORS = [RED, TEAL, SUN, SKY, TERRACOTTA, SAGE, "#7A5FA8"]


def wall(px, py):
    """(x, z) on the back wall for a layout pixel."""
    return (px - 800) * PX_TO_M, (560 - py) * PX_TO_M


def floor(px, py):
    """(x, y) on the floor for a layout pixel."""
    d = FOCAL_PX * CAM_H / (py - HORIZON_PX)
    return (px - 800) * d / FOCAL_PX, BACK_Y - CAM_DIST + d


def _shell(kit):
    wall_mat = kit.plaster(CREAM)
    rim = kit.natural(HONEY)
    t = .14
    win_l, win_top = wall(640, 110)
    win_r, win_bot = wall(960, 430)
    y = BACK_Y + t / 2
    with group("shell"):
        # Back wall in four pieces around a real opening, so sun can pass through the lattice
        rbox("wall_left", (win_l + WIDTH / 2 + t, t, HEIGHT), .01, wall_mat,
             ((win_l - WIDTH / 2 - t) / 2, y, HEIGHT / 2))
        rbox("wall_right", (WIDTH / 2 - win_r + t, t, HEIGHT), .01, wall_mat,
             ((win_r + WIDTH / 2 + t) / 2, y, HEIGHT / 2))
        rbox("wall_below", (win_r - win_l, t, win_bot), .01, wall_mat, (0, y, win_bot / 2))
        rbox("wall_above", (win_r - win_l, t, HEIGHT - win_top), .01, wall_mat,
             (0, y, (HEIGHT + win_top) / 2))
        # Side walls, open towards the camera like a dollhouse
        length = BACK_Y + 3.2
        for side, sign in (("left", -1), ("right", 1)):
            rbox(f"wall_{side}", (t, length, HEIGHT), .01, wall_mat,
                 (sign * (WIDTH + t) / 2, BACK_Y - length / 2, HEIGHT / 2))
            rbox(f"cap_{side}", (t + .05, length + .05, .06), .02, rim,
                 (sign * (WIDTH + t) / 2, BACK_Y - length / 2, HEIGHT + .03))
            rbox(f"skirt_{side}", (.04, length, .16), .012, rim,
                 (sign * (WIDTH / 2 - .02), BACK_Y - length / 2, .08))
        rbox("cap_back", (WIDTH + 2 * t + .05, t + .05, .06), .02, rim, (0, y, HEIGHT + .03))
        rbox("skirt_back", (WIDTH, .04, .16), .012, rim, (0, BACK_Y - .02, .08))

        if kit.wood:
            # Pale planks
            n = 11
            w = WIDTH / n
            for i in range(n):
                # Built upright and laid down, so the grain runs along the plank
                rbox(f"plank_{i}", (w - .006, .05, BACK_Y + 3.4), .006, kit.natural(PALE_WOOD),
                     (-WIDTH / 2 + w * (i + .5), BACK_Y - (BACK_Y + 3.4) / 2, -.025), (90, 0, 0))
        else:
            rbox("floor", (WIDTH + .3, BACK_Y + 3.4, .05), .01, kit.paint(SAGE),
                 (0, BACK_Y - (BACK_Y + 3.4) / 2, -.025))


def _window(kit):
    wood = kit.natural(DARK_WOOD if kit.wood else HONEY)
    l, top = wall(640, 110)
    r, bot = wall(960, 430)
    cx, cz = (l + r) / 2, (top + bot) / 2
    w, h = r - l, top - bot
    y = BACK_Y + .02
    with group("window"):
        # Frame
        rbox("frame_top", (w + .1, .16, .08), .02, wood, (cx, y, top))
        rbox("frame_bot", (w + .18, .22, .08), .02, wood, (cx, y - .03, bot))
        for sign in (-1, 1):
            rbox(f"frame_{sign}", (.08, .16, h), .02, wood, (cx + sign * w / 2, y, cz))

        # Mashrabiya lattice: diagonal bars with turned beads at the crossings
        step = .15
        bars = []
        reach = int((w + h) / step) + 2
        for sign in (-1, 1):
            for i in range(-reach, reach):
                # Line through (cx + i*step, cz) with slope +-1, clipped to the opening
                pts = _clip_diagonal(i * step, sign, w / 2, h / 2)
                if pts:
                    bars.append(pts)
        with group("mashrabiya"):
            for i, (a, b) in enumerate(bars):
                mid = ((a[0] + b[0]) / 2 + cx, y, (a[1] + b[1]) / 2 + cz)
                length = math.dist(a, b)
                angle = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
                rbox(f"bar_{i}", (length, .022, .016), .006, wood, mid, (0, -angle, 0), seg=2)
            for i in range(-reach, reach):
                for j in range(-reach, reach):
                    bx, bz = (i * step + j * step) / 2, (j * step - i * step) / 2
                    if abs(bx) < w / 2 - .02 and abs(bz) < h / 2 - .02:
                        sphere(f"bead_{i}_{j}", .017, wood, (cx + bx, y, cz + bz), seg=10)

        _view_outside(kit, cx, cz, w, h)

        # Teal curtains: chunky pleats pinched by a tie
        rod = kit.natural(HONEY)
        cyl("rod", .022, 2.5, rod, (cx, y - .2, top + .13), (0, 90, 0))
        for end in (-1, 1):
            sphere(f"rod_end_{end}", .04, rod, (cx + end * 1.25, y - .2, top + .13), seg=16)
        cloth = kit.cloth(TEAL)
        for sign in (-1, 1):
            base = cx + sign * (w / 2 + .1)
            for i, off in enumerate((-.09, 0, .09)):
                radius_top, radius_low = .07, .082
                tube(f"curtain_{sign}_{i}",
                     [(base + off * 1.2, y - .2, top + .1),
                      (base + off * 1.1, y - .2 - .01, top - .55),
                      (base + off * .55 + sign * .02, y - .22, cz - .24),
                      (base + off * 1.0 + sign * .02, y - .21, bot - .1),
                      (base + off * 1.25 + sign * .03, y - .2, bot - .42)],
                     [radius_top, radius_top + .01, .05, radius_low, radius_low], cloth)
            torus(f"curtain_tie_{sign}", .13, .02, kit.paint(SUN),
                  (base + sign * .02, y - .22, cz - .24), (0, 0, 0))


def _view_outside(kit, cx, cz, w, h):
    """Late-afternoon sky, hills and round trees. None of it blocks the sun."""
    sky = bpy.data.materials.new("sky")
    sky.use_nodes = True
    nodes, links = sky.node_tree.nodes, sky.node_tree.links
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0, 0, 0, 1)
    bsdf.inputs["Emission Strength"].default_value = 1.0
    coord = nodes.new("ShaderNodeTexCoord")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = linear("#FFE9C4")
    ramp.color_ramp.elements[0].position = .25
    ramp.color_ramp.elements[1].color = linear("#8CC8E8")
    ramp.color_ramp.elements[1].position = .85
    links.new(coord.outputs["Generated"], sep.inputs["Vector"])
    links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Emission Color"])
    y = BACK_Y + 1.2
    parts = [rbox("sky", (w + .6, .02, h + .6), .001, sky, (cx, y, cz))]
    parts.append(sphere("hill_far", (1.3, .02, .55), kit.glow("#A9CF9B", 1.0), (cx + .45, y - .1, cz - h * .62), seg=32))
    parts.append(sphere("hill_near", (1.2, .02, .42), kit.glow("#8DBE85", 1.0), (cx - .6, y - .2, cz - h * .66), seg=32))
    for i, (dx, dz, rx, rz) in enumerate(((-.42, -.18, .17, .24), (.5, -.1, .2, .28), (.1, -.3, .12, .16))):
        parts.append(sphere(f"tree_{i}", (rx, .02, rz), kit.glow("#6FA874", .9), (cx + dx, y - .3, cz + dz), seg=24))
        parts.append(rbox(f"trunk_{i}", (.04, .02, .3), .01, kit.glow("#8A6238", 1.0), (cx + dx, y - .25, cz + dz - rz - .1)))
    for part in parts:
        part.visible_shadow = False


def _clip_diagonal(c, slope, hw, hh):
    """Clip the line z = slope * (x - c) to the rectangle; returns two points or None."""
    pts = []
    for x in (-hw, hw):
        z = slope * (x - c)
        if -hh <= z <= hh:
            pts.append((x, z))
    for z in (-hh, hh):
        x = c + z / slope
        if -hw < x < hw:
            pts.append((x, z))
    return (pts[0], pts[1]) if len(pts) >= 2 and pts[0] != pts[1] else None


def _frame(kit, name, px0, py0, px1, py1, wood=HONEY, y=None):
    """Picture frame hung on the back wall. Returns its centre and inner size."""
    x0, z1 = wall(px0, py0)
    x1, z0 = wall(px1, py1)
    w, h = x1 - x0, z1 - z0
    at = (x0 + w / 2, (y if y is not None else BACK_Y - .025), z0 + h / 2)
    rbox(f"{name}_frame", (w, .05, h), .018, kit.natural(wood), at)
    return at, (w - .09, h - .09)


def _family_photo(kit):
    with group("family_photo"):
        at, (w, h) = _frame(kit, "photo", 490, 150, 595, 245)
        rbox("photo_mat", (w, .012, h), .003, kit.paint("#FBF4E2"), (at[0], at[1] - .025, at[2]))
        rbox("photo_sky", (w * .86, .006, h * .78), .002, kit.ink("#BFE3E0"), (at[0], at[1] - .031, at[2]))
        # Family as four simple figures
        for dx, r, color in ((-.15, .05, TERRACOTTA), (-.05, .056, SKY), (.06, .04, SUN), (.15, .034, SAGE)):
            base = at[2] - h * .32
            sphere("fig_body", (r * 1.05, .008, r * 1.5), kit.ink(color), (at[0] + dx, at[1] - .036, base + r * .6), seg=16)
            sphere("fig_head", (r * .78, .008, r * .78), kit.ink("#C68D62"), (at[0] + dx, at[1] - .037, base + r * 2.1), seg=16)


def _calligraphy(kit):
    """The word الله, using the font's dedicated ligature so it's written correctly."""
    with group("calligraphy"):
        at, (w, h) = _frame(kit, "calligraphy", 1010, 140, 1120, 270, wood=BRASS)
        rbox("cal_ground", (w, .012, h), .003, kit.paint("#1F4E79"), (at[0], at[1] - .025, at[2]))
        gold = kit.metal(SUN)
        # The ligature's marks sit high in its em box, so centre it by eye
        size = w * 1.9
        glyph("allah", "\uFDF2", size, .004, gold, (at[0], at[1] - .036, at[2] - size * .104), (90, 0, 0),
              font=str(AMIRI))


def _clock(kit):
    x, z = wall(1210, 165)
    r = 42 * PX_TO_M * 1.0
    with group("clock", (x, BACK_Y - .03, z), (90, 0, 0)):
        cyl("clock_case", r, .05, kit.natural(HONEY))
        cyl("clock_face", r * .84, .012, kit.paint("#FBF4E2"), (0, 0, .026))
        for i in range(12):
            a = math.pi * 2 * i / 12
            sphere(f"tick_{i}", (r * .055, r * .055, .004), kit.ink("#34405A" if i % 3 == 0 else "#A79F8F"),
                   (math.sin(a) * r * .68, math.cos(a) * r * .68, .033), seg=12)
        # 4:30-ish, late afternoon like the light
        rbox("hand_hour", (r * .1, r * .46, .008), .003, kit.ink("#34405A"),
             (r * .17, -r * .13, .04), (0, 0, 52))
        rbox("hand_min", (r * .07, r * .66, .008), .003, kit.ink(RED), (-.0, -r * .28, .047))
        cyl("hand_pin", r * .07, .016, kit.metal(BRASS), (0, 0, .05))


def _calendar(kit):
    x0, z1 = wall(1170, 230)
    x1, z0 = wall(1255, 330)
    w, h = x1 - x0, z1 - z0
    cx, cz = x0 + w / 2, z0 + h / 2
    y = BACK_Y - .02
    with group("calendar"):
        rbox("cal_board", (w, .02, h), .012, kit.paint("#FBF4E2"), (cx, y, cz))
        rbox("cal_head", (w * .98, .03, h * .24), .012, kit.paint(TEAL), (cx, y - .01, z1 - h * .12))
        rbox("cal_pad", (w * .82, .025, h * .6), .004, kit.paint("#FFFFFF"), (cx, y - .015, z0 + h * .36))
        # Hijri crescent on the header, a block for the date, rows of dots. Real dates come
        # later as a texture.
        sphere("cal_moon", (w * .085, .006, w * .085), kit.ink(SUN), (cx, y - .03, z1 - h * .12), seg=20)
        sphere("cal_moon_cut", (w * .072, .007, w * .072), kit.ink(TEAL), (cx + w * .035, y - .032, z1 - h * .11), seg=20)
        rbox("cal_day", (w * .36, .008, h * .24), .012, kit.ink(TERRACOTTA), (cx, y - .03, z0 + h * .45))
        for row in range(2):
            for col in range(5):
                sphere(f"cal_dot_{row}_{col}", (.012, .004, .012), kit.ink("#B9AE9B"),
                       (cx + (col - 2) * w * .14, y - .03, z0 + h * (.15 - row * .07 + .04)), seg=10)


def _bookshelf(kit):
    wood = kit.natural(HONEY)
    x0, top = wall(270, 130)
    x1, _ = wall(470, 130)
    w = x1 - x0
    cx = x0 + w / 2
    depth = .38
    y = BACK_Y - depth / 2 - .005
    _, s1 = wall(0, 260)
    _, s2 = wall(0, 390)
    with group("bookshelf"):
        rbox("shelf_back", (w, .03, top), .01, kit.natural(PALE_WOOD), (cx, BACK_Y - .02, top / 2))
        for sign in (-1, 1):
            rbox(f"shelf_side_{sign}", (.06, depth, top), .02, wood, (cx + sign * (w - .06) / 2, y, top / 2))
        for name, z in (("top", top - .025), ("upper", s1), ("middle", s2), ("bottom", .08)):
            rbox(f"shelf_{name}", (w, depth, .055), .018, wood, (cx, y, z))

    # Top shelf: chunky books and the Big Ben model
    _, z_top = wall(0, 260)
    z_top += .03
    with group("books"):
        x = wall(285, 0)[0]
        for i, (width, height) in enumerate(((.085, .5), (.075, .56), (.09, .46), (.07, .53), (.085, .48), (.075, .55))):
            rbox(f"book_{i}", (width, .25, height), .014, kit.paint(BOOK_COLORS[i % len(BOOK_COLORS)]),
                 (x + width / 2, y + .02, z_top + height / 2))
            rbox(f"book_band_{i}", (width + .002, .25, .02), .004, kit.paint(SUN if i % 2 else CREAM),
                 (x + width / 2, y + .019, z_top + height * .72))
            x += width + .006
    _big_ben(kit, wall(427, 0)[0], y + .03, z_top)

    # Middle shelf
    _, z_mid = wall(0, 390)
    z_mid += .03
    _trophy(kit, wall(325, 0)[0], y + .02, z_mid)
    _abacus(kit, wall(412, 0)[0], y + .03, z_mid)

    # Bottom shelf: a plant and stacking toys
    z_bot = .11
    _potted_plant(kit, wall(335, 0)[0], y + .03, z_bot)
    with group("stacking_rings", (wall(425, 0)[0], y + .03, z_bot)):
        cyl("ring_base", .1, .03, kit.natural(PALE_WOOD), (0, 0, .015))
        cyl("ring_peg", .018, .34, kit.natural(PALE_WOOD), (0, 0, .17))
        for i, (radius, color) in enumerate(((.095, RED), (.082, SUN), (.068, TEAL), (.054, SKY))):
            torus(f"ring_{i}", radius - .02, .032, kit.paint(color), (0, 0, .062 + i * .062), seg=40, tube_seg=14)


def _big_ben(kit, x, y, z):
    stone = kit.natural("#E3CFA5")
    roof = kit.paint("#2C4A6B")
    with group("big_ben", (x, y, z)):
        rbox("base", (.27, .27, .05), .012, kit.natural(DARK_WOOD), (0, 0, .025))
        rbox("tower", (.15, .15, .36), .012, stone, (0, 0, .23))
        for i in range(3):
            rbox(f"band_{i}", (.16, .16, .014), .005, kit.natural(HONEY), (0, 0, .1 + i * .1))
        rbox("clock_block", (.185, .185, .15), .018, stone, (0, 0, .45))
        cyl("clock_face", .066, .012, kit.paint("#FBF4E2"), (0, -.094, .45), (90, 0, 0))
        torus("clock_ring", .066, .008, kit.metal(BRASS), (0, -.098, .45), (90, 0, 0), seg=32, tube_seg=8)
        rbox("hand_a", (.008, .006, .05), .002, kit.ink("#34405A"), (0, -.102, .47))
        rbox("hand_b", (.036, .006, .008), .002, kit.ink("#34405A"), (.016, -.102, .45))
        lathe("spire", [(.125, .525), (.095, .56), (.05, .62), (.018, .69), (.0, .72)], roof, seg=4, smooth=0,
              rot=(0, 0, 45))
        sphere("spire_tip", .012, kit.metal(BRASS), (0, 0, .725), seg=12)


def _trophy(kit, x, y, z):
    gold = kit.metal(SUN)
    with group("trophy", (x, y, z)):
        rbox("base", (.2, .2, .07), .018, kit.natural(DARK_WOOD), (0, 0, .035))
        lathe("cup", [(.0, .07), (.085, .075), (.05, .1), (.025, .135), (.022, .2), (.04, .225), (.11, .27),
                      (.135, .36), (.14, .44), (.122, .445), (.11, .36), (.0, .3)], gold, smooth=2)
        for sign in (-1, 1):
            tube(f"handle_{sign}", [(sign * .13, 0, .42), (sign * .2, 0, .4), (sign * .19, 0, .32), (sign * .115, 0, .285)],
                 .014, gold)
        sphere("star", (.03, .006, .03), kit.paint(RED), (0, -.128, .37), seg=16)


def _abacus(kit, x, y, z):
    frame = kit.natural(DARK_WOOD if kit.wood else HONEY)
    w, h = .38, .4
    rods = 4
    with group("abacus", (x, y, z)):
        rbox("foot", (w + .06, .14, .035), .012, frame, (0, 0, .0175))
        for sign in (-1, 1):
            rbox(f"post_{sign}", (.038, .05, h), .014, frame, (sign * w / 2, 0, h / 2 + .02))
        rbox("top", (w + .05, .05, .038), .014, frame, (0, 0, h + .02))
        colors = [RED, SUN, TEAL, SKY]
        for r in range(rods):
            z_rod = .09 + r * (h - .12) / (rods - 1)
            cyl(f"rod_{r}", .006, w, kit.metal("#C9CDD1"), (0, 0, z_rod), (0, 90, 0), seg=12)
            n_left = 2 + (r * 2) % 3
            for i in range(6):
                bx = -w / 2 + .045 + i * .04 if i < n_left else w / 2 - .045 - (5 - i) * .04
                sphere(f"bead_{r}_{i}", (.02, .034, .034), kit.paint(colors[r]), (bx, 0, z_rod), seg=20)


def _potted_plant(kit, x, y, z):
    with group("plant", (x, y, z)) as plant:
        plant.scale = (1.25, 1.25, 1.25)
        lathe("pot", [(.0, 0), (.09, 0), (.115, .05), (.125, .15), (.135, .165), (.12, .17), (.0, .15)],
              kit.paint(TERRACOTTA), smooth=1)
        sphere("soil", (.11, .11, .012), kit.ink("#5B3D2C"), (0, 0, .155), seg=20)
        leaf = kit.paint("#5FA36A")
        leaf2 = kit.paint("#7DBC7B")
        for i, (a, length, up) in enumerate(((0, .2, .28), (65, .17, .34), (130, .2, .24), (195, .17, .32),
                                             (260, .19, .26), (320, .15, .36), (30, .09, .4))):
            ang = math.radians(a)
            tip = (math.cos(ang) * length, math.sin(ang) * length * .55, .155 + up)
            mat = leaf if i % 2 else leaf2
            tube(f"stem_{i}", [(0, 0, .155), (tip[0] * .5, tip[1] * .5, .155 + up * .7), tip], .007, kit.paint("#4C8A57"), caps=False)
            sphere(f"leaf_{i}", (.075, .03, .04), mat, tip, (0, -math.degrees(math.atan2(up * .3, length)) * math.cos(ang) * .8, a), seg=20)


def _cabinet(kit):
    wood = kit.natural(HONEY)
    x0, top = wall(960, 440)
    x1, _ = wall(1280, 440)
    w = x1 - x0
    cx = x0 + w / 2
    depth = .42
    y = BACK_Y - depth / 2 - .01
    with group("cabinet"):
        rbox("cab_body", (w, depth, top - .06), .025, wood, (cx, y, (top - .06) / 2 + .06))
        rbox("cab_top", (w + .05, depth + .05, .05), .02, kit.natural(DARK_WOOD if kit.wood else PALE_WOOD),
             (cx, y, top + .01))
        door_w = w / 3 - .025
        for i in range(3):
            dx = cx + (i - 1) * (door_w + .025)
            rbox(f"door_{i}", (door_w, .025, top - .13), .012, kit.natural(PALE_WOOD), (dx, y - depth / 2 - .005, (top + .03) / 2 + .01))
            star = star_points(8, .06, .038)
            poly(f"door_star_{i}", star, .008, kit.paint(TERRACOTTA if i == 1 else TEAL),
                 (dx, y - depth / 2 - .018, (top + .03) / 2 + .01), (90, 0, 0), bevel=.002)
            sphere(f"knob_{i}", .016, kit.metal(BRASS), (dx + door_w * .36 * (1 if i < 2 else -1), y - depth / 2 - .027, (top + .03) / 2), seg=12)
        for sign in (-1, 1):
            rbox(f"foot_{sign}", (.09, depth * .9, .06), .018, kit.natural(DARK_WOOD), (cx + sign * (w / 2 - .1), y, .03))

    # Small rounded TV (décor for now)
    tx0, tv_top = wall(990, 330)
    tx1, _ = wall(1150, 330)
    tv_w = tx1 - tx0
    tv_h = tv_top - top - .05
    tv_c = tx0 + tv_w / 2
    tv_z = top + .05 + tv_h / 2
    with group("tv"):
        rbox("tv_body", (tv_w, .24, tv_h), .05, kit.paint(TEAL), (tv_c, y + .04, tv_z))
        rbox("tv_screen", (tv_w * .78, .03, tv_h * .72), .03, kit.glass("#27364F"), (tv_c - tv_w * .03, y - .08, tv_z))
        sphere("tv_shine", (tv_w * .1, .004, tv_h * .1), kit.ink("#5B7BA3"), (tv_c - tv_w * .24, y - .096, tv_z + tv_h * .17), seg=16)
        for i, zz in enumerate((.22, .0, -.22)):
            sphere(f"tv_knob_{i}", (.024, .012, .024), kit.paint(SUN), (tv_c + tv_w * .43, y - .082, tv_z + zz * tv_h), seg=16)
        for sign in (-1, 1):
            tube(f"antenna_{sign}", [(tv_c, y + .04, tv_z + tv_h / 2), (tv_c + sign * .14, y + .04, tv_z + tv_h / 2 + .22)], .007,
                 kit.metal("#C9CDD1"))

    # Game console (future submarine game)
    gx, _ = wall(1217, 0)
    with group("console", (gx, y - .04, top + .035)):
        rbox("console_body", (.46, .25, .1), .035, kit.paint("#FBF4E2"), (0, 0, .05))
        rbox("console_slot", (.2, .03, .018), .006, kit.ink("#34405A"), (0, .06, .1))
        rbox("console_panel", (.4, .02, .05), .014, kit.paint(TERRACOTTA), (0, -.122, .05))
        for i, color in enumerate((SUN, SKY)):
            sphere(f"console_btn_{i}", (.018, .01, .018), kit.paint(color), (.1 + i * .06, -.135, .05), seg=14)
        # Joystick
        rbox("stick_base", (.12, .12, .03), .012, kit.paint("#34405A"), (-.11, -.03, .115))
        cyl("stick", .012, .1, kit.metal("#C9CDD1"), (-.11, -.03, .175), seg=12)
        sphere("stick_ball", .03, kit.paint(RED), (-.11, -.03, .235), seg=20)


def _door(kit):
    """The room door on the right wall. Behind it: the parents' area."""
    wood = kit.natural(DARK_WOOD if kit.wood else HONEY)
    panel = kit.natural(HONEY if kit.wood else PALE_WOOD)
    y0, y1 = 3.21, 3.92
    w = y1 - y0
    h = 2.12
    x = WIDTH / 2 - .02
    cy = (y0 + y1) / 2
    with group("door"):
        rbox("door_frame_a", (.05, .08, h + .06), .015, wood, (x, y0 - .03, (h + .06) / 2))
        rbox("door_frame_b", (.05, .08, h + .06), .015, wood, (x, y1 + .03, (h + .06) / 2))
        rbox("door_frame_top", (.05, w + .14, .08), .015, wood, (x, cy, h + .03))
        rbox("door_slab", (.04, w, h), .012, wood, (x + .004, cy, h / 2))
        for i, (zc, zh) in enumerate(((.55, .78), (1.54, .86))):
            rbox(f"door_panel_{i}", (.018, w - .2, zh), .008, panel, (x - .018, cy, zc))
        sphere("door_knob", .042, kit.metal(BRASS), (x - .05, y0 + .09, 1.02), seg=20)


def _rug(kit):
    x, y = floor(800, 745)
    with group("rug", (x, y, 0)):
        rings = ((1.62, 1.1, TERRACOTTA), (1.52, 1.02, CREAM), (1.42, .94, SAGE if kit.wood else "#6E9D6D"),
                 (1.0, .66, CREAM), (.92, .6, TERRACOTTA))
        for i, (rx, ry, color) in enumerate(rings):
            sphere(f"rug_{i}", (rx, ry, .012 + i * .001), kit.cloth(color), (0, 0, .006 + i * .0015), seg=64)
        star_mat = kit.cloth(SUN)
        for i in range(8):
            a = math.pi * 2 * i / 8 + math.pi / 8
            poly(f"rug_star_{i}", star_points(8, .1, .065), .006, star_mat,
                 (math.cos(a) * 1.2, math.sin(a) * .8, .022), bevel=.002)
        poly("rug_center", star_points(8, .4, .26), .006, kit.cloth(CREAM), (0, 0, .024), bevel=.002)
        poly("rug_center_2", star_points(8, .2, .13), .006, kit.cloth(TEAL), (0, 0, .03), bevel=.002)


def _low_table(kit):
    x, y = floor(800, 710)
    h = .28
    wood = kit.natural(HONEY)
    with group("low_table", (x, y + .15, 0)):
        rbox("table_top", (1.06, .62, .05), .022, wood, (0, 0, h))
        for sx in (-1, 1):
            for sy in (-1, 1):
                lathe(f"leg_{sx}_{sy}", [(.0, 0), (.04, .0), (.032, .05), (.044, .14), (.03, .26), (.0, .26)],
                      kit.natural(DARK_WOOD), (sx * .44, sy * .23, 0), seg=20)
    return x, y + .15, h + .025


def _letter_cube(kit, table):
    tx, ty, tz = table
    s = .36
    with group("letter_cube", (tx - .26, ty - .02, tz + s / 2), (0, 0, -22)):
        rbox("cube", (s, s, s), .055, kit.paint(RED))
        glyph("letter", "أ", .42, .012, kit.paint("#FBF4E2"), (0, -s / 2 - .002, -.01), (90, 0, 0))
        glyph("digit", "١", .42, .012, kit.paint(SUN), (s / 2 + .002, 0, -.01), (90, 0, 90))
        rbox("cube_top", (s * .62, s * .62, .01), .004, kit.paint(SUN), (0, 0, s / 2))


def _camel(kit, table):
    """A wooden pull-along camel on wheels."""
    tx, ty, tz = table
    body = kit.natural(HONEY) if kit.wood else kit.paint("#E2B571")
    dark = kit.natural(DARK_WOOD) if kit.wood else kit.paint("#BF8A4A")
    with group("camel_toy", (tx + .27, ty - .02, tz), (0, 0, -22)):
        rbox("cart", (.36, .17, .03), .012, kit.paint(TEAL), (0, 0, .055))
        for sx in (-1, 1):
            for sy in (-1, 1):
                cyl(f"wheel_{sx}_{sy}", .036, .02, kit.paint(RED), (sx * .13, sy * .098, .036), (90, 0, 0), seg=20)
        for sx in (-1, 1):
            for sy in (-1, 1):
                cyl(f"leg_{sx}_{sy}", .018, .09, body, (sx * .09, sy * .045, .11), seg=14)
        sphere("camel_body", (.16, .085, .07), body, (0, 0, .19))
        sphere("hump", (.078, .062, .075), body, (.015, 0, .265))
        rbox("saddle", (.12, .11, .012), .005, kit.cloth(TERRACOTTA) if kit.wood else kit.paint(TERRACOTTA), (.015, 0, .335))
        tube("neck", [(-.12, 0, .21), (-.19, 0, .28), (-.2, 0, .36)], [.045, .036, .036], body)
        sphere("camel_head", (.056, .04, .038), body, (-.24, 0, .385))
        for sign in (-1, 1):
            sphere(f"eye_{sign}", (.007, .007, .007), kit.ink("#2B2230"), (-.25, sign * .036, .4), seg=10)
            sphere(f"ear_{sign}", (.012, .012, .018), dark, (-.205, sign * .03, .425), seg=10)
        sphere("muzzle", (.024, .03, .022), dark, (-.285, 0, .375), seg=14)
        tube("tail", [(.15, 0, .21), (.185, 0, .17), (.19, 0, .12)], .009, dark)


def _majlis(kit):
    """The floor seating corner, against the left wall."""
    y0, y1 = 1.35, 3.25
    x_wall = -WIDTH / 2
    with group("majlis"):
        rbox("mattress", (1.12, y1 - y0, .17), .06, kit.cloth(TERRACOTTA), (x_wall + .6, (y0 + y1) / 2, .085))
        for i, cy in enumerate((1.68, 2.3, 2.92)):
            color = (TEAL, SUN, TEAL)[i]
            rbox(f"back_cushion_{i}", (.24, .6, .46), .095, kit.cloth(color), (x_wall + .17, cy, .39), (0, -12, 0))
        rbox("corner_cushion", (.46, .24, .36), .085, kit.cloth(SAGE), (x_wall + .36, y1 - .1, .35), (9, 0, 0))
        tube("bolster", [(x_wall + .36, 1.42, .28), (x_wall + 1.0, 1.42, .28)], .095, kit.cloth(CREAM))
        for sign, xx in ((-1, x_wall + .3), (1, x_wall + 1.06)):
            torus(f"bolster_trim_{sign}", .09, .012, kit.paint(TERRACOTTA), (xx, 1.42, .28), (0, 90, 0), seg=32, tube_seg=8)

    # Cat napping on the seat, facing into the room
    cx, cy = floor(290, 650)
    cast.cat(kit, (max(cx, x_wall + .55), min(cy, 2.5), .17), (0, 0, -20), pose="sleep")

    # Tray with dallah
    tx, ty = floor(450, 680)
    with group("dallah_tray", (tx, ty, 0)):
        cyl("tray_stand", .18, .1, kit.natural(DARK_WOOD), (0, 0, .05))
        lathe("tray", [(.0, .1), (.3, .1), (.32, .12), (.33, .14), (.3, .13), (.0, .12)], kit.metal(BRASS), smooth=1)
        _dallah(kit, -.08, .03, .125)
        for i, (dx, dy) in enumerate(((.15, -.05), (.2, .08), (.08, .14))):
            lathe(f"cup_{i}", [(.0, 0), (.022, 0), (.034, .025), (.04, .055), (.035, .055), (.0, .012)], kit.paint(CREAM),
                  (dx, dy, .125), seg=20, smooth=1)


def _dallah(kit, x, y, z):
    brass = kit.metal(BRASS)
    with group("dallah", (x, y, z)):
        lathe("dallah_body", [(.0, 0), (.1, .0), (.115, .03), (.095, .1), (.055, .17), (.05, .2), (.065, .23), (.05, .24)], brass)
        lathe("dallah_lid", [(.06, .235), (.05, .265), (.03, .29), (.012, .31), (.018, .33), (.0, .34)], brass)
        tube("dallah_spout", [(-.065, 0, .14), (-.115, 0, .2), (-.165, 0, .255)], [.024, .018, .012], brass)
        tube("dallah_handle", [(.055, 0, .22), (.13, 0, .24), (.145, 0, .13), (.09, 0, .07)], .011, brass)


def _bench(kit, ckit):
    x, y = floor(1185, 790)
    wood = kit.natural(HONEY)
    h = .34
    with group("bench", (x, y, 0), (0, 0, -8)):
        rbox("bench_seat", (1.0, .44, .06), .025, wood, (0, 0, h))
        rbox("bench_cushion", (.92, .38, .05), .024, kit.cloth(TEAL), (0, 0, h + .05))
        rbox("bench_back", (1.0, .05, .34), .022, wood, (0, .2, h + .22))
        for sx in (-1, 1):
            for sy in (-1, 1):
                lathe(f"leg_{sx}_{sy}", [(.0, 0), (.042, 0), (.034, .08), (.044, .22), (.036, .32), (.0, .32)],
                      kit.natural(DARK_WOOD), (sx * .43, sy * .17, 0), seg=20)
        for sign in (-1, 1):
            rbox(f"armrest_{sign}", (.05, .36, .04), .018, wood, (sign * .49, .02, h + .19))
            rbox(f"armpost_{sign}", (.04, .04, .19), .012, wood, (sign * .49, -.13, h + .1))
    host = cast.nabeeh(ckit, (x, y - .04, h + .075), (0, 0, -8), pose="sit")
    host.scale = (1.15, 1.15, 1.15)


def _side_decor(kit):
    """Wide-screen only: quiet wall panels outside the 4:3 safe area."""
    for sign in (-1, 1):
        for i, cy in enumerate((.6, -.6)):
            x = sign * (WIDTH / 2 - .02)
            rbox(f"side_panel_{sign}_{i}", (.02, .78, 1.0), .012, kit.natural(PALE_WOOD), (x, cy, 1.45))
            poly(f"side_star_{sign}_{i}", star_points(8, .22, .14), .01, kit.paint(TERRACOTTA if i else TEAL),
                 (x - sign * .012, cy, 1.45), (90, 0, 90 * sign), bevel=.003)


def _lights(kit):
    stage.world("#FBF3E4", .55)
    backdrop = rbox("backdrop", (30, .05, 16), .001, kit.glow("#F2D9B4", .85), (0, BACK_Y + 3, 4))
    backdrop.visible_shadow = False
    # Invisible extension of the back wall: the sun enters through the window only
    blocker = rbox("sun_blocker", (30, .1, 8), .001, kit.ink("#000000"), (0, BACK_Y + .1, HEIGHT + 4.05))
    blocker.visible_camera = False
    # Late-afternoon sun through the mashrabiya, landing on the rug and floor
    stage.sun_light("sun", (.16, -.8, -.58), 9.0, "#FFCF96", angle_deg=1.0)
    stage.area_light("fill", (0, -2.8, 4.2), (0, 2.2, .4), (7, 4), 215, "#FFF6E8")
    stage.area_light("front", (-2.0, -3.6, 1.8), (.4, 2.5, .9), (4, 3), 60, "#FFF1E0")


def build(ckit, rkit):
    _shell(rkit)
    _window(rkit)
    _family_photo(rkit)
    _calligraphy(rkit)
    _clock(rkit)
    _calendar(rkit)
    _bookshelf(rkit)
    _cabinet(rkit)
    _door(rkit)
    _rug(rkit)
    table = _low_table(rkit)
    _letter_cube(rkit, table)
    _camel(rkit, table)
    _majlis(rkit)
    _bench(rkit, ckit)
    _side_decor(rkit)
    _lights(rkit)
    # Lens shift puts the horizon at HORIZON_PX while verticals stay straight
    cam_y = BACK_Y - CAM_DIST
    shift = -(450 - HORIZON_PX) / PX_W
    stage.camera((0, cam_y, CAM_H), lens=LENS, shift_y=shift, rot=(math.radians(90), 0, 0))
