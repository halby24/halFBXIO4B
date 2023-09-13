// Copyright 2023 HALBY
// This program is distributed under the terms of the MIT License. See the file LICENSE for details.

#include "HalFbxExporter.h"

static bool gVerbose = true;

DLLEXPORT int __stdcall ExportFbx(char* pFilePath)
{
    FbxManager* lSdkManager = NULL;
    FbxScene* lScene = NULL;
    bool lResult;

    // Prepare the FBX SDK.
    InitializeSdkObjects(lSdkManager, lScene);

    // The example can take a FBX file as an argument.
	FbxString lFilePath(pFilePath);

	if( lFilePath.IsEmpty() )
	{
        lResult = false;
        FBXSDK_printf("\n\nFile path is invalid.\n\n");
        DestroySdkObjects(lSdkManager, lResult);
        return 1;
	}

    FBXSDK_printf("\n\nSave path: %s\n\n", lFilePath.Buffer());

    char* lPath = NULL;
    FbxAnsiToUTF8(lFilePath.Buffer(), lPath, NULL);
    lFilePath = lPath;

    lResult = SaveScene(lSdkManager, lScene, lFilePath.Buffer());
    if(lResult == false)
    {
        FBXSDK_printf("\n\nAn error occurred while saving the scene...\n");
        DestroySdkObjects(lSdkManager, lResult);
        return 1;
    }

    // Destroy all objects created by the FBX SDK.
    DestroySdkObjects(lSdkManager, lResult);

    return 0;
}
