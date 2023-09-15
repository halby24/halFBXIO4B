# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

import bpy
import ctypes

class ConstructExportObject:
    def __init__(self, objs: [bpy.types.Object]) -> None:
        self.objs = objs
    
    
    def getExportData(self) -> bytes:
        pass