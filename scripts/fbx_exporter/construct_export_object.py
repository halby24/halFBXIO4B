# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

import itertools
import bpy
from collections import namedtuple
from .lib.HalFbxExporter import create_object_data, create_export_data, ExportData, ObjectData

class ConstructExportObject:
    def __init__(self, objs: list[bpy.types.Object]) -> None:
        self.objs = objs
    
    def getExportData(self) -> ExportData:
        export_objs = self.getExportObjsFromBlenderObjs(self.objs)
        object_data = create_object_data(
            'root', # name
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1], # local matrix
            export_objs, # children
            [] # vertices
        )
        export_data = create_export_data(object_data, False)
        return export_data

    @staticmethod
    def getExportObjsFromBlenderObjs(objs: list[bpy.types.Object]) -> list[ObjectData]:
        # create object data
        obj_infos = []
        for obj_orig in objs:
            name = obj_orig.name.encode('utf-8')
            m = obj_orig.matrix_local
            matrix_local = [m[0][0], m[0][1], m[0][2], m[0][3], m[1][0], m[1][1], m[1][2], m[1][3], m[2][0], m[2][1], m[2][2], m[2][3], m[3][0], m[3][1], m[3][2], m[3][3]]
            children = []
            vertices = []
            obj_infos.append(create_object_data(name, matrix_local, children, vertices))
        return obj_infos
