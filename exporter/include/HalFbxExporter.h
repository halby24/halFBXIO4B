#pragma once

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
    };

    bool export_fbx(char* export_path, ExportData* export_data);
    ObjectData* create_object_data(char* name, size_t name_length, double* matrix_local, ObjectData* children, size_t child_count, double* vertices, size_t vertex_count);
    ExportData* create_export_data(ObjectData* root, bool is_ascii);
    void destroy_export_data(ExportData* export_data);
}