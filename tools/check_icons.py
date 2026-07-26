# -*- coding: utf-8 -*-
import os

if "RAIZ" in globals():
    RAIZ = globals()["RAIZ"]
elif "__file__" in globals():
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    RAIZ = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
else:
    RAIZ = os.environ.get("HYDRO_PROJECT_ROOT", os.getcwd())
_proj_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
BASE_DIR = os.path.join(_proj_root, "revit-hydro-designer.extension")

icons_found = []
for r, d, files in os.walk(BASE_DIR):
    for f in files:
        if f.lower() == "icon.png":
            fp = os.path.join(r, f)
            sz = os.path.getsize(fp)
            icons_found.append((fp, sz))

print("Found {0} icon.png files:".format(len(icons_found)))
for path, sz in icons_found:
    print("  {0:85} | {1} bytes".format(path, sz))
