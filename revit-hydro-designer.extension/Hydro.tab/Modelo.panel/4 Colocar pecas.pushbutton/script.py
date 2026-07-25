#! python3
# -*- coding: utf-8 -*-
"""Coloca as peças hidrossanitárias no modelo MEP.

Lê a arquitetura pelo vínculo e posiciona as famílias correspondentes no nível
certo. A partir daqui o modelo é seu: adicione, remova e mova à vontade. O
cálculo passa a ler o modelo MEP, não mais o vínculo.
"""
from pyrevit import forms, script

import hydro

output = script.get_output()
output.print_md("# Colocação das peças")

if not forms.alert("As peças serão colocadas no modelo aberto a partir do "
                   "vínculo da arquitetura.\n\n"
                   "Peças já existentes não são removidas — se rodar duas "
                   "vezes, haverá duplicatas.",
                   title="Colocar peças", ok=False, yes=True, no=True):
    script.exit()

try:
    saida = hydro.rodar("m5_colocar_pecas.py")
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
    script.exit()

output.print_md(hydro.bloco(saida))
output.print_md("---")
output.print_md("Revise o posicionamento no modelo. "
                "**Próximo passo:** botão *5 Gerar rede*.")
