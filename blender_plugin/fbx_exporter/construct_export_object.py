# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

import bpy
from .c_data_structure import *

class ConstructExportObject:
    def __init__(self, objs: [bpy.types.Object]) -> None:
        self.objs = objs
    
    def getExportData(self) -> ExportData:
        export_data = ExportData()
        for obj in self.objs:
            export_data.objects.append(self.getExportObject(obj))

    @staticmethod
    def getExportObjFromBlenderObj(obj: bpy.types.Object) -> ObjectData:
        obj_data = ObjectData()
        name_bytes = bytes(obj.name, 'utf-8')
        obj_data.name = ctypes.create_string_buffer(name_bytes)
        obj_data.name_length = len(name_bytes)
        obj_data.local_matrix = obj.matrix_local
        