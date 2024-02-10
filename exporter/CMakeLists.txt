# Copyright 2023 HALBY
# This program is distributed under the terms of the MIT License. See the file LICENSE for details.
cmake_minimum_required(VERSION 3.20)

set(FBX_TARGET_NAME HalFbxExporter)
set(FBX_TARGET_SOURCE
    src/HalFbxExporter.h
    src/HalFbxExporter.cxx
)

set(FBX_SDK_PATH "" CACHE PATH "Path to the FBX SDK")

set(CMAKE_CXX_STANDARD 14)

find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 REQUIRED)

project(${FBX_TARGET_NAME})
add_library(HalFbxExporter SHARED ${FBX_TARGET_SOURCE})
target_include_directories(${FBX_TARGET_NAME} PRIVATE "${FBX_SDK_PATH}/include")
target_link_libraries(${FBX_TARGET_NAME} PRIVATE "${FBX_SDK_PATH}/lib/vs2022/x64/debug/libfbxsdk")
