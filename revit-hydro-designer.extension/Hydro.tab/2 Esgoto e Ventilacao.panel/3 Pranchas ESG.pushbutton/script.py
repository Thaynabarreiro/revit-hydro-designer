# -*- coding: utf-8 -*-
from pyrevit import script
import hydro
output = script.get_output()
output.print_md("# Geração Automática de Pranchas por Ambiente (ESG)")
try:
    s = hydro.rodar("m7_gerar_pranchas.py")
    output.print_md(hydro.bloco(s))
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
