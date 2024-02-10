#include "./HalFbxExporter.h"
#include <pybind11/pybind11.h>
namespace py = pybind11;

PYBIND11_MODULE(HalFbxExporter, m) {
    m.doc() = "Export FBX file";
    // m.add_object("ObjectData", py::capsule(&ObjectData, "ObjectData"));
    m.def("export_fbx", &export_fbx, "Export FBX file");
}