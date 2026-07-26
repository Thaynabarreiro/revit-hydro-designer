# -*- coding: utf-8 -*-
import os, webbrowser
from pyrevit import script
import hydro
output = script.get_output()
output.print_md("# Memorial Pluvial")
try:
    s = hydro.rodar("m8_memorial_pluv.py")
    output.print_md(hydro.bloco(s))
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
