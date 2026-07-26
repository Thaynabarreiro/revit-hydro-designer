# -*- coding: utf-8 -*-
"""Script to create and configure individual discipline pyRevit pushbuttons."""
import os
import shutil

BASE_DIR = r"c:\Users\Shadow\Documents\00 - Claude - Revit\revit-hydro-designer.extension\Hydro.tab"

def create_button(panel, name, title, tooltip, script_content, src_icon):
    btn_dir = os.path.join(BASE_DIR, panel, name + ".pushbutton")
    os.makedirs(btn_dir, exist_ok=True)
    
    # Write script.py
    with open(os.path.join(btn_dir, "script.py"), "w", encoding="utf-8") as f:
        f.write(script_content)
        
    # Write bundle.yaml
    bundle_yaml = 'title: "{0}"\ntooltip: "{1}"\nauthor: "Thayna Barreiro"\n'.format(title, tooltip)
    with open(os.path.join(btn_dir, "bundle.yaml"), "w", encoding="utf-8") as f:
        f.write(bundle_yaml)
        
    # Copy icon
    if os.path.exists(src_icon):
        shutil.copy(src_icon, os.path.join(btn_dir, "icon.png"))
        
    print("Created button:", btn_dir)

icon_sizing = os.path.join(BASE_DIR, r"Calculo.panel\3 Dimensionar.pushbutton\icon.png")
icon_network = os.path.join(BASE_DIR, r"Modelo.panel\5 Gerar rede.pushbutton\icon.png")
icon_report = os.path.join(BASE_DIR, r"Documentos.panel\6 Memorial.pushbutton\icon.png")

# --- CALCULO PANEL ---
create_button("Calculo.panel", "Dim AF", "Dimensionar\nÁgua Fria", "Dimensionamento de Água Fria conforme NBR 5626",
"""# -*- coding: utf-8 -*-
from pyrevit import script, forms
import hydro
output = script.get_output()
output.print_md("# Dimensionamento de Água Fria (NBR 5626)")
try:
    hydro.rodar("m2_dimensionamento.py")
    hydro.rodar("m9_perda_carga.py")
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
""", icon_sizing)

create_button("Calculo.panel", "Dim AQ", "Dimensionar\nÁgua Quente", "Dimensionamento de Água Quente conforme NBR 7198",
"""# -*- coding: utf-8 -*-
from pyrevit import script, forms
import hydro
output = script.get_output()
output.print_md("# Dimensionamento de Água Quente (NBR 7198)")
try:
    hydro.rodar("m2_dimensionamento_aq.py")
    hydro.rodar("m9_perda_carga_aq.py")
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
""", icon_sizing)

create_button("Calculo.panel", "Dim ESG", "Dimensionar\nEsgoto", "Dimensionamento de Esgoto e Ventilação conforme NBR 8160",
"""# -*- coding: utf-8 -*-
from pyrevit import script, forms
import hydro
output = script.get_output()
output.print_md("# Dimensionamento de Esgoto e Ventilação (NBR 8160)")
try:
    hydro.rodar("m2_dimensionamento_esg.py")
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
""", icon_sizing)

create_button("Calculo.panel", "Dim PLUV", "Dimensionar\nPluvial", "Dimensionamento de Águas Pluviais conforme NBR 10844 / DTU 60.11",
"""# -*- coding: utf-8 -*-
from pyrevit import script, forms
import hydro
output = script.get_output()
output.print_md("# Dimensionamento de Águas Pluviais (NBR 10844)")
try:
    hydro.rodar("m2_dimensionamento_pluv.py")
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
""", icon_sizing)

create_button("Calculo.panel", "Dim TRAT", "Dimensionar\nTratamento", "Dimensionamento de Tratamento no Lote (NBR 7229 / NBR 13969)",
"""# -*- coding: utf-8 -*-
from pyrevit import script, forms
import hydro
output = script.get_output()
output.print_md("# Dimensionamento de Tratamento no Lote (NBR 7229/13969)")
try:
    hydro.rodar("m2_dimensionamento_trat.py")
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
""", icon_sizing)

create_button("Calculo.panel", "Dim BOMBA", "Dimensionar\nMoto-Bomba", "Dimensionamento de Conjunto Moto-Bomba de Recalque",
"""# -*- coding: utf-8 -*-
from pyrevit import script, forms
import hydro
output = script.get_output()
output.print_md("# Dimensionamento de Moto-Bomba de Recalque")
try:
    hydro.rodar("m2_dimensionamento_bomba.py")
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
""", icon_sizing)

# --- MODELO PANEL ---
create_button("Modelo.panel", "Rede AF", "Gerar 3D\nÁgua Fria", "Gera a rede 3D de Água Fria no Revit",
"""# -*- coding: utf-8 -*-
from pyrevit import script, forms
import hydro
output = script.get_output()
output.print_md("# Geração da Rede 3D de Água Fria")
try:
    saida = hydro.rodar("m6g_rede_final.py")
    output.print_md(hydro.bloco(saida))
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
""", icon_network)

create_button("Modelo.panel", "Rede AQ", "Gerar 3D\nÁgua Quente", "Gera a rede 3D de Água Quente no Revit",
"""# -*- coding: utf-8 -*-
from pyrevit import script, forms
import hydro
output = script.get_output()
output.print_md("# Geração da Rede 3D de Água Quente")
try:
    saida = hydro.rodar("m6_rede_agua_quente.py")
    output.print_md(hydro.bloco(saida))
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
""", icon_network)

create_button("Modelo.panel", "Rede ESG", "Gerar 3D\nEsgoto", "Gera a rede 3D de Esgoto e Ventilação no Revit",
"""# -*- coding: utf-8 -*-
from pyrevit import script, forms
import hydro
output = script.get_output()
output.print_md("# Geração da Rede 3D de Esgoto")
try:
    saida = hydro.rodar("m6_rede_esgoto.py")
    output.print_md(hydro.bloco(saida))
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
""", icon_network)

# --- DOCUMENTOS PANEL ---
create_button("Documentos.panel", "Memoriais AF", "Memorial\nÁgua Fria", "Gera o memorial de Água Fria (NBR 5626)",
"""# -*- coding: utf-8 -*-
import os, webbrowser
from pyrevit import script
import hydro
output = script.get_output()
output.print_md("# Memorial de Água Fria")
try:
    saida = hydro.rodar("m8_memorial.py")
    output.print_md(hydro.bloco(saida))
    webbrowser.open("file:///" + os.path.join(hydro.RAIZ, "memoriais", "Memorial_AguaFria_Casa_AeR.html").replace("\\\\", "/"))
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
""", icon_report)

create_button("Documentos.panel", "Memoriais AQ", "Memorial\nÁgua Quente", "Gera o memorial de Água Quente (NBR 7198)",
"""# -*- coding: utf-8 -*-
import os, webbrowser
from pyrevit import script
import hydro
output = script.get_output()
output.print_md("# Memorial de Água Quente")
try:
    saida = hydro.rodar("m8_memorial_aq.py")
    output.print_md(hydro.bloco(saida))
    webbrowser.open("file:///" + os.path.join(hydro.RAIZ, "memoriais", "Memorial_AguaQuente_Casa_AeR.html").replace("\\\\", "/"))
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
""", icon_report)

create_button("Documentos.panel", "Memoriais ESG", "Memorial\nEsgoto", "Gera o memorial de Esgoto e Ventilação (NBR 8160)",
"""# -*- coding: utf-8 -*-
import os, webbrowser
from pyrevit import script
import hydro
output = script.get_output()
output.print_md("# Memorial de Esgoto e Ventilação")
try:
    saida = hydro.rodar("m8_memorial_esg.py")
    output.print_md(hydro.bloco(saida))
    webbrowser.open("file:///" + os.path.join(hydro.RAIZ, "memoriais", "Memorial_Esgoto_Casa_AeR.html").replace("\\\\", "/"))
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
""", icon_report)

print("All individual discipline pushbuttons created successfully!")
