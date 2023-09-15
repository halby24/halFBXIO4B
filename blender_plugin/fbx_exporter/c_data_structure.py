# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

import ctypes

class ObjectData(ctypes.Structure):
    _pack_ = 1

ObjectData._fields_ = (
    ('name', ctypes.POINTER(ctypes.c_char)),
    ('name_length', ctypes.c_size_t),
    ('matrix_local', ctypes.c_float * 16),
    ('parent', ctypes.POINTER(ObjectData)),
)

class ExportData(ctypes.Structure):
    _pack_ = 1
    _fields_ = (
        ('objects', ctypes.POINTER(ObjectData)),
        ('object_count', ctypes.c_size_t),
    )