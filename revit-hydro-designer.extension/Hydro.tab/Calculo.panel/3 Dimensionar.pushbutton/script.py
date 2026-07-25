# -*- coding: utf-8 -*-
"""Dimensionamento completo: consumo, reservação, vazão, hidrômetro e pressão.

Roda o dimensionamento (M2) e, em seguida, a verificação de perda de carga (M9),
que é quem de fato manda nos diâmetros. O critério de velocidade praticamente
nunca é restritivo em residência.
"""
from pyrevit import forms, script

import hydro

output = script.get_output()
output.print_md("# Dimensionamento")

if not hydro.ler_dado("pontos_consumo.json"):
    forms.alert("Nenhum levantamento encontrado.\n\n"
                "Rode antes o botão *2 Levantar*.",
                title="Falta o levantamento", exitscript=True)

# ------------------------------------------------- M2: dimensionamento
try:
    hydro.rodar("m2_dimensionamento.py")
except hydro.ErroDeFerramenta as e:
    hydro.relatar_erro(output, e)
    script.exit()

dim = hydro.ler_dado("dimensionamento.json", {})
oc = dim.get("ocupacao", {})
rv = dim.get("reservacao", {})
af = dim.get("agua_fria", {})
hid = dim.get("hidrometro", {})

output.print_md("## Água fria")
output.print_md("| | |")
output.print_md("|---|---|")
output.print_md("| Dormitórios | {} |".format(", ".join(oc.get("dormitorios", [])) or "—"))
output.print_md("| População de projeto | {} |".format(oc.get("moradores", "—")))
output.print_md("| Consumo diário | {} L/dia |".format(oc.get("consumo_diario_l", "—")))
output.print_md("| Reservação ({} dia(s)) | {} L necessários → **{} L** adotados |".format(
    rv.get("dias", "—"), rv.get("volume_necessario_l", "—"),
    rv.get("volume_adotado_l", "—")))
output.print_md("| Pontos de consumo | {} |".format(af.get("n_pontos", "—")))
output.print_md("| Soma dos pesos | {} |".format(af.get("peso_total", "—")))
output.print_md("| Vazão de projeto | **{} L/s** ({} m³/h) |".format(
    af.get("vazao_projeto_ls", "—"), af.get("vazao_projeto_m3h", "—")))
output.print_md("| Hidrômetro | {} — DN {} mm |".format(
    hid.get("nome", "—"), hid.get("dn_mm", "—")))
output.print_md("| Ramal de entrada | DN {} mm (v = {} m/s) |".format(
    af.get("diametro_ramal_mm", "—"), af.get("velocidade_real_ms", "—")))

# --------------------------------------------------- M9: perda de carga
output.print_md("## Verificação de pressão")

tem_rede = True
try:
    hydro.rodar("m9_perda_carga.py")
except hydro.ErroDeFerramenta as e:
    tem_rede = False
    output.print_md("A verificação de pressão não pôde rodar. Ela precisa das "
                    "peças colocadas no modelo (botão *4 Colocar peças*).")
    output.print_md("`{}`".format(e))

if tem_rede:
    vp = hydro.ler_dado("verificacao_pressao.json", {})
    res = vp.get("resumo", {})
    fora = res.get("pecas_fora", 0)
    total = res.get("total", 0)

    output.print_md("| | |")
    output.print_md("|---|---|")
    output.print_md("| Peças verificadas | {} |".format(total))
    output.print_md("| Fora do critério | **{}** |".format(fora))
    output.print_md("| Diâmetros adotados | DN {} |".format(
        ", ".join(str(int(d)) for d in res.get("diametros_usados", []))))
    output.print_md("| Iterações de diâmetro | {} |".format(vp.get("iteracoes", "—")))
    output.print_md("| Altura do reservatório | {} m (mínima: **{} m**) |".format(
        vp.get("reservatorio_z_m", "—"), vp.get("reservatorio_z_min_m", "—")))

    pecas = vp.get("pecas", [])
    if pecas:
        criticas = sorted(pecas, key=lambda p: p.get("disponivel_mca", 0) -
                          p.get("exigida_mca", 0))[:3]
        output.print_md("**Peças com menor folga de pressão:**")
        for p in criticas:
            folga = p.get("disponivel_mca", 0) - p.get("exigida_mca", 0)
            output.print_md("- {} — disponível {} mca, exigida {} mca "
                            "(**folga {:.2f} mca**){}".format(
                                p.get("familia", "—"), p.get("disponivel_mca"),
                                p.get("exigida_mca"), folga,
                                "" if p.get("atende") else "  ⚠ **INSUFICIENTE**"))

    if fora:
        forms.alert("{} de {} peças não atendem à pressão mínima.\n\n"
                    "Os diâmetros comerciais disponíveis se esgotaram. "
                    "Considere elevar o reservatório ou revisar o traçado."
                    .format(fora, total), title="Pressão insuficiente")
    else:
        margem = vp.get("reservatorio_z_m", 0) - vp.get("reservatorio_z_min_m", 0)
        if margem < 0.30:
            output.print_md("---")
            output.print_md("Todas as peças atendem, mas a margem de altura do "
                            "reservatório é de apenas **{:.2f} m**. Vale decidir "
                            "conscientemente se aceita trabalhar tão perto do "
                            "limite.".format(margem))

output.print_md("---")
output.print_md("**Próximo passo:** botão *4 Colocar peças*, se ainda não colocou, "
                "ou *5 Gerar rede*.")
