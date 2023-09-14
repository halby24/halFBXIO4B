# Copyright 2023 HALBY
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import bpy
import bpy_extras
from bpy.props import StringProperty

class FbxExporter(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "hal_fbx_export.fbx"
    bl_label = "HalFbxExporter"
    bl_options = {'UNDO', 'PRESET'}

    # ExportHelper mixin class uses this
    filename_ext = ".fbx"

    filter_glob: StringProperty(
        default="*.fbx",
        options={'HIDDEN'},
        maxlen=255, # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        pass


def create_export_menu(self, context):
    self.layout.operator(FbxExporter.bl_idname, text="HalFbxExporter (.fbx)")

def register():
    bpy.types.TOPBAR_MT_file_export.append(create_export_menu)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(create_export_menu)