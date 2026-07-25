# -*- coding: utf-8 -*-
"""Gera a rede de água fria e conecta as peças.

Topologia de barrilete real: coluna vertical, espinha em dois ramos a partir
da prumada, ramais perpendiculares por faixa e descidas até cada peça. Todo
encontro fica em 90°, que é o que permite ao Revit inserir tês e joelhos.

É idempotente: apaga a rede anterior antes de recriar.
"""
from pyrevit import forms, script

import hydro

output = script.get_output()
output.print_md("# Geração da rede")

if not hydro.ler_dado("dimensionamento.json"):
    forms.alert("Nenhum dimensionamento encontrado.\n\n"
                "Rode antes o botão *3 Dimensionar*.",
                title="Falta o dimensionamento", exitscript=True)

if not forms.alert("A rede de água fria existente será apagada e recriada.\n\n"
                   "As peças não são afetadas.",
                   title="Gerar rede", ok=False, yes=True, no=True):
    script.exit()

try:
    saida = hydro.rodar("m6g_rede_final.py")
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
    script.exit()

output.print_md(hydro.bloco(saida))
output.print_md("---")
output.print_md("Rode o botão *3 Dimensionar* de novo para verificar a pressão "
                "sobre a geometria criada, e depois *6 Memorial*.")
