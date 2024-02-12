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

    struct MeshData
    {
        char* name;
        size_t name_length;
        Vector4* vertices;
        Vector4* normals;
        Vector2* uvs;
        size_t vertex_count;
        unsigned int* indices;
        size_t index_count;
        unsigned int* polys; // ポリゴン開始インデックスの配列
        size_t poly_count;
    };

    struct ObjectData
    {
        char* name;
        size_t name_length;
        double matrix_local[16];
        ObjectData* children;
        size_t child_count;
        MeshData* mesh; // nullptr if not a mesh
    };

    struct ExportData
    {
        bool is_ascii;
        double unit_scale; // 1.0 for meters, 0.01 for centimeters, 0.0254 for inches
        ObjectData* root;
    };

    DLLEXPORT(bool) export_fbx(char* export_path, ExportData* export_data);
    DLLEXPORT(void) vertex_normal_from_poly_normal(unsigned int* indices, size_t index_count, unsigned int* polys, size_t poly_count, Vector4* poly_normals, Vector4* out_vertex_normals);
}