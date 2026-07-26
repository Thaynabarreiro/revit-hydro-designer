# -*- coding: utf-8 -*-
import traceback

try:
    with open(r"c:\Users\Shadow\Documents\00 - Claude - Revit\tools\m7_gerar_pranchas.py") as f:
        code = f.read()
    exec(code)
    print("M7 Executed SUCCESS!")
except Exception as e:
    print("M7 Error: " + str(e))
    traceback.print_exc()
