// Copyright 2023 HALBY
// This program is distributed under the terms of the MIT License. See the file LICENSE for details.
#pragma once

struct ObjectData
{
    char* name;
    size_t name_length;
    double matrix_local[16];
    int child_count;
    ObjectData* children;
    int vertex_count;
    double* vertices;
};

struct ExportData
{
    ObjectData* root;
    bool is_ascii;
};

int export_fbx(char* export_path, ExportData* export_data);