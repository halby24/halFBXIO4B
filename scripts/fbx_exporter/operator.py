# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

from operator import is_
import bpy
import bpy_extras
from bpy.props import StringProperty, EnumProperty
from .expoter import Exporter

class halFBXIO4BOperator(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_export.hal_fbxio4b"
    bl_label = "halFBXIO4B"
    bl_options = {'UNDO', 'PRESET'}

    exporter = Exporter()

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
        name="保存形式",
        description="",
        items=(
            ('ascii', "ASCII", "FBX ASCII file format"),
            ('binary', "Binary", "FBX binary file format"),
        ),
        default='binary',
    )

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        layout.label(text="FBX SDKを使用してFBXファイルをエクスポートします。")

        box = layout.box()
        box.label(text="保存形式:")
        box.prop(self, "save_format")

    def execute(self, context: bpy.types.Context):
        objs = context.selected_objects
        filepath: str = self.filepath
        ext = self.filename_ext
        is_ascii = self.save_format == 'ascii'
        self.exporter.export(objs, is_ascii, filepath, ext)

        return {'FINISHED'}


def create_export_menu(self, context: bpy.types.Context):
    self.layout.operator(halFBXIO4BOperator.bl_idname, text="FBX Export (halFBXIO4B)")

def register():
    bpy.utils.register_class(halFBXIO4BOperator)
    bpy.types.TOPBAR_MT_file_export.append(create_export_menu)

def unregister():
    bpy.utils.unregister_class(halFBXIO4BOperator)
    bpy.types.TOPBAR_MT_file_export.remove(create_export_menu)
