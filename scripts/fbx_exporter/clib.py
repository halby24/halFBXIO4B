import os
import ctypes
from .util import Singleton

class ObjectData(ctypes.Structure):
    _fields_ = [
        ('name', ctypes.c_char_p),
        ('name_length', ctypes.c_size_t),
        ('local_matrix', ctypes.POINTER(ctypes.c_double)),
        ('children', ctypes.POINTER(ctypes.POINTER('ObjectData'))),
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
        self.__lib.create_object_data.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ObjectData), ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
        self.__lib.create_object_data.restype = ctypes.POINTER(ObjectData)
        self.__lib.create_export_data.argtypes = [ctypes.POINTER(ObjectData), ctypes.c_bool]
        self.__lib.create_export_data.restype = ctypes.POINTER(ExportData)
        self.__lib.destroy_export_data.argtypes = [ctypes.POINTER(ExportData)]
        self.__lib.destroy_export_data.restype = None
        self.__lib.export_fbx.argtypes = [ctypes.c_char_p, ctypes.POINTER(ExportData)]
        self.__lib.export_fbx.restype = ctypes.c_char_p
    
    def export_fbx(self, filepath: str, export_data: ctypes.POINTER) -> str:
        return self.__lib.export_fbx(filepath.encode('utf-8'), export_data)
    
    def create_object_data(self, name: str, local_matrix: list[float], children: list[ObjectData], vertices: list[float]) -> ctypes.POINTER:
        name = name.encode('utf-8')
        local_matrix = (ctypes.c_double * 16)(*local_matrix)
        children = (ObjectData * len(children))(*children)
        vertices = (ctypes.c_double * len(vertices))(*vertices)
        return self.__lib.create_object_data(name, local_matrix, children, vertices, len(vertices))
    
    def create_export_data(self, root: ctypes.POINTER, is_binary: bool) -> ctypes.POINTER:
        return self.__lib.create_export_data(root, is_binary)
    
    def destroy_export_data(self, export_data: ctypes.POINTER) -> None:
        self.__lib.destroy_export_data(export_data)