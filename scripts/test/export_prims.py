# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

import bpy
from ..fbx_exporter.importer_exporter import Exporter

# add primitives
cube = bpy.ops.mesh.primitive_cube_add()
bpy.context.object.name = "Cube"
bpy.context.object.location = (0, 0, 0)

ico_sphere = bpy.ops.mesh.primitive_ico_sphere_add()
bpy.context.object.name = "IcoSphere"
bpy.context.object.location = (2, 0, 0)

objs = [cube, ico_sphere]

# export fbx
export_service = Exporter()
export_service.export(objs, "test.fbx", ".fbx")
