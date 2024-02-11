# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

import bpy
from collections import namedtuple
from .clib import ExportData, ObjectData, CLib

class ConstructExportObject:
    def __init__(self, objs: list[bpy.types.Object]) -> None:
        self.__clib = CLib()
        self.objs = objs
    
    def getExportData(self) -> ExportData:
        export_objs = self.getExportObjsFromBlenderObjs(self.objs)
        object_data = self.__clib.createObjectData(
            'root', # name
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1], # local matrix
            export_objs, # children
            None # mesh
        )
        scene = bpy.context.scene
        unit_scale = scene.unit_settings.scale_length
        export_data = self.__clib.createExportData(object_data, False, unit_scale)
        return export_data

    def getExportObjsFromBlenderObjs(self, objs: list[bpy.types.Object]) -> list[ObjectData]:
        # create object data
        obj_infos = []
        for i, obj_orig in enumerate(objs):
            name = obj_orig.name
            m = obj_orig.matrix_local
            matrix_local = [m[0][0], m[0][1], m[0][2], m[0][3], m[1][0], m[1][1], m[1][2], m[1][3], m[2][0], m[2][1], m[2][2], m[2][3], m[3][0], m[3][1], m[3][2], m[3][3]]
            children = []
            mesh_data = None
            if obj_orig.type == 'MESH':
                mesh = obj_orig.data
                vertices = []
                for vertex in mesh.vertices:
                    vertices.append(vertex.co.x)
                    vertices.append(vertex.co.y)
                    vertices.append(vertex.co.z)
                    vertices.append(1)
                faces = []
                for face in mesh.polygons:
                    face_data = self.__clib.createFaceData(face.vertices)
                    faces.append(face_data)
                mesh_data = self.__clib.createMeshData(vertices, faces) 
            obj_infos.append(self.__clib.createObjectData(name, matrix_local, children, mesh_data))
        return obj_infos
