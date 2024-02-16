# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

import bpy
import itertools
from .clib import ExportData, Material, Mesh, Object, CLib, Vector2, Vector4


class ConstructExportObject:
    def __init__(self, objs: list[bpy.types.Object]) -> None:
        self.__clib = CLib()
        self.objs = objs

    def getExportData(self) -> ExportData:
        mat_pairs = self.__createMatPairs(self.objs)
        objs = self.__getObjs(self.objs, mat_pairs)
        material_slots = [mat[1] for mat in mat_pairs]  # Convert mats to list[Material]
        object = self.__clib.createObject(
            name="root",
            local_matrix=[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            children=objs,
            mesh=None,
            material_slots=material_slots,  # Use the converted material_slots
        )
        scene = bpy.context.scene
        unit_scale = scene.unit_settings.scale_length
        materials = [mat[1] for mat in mat_pairs]  # Convert mats to list[Material]
        export_data = self.__clib.createExportData(object, False, unit_scale, materials)
        return export_data

    def __getObjs(
        self,
        bobjs: list[bpy.types.Object],
        mat_pairs: list[tuple[bpy.types.Material, Material]],
    ) -> list[Object]:
        objs: list[Object] = []
        for bobj in bobjs:
            name = bobj.name
            m: list[list[float]] = bobj.matrix_local
            matrix_local = list(itertools.chain.from_iterable(m))
            children: list[Object] = []
            mesh_data = None
            if bobj.type == "MESH":
                mesh_data = self.__createMesh(bobj.data)
            mat_slots: list[Material] = []
            for slot in bobj.material_slots:
                bmat: bpy.types.Material = slot.material
                mat = mat_pairs[[mat[0] for mat in mat_pairs].index(bmat)][1]
                mat_slots.append(mat)

            objs.append(
                self.__clib.createObject(
                    name, matrix_local, children, mesh_data, mat_slots
                )
            )
        return objs

    def __createMatPairs(
        self, bobjs: list[bpy.types.Object]
    ) -> list[tuple[bpy.types.Material, Material]]:
        bmats: list[bpy.types.Material] = []
        for obj in bobjs:
            for slot in obj.material_slots:
                mat: bpy.types.Material = slot.material  # type: ignore
                if mat not in bmats:
                    bmats.append(mat)

        mats: list[tuple[bpy.types.Material, Material]] = []
        for bmat in bmats:
            mats.append(
                (
                    bmat,
                    Material(
                        name=bmat.name.encode("utf-8"),
                        name_length=len(bmat.name),
                        diffuse_color=Vector4(
                            bmat.diffuse_color[0],
                            bmat.diffuse_color[1],
                            bmat.diffuse_color[2],
                            1,
                        ),
                        specular_color=Vector4(
                            bmat.specular_color[0],
                            bmat.specular_color[1],
                            bmat.specular_color[2],
                            1,
                        ),
                        shininess=bmat.specular_hardness,
                    ),
                )
            )

        return mats

    def __createMesh(self, bmesh: bpy.types.Mesh) -> Mesh:
        polys: list[int] = []
        indices: list[int] = []
        index = 0

        poly_index = 0
        for polygon in bmesh.polygons:
            polys.append(index)
            print("polygon: ", poly_index)
            poly_index += 1
            for vert in polygon.vertices:
                indices.append(vert)
                print("vert: ", vert)
                index += 1

        normals: list[Vector4] = []
        if len(bmesh.corner_normals) > 0: # 頂点法線の場合
            for corner_normal in bmesh.corner_normals:
                normals.append(
                    Vector4(
                        corner_normal.x, corner_normal.y, corner_normal.z, 1
                    )
                )
        elif len(bmesh.polygon_normals) > 0: # 面法線の場合
            poly_normals: list[Vector4] = []
            for polygon_normal in bmesh.polygon_normals:
                poly_normals.append(
                    Vector4(
                        polygon_normal.vector.x,
                        polygon_normal.vector.y,
                        polygon_normal.vector.z,
                        1,
                    )
                )
            vertex_normals = self.__clib.vertex_normal_from_poly_normal(
                indices, polys, poly_normals
            )
            for vertex_normal in vertex_normals:
                normals.append(
                    Vector4(
                        vertex_normal.x, vertex_normal.y, vertex_normal.z, 1
                    )
                )

        uvs: list[Vector2] = []
        uv_layer: bpy.types.MeshUVLoopLayer = bmesh.uv_layers[0]
        for uv in uv_layer.uv:
            uvs.append(Vector2(uv.vector.x, uv.vector.y))

        vertices: list[Vector4] = []
        for vertex in bmesh.vertices:
            vertices.append(Vector4(vertex.co.x, vertex.co.y, vertex.co.z, 1))

        mesh = self.__clib.createMesh(
            bmesh.name, vertices, normals, uvs, indices, polys
        )

        return mesh