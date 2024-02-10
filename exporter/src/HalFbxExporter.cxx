// Copyright 2023 HALBY
// This program is distributed under the terms of the MIT License. See the file LICENSE for details.

#include "./HalFbxExporter.h"
#include <fbxsdk.h>
#include <iostream>

#define TRUE 1
#define FALSE 0

FbxNode* create_node_recursive(FbxScene* scene, ObjectData* object_data);

int export_fbx(char* export_path, ExportData* export_data)
{
    auto manager = FbxManager::Create();
    auto scene = FbxScene::Create(manager, "Scene");

    // The example can take a FBX file as an argument.
    FbxString path_fbxstr(export_path);

    if (path_fbxstr.IsEmpty())
    {
        FBXSDK_printf("\n\nFile path is invalid.\n\n");
        manager->Destroy();
        return FALSE;
    }

    FBXSDK_printf("\n\nSave path: %s\n\n", path_fbxstr.Buffer());

    char* path_char = NULL;
    FbxAnsiToUTF8(path_fbxstr.Buffer(), path_char, NULL);
    path_fbxstr = path_char;

    // Add objects to the scene.
    auto root = export_data->root;
    auto root_node = create_node_recursive(scene, root);
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
        FBXSDK_printf("\n\nAn error occurred while initializing the exporter...\n");
        manager->Destroy();
        return FALSE;
    }

    return TRUE;
}

FbxNode* create_node_recursive(FbxScene* scene, ObjectData* object_data)
{
    auto node = FbxNode::Create(scene, object_data->name);
    
    FbxAMatrix transform;
    for (int i = 0; i < 16; i++) { transform[i / 4][i % 4] = object_data->matrix_local[i]; }
    node->LclTranslation.Set(FbxVector4(transform.GetT()));
    node->LclRotation.Set(FbxVector4(transform.GetR()));
    node->LclScaling.Set(FbxVector4(transform.GetS()));

    if (object_data->vertex_count > 0)
    {
        auto mesh = FbxMesh::Create(scene, object_data->name);
        mesh->InitControlPoints(object_data->vertex_count);
        auto control_points = mesh->GetControlPoints();
        memccpy(control_points, object_data->vertices, object_data->vertex_count, sizeof(double));
        node->SetNodeAttribute(mesh);
    }

    for (int i = 0; i < object_data->child_count; i++)
    {
        auto child = create_node_recursive(scene, &object_data->children[i]);
        node->AddChild(child);
    }

    return node;
}