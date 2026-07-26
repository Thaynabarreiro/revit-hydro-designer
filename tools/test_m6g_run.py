# -*- coding: utf-8 -*-
import sys, traceback

try:
    with open(r"c:\Users\Shadow\Documents\00 - Claude - Revit\tools\m6g_rede_final.py") as f:
        code = f.read()
    exec(code)
    print("Execution SUCCESS!")
except Exception as e:
    print("ERROR MSG: " + str(e))
    print("TRACEBACK: " + traceback.format_exc())
