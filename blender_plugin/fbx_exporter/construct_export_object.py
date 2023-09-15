# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

import itertools
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
    def getExportObjsFromBlenderObjs(objs: [bpy.types.Object]) -> [ObjectData]:
        obj_datas = []
        for obj in objs:
            obj_data = ObjectData()
            name_bytes = bytes(obj.name, 'utf-8')
            obj_data.name = ctypes.create_string_buffer(name_bytes)
            obj_data.name_length = len(name_bytes)
            obj_data.matrix_local = list(itertools.chain.from_iterable(obj.matrix_local)) # flatten matrix_local
            obj_datas.append([obj, obj_data])
        
        export_objs = []
        for obj, obj_data in obj_datas:
            if obj.parent is None:
                export_objs.append(obj_data)
            else:
                parent_obj = obj.parent
                parent_obj_data = [obj_data for obj_data in obj_datas if obj_data[0] == parent_obj][0][1]
        