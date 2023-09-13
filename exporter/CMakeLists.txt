# Copyright 2023 HALBY
# This program is distributed under the terms of the MIT License. See the file LICENSE for details.

SET(CMAKE_MIN_REQ_VERSION 2.4)
cmake_minimum_required(VERSION ${CMAKE_MIN_REQ_VERSION})

INCLUDE("variables.cmake")

if (WIN32)
    SET(FBX_ROOT $CACHE{FBX_ROOT_WIN32})
elseif (LINUX)
    SET(FBX_ROOT $CACHE{FBX_ROOT_LINUX})
elseif (APPLE)
    SET(FBX_ROOT $CACHE{FBX_ROOT_MACOS})
endif()

INCLUDE("CMakeSettings.txt")

FBX_PROJECT(HalFbxExporter .)
SET(FBX_TARGET_SOURCE
    src/HalFbxExporter.h
    src/HalFbxExporter.cxx
    src/Common.h
    src/Common.cxx
)
ADD_LIBRARY(
   ${FBX_TARGET_NAME}
   SHARED
   ${FBX_TARGET_SOURCE}
)
SET_SAMPLES_GLOBAL_FLAGS()
