# -*- coding: utf-8 -*-
"""Refactor all python scripts to use portable automatic project-root discovery."""
import os
import glob

_this_dir = os.path.dirname(os.path.abspath(__file__))
_proj_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
TOOLS_DIR = os.path.join(_proj_root, "tools")
EXT_LIB = os.path.join(_proj_root, "revit-hydro-designer.extension", "lib", "hydro.py")

PORTABLE_HEADER = """_this_dir = os.path.dirname(os.path.abspath(__file__))
_auto_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
_this_dir = os.path.dirname(os.path.abspath(__file__))
_auto_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
RAIZ = globals().get("RAIZ", os.environ.get("HYDRO_PROJECT_ROOT", _auto_root))

# Target scripts to replace
py_files = glob.glob(os.path.join(TOOLS_DIR, "*.py"))

replaced_count = 0
for py_file in py_files:
    with open(py_file, "r", encoding="utf-8") as f:
        content = f.read()
    
_this_dir = os.path.dirname(os.path.abspath(__file__))
_auto_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
RAIZ = globals().get("RAIZ", os.environ.get("HYDRO_PROJECT_ROOT", _auto_root))
    lines = content.splitlines()
    new_lines = []
    modified = False
    for line in lines:
_this_dir = os.path.dirname(os.path.abspath(__file__))
_auto_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
RAIZ = globals().get("RAIZ", os.environ.get("HYDRO_PROJECT_ROOT", _auto_root))
            new_lines.append(PORTABLE_HEADER)
            modified = True
_this_dir = os.path.dirname(os.path.abspath(__file__))
_auto_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
RAIZ = globals().get("RAIZ", os.environ.get("HYDRO_PROJECT_ROOT", _auto_root))
D = os.path.join(RAIZ, "data")
_this_dir = os.path.dirname(os.path.abspath(__file__))
_auto_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
RAIZ = globals().get("RAIZ", os.environ.get("HYDRO_PROJECT_ROOT", _auto_root))
            modified = True
        else:
            new_lines.append(line)
            
    if modified:
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines) + "\n")
        replaced_count += 1
        print("Updated:", py_file)

print("Total files refactored for portable RAIZ:", replaced_count)
