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

    struct Material
    {
        char* name;
        size_t name_length;
        Vector4 diffuse;
        Vector4 specular;
        Vector4 emissive;
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
        Material* material_slots;
        size_t material_slot_count;
    };

    struct ExportData
    {
        bool is_ascii;
        double unit_scale; // 1.0 for meters, 0.01 for centimeters, 0.0254 for inches
        Object* root;
        Material* materials;
        size_t material_count;
    };

    DLLEXPORT(bool) export_fbx(char* export_path, ExportData* export_data);
    DLLEXPORT(void) vertex_normal_from_poly_normal(unsigned int* indices, size_t index_count, unsigned int* polys, size_t poly_count, Vector4* poly_normals, Vector4* out_vertex_normals);
}