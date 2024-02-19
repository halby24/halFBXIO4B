# from curses import meta
import os
import ctypes
from .util import Singleton


class Vector2(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
    ]

    def __repr__(self):
        fields = ",\n".join(
            f"{field}: {getattr(self, field)}" for field, _ in self._fields_
        )
        return f"{self.__class__.__name__}({fields})"


class Vector4(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
        ("z", ctypes.c_double),
        ("w", ctypes.c_double),
    ]

    def __repr__(self):
        fields = ",\n".join(
            f"{field}: {getattr(self, field)}" for field, _ in self._fields_
        )
        return f"{self.__class__.__name__}({fields})"


class StandardSurface(ctypes.Structure):
    _fields_ = [
        ("base", ctypes.c_double),
        ("base_color", Vector4),
        ("emission", ctypes.c_double),
        ("emission_color", Vector4),
        ("specular", ctypes.c_double),
        ("specular_ior", ctypes.c_double),
        ("specular_color", Vector4),
        ("specular_anisotropy", ctypes.c_double),
        ("specular_roughness", ctypes.c_double),
        ("specular_rotation", ctypes.c_double),
        ("transmission", ctypes.c_double),
        ("transmission_depth", ctypes.c_double),
        ("transmission_color", Vector4),
        ("transmission_scatter", Vector4),
        ("transmission_extra_roughness", ctypes.c_double),
        ("transmission_dispersion", ctypes.c_double),
        ("transmission_scatter_anisotropy", ctypes.c_double),
        ("sheen", ctypes.c_double),
        ("sheen_color", Vector4),
        ("sheen_roughness", ctypes.c_double),
        ("coat", ctypes.c_double),
        ("coat_affect_color", Vector4),
        ("coat_normal", Vector4),
        ("coat_roughness", ctypes.c_double),
        ("coat_color", Vector4),
        ("coat_ior", ctypes.c_double),
        ("coat_affect_roughness", ctypes.c_double),
        ("coat_rotation", ctypes.c_double),
        ("coat_anisotropy", ctypes.c_double),
        ("thin_walld", ctypes.c_double),
        ("thin_film_ior", ctypes.c_double),
        ("thin_film_thickness", ctypes.c_double),
        ("subsurface", ctypes.c_double),
        ("subsurface_scale", ctypes.c_double),
        ("subsurface_anisotropy", ctypes.c_double),
        ("subsurface_radius", Vector4),
        ("subsurface_color", Vector4),
        ("metalness", ctypes.c_double),
        ("opacity", ctypes.c_double),
        ("diffuse_roughness", ctypes.c_double),
    ]

    def __repr__(self):
        fields = ",\n".join(
            f"{field}: {getattr(self, field)}" for field, _ in self._fields_
        )
        return f"{self.__class__.__name__}({fields})"


class Material(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("name_length", ctypes.c_size_t),
        ("standard_surface", StandardSurface),
    ]

    def __repr__(self):
        fields = ",\n".join(
            f"{field}: {getattr(self, field)}" for field, _ in self._fields_
        )
        return f"{self.__class__.__name__}({fields})"


class UV(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("name_length", ctypes.c_size_t),
        ("uv", ctypes.POINTER(Vector2)),
    ]

    def __repr__(self):
        fields = ",\n".join(
            f"{field}: {getattr(self, field)}" for field, _ in self._fields_
        )
        return f"{self.__class__.__name__}({fields})"


class Normal(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("name_length", ctypes.c_size_t),
        ("normal", ctypes.POINTER(Vector4)),
    ]

    def __repr__(self):
        fields = ",\n".join(
            f"{field}: {getattr(self, field)}" for field, _ in self._fields_
        )
        return f"{self.__class__.__name__}({fields})"


class Mesh(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("name_length", ctypes.c_size_t),
        ("vertices", ctypes.POINTER(Vector4)),
        ("vertex_count", ctypes.c_size_t),
        ("indices", ctypes.POINTER(ctypes.c_uint)),
        ("index_count", ctypes.c_size_t),
        ("polys", ctypes.POINTER(ctypes.c_uint)),
        ("material_indices", ctypes.POINTER(ctypes.c_uint)),
        ("poly_count", ctypes.c_size_t),
        ("uv_sets", ctypes.POINTER(UV)),
        ("uv_set_count", ctypes.c_size_t),
        ("normal_sets", ctypes.POINTER(Normal)),
        ("normal_set_count", ctypes.c_size_t),
    ]

    def __repr__(self):
        fields = ",\n".join(
            f"{field}: {getattr(self, field)}" for field, _ in self._fields_
        )
        return f"{self.__class__.__name__}({fields})"


class Object(ctypes.Structure):
    def __repr__(self):
        fields = ",\n".join(
            f"{field}: {getattr(self, field)}" for field, _ in self._fields_
        )
        return f"{self.__class__.__name__}({fields})"


Object._fields_ = [
    ("name", ctypes.c_char_p),
    ("name_length", ctypes.c_size_t),
    ("local_matrix", ctypes.c_double * 16),
    ("children", ctypes.POINTER(Object)),
    ("child_count", ctypes.c_size_t),
    ("mesh", ctypes.POINTER(Mesh)),
    ("material_slots", ctypes.POINTER(ctypes.POINTER(Material))),
    ("material_slot_count", ctypes.c_size_t),
]


class ExportData(ctypes.Structure):
    _fields_ = [
        ("is_binary", ctypes.c_bool),
        ("unit_scale", ctypes.c_double),
        ("root", ctypes.POINTER(Object)),
        ("materials", ctypes.POINTER(Material)),
        ("material_count", ctypes.c_size_t),
    ]

    def __repr__(self):
        fields = ",\n".join(
            f"{field}: {getattr(self, field)}" for field, _ in self._fields_
        )
        return f"{self.__class__.__name__}({fields})"


class CLib(Singleton):
    def __init__(self) -> None:
        self.__lib = ctypes.CDLL(
            os.path.dirname(os.path.abspath(__file__)) + "/lib/halFBXIO4B.dll"
        )
        self.__init_functions()

    def __init_functions(self):
        self.__lib.export_fbx.argtypes = [ctypes.c_char_p, ctypes.POINTER(ExportData)]
        self.__lib.export_fbx.restype = ctypes.c_bool
        self.__lib.vertex_normal_from_poly_normal.argtypes = [
            ctypes.POINTER(ctypes.c_uint),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint),
            ctypes.c_size_t,
            ctypes.POINTER(Vector4),
            ctypes.POINTER(Vector4),
        ]
        self.__lib.vertex_normal_from_poly_normal.restype = None

    def export_fbx(self, filepath: str, export_data: ExportData) -> str:
        export_data_ptr = ctypes.pointer(export_data)
        return self.__lib.export_fbx(filepath.encode("utf-8"), export_data_ptr)

    def vertex_normal_from_poly_normal(
        self, indices: list[int], polys: list[int], normals: list[Vector4]
    ) -> list[Vector4]:
        out_vertex_normals_array = (Vector4 * len(indices))()
        self.__lib.vertex_normal_from_poly_normal(
            (ctypes.c_uint * len(indices))(*indices),
            len(indices),
            (ctypes.c_uint * len(polys))(*polys),
            len(polys),
            (Vector4 * len(normals))(*normals),
            out_vertex_normals_array,
        )
        return list(out_vertex_normals_array)

    def createObject(
        self,
        name: str,
        local_matrix: list[float],
        children: list[Object],
        mesh: Mesh | None,
        material_slots: list[ctypes.POINTER],
    ) -> Object:
        return Object(
            name=name.encode("utf-8"),
            name_length=len(name),
            local_matrix=(ctypes.c_double * 16)(*local_matrix),
            children=(Object * len(children))(*children),
            child_count=len(children),
            mesh=ctypes.pointer(mesh) if mesh else ctypes.POINTER(Mesh)(),
            material_slots=(ctypes.POINTER(Material) * len(material_slots))(
                *material_slots
            ),
            material_slot_count=len(material_slots),
        )

    def createExportData(
        self,
        root: Object,
        is_binary: bool,
        unit_scale: float,
        materials: ctypes.Array[Material], # Arrayじゃないとアドレスが変わる
    ) -> ExportData:
        return ExportData(
            root=ctypes.pointer(root),
            is_binary=is_binary,
            unit_scale=unit_scale,
            materials=materials,
            material_count=len(materials),
        )

    def createMesh(
        self,
        name: str,
        vertices: list[Vector4],
        normals: list[Normal],
        uvs: list[UV],
        indices: list[int],
        polys: list[int],
        mat_indices: list[int],
    ) -> Mesh:
        return Mesh(
            name=name.encode("utf-8"),
            name_length=len(name),
            vertices=(Vector4 * len(vertices))(*vertices),
            vertex_count=len(vertices),
            indices=(ctypes.c_uint * len(indices))(*indices),
            index_count=len(indices),
            polys=(ctypes.c_uint * len(polys))(*polys),
            material_indices=(ctypes.c_uint * len(mat_indices))(*mat_indices),
            poly_count=len(polys),
            uv_sets=(UV * len(uvs))(*uvs),
            uv_set_count=len(uvs),
            normal_sets=(Normal * len(normals))(*normals),
            normal_set_count=len(normals),
        )

    def createMaterial(
        self,
        name: str,
        basecolor: Vector4,
        metallic: float,
        roughness: float,
        emissive: Vector4,
    ) -> Material:
        print('py opacity: ', basecolor.w)
        surf = StandardSurface(
            base=1,
            base_color=basecolor,
            emission=1,
            emission_color=emissive,
            specular=1,
            specular_color=basecolor,
            specular_roughness=roughness,
            metalness=metallic,
            opacity=basecolor.w,
        )
        return Material(
            name=name.encode("utf-8"),
            name_length=len(name),
            standard_surface=surf,
        )

    def createUV(self, name: str, uv: list[Vector2]) -> UV:
        return UV(
            name=name.encode("utf-8"),
            name_length=len(name),
            uv=(Vector2 * len(uv))(*uv),
        )

    def createNormal(self, name: str, normal: list[Vector4]) -> Normal:
        return Normal(
            name=name.encode("utf-8"),
            name_length=len(name),
            normal=(Vector4 * len(normal))(*normal),
        )
