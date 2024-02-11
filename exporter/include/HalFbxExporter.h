#pragma once

#define DLLEXPORT __declspec(dllexport)

extern "C"
{
    struct ObjectData
    {
        char* name;
        size_t name_length;
        double matrix_local[16];
        ObjectData* children;
        size_t child_count;
        double* vertices;
        size_t vertex_count;
    };

    struct ExportData
    {
        ObjectData* root;
        bool is_ascii;
        double unit_scale; // 1.0 for meters, 0.01 for centimeters, 0.0254 for inches
    };

    DLLEXPORT bool export_fbx(char* export_path, ExportData* export_data);
}