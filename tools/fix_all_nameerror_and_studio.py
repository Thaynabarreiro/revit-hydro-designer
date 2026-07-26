# -*- coding: utf-8 -*-
"""Fix NameError __file__ in all scripts and rebuild pyRevit buttons with full options."""
import os
import glob

if "RAIZ" in globals():
    RAIZ = globals()["RAIZ"]
elif "__file__" in globals():
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    RAIZ = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
else:
    RAIZ = os.environ.get("HYDRO_PROJECT_ROOT", os.getcwd())
_proj_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir

SAFE_RAIZ_BLOCK = """if "RAIZ" in globals():
    RAIZ = globals()["RAIZ"]
elif "__file__" in globals():
if "RAIZ" in globals():
    RAIZ = globals()["RAIZ"]
elif "__file__" in globals():
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    RAIZ = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
else:
    RAIZ = os.environ.get("HYDRO_PROJECT_ROOT", os.getcwd())
    RAIZ = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
else:
    RAIZ = os.environ.get("HYDRO_PROJECT_ROOT", os.getcwd())"""

# Update all python scripts in tools/
py_files = glob.glob(os.path.join(_proj_root, "tools", "*.py"))

fixed_files = 0
for py_file in py_files:
    with open(py_file, "r", encoding="utf-8") as f:
        content = f.read()
        
if "RAIZ" in globals():
    RAIZ = globals()["RAIZ"]
elif "__file__" in globals():
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    RAIZ = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
else:
    RAIZ = os.environ.get("HYDRO_PROJECT_ROOT", os.getcwd())
        # Replace un-guarded __file__ usage
        lines = content.splitlines()
        new_lines = []
        skip_next = 0
        modified = False
        for i, line in enumerate(lines):
            if skip_next > 0:
                skip_next -= 1
                continue
if "RAIZ" in globals():
    RAIZ = globals()["RAIZ"]
elif "__file__" in globals():
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    RAIZ = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
else:
    RAIZ = os.environ.get("HYDRO_PROJECT_ROOT", os.getcwd())
                # Check next lines
                new_lines.append(SAFE_RAIZ_BLOCK)
                modified = True
                # Skip the old 2 lines following if they were the old block
                if i + 2 < len(lines) and 'RAIZ = globals().get("RAIZ"' in lines[i + 2]:
                    skip_next = 2
                elif i + 1 < len(lines) and 'RAIZ = globals().get("RAIZ"' in lines[i + 1]:
                    skip_next = 1
            else:
                new_lines.append(line)
                
        if modified:
            with open(py_file, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines) + "\n")
            fixed_files += 1
            print("Fixed safe RAIZ in:", py_file)

print("Total files fixed for safe RAIZ:", fixed_files)
