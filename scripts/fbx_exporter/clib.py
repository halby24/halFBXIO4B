import os
import ctypes
from .util import Singleton

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
    ('vertices', ctypes.POINTER(ctypes.c_double)),
    ('vertex_count', ctypes.c_size_t)
]

class ExportData(ctypes.Structure):
    _fields_ = [
        ('root', ctypes.POINTER(ObjectData)),
        ('is_binary', ctypes.c_bool)
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
    
    def createObjectData(self, name: str, local_matrix: list[float], children: list[ObjectData], vertices: list[float]) -> ObjectData:
        children_ptr = ctypes.cast(ctypes.pointer((ObjectData * len(children))(*children)), ctypes.POINTER(ObjectData))
        vertices_ptr = ctypes.cast(ctypes.pointer((ctypes.c_double * len(vertices))(*vertices)), ctypes.POINTER(ctypes.c_double))
        return ObjectData(
            name=name.encode('utf-8'),
            name_length=len(name),
            local_matrix=(ctypes.c_double * 16)(*local_matrix),
            children=children_ptr,
            child_count=len(children),
            vertices=vertices_ptr,
            vertex_count=len(vertices)
        )
    
    def createExportData(self, root: ObjectData, is_binary: bool) -> ctypes.POINTER:
        root_ptr = ctypes.pointer(root)
        return ExportData(
            root=root_ptr,
            is_binary=is_binary
        )