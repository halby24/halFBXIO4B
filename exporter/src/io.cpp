// Copyright 2023 HALBY
// This program is distributed under the terms of the MIT License. See the file
// LICENSE for details.

#include "../include/io.h"

#include <fbxsdk.h>

#include <cstring>
#include <iostream>
#define _USE_MATH_DEFINES
#include <concepts>
#include <math.h>
#include <vector>

FbxString get_path(const char* path);
FbxNode* create_node_recursive(FbxScene* scene, const IOData* export_data,
                               Object* object_data);
FbxMesh* create_mesh(const Mesh* mesh_data, const char* name, FbxScene* scene,
                     double unit_scale);
FbxSurfaceMaterial* create_material(FbxScene* scene, const Material& input);
template <typename T>
void define_property(FbxSurfaceMaterial* mat, const char* name,
                     const char* shader_name, FbxDataType data_type, T value);
void set_normal(const Normal* input, size_t input_count,
                FbxGeometryElementNormal* target);
void set_uv(const UV* input, size_t input_count, FbxGeometryElementUV* target);
void fix_coord(double unit_scale, Vector4* vertices, size_t vertex_count);
FbxAMatrix fix_rot_m(const FbxAMatrix& input);
FbxAMatrix fix_scale_m(const FbxAMatrix& input, double unit_scale);
void recursive_delete_object(Object* object);
void delete_mesh(Mesh* mesh);
Object* read_node_recursive(FbxNode* node, Material* mats);
Mesh* read_mesh(FbxMesh* fmesh);
int read_materials(FbxScene* scene, Material** out_mats);

/// @brief FBXファイルをインポートする
/// @param import_path インポートするファイルのパス
/// @return インポートされたデータ
IOData* import_fbx(const char* import_path)
{
    auto path_fbxstr = get_path(import_path);
    if (path_fbxstr.IsEmpty())
    {
        std::cerr << "File path is invalid." << std::endl;
        return nullptr;
    }

    auto manager = FbxManager::Create();
    auto importer = FbxImporter::Create(manager, "");

    if (!importer->Initialize(path_fbxstr, -1, manager->GetIOSettings()))
    {
        std::cerr << "An error occurred while initializing the importer..."
                  << std::endl;
        manager->Destroy();
        return nullptr;
    }

    auto scene = FbxScene::Create(manager, "Scene");
    importer->Import(scene);
    importer->Destroy();

    auto root_node = scene->GetRootNode();
    if (root_node == nullptr)
    {
        std::cerr << "Root node is null." << std::endl;
        manager->Destroy();
        return nullptr;
    }

    Material* mats = nullptr;
    auto mat_count = read_materials(scene, &mats);
    auto root = read_node_recursive(root_node, mats);

    manager->Destroy();

    auto data = new IOData();
    data->root = root;
    data->unit_scale = 0.01;
    data->is_ascii = true;
    data->materials = mats;
    data->material_count = mat_count;

    return data;
}

/// @brief FBXファイルをエクスポートする
/// @param export_path エクスポート先のパス
/// @param export_data エクスポートするデータ
/// @return エクスポートに成功したかどうか
bool export_fbx(const char* export_path, const IOData* export_data)
{
    auto path_fbxstr = get_path(export_path);
    if (path_fbxstr.IsEmpty())
    {
        std::cerr << "File path is invalid." << std::endl;
        return false;
    }

    auto manager = FbxManager::Create();
    auto scene = FbxScene::Create(manager, "Scene");

    // マテリアルの設定 (ノードツリーの作成より先に行う必要がある)
    for (auto i = 0; i < export_data->material_count; i++)
    {
        auto emat = export_data->materials[i];
        auto fmat = create_material(scene, emat);
        scene->AddMaterial(fmat);
    }

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

/// @brief ノードを再帰的に読み込む
/// @param node ノード
/// @param mats マテリアル
/// @return 読み込まれたノード
Object* read_node_recursive(FbxNode* node, Material* mats)
{
    if (node == nullptr) return nullptr;

    auto object = new Object();
    object->name = new char[strlen(node->GetName()) + 1];
    std::strcpy(object->name, node->GetName());
    object->child_count = node->GetChildCount();
    object->children = new Object[object->child_count];
    for (auto i = 0; i < object->child_count; i++)
    {
        object->children[i] = *read_node_recursive(node->GetChild(i), mats);
    }

    auto mesh = node->GetMesh();
    if (mesh != nullptr) { object->mesh = read_mesh(mesh); }

    auto material_count = node->GetMaterialCount();
    if (material_count > 0)
    {
        object->material_slot_count = material_count;
        object->material_slots = new Material*[material_count];
        for (auto i = 0; i < material_count; i++)
        {
            auto fmat = node->GetMaterial(i);
            for (auto mat_i = 0; mat_i < material_count; mat_i++)
            {
                if (std::strcmp(fmat->GetName(), mats[mat_i].name) == 0)
                {
                    object->material_slots[i] = &mats[mat_i];
                    break;
                }
            }
        }
    }

    return object;
}

/// @brief パスのバリデーション
/// @param path パス
/// @return バリデーションされたパス
FbxString get_path(const char* path)
{
    // The example can take a FBX file as an argument.
    FbxString path_fbxstr(path);

    std::cerr << "Save path: " << path_fbxstr.Buffer() << std::endl;

    char* path_char = NULL;
    FbxAnsiToUTF8(path_fbxstr.Buffer(), path_char, NULL);
    path_fbxstr = path_char;

    return path_fbxstr;
}

/// @brief ノードを再帰的に作成する
/// @param scene シーン
/// @param export_data エクスポートデータ
/// @param object_data オブジェクトデータ
/// @return 作成されたノード
FbxNode* create_node_recursive(FbxScene* scene, const IOData* export_data,
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

    // マテリアルの設定はメッシュの設定より先にやったほうがいい気がする
    if (object_data->material_slot_count > 0)
    {
        for (auto i = 0; i < object_data->material_slot_count; i++)
        {
            auto mat = object_data->material_slots[i];
            for (auto mat_i = 0; mat_i < export_data->material_count; mat_i++)
            {
                if (&export_data->materials[mat_i] != mat) continue;

                auto fbx_mat = scene->GetMaterial(mat_i);
                node->AddMaterial(fbx_mat);
                break;
            }
        }
    }

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

/// @brief メッシュを読み込む
/// @param fmesh 読み込むメッシュ
/// @return 読み込まれたメッシュ
Mesh* read_mesh(FbxMesh* fmesh)
{
    if (fmesh == nullptr) return nullptr;

    auto imesh = new Mesh();
    imesh->name = new char[strlen(fmesh->GetName()) + 1];
    std::strcpy(imesh->name, fmesh->GetName());

    // 頂点の追加
    imesh->vertex_count = fmesh->GetControlPointsCount();
    imesh->vertices = new Vector4[imesh->vertex_count];
    auto control_points = fmesh->GetControlPoints();
    for (auto i = 0; i < imesh->vertex_count; i++)
    {
        imesh->vertices[i] = *(Vector4*)&control_points[i];
    }

    // 頂点インデックスの設定
    imesh->index_count = fmesh->GetPolygonVertexCount();
    imesh->indices = new unsigned int[imesh->index_count];
    std::memcpy(imesh->indices, fmesh->GetPolygonVertices(),
                imesh->index_count * sizeof(unsigned int));

    // 面の設定
    imesh->poly_count = fmesh->GetPolygonCount();
    imesh->polys = new unsigned int[imesh->poly_count];
    std::memcpy(imesh->polys, fmesh->GetPolygonVertices(),
                imesh->poly_count * sizeof(unsigned int));

    // マテリアルの設定
    imesh->material_indices = new unsigned int[imesh->poly_count];
    for (auto i = 0; i < imesh->poly_count; i++)
    {
        imesh->material_indices[i] =
            fmesh->GetElementMaterial()->GetIndexArray().GetAt(i);
    }

    // UVの設定
    imesh->uv_set_count = fmesh->GetElementUVCount();
    imesh->uv_sets = new UV[imesh->uv_set_count];
    for (auto i = 0; i < imesh->uv_set_count; i++)
    {
        auto eluv = fmesh->GetElementUV(i);
        imesh->uv_sets[i].name = new char[strlen(eluv->GetName()) + 1];
        std::strcpy(imesh->uv_sets[i].name, eluv->GetName());
        imesh->uv_sets[i].uv = new Vector2[imesh->index_count];
        for (auto j = 0; j < imesh->index_count; j++)
        {
            auto uv = eluv->GetDirectArray().GetAt(j);
            imesh->uv_sets[i].uv[j] = *(Vector2*)&uv;
        }
    }

    // 頂点法線の設定
    imesh->normal_set_count = fmesh->GetElementNormalCount();
    imesh->normal_sets = new Normal[imesh->normal_set_count];
    for (auto i = 0; i < imesh->normal_set_count; i++)
    {
        auto elnrm = fmesh->GetElementNormal(i);
        imesh->normal_sets[i].name = new char[strlen(elnrm->GetName()) + 1];
        std::strcpy(imesh->normal_sets[i].name, elnrm->GetName());
        imesh->normal_sets[i].normal = new Vector4[imesh->index_count];
        for (auto j = 0; j < imesh->index_count; j++)
        {
            auto normal = elnrm->GetDirectArray().GetAt(j);
            imesh->normal_sets[i].normal[j] = *(Vector4*)&normal;
        }
    }

    return imesh;
}

/// @brief メッシュを作成する
/// @param mesh_data メッシュのデータ
/// @param name メッシュの名前
/// @param scene メッシュを登録するシーン
/// @param unit_scale 単位
/// @return 作成されたメッシュ
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

    // メッシュのポリゴンを設定
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

    // 頂点法線の設定
    for (auto i = 0; i < mesh_data->normal_set_count; i++)
    {
        auto elnrm = mesh->CreateElementNormal();
        set_normal(&mesh_data->normal_sets[i], mesh_data->index_count, elnrm);
    }

    // UVの設定
    for (auto i = 0; i < mesh_data->uv_set_count; i++)
    {
        auto eluv = mesh->CreateElementUV(mesh_data->uv_sets[i].name);
        set_uv(&mesh_data->uv_sets[i], mesh_data->index_count, eluv);
    }

    // マテリアルの設定
    auto elmat = mesh->CreateElementMaterial();
    elmat->SetMappingMode(FbxGeometryElement::eByPolygon);
    elmat->SetReferenceMode(FbxGeometryElement::eIndexToDirect);
    elmat->GetIndexArray().SetCount(mesh_data->poly_count);
    for (auto i = 0; i < mesh_data->poly_count; i++)
    {
        elmat->GetIndexArray().SetAt(i, mesh_data->material_indices[i]);
    }

    return mesh;
}

/// @brief マテリアルを読み込む
/// @param scene マテリアルを読み込むシーン
/// @param out_mats マテリアルの出力先
/// @return マテリアルの個数
int read_materials(FbxScene* scene, Material** out_mats)
{
    auto mat_count = scene->GetMaterialCount();
    auto mats = new Material[mat_count];
    for (auto i = 0; i < mat_count; i++)
    {
        auto fbx_mat = scene->GetMaterial(i);
        mats[i].name = new char[strlen(fbx_mat->GetName()) + 1];
        std::strcpy(mats[i].name, fbx_mat->GetName());
    }
    *out_mats = mats;
    return mat_count;
}

// FbxSurfaceMaterial* create_material(FbxScene* scene, const Material& input)
// {
//     auto mat = FbxSurfaceMaterialUtils::CreateShaderMaterial(
//         scene, input.name, FBXSDK_SHADING_LANGUAGE_SSSL, "1.0.1",
//         FBXSDK_RENDERING_API_SSSL, "");

//     FbxProperty prop;
//     define_property(mat, "Base", "base", FbxFloatDT,
//     input.standard_surface.base); define_property(mat, "BaseColor",
//     "base_color", FbxDouble3DT,
//                     FbxDouble3(input.standard_surface.base_color.x,
//                     input.standard_surface.base_color.y,
//                     input.standard_surface.base_color.z));
//     define_property(mat, "Emission", "emission", FbxFloatDT,
//     input.standard_surface.emission); define_property(mat, "EmissionColor",
//     "emission_color", FbxDouble3DT,
//                     FbxDouble3(input.standard_surface.emission_color.x,
//                     input.standard_surface.emission_color.y,
//                     input.standard_surface.emission_color.z));
//     define_property(mat, "Specular", "specular", FbxFloatDT,
//     input.standard_surface.specular); define_property(mat, "SpecularIOR",
//     "specular_IOR", FbxFloatDT, input.standard_surface.specular_ior);
//     define_property(mat, "SpecularColor", "specular_color", FbxDouble3DT,
//                     FbxDouble3(input.standard_surface.specular_color.x,
//                     input.standard_surface.specular_color.y,
//                     input.standard_surface.specular_color.z));
//     define_property(mat, "SpecularAnisotropy", "specular_anisotropy",
//                     FbxFloatDT, input.standard_surface.specular_anisotropy);
//     define_property(mat, "SpecularRoughness", "specular_roughness",
//     FbxFloatDT,
//                     input.standard_surface.specular_roughness);
//     define_property(mat, "SpecularRotation", "specular_rotation", FbxFloatDT,
//                     input.standard_surface.specular_rotation);
//     define_property(mat, "Transmission", "transmission", FbxFloatDT,
//     input.standard_surface.transmission); define_property(mat,
//     "TransmissionDepth", "transmission_depth", FbxFloatDT,
//                     input.standard_surface.transmission_depth);
//     define_property(mat, "TransmissionColor", "transmission_color",
//                     FbxDouble3DT,
//                     FbxDouble3(input.standard_surface.transmission_color.x,
//                     input.standard_surface.transmission_color.y,
//                     input.standard_surface.transmission_color.z));
//     define_property(mat, "TransmissionScatter", "transmission_scatter",
//                     FbxDouble3DT,
//                     FbxDouble3(input.standard_surface.transmission_scatter.x,
//                     input.standard_surface.transmission_scatter.y,
//                     input.standard_surface.transmission_scatter.z));
//     define_property(mat, "TransmissionExtraRoughness",
//                     "transmission_extra_roughness", FbxFloatDT,
//                     input.standard_surface.transmission_extra_roughness);
//     define_property(mat, "TransmissionDispersion", "transmission_dispersion",
//                     FbxFloatDT,
//                     input.standard_surface.transmission_dispersion);
//     define_property(mat, "TransmissionScatterAnisotropy",
//                     "transmission_scatter_anisotropy", FbxFloatDT,
//                     input.standard_surface.transmission_scatter_anisotropy);
//     define_property(mat, "Sheen", "sheen", FbxFloatDT,
//     input.standard_surface.sheen); define_property(mat, "SheenColor",
//     "sheen_color", FbxDouble3DT,
//                     FbxDouble3(input.standard_surface.sheen_color.x,
//                     input.standard_surface.sheen_color.y,
//                     input.standard_surface.sheen_color.z));
//     define_property(mat, "SheenRoughness", "sheen_roughness", FbxFloatDT,
//     input.standard_surface.sheen_roughness); define_property(mat, "Coat",
//     "coat", FbxFloatDT, input.standard_surface.coat); define_property(mat,
//     "CoatAffectColor", "coat_affect_color", FbxFloatDT,
//                     input.standard_surface.coat_affect_color);
//     define_property(mat, "CoatNormal", "coat_normal", FbxDouble3DT,
//                     FbxDouble3(input.standard_surface.coat_normal.x,
//                     input.standard_surface.coat_normal.y,
//                     input.standard_surface.coat_normal.z));
//     define_property(mat, "CoatRoughness", "coat_roughness", FbxFloatDT,
//     input.standard_surface.coat_roughness); define_property(mat, "CoatColor",
//     "coat_color", FbxDouble3DT,
//                     FbxDouble3(input.standard_surface.coat_color.x,
//                     input.standard_surface.coat_color.y,
//                     input.standard_surface.coat_color.z));
//     define_property(mat, "CoatIOR", "coat_IOR", FbxFloatDT,
//     input.standard_surface.coat_ior); define_property(mat,
//     "CoatAffectRoughness", "coat_affect_roughness",
//                     FbxFloatDT,
//                     input.standard_surface.coat_affect_roughness);
//     define_property(mat, "CoatRotation", "coat_rotation", FbxFloatDT,
//     input.standard_surface.coat_rotation); define_property(mat,
//     "CoatAnisotropy", "coat_anisotropy", FbxFloatDT,
//     input.standard_surface.coat_anisotropy); define_property(mat,
//     "ThinWalled", "thin_walled", FbxBoolDT,
//     input.standard_surface.thin_walld); define_property(mat, "ThinFilmIOR",
//     "thin_film_IOR", FbxFloatDT, input.standard_surface.thin_film_ior);
//     define_property(mat, "ThinFilmThickness", "thin_film_thickness",
//     FbxFloatDT,
//                     input.standard_surface.thin_film_thickness);
//     define_property(mat, "Subsurface", "subsurface", FbxFloatDT,
//     input.standard_surface.subsurface); define_property(mat,
//     "SubsurfaceScale", "subsurface_scale", FbxFloatDT,
//                     input.standard_surface.subsurface_scale);
//     define_property(mat, "SubsurfaceAnisotropy", "subsurface_anisotropy",
//                     FbxFloatDT,
//                     input.standard_surface.subsurface_anisotropy);
//     define_property(mat, "SubsurfaceRadius", "subsurface_radius",
//     FbxDouble3DT,
//                     FbxDouble3(input.standard_surface.subsurface_radius.x,
//                     input.standard_surface.subsurface_radius.y,
//                     input.standard_surface.subsurface_radius.z));
//     define_property(mat, "SubsurfaceColor", "subsurface_color", FbxDouble3DT,
//                     FbxDouble3(input.standard_surface.subsurface_color.x,
//                     input.standard_surface.subsurface_color.y,
//                     input.standard_surface.subsurface_color.z));
//     define_property(mat, "Metalness", "metalness", FbxFloatDT,
//     input.standard_surface.metalness); define_property(mat, "Opacity",
//     "opacity", FbxFloatDT,
//                     input.standard_surface.opacity);
//     define_property(mat, "DiffuseRoughness", "diffuse_roughness", FbxFloatDT,
//                     input.standard_surface.diffuse_roughness);

//     return mat;
// }

/// @brief マテリアルを作成する
/// @param scene マテリアルを登録するシーン
/// @param input マテリアルのデータ
/// @return 作成されたマテリアル
FbxSurfaceMaterial* create_material(FbxScene* scene, const Material& input)
{
    auto mat = FbxSurfaceLambert::Create(scene, input.name);
    mat->Ambient.Set(FbxDouble3(input.standard_surface.base_color.x,
                                input.standard_surface.base_color.y,
                                input.standard_surface.base_color.z));
    mat->Diffuse.Set(FbxDouble3(input.standard_surface.base_color.x,
                                input.standard_surface.base_color.y,
                                input.standard_surface.base_color.z));
    mat->TransparencyFactor.Set(1.0 - input.standard_surface.opacity);
    mat->Emissive.Set(FbxDouble3(input.standard_surface.emission_color.x,
                                input.standard_surface.emission_color.y,
                                input.standard_surface.emission_color.z));
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

/// @brief メッシュに対して頂点法線を設定する
/// @param input 頂点法線のデータ (配列)
/// @param input_count 頂点法線の数
/// @param target 設定する対象のジオメトリ
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

/// @brief メッシュに対してUVを設定する
/// @param input UVのデータ (配列)
/// @param input_count UVの数
/// @param target 設定する対象のジオメトリ
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

/// @brief 面法線から頂点法線を計算する
/// @param indices 頂点インデックスの配列
/// @param index_count 頂点インデックスの数
/// @param polys ポリゴン開始インデックスの配列
/// @param poly_count ポリゴン数
/// @param poly_normals ポリゴン法線の配列
/// @param out_vertex_normals 計算した頂点法線の出力先
void vnrm_from_pnrm(const unsigned int* indices, size_t index_count,
                    const unsigned int* polys, size_t poly_count,
                    const Vector4* poly_normals, Vector4* out_vertex_normals)
{
    std::vector<Vector4> vertex_normals;
    vertex_normals.resize(index_count);
    for (auto i = 0; i < poly_count; i++)
    {
        auto normal = poly_normals[i];
        FbxAMatrix m;
        m.SetIdentity();
        m = fix_rot_m(m);
        auto f_nrm = m.MultT(*(FbxVector4*)&normal);
        normal = *(Vector4*)&f_nrm;

        auto curr_index = polys[i];
        auto next_index = (i == poly_count - 1) ? index_count : polys[i + 1];

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

/// @brief ジオメトリの座標系を修正する
/// @param unit_scale 単位
/// @param vertices 修正する頂点の配列
/// @param vertex_count 頂点の数
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

/// @brief 座標系を修正する行列を作成する
/// @param input 入力行列
/// @return 修正された行列
FbxAMatrix fix_rot_m(const FbxAMatrix& input)
{
    FbxAMatrix m(input);
    auto rad = cos(M_PI / 4.0);
    m.SetQ(FbxQuaternion(rad, 0, 0, -rad)); // Z-up to Y-up
    return m;
}

/// @brief 大きさを修正する行列を作成する
/// @param input 入力行列
/// @param unit_scale 単位
/// @return 修正された行列
FbxAMatrix fix_scale_m(const FbxAMatrix& input, double unit_scale)
{
    FbxAMatrix m(input);
    auto cm_scale = unit_scale * 100.0;
    m.SetS(FbxVector4(cm_scale, cm_scale, cm_scale));
    return m;
}

/// @brief IODataのメモリを解放する
/// @param data 解放するデータ
void delete_iodata(IOData* data)
{
    if (data == nullptr) return;
    if (data->root != nullptr) recursive_delete_object(data->root);
    if (data->materials != nullptr) delete[] data->materials;
    delete data;
}

/// @brief Objectのメモリを再帰的に解放する
/// @param object 解放するオブジェクト
void recursive_delete_object(Object* object)
{
    if (object == nullptr) return;
    if (object->name != nullptr) delete[] object->name;
    if (object->children != nullptr)
    {
        for (auto i = 0; i < object->child_count; i++)
        {
            recursive_delete_object(&object->children[i]);
        }
        delete[] object->children;
    }
    if (object->mesh != nullptr) delete_mesh(object->mesh);
    if (object->material_slots != nullptr) delete[] object->material_slots;
    delete object;
}

/// @brief Meshのメモリを解放する
/// @param mesh 解放するメッシュ
void delete_mesh(Mesh* mesh)
{
    if (mesh == nullptr) return;
    if (mesh->name != nullptr) delete[] mesh->name;
    if (mesh->vertices != nullptr) delete[] mesh->vertices;
    if (mesh->indices != nullptr) delete[] mesh->indices;
    if (mesh->polys != nullptr) delete[] mesh->polys;
    if (mesh->material_indices != nullptr) delete[] mesh->material_indices;
    if (mesh->uv_sets != nullptr)
    {
        for (auto i = 0; i < mesh->uv_set_count; i++)
        {
            if (mesh->uv_sets[i].name != nullptr)
                delete[] mesh->uv_sets[i].name;
            if (mesh->uv_sets[i].uv != nullptr) delete[] mesh->uv_sets[i].uv;
        }
        delete[] mesh->uv_sets;
    }
    if (mesh->normal_sets != nullptr)
    {
        for (auto i = 0; i < mesh->normal_set_count; i++)
        {
            if (mesh->normal_sets[i].name != nullptr)
                delete[] mesh->normal_sets[i].name;
            if (mesh->normal_sets[i].normal != nullptr)
                delete[] mesh->normal_sets[i].normal;
        }
        delete[] mesh->normal_sets;
    }
    delete mesh;
}
