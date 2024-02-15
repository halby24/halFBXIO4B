// Copyright 2023 HALBY
// This program is distributed under the terms of the MIT License. See the file LICENSE for details.

#include "../include/HalFbxExporter.h"
#include <cstring>
#include <fbxsdk.h>
#include <iostream>
#define _USE_MATH_DEFINES
#include <math.h>
#include <vector>

FbxNode* create_node_recursive(FbxScene* scene, ExportData* export_data, Object* object_data);
void fix_coord(double unit_scale, Vector4* vertices, size_t vertex_count);
FbxAMatrix fix_rot_m(FbxAMatrix& input);
FbxAMatrix fix_scale_m(FbxAMatrix& input, double unit_scale);

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
    for (auto i = 0; i < root->child_count; i++) { scene->GetRootNode()->AddChild(root_node->GetChild(i)); }

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

FbxNode* create_node_recursive(FbxScene* scene, ExportData* export_data, Object* object_data)
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

    if (object_data->mesh != nullptr)
    {
        auto mesh_data = object_data->mesh;
        auto mesh = FbxMesh::Create(scene, object_data->name);
        node->SetNodeAttribute(mesh);

        mesh->InitControlPoints(mesh_data->vertex_count);
        auto control_points = mesh->GetControlPoints();

        // メッシュの頂点座標を設定、Z-up to Y-up
        fix_coord(export_data->unit_scale, mesh_data->vertices, mesh_data->vertex_count);
        std::memcpy(control_points, mesh_data->vertices, mesh_data->vertex_count * sizeof(Vector4));

        for (auto i = 0; i < mesh_data->poly_count; i++)
        {
            auto curr_index = mesh_data->polys[i];
            auto next_index = (i == mesh_data->poly_count - 1) ? mesh_data->index_count : mesh_data->polys[i + 1];

            mesh->BeginPolygon();
            for (int j = curr_index; j < next_index; j++) mesh->AddPolygon(mesh_data->indices[j]);
            mesh->EndPolygon();
        }

        auto elnrm = mesh->CreateElementNormal();
        elnrm->SetMappingMode(FbxGeometryElement::eByPolygonVertex);
        elnrm->SetReferenceMode(FbxGeometryElement::eDirect);
        for (auto i = 0; i < mesh_data->poly_count; i++)
        {
            auto curr_index = mesh_data->polys[i];
            auto next_index = (i == mesh_data->poly_count - 1) ? mesh_data->index_count : mesh_data->polys[i + 1];

            for (int j = curr_index; j < next_index; j++) elnrm->GetDirectArray().Add(*(FbxVector4*)&mesh_data->normals[j]);
        }
    }

    for (auto i = 0; i < object_data->child_count; i++)
    {
        auto child_node = create_node_recursive(scene, export_data, &object_data->children[i]);
        node->AddChild(child_node);
    }

    return node;
}

void vertex_normal_from_poly_normal(unsigned int* indices, size_t index_count, unsigned int* polys, size_t poly_count, Vector4* poly_normals, Vector4* out_vertex_normals)
{
    std::vector<Vector4> vertex_normals;
    vertex_normals.resize(index_count);
    for (auto i = 0; i < poly_count; i++)
    {
        auto curr_index = polys[i];
        auto next_index = (i == poly_count - 1) ? index_count : polys[i + 1];
        auto normal = poly_normals[i];
        FbxAMatrix m;
        m.SetIdentity();
        m = fix_rot_m(m);
        normal = *(Vector4*)&m.MultT(*(FbxVector4*)&normal);
        for (auto j = curr_index; j < next_index; j++) { vertex_normals[j] = normal; }
    }
    for (auto i = 0; i < index_count; i++) { out_vertex_normals[i] = vertex_normals[i]; }
}

void fix_coord(double unit_scale, Vector4* vertices, size_t vertex_count)
{
    auto cm_scale = unit_scale * 100.0;
    auto vecs = (FbxVector4*)vertices;

    FbxAMatrix m;
    m.SetIdentity();
    m = fix_rot_m(m);
    m = fix_scale_m(m, unit_scale);
    for (size_t i = 0; i < vertex_count; i++) { vecs[i] = m.MultT(vecs[i]); }
}

FbxAMatrix fix_rot_m(FbxAMatrix& input)
{
    FbxAMatrix m(input);
    auto rad = cos(M_PI / 4.0);
    m.SetQ(FbxQuaternion(rad, 0, 0, rad)); // Z-up to Y-up
    return m;
}

FbxAMatrix fix_scale_m(FbxAMatrix& input, double unit_scale)
{
    FbxAMatrix m(input);
    auto cm_scale = unit_scale * 100.0;
    m.SetS(FbxVector4(cm_scale, cm_scale, cm_scale));
    return m;
}