# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

import bpy
from collections import namedtuple
from .clib import ExportData, ObjectData, CLib, Vector2, Vector4

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
                polys = []
                indices = []
                index = 0
                print('mesh: ', mesh.name, '\nvertices: ', len(mesh.vertices), '\npolygons: ', len(mesh.polygons))
                for polygon in mesh.polygons:
                    polys.append(index)
                    print('polygon: ', index)
                    for vert in polygon.vertices:
                        indices.insert(0, vert)
                        print('vert: ', vert)
                        index += 1
                normals = []
                if len(mesh.corner_normals) > 0:
                    for corner_normal in mesh.corner_normals:
                        normals.append(Vector4(corner_normal.x, corner_normal.y, corner_normal.z, 1))
                elif len(mesh.polygon_normals) > 0:
                    poly_normals = []
                    for polygon_normal in mesh.polygon_normals:
                        poly_normals.append(Vector4(polygon_normal.vector.x, polygon_normal.vector.y, polygon_normal.vector.z, 1))
                    vertex_normals = self.__clib.vertex_normal_from_poly_normal(indices, polys, poly_normals)
                    for vertex_normal in vertex_normals:
                        normals.append(Vector4(vertex_normal.x, vertex_normal.y, vertex_normal.z, 1))
                vertices = []
                for vertex in mesh.vertices:
                    vertices.append(Vector4(vertex.co.x, vertex.co.y, vertex.co.z, 1))
                mesh_data = self.__clib.createMeshData(mesh.name, vertices, normals, [], indices, polys)
            obj_infos.append(self.__clib.createObjectData(name, matrix_local, children, mesh_data))
        return obj_infos
