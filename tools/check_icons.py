# -*- coding: utf-8 -*-
import os

BASE_DIR = r"c:\Users\Shadow\Documents\00 - Claude - Revit\revit-hydro-designer.extension"

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
