# Copyright 2023 HALBY
# This program is distributed under the terms of the MIT License. See the file LICENSE for details.
set(CMAKE_MIN_REQ_VERSION 3.12)
cmake_minimum_required(VERSION ${CMAKE_MIN_REQ_VERSION})

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_CURRENT_LIST_DIR}/cmake")

find_package(FBXSDK REQUIRED)

set(FBX_TARGET_NAME HalFbxExporter)
set(FBX_TARGET_SOURCE
    src/HalFbxExporter.h
    src/HalFbxExporter.cxx
    src/Common.h
    src/Common.cxx
)
project(${FBX_TARGET_NAME})
add_library(HalFbxExporter SHARED ${FBX_TARGET_SOURCE})
target_link_libraries(${FBX_TARGET_NAME} FBXSDK::FBXSDK)

include(GNUInstallDirs)
set(CMAKE_INSTALL_PREFIX ${CMAKE_CURRENT_LIST_DIR}/../scripts)
install(TARGETS ${FBX_TARGET_NAME} LIBRARY)
string(REPLACE "${CMAKE_STATIC_LIBRARY_SUFFIX}" "${CMAKE_SHARED_LIBRARY_SUFFIX}" FBXSDK_DYLIB ${FBXSDK_LIBRARY})
install(FILES ${FBXSDK_DYLIB} DESTINATION ${CMAKE_INSTALL_BINDIR})