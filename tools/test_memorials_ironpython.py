# -*- coding: utf-8 -*-
import codecs
import traceback

print("=== TESTING MEMORIAL SCRIPTS FOR IRONPYTHON / PYTHON 2 & 3 COMPATIBILITY ===")

for sc in ["m8_memorial.py", "m8_memorial_esg.py", "m8_memorial_pluv.py"]:
    print("Testing script:", sc)
    try:
        with codecs.open(r"c:\Users\Shadow\Documents\00 - Claude - Revit\tools\\" + sc, "r", encoding="utf-8") as f:
            code = f.read()
        exec(code)
        print("  -> OK!")
    except Exception as ex:
        print("  -> ERROR:", ex)
        traceback.print_exc()
