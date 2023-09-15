# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

bl_info = {
    "name" : "HalFbxExporter",
    "author" : "HALBY",
    "description" : "Export fbx files with official FBX SDK.",
    "blender" : (3, 6, 0),
    "version" : (0, 0, 1),
    "category": "Import-Export",
    "location": "File > Import-Export",
    "warning" : "",
}

from . import auto_load

auto_load.init()

def register():
    auto_load.register()

def unregister():
    auto_load.unregister()
