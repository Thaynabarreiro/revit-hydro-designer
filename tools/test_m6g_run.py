# -*- coding: utf-8 -*-
import sys, traceback

try:
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    _proj_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
    m6g_file = os.path.join(_proj_root, "tools", "m6g_rede_final.py")
    with open(m6g_file) as f:
        code = f.read()
    exec(code)
    print("Execution SUCCESS!")
except Exception as e:
    print("ERROR MSG: " + str(e))
    print("TRACEBACK: " + traceback.format_exc())
