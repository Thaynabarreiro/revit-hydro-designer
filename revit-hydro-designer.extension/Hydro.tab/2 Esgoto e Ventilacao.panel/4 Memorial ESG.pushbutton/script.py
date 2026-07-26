# -*- coding: utf-8 -*-
import os, webbrowser
from pyrevit import script
import hydro
output = script.get_output()
output.print_md("# Memorial Sanitário")
try:
    s = hydro.rodar("m8_memorial_esg.py")
    output.print_md(hydro.bloco(s))
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
