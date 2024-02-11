import os
import ctypes
from .util import Singleton

class FaceData(ctypes.Structure):
    _fields_ = [
        ('indices', ctypes.POINTER(ctypes.c_uint)),
        ('index_count', ctypes.c_size_t),
    ]
    def __repr__(self):
        fields = ',\n'.join(f"{field}: {getattr(self, field)}" for field, _ in self._fields_)
        return f"{self.__class__.__name__}({fields})"

class MeshData(ctypes.Structure):
    _fields_ = [
        ('vertices', ctypes.POINTER(ctypes.c_double)),
        ('vertex_count', ctypes.c_size_t),
        ('faces', ctypes.POINTER(FaceData)),
        ('face_count', ctypes.c_size_t),
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
        ('root', ctypes.POINTER(ObjectData)),
        ('is_binary', ctypes.c_bool),
        ('unit_scale', ctypes.c_double),
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
    
    def export_fbx(self, filepath: str, export_data: ctypes.POINTER) -> str:
        return self.__lib.export_fbx(filepath.encode('utf-8'), export_data)
    
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
    
    def createMeshData(self, vertices: list[float], faces: list[FaceData]) -> MeshData:
        vertices_array_ptr = ctypes.pointer((ctypes.c_double * len(vertices))(*vertices))
        vertices_ptr = ctypes.cast(vertices_array_ptr, ctypes.POINTER(ctypes.c_double))
        faces_array_ptr = ctypes.pointer((FaceData * len(faces))(*faces))
        faces_ptr = ctypes.cast(faces_array_ptr, ctypes.POINTER(FaceData))
        return MeshData(
            vertices=vertices_ptr,
            vertex_count=len(vertices),
            faces=faces_ptr,
            face_count=len(faces)
        )
    
    def createFaceData(self, indices: list[int]) -> FaceData:
        indices_array_ptr = ctypes.pointer((ctypes.c_uint * len(indices))(*indices))
        indices_ptr = ctypes.cast(indices_array_ptr, ctypes.POINTER(ctypes.c_uint))
        return FaceData(
            indices=indices_ptr,
            index_count=len(indices)
        )