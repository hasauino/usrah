"""نبيه, second generation: modelled to match art/concepts/batch-02 (Gemini target images).

Same design as cast.nabeeh, with real lenses over domed eyes, a shaped cap brim, stitched cap
seams, a recessed keypad, full sneakers and a hardcover book. Faces -Y; parts are grouped at
their joints for animation.
"""
import math

from mathutils import Quaternion

from .shapes import Surface, capsule, group, poly, rbox, ring, sphere, star_points, torus, tube

SHELL = "#E9E6E0"
JOINT = "#AEB6BC"
PANEL = "#8C949B"
SEAM = "#6F7880"
WHITE = "#FBFAF6"
SKY = "#3D7BD9"
SKY_DARK = "#2F63B3"
SKY_LIGHT = "#7FA9E8"
SUN = "#F4C542"
NAVY = "#2F3B55"
INK = "#2B2230"
RED = "#C43D3D"
RED_DARK = "#9E2E30"
PAGES = "#FBF4E2"
KEY_COLORS = ["#F4C542", "#5B95E0", "#EE8A6B",
              "#66BFA6", "#A9CC7A", "#F4C542",
              "#EE8A6B", "#5B95E0", "#66BFA6"]

BODY_R = .153
HEAD_R = (.182, .172, .168)
HEAD_ABOVE_BODY = .275


def _head(kit, head_z):
    with group("head", pivot=(0, 0, head_z - .15)):
        center = (0, 0, head_z)
        head = Surface(center, HEAD_R)
        sphere("head_mesh", HEAD_R, kit.paint(SHELL), center)

        # Domed eyes: white, iris, pupil, two highlights
        for side, sign in (("l", -1), ("r", 1)):
            yaw, pitch = 26 * sign, -2
            head.patch(f"eye_white_{side}", yaw, pitch, .05, .05, .008, kit.ink("#F7F3EA"))
            head.patch(f"iris_{side}", yaw, pitch - 1, .034, .036, .007, kit.ink("#6B625A"), lift=.004)
            head.patch(f"pupil_{side}", yaw, pitch - 1, .023, .025, .006, kit.ink("#23202A"), lift=.0075)
            head.patch(f"shine_{side}", yaw + 4, pitch + 5, .0085, .0085, .003, kit.ink("#FFFFFF"), lift=.0115)
            head.patch(f"shine2_{side}", yaw - 4, pitch - 5, .004, .004, .002, kit.ink("#FFFFFF"), lift=.011)
            head.patch(f"cheek_{side}", 43 * sign, -24, .03, .017, .0015, kit.ink("#EDC9BA"))

        head.stroke("mouth", [(-14, -32), (-7, -37.5), (0, -39.5), (7, -37.5), (14, -32)], .0048,
                    kit.ink(INK), lift=.002)

        # Glasses: thick frames, real lenses standing off the eyes
        rim = kit.paint(NAVY)
        for side, sign in (("l", -1), ("r", 1)):
            yaw, pitch = 26 * sign, -2
            at = head.point(yaw, pitch, .021)
            turn = head.facing(yaw, pitch)
            flat = turn @ Quaternion((1, 0, 0), math.radians(90))
            torus(f"glasses_{side}", .06, .0098, rim, at, flat, tube_seg=16)
            lens = sphere(f"lens_{side}", (.0595, .0115, .0595), kit.lens(), at, turn, seg=32)
            lens.visible_shadow = False
            tube(f"temple_{side}", [tuple(head.point(49 * sign, -1, .017)), tuple(head.point(68 * sign, 0, .012)),
                                    tuple(head.point(88 * sign, 0, .004))], .0058, rim)
        head.stroke("bridge", [(-7, -1), (0, 2), (7, -1)], .0072, rim, lift=.021)

        # Cap
        zp = head_z + .058
        cap_c = (0, .012, head_z + .02)
        cap_r = .186
        sphere("cap", cap_r, kit.paint(SKY), cap_c, clip=((0, 0, zp), (0, -.26, -1)))
        torus("cap_band", .1829, .0078, kit.paint(SKY_DARK), (0, .0205, head_z + .0527), (-14.6, 0, 0), tube_seg=14)
        sphere("cap_button", (.019, .019, .011), kit.paint(SUN), (0, .012, head_z + .205))
        cap_s = Surface(cap_c, cap_r)
        for yaw in (-38, 38, -110, 110, 180):
            cap_s.stroke(f"cap_seam_{yaw}", [(yaw, 24), (yaw, 50), (yaw * .9 if abs(yaw) < 180 else 180, 72), (0, 88)],
                         .0024, kit.ink(SKY_DARK), lift=.0002)
            cap_s.stroke(f"cap_stitch_{yaw}", [(yaw + 4, 24), (yaw + 3.8, 50), (yaw * .9 + 5, 70)],
                         .0013, kit.ink(SKY_LIGHT), lift=.0006)
        cap_s.emblem("cap_star", star_points(8, .047, .03), .007, kit.paint(SUN), 0, 47, lift=-.001, bevel=.0028)
        # Brim: a flattened tongue tilted down a little
        sphere("brim", (.145, .112, .0125), kit.paint(SKY_DARK), (0, -.228, head_z + .09), (-13, 0, 0))


def _sneaker(kit, side, sign, foot, tilt):
    white = kit.paint(WHITE)
    with group(f"sneaker_{side}", foot, tilt):
        rbox(f"sole_{side}", (.112, .192, .034), .016, white, (0, -.008, -.036), seg=5)
        sphere(f"upper_{side}", (.058, .098, .05), kit.paint(SKY), (0, .004, .002))
        sphere(f"toecap_{side}", (.054, .058, .036), white, (0, -.06, -.006))
        torus(f"collar_{side}", .037, .0085, kit.paint(SKY_DARK), (0, .03, .046), (8, 0, 0), seg=28, tube_seg=10)
        sphere(f"tongue_{side}", (.024, .036, .012), white, (0, -.006, .046), (-16, 0, 0))
        for i, y in enumerate((-.03, -.012, .006)):
            capsule(f"lace_{side}_{i}", (-.024, y, .04 + i * .005), (.024, y, .04 + i * .005), .0042, white)
        sphere(f"heel_{side}", (.03, .012, .022), white, (0, .098, .006))


def _book_closed(kit, at, turn):
    cover = kit.paint(RED)
    with group("book", at, turn):
        for name, x in (("a", -.0255), ("b", .0255)):
            rbox(f"cover_{name}", (.0085, .118, .158), .0035, cover, (x, 0, 0))
        rbox("spine", (.06, .0085, .158), .0035, kit.paint(RED_DARK), (0, .059, 0))
        rbox("pages", (.043, .109, .145), .0015, kit.paint(PAGES), (0, -.002, 0))
        ribbon = [(-.006, 0), (.006, 0), (.006, -.05), (0, -.04), (-.006, -.05)]
        poly("ribbon", ribbon, .002, kit.paint(RED_DARK), (.006, -.05, -.072), (90, 0, 0), bevel=.0006)


def _book_open(kit, at, turn):
    cover = kit.paint(RED)
    pages = kit.paint(PAGES)
    with group("book", at, turn):
        for sign in (-1, 1):
            rbox(f"cover_{sign}", (.128, .172, .009), .0035, cover, (sign * .066, 0, 0), (0, sign * 11, 0))
            rbox(f"pages_{sign}", (.112, .156, .018), .004, pages, (sign * .059, 0, .013), (0, sign * 11, 0))
        ribbon = [(-.005, 0), (.005, 0), (.005, -.045), (0, -.036), (-.005, -.045)]
        poly("ribbon", ribbon, .002, kit.paint(RED_DARK), (.004, -.078, .018), (0, 0, 0), bevel=.0006)


def _arm(kit, side, sign, shoulder, points, hand, radii=(.028, .024)):
    joint = kit.metal(JOINT)
    with group(f"arm_{side}", pivot=shoulder):
        sphere(f"shoulder_{side}", .037, joint, shoulder)
        ring(f"shoulder_ring_{side}", (shoulder[0] * .7, shoulder[1], shoulder[2]), shoulder, .036, .0065, kit.ink(SEAM))
        tube(f"arm_{side}_mesh", [shoulder, *points, hand],
             [radii[0]] + [(radii[0] + radii[1]) / 2] * len(points) + [radii[1]], joint)
        white = kit.paint(WHITE)
        sphere(f"hand_{side}", (.054, .052, .054), white, hand)
        thumb = (hand[0] - sign * .037, hand[1] - .03, hand[2] + .024)
        capsule(f"thumb_{side}", hand, thumb, .018, white, .0205)


def nabeeh(kit, loc=(0, 0, 0), rot=(0, 0, 0), pose="stand"):
    sit = pose == "sit"
    body_z = .13 if sit else .25
    head_z = body_z + HEAD_ABOVE_BODY
    joint = kit.metal(JOINT)

    with group("nabeeh", loc, rot) as root:
        with group("body"):
            center = (0, 0, body_z)
            radii = (BODY_R, BODY_R * .98, BODY_R * .97)
            body = Surface(center, radii)
            sphere("body_mesh", radii, kit.paint(SHELL), center)
            # Runs around the back and sides only, stopping short of the keypad
            body.stroke("waist_seam", [(yaw, -8) for yaw in range(48, 313, 24)], .0028, kit.ink(SEAM))
            # Recessed keypad: a darker cap inside a soft ring, with domed buttons
            plane = (0, -.114, body_z + .012)
            normal = (0, 1, -.1)
            sphere("keypad_panel", (BODY_R + .004, BODY_R * .98 + .004, BODY_R * .97 + .004),
                   kit.ink(PANEL), center, clip=(plane, normal))
            torus("keypad_ring", .104, .0042, kit.ink(SEAM), (0, -.1165, body_z + .012), (84.3, 0, 0), seg=64, tube_seg=8)
            for i, color in enumerate(KEY_COLORS):
                yaw = (i % 3 - 1) * 21
                pitch = 5 + (1 - i // 3) * 21
                body.patch(f"key_{i}", yaw, pitch, .0185, .0185, .012, kit.paint(color), lift=.0085)
        capsule("neck", (0, 0, body_z + .12), (0, 0, body_z + .17), .05, joint)

        _head(kit, head_z)

        for side, sign in (("l", -1), ("r", 1)):
            with group(f"leg_{side}", pivot=(sign * .07, 0, body_z - .1)):
                if sit:
                    capsule(f"leg_{side}_mesh", (sign * .075, -.05, .05), (sign * .09, -.2, .02), .034, joint, .03)
                    foot = (sign * .095, -.262, -.022)
                    tilt = (-12, 0, sign * -6)
                else:
                    capsule(f"leg_{side}_mesh", (sign * .07, 0, body_z - .1), (sign * .074, -.005, .06), .034, joint, .03)
                    foot = (sign * .076, -.03, .053)
                    tilt = (0, 0, sign * -6)
                _sneaker(kit, side, sign, foot, tilt)

        if sit:
            for side, sign in (("l", -1), ("r", 1)):
                shoulder = (sign * .142, -.005, body_z + .045)
                hand = (sign * .118, -.205, body_z + .005)
                _arm(kit, side, sign, shoulder, [(sign * .185, -.09, body_z - .03)], hand)
            _book_open(kit, (0, -.235, body_z + .025), (-58, 0, 0))
        else:
            _arm(kit, "l", -1, (-.142, -.005, body_z + .045),
                 [(-.235, -.015, body_z + .07)], (-.292, -.03, body_z + .215))
            hand = (.172, -.142, body_z + .03)
            _arm(kit, "r", 1, (.142, -.005, body_z + .045), [(.21, -.075, body_z - .03)], hand)
            _book_closed(kit, (.17, -.1, body_z + .045), (0, 0, -52))
    return root
