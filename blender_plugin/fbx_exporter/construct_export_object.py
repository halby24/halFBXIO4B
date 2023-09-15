# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

import itertools
import bpy
from .c_data_structure import *
from collections import namedtuple

class ConstructExportObject:
    def __init__(self, objs: list[bpy.types.Object]) -> None:
        self.objs = objs
    
    def getExportData(self) -> ExportData:
        export_data = ExportData()
        export_objs = self.getExportObjsFromBlenderObjs(self.objs)
        export_data.objects = (ObjectData * len(export_objs))(*export_objs)
        export_data.object_count = len(export_objs)
        return export_data

    @staticmethod
    def getExportObjsFromBlenderObjs(objs: list[bpy.types.Object]) -> list[ObjectData]:
        # create object data
        obj_infos = []
        for obj_orig in objs:
            obj_data = ObjectData()
            obj_data.name = obj_orig.name.encode('utf-8')
            obj_data.matrix_local = list(itertools.chain.from_iterable(obj_orig.matrix_local)) # flatten matrix_local
            obj_data.parent = None
            obj_infos.append([obj_orig, obj_data])
        
        # set parent
        export_objs = []
        for obj_orig, obj_data in obj_infos:
            if obj_orig.parent is not None:
                parent_obj = obj_orig.parent
                for parent_obj_orig, parent_obj_data in obj_infos:
                    if parent_obj_orig == parent_obj:
                        obj_data.parent = parent_obj_data.pointer()
                        break
            export_objs.append(obj_data)
        
        return export_objs
