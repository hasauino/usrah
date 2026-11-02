"""Material kits. A kit gives every model the same vocabulary (paint, natural, cloth, ...)
and each kit renders it in one art direction, so style changes never touch model code.
"""
import bpy


def linear(hex_color):
    """'#RRGGBB' (sRGB) to linear RGBA."""
    hex_color = hex_color.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(hex_color[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def shade(rgba, factor):
    return (rgba[0] * factor, rgba[1] * factor, rgba[2] * factor, 1.0)


def _principled(name, color, rough=.5, metallic=0.0, sss=0.0, coat=0.0, sheen=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Subsurface Weight"].default_value = sss
    bsdf.inputs["Subsurface Scale"].default_value = .03
    bsdf.inputs["Coat Weight"].default_value = coat
    bsdf.inputs["Coat Roughness"].default_value = .35
    bsdf.inputs["Sheen Weight"].default_value = sheen
    return mat, bsdf


def _grain(mat, bsdf, light, dark, scale=4.0, bump=.025, stretch=.08):
    """Wood grain: distorted bands in object space, stretched along Z, offset per object
    so neighbouring planks don't repeat each other."""
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (1, 1, stretch)
    info = nodes.new("ShaderNodeObjectInfo")
    spread = nodes.new("ShaderNodeVectorMath")
    spread.operation = "SCALE"
    spread.inputs[3].default_value = 30.0
    combine = nodes.new("ShaderNodeCombineXYZ")
    links.new(info.outputs["Random"], combine.inputs["X"])
    links.new(info.outputs["Random"], combine.inputs["Z"])
    links.new(combine.outputs["Vector"], spread.inputs[0])
    links.new(spread.outputs["Vector"], mapping.inputs["Location"])
    wave = nodes.new("ShaderNodeTexWave")
    wave.bands_direction = "X"
    wave.inputs["Scale"].default_value = scale
    wave.inputs["Distortion"].default_value = 15
    wave.inputs["Detail"].default_value = 2.5
    wave.inputs["Detail Scale"].default_value = .8
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = .25
    ramp.color_ramp.elements[0].color = dark
    ramp.color_ramp.elements[1].position = .75
    ramp.color_ramp.elements[1].color = light
    links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], wave.inputs["Vector"])
    links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    height = nodes.new("ShaderNodeBump")
    height.inputs["Strength"].default_value = bump
    height.inputs["Distance"].default_value = .01
    links.new(wave.outputs["Fac"], height.inputs["Height"])
    links.new(height.outputs["Normal"], bsdf.inputs["Normal"])


def _felt(mat, bsdf, scale=420.0):
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = 6
    height = nodes.new("ShaderNodeBump")
    height.inputs["Strength"].default_value = .35
    height.inputs["Distance"].default_value = .004
    links.new(noise.outputs["Fac"], height.inputs["Height"])
    links.new(height.outputs["Normal"], bsdf.inputs["Normal"])


class _Kit:
    wood = False

    def __init__(self):
        self._cache = {}

    def _get(self, key, build):
        if key not in self._cache:
            self._cache[key] = build()
        return self._cache[key]

    def ink(self, hex_color):
        """Matte print, used for faces. Same in every kit."""
        return self._get(("ink", hex_color),
                         lambda: _principled(f"ink {hex_color}", linear(hex_color), rough=.7)[0])

    def glow(self, hex_color, strength=1.4):
        def build():
            mat, bsdf = _principled(f"glow {hex_color}", linear(hex_color))
            bsdf.inputs["Emission Color"].default_value = linear(hex_color)
            bsdf.inputs["Emission Strength"].default_value = strength
            return mat
        return self._get(("glow", hex_color), build)

    def plaster(self, hex_color):
        """Plain matte wall paint. Same in every kit."""
        return self._get(("plaster", hex_color),
                         lambda: _principled(f"plaster {hex_color}", linear(hex_color), rough=.85)[0])

    def glass(self, hex_color):
        """Glossy dark screen."""
        return self._get(("glass", hex_color),
                         lambda: _principled(f"screen {hex_color}", linear(hex_color),
                                             rough=.18, coat=.6)[0])


class Vinyl(_Kit):
    """Soft matte-satin designer-toy plastic."""

    def paint(self, hex_color):
        return self._get(("paint", hex_color), lambda: _principled(
            f"vinyl {hex_color}", linear(hex_color), rough=.42, sss=.25, coat=.12)[0])

    natural = skin = paint

    def cloth(self, hex_color):
        return self._get(("cloth", hex_color), lambda: _principled(
            f"soft {hex_color}", linear(hex_color), rough=.62, sss=.2, sheen=.25)[0])

    def metal(self, hex_color):
        return self._get(("metal", hex_color), lambda: _principled(
            f"pearl {hex_color}", linear(hex_color), rough=.34, metallic=.18, sss=.1, coat=.25)[0])


class Wood(_Kit):
    """Hand-made toy: turned beech, painted wood and felt."""
    wood = True

    def natural(self, hex_color):
        def build():
            base = linear(hex_color)
            mat, bsdf = _principled(f"wood {hex_color}", base, rough=.5)
            _grain(mat, bsdf, base, shade(base, .8))
            return mat
        return self._get(("natural", hex_color), build)

    def skin(self, hex_color):
        """Lightly stained wood, with a very quiet grain so faces stay clean."""
        def build():
            base = linear(hex_color)
            mat, bsdf = _principled(f"stain {hex_color}", base, rough=.48)
            _grain(mat, bsdf, base, shade(base, .94), bump=.006)
            return mat
        return self._get(("skin", hex_color), build)

    def paint(self, hex_color):
        """Water-based stain: the colour dominates and the grain still shows through."""
        def build():
            base = linear(hex_color)
            mat, bsdf = _principled(f"painted {hex_color}", base, rough=.5, coat=.05)
            _grain(mat, bsdf, base, shade(base, .91), bump=.01)
            return mat
        return self._get(("paint", hex_color), build)

    def cloth(self, hex_color):
        def build():
            mat, bsdf = _principled(f"felt {hex_color}", linear(hex_color), rough=1.0, sheen=.6)
            _felt(mat, bsdf)
            return mat
        return self._get(("cloth", hex_color), build)

    def metal(self, hex_color):
        return self._get(("metal", hex_color), lambda: _principled(
            f"brass {hex_color}", linear(hex_color), rough=.38, metallic=.7)[0])


# Style direction -> (character kit, room kit)
STYLES = {
    "a": (Vinyl, Vinyl),
    "b": (Wood, Wood),
    "c": (Vinyl, Wood),
}


def kits(style):
    """Character and room kits. One instance when a style uses the same class for both."""
    chars, room = STYLES[style]
    c = chars()
    return c, (c if room is chars else room())
