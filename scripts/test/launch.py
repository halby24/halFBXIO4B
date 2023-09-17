import os
import sys
import json
import traceback
import threading
import debugpy
from pathlib import Path

DEBUG_HOST = os.environ['DEBUG_HOST']
DEBUG_PORT = os.environ['DEBUG_PORT']

try:
    debugpy.listen((DEBUG_HOST, DEBUG_PORT))
    
    print("Waiting for debug client.")
    debugpy.wait_for_client()
    print("Debug client attached.")

except Exception as e:
    if type(e) is not SystemExit:
        traceback.print_exc()
        sys.exit()
