# -*- coding: utf-8 -*-
"""Deploy original high-res icons to all pyRevit pushbutton directories."""
import os
import shutil

_this_dir = os.path.dirname(os.path.abspath(__file__))
_proj_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
TAB_DIR = os.path.join(_proj_root, "revit-hydro-designer.extension", "Hydro.tab")

BRAIN_DIR = r"C:\Users\Shadow\.gemini\antigravity\brain\e3b196de-8f9c-4bcc-bba7-50de642ce1f8"

# Available source icons
icon_config = os.path.join(BRAIN_DIR, "icon_config_v2_1785066286289.jpg")
icon_reader = os.path.join(BRAIN_DIR, "icon_reader_v2_1785066294907.jpg")
icon_sizing = os.path.join(BRAIN_DIR, "icon_sizing_v2_1785066304339.jpg")
icon_placement = os.path.join(BRAIN_DIR, "icon_placement_v2_1785066313302.jpg")
icon_network = os.path.join(BRAIN_DIR, "icon_network_v2_1785066323342.jpg")
icon_audit = os.path.join(BRAIN_DIR, "icon_audit_1785061361288.jpg")
icon_report = os.path.join(BRAIN_DIR, "icon_report_1785061353456.jpg")

mapping = {
    r"1 Agua Fria e Quente.panel\1 Configurar.pushbutton": icon_config,
    r"1 Agua Fria e Quente.panel\2 Dimensionar AF_AQ.pushbutton": icon_sizing,
    r"1 Agua Fria e Quente.panel\3 Gerar 3D AF_AQ.pushbutton": icon_network,
    r"1 Agua Fria e Quente.panel\4 Pranchas AF_AQ.pushbutton": icon_placement,
    r"1 Agua Fria e Quente.panel\5 Memorial AF_AQ.pushbutton": icon_report,
    
    r"2 Esgoto e Ventilacao.panel\1 Dimensionar ESG.pushbutton": icon_sizing,
    r"2 Esgoto e Ventilacao.panel\2 Gerar 3D ESG.pushbutton": icon_network,
    r"2 Esgoto e Ventilacao.panel\3 Pranchas ESG.pushbutton": icon_placement,
    r"2 Esgoto e Ventilacao.panel\4 Memorial ESG.pushbutton": icon_report,
    
    r"3 Pluvial e Tratamento.panel\1 Dimensionar PLUV.pushbutton": icon_sizing,
    r"3 Pluvial e Tratamento.panel\2 Dimensionar TRAT.pushbutton": icon_sizing,
    r"3 Pluvial e Tratamento.panel\3 Dimensionar BOMBA.pushbutton": icon_sizing,
    r"3 Pluvial e Tratamento.panel\4 Pranchas PLUV.pushbutton": icon_placement,
    r"3 Pluvial e Tratamento.panel\5 Memorial PLUV.pushbutton": icon_report,
    
    r"4 Ferramentas.panel\1 Auditoria.pushbutton": icon_audit,
    r"4 Ferramentas.panel\2 Painel Web.pushbutton": icon_network,
}

copied = 0
for rel_path, src_img in mapping.items():
    btn_dir = os.path.join(TAB_DIR, rel_path)
    if os.path.isdir(btn_dir) and os.path.exists(src_img):
        dest_png = os.path.join(btn_dir, "icon.png")
        shutil.copy(src_img, dest_png)
        copied += 1
        print("Copied icon to:", dest_png)

print("Total icons deployed:", copied)
