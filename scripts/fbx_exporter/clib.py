import os
import ctypes
from .util import Singleton

class ObjectData(ctypes.Structure):
    pass
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

class CLib(Singleton):
    def __init__(self) -> None:
        self.__lib = ctypes.CDLL(os.path.dirname(os.path.abspath(__file__)) + '/lib/HalFbxExporter.dll')
        self.__init_functions()
    
    def __init_functions(self):
        self.__lib.create_object_data.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ObjectData), ctypes.c_size_t, ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
        self.__lib.create_object_data.restype = ctypes.POINTER(ObjectData)
        self.__lib.create_export_data.argtypes = [ctypes.POINTER(ObjectData), ctypes.c_bool]
        self.__lib.create_export_data.restype = ctypes.POINTER(ExportData)
        self.__lib.destroy_export_data.argtypes = [ctypes.POINTER(ExportData)]
        self.__lib.destroy_export_data.restype = None
        self.__lib.export_fbx.argtypes = [ctypes.c_char_p, ctypes.POINTER(ExportData)]
        self.__lib.export_fbx.restype = ctypes.c_char_p
    
    def export_fbx(self, filepath: str, export_data: ctypes.POINTER) -> str:
        return self.__lib.export_fbx(filepath.encode('utf-8'), export_data)
    
    def createObjectData(self, name: str, local_matrix: list[float], children: list[ObjectData], vertices: list[float]) -> ObjectData:
        children_ptr = ctypes.cast(ctypes.pointer((ObjectData * len(children))(*children)), ctypes.POINTER(ObjectData))
        vertices_ptr = ctypes.cast(ctypes.pointer((ctypes.c_double * len(vertices))(*vertices)), ctypes.POINTER(ctypes.c_double))
        print('children_ptr: ', children_ptr)
        print('vertices_ptr: ', vertices_ptr)
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
    
    def destroy_export_data(self, export_data: ctypes.POINTER) -> None:
        self.__lib.destroy_export_data(export_data)