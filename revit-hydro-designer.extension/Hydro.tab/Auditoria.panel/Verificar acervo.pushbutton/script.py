# -*- coding: utf-8 -*-
"""Verificação de acervo — o template tem o que este projeto vai precisar?

Roda antes de gerar qualquer coisa. Uma família ausente vira falha no meio da
geração ou, pior, peça errada colocada em silêncio. Aqui ela vira uma lista.
"""
from pyrevit import forms, script

import hydro

output = script.get_output()
output.print_md("# Verificação de acervo")

try:
    hydro.rodar("verificar_acervo.py")
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
    script.exit()

r = hydro.ler_dado("acervo.json", {})

output.print_md("**Modelo:** {}".format(r.get("modelo", "—")))
output.print_md("")
output.print_md("| | |")
output.print_md("|---|---|")
output.print_md("| Famílias de peça no modelo | {} |".format(r.get("familias_no_modelo", "—")))
output.print_md("| Mapeamentos resolvidos | {} |".format(len(r.get("ok", []))))
output.print_md("| **Faltando** | **{}** |".format(len(r.get("faltando", []))))
output.print_md("| Tipos de tubulação prontos | {} |".format(
    len(r.get("tipos_tubulacao_prontos", []))))
output.print_md("| Sistema de água fria | {} |".format(
    r.get("sistema_agua_fria") or "**não encontrado**"))

faltando = r.get("faltando", [])
if faltando:
    output.print_md("## Faltando no template")
    output.print_md("Carregue estas famílias antes de gerar, ou aponte "
                    "`data/familias_pecas.json` para as que você usa:")
    for item in faltando:
        output.print_md("- **{}** — esperava `{}`".format(
            item.get("peca"), item.get("esperado")))

avisos = r.get("avisos", [])
if avisos:
    output.print_md("## Avisos")
    for a in avisos:
        output.print_md("- {}".format(a))

incompletos = r.get("tipos_tubulacao_incompletos", [])
if incompletos:
    output.print_md("## Tipos de tubulação incompletos")
    output.print_md("Sem segmento e curvas nas *routing preferences*, o Revit "
                    "não consegue gerar rede com estes tipos:")
    for t in incompletos:
        output.print_md("- {}".format(t))

ausentes = r.get("parametros_ausentes", [])
if ausentes:
    output.print_md("## Parâmetros de cálculo ausentes")
    output.print_md("As famílias não expõem estes parâmetros, então vazão e "
                    "peso terão de vir da tabela normativa em vez do modelo:")
    for p in ausentes:
        output.print_md("- `{}`".format(p))

output.print_md("---")
if r.get("apto"):
    output.print_md("## Apto a gerar")
    output.print_md("O template tem o necessário para este projeto.")
else:
    output.print_md("## Não apto")
    forms.alert("O template não tem tudo que este projeto precisa.\n\n"
                "Veja o relatório: {} item(ns) faltando.".format(len(faltando)),
                title="Acervo incompleto")
