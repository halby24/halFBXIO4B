// Copyright 2023 HALBY
// This program is distributed under the terms of the MIT License. See the file
// LICENSE for details.

#include "../include/HalFbxExporter.h"

#include <fbxsdk.h>

#include <cstring>
#include <iostream>
#define _USE_MATH_DEFINES
#include <math.h>

#include <vector>

FbxNode* create_node_recursive(FbxScene* scene, const ExportData* export_data,
                               Object* object_data);
FbxMesh* create_mesh(const Mesh* mesh_data, const char* name, FbxScene* scene,
                     double unit_scale);
FbxSurfaceMaterial* create_material(FbxScene* scene, const Material* input);
template <typename T>
void define_property(FbxSurfaceMaterial* mat, const char* name,
                     const char* shader_name, FbxDataType data_type, T value);
void set_normal(const Normal* input, size_t input_count,
                FbxGeometryElementNormal* target);
void set_uv(const UV* input, size_t input_count, FbxGeometryElementUV* target);
void fix_coord(double unit_scale, Vector4* vertices, size_t vertex_count);
FbxAMatrix fix_rot_m(const FbxAMatrix& input);
FbxAMatrix fix_scale_m(const FbxAMatrix& input, double unit_scale);

bool export_fbx(const char* export_path, const ExportData* export_data)
{
    auto manager = FbxManager::Create();
    auto scene = FbxScene::Create(manager, "Scene");

    // The example can take a FBX file as an argument.
    FbxString path_fbxstr(export_path);

    if (path_fbxstr.IsEmpty())
    {
        std::cerr << "File path is invalid." << std::endl;
        manager->Destroy();
        return false;
    }

    std::cerr << "Save path: " << path_fbxstr.Buffer() << std::endl;

    char* path_char = NULL;
    FbxAnsiToUTF8(path_fbxstr.Buffer(), path_char, NULL);
    path_fbxstr = path_char;

    // ノードツリーの作成
    auto root = export_data->root;
    auto root_node = create_node_recursive(scene, export_data, root);
    if (root_node == nullptr)
    {
        std::cerr << "Root node is null." << std::endl;
        manager->Destroy();
        return false;
    }
    for (auto i = 0; i < root->child_count; i++)
    {
        scene->GetRootNode()->AddChild(root_node->GetChild(i));
    }

    // マテリアルの設定
    for (auto i = 0; i < export_data->material_count; i++)
    {
        auto emat = export_data->materials[i];
        auto fmat = create_material(scene, emat);
        scene->AddMaterial(fmat);
    }

    // バイナリまたはASCII形式の選択
    int format;
    if (export_data->is_ascii)
        format = manager->GetIOPluginRegistry()->FindWriterIDByDescription(
            "FBX ascii (*.fbx)");
    else
        format = manager->GetIOPluginRegistry()->FindWriterIDByDescription(
            "FBX binary (*.fbx)");

    auto exporter = FbxExporter::Create(manager, "");
    if (!exporter->Initialize(path_fbxstr, format))
    {
        std::cerr << "An error occurred while initializing the exporter..."
                  << std::endl;
        manager->Destroy();
        return false;
    }

    exporter->Export(scene);
    manager->Destroy();

    return true;
}

FbxNode* create_node_recursive(FbxScene* scene, const ExportData* export_data,
                               Object* object_data)
{
    if (object_data == nullptr)
    {
        std::cerr << "ObjectData is null." << std::endl;
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
        auto mesh = create_mesh(object_data->mesh, object_data->name, scene,
                                export_data->unit_scale);
        if (mesh == nullptr)
        {
            std::cerr << "Mesh is null." << std::endl;
            return nullptr;
        }
        node->SetNodeAttribute(mesh);
    }

    for (auto i = 0; i < object_data->child_count; i++)
    {
        auto child_node = create_node_recursive(scene, export_data,
                                                &object_data->children[i]);
        node->AddChild(child_node);
    }

    return node;
}

FbxMesh* create_mesh(const Mesh* mesh_data, const char* name, FbxScene* scene,
                     double unit_scale)
{
    auto mesh = FbxMesh::Create(scene, name);

    mesh->InitControlPoints(mesh_data->vertex_count);
    auto control_points = mesh->GetControlPoints();

    // メッシュの頂点座標を設定、Z-up to Y-up
    fix_coord(unit_scale, mesh_data->vertices, mesh_data->vertex_count);
    std::memcpy(control_points, mesh_data->vertices,
                mesh_data->vertex_count * sizeof(Vector4));

    for (auto i = 0; i < mesh_data->poly_count; i++)
    {
        auto curr_index = mesh_data->polys[i];
        auto next_index = (i == mesh_data->poly_count - 1)
                              ? mesh_data->index_count
                              : mesh_data->polys[i + 1];

        mesh->BeginPolygon();
        for (int j = curr_index; j < next_index; j++)
            mesh->AddPolygon(mesh_data->indices[j]);
        mesh->EndPolygon();
    }

    for (auto i = 0; i < mesh_data->normal_set_count; i++)
    {
        auto elnrm = mesh->CreateElementNormal();
        set_normal(&mesh_data->normal_sets[i], mesh_data->index_count, elnrm);
    }

    for (auto i = 0; i < mesh_data->uv_set_count; i++)
    {
        auto eluv = mesh->CreateElementUV(mesh_data->uv_sets[i].name);
        set_uv(&mesh_data->uv_sets[i], mesh_data->index_count, eluv);
    }

    return mesh;
}

FbxSurfaceMaterial* create_material(FbxScene* scene, const Material* input)
{
    auto mat = FbxSurfaceMaterialUtils::CreateShaderMaterial(
        scene, input->name, FBXSDK_SHADING_LANGUAGE_SSSL, "1.0.1",
        FBXSDK_RENDERING_API_SSSL, "");

    FbxProperty prop;
    define_property(mat, "Base", "base", FbxFloatDT, 1);
    define_property(mat, "BaseColor", "base_color", FbxDouble3DT,
                    FbxDouble3(1.0, 1.0, 1.0));
    define_property(mat, "Emission", "emission", FbxFloatDT, 0.0);
    define_property(mat, "EmissionColor", "emission_color", FbxDouble3DT,
                    FbxDouble3(1.0, 1.0, 1.0));
    define_property(mat, "Specular", "specular", FbxFloatDT, 0.2);
    define_property(mat, "SpecularIOR", "specular_IOR", FbxFloatDT, 1.5);
    define_property(mat, "SpecularColor", "specular_color", FbxDouble3DT,
                    FbxDouble3(1.0, 1.0, 1.0));
    define_property(mat, "SpecularAnisotropy", "specular_anisotropy",
                    FbxFloatDT, 0.0);
    define_property(mat, "SpecularRoughness", "specular_roughness", FbxFloatDT,
                    0.4);
    define_property(mat, "SpecularRotation", "specular_rotation", FbxFloatDT,
                    0.0);
    define_property(mat, "Transmission", "transmission", FbxFloatDT, 0.0);
    define_property(mat, "TransmissionDepth", "transmission_depth", FbxFloatDT,
                    0.0);
    define_property(mat, "TransmissionColor", "transmission_color",
                    FbxDouble3DT, FbxDouble3(1.0, 1.0, 1.0));
    define_property(mat, "TransmissionScatter", "transmission_scatter",
                    FbxDouble3DT, FbxDouble3(0.0, 0.0, 0.0));
    define_property(mat, "TransmissionExtraRoughness",
                    "transmission_extra_roughness", FbxFloatDT, 0.0);
    define_property(mat, "TransmissionDispersion", "transmission_dispersion",
                    FbxFloatDT, 0.0);
    define_property(mat, "TransmissionScatterAnisotropy",
                    "transmission_scatter_anisotropy", FbxFloatDT, 0.0);
    define_property(mat, "Sheen", "sheen", FbxFloatDT, 0.0);
    define_property(mat, "SheenColor", "sheen_color", FbxDouble3DT,
                    FbxDouble3(1.0, 1.0, 1.0));
    define_property(mat, "SheenRoughness", "sheen_roughness", FbxFloatDT, 0.3);
    define_property(mat, "Coat", "coat", FbxFloatDT, 0.0);
    define_property(mat, "CoatAffectColor", "coat_affect_color", FbxFloatDT,
                    0.0);
    define_property(mat, "CoatNormal", "coat_normal", FbxDouble3DT,
                    FbxDouble3(0.0, 0.0, 0.0));
    define_property(mat, "CoatRoughness", "coat_roughness", FbxFloatDT, 0.1);
    define_property(mat, "CoatColor", "coat_color", FbxDouble3DT,
                    FbxDouble3(1.0, 1.0, 1.0));
    define_property(mat, "CoatIOR", "coat_IOR", FbxFloatDT, 1.5);
    define_property(mat, "CoatAffectRoughness", "coat_affect_roughness",
                    FbxFloatDT, 0.0);
    define_property(mat, "CoatRotation", "coat_rotation", FbxFloatDT, 0.0);
    define_property(mat, "CoatAnisotropy", "coat_anisotropy", FbxFloatDT, 0.0);
    define_property(mat, "ThinWalled", "thin_walled", FbxBoolDT, false);
    define_property(mat, "ThinFilmIOR", "thin_film_IOR", FbxFloatDT, 1.5);
    define_property(mat, "ThinFilmThickness", "thin_film_thickness", FbxFloatDT,
                    0.0);
    define_property(mat, "Subsurface", "subsurface", FbxFloatDT, 0.0);
    define_property(mat, "SubsurfaceScale", "subsurface_scale", FbxFloatDT,
                    1.0);
    define_property(mat, "SubsurfaceAnisotropy", "subsurface_anisotropy",
                    FbxFloatDT, 0.0);
    define_property(mat, "SubsurfaceRadius", "subsurface_radius", FbxDouble3DT,
                    FbxDouble3(1.0, 1.0, 1.0));
    define_property(mat, "SubsurfaceColor", "subsurface_color", FbxDouble3DT,
                    FbxDouble3(1.0, 1.0, 1.0));
    define_property(mat, "Metalness", "metalness", FbxFloatDT, 0.0);
    define_property(mat, "Opacity", "opacity", FbxDouble3DT,
                    FbxDouble3(1.0, 1.0, 1.0));
    define_property(mat, "DiffuseRoughness", "diffuse_roughness", FbxFloatDT,
                    0.0);

    return mat;
}

template <typename T>
void define_property(FbxSurfaceMaterial* mat, const char* name,
                     const char* shader_name, FbxDataType data_type, T value)
{
    auto prop =
        FbxSurfaceMaterialUtils::AddProperty(mat, name, shader_name, data_type);
    if (prop.IsValid()) prop.Set<T>(value);
}

void set_normal(const Normal* input, size_t input_count,
                FbxGeometryElementNormal* target)
{
    target->SetName(input->name);
    target->SetMappingMode(FbxGeometryElement::eByPolygonVertex);
    target->SetReferenceMode(FbxGeometryElement::eDirect);

    for (auto i = 0; i < input_count; i++)
    {
        auto normal = input->normal[i];
        target->GetDirectArray().Add(*(FbxVector4*)&normal);
    }
}

void set_uv(const UV* input, size_t input_count, FbxGeometryElementUV* target)
{
    target->SetName(input->name);
    target->SetMappingMode(FbxGeometryElement::eByPolygonVertex);
    target->SetReferenceMode(FbxGeometryElement::eDirect);
    for (auto i = 0; i < input_count; i++)
    {
        auto uv = input->uv[i];
        target->GetDirectArray().Add(*(FbxVector2*)&uv);
    }
}

void vertex_normal_from_poly_normal(
    const unsigned int* indices, size_t index_count, const unsigned int* polys,
    size_t poly_count, const Vector4* poly_normals, Vector4* out_vertex_normals)
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
        for (auto j = curr_index; j < next_index; j++)
        {
            vertex_normals[j] = normal;
        }
    }
    for (auto i = 0; i < index_count; i++)
    {
        out_vertex_normals[i] = vertex_normals[i];
    }
}

void fix_normal_rot(Vector4* normals, size_t normal_count)
{
    FbxAMatrix m;
    m.SetIdentity();
    m = fix_rot_m(m);
    for (size_t i = 0; i < normal_count; i++)
    {
        normals[i] = *(Vector4*)&m.MultT(*(FbxVector4*)&normals[i]);
    }
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

FbxAMatrix fix_rot_m(const FbxAMatrix& input)
{
    FbxAMatrix m(input);
    auto rad = cos(M_PI / 4.0);
    m.SetQ(FbxQuaternion(rad, 0, 0, rad)); // Z-up to Y-up
    return m;
}

FbxAMatrix fix_scale_m(const FbxAMatrix& input, double unit_scale)
{
    FbxAMatrix m(input);
    auto cm_scale = unit_scale * 100.0;
    m.SetS(FbxVector4(cm_scale, cm_scale, cm_scale));
    return m;
}