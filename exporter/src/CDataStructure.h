// Copyright 2023 HALBY
// This program is distributed under the terms of the MIT License. See the file LICENSE for details.

#ifndef C_DATA_STRUCTURE_H
#define C_DATA_STRUCTURE_H

#pragma pack(push, 1)

typedef struct
{
    char* name;
    size_t name_length;
    float local_matrix[16];
    ObjectData* parent;
} ObjectData;

typedef struct
{
    ObjectData* objects;
    size_t object_count;
} ExportData;

#endif