# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

import bpy
from .construct_export_object import ConstructExportObject
from .lib.HalFbxExporter import export_fbx, destroy_export_data

class ExportService:
    def export(self, objs: list[bpy.types.Object], filepath: str, ext: str):
        filepath = bpy.path.ensure_ext(filepath, ext)

        export_objects = objs
        objConstructor = ConstructExportObject(export_objects)
        export_data = objConstructor.getExportData()
        result = export_fbx(filepath, export_data)
        destroy_export_data(export_data)
        
        # print(result)