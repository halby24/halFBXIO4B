# Copyright 2023 HALBY
# This program is distributed under the terms of the MIT License. See the file LICENSE for details.

set(CMAKE_MIN_REQ_VERSION 3.12)
cmake_minimum_required(VERSION ${CMAKE_MIN_REQ_VERSION})

project(HalFbxExporter)
set(FBX_TARGET_SOURCE
    src/HalFbxExporter.h
    src/HalFbxExporter.cxx
    src/Common.h
    src/Common.cxx
)
add_library(HalFbxExporter SHARED ${FBX_TARGET_SOURCE})

SET(CMAKE_INSTALL_PREFIX ${CMAKE_CURRENT_LIST_DIR}/../scripts)
INSTALL(TARGETS ${FBX_TARGET_NAME} LIBRARY DESTINATION lib)