// Copyright 2023 HALBY
// This program is distributed under the terms of the MIT License. See the file LICENSE for details.

#include "../include/HalFbxExporter.h"
#include <cstring>
#include <fbxsdk.h>
#include <iostream>
#define _USE_MATH_DEFINES
#include <math.h>

FbxNode* create_node_recursive(FbxScene* scene, ExportData* export_data, ObjectData* object_data);
void fix_coord(double unit_scale, FbxVector4* vertices, size_t vertex_count);

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
    auto root = export_data->root;
    auto root_node = create_node_recursive(scene, export_data, root);
    if (root_node == nullptr)
    {
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

    exporter->Export(scene);
    manager->Destroy();

    return true;
}

FbxNode* create_node_recursive(FbxScene* scene, ExportData* export_data, ObjectData* object_data)
{
    if (object_data == nullptr)
    {
        FBXSDK_printf("ObjectData is null.\n");
        return nullptr;
    }

    auto node = FbxNode::Create(scene, object_data->name);

    FbxAMatrix transform;
    std::memcpy(transform, object_data->matrix_local, 16 * sizeof(double));
    node->LclTranslation.Set(FbxVector4(transform.GetT()));
    node->LclRotation.Set(FbxVector4(transform.GetR()));
    node->LclScaling.Set(FbxVector4(transform.GetS()));

    if (object_data->vertex_count > 0)
    {
        auto mesh = FbxMesh::Create(scene, object_data->name);
        node->SetNodeAttribute(mesh);

        mesh->InitControlPoints(object_data->vertex_count);
        auto control_points = mesh->GetControlPoints();

        fix_coord(export_data->unit_scale, (FbxVector4*)object_data->vertices, object_data->vertex_count / 4);
        std::memcpy(control_points, object_data->vertices, object_data->vertex_count * sizeof(double));
    }

    for (int i = 0; i < object_data->child_count; i++)
    {
        auto child_node = create_node_recursive(scene, export_data, &object_data->children[i]);
        node->AddChild(child_node);
    }

    return node;
}

void fix_coord(double unit_scale, FbxVector4* vertices, size_t vertex_count)
{
    auto cm_scale = unit_scale * 100.0;

    FbxAMatrix m;
    m.SetIdentity();
    auto rad = cos(M_PI / 4.0);
    m.SetQ(FbxQuaternion(rad, 0, 0, rad)); // Z-up to Y-up
    m.SetS(FbxVector4(cm_scale, cm_scale, cm_scale));
    for (size_t i = 0; i < vertex_count; i++)
    {
        vertices[i] = m.MultT(vertices[i]);
    }
}