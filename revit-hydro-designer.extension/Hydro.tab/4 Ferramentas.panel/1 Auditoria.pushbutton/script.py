# -*- coding: utf-8 -*-
from pyrevit import script
import hydro
output = script.get_output()
output.print_md("# Auditoria e BCL")
try:
    s = hydro.rodar("m0_audit_bridge.py")
    output.print_md(hydro.bloco(s))
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
