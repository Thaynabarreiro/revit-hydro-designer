# -*- coding: utf-8 -*-
from pyrevit import script
import hydro
output = script.get_output()
output.print_md("# Geração 3D Esgoto")
try:
    s = hydro.rodar("m6_rede_esgoto.py")
    output.print_md(hydro.bloco(s))
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
