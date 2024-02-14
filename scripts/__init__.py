# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

bl_info = {
    "name" : "halFBXIO4B",
    "author" : "HALBY",
    "description" : "Export fbx files with official FBX SDK.",
    "blender" : (4, 0, 0),
    "version" : (0, 0, 1),
    "category": "Import-Export",
    "location": "File > Import-Export",
    "warning" : "",
    "support" : "TESTING",
}

from . import fbx_exporter

def register():
    fbx_exporter.register()

def unregister():
    fbx_exporter.unregister()
