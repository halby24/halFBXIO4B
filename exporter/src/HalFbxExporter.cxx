// Copyright 2023 HALBY
// This program is distributed under the terms of the MIT License. See the file LICENSE for details.

#include "./HalFbxExporter.h"
#include <fbxsdk.h>
#include <iostream>

static bool gVerbose = true;

int ExportFbx(char* pFilePath, ExportData* pExportData)
{
    auto manager = FbxManager::Create();
    auto scene = FbxScene::Create(manager, "Scene");

    // The example can take a FBX file as an argument.
    FbxString path(pFilePath);

    if (path.IsEmpty())
    {
        FBXSDK_printf("\n\nFile path is invalid.\n\n");
        manager->Destroy();
        return 0;
    }

    FBXSDK_printf("\n\nSave path: %s\n\n", path.Buffer());

    char* lPath = NULL;
    FbxAnsiToUTF8(path.Buffer(), lPath, NULL);
    path = lPath;

    // Add objects to the scene.
    for (int i = 0; i < pExportData->object_count; i++)
    {
        FbxNode* lNode = FbxNode::Create(lScene, pExportData->objects[i].name);
        FbxDouble4x4 lMatrix;
        for (int j = 0; j < 16; j++) { lMatrix[j / 4][j % 4] = pExportData->objects[i].matrix_local[j]; }

        lScene->GetRootNode()->AddChild(lNode);
    }

    // バイナリまたはASCII形式の選択
    int lFileFormat;
    if (pExportData->is_ascii)
        lFileFormat = lSdkManager->GetIOPluginRegistry()->FindWriterIDByDescription("FBX ascii (*.fbx)");
    else
        lFileFormat = lSdkManager->GetIOPluginRegistry()->FindWriterIDByDescription("FBX binary (*.fbx)");

    lResult = SaveScene(lSdkManager, lScene, path.Buffer(), lFileFormat, false);
    if (lResult == false)
    {
        FBXSDK_printf("\n\nAn error occurred while saving the scene...\n");
        manager->Destroy();
        return 0;
    }

    return 1;
}
