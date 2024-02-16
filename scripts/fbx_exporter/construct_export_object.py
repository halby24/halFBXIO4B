# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

import bpy
import itertools
from .clib import ExportData, Material, Object, CLib, Vector2, Vector4

class ConstructExportObject:
    def __init__(self, objs: list[bpy.types.Object]) -> None:
        self.__clib = CLib()
        self.objs = objs

    def getExportData(self) -> ExportData:
        objs = self.getObjs(self.objs)
        mats = self.getMats(self.objs)
        object_data = self.__clib.createObject(
            name='root',
            local_matrix=[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            children=objs,
            mesh=None,
            material_slots=mats
        )
        scene = bpy.context.scene
        unit_scale = scene.unit_settings.scale_length
        export_data = self.__clib.createExportData(object_data, False, unit_scale, mats)
        return export_data

    def getObjs(self, bobjs: list[bpy.types.Object]) -> list[Object]:
        objs: list[Object] = []
        for i, bobj in enumerate(bobjs):
            name = bobj.name
            m: list[list[float]] = bobj.matrix_local
            matrix_local = list(itertools.chain.from_iterable(m))
            children: list[Object] = []
            mesh_data = None
            if bobj.type == 'MESH':
                mesh = bobj.data
                polys: list[int] = []
                indices: list[int] = []
                index = 0
                poly_index = 0
                for polygon in mesh.polygons:
                    polys.append(index)
                    print('polygon: ', poly_index)
                    poly_index += 1
                    for vert in polygon.vertices:
                        indices.append(vert)
                        print('vert: ', vert)
                        index += 1
                normals: list[Vector4] = []
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
                vertices: list[Vector4] = []
                for vertex in mesh.vertices:
                    vertices.append(Vector4(vertex.co.x, vertex.co.y, vertex.co.z, 1))
                mesh_data = self.__clib.createMesh(mesh.name, vertices, normals, [], indices, polys)
            mat_slots: list[Material] = []
            for slot in bobj.material_slots:
                mat: bpy.types.Material = slot.material # type: ignore
                mat_slots.append(self.__clib.createMaterial(
                    name=mat.name,
                    diffuse=Vector4(mat.diffuse_color[0], mat.diffuse_color[1], mat.diffuse_color[2], 1),
                    specular=Vector4(mat.specular_color[0], mat.specular_color[1], mat.specular_color[2], 1),
                    emissive=Vector4(0, 0, 0, 1)
                ))
            objs.append(self.__clib.createObject(name, matrix_local, children, mesh_data, mat_slots))
        return objs

    def getMats(self, bobjs: list[bpy.types.Object]) -> list[Material]:
        bmats: list[bpy.types.Material] = []
        for obj in bobjs:
            for slot in obj.material_slots:
                mat: bpy.types.Material = slot.material # type: ignore
                if mat not in bmats:
                    bmats.append(mat)
        mats: list[Material] = []
        for bmat in bmats:
            mats.append(self.__clib.createMaterial(
                name=bmat.name,
                diffuse=Vector4(bmat.diffuse_color[0], bmat.diffuse_color[1], bmat.diffuse_color[2], 1),
                specular=Vector4(bmat.specular_color[0], bmat.specular_color[1], bmat.specular_color[2], 1),
                emissive=Vector4(0, 0, 0, 1)
            ))
        return mats
