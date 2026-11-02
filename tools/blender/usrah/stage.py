"""Render setup: Cycles on the GPU, cameras and lights for character sheets."""
import bmesh
import bpy
from mathutils import Vector

from .materials import linear


def setup_render(out, width=1600, height=900, samples=128):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.filepath = str(out)
    scene.render.image_settings.file_format = "PNG"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = "OPENIMAGEDENOISE"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    for device in prefs.devices:
        device.use = True
    scene.cycles.device = "GPU"
    return scene


def world(hex_color, strength=1.0):
    w = bpy.data.worlds.new("world")
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = linear(hex_color)
    bg.inputs["Strength"].default_value = strength
    bpy.context.scene.world = w


def aim(ob, target):
    direction = Vector(target) - ob.location
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = direction.to_track_quat("-Z", "Y")


def camera(loc, target=None, lens=50.0, shift_y=0.0, rot=None):
    cam = bpy.data.objects.new("camera", bpy.data.cameras.new("camera"))
    bpy.context.collection.objects.link(cam)
    cam.location = loc
    cam.data.lens = lens
    cam.data.sensor_width = 36
    cam.data.shift_y = shift_y
    if target:
        aim(cam, target)
    elif rot:
        cam.rotation_euler = rot
    bpy.context.scene.camera = cam
    return cam


def area_light(name, loc, target, size, power, hex_color="#FFFFFF"):
    light = bpy.data.lights.new(name, "AREA")
    light.shape = "RECTANGLE"
    light.size, light.size_y = size if isinstance(size, tuple) else (size, size)
    light.energy = power
    light.color = linear(hex_color)[:3]
    ob = bpy.data.objects.new(name, light)
    bpy.context.collection.objects.link(ob)
    ob.location = loc
    aim(ob, target)
    return ob


def sun_light(name, direction, energy, hex_color="#FFFFFF", angle_deg=3.0):
    from math import radians
    light = bpy.data.lights.new(name, "SUN")
    light.energy = energy
    light.angle = radians(angle_deg)
    light.color = linear(hex_color)[:3]
    ob = bpy.data.objects.new(name, light)
    bpy.context.collection.objects.link(ob)
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = Vector(direction).normalized().to_track_quat("-Z", "Y")
    return ob


def cyclorama(mat, width=14.0, floor_depth=7.0, height=7.0, radius=1.6, back=3.0):
    """Seamless studio sweep behind a character lineup."""
    import math
    profile = [(-floor_depth, 0.0), (back - radius, 0.0)]
    for i in range(1, 13):
        a = math.pi / 2 * i / 12
        profile.append((back - radius + radius * math.sin(a), radius - radius * math.cos(a)))
    profile.append((back, height))
    bm = bmesh.new()
    left = [bm.verts.new((-width / 2, y, z)) for y, z in profile]
    right = [bm.verts.new((width / 2, y, z)) for y, z in profile]
    for i in range(len(profile) - 1):
        bm.faces.new((left[i], right[i], right[i + 1], left[i + 1]))
    me = bpy.data.meshes.new("cyclorama")
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    me.materials.append(mat)
    ob = bpy.data.objects.new("cyclorama", me)
    bpy.context.collection.objects.link(ob)
    return ob


def studio(backdrop_mat):
    """Soft three-light studio for model sheets."""
    world("#F7F0E4", .55)
    cyclorama(backdrop_mat)
    area_light("key", (-2.6, -3.6, 3.6), (0, 0, .6), (4.5, 4.5), 230, "#FFF3E2")
    area_light("fill", (3.4, -3.0, 1.6), (0, 0, .6), (4, 4), 70, "#EEF3FF")
    area_light("rim", (.6, 2.2, 3.4), (0, 0, .8), (3.4, 1.8), 70, "#FFFFFF")
