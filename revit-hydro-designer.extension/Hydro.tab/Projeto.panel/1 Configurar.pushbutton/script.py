#! python3
# -*- coding: utf-8 -*-
"""Formulario de configuracao do projeto hidrossanitario.

Le e grava data/config_projeto.json. E o unico lugar onde a engenheira
informa os dados que mudam de obra para obra.

Roda no engine CPython do pyRevit (nao passa pelo bridge), entao aqui
literais acentuados sao seguros.
"""
import codecs
import json
import os

from pyrevit import forms, script

import hydro

RAIZ = hydro.RAIZ
ARQ = hydro.caminho_dado("config_projeto.json")

output = script.get_output()


def ler():
    with codecs.open(ARQ, "r", encoding="utf-8") as f:
        return json.loads(f.read())


def gravar(d):
    with codecs.open(ARQ, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=2, ensure_ascii=False))


if not os.path.isfile(ARQ):
    forms.alert("Arquivo de configuração não encontrado:\n{}".format(ARQ),
                exitscript=True)

cfg = ler()
proj = cfg["projeto"]
oc = cfg["ocupacao"]
rv = cfg["reservacao"]

# ------------------------------------------------------------ formulário
# ComboBox recebe LISTA de strings, não dicionário: a variante com dicionário
# é frágil no engine CPython. O texto escolhido é traduzido de volta abaixo.
NORMAS = ["BR — NBR 5626", "FR — DTU 60.11"]
NORMA_PARA_PAIS = {"BR — NBR 5626": "BR", "FR — DTU 60.11": "FR"}

RESERVACOES = ["Superior (por gravidade)", "Inferior + superior (com recalque)"]
RESERVACAO_PARA_TIPO = {
    "Superior (por gravidade)": "superior",
    "Inferior + superior (com recalque)": "inferior_superior",
}

norma_atual = NORMAS[0] if proj.get("pais", "BR") == "BR" else NORMAS[1]
reserv_atual = RESERVACOES[0] if rv.get("tipo") == "superior" else RESERVACOES[1]

componentes = [
    forms.Label("PROJETO"),
    forms.TextBox("nome", Text=str(proj.get("nome", ""))),
    forms.Label("Cidade (usada para pluviometria)"),
    forms.TextBox("cidade", Text=str(proj.get("cidade", ""))),

    forms.Label("Norma"),
    forms.ComboBox("norma", NORMAS, default=norma_atual),

    forms.Separator(),
    forms.Label("OCUPAÇÃO"),
    forms.Label("Pessoas por dormitório"),
    forms.TextBox("pessoas_dorm", Text=str(oc.get("pessoas_por_dormitorio", 2))),
    forms.Label("Moradores (deixe vazio para contar os dormitórios do modelo)"),
    forms.TextBox("moradores", Text=str(oc.get("moradores_override") or "")),
    forms.Label("Consumo per capita (L/hab.dia)"),
    forms.TextBox("percapita", Text=str(oc.get("consumo_per_capita_l_dia", 150))),

    forms.Separator(),
    forms.Label("RESERVAÇÃO"),
    forms.Label("Dias de reserva"),
    forms.TextBox("dias", Text=str(rv.get("dias_reserva", 2))),
    forms.Label("Tipo de reservação"),
    forms.ComboBox("tipo_res", RESERVACOES, default=reserv_atual),
    forms.Label("Reserva de incêndio (L) — 0 se não houver"),
    forms.TextBox("incendio", Text=str(rv.get("reserva_incendio_l", 0))),

    forms.Separator(),
    forms.Button("Salvar configuração"),
]

r = forms.FlexForm("Configuração do Projeto — Hydro", componentes)
if not r.show():
    script.exit()

v = r.values


def num(chave, padrao, inteiro=True):
    txt = str(v.get(chave, "")).strip().replace(",", ".")
    if not txt:
        return padrao
    try:
        return int(float(txt)) if inteiro else float(txt)
    except ValueError:
        return padrao


proj["nome"] = str(v.get("nome", "")).strip() or proj.get("nome", "")
proj["cidade"] = str(v.get("cidade", "")).strip()
proj["pais"] = NORMA_PARA_PAIS.get(v.get("norma"), "BR")
proj["norma"] = "NBR" if proj["pais"] == "BR" else "DTU"

oc["pessoas_por_dormitorio"] = num("pessoas_dorm", 2)
mor = str(v.get("moradores", "")).strip()
oc["moradores_override"] = num("moradores", None) if mor else None
oc["consumo_per_capita_l_dia"] = num("percapita", 150)

rv["dias_reserva"] = num("dias", 2)
rv["tipo"] = RESERVACAO_PARA_TIPO.get(v.get("tipo_res"), "superior")
rv["reserva_incendio_l"] = num("incendio", 0)

gravar(cfg)

# ------------------------------------------------------------- resumo
output.print_md("# Configuração salva")
output.print_md("")
output.print_md("| Campo | Valor |")
output.print_md("|---|---|")
output.print_md("| Projeto | {} |".format(proj["nome"]))
output.print_md("| Cidade | {} |".format(proj["cidade"] or "—"))
output.print_md("| Norma | {} |".format(proj["norma"]))
output.print_md("| Pessoas/dormitório | {} |".format(oc["pessoas_por_dormitorio"]))
output.print_md("| Moradores | {} |".format(
    oc["moradores_override"] or "automático (conta os dormitórios)"))
output.print_md("| Consumo per capita | {} L/hab.dia |".format(
    oc["consumo_per_capita_l_dia"]))
output.print_md("| Dias de reserva | {} |".format(rv["dias_reserva"]))
output.print_md("| Tipo de reservação | {} |".format(rv["tipo"]))
output.print_md("")
output.print_md("Peças complementares continuam em `data/config_projeto.json` "
                "(máquina de lavar, torneira de jardim...).")
output.print_md("")
output.print_md("**Próximo passo:** botão *2 Levantar*.")
