// Copyright 2023 HALBY
// This program is distributed under the terms of the MIT License. See the file LICENSE for details.

#include <fbxsdk.h>
#include <iostream>
#include "../include/HalFbxExporter.h"

FbxNode* create_node_recursive(FbxScene* scene, ObjectData* object_data);

bool export_fbx(char* export_path, ExportData* export_data)
{
    auto manager = FbxManager::Create();
    auto scene = FbxScene::Create(manager, "Scene");

    // The example can take a FBX file as an argument.
    FbxString path_fbxstr(export_path);

    if (path_fbxstr.IsEmpty())
    {
        FBXSDK_printf("File path is invalid.\n");
        manager->Destroy();
        return false;
    }

    FBXSDK_printf("Save path: %s\n", path_fbxstr.Buffer());

    char* path_char = NULL;
    FbxAnsiToUTF8(path_fbxstr.Buffer(), path_char, NULL);
    path_fbxstr = path_char;

    // Add objects to the scene.
    auto& root = export_data->root;
    auto root_node = create_node_recursive(scene, root);
    if (root_node == nullptr) {
        FBXSDK_printf("Root node is null.\n");
        manager->Destroy();
        return false;
    }
    for (int i = 0; i < root->child_count; i++) { scene->GetRootNode()->AddChild(root_node->GetChild(i)); }

    // バイナリまたはASCII形式の選択
    int format;
    if (export_data->is_ascii)
        format = manager->GetIOPluginRegistry()->FindWriterIDByDescription("FBX ascii (*.fbx)");
    else
        format = manager->GetIOPluginRegistry()->FindWriterIDByDescription("FBX binary (*.fbx)");

    auto exporter = FbxExporter::Create(manager, "");
    if (!exporter->Initialize(path_fbxstr, format))
    {
        FBXSDK_printf("An error occurred while initializing the exporter...\n");
        manager->Destroy();
        return false;
    }

    return true;
}

FbxNode* create_node_recursive(FbxScene* scene, ObjectData* object_data)
{
    if (object_data == nullptr) {
        FBXSDK_printf("ObjectData is null.\n");
        return nullptr;
    }

    auto node = FbxNode::Create(scene, object_data->name);

    FbxAMatrix transform;
    for (int i = 0; i < 16; i++) { transform[i / 4][i % 4] = object_data->matrix_local[i]; }
    node->LclTranslation.Set(FbxVector4(transform.GetT()));
    node->LclRotation.Set(FbxVector4(transform.GetR()));
    node->LclScaling.Set(FbxVector4(transform.GetS()));

    for (int i = 0; i < object_data->child_count; i++)
    {
        auto child_node = create_node_recursive(scene, &object_data->children[i]);
        node->AddChild(child_node);
    }

    return node;
}

ObjectData* create_object_data(char* name, size_t name_length, double* matrix_local, ObjectData* children, size_t child_count, double* vertices, size_t vertex_count)
{
    auto object_data = new ObjectData();
    object_data->name = name;
    object_data->name_length = name_length;
    for (int i = 0; i < 16; i++) { object_data->matrix_local[i] = matrix_local[i]; }
    object_data->children = children;
    object_data->child_count = child_count;
    object_data->vertices = vertices;
    object_data->vertex_count = vertex_count;
    return object_data;
}

ExportData* create_export_data(ObjectData* root, bool is_ascii)
{
    auto export_data = new ExportData();
    export_data->root = root;
    export_data->is_ascii = is_ascii;
    return export_data;
}

void destroy_object_data(ObjectData* object_data)
{
    if (object_data == nullptr) return; 
    for (int i = 0; i < object_data->child_count; i++) destroy_object_data(&object_data->children[i]);
    delete object_data;
}

void destroy_export_data(ExportData* export_data)
{
    if (export_data == nullptr) return;
    destroy_object_data(export_data->root);
    delete export_data;
}