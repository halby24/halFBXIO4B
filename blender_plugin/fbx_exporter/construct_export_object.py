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
        obj_data.name = obj.name
        