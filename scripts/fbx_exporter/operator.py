# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

import os
import ctypes
import bpy
import bpy_extras
from bpy.props import StringProperty, EnumProperty
from .i18n import fbx_exporter_dict
from .export_service import ExportService

class HALFBXEXP_OT_FbxExporter(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_export.halfbxexp_fbx_exporter"
    bl_label = "HalFbxExporter"
    bl_options = {'UNDO', 'PRESET'}

    export_service = ExportService()

    # ExportHelper mixin class uses this
    filename_ext = ".fbx"

    filter_glob: StringProperty(
        default="*.fbx",
        options={'HIDDEN'},
        maxlen=255, # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    save_format: EnumProperty(
        name="Save Format",
        description="FBX save format",
        items=(
            ('ascii', "ASCII", "FBX ASCII file format"),
            ('binary', "Binary", "FBX binary file format"),
        ),
        default='BINARY',
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Exporting fbx files with official FBX SDK.")

        box = layout.box()
        box.label(text="Save Format:")
        box.prop(self, "save_format")

    def execute(self, context):
        objs = context.selected_objects
        filepath = self.filepath
        ext = self.filename_ext
        self.export_service.export(objs, filepath, ext)

        return {'FINISHED'}


def create_export_menu(self, context):
    self.layout.operator(HALFBXEXP_OT_FbxExporter.bl_idname, text="HalFbxExporter (.fbx)")

def register():
    bpy.types.TOPBAR_MT_file_export.append(create_export_menu)
    bpy.app.translations.register(__name__, fbx_exporter_dict)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(create_export_menu)
    bpy.app.translations.unregister(__name__)