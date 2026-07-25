# -*- coding: utf-8 -*-
"""M8 - Gerador de memorial de calculo.

Le data/dimensionamento.json + data/textos_memorial_<pais>.json e gera um
memorial em HTML formatado para impressao (Ctrl+P -> Salvar como PDF).

IMPORTANTE - por que nenhum texto acentuado aparece neste arquivo:
o bridge do pyRevit Routes entrega o codigo ao exec() como unicode, e os
literais acentuados do script sao remontados errado, gerando dupla codificacao
("CAlculo" vira "CA(c)lculo" no navegador). Texto lido de JSON via codecs nao
sofre disso. Entao TODO texto visivel vive em data/textos_memorial_*.json.
Efeito colateral bem-vindo: traduzir para frances e copiar o arquivo.
"""
import codecs
import json
import os
from datetime import datetime

RAIZ = "C:/Users/Shadow/Documents/00 - Claude - Revit"
D = os.path.join(RAIZ, "data")
SAIDA = os.path.join(RAIZ, "memoriais")


def ler_json(caminho):
    f = codecs.open(caminho, "r", encoding="utf-8")
    dados = json.loads(f.read())
    f.close()
    return dados


R = ler_json(os.path.join(D, "dimensionamento.json"))

proj = R["projeto"]
oc = R["ocupacao"]
res = R["reservacao"]
af = R["agua_fria"]
hid = R["hidrometro"]
pre = R["pressao"]

CFGP = ler_json(os.path.join(D, "config_projeto.json"))
RESP = CFGP.get("responsavel_tecnico", {"nome": "", "titulo": ""})

pais = proj.get("pais", "BR").lower()
T = ler_json(os.path.join(D, "textos_memorial_" + pais + ".json"))

hoje = datetime.now().strftime("%d/%m/%Y")

CSS = """
@page { size: A4; margin: 22mm 18mm; }
* { box-sizing: border-box; }
body { font-family: Calibri, 'Segoe UI', Arial, sans-serif; font-size: 10.5pt;
       color: #1a1a1a; line-height: 1.55; margin: 0; padding: 24px; max-width: 900px; }
h1 { font-size: 19pt; margin: 0 0 4px; color: #0f3d5c; }
h2 { font-size: 13pt; margin: 26px 0 8px; color: #0f3d5c;
     border-bottom: 2px solid #0f3d5c; padding-bottom: 3px; }
h3 { font-size: 11pt; margin: 16px 0 6px; color: #22546f; }
.sub { color: #55606a; font-size: 10pt; margin-bottom: 18px; }
.capa { border: 1px solid #c9d3da; border-left: 5px solid #0f3d5c;
        padding: 18px 20px; margin-bottom: 22px; background: #f7fafc; }
.capa table { border: 0; margin: 0; }
.capa td { border: 0; padding: 2px 14px 2px 0; }
.capa td:first-child { color: #55606a; width: 160px; }
table { border-collapse: collapse; width: 100%; margin: 10px 0 14px; font-size: 9.8pt; }
th { background: #0f3d5c; color: #fff; text-align: left; padding: 6px 9px; font-weight: 600; }
td { border-bottom: 1px solid #dde4e9; padding: 5px 9px; }
tr:nth-child(even) td { background: #f7fafc; }
.formula { background: #f2f6f8; border-left: 3px solid #6f97ad;
           padding: 9px 13px; margin: 9px 0; font-family: Consolas, monospace;
           font-size: 9.8pt; white-space: pre-wrap; }
.res { background: #e8f4ea; border-left: 3px solid #2e7d4f; padding: 9px 13px;
       margin: 9px 0; font-weight: 600; }
.aviso { background: #fff6e5; border-left: 3px solid #d08700; padding: 11px 14px;
         margin: 14px 0; font-size: 9.8pt; }
.assinatura { margin-top: 55px; padding-top: 7px; border-top: 1px solid #333;
              width: 320px; text-align: center; font-size: 9.8pt; }
.rodape { margin-top: 30px; padding-top: 9px; border-top: 1px solid #dde4e9;
          color: #77828b; font-size: 8.5pt; }
.tag { display: inline-block; padding: 1px 7px; border-radius: 9px; font-size: 8.5pt; }
.tag-m { background: #e3edf5; color: #24506e; }
.tag-c { background: #fdeede; color: #96590a; }
@media print { body { padding: 0; } h2 { page-break-after: avoid; }
               table { page-break-inside: avoid; } }
"""

h = []
a = h.append


def fmt(chave, **kw):
    """Texto do JSON com placeholders {x} substituidos."""
    txt = T[chave]
    for k, v in kw.items():
        txt = txt.replace("{" + k + "}", unicode(v))
    return txt


a('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">')
a('<title>' + T["titulo"] + ' - ' + proj["nome"] + '</title>')
a('<style>' + CSS + '</style></head><body>')

# ------------------------------------------------------------- capa
a('<h1>' + T["titulo"] + '</h1>')
a('<div class="sub">' + T["subtitulo"] + '</div>')
a('<div class="capa"><table>')
a('<tr><td>' + T["lbl_projeto"] + '</td><td><b>' + proj["nome"] + '</b></td></tr>')
a('<tr><td>' + T["lbl_localidade"] + '</td><td>' + proj.get("cidade", "-") + '</td></tr>')
a('<tr><td>' + T["lbl_norma"] + '</td><td>' + T["norma_nome"] + '</td></tr>')
a('<tr><td>' + T["lbl_data"] + '</td><td>' + hoje + '</td></tr>')
a('<tr><td>' + T["lbl_responsavel"] + '</td><td>' + fmt("responsavel", responsavel_nome=RESP["nome"], responsavel_titulo=RESP["titulo"]) + '</td></tr>')
a('</table></div>')

# ---------------------------------------------------------- objetivo
a('<h2>' + T["h_objetivo"] + '</h2>')
a('<p>' + fmt("p_objetivo", projeto=proj["nome"]) + '</p>')

# ------------------------------------------------------ metodologia
a('<h2>' + T["h_metodologia"] + '</h2>')
a('<p>' + T["p_metodologia_1"] + '</p>')
a('<p>' + T["p_metodologia_2"] + '</p>')

# --------------------------------------------------- dados do projeto
a('<h2>' + T["h_dados"] + '</h2>')
a('<table><tr><th>' + T["th_parametro"] + '</th><th>' + T["th_valor"] +
  '</th><th>' + T["th_origem"] + '</th></tr>')
a('<tr><td>' + T["lbl_dormitorios"] + '</td><td>' + str(len(oc["dormitorios"])) +
  '</td><td>' + ", ".join(oc["dormitorios"]) + '</td></tr>')
a('<tr><td>' + T["lbl_populacao"] + '</td><td>' + str(oc["moradores"]) + ' ' +
  T["txt_pessoas"] + '</td><td>' + oc["origem"] + '</td></tr>')
a('<tr><td>' + T["lbl_percapita"] + '</td><td>' +
  str(oc["consumo_per_capita_l_dia"]) + ' L/hab.dia</td><td>' +
  T["txt_percapita_origem"] + '</td></tr>')
a('<tr><td>' + T["lbl_reserva"] + '</td><td>' + str(res["dias"]) + ' ' +
  T["txt_dias"] + '</td><td>' + T["txt_reserva_origem"] + '</td></tr>')
a('</table>')

# --------------------------------------------- pontos de consumo
a('<h2>' + T["h_levantamento"] + '</h2>')
a('<table><tr><th>' + T["th_ambiente"] + '</th><th>' + T["th_peca"] +
  '</th><th>' + T["th_vazao"] + '</th><th>' + T["th_peso"] + '</th><th>' +
  T["th_pressao_min"] + '</th><th>' + T["th_origem"] + '</th></tr>')

pontos = sorted(R["pontos_consumo"], key=lambda p: (p["ambiente"], p["tipo_peca"]))
for p in pontos:
    if p.get("origem") == "complementar":
        tag = '<span class="tag tag-c">' + T["tag_complementar"] + '</span>'
    else:
        tag = '<span class="tag tag-m">' + T["tag_modelo"] + '</span>'
    a('<tr><td>' + p["ambiente"] + '</td><td>' + p.get("desc", p["tipo_peca"]) +
      '</td><td>' + str(p["vazao_ls"]) + '</td><td>' + str(p["peso"]) +
      '</td><td>' + str(p["pressao_min_kpa"]) + '</td><td>' + tag + '</td></tr>')

a('<tr><td colspan="3"><b>' + T["th_total"] + '</b></td><td><b>' +
  str(af["peso_total"]) + '</b></td><td colspan="2"><b>' + str(af["n_pontos"]) +
  ' ' + T["txt_pontos"] + '</b></td></tr>')
a('</table>')

compl = [p for p in pontos if p.get("origem") == "complementar"]
if compl:
    a('<div class="aviso">' + T["aviso_complementares"] + '<ul>')
    for c in compl:
        a('<li>' + c.get("desc", c["tipo_peca"]) + ' &mdash; ' + c["ambiente"] +
          ' (' + c.get("motivo", "") + ')</li>')
    a('</ul></div>')

# ------------------------------------------------ consumo e reservacao
a('<h2>' + T["h_consumo"] + '</h2>')
a('<h3>' + T["h_consumo_diario"] + '</h3>')
a('<div class="formula">CD = P x q\nCD = ' + str(oc["moradores"]) + ' hab x ' +
  str(oc["consumo_per_capita_l_dia"]) + ' L/hab.dia</div>')
a('<div class="res">' + fmt("res_consumo", cd=oc["consumo_diario_l"]) + '</div>')

a('<h3>' + T["h_volume"] + '</h3>')
a('<div class="formula">V = CD x n\nV = ' + str(oc["consumo_diario_l"]) +
  ' L/dia x ' + str(res["dias"]) + '</div>')
a('<div class="res">' + fmt("res_volume", vn=res["volume_necessario_l"],
                            va=res["volume_adotado_l"]) + '</div>')
if res["tipo"] == "inferior_superior":
    a('<p>' + fmt("p_reserv_duplo", sup=res["volume_superior_l"],
                  inf=res["volume_inferior_l"]) + '</p>')
else:
    a('<p>' + T["p_reserv_superior"] + '</p>')

# ------------------------------------------------------ vazao
a('<h2>' + T["h_vazao"] + '</h2>')
a('<p>' + T["p_vazao"] + '</p>')
a('<div class="formula">Q = C x raiz(soma dos pesos)\nQ = ' + str(af["coef_C"]) +
  ' x raiz(' + str(af["peso_total"]) + ')</div>')
a('<div class="res">Q = ' + str(af["vazao_projeto_ls"]) + ' L/s = ' +
  str(af["vazao_projeto_m3h"]) + ' m3/h</div>')

# -------------------------------------------------- hidrometro / ramal
a('<h2>' + T["h_hidrometro"] + '</h2>')
a('<h3>' + T["h_hidrometro_sub"] + '</h3>')
a('<p>' + T["p_hidrometro"] + '</p>')
a('<div class="res">' + fmt("res_hidrometro", nome=hid["nome"], dn=hid["dn_mm"]) +
  '</div>')

a('<h3>' + T["h_ramal"] + '</h3>')
a('<div class="formula">D = raiz(4Q / pi.v)\nQ = ' + str(af["vazao_projeto_ls"]) +
  ' L/s   |   v_max = 3,0 m/s</div>')
a('<div class="res">' + fmt("res_ramal", dt=af["diametro_teorico_mm"],
                            da=af["diametro_ramal_mm"],
                            v=af["velocidade_real_ms"]) + '</div>')

# ------------------------------------------------------ sub-ramais
a('<h2>' + T["h_subramais"] + '</h2>')
a('<table><tr><th>' + T["th_ambiente"] + '</th><th>' + T["th_pecas"] +
  '</th><th>' + T["th_soma_pesos"] + '</th><th>' + T["th_vazao"] + '</th><th>' +
  T["th_dn"] + '</th></tr>')
for s in R["sub_ramais"]:
    a('<tr><td>' + s["ambiente"] + '</td><td>' + str(s["n_pecas"]) + '</td><td>' +
      str(s["peso"]) + '</td><td>' + str(s["vazao_ls"]) + '</td><td>' +
      str(s["diametro_mm"]) + '</td></tr>')
a('</table>')

# ------------------------------------------------------- pressao
a('<h2>' + T["h_pressao"] + '</h2>')
a('<p>' + fmt("p_pressao", kpa=pre["min_exigida_kpa"], mca=pre["altura_min_m"]) + '</p>')
a('<div class="res">' + fmt("res_pressao", mca=pre["altura_min_m"]) + '</div>')

# ------------------------------------------------------- ressalvas
a('<h2>' + T["h_ressalvas"] + '</h2>')
a('<div class="aviso">')
a('<p>' + T["ressalva_escopo"] + '</p>')
a('<p>' + T["ressalva_altura"] + '</p>')
a('<p>' + T["ressalva_responsabilidade"] + '</p>')
a('</div>')

a('<div class="assinatura">' + fmt("assinatura_nome", responsavel_nome=RESP["nome"]) + '<br>' +
  fmt("assinatura_cargo", responsavel_titulo=RESP["titulo"]) + '</div>')
a('<div class="rodape">' + T["rodape"] + ' &middot; ' + hoje + '</div>')
a('</body></html>')

if not os.path.isdir(SAIDA):
    os.makedirs(SAIDA)

nome_arq = "Memorial_AguaFria_" + proj["nome"].replace(" ", "_").replace("&", "e") + ".html"
destino = os.path.join(SAIDA, nome_arq)

fo = codecs.open(destino, "w", encoding="utf-8")
fo.write("\n".join(h))
fo.close()

print("Memorial gerado:")
print("  " + destino)
print("")
print("idioma: " + T["_idioma"])
print("conteudo: {0} pontos, {1} sub-ramais, reservatorio {2} L".format(
    af["n_pontos"], len(R["sub_ramais"]), res["volume_adotado_l"]))
