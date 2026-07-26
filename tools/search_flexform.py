# -*- coding: utf-8 -*-
import os
appdata = os.environ.get("APPDATA", "")
root = os.path.join(appdata, "pyRevit-Master", "pyrevitlib")
if os.path.exists(root):
    for r, d, files in os.walk(root):
        for f in files:
            if f.endswith(".py") and "flex" in f.lower():
                print(os.path.join(r, f))
