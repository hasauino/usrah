"""One toy per Arabic letter, plus number-game objects, in the locked vinyl style.

Each builder makes a model about one unit tall around the origin, standing on z=0, front -Y.
"""
import math

from . import cast
from .shapes import Surface, capsule, group, lathe, poly, rbox, sphere, star_points, torus, tube

INK = "#2B2230"


def _eyes(kit, head, yaw=24, pitch=8, size=.05):
    for sign in (-1, 1):
        head.patch(f"eye_{sign}", yaw * sign, pitch, size, size * 1.2, size * .2, kit.ink(INK))
        head.patch(f"shine_{sign}", (yaw + 5) * sign, pitch + 7, size * .34, size * .34, size * .08,
                   kit.ink("#FFFFFF"), lift=size * .16)


def _smile(kit, head, pitch=-18, width=14, thick=.012):
    head.stroke("smile", [(-width, pitch + 3), (0, pitch - 3), (width, pitch + 3)], thick, kit.ink(INK), lift=.003)


def _blush(kit, head, yaw=44, pitch=-10, size=.05):
    for sign in (-1, 1):
        head.patch(f"blush_{sign}", yaw * sign, pitch, size, size * .6, size * .1, kit.ink("#EE9C88"))


def _legs(kit, mat, spots, top, r=.055, foot=None):
    for i, (x, y) in enumerate(spots):
        capsule(f"leg_{i}", (x, y, r), (x, y, top), r, mat)
        if foot:
            sphere(f"foot_{i}", (r * 1.2, r * 1.5, r * .8), foot, (x, y - r * .3, r * .7), seg=20)


def rabbit(k):
    fur = k.paint("#F1ECE6")
    sphere("body", (.26, .24, .3), fur, (0, .03, .3))
    sphere("tail", .08, fur, (0, .27, .22), seg=20)
    for s in (-1, 1):
        sphere(f"foot_{s}", (.1, .15, .06), fur, (s * .14, -.14, .06), seg=20)
        capsule(f"ear_{s}", (s * .1, .02, .85), (s * .15, .04, 1.2), .055, fur, .05)
        capsule(f"ear_in_{s}", (s * .1, -.022, .87), (s * .15, -.004, 1.18), .028, k.paint("#F2B8B5"), .024)
    head = Surface((0, -.02, .68), (.24, .22, .21))
    sphere("head", head.r, fur, head.c)
    _eyes(k, head, 28, 10)
    head.patch("nose", 0, -6, .025, .018, .012, k.paint("#E8818C"), lift=.003)
    _smile(k, head, -18, 11, .008)
    _blush(k, head)


def duck(k):
    y = k.paint("#F7CE4B")
    o = k.paint("#EE8F3A")
    sphere("body", (.32, .38, .28), y, (0, .05, .3))
    sphere("tail", (.09, .14, .1), y, (0, .42, .42), (-30, 0, 0), seg=20)
    for s in (-1, 1):
        sphere(f"wing_{s}", (.05, .2, .14), k.paint("#EDBB35"), (s * .31, .07, .33), seg=24)
        sphere(f"foot_{s}", (.1, .13, .03), o, (s * .13, -.12, .03), seg=20)
    head = Surface((0, -.14, .74), .22)
    sphere("head", .22, y, head.c)
    _eyes(k, head, 28, 14, .042)
    sphere("beak", (.13, .1, .045), o, (0, -.35, .7), seg=24)
    sphere("beak_low", (.09, .07, .03), k.paint("#D9782D"), (0, -.33, .66), seg=20)


def apple(k):
    lathe("apple", [(0, .05), (.2, .03), (.38, .22), (.42, .46), (.34, .72), (.16, .8), (.05, .72), (0, .7)],
          k.paint("#D9413D"), smooth=3)
    sphere("shine", (.08, .02, .12), k.paint("#F2807B"), (-.17, -.36, .54), (0, -24, -24), seg=20)
    tube("stem", [(0, 0, .7), (.02, 0, .85), (.07, 0, .95)], [.025, .02, .025], k.paint("#7A5230"))
    sphere("leaf", (.16, .025, .07), k.paint("#5FA36A"), (.2, 0, .88), (0, -24, 0), seg=24)


def fox(k):
    o = k.paint("#E9843A")
    c = k.paint("#FAEBD7")
    sphere("body", (.2, .2, .26), o, (0, .05, .28))
    sphere("belly", (.13, .1, .19), c, (0, -.1, .26), seg=24)
    tube("tail", [(.14, .18, .12), (.36, .24, .2), (.46, .18, .42)], [.08, .14, .03], o)
    sphere("tail_tip", .05, c, (.46, .18, .44), seg=16)
    head = Surface((0, -.03, .66), (.28, .22, .2))
    sphere("head", head.r, o, head.c)
    sphere("muzzle", (.15, .13, .09), c, (0, -.17, .6), seg=24)
    for s in (-1, 1):
        poly(f"ear_{s}", [(-.09, 0), (.09, 0), (.012, .22), (-.012, .22)], .06, o, (s * .17, .0, .8), (90, s * 16, 0), bevel=.018)
    _eyes(k, head, 26, 14, .04)
    sphere("nose", (.03, .024, .022), k.ink(INK), (0, -.3, .63), seg=16)


def camel(k):
    b = k.paint("#E2B571")
    d = k.paint("#BF8A4A")
    sphere("body", (.36, .19, .17), b, (0, 0, .46))
    sphere("hump", (.15, .13, .16), b, (.04, 0, .62))
    for x in (-.24, .24):
        for y in (-.1, .1):
            capsule(f"leg_{x}_{y}", (x, y, .05), (x, y, .42), .05, b)
            sphere(f"hoof_{x}_{y}", (.06, .07, .04), d, (x, y, .04), seg=16)
    tube("neck", [(-.28, 0, .5), (-.42, 0, .66), (-.42, 0, .86)], [.09, .07, .07], b)
    head = Surface((-.48, 0, .92), (.13, .09, .085))
    sphere("head", head.r, b, head.c)
    sphere("muzzle", (.06, .07, .05), d, (-.58, 0, .89), seg=16)
    for s in (-1, 1):
        sphere(f"eye_{s}", .018, k.ink(INK), (-.5, s * .08, .95), seg=12)
        sphere(f"ear_{s}", (.025, .025, .04), d, (-.42, s * .07, 1.0), seg=12)
    tube("tail", [(.36, 0, .52), (.42, 0, .42), (.42, 0, .32)], [.02, .018, .03], d)


def horse(k):
    b = k.paint("#B87A46")
    d = k.paint("#5A3B28")
    sphere("body", (.36, .18, .19), b, (0, 0, .5))
    for x in (-.24, .24):
        for y in (-.1, .1):
            capsule(f"leg_{x}_{y}", (x, y, .05), (x, y, .46), .05, b)
            sphere(f"hoof_{x}_{y}", (.062, .07, .04), d, (x, y, .04), seg=16)
    tube("neck", [(-.26, 0, .58), (-.38, 0, .76), (-.4, 0, .88)], [.12, .09, .08], b)
    sphere("head", (.17, .09, .085), b, (-.5, 0, .9), (0, 22, 0))
    sphere("muzzle", (.07, .08, .065), k.paint("#E0B58C"), (-.62, 0, .85), seg=16)
    tube("mane", [(-.38, 0, 1.0), (-.26, 0, .86), (-.16, 0, .68)], [.04, .06, .03], d)
    tube("tail", [(.36, 0, .6), (.46, 0, .48), (.46, 0, .26)], [.03, .06, .02], d)
    for s in (-1, 1):
        sphere(f"eye_{s}", .018, k.ink(INK), (-.5, s * .085, .94), seg=12)
        sphere(f"ear_{s}", (.025, .025, .05), b, (-.42, s * .05, 1.0), seg=12)


def sheep(k):
    w = k.paint("#F8F4EA")
    f = k.paint("#3D3440")
    for i, (x, y, z, r) in enumerate(((0, 0, .46, .3), (-.2, 0, .44, .22), (.22, 0, .44, .22), (0, .16, .46, .22),
                                      (-.12, -.14, .42, .2), (.12, -.14, .42, .2), (0, 0, .62, .2))):
        sphere(f"wool_{i}", r, w, (x, y, z), seg=24)
    for x in (-.17, .17):
        for y in (-.1, .12):
            capsule(f"leg_{x}_{y}", (x, y, .05), (x, y, .28), .04, f)
    head = Surface((0, -.3, .56), (.15, .14, .16))
    sphere("head", head.r, f, head.c)
    sphere("fringe", .1, w, (0, -.28, .7), seg=20)
    for s in (-1, 1):
        sphere(f"ear_{s}", (.09, .03, .04), f, (s * .19, -.26, .58), (0, s * 20, 0), seg=16)
        head.patch(f"eye_white_{s}", 28 * s, 8, .04, .045, .01, k.ink("#FFFFFF"))
        head.patch(f"eye_{s}", 28 * s, 6, .02, .024, .006, k.ink(INK), lift=.006)


def bear(k):
    b = k.paint("#A9713C")
    c = k.paint("#E5C28F")
    sphere("body", (.28, .25, .29), b, (0, .03, .29))
    sphere("belly", (.17, .1, .2), c, (0, -.17, .27), seg=24)
    for s in (-1, 1):
        sphere(f"foot_{s}", (.1, .13, .07), b, (s * .17, -.16, .07), seg=20)
        sphere(f"arm_{s}", (.08, .08, .16), b, (s * .29, -.03, .36), (0, s * -28, 0), seg=20)
        sphere(f"ear_{s}", .09, b, (s * .2, 0, .91), seg=20)
        sphere(f"ear_in_{s}", (.05, .03, .05), c, (s * .2, -.07, .91), seg=16)
    head = Surface((0, -.03, .7), (.27, .24, .23))
    sphere("head", head.r, b, head.c)
    sphere("muzzle", (.12, .09, .085), c, (0, -.22, .64), seg=24)
    sphere("nose", (.045, .03, .032), k.ink(INK), (0, -.31, .67), seg=16)
    _eyes(k, head, 26, 14, .036)


def corn(k):
    y = k.paint("#F6CF4A")
    lathe("cob", [(0, .12), (.15, .16), (.2, .4), (.17, .75), (.08, .98), (0, 1.0)], k.paint("#F0BE36"), smooth=2)
    surf = Surface((0, 0, .55), (.2, .2, .46))
    for r, pitch in enumerate(range(-56, 66, 11)):
        for c in range(-3, 4):
            surf.patch(f"kernel_{r}_{c}", c * 25 + (r % 2) * 12, pitch, .026, .028, .012, y)
    g = k.paint("#6FAF62")
    for s, tip in ((-1, .72), (1, .72), (0, .55)):
        tube(f"husk_{s}", [(s * .08, -.06 if s == 0 else 0, .0), (s * .27, -.16 if s == 0 else -.06, .3), (s * .2, -.2 if s == 0 else -.08, tip)],
             [.11, .1, .01], g)


def pomegranate(k):
    r = k.paint("#C8344B")
    lathe("fruit", [(0, .03), (.2, .03), (.4, .22), (.43, .44), (.35, .68), (.16, .78), (0, .78)], r, smooth=3)
    sphere("shine", (.08, .02, .12), k.paint("#E77A87"), (-.18, -.37, .52), (0, -24, -24), seg=20)
    lathe("crown_base", [(.1, .74), (.09, .84), (.05, .86), (0, .86)], r, smooth=1, seg=24)
    for i in range(6):
        a = math.tau * i / 6
        capsule(f"crown_{i}", (math.cos(a) * .07, math.sin(a) * .07, .84), (math.cos(a) * .15, math.sin(a) * .15, .99),
                .03, r, .012)


def giraffe(k):
    y = k.paint("#F2C260")
    d = k.paint("#B26F35")
    sphere("body", (.28, .16, .15), y, (0, 0, .42))
    for x in (-.18, .18):
        for yy in (-.08, .08):
            capsule(f"leg_{x}_{yy}", (x, yy, .04), (x, yy, .4), .04, y)
            sphere(f"hoof_{x}_{yy}", (.05, .055, .03), d, (x, yy, .03), seg=12)
    tube("neck", [(-.2, 0, .46), (-.3, 0, .76), (-.33, 0, 1.0)], [.085, .055, .05], y)
    head = Surface((-.4, 0, 1.06), (.11, .07, .065))
    sphere("head", head.r, y, head.c)
    for s in (-1, 1):
        capsule(f"horn_{s}", (-.36, s * .03, 1.11), (-.36, s * .035, 1.18), .012, d, .02)
        sphere(f"eye_{s}", .015, k.ink(INK), (-.42, s * .062, 1.08), seg=12)
    body = Surface((0, 0, .42), (.28, .16, .15))
    for i, (yaw, pitch) in enumerate(((35, 25), (-30, 40), (0, -10), (60, -15), (-60, -5), (-5, 55))):
        body.patch(f"spot_{i}", yaw, pitch, .05, .045, .006, d)
    for i, (x, z) in enumerate(((-.25, .62), (-.3, .8), (-.32, .93))):
        sphere(f"neck_spot_{i}", (.03, .062, .035), d, (x, 0, z), seg=12)
    tube("tail", [(.27, 0, .46), (.34, 0, .34), (.34, 0, .25)], [.012, .012, .024], d)


def fish(k):
    b = k.paint("#F08A3C")
    w = k.paint("#FBE9D0")
    z = .5
    sphere("body", (.42, .17, .29), b, (0, 0, z))
    poly("tail", [(0, -.04), (.26, -.2), (.3, 0), (.26, .2), (0, .04)], .07, b, (.34, -.035, z), (90, 0, 0), bevel=.02)
    poly("fin", [(-.1, 0), (.14, 0), (.1, .16), (-.04, .13)], .05, k.paint("#D9702A"), (0, -.025, z + .25), (90, 0, 0), bevel=.015)
    surf = Surface((0, 0, z), (.42, .17, .29))
    for i, (x, h) in enumerate(((-.04, .22), (.14, .2))):
        sphere(f"stripe_{i}", (.04, .172, h), w, (x, 0, z), seg=24)
    sphere("eye_white", (.075, .03, .075), k.ink("#FFFFFF"), (-.25, -.13, z + .07), seg=20)
    sphere("eye", (.04, .02, .045), k.ink(INK), (-.26, -.15, z + .07), seg=16)
    surf.stroke("mouth", [(-82, -18), (-74, -24), (-65, -20)], .012, k.ink(INK), lift=.002)


def sun(k):
    y = k.paint("#F9C93E")
    o = k.paint("#F39C2F")
    z = .52
    for i in range(12):
        a = math.tau * i / 12
        capsule(f"ray_{i}", (math.cos(a) * .3, 0, z + math.sin(a) * .3), (math.cos(a) * .5, 0, z + math.sin(a) * .5), .06, o, .02)
    head = Surface((0, 0, z), .34)
    sphere("sun", .34, y, head.c)
    _eyes(k, head, 22, 10, .05)
    _smile(k, head, -20, 16, .014)
    _blush(k, head, 42, -8, .06)


def rocket(k):
    w = k.paint("#F5F3EE")
    r = k.paint("#D9413D")
    lathe("hull", [(0, .12), (.12, .12), (.2, .3), (.21, .55), (.15, .78), (0, .86)], w, smooth=2)
    lathe("nose", [(.145, .76), (.11, .86), (.05, .98), (0, 1.03)], r, smooth=2)
    lathe("burner", [(.1, .02), (.12, .1), (.13, .15), (0, .15)], k.paint("#6E7A85"), smooth=0, seg=24)
    for i, a in enumerate((90, 210, 330)):
        poly(f"fin_{i}", [(0, 0), (.17, -.1), (.17, .04), (0, .28)], .045, r, (math.cos(math.radians(a)) * .17, math.sin(math.radians(a)) * .17, .14),
             (90, 0, a), bevel=.012)
    torus("window_ring", .085, .02, k.paint("#3D7BD9"), (0, -.205, .58), (90, 0, 0), seg=36, tube_seg=12)
    sphere("window", (.08, .02, .08), k.glass("#8CC8E8"), (0, -.205, .58), seg=24)


def frog(k):
    g = k.paint("#6FBF5B")
    d = k.paint("#58A649")
    sphere("body", (.34, .3, .26), g, (0, .05, .28))
    sphere("belly", (.22, .1, .16), k.paint("#CFE8A3"), (0, -.21, .22), seg=24)
    for s in (-1, 1):
        sphere(f"leg_{s}", (.14, .2, .1), d, (s * .3, .02, .11), seg=24)
        sphere(f"foot_{s}", (.1, .15, .03), d, (s * .24, -.24, .03), seg=20)
    head = Surface((0, -.08, .5), (.3, .24, .17))
    sphere("head", head.r, g, head.c)
    for s in (-1, 1):
        sphere(f"bump_{s}", .1, g, (s * .17, -.13, .66), seg=24)
        sphere(f"eye_white_{s}", (.075, .05, .075), k.ink("#FFFFFF"), (s * .17, -.2, .67), seg=20)
        sphere(f"eye_{s}", (.04, .02, .05), k.ink(INK), (s * .17, -.25, .67), seg=16)
    head.stroke("mouth", [(-46, -14), (-20, -34), (0, -38), (20, -34), (46, -14)], .012, k.ink(INK), lift=.002)


def airplane(k):
    w = k.paint("#F5F3EE")
    b = k.paint("#3D7BD9")
    z = .5
    capsule("fuselage", (.42, 0, z), (-.42, 0, z), .13, w, .15)
    rbox("wing", (.26, 1.1, .04), .018, b, (-.03, 0, z - .02), (0, 0, -9))
    rbox("tail_h", (.14, .4, .03), .012, b, (.46, 0, z + .03))
    poly("tail_v", [(0, 0), (.2, 0), (.24, .24), (.12, .24)], .035, k.paint("#D9413D"), (.38, -.018, z + .08), (90, 0, 0), bevel=.012)
    for i, x in enumerate((-.3, -.16, -.02, .12, .26)):
        sphere(f"win_{i}", (.028, .012, .032), k.glass("#3B6E9E"), (x, -.138, z + .04), seg=14)
    sphere("cockpit", (.08, .1, .05), k.glass("#8CC8E8"), (-.46, 0, z + .06), seg=20)
    capsule("engine_a", (.04, -.3, z - .08), (-.12, -.3, z - .08), .04, k.paint("#6E7A85"))
    capsule("engine_b", (.04, .3, z - .08), (-.12, .3, z - .08), .04, k.paint("#6E7A85"))


def envelope(k):
    c = k.paint("#F5E8CC")
    z = .46
    rbox("env", (.9, .05, .6), .03, c, (0, 0, z))
    poly("flap", [(-.42, 0), (.42, 0), (.03, -.3), (-.03, -.3)], .018, k.paint("#EAD8B0"), (0, -.038, z + .285), (90, 0, 0), bevel=.008)
    poly("fold_l", [(-.43, -.27), (-.02, 0), (-.43, .27)], .008, k.paint("#EEDFBC"), (0, -.03, z), (90, 0, 0), bevel=.003)
    poly("fold_r", [(.43, .27), (.02, 0), (.43, -.27)], .008, k.paint("#EEDFBC"), (0, -.03, z), (90, 0, 0), bevel=.003)
    sphere("seal", (.09, .018, .09), k.paint("#C43D3D"), (0, -.065, z + .03), seg=24)
    poly("seal_star", star_points(8, .05, .03), .006, k.paint("#E8716C"), (0, -.079, z + .03), (90, 0, 0), bevel=.002)


def bird(k):
    b = k.paint("#5B95E0")
    sphere("body", (.28, .25, .3), b, (0, .02, .36))
    sphere("belly", (.17, .08, .19), k.paint("#F6E9CF"), (0, -.19, .3), seg=24)
    for s in (-1, 1):
        sphere(f"wing_{s}", (.05, .16, .17), k.paint("#3D7BD9"), (s * .28, .05, .38), (0, s * 12, 0), seg=24)
        capsule(f"foot_{s}", (s * .09, -.02, .1), (s * .09, -.08, .025), .02, k.paint("#EE8F3A"))
    poly("tail", [(-.09, 0), (.09, 0), (.13, .3), (-.13, .3)], .04, k.paint("#3D7BD9"), (0, .22, .3), (-20, 0, 0), bevel=.012)
    head = Surface((0, -.03, .72), .21)
    sphere("head", .21, b, head.c)
    _eyes(k, head, 28, 12, .042)
    sphere("beak", (.05, .07, .035), k.paint("#F4A63A"), (0, -.25, .69), seg=16)


def cloud(k):
    w = k.paint("#FBFAF6")
    for i, (x, z, r) in enumerate(((-.3, .4, .22), (.32, .4, .24), (-.08, .58, .3), (.13, .52, .24), (0, .36, .24))):
        sphere(f"puff_{i}", r, w, (x, 0, z), seg=32)
    face = Surface((-.02, 0, .47), .3)
    _eyes(k, face, 22, 6, .042)
    _smile(k, face, -18, 13, .012)
    _blush(k, face, 42, -8, .05)


def butterfly(k):
    z = .5
    for s in (-1, 1):
        sphere(f"wing_up_{s}", (.25, .03, .22), k.paint("#EE7E9A"), (s * .25, 0, z + .14), (0, s * 24, 0), seg=28)
        sphere(f"wing_low_{s}", (.16, .03, .15), k.paint("#F4C542"), (s * .18, 0, z - .15), (0, s * -28, 0), seg=24)
        sphere(f"dot_up_{s}", (.08, .02, .07), k.paint("#FBEFD8"), (s * .28, -.028, z + .15), seg=16)
        sphere(f"dot_low_{s}", (.05, .02, .045), k.paint("#EE8F3A"), (s * .18, -.028, z - .15), seg=16)
        tube(f"antenna_{s}", [(s * .02, -.02, z + .24), (s * .08, -.02, z + .42), (s * .15, -.02, z + .46)], .008, k.ink(INK))
        sphere(f"antenna_tip_{s}", .02, k.ink(INK), (s * .15, -.02, z + .46), seg=10)
    capsule("body", (0, -.03, z - .22), (0, -.03, z + .14), .045, k.paint("#4A3656"))
    head = Surface((0, -.04, z + .21), .08)
    sphere("head", .08, k.paint("#4A3656"), head.c, seg=24)
    for s in (-1, 1):
        head.patch(f"eye_{s}", 28 * s, 8, .018, .022, .004, k.ink("#FFFFFF"))


def cat(k):
    with group("cat_sized", (0, 0, 0)) as g:
        g.scale = (2.4, 2.4, 2.4)
        cast.cat(k, pose="sit")


def ball(k):
    z = .44
    sphere("ball", .42, k.paint("#D9413D"), (0, 0, z))
    for name, rot, color in (("a", (12, 0, 0), "#FBFAF6"), ("b", (72, 0, 34), "#3D7BD9"), ("c", (72, 0, -34), "#F4C542")):
        torus(f"band_{name}", .414, .045, k.paint(color), (0, 0, z), rot, seg=56, tube_seg=12)


def lemon(k):
    y = k.paint("#F6DC4A")
    z = .44
    sphere("lemon", (.42, .34, .32), y, (0, 0, z))
    sphere("tip_a", (.05, .06, .06), y, (.43, 0, z), seg=16)
    sphere("tip_b", (.04, .05, .05), k.paint("#D9BE34"), (-.43, 0, z), seg=16)
    sphere("shine", (.09, .02, .07), k.paint("#FBEE97"), (-.14, -.3, z + .13), seg=16)
    sphere("leaf", (.18, .028, .08), k.paint("#5FA36A"), (.1, 0, z + .36), (0, -20, 0), seg=24)


def banana(k):
    tube("banana", [(-.42, 0, .86), (-.42, 0, .5), (-.2, 0, .2), (.12, 0, .12), (.42, 0, .28)],
         [.05, .13, .15, .13, .05], k.paint("#F6D24A"))
    tube("tip", [(-.42, 0, .86), (-.42, 0, .97)], [.055, .04], k.paint("#7A5A30"))
    sphere("end", (.04, .045, .045), k.paint("#5C4426"), (.43, 0, .29), seg=12)
    tube("ridge", [(-.36, -.125, .5), (-.16, -.14, .24), (.14, -.125, .17)], .01, k.paint("#D9B635"))


def star(k):
    z = .47
    pts = star_points(5, .5, .26, turn=math.pi / 2)
    poly("star", pts, .17, k.paint("#F9C93E"), (0, .085, z), (90, 0, 0), bevel=.06)
    for s in (-1, 1):
        sphere(f"eye_{s}", (.038, .012, .048), k.ink(INK), (s * .09, -.145, z + .03), seg=16)
        sphere(f"shine_{s}", (.012, .006, .014), k.ink("#FFFFFF"), (s * .1, -.156, z + .05), seg=10)
    tube("smile", [(-.06, -.145, z - .06), (0, -.15, z - .095), (.06, -.145, z - .06)], .01, k.ink(INK))


def crescent(k):
    outer = [(.5 * math.cos(math.radians(a)), .5 * math.sin(math.radians(a))) for a in range(40, 321, 8)]
    inner = [(.14 + .36 * math.cos(math.radians(a)), .36 * math.sin(math.radians(a)) * 1.0) for a in range(300, 59, -8)]
    poly("crescent", outer + inner, .16, k.paint("#F4C542"), (-.04, .08, .5), (90, 0, 0), bevel=.05)
    poly("small_star", star_points(5, .13, .06, turn=math.pi / 2), .05, k.paint("#F9DC6B"), (.26, .025, .52), (90, 0, 0), bevel=.015)


def flower(k):
    tube("stem", [(0, 0, 0), (.04, 0, .3), (0, 0, .62)], .03, k.paint("#5FA36A"), caps=False)
    sphere("leaf_a", (.17, .03, .07), k.paint("#6FAF62"), (.15, 0, .24), (0, -28, 0), seg=20)
    sphere("leaf_b", (.15, .03, .06), k.paint("#6FAF62"), (-.12, 0, .34), (0, 28, 0), seg=20)
    z = .72
    for i in range(7):
        a = math.tau * i / 7
        sphere(f"petal_{i}", (.135, .05, .1), k.paint("#EE7E9A"), (math.cos(a) * .19, 0, z + math.sin(a) * .19),
               (0, -math.degrees(a), 0), seg=24)
    head = Surface((0, -.05, z), .13)
    sphere("center", .13, k.paint("#F4C542"), head.c, seg=28)
    _eyes(k, head, 24, 8, .024)
    _smile(k, head, -24, 16, .007)


def hand(k):
    s = k.paint("#C68D62")
    rbox("palm", (.46, .14, .46), .13, s, (0, 0, .34), seg=6)
    for i, (x, h) in enumerate(((-.17, .24), (-.06, .3), (.06, .32), (.17, .27))):
        capsule(f"finger_{i}", (x, 0, .5), (x, 0, .54 + h), .058, s, .052)
    capsule("thumb", (.2, -.03, .3), (.42, -.05, .52), .068, s, .055)
    rbox("cuff", (.4, .15, .14), .05, k.paint("#3D7BD9"), (0, 0, .08), seg=4)


# (id, builder): one per letter, in order
WORDS = [("rabbit", rabbit), ("duck", duck), ("apple", apple), ("fox", fox), ("camel", camel), ("horse", horse),
         ("sheep", sheep), ("bear", bear), ("corn", corn), ("pomegranate", pomegranate), ("giraffe", giraffe),
         ("fish", fish), ("sun", sun), ("rocket", rocket), ("frog", frog), ("airplane", airplane),
         ("envelope", envelope), ("bird", bird), ("cloud", cloud), ("butterfly", butterfly), ("cat", cat),
         ("ball", ball), ("lemon", lemon), ("banana", banana), ("star", star), ("crescent", crescent),
         ("flower", flower), ("hand", hand)]
