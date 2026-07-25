# -*- coding: utf-8 -*-
"""Infraestrutura compartilhada pelos botões da aba Hydro.

Os módulos em `tools/` foram escritos para o bridge do pyRevit Routes, que
executa IronPython 2.7 com o `doc` injetado. Os botões rodam em CPython 3.12.
Em vez de manter duas versões de cada cálculo, este módulo executa o mesmo
arquivo dentro de um namespace preparado:

- injeta `doc`, `uidoc`, `DB` e `revit`
- injeta `RAIZ`, descoberta a partir da localização desta extensão, para que
  os scripts não dependam de caminho fixo
- fornece `unicode` (que não existe em Python 3) para o código escrito para
  IronPython continuar válido
- captura o stdout e devolve como texto
"""
import io
import json
import os
import sys

from pyrevit import revit

# .../<raiz>/revit-hydro-designer.extension/lib/hydro.py
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS = os.path.join(RAIZ, "tools")
DATA = os.path.join(RAIZ, "data")


class ErroDeFerramenta(Exception):
    """Falha ao executar um script de tools/, com o stdout já capturado."""

    def __init__(self, mensagem, saida=""):
        Exception.__init__(self, mensagem)
        self.saida = saida


def caminho_dado(nome):
    return os.path.join(DATA, nome)


def ler_dado(nome, padrao=None):
    caminho = caminho_dado(nome)
    if not os.path.isfile(caminho):
        return padrao
    with io.open(caminho, "r", encoding="utf-8") as f:
        return json.loads(f.read())


def rodar(nome_script):
    """Executa tools/<nome_script> e devolve o stdout como texto.

    Levanta ErroDeFerramenta preservando o que já tinha sido impresso — sem
    isso, uma falha no meio do cálculo esconde as linhas que explicam onde parou.
    """
    caminho = os.path.join(TOOLS, nome_script)
    if not os.path.isfile(caminho):
        raise ErroDeFerramenta("Script não encontrado: {}".format(caminho))

    with io.open(caminho, "r", encoding="utf-8") as f:
        codigo = f.read()

    from Autodesk.Revit import DB

    ns = {
        "__name__": "__main__",
        "doc": revit.doc,
        "uidoc": revit.uidoc,
        "DB": DB,
        "revit": revit,
        "RAIZ": RAIZ,
        "unicode": str,          # o código de tools/ foi escrito para IronPython
    }

    antigo, captura = sys.stdout, io.StringIO()
    sys.stdout = captura
    try:
        exec(compile(codigo, caminho, "exec"), ns)
    except Exception as e:
        sys.stdout = antigo
        raise ErroDeFerramenta("{}: {}".format(type(e).__name__, e),
                               captura.getvalue())
    finally:
        sys.stdout = antigo

    return captura.getvalue()


def bloco(saida):
    """Formata o stdout de uma ferramenta como bloco de código markdown."""
    return "```\n" + (saida or "(sem saída)").rstrip() + "\n```"


def relatar_erro(output, erro):
    """Imprime uma falha de ferramenta de forma legível na janela do pyRevit."""
    output.print_md("## Falhou")
    output.print_md("`{}`".format(erro))
    if getattr(erro, "saida", ""):
        output.print_md("O que chegou a rodar antes de parar:")
        output.print_md(bloco(erro.saida))
