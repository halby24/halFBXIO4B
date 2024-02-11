# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

import bpy
from .construct_export_object import ConstructExportObject
from .clib import CLib
import pprint

class Exporter:
    def __init__(self) -> None:
        self.__clib = CLib()
        pass

    def export(self, objs: list[bpy.types.Object], filepath: str, ext: str):
        filepath = bpy.path.ensure_ext(filepath, ext)

        eo = ConstructExportObject(objs)
        data = eo.getExportData()
        result = self.__clib.export_fbx(filepath, data)

        print(result)