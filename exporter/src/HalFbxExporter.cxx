// Copyright 2023 HALBY
// This program is distributed under the terms of the MIT License. See the file LICENSE for details.

#include <fbxsdk.h>
#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>
#include <vector>
#include <memory>
namespace py = pybind11;

struct ObjectData
{
    std::string name;
    std::array<double, 16> matrix_local;
    std::vector<ObjectData*> children;
    std::vector<double> vertices;
};

struct ExportData
{
    ObjectData* root;
    bool is_ascii;
};

FbxNode* create_node_recursive(FbxScene* scene, ObjectData* object_data);
bool export_fbx(std::string export_path, ExportData* export_data);
ObjectData* create_object_data(std::string name, std::array<double, 16> matrix_local, std::vector<ObjectData*> children, std::vector<double> vertices);
ExportData* create_export_data(ObjectData* root, bool is_ascii);
void destroy_object_data(ObjectData* object_data);
void destroy_export_data(ExportData* export_data);

PYBIND11_MODULE(HalFbxExporter, m)
{
    m.doc() = "Export FBX file";
    py::class_<ObjectData>(m, "ObjectData");
    py::class_<ExportData>(m, "ExportData");
    m.def("create_object_data", &create_object_data, "Create ObjectData");
    m.def("create_export_data", &create_export_data, "Create ExportData");
    m.def("destroy_object_data", &destroy_object_data, "Destroy ObjectData");
    m.def("destroy_export_data", &destroy_export_data, "Destroy ExportData");
    m.def("export_fbx", &export_fbx, "Export FBX file");
}

bool export_fbx(std::string export_path, ExportData* export_data)
{
    auto manager = FbxManager::Create();
    auto scene = FbxScene::Create(manager, "Scene");

    // The example can take a FBX file as an argument.
    FbxString path_fbxstr(export_path.c_str());

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
    for (int i = 0; i < root->children.size(); i++) { scene->GetRootNode()->AddChild(root_node->GetChild(i)); }

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

    std::cout << "Create node: " << object_data->name << std::endl;
    auto node = FbxNode::Create(scene, object_data->name.c_str());

    FbxAMatrix transform;
    for (int i = 0; i < 16; i++) { transform[i / 4][i % 4] = object_data->matrix_local[i]; }
    node->LclTranslation.Set(FbxVector4(transform.GetT()));
    node->LclRotation.Set(FbxVector4(transform.GetR()));
    node->LclScaling.Set(FbxVector4(transform.GetS()));

    if (object_data->vertices.size() > 0)
    {
        auto mesh = FbxMesh::Create(scene, object_data->name.c_str());
        mesh->InitControlPoints(object_data->vertices.size());
        auto control_points = mesh->GetControlPoints();
        memccpy(control_points, object_data->vertices.data(), object_data->vertices.size(), sizeof(double));
        node->SetNodeAttribute(mesh);
    }

    for (auto child : object_data->children)
    {
        auto child_node = create_node_recursive(scene, child);
        node->AddChild(child_node);
    }

    return node;
}

ObjectData* create_object_data(std::string name, std::array<double, 16> matrix_local, std::vector<ObjectData*> children, std::vector<double> vertices)
{
    auto object_data = new ObjectData();
    object_data->name = name;
    object_data->matrix_local = matrix_local;
    object_data->children = children;
    object_data->vertices = vertices;
    return object_data;
}

ExportData* create_export_data(ObjectData* root, bool is_ascii)
{
    auto export_data = new ExportData();
    export_data->root = std::move(root);
    export_data->is_ascii = is_ascii;
    return export_data;
}

void destroy_object_data(ObjectData* object_data)
{
    if (object_data == nullptr) return; 
    for (auto& child : object_data->children) destroy_object_data(child);
    delete object_data;
}

void destroy_export_data(ExportData* export_data)
{
    if (export_data == nullptr) return;
    destroy_object_data(export_data->root);
    delete export_data;
}