# -*- coding: utf-8 -*-
import traceback

try:
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    _proj_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
    m7_file = os.path.join(_proj_root, "tools", "m7_gerar_pranchas.py")
    with open(m7_file) as f:
        code = f.read()
    exec(code)
    print("M7 Executed SUCCESS!")
except Exception as e:
    print("M7 Error: " + str(e))
    traceback.print_exc()
