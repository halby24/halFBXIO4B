#pragma once

#define DLLEXPORT(type) __declspec(dllexport) type __stdcall

extern "C"
{
    struct Vector2
    {
        double x, y;
    };

    struct Vector4
    {
        double x, y, z, w;
    };

    struct StandardSurface
    {
        double base;
        Vector4 base_color;
        double emission;
        Vector4 emission_color;
        double specular;
        double specular_ior;
        Vector4 specular_color;
        double specular_anisotropy;
        double specular_roughness;
        double specular_rotation;
        double transmission;
        double transmission_depth;
        Vector4 transmission_color;
        Vector4 transmission_scatter;
        double transmission_extra_roughness;
        double transmission_dispersion;
        double transmission_scatter_anisotropy;
        double sheen;
        Vector4 sheen_color;
        double sheen_roughness;
        double coat;
        Vector4 coat_affect_color;
        Vector4 coat_normal;
        double coat_roughness;
        Vector4 coat_color;
        double coat_ior;
        double coat_affect_roughness;
        double coat_rotation;
        double coat_anisotropy;
        double thin_walld;
        double thin_film_ior;
        double thin_film_thickness;
        double subsurface;
        double subsurface_scale;
        double subsurface_anisotropy;
        Vector4 subsurface_radius;
        Vector4 subsurface_color;
        double metalness;
        double opacity;
        double diffuse_roughness;
    };

    struct Material
    {
        char* name;
        size_t name_length;
        StandardSurface standard_surface;
    };

    struct UV
    {
        char* name;
        size_t name_length;
        Vector2* uv;
    };

    struct Normal
    {
        char* name;
        size_t name_length;
        Vector4* normal;
    };

    struct Mesh
    {
        char* name;
        size_t name_length;
        Vector4* vertices;
        size_t vertex_count;
        unsigned int* indices;
        size_t index_count;
        unsigned int* polys; // ポリゴン開始インデックスの配列
        unsigned int* material_indices; // ポリゴンごとのマテリアルインデックス
        size_t poly_count;
        UV* uv_sets;
        size_t uv_set_count;
        Normal* normal_sets;
        size_t normal_set_count;
    };

    struct Object
    {
        char* name;
        size_t name_length;
        double matrix_local[16];
        Object* children;
        size_t child_count;
        Mesh* mesh; // nullptr if not a mesh
        Material** material_slots;
        size_t material_slot_count;
    };

    struct ExportData
    {
        bool is_ascii;
        double unit_scale; // 1.0 for meters, 0.01 for centimeters, 0.0254 for
                           // inches
        Object* root;
        Material* materials;
        size_t material_count;
    };

    DLLEXPORT(bool)
    export_fbx(const char* export_path, const ExportData* export_data);
    DLLEXPORT(void)
    vertex_normal_from_poly_normal(const unsigned int* indices,
                                   size_t index_count,
                                   const unsigned int* polys, size_t poly_count,
                                   const Vector4* poly_normals,
                                   Vector4* out_vertex_normals);
    DLLEXPORT(void) fix_normal_rot(Vector4* normals, size_t normal_count);
}
