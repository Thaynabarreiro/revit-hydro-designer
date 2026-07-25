# -*- coding: utf-8 -*-
"""Gera o memorial de cálculo e abre no navegador.

Sai em HTML formatado para impressão: abra e use Ctrl+P para salvar em PDF.
Todo o texto vem de data/textos_memorial_<pais>.json — traduzir é copiar o
arquivo, sem tocar em código.
"""
import os
import webbrowser

from pyrevit import forms, script

import hydro

output = script.get_output()
output.print_md("# Memorial de cálculo")

if not hydro.ler_dado("dimensionamento.json"):
    forms.alert("Nenhum dimensionamento encontrado.\n\n"
                "Rode antes o botão *3 Dimensionar*.",
                title="Falta o dimensionamento", exitscript=True)

try:
    saida = hydro.rodar("m8_memorial.py")
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
    script.exit()

output.print_md(hydro.bloco(saida))

# a última linha útil do stdout traz o caminho do arquivo gerado
caminho = None
for linha in saida.splitlines():
    if linha.strip().lower().endswith(".html"):
        caminho = linha.strip()

if caminho and os.path.isfile(caminho):
    webbrowser.open("file:///" + caminho.replace("\\", "/"))
    output.print_md("---")
    output.print_md("Aberto no navegador. Use **Ctrl+P → Salvar como PDF**.")
else:
    output.print_md("---")
    output.print_md("Memorial gerado. Procure em `memoriais/` na pasta do projeto.")
