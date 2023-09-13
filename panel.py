# Copyright 2023 HALBY
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

class HALFBXEXP_PT_panel(bpy.types.Panel):
    bl_label = "Main Settings"
    bl_idname = "HALFBXEXP_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hal Fbx Exporter'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Hello world!", icon='WORLD_DATA')