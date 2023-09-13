// Copyright 2023 HALBY
// This program is distributed under the terms of the MIT License. See the file LICENSE for details.

#ifndef _HALFBXEXPORTER_H
#define _HALFBXEXPORTER_H

#include "Common.h"

#define DLLEXPORT extern "C" __declspec(dllexport)

DLLEXPORT int __stdcall ExportFbx(char* pFilePath);

#endif // #ifndef _HALFBXEXPORTER_H