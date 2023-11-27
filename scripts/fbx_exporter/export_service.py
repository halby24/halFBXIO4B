# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

import os
import ctypes
import bpy
from .construct_export_object import ConstructExportObject
from .c_data_structure import ExportData

class ExportService:
    fbxlib = ctypes.cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), "..", "bin", "HalFbxExporter." + ("dll" if os.name == "nt" else "so")))

    def export(self, objs: list[bpy.types.Object], filepath: str, ext: str):
        filepath = bpy.path.ensure_ext(filepath, ext)

        export_objects = objs
        
        objConstructor = ConstructExportObject(export_objects)
        export_data = objConstructor.getExportData()

        export_fbx = self.fbxlib.ExportFbx
        export_fbx.argtypes = [ctypes.c_char_p, ctypes.POINTER(ExportData)]
        export_fbx.restype = ctypes.c_int
        result = export_fbx(filepath.encode('utf-8'), ctypes.pointer(export_data))
        print(result)