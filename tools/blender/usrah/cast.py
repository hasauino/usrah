"""The cast: نبيه (robot host), سارة, يوسف and the cat.

Characters are rigid parts on named groups (no skin deformation), facing -Y.
Face marks are separate thin parts here; in the game they become swappable textures.
"""
import math

from mathutils import Quaternion

from .shapes import Surface, capsule, group, lathe, poly, rbox, ring, sphere, star_points, torus, tube

CREAM = "#F6E9CF"
TEAL = "#2F9C95"
TERRACOTTA = "#D9734E"
SAGE = "#8DB580"
SKY = "#3D7BD9"
SUN = "#F4C542"
DENIM = "#5B7FA8"
INK = "#2B2230"
BLUSH = "#E8876F"

SARA_SKIN = "#C68D62"
YUSUF_SKIN = "#BD8357"
SARA_HAIR = "#4A2C20"
YUSUF_HAIR = "#2A211F"


def _face(head, kit, skin_dark, eye_yaw=23.0, eye_pitch=-4.0, eye=(.034, .044), grin=False):
    """Printed face: oval eyes with a highlight, brows, cheeks, a small nose and a mouth."""
    ink = kit.ink(INK)
    white = kit.ink("#FFFFFF")
    for side, sign in (("l", -1), ("r", 1)):
        yaw = eye_yaw * sign
        head.patch(f"eye_{side}", yaw, eye_pitch, eye[0], eye[1], .007, ink)
        head.patch(f"eye_shine_{side}", yaw + 3.5, eye_pitch + 4.5, eye[0] * .34, eye[0] * .34, .003,
                   white, lift=.0055)
        head.patch(f"cheek_{side}", (eye_yaw + 15) * sign, eye_pitch - 21, .042, .026, .002,
                   kit.ink(BLUSH))
        head.stroke(f"brow_{side}", [(yaw - 8 * sign, eye_pitch + 20), (yaw, eye_pitch + 23),
                                     (yaw + 8 * sign, eye_pitch + 20)], .0055, ink, lift=.002)
    head.patch("nose", 0, -14, .017, .014, .009, kit.skin(skin_dark))
    if grin:
        # Open grin: a dark half-moon with a band of teeth along its top
        head.emblem("mouth", _half_moon(.062, .042), .006, kit.ink("#7A2E2E"), 0, -30, lift=-.002)
        head.emblem("teeth", _band(.052, .011), .004, kit.ink("#FFFFFF"), 0, -25, lift=.0015)
    else:
        head.stroke("mouth", [(-14, -31), (-7, -35), (0, -36.5), (7, -35), (14, -31)], .0052, ink,
                    lift=.002)


def _half_moon(w, h, n=14):
    """Smile outline: flat top, rounded bottom, CCW."""
    pts = [(w * math.cos(math.pi + math.pi * i / n), -h * math.sin(math.pi * i / n) * 1.0)
           for i in range(n + 1)]
    return pts


def _band(w, h, n=6):
    pts = [(-w + 2 * w * i / n, -h) for i in range(n + 1)]
    return pts + [(w, 0), (-w, 0)]


def _hand(name, at, r, kit, skin, thumb=(.8, -.6, .35)):
    if kit.wood:
        sphere(name, r, kit.skin(skin), at)
    else:
        sphere(name, r, kit.skin(skin), at)
        sphere(name + "_thumb", r * .42, kit.skin(skin),
               (at[0] + r * thumb[0], at[1] + r * thumb[1], at[2] + r * thumb[2]))


def _joint(name, at, r, kit, skin):
    """Visible ball joint on the wooden toy version."""
    if kit.wood:
        sphere(name, r, kit.natural("#D9B98A"), at, seg=24)


def sara(kit, loc=(0, 0, 0), rot=(0, 0, 0), wave=True):
    top = kit.cloth(TERRACOTTA) if kit.wood else kit.paint(TERRACOTTA)
    trim = kit.paint(CREAM)
    trousers = kit.paint(SAGE)
    with group("sara", loc, rot) as root:
        for side, sign in (("l", -1), ("r", 1)):
            with group(f"leg_{side}"):
                capsule(f"leg_{side}_mesh", (sign * .083, 0, .09), (sign * .088, 0, .43), .07, trousers, .082)
                _joint(f"knee_{side}", (sign * .085, 0, .25), .075, kit, SARA_SKIN)
                sphere(f"shoe_{side}", (.082, .122, .056), kit.paint(CREAM), (sign * .085, -.035, .052))
                sphere(f"shoe_cap_{side}", (.072, .07, .042), kit.paint(TEAL), (sign * .085, -.095, .05))
        sphere("hips", (.142, .112, .078), trousers, (0, 0, .44))
        lathe("torso", [(.128, .405), (.128, .47), (.118, .55), (.126, .64), (.118, .715),
                        (.062, .762)], top, (0, 0, 0), seg=48, smooth=2)
        torus("hem", .127, .011, trim, (0, 0, .41))
        torus("collar", .063, .012, trim, (0, 0, .762))
        capsule("neck", (0, 0, .74), (0, 0, .82), .052, kit.skin(SARA_SKIN))

        # Arms: the right one relaxed, the left one waving
        with group("arm_r"):
            capsule("arm_r_mesh", (.14, 0, .70), (.195, -.02, .46), .05, top, .045)
            _joint("shoulder_r", (.14, 0, .70), .056, kit, SARA_SKIN)
            ring("cuff_r", (.14, 0, .70), (.195, -.02, .46), .046, .008, trim)
            _hand("hand_r", (.2, -.022, .425), .052, kit, SARA_SKIN)
        with group("arm_l"):
            if wave:
                capsule("arm_l_mesh", (-.14, 0, .70), (-.285, -.03, .86), .05, top, .045)
                ring("cuff_l", (-.14, 0, .70), (-.285, -.03, .86), .046, .008, trim)
                _hand("hand_l", (-.31, -.035, .895), .052, kit, SARA_SKIN, thumb=(.85, -.5, -.1))
            else:
                capsule("arm_l_mesh", (-.14, 0, .70), (-.195, -.02, .46), .05, top, .045)
                ring("cuff_l", (-.14, 0, .70), (-.195, -.02, .46), .046, .008, trim)
                _hand("hand_l", (-.2, -.022, .425), .052, kit, SARA_SKIN, thumb=(-.8, -.6, .35))
            _joint("shoulder_l", (-.14, 0, .70), .056, kit, SARA_SKIN)

        with group("head"):
            center = (0, 0, 1.0)
            head = Surface(center, (.262, .248, .24))
            sphere("head_mesh", head.r, kit.skin(SARA_SKIN), center)
            for side, sign in (("l", -1), ("r", 1)):
                sphere(f"ear_{side}", (.024, .036, .044), kit.skin(SARA_SKIN), (sign * .26, .012, .985))
            _face(head, kit, "#B57E55")

            hair = kit.paint(SARA_HAIR)
            sphere("hair", (.282, .272, .262), hair, (0, .03, 1.03),
                   clip=((0, 0, 1.0), (0, -.5, -1)))
            # Side-swept fringe
            hair_top = Surface((0, .03, 1.03), (.282, .272, .262))
            hair_top.patch("fringe_l", -22, 42, .13, .068, .028, hair, roll=22, lift=-.003)
            hair_top.patch("fringe_r", 26, 45, .105, .055, .022, hair, roll=-26, lift=-.003)
            # High ponytail swinging to one side, so it reads from the front
            torus("hair_band", .05, .019, kit.paint(TEAL), (.03, .2, 1.235), (68, 0, 8))
            tube("ponytail", [(.03, .21, 1.25), (.13, .29, 1.31), (.29, .31, 1.21), (.33, .29, 1.03),
                              (.35, .26, .92)], [.052, .086, .082, .056, .018], hair)
    return root


def yusuf(kit, loc=(0, 0, 0), rot=(0, 0, 0)):
    shirt = kit.paint(SUN)
    shorts = kit.cloth(DENIM) if kit.wood else kit.paint(DENIM)
    skin = kit.skin(YUSUF_SKIN)
    with group("yusuf", loc, rot) as root:
        for side, sign in (("l", -1), ("r", 1)):
            with group(f"leg_{side}"):
                capsule(f"leg_{side}_mesh", (sign * .08, 0, .08), (sign * .08, 0, .28), .054, skin, .058)
                _joint(f"knee_{side}", (sign * .08, 0, .185), .06, kit, YUSUF_SKIN)
                capsule(f"short_{side}", (sign * .083, 0, .25), (sign * .083, 0, .36), .082, shorts, .088)
                torus(f"short_hem_{side}", .081, .008, kit.paint("#7D9CC0"), (sign * .083, 0, .235))
                # Big chunky sneakers
                sphere(f"sneaker_{side}", (.092, .15, .068), kit.paint("#F5F3EE"), (sign * .082, -.05, .062))
                sphere(f"toe_{side}", (.074, .072, .046), kit.paint(TERRACOTTA), (sign * .082, -.135, .06))
                torus(f"sock_{side}", .056, .012, kit.paint("#FFFFFF"), (sign * .08, 0, .105))
        sphere("hips", (.138, .112, .07), shorts, (0, 0, .365))
        lathe("torso", [(.13, .345), (.136, .40), (.132, .48), (.122, .54), (.06, .585)], shirt,
              (0, 0, 0), smooth=2)
        torus("collar", .062, .011, kit.paint("#E0AE2E"), (0, 0, .582))
        torus("shirt_hem", .131, .008, kit.paint("#E0AE2E"), (0, 0, .35))
        chest = Surface((0, 0, .46), (.136, .13, .17))
        chest.emblem("shirt_star", star_points(5, .056, .025, turn=1.5708), .006, kit.paint(TERRACOTTA),
                     0, 2, lift=-.002)
        capsule("neck", (0, 0, .57), (0, 0, .63), .045, skin)

        with group("arm_r"):
            # Fist pumped up
            capsule("sleeve_r", (.135, 0, .54), (.2, -.01, .47), .05, shirt, .05)
            _joint("shoulder_r", (.135, 0, .54), .05, kit, YUSUF_SKIN)
            capsule("arm_r_mesh", (.2, -.01, .47), (.25, -.03, .62), .04, skin, .038)
            _hand("hand_r", (.26, -.035, .67), .053, kit, YUSUF_SKIN, thumb=(-.7, -.6, .1))
        with group("arm_l"):
            capsule("sleeve_l", (-.135, 0, .54), (-.178, -.01, .45), .05, shirt, .05)
            _joint("shoulder_l", (-.135, 0, .54), .05, kit, YUSUF_SKIN)
            capsule("arm_l_mesh", (-.178, -.01, .45), (-.19, -.02, .33), .04, skin, .038)
            _hand("hand_l", (-.195, -.022, .29), .05, kit, YUSUF_SKIN, thumb=(-.8, -.6, .35))

        with group("head"):
            center = (0, 0, .79)
            head = Surface(center, (.248, .235, .226))
            sphere("head_mesh", head.r, skin, center)
            for side, sign in (("l", -1), ("r", 1)):
                sphere(f"ear_{side}", (.03, .042, .05), skin, (sign * .248, .012, .775))
            _face(head, kit, "#A97347", eye_yaw=24, eye_pitch=-2, eye=(.033, .042), grin=True)
            hair = kit.paint(YUSUF_HAIR)
            sphere("hair", (.262, .255, .242), hair, (0, .03, .815),
                   clip=((0, 0, .815), (0, -.6, -1)))
            tube("cowlick", [(.02, -.02, 1.045), (.05, -.05, 1.085), (.1, -.05, 1.1), (.13, -.02, 1.075)],
                 [.05, .036, .022, .006], hair)
    return root


def nabeeh(kit, loc=(0, 0, 0), rot=(0, 0, 0), face="painted", pose="stand", book=True):
    """The host. Round head on a ball body, so he can curl up and roll in."""
    shell = kit.metal("#DDE3E8") if not kit.wood else kit.paint("#E6E4DD")
    joint = kit.metal("#AEB7BF") if not kit.wood else kit.natural("#D9B98A")
    white = kit.paint("#FBFAF6")
    cap = kit.paint(SKY)
    trim = kit.paint(SUN)
    sit = pose == "sit"
    body_z = .24 if not sit else .13
    with group("nabeeh", loc, rot) as root:
        for side, sign in (("l", -1), ("r", 1)):
            with group(f"leg_{side}"):
                if sit:
                    capsule(f"leg_{side}_mesh", (sign * .075, -.05, .06), (sign * .09, -.2, .03), .035, joint, .03)
                    foot = (sign * .1, -.262, -.032)
                    tilt = (-14, 0, 0)
                else:
                    capsule(f"leg_{side}_mesh", (sign * .068, 0, .16), (sign * .072, -.005, .055), .034, joint, .03)
                    foot = (sign * .074, -.03, .045)
                    tilt = (0, 0, 0)
                # Sneakers: blue with a white sole, toe cap and heel
                with group(f"sneaker_{side}", foot, tilt):
                    sphere(f"sneaker_{side}_mesh", (.062, .1, .046), cap, (0, 0, 0))
                    rbox(f"sole_{side}", (.114, .184, .022), .011, white, (0, 0, -.033))
                    sphere(f"toecap_{side}", (.05, .05, .034), white, (0, -.063, -.003))
                    sphere(f"lace_{side}", (.03, .016, .012), white, (0, -.012, .042))
        with group("body"):
            center = (0, 0, body_z)
            body = Surface(center, .16)
            sphere("body_mesh", .16, shell, center)
            torus("waist_seam", .1595, .0028, kit.ink("#7E8891"), center)
            # 3x3 keypad on a darker panel
            sphere("keypad_panel", .1625, kit.ink("#7C8792"), center,
                   clip=((0, -.122, body_z + .017), (0, 1, -.14)))
            colors = [SUN, SKY, TERRACOTTA, TEAL, SAGE, SUN, TERRACOTTA, SKY, TEAL]
            for i, color in enumerate(colors):
                yaw = (i % 3 - 1) * 21
                pitch = 8 + (1 - i // 3) * 21
                body.patch(f"key_{i}", yaw, pitch, .0175, .0175, .009, kit.paint(color), lift=.0045)
        capsule("neck", (0, 0, body_z + .13), (0, 0, body_z + .18), .05, joint)

        head_z = body_z + .325
        with group("head", (0, 0, 0)):
            center = (0, 0, head_z)
            head = Surface(center, .185)
            sphere("head_mesh", .185, shell, center)
            if face == "screen":
                sphere("face_plate", .1875, kit.glass("#1E2A44"), center,
                       clip=((0, -.112, head_z - .012), (0, 1, -.1)))
                torus("face_rim", .1515, .0065, joint, (0, -.112, head_z - .012), (84.3, 0, 0))
                eye_mat, mouth_mat = kit.glow("#8FF0E6"), kit.glow("#8FF0E6")
                for side, sign in (("l", -1), ("r", 1)):
                    head.patch(f"eye_{side}", 24 * sign, -2, .028, .036, .005, eye_mat, lift=.003)
                head.stroke("mouth", [(-15, -25), (-7, -30), (0, -31.5), (7, -30), (15, -25)], .0055,
                            mouth_mat, lift=.0035)
                rim = trim
                rim_lift = .012
            else:
                ink = kit.ink(INK)
                for side, sign in (("l", -1), ("r", 1)):
                    head.patch(f"eye_{side}", 25 * sign, -3, .03, .038, .006, ink)
                    head.patch(f"eye_shine_{side}", 28 * sign, 1, .011, .011, .003, kit.ink("#FFFFFF"), lift=.0045)
                head.stroke("mouth", [(-14, -30), (-7, -34.5), (0, -36), (7, -34.5), (14, -30)], .005, ink, lift=.002)
                rim = kit.paint("#34405A")
                rim_lift = .006

            # Big round glasses
            for side, sign in (("l", -1), ("r", 1)):
                yaw = 25 * sign
                at = head.point(yaw, -2, rim_lift)
                turn = head.facing(yaw, -2)
                torus(f"glasses_{side}", .059, .0085, rim, at, _flat_to_front(turn), tube_seg=12)
                # Temple arm running back over the ear
                tube(f"temple_{side}", [tuple(head.point(58 * sign, -2, .004)),
                                        tuple(head.point(85 * sign, 2, .004))], .0065, rim)
            head.stroke("bridge", [(-8, -1), (0, 2), (8, -1)], .0075, rim, lift=rim_lift)

            # Baseball cap
            cap_c = (0, .012, head_z + .018)
            sphere("cap", .188, cap, cap_c, clip=((0, 0, head_z + .058), (0, -.26, -1)))
            torus("cap_band", .1846, .0075, kit.paint("#2F63B3"), (0, .021, head_z + .0526), (-14.6, 0, 0))
            sphere("cap_button", (.018, .018, .01), trim, (0, .012, head_z + .205))
            cap_s = Surface(cap_c, .188)
            for yaw in (-40, 40):
                cap_s.stroke(f"cap_panel_{yaw}", [(yaw, 30), (yaw * .72, 58), (0, 86)], .0022,
                             kit.ink("#2F63B3"), lift=.0005)
            cap_s.stroke("cap_panel_c", [(0, 42), (0, 86)], .0022, kit.ink("#2F63B3"), lift=.0005)
            cap_s.emblem("cap_star", star_points(8, .045, .029), .005, trim, 0, 44, lift=-.001)
            # Brim, a rounded tongue tilted slightly down
            sphere("brim", (.14, .105, .012), kit.paint("#2F63B3"), (0, -.232, head_z + .083), (-13, 0, 0))

        # Arms with white mitten hands
        for side, sign in (("l", -1), ("r", 1)):
            with group(f"arm_{side}"):
                shoulder = (sign * .15, -.005, body_z + .045)
                sphere(f"shoulder_{side}", .036, joint, shoulder)
                if sit and book:
                    hand = (sign * .1, -.205, body_z + .05)
                    elbow = (sign * .19, -.085, body_z - .005)
                    tube(f"arm_{side}_mesh", [shoulder, elbow, hand], .024, joint)
                elif sign < 0 and not sit:
                    hand = (sign * .305, -.03, body_z + .215)
                    tube(f"arm_{side}_mesh", [shoulder, (sign * .24, -.02, body_z + .09), hand], .024, joint)
                elif book:
                    hand = (sign * .16, -.17, body_z + .03)
                    tube(f"arm_{side}_mesh", [shoulder, (sign * .215, -.08, body_z - .02), hand], .024, joint)
                else:
                    hand = (sign * .23, -.02, body_z - .09)
                    tube(f"arm_{side}_mesh", [shoulder, hand], .024, joint)
                sphere(f"hand_{side}", .05, white, hand)
                sphere(f"thumb_{side}", .021, white, (hand[0] - sign * .035, hand[1] - .03, hand[2] + .025))
        if book:
            _red_book(kit, sit, body_z)
    return root


def _flat_to_front(turn):
    return turn @ Quaternion((1, 0, 0), math.radians(90))


def _red_book(kit, sit, body_z):
    """نبيه's book. Open on his lap when reading, closed under his arm otherwise."""
    cover = kit.paint("#C43D3D")
    pages = kit.paint("#FBF4E2")
    if sit:
        with group("book", (0, -.235, body_z + .075), (-68, 0, 0)):
            for sign in (-1, 1):
                rbox(f"cover_{sign}", (.115, .15, .012), .005, cover, (sign * .06, 0, 0), (0, sign * 12, 0))
                rbox(f"pages_{sign}", (.1, .135, .016), .004, pages, (sign * .055, 0, .012), (0, sign * 12, 0))
    else:
        with group("book", (.142, -.195, body_z + .035), (0, 0, -8)):
            rbox("cover", (.024, .116, .152), .006, cover)
            rbox("pages", (.016, .1, .136), .003, pages, (0, -.006, 0))


def cat(kit, loc=(0, 0, 0), rot=(0, 0, 0), pose="sit"):
    fur = kit.paint("#F4E2C2")
    ginger = kit.paint("#E2A04E")
    with group("cat", loc, rot) as root:
        if pose == "sit":
            sphere("body", (.105, .125, .13), fur, (0, .02, .125))
            for sign in (-1, 1):
                sphere(f"paw_{sign}", (.036, .05, .028), fur, (sign * .045, -.095, .026))
                sphere(f"haunch_{sign}", (.052, .082, .058), fur, (sign * .09, .04, .056))
            body = Surface((0, .02, .125), (.105, .125, .13))
            for i, (pitch, width) in enumerate(((45, .05), (20, .06), (-5, .058))):
                body.patch(f"stripe_{i}", 180, pitch, width, .017, .006, ginger)
            tube("tail", [(.03, .135, .035), (.15, .155, .04), (.2, .07, .05), (.16, .0, .1)],
                 [.03, .03, .027, .022], ginger)
            head_c = (0, -.015, .31)
        else:
            # Curled up asleep
            sphere("body", (.17, .135, .082), fur, (0, 0, .08))
            sphere("haunch", (.082, .1, .07), fur, (.1, .03, .07))
            body = Surface((0, 0, .08), (.17, .135, .082))
            for i, yaw in enumerate((140, 170, 200)):
                body.patch(f"stripe_{i}", yaw, 45, .018, .05, .006, ginger)
            tube("tail", [(.15, .08, .03), (.1, -.09, .025), (-.03, -.12, .025), (-.1, -.09, .03)],
                 [.028, .028, .026, .02], ginger)
            head_c = (-.135, -.045, .095)

        head = Surface(head_c, (.105, .092, .088))
        sphere("head", head.r, ginger, head_c)
        sphere("muzzle", (.052, .036, .036), fur, (head_c[0], head_c[1] - .068, head_c[2] - .022))
        for sign in (-1, 1):
            ear = [(-.036, 0), (.036, 0), (.004, .07), (-.004, .07)]
            poly(f"ear_{sign}", ear, .02, ginger,
                 (head_c[0] + sign * .06, head_c[1] + .014, head_c[2] + .058), (90, sign * 14, 0), bevel=.007)
            for i, pitch in enumerate((-20, -27)):
                y0 = 34 * sign
                head.stroke(f"whisker_{sign}_{i}", [(y0, pitch), (y0 + 26 * sign, pitch - 3)], .0018,
                            kit.ink("#A9794A"), lift=.012 + .012 * i)
            if pose == "sit":
                head.patch(f"eye_{sign}", 31 * sign, 6, .017, .023, .004, kit.ink(INK))
                head.patch(f"eye_shine_{sign}", 35 * sign, 12, .006, .006, .002, kit.ink("#FFFFFF"), lift=.0035)
            else:
                # Closed sleeping eyes
                head.stroke(f"eye_{sign}", [(21 * sign, 5), (31 * sign, 1), (41 * sign, 5)], .0028, kit.ink(INK), lift=.001)
        for i, yaw in enumerate((-14, 0, 14)):
            head.patch(f"head_stripe_{i}", yaw, 62, .009, .03, .004, kit.paint("#C98638"))
        head.patch("nose", 0, -14, .012, .009, .005, kit.ink("#D9736C"), lift=.03)
    return root
