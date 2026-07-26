# -*- coding: utf-8 -*-
import sys, traceback

try:
if "RAIZ" in globals():
    RAIZ = globals()["RAIZ"]
elif "__file__" in globals():
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    RAIZ = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
else:
    RAIZ = os.environ.get("HYDRO_PROJECT_ROOT", os.getcwd())
    _proj_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
    m6g_file = os.path.join(_proj_root, "tools", "m6g_rede_final.py")
    with open(m6g_file) as f:
        code = f.read()
    exec(code)
    print("Execution SUCCESS!")
except Exception as e:
    print("ERROR MSG: " + str(e))
    print("TRACEBACK: " + traceback.format_exc())
