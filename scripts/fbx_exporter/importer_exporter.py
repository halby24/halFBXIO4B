# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

import bpy
from .construct_export_object import ConstructIOObject
from .clib import CLib


class Exporter:
    def __init__(self) -> None:
        self.__clib = CLib()
        pass

    def export(self, objs: list[bpy.types.Object], is_ascii: bool, filepath: str, ext: str):
        filepath = bpy.path.ensure_ext(filepath, ext)

        eo = ConstructIOObject(objs)
        data = eo.getExportData(is_ascii)
        result = self.__clib.export_fbx(filepath, data)

        print(result)

class Importer:
    def __init__(self) -> None:
        self.__clib = CLib()
        pass

    def importData(self, path: str) -> None:
        eo = ConstructIOObject([])
        eo.importData(path)
        pass
