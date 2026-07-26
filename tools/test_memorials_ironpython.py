# -*- coding: utf-8 -*-
import codecs
import traceback
import os

print("=== TESTING MEMORIAL SCRIPTS FOR IRONPYTHON / PYTHON 2 & 3 COMPATIBILITY ===")

_this_dir = os.path.dirname(os.path.abspath(__file__))
_proj_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
for sc in ["m8_memorial.py", "m8_memorial_esg.py", "m8_memorial_pluv.py"]:
    print("Testing script:", sc)
    try:
        sc_path = os.path.join(_proj_root, "tools", sc)
        with codecs.open(sc_path, "r", encoding="utf-8") as f:
            code = f.read()
        exec(code)
        print("  -> OK!")
    except Exception as ex:
        print("  -> ERROR:", ex)
        traceback.print_exc()
