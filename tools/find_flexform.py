# -*- coding: utf-8 -*-
import os
appdata = os.environ.get("APPDATA", "")
ipy_path = os.path.join(appdata, "pyRevit-Master", "pyrevitlib", "pyrevit", "forms", "_ipy.py")
if os.path.exists(ipy_path):
    with open(ipy_path, "r", encoding="utf-8") as f:
        print(f.read()[:500])
