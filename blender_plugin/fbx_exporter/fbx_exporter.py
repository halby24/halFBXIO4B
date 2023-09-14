# Copyright 2023 HALBY
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import os
import ctypes
import bpy
import bpy_extras
from bpy.props import StringProperty, EnumProperty
from .i18n import fbx_exporter_dict

class HALFBXEXP_OT_FbxExporter(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_export.halfbxexp_fbx_exporter"
    bl_label = "HalFbxExporter"
    bl_options = {'UNDO', 'PRESET'}

    fbxlib = ctypes.CDLL(os.path.join(os.path.dirname(__file__), "..", "bin", "HalFbxExporter." + ("dll" if os.name == "nt" else "so")))

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
        filepath = bpy.path.ensure_ext(self.filepath, self.filename_ext)

        export_objects = bpy.context.selected_objects

        return {'FINISHED'}


def create_export_menu(self, context):
    self.layout.operator(HALFBXEXP_OT_FbxExporter.bl_idname, text="HalFbxExporter (.fbx)")

def register():
    bpy.types.TOPBAR_MT_file_export.append(create_export_menu)
    bpy.app.translations.register(__name__, fbx_exporter_dict)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(create_export_menu)
    bpy.app.translations.unregister(__name__)