# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

import bpy
import itertools
from .clib import IOData, Material, Mesh, UV, Normal, Object, CLib, Vector2, Vector4
import pprint
import ctypes

class ConstructIOObject:
    def __init__(self, objs: list[bpy.types.Object]) -> None:
        self.__clib = CLib()
        self.objs = objs

    def importData(self, path: str) -> None:
        idata = self.__clib.import_fbx(path)
        mats_ptr: ctypes.POINTER = idata.materials
        imats: ctypes.Array[Material] = mats_ptr.getArray()
        for imat in imats:
            bmat = bpy.data.materials.new(mat.name)
            bmat.use_nodes = True
            p_bsdf: bpy.types.Node = bmat.node_tree.nodes["Principled BSDF"]
            p_bsdf.inputs["Base Color"].default_value = (
                imat.basecolor.x,
                imat.basecolor.y,
                imat.basecolor.z,
                mat.basecolor.w,
            )
            p_bsdf.inputs["Metallic"].default_value = imat.metallic
            p_bsdf.inputs["Roughness"].default_value = imat.roughness
            p_bsdf.inputs["Emission"].default_value = (
                imat.emissive.x,
                imat.emissive.y,
                imat.emissive.z,
                imat.emissive.w,
            )
            p_bsdf.inputs["Alpha"].default_value = imat.basecolor.w
        self.__clib.delete_iodata(ctypes.pointer(idata))

    def getExportData(self, is_ascii: bool) -> IOData:
        mat_pairs = self.__createMatPairs(self.objs)
        objs = self.__getObjs(self.objs, mat_pairs)
        object = self.__clib.createObject(
            name="root",
            local_matrix=[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            children=objs,
            mesh=None,
            material_slots=[],  # Use the converted material_slots
        )
        scene = bpy.context.scene
        unit_scale = scene.unit_settings.scale_length
        materials = mat_pairs[1]
        export_data = self.__clib.createExportData(object, is_ascii, unit_scale, materials)
        return export_data

    def __getObjs(
        self,
        bobjs: list[bpy.types.Object],
        mat_pairs: tuple[list[bpy.types.Material], ctypes.Array[Material]],
    ) -> list[Object]:
        objs: list[Object] = []
        for bobj in bobjs:
            name = bobj.name
            m: list[list[float]] = bobj.matrix_local
            matrix_local = list(itertools.chain.from_iterable(m))
            children: list[Object] = self.__getObjs(list(bobj.children), mat_pairs)
            mesh_data = None
            if bobj.type == "MESH":
                depsgraph = bpy.context.evaluated_depsgraph_get()
                bmesh = bobj.evaluated_get(depsgraph).data
                mesh_data = self.__createMesh(bmesh)
            mat_slots: list[ctypes._Pointer[Material]] = []
            for slot in bobj.material_slots:
                bmat: bpy.types.Material = slot.material
                mat = mat_pairs[1][mat_pairs[0].index(bmat)]
                mat_slots.append(ctypes.pointer(mat))

            objs.append(
                self.__clib.createObject(
                    name, matrix_local, children, mesh_data, mat_slots
                )
            )
        return objs

    def __createMatPairs(
        self, bobjs: list[bpy.types.Object]
    ) -> tuple[list[bpy.types.Material], ctypes.Array[Material]]:
        bmats: list[bpy.types.Material] = []

        allbobjs: list[bpy.types.Object] = []
        for obj in bobjs:
            if obj not in allbobjs:
                allbobjs.append(obj)
            for child in list(obj.children):
                if child not in allbobjs:
                    allbobjs.append(child)

        for obj in allbobjs:
            for slot in obj.material_slots:
                mat: bpy.types.Material = slot.material
                if mat not in bmats:
                    bmats.append(mat)

        emats: ctypes.Array[Material] = (Material * len(bmats))()
        for bmat in bmats:
            emat = self.__createMatFromShader(bmat.name)
            emats[bmats.index(bmat)] = emat
        return (bmats, emats)

    def __createMesh(self, bmesh: bpy.types.Mesh) -> Mesh:
        polys: list[int] = []
        indices: list[int] = []
        mat_indices: list[int] = []
        index = 0
        is_smooth = bmesh.use_auto_smooth
        poly_index = 0
        for polygon in bmesh.polygons:
            polys.append(index)
            mat_indices.append(polygon.material_index - 1)
            poly_index += 1
            for vert in polygon.vertices:
                indices.append(vert)
                index += 1

        normals: list[Normal] = self.__createNormals(bmesh, indices, polys)

        uvs: list[UV] = []
        for uv_layer in bmesh.uv_layers:
            uv = [Vector2(uv.vector.x, uv.vector.y) for uv in uv_layer.uv]
            uvs.append(
                self.__clib.createUV(
                    uv_layer.name,
                    uv,
                )
            )

        vertices: list[Vector4] = []
        for vertex in bmesh.vertices:
            vertices.append(Vector4(vertex.co.x, vertex.co.y, vertex.co.z, 1))

        mesh = self.__clib.createMesh(
            bmesh.name, vertices, normals, uvs, indices, polys, mat_indices, is_smooth
        )

        return mesh

    def __createNormals(
        self, bmesh: bpy.types.Mesh, indices: list[int], polys: list[int]
    ) -> list[Normal]:
        normals: list[Normal] = []

        if len(bmesh.corner_normals) > 0:  # 頂点法線の場合
            normal_vecs: list[Vector4] = []
            for corner_normal in bmesh.corner_normals:
                normal_vecs.append(
                    Vector4(corner_normal.x, corner_normal.y, corner_normal.z, 1)
                )
            normal = self.__clib.createNormal("Normal", normal_vecs)
            normals.append(normal)

        elif len(bmesh.polygon_normals) > 0:  # 面法線の場合
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
            vertex_normals = self.__clib.vnrm_from_pnrm(indices, polys, poly_normals)
            normal_vecs: list[Vector4] = []
            for vertex_normal in vertex_normals:
                normal_vecs.append(
                    Vector4(vertex_normal.x, vertex_normal.y, vertex_normal.z, 1)
                )
            normal = self.__clib.createNormal("Normal", normal_vecs)
            normals.append(normal)

        return normals

    def __createMatFromShader(self, name: str) -> Material:
        mat = bpy.data.materials[name]
        node_tree = mat.node_tree
        nodes = node_tree.nodes
        bsdf: bpy.types.Node = nodes.get("Principled BSDF")

        basecolor: tuple[float, float, float, float] = (1, 1, 1, 1)
        metallic: float = 0
        roughness: float = 0.5
        emissive: tuple[float, float, float, float] = (0, 0, 0, 1)
        opacity: float = 1
        if bsdf is not None:
            basecolor: tuple[float, float, float, float] = bsdf.inputs[
                "Base Color"
            ].default_value
            metallic: float = bsdf.inputs["Metallic"].default_value
            roughness: float = bsdf.inputs["Roughness"].default_value
            emissive: tuple[float, float, float, float] = bsdf.inputs[
                "Emission Color"
            ].default_value
            opacity: float = bsdf.inputs["Alpha"].default_value

        return self.__clib.createMaterial(
            name,
            basecolor=Vector4(basecolor[0], basecolor[1], basecolor[2], opacity),
            metallic=metallic,
            roughness=roughness,
            emissive=Vector4(emissive[0], emissive[1], emissive[2], 1),
        )
