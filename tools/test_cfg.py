# -*- coding: utf-8 -*-
"""Test loading 1 Configurar script."""
import codecs, json, os

_this_dir = os.path.dirname(os.path.abspath(__file__))
_auto_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
RAIZ = globals().get("RAIZ", os.environ.get("HYDRO_PROJECT_ROOT", _auto_root))
cfg_path = os.path.join(RAIZ, "data", "config_projeto.json")

print("Checking config_projeto.json path:", os.path.isfile(cfg_path))
with codecs.open(cfg_path, "r", encoding="utf-8") as f:
    cfg = json.loads(f.read())

print("Config read OK:", cfg["projeto"]["nome"])
