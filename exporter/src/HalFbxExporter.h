// Copyright 2023 HALBY
// This program is distributed under the terms of the MIT License. See the file LICENSE for details.

#ifndef HAL_FBX_EXPORTER_H
#define HAL_FBX_EXPORTER_H

#include "Common.h"
#include "CDataStructure.h"

#define DLLEXPORT extern "C" __declspec(dllexport)

DLLEXPORT int __stdcall ExportFbx(char* pFilePath, ExportData* pExportData);

#endif