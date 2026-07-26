# -*- coding: utf-8 -*-
import pyrevit
print("pyrevit dir:", dir(pyrevit))
try:
    from pyrevit import loader
    print("loader:", dir(loader))
except Exception as e:
    print(e)
