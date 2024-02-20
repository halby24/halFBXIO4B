# Copyright 2023 HALBY
# This program is distributed under the terms of the MIT License. See the file LICENSE for details.
cmake_minimum_required(VERSION 3.20)

set(FBX_TARGET_NAME halFBXIO4B)
set(FBX_TARGET_SOURCE
    include/io.h
    src/io.cpp
)

set(CMAKE_CXX_STANDARD 20)
set(FBX_SDK_PATH "" CACHE PATH "Path to the FBX SDK")
set(FBX_LIB_DIR "${FBX_SDK_PATH}/lib/vs2022/x64/debug")

project(${FBX_TARGET_NAME})
add_library(${FBX_TARGET_NAME} SHARED ${FBX_TARGET_SOURCE})
target_include_directories(${FBX_TARGET_NAME} PRIVATE "${FBX_SDK_PATH}/include")
target_link_libraries(${FBX_TARGET_NAME} PRIVATE "${FBX_LIB_DIR}/libfbxsdk.lib")
target_compile_definitions(${FBX_TARGET_NAME} PRIVATE "FBXSDK_SHARED")

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
