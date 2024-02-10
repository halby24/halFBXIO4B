// Copyright 2023 HALBY
// This program is distributed under the terms of the MIT License. See the file LICENSE for details.
#pragma once
#define DLLEXPORT extern "C" __declspec(dllexport)

DLLEXPORT struct ExportData {
    int object_count;
    struct Object {
        char* name;
        double matrix_local[16];
    } objects[100];
    bool is_ascii;
};

DLLEXPORT int ExportFbx(char* pFilePath, ExportData* pExportData);