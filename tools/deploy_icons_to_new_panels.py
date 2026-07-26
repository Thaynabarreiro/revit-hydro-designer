# -*- coding: utf-8 -*-
"""Deploy icons to new discipline panels."""
import os
import shutil

if "RAIZ" in globals():
    RAIZ = globals()["RAIZ"]
elif "__file__" in globals():
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    RAIZ = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
else:
    RAIZ = os.environ.get("HYDRO_PROJECT_ROOT", os.getcwd())
_proj_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
BASE_DIR = os.path.join(_proj_root, "revit-hydro-designer.extension", "Hydro.tab")

ASSETS_DIR = os.path.join(_proj_root, "data")

icon_config = os.path.join(_proj_root, "data", "icon_config.png")
icon_sizing = os.path.join(_proj_root, "data", "icon_sizing.png")

mapping = {
    r"1 Agua Fria e Quente.panel\1 Configurar.pushbutton": icon_config,
    r"1 Agua Fria e Quente.panel\2 Dimensionar AF_AQ.pushbutton": icon_sizing,
    r"1 Agua Fria e Quente.panel\3 Gerar 3D AF_AQ.pushbutton": icon_config,
    r"1 Agua Fria e Quente.panel\4 Pranchas AF_AQ.pushbutton": icon_config,
    r"1 Agua Fria e Quente.panel\5 Memorial AF_AQ.pushbutton": icon_config,
    
    r"2 Esgoto e Ventilacao.panel\1 Dimensionar ESG.pushbutton": icon_sizing,
    r"2 Esgoto e Ventilacao.panel\2 Gerar 3D ESG.pushbutton": icon_config,
    r"2 Esgoto e Ventilacao.panel\3 Pranchas ESG.pushbutton": icon_config,
    r"2 Esgoto e Ventilacao.panel\4 Memorial ESG.pushbutton": icon_config,
    
    r"3 Pluvial e Tratamento.panel\1 Dimensionar PLUV.pushbutton": icon_sizing,
    r"3 Pluvial e Tratamento.panel\2 Dimensionar TRAT.pushbutton": icon_sizing,
    r"3 Pluvial e Tratamento.panel\3 Dimensionar BOMBA.pushbutton": icon_sizing,
    r"3 Pluvial e Tratamento.panel\4 Memorial PLUV.pushbutton": icon_config,
    
    r"4 Ferramentas.panel\1 Auditoria.pushbutton": icon_config,
    r"4 Ferramentas.panel\2 Painel Web.pushbutton": icon_config,
}

for rel_path, src_img in mapping.items():
    btn_dir = os.path.join(BASE_DIR, rel_path)
    if os.path.isdir(btn_dir) and os.path.exists(src_img):
        dest_img = os.path.join(btn_dir, "icon.png")
        shutil.copy(src_img, dest_img)
        print("Copied icon to:", btn_dir)

print("Icons deployed successfully!")
