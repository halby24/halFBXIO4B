if(NOT DEFINED FBXSDK_VERSION)
    set(FBXSDK_VERSION "2020.3.4")
endif()
if(WIN32 AND NOT DEFINED FBXSDK_ROOT)
    set(FBXSDK_ROOT "C:/Program Files/Autodesk/FBX/FBX SDK/${FBXSDK_VERSION}")
endif()
if(APPLE AND NOT DEFINED FBXSDK_ROOT)
    set(FBXSDK_ROOT "/Applications/Autodesk/FBX SDK/${FBXSDK_VERSION}")
endif()

set(ARCH "x64")
if(CMAKE_SYSTEM_PROCESSOR)
    set(ARCH "${CMAKE_SYSTEM_PROCESSOR}")
endif()
if (WIN32)
    set(FBXSDK_LIB_SUFFIX "lib/vs2022/${ARCH}/${CMAKE_BUILD_TYPE}")
else()
    set(FBXSDK_LIB_SUFFIX "lib/${CMAKE_BUILD_TYPE}")
endif()

find_path(FBXSDK_INCLUDE_DIR fbxsdk.h
    PATHS
        ENV FBXSDK_ROOT
        ENV FBXSDK_INCLUDE_DIR
        ${FBXSDK_ROOT}
        /usr
        /usr/local
        ~/.local
    PATH_SUFFIXES
        include
)

find_library(FBXSDK_LIBRARY
    NAMES
        libfbxsdk
    PATHS
        ENV FBXSDK_ROOT
        ENV FBXSDK_LIB_DIR
        ${FBXSDK_ROOT}
        /usr
        /usr/local
        ~/.local
    PATH_SUFFIXES
        ${FBXSDK_LIB_SUFFIX}
)
mark_as_advanced(
  FBXSDK_INCLUDE_DIR
  FBXSDK_LIBRARY
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(FBXSDK
  REQUIRED_VARS
    FBXSDK_INCLUDE_DIR
    FBXSDK_LIBRARY
)

if(FBXSDK_FOUND AND NOT TARGET FBXSDK::FBXSDK)
  add_library(FBXSDK::FBXSDK UNKNOWN IMPORTED)
  set_target_properties(FBXSDK::FBXSDK PROPERTIES
    IMPORTED_LINK_INTERFACE_LANGUAGES ["C"|"CXX"]
    IMPORTED_LOCATION "${FBXSDK_LIBRARY}"
    INTERFACE_INCLUDE_DIRECTORIES "${FBXSDK_INCLUDE_DIR}"
)
endif()

add_definitions(-DFBXSDK_SHARED)