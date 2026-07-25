#! python3
# -*- coding: utf-8 -*-
"""Levantamento dos pontos de consumo — e a etapa de revisão humana.

Lê a arquitetura pelo vínculo, agrupa peças coincidentes e classifica cada
ponto. Depois mostra o que encontrou, o que agrupou e o que **inferiu**, para
a engenheira conferir antes de qualquer cálculo.

Este passo não é burocracia. Os dois erros reais já encontrados no projeto —
uma louça contada várias vezes por estar modelada em famílias aninhadas, e um
ambiente chamado "banho suíte" contado como dormitório — passariam despercebidos
sem ele.
"""
from pyrevit import forms, script

import hydro

output = script.get_output()
output.print_md("# Levantamento dos pontos de consumo")

try:
    saida = hydro.rodar("m1_reader.py")
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
    script.exit()

dados = hydro.ler_dado("pontos_consumo.json")
if not dados:
    output.print_md("O levantamento rodou mas não gerou `pontos_consumo.json`.")
    output.print_md(hydro.bloco(saida))
    script.exit()

resumo = dados.get("resumo", {})
pontos = dados.get("pontos_consumo", [])
revisar = dados.get("revisar", [])
ignorados = dados.get("ignorados", {})

# ------------------------------------------------------------- resumo
output.print_md("**Modelo vinculado:** {}".format(dados.get("modelo", "—")))
output.print_md("")
output.print_md("| | |")
output.print_md("|---|---|")
output.print_md("| Ambientes colocados | {} |".format(
    resumo.get("ambientes_colocados", "—")))
output.print_md("| Pontos de consumo | {} |".format(len(pontos)))
output.print_md("| Pendentes de revisão | {} |".format(len(revisar)))
output.print_md("| Soma dos pesos | {} |".format(resumo.get("peso_total", "—")))
output.print_md("| Vazão de projeto | {} L/s |".format(
    resumo.get("vazao_projeto_ls", "—")))

# ------------------------------------------------ pontos por ambiente
output.print_md("## Pontos encontrados")
por_ambiente = {}
for p in pontos:
    por_ambiente.setdefault(p.get("ambiente", "—"), []).append(p)

for ambiente in sorted(por_ambiente):
    output.print_md("**{}**".format(ambiente))
    linhas = []
    for p in por_ambiente[ambiente]:
        nota = []
        agrupadas = p.get("familias_agrupadas") or []
        if len(agrupadas) > 1:
            nota.append("agrupou {} famílias".format(len(agrupadas)))
        if p.get("confianca") == "inferido pelo ambiente":
            nota.append("**tipo inferido pelo nome do ambiente**")
        linhas.append("- {} — peso {}, vazão {} L/s{}".format(
            p.get("tipo_peca"), p.get("peso"), p.get("vazao_ls"),
            "  _({})_".format("; ".join(nota)) if nota else ""))
    output.print_md("\n".join(linhas))

# --------------------------------------------------- o que conferir
inferidos = [p for p in pontos if p.get("confianca") == "inferido pelo ambiente"]
agrupados = [p for p in pontos if len(p.get("familias_agrupadas") or []) > 1]

if inferidos or agrupados or revisar:
    output.print_md("## Confira antes de seguir")

if agrupados:
    output.print_md("**Peças agrupadas** — famílias próximas tratadas como um "
                    "único ponto. Se alguma dessas for de fato duas louças "
                    "distintas, o dimensionamento sairá pequeno:")
    for p in agrupados:
        output.print_md("- {} em {}: {}".format(
            p.get("tipo_peca"), p.get("ambiente"),
            ", ".join(p.get("familias_agrupadas"))))

if inferidos:
    output.print_md("**Tipo inferido pelo ambiente** — o nome da família não "
                    "bastou para classificar, então valeu o nome do ambiente:")
    for p in inferidos:
        output.print_md("- {} em {} (família: {})".format(
            p.get("tipo_peca"), p.get("ambiente"), p.get("familia")))

if revisar:
    output.print_md("**Não classificadas** — não entram no cálculo enquanto "
                    "não forem resolvidas em `data/pecas_br.json`:")
    for p in revisar:
        output.print_md("- {} :: {} em {} — {}".format(
            p.get("familia"), p.get("tipo_familia"),
            p.get("ambiente"), p.get("motivo")))

if ignorados:
    output.print_md("## Ignorados de propósito")
    for chave, qtd in sorted(ignorados.items()):
        output.print_md("- {} × {}".format(chave, qtd))

# ------------------------------------------------------- confirmação
output.print_md("## Peças complementares")
output.print_md("Peças que a arquitetura costuma não modelar (máquina de lavar, "
                "torneira de jardim) entram no cálculo pelo campo "
                "`pecas_complementares` de `data/config_projeto.json`, sem "
                "precisar alterar o modelo do arquiteto.")

if revisar:
    forms.alert("Levantamento concluído com {} peça(s) não classificada(s).\n\n"
                "Elas ficam fora do dimensionamento até serem resolvidas. "
                "Veja o relatório para os detalhes.".format(len(revisar)),
                title="Revisar antes de dimensionar")
else:
    output.print_md("---")
    output.print_md("Nenhuma pendência de classificação. "
                    "**Próximo passo:** botão *3 Dimensionar*.")
