# Copyright 2023 HALBY
# This software is released under the MIT License, see LICENSE.

import os
import sys
import traceback
import debugpy
import importlib

DEBUG_HOST = os.environ['DEBUG_HOST']
DEBUG_PORT = os.environ['DEBUG_PORT']

def debug(callback: callable):
    try:
        debugpy.listen((DEBUG_HOST, DEBUG_PORT))
        
        print("Waiting for debug client.")
        debugpy.wait_for_client()
        print("Debug client attached.")

        importlib.import_module('..')

        callback()

    except Exception as e:
        if type(e) is not SystemExit:
            traceback.print_exc()
            sys.exit()