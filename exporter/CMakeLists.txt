# Copyright 2023 HALBY
# This program is distributed under the terms of the MIT License. See the file LICENSE for details.
cmake_minimum_required(VERSION 3.20)

set(FBX_TARGET_NAME HalFbxExporter)
set(FBX_TARGET_SOURCE
    src/HalFbxExporter.cxx
)

set(FBX_SDK_PATH "" CACHE PATH "Path to the FBX SDK")

set(CMAKE_CXX_STANDARD 14)

set(PYTHON_VERSION CACHE STRING "Python version to use")
find_package(Python3 ${PYTHON_VERSION} EXACT COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 REQUIRED)

set(FBX_LIB_DIR "${FBX_SDK_PATH}/lib/vs2022/x64/debug")

project(${FBX_TARGET_NAME})
pybind11_add_module(HalFbxExporter SHARED ${FBX_TARGET_SOURCE})
target_include_directories(${FBX_TARGET_NAME} PRIVATE "${FBX_SDK_PATH}/include")
target_link_libraries(${FBX_TARGET_NAME} PRIVATE "${FBX_LIB_DIR}/libfbxsdk.lib")

set(LIB_DIR "${CMAKE_CURRENT_LIST_DIR}/../scripts/fbx_exporter/lib")

add_custom_command(
    TARGET ${FBX_TARGET_NAME}
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
    "${FBX_LIB_DIR}/libfbxsdk.dll"
    ${LIB_DIR}
)

add_custom_command(
    TARGET ${FBX_TARGET_NAME}
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
    $<TARGET_FILE:${FBX_TARGET_NAME}>
    ${LIB_DIR}
)