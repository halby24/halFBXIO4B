if(NOT DEFINED FBXSDK_VERSION)
    set(FBXSDK_VERSION "2020.3.4")
endif()
if(WIN32 AND NOT DEFINED FBXSDK_ROOT)
    set(FBXSDK_ROOT "C:/Program Files/Autodesk/FBX/FBX SDK/${FBXSDK_VERSION}")
endif()
if(APPLE AND NOT DEFINED FBXSDK_ROOT)
    set(FBXSDK_ROOT "/Applications/Autodesk/FBX SDK/${FBXSDK_VERSION}")
endif()

if(WIN32)
    set(LIB_EXT ".lib")
elseif(APPLE)
    set(LIB_EXT ".dylib")
else()
    set(LIB_EXT ".so")
endif()
set(FBXSDK_LIB "libfbxsdk${LIB_EXT} libxml${LIB_EXT} zlib${LIB_EXT}")

if (WIN32)
    IF(MSVC_VERSION GREATER 1910 AND MSVC_VERSION LESS 1920)
        SET(FBX_COMPILER "vs2017")
    ELSEIF(MSVC_VERSION GREATER 1919 AND MSVC_VERSION LESS 1930)
        SET(FBX_COMPILER "vs2019")
    ELSEIF(MSVC_VERSION GREATER 1929 AND MSVC_VERSION LESS 1940)
        SET(FBX_COMPILER "vs2022")
    ENDIF()
    set(FBXSDK_LIB_SUFFIX "lib/${FBX_COMPILER}/${MSVC_TOOLSET_VERSION}/${CMAKE_BUILD_TYPE}")
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
        fbxsdk
        xml2
        zlib
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