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

class MeshData(ctypes.Structure):
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
        ('poly_count', ctypes.c_size_t),
    ]
    def __repr__(self):
        fields = ',\n'.join(f"{field}: {getattr(self, field)}" for field, _ in self._fields_)
        return f"{self.__class__.__name__}({fields})"

class ObjectData(ctypes.Structure):
    def __repr__(self):
        fields = ',\n'.join(f"{field}: {getattr(self, field)}" for field, _ in self._fields_)
        return f"{self.__class__.__name__}({fields})"
ObjectData._fields_ = [
    ('name', ctypes.c_char_p),
    ('name_length', ctypes.c_size_t),
    ('local_matrix', ctypes.c_double * 16),
    ('children', ctypes.POINTER(ObjectData)),
    ('child_count', ctypes.c_size_t),
    ('mesh', ctypes.POINTER(MeshData)),
]

class ExportData(ctypes.Structure):
    _fields_ = [
        ('is_binary', ctypes.c_bool),
        ('unit_scale', ctypes.c_double),
        ('root', ctypes.POINTER(ObjectData)),
    ]
    def __repr__(self):
        fields = ',\n'.join(f"{field}: {getattr(self, field)}" for field, _ in self._fields_)
        return f"{self.__class__.__name__}({fields})"

class CLib(Singleton):
    def __init__(self) -> None:
        self.__lib = ctypes.CDLL(os.path.dirname(os.path.abspath(__file__)) + '/lib/HalFbxExporter.dll')
        self.__init_functions()
    
    def __init_functions(self):
        self.__lib.export_fbx.argtypes = [ctypes.c_char_p, ctypes.POINTER(ExportData)]
        self.__lib.export_fbx.restype = ctypes.c_bool
        self.__lib.vertex_normal_from_poly_normal.argtypes = [ctypes.POINTER(ctypes.c_uint), ctypes.c_size_t, ctypes.POINTER(ctypes.c_uint), ctypes.c_size_t, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
        self.__lib.vertex_normal_from_poly_normal.restype = None
    
    def export_fbx(self, filepath: str, export_data: ctypes.POINTER) -> str:
        return self.__lib.export_fbx(filepath.encode('utf-8'), export_data)
    
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
    
    def createObjectData(self, name: str, local_matrix: list[float], children: list[ObjectData], mesh: MeshData) -> ObjectData:
        children_array_ptr = ctypes.pointer((ObjectData * len(children))(*children))
        children_ptr = ctypes.cast(children_array_ptr, ctypes.POINTER(ObjectData))
        return ObjectData(
            name=name.encode('utf-8'),
            name_length=len(name),
            local_matrix=(ctypes.c_double * 16)(*local_matrix),
            children=children_ptr,
            child_count=len(children),
            mesh=ctypes.pointer(mesh) if mesh else ctypes.POINTER(MeshData)()
        )
    
    def createExportData(self, root: ObjectData, is_binary: bool, unit_scale: float) -> ExportData:
        return ExportData(
            root=ctypes.pointer(root),
            is_binary=is_binary,
            unit_scale=unit_scale
        )
    
    def createMeshData(self, name: str, vertices: list[Vector4], normals: list[Vector4], uvs: list[Vector2], indices: list[int], polys: list[int]) -> MeshData:
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
        return MeshData(
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