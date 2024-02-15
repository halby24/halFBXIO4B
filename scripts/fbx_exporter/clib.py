import os
import ctypes
from .util import Singleton

class Vector2(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_double),
        ('y', ctypes.c_double),
    ]
    def __repr__(self):
        fields = ',\n'.join(f"{field}: {getattr(self, field)}" for field, _ in self._fields_)
        return f"{self.__class__.__name__}({fields})"

class Vector4(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_double),
        ('y', ctypes.c_double),
        ('z', ctypes.c_double),
        ('w', ctypes.c_double),
    ]
    def __repr__(self):
        fields = ',\n'.join(f"{field}: {getattr(self, field)}" for field, _ in self._fields_)
        return f"{self.__class__.__name__}({fields})"

class Material(ctypes.Structure):
    _fields_ = [
        ('name', ctypes.c_char_p),
        ('name_length', ctypes.c_size_t),
        ('diffuse', Vector4),
        ('specular', Vector4),
        ('emissive', Vector4),
    ]
    def __repr__(self):
        fields = ',\n'.join(f"{field}: {getattr(self, field)}" for field, _ in self._fields_)
        return f"{self.__class__.__name__}({fields})"

class Mesh(ctypes.Structure):
    _fields_ = [
        ('name', ctypes.c_char_p),
        ('name_length', ctypes.c_size_t),
        ('vertices', ctypes.POINTER(Vector4)),
        ('normals', ctypes.POINTER(Vector4)),
        ('uvs', ctypes.POINTER(Vector2)),
        ('vertex_count', ctypes.c_size_t),
        ('indices', ctypes.POINTER(ctypes.c_uint)),
        ('index_count', ctypes.c_size_t),
        ('polys', ctypes.POINTER(ctypes.c_uint)),
        ('material_indices', ctypes.POINTER(ctypes.c_uint)),
        ('poly_count', ctypes.c_size_t),
    ]
    def __repr__(self):
        fields = ',\n'.join(f"{field}: {getattr(self, field)}" for field, _ in self._fields_)
        return f"{self.__class__.__name__}({fields})"

class Object(ctypes.Structure):
    def __repr__(self):
        fields = ',\n'.join(f"{field}: {getattr(self, field)}" for field, _ in self._fields_)
        return f"{self.__class__.__name__}({fields})"
Object._fields_ = [
    ('name', ctypes.c_char_p),
    ('name_length', ctypes.c_size_t),
    ('local_matrix', ctypes.c_double * 16),
    ('children', ctypes.POINTER(Object)),
    ('child_count', ctypes.c_size_t),
    ('mesh', ctypes.POINTER(Mesh)),
    ('material_slots', ctypes.POINTER(Material)),
    ('material_slot_count', ctypes.c_size_t),
]

class ExportData(ctypes.Structure):
    _fields_ = [
        ('is_binary', ctypes.c_bool),
        ('unit_scale', ctypes.c_double),
        ('root', ctypes.POINTER(Object)),
        ('materials', ctypes.POINTER(Material)),
        ('material_count', ctypes.c_size_t),
    ]
    def __repr__(self):
        fields = ',\n'.join(f"{field}: {getattr(self, field)}" for field, _ in self._fields_)
        return f"{self.__class__.__name__}({fields})"

class CLib(Singleton):
    def __init__(self) -> None:
        self.__lib = ctypes.CDLL(os.path.dirname(os.path.abspath(__file__)) + '/lib/halFBXIO4B.dll')
        self.__init_functions()

    def __init_functions(self):
        self.__lib.export_fbx.argtypes = [ctypes.c_char_p, ctypes.POINTER(ExportData)]
        self.__lib.export_fbx.restype = ctypes.c_bool
        self.__lib.vertex_normal_from_poly_normal.argtypes = [ctypes.POINTER(ctypes.c_uint), ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint), ctypes.c_size_t, ctypes.POINTER(Vector4), ctypes.POINTER(Vector4)]
        self.__lib.vertex_normal_from_poly_normal.restype = None

    def export_fbx(self, filepath: str, export_data: ExportData) -> str:
        export_data_ptr = ctypes.pointer(export_data)
        return self.__lib.export_fbx(filepath.encode('utf-8'), export_data_ptr)

    def vertex_normal_from_poly_normal(self, indices: list[int], polys: list[int], normals: list[Vector4]) -> list[Vector4]:
        indices_array_ptr = ctypes.pointer((ctypes.c_uint * len(indices))(*indices))
        indices_ptr = ctypes.cast(indices_array_ptr, ctypes.POINTER(ctypes.c_uint))
        polys_array_ptr = ctypes.pointer((ctypes.c_uint * len(polys))(*polys))
        polys_ptr = ctypes.cast(polys_array_ptr, ctypes.POINTER(ctypes.c_uint))
        normals_array_ptr = ctypes.pointer((Vector4 * len(normals))(*normals))
        normals_ptr = ctypes.cast(normals_array_ptr, ctypes.POINTER(Vector4))
        out_vertex_normals_array = (Vector4 * len(indices))()
        out_vertex_normals_array_ptr = ctypes.pointer(out_vertex_normals_array)
        out_vertex_normals_ptr = ctypes.cast(out_vertex_normals_array_ptr, ctypes.POINTER(Vector4))
        self.__lib.vertex_normal_from_poly_normal(indices_ptr, len(indices), polys_ptr, len(polys), normals_ptr, out_vertex_normals_ptr)
        return list(out_vertex_normals_array)

    def createObject(self, name: str, local_matrix: list[float], children: list[Object], mesh: Mesh | None, material_slots: list[Material]) -> Object:
        children_array_ptr = ctypes.pointer((Object * len(children))(*children))
        children_ptr = ctypes.cast(children_array_ptr, ctypes.POINTER(Object))
        material_slots_array_ptr = ctypes.pointer((Material * len(material_slots))(*material_slots))
        material_slots_ptr = ctypes.cast(material_slots_array_ptr, ctypes.POINTER(Material))
        return Object(
            name=name.encode('utf-8'),
            name_length=len(name),
            local_matrix=(ctypes.c_double * 16)(*local_matrix),
            children=children_ptr,
            child_count=len(children),
            mesh=ctypes.pointer(mesh) if mesh else ctypes.POINTER(Mesh)(),
            material_slots=material_slots_ptr,
            material_slot_count=len(material_slots)
        )

    def createExportData(self, root: Object, is_binary: bool, unit_scale: float, materials: list[Material]) -> ExportData:
        materials_array_ptr = ctypes.pointer((Material * len(materials))(*materials))
        materials_ptr = ctypes.cast(materials_array_ptr, ctypes.POINTER(Material))
        return ExportData(
            root=ctypes.pointer(root),
            is_binary=is_binary,
            unit_scale=unit_scale,
            materials=materials_ptr,
        )

    def createMesh(self, name: str, vertices: list[Vector4], normals: list[Vector4], uvs: list[Vector2], indices: list[int], polys: list[int]) -> Mesh:
        vertices_array_ptr = ctypes.pointer((Vector4 * len(vertices))(*vertices))
        vertices_ptr = ctypes.cast(vertices_array_ptr, ctypes.POINTER(Vector4))
        normals_array_ptr = ctypes.pointer((Vector4 * len(normals))(*normals))
        normals_ptr = ctypes.cast(normals_array_ptr, ctypes.POINTER(Vector4))
        uvs_array_ptr = ctypes.pointer((Vector2 * len(uvs))(*uvs))
        uvs_ptr = ctypes.cast(uvs_array_ptr, ctypes.POINTER(Vector2))
        indices_array_ptr = ctypes.pointer((ctypes.c_uint * len(indices))(*indices))
        indices_ptr = ctypes.cast(indices_array_ptr, ctypes.POINTER(ctypes.c_uint))
        polys_array_ptr = ctypes.pointer((ctypes.c_uint * len(polys))(*polys))
        polys_ptr = ctypes.cast(polys_array_ptr, ctypes.POINTER(ctypes.c_uint))
        return Mesh(
            name=name.encode('utf-8'),
            name_length=len(name),
            vertices=vertices_ptr,
            normals=normals_ptr,
            uvs=uvs_ptr,
            vertex_count=len(vertices),
            indices=indices_ptr,
            index_count=len(indices),
            polys=polys_ptr,
            poly_count=len(polys)
        )

    def createMaterial(self, name: str, diffuse: Vector4, specular: Vector4, emissive: Vector4) -> Material:
        return Material(
            name=name.encode('utf-8'),
            name_length=len(name),
            diffuse=diffuse,
            specular=specular,
            emissive=emissive,
        )