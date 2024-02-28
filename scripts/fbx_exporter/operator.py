# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

from operator import is_
import bpy
import bpy_extras
from bpy.props import StringProperty, EnumProperty
from .importer_exporter import Exporter, Importer

class halFBXExporterOperator(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
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

class halFBXImporterOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_export.hal_fbxio4b"
    bl_label = "halFBXIO4B"
    bl_options = {'UNDO', 'PRESET'}

    importer = Importer()

    # ImportHelper mixin class uses this
    filename_ext = ".fbx"

    filter_glob: StringProperty(
        default="*.fbx",
        options={'HIDDEN'},
        maxlen=255, # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context: bpy.types.Context):
        path = self.filepath
        self.importer.importData(path)

        return {'FINISHED'}


def create_export_menu(self, context: bpy.types.Context):
    self.layout.operator(halFBXExporterOperator.bl_idname, text="FBX Export (halFBXIO4B)")

def create_import_menu(self, context: bpy.types.Context):
    self.layout.operator(halFBXImporterOperator.bl_idname, text="FBX Import (halFBXIO4B)")

def register():
    bpy.utils.register_class(halFBXExporterOperator)
    bpy.utils.register_class(halFBXImporterOperator)
    bpy.types.TOPBAR_MT_file_export.append(create_export_menu)
    bpy.types.TOPBAR_MT_file_import.append(create_import_menu)

def unregister():
    bpy.utils.unregister_class(halFBXExporterOperator)
    bpy.utils.unregister_class(halFBXImporterOperator)
    bpy.types.TOPBAR_MT_file_export.remove(create_export_menu)
    bpy.types.TOPBAR_MT_file_import.remove(create_import_menu)
