# -*- coding: utf-8 -*-
import os
import shutil

_this_dir = os.path.dirname(os.path.abspath(__file__))
_proj_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
print("Icon updater ready.")
