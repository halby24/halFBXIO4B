# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

import bpy

class HALFBXEXP_PT_panel(bpy.types.Panel):
    bl_label = ""
    bl_idname = "HALFBXEXP_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hal Fbx Exporter'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Hello world!", icon='WORLD_DATA')