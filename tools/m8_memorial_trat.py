# -*- coding: utf-8 -*-
"""M8 TRAT - Gerador de memorial de calculo de Tratamento de Esgoto no Lote (NBR 7229 / 13969).

Le: data/dimensionamento_tratamento.json
Gera: memoriais/Memorial_Tratamento_<nome_projeto>.html
"""
import codecs
import json
import os
from datetime import datetime

_this_dir = os.path.dirname(os.path.abspath(__file__))
_auto_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
RAIZ = globals().get("RAIZ", os.environ.get("HYDRO_PROJECT_ROOT", _auto_root))
D = os.path.join(RAIZ, "data")
SAIDA = os.path.join(RAIZ, "memoriais")


def ler_json(caminho):
    f = codecs.open(caminho, "r", encoding="utf-8")
    dados = json.loads(f.read())
    f.close()
    return dados


R_TRAT = ler_json(os.path.join(D, "dimensionamento_tratamento.json"))
CFGP = ler_json(os.path.join(D, "config_projeto.json"))
RESP = CFGP.get("responsavel_tecnico", {"nome": "", "titulo": ""})

proj = R_TRAT["projeto"]
trat = R_TRAT["tratamento"]
fossa = trat["fossa_septica"]
filtro = trat["filtro_anaerobio"]
sumid = trat["sumidouro"]
hoje = datetime.now().strftime("%d/%m/%Y")

CSS = """
@page { size: A4; margin: 22mm 18mm; }
* { box-sizing: border-box; }
body { font-family: Calibri, 'Segoe UI', Arial, sans-serif; font-size: 10.5pt;
       color: #1a1a1a; line-height: 1.55; margin: 0; padding: 24px; max-width: 900px; }
h1 { font-size: 19pt; margin: 0 0 4px; color: #4a6b22; }
h2 { font-size: 13pt; margin: 26px 0 8px; color: #4a6b22;
     border-bottom: 2px solid #4a6b22; padding-bottom: 3px; }
h3 { font-size: 11pt; margin: 16px 0 6px; color: #354e17; }
.sub { color: #55606a; font-size: 10pt; margin-bottom: 18px; }
.capa { border: 1px solid #cadab5; border-left: 5px solid #4a6b22;
        padding: 18px 20px; margin-bottom: 22px; background: #fbfdf8; }
.capa table { border: 0; margin: 0; }
.capa td { border: 0; padding: 2px 14px 2px 0; }
.capa td:first-child { color: #55606a; width: 160px; }
table { border-collapse: collapse; width: 100%; margin: 10px 0 14px; font-size: 9.8pt; }
th { background: #4a6b22; color: #fff; text-align: left; padding: 6px 9px; font-weight: 600; }
td { border-bottom: 1px solid #e3eed7; padding: 5px 9px; }
tr:nth-child(even) td { background: #fbfdf8; }
.formula { background: #f6fdf0; border-left: 3px solid #7ab83c;
           padding: 9px 13px; margin: 9px 0; font-family: Consolas, monospace;
           font-size: 9.8pt; white-space: pre-wrap; }
.res { background: #eef7e5; border-left: 3px solid #4a6b22; padding: 9px 13px;
       margin: 9px 0; font-weight: 600; }
.assinatura { margin-top: 55px; padding-top: 7px; border-top: 1px solid #333;
              width: 320px; text-align: center; font-size: 9.8pt; }
.rodape { margin-top: 30px; padding-top: 9px; border-top: 1px solid #dde4e9;
          color: #77828b; font-size: 8.5pt; }
"""

h = []
a = h.append

a('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">')
a('<title>Memorial de Cálculo - Tratamento de Esgoto - ' + proj["nome"] + '</title>')
a('<style>' + CSS + '</style></head><body>')

# Capa
a('<h1>Memorial de Cálculo — Tratamento de Esgoto no Lote</h1>')
a('<div class="sub">Dimensionamento de Fossa Séptica, Filtro Anaeróbio e Sumidouro conforme NBR 7229 / NBR 13969</div>')
a('<div class="capa"><table>')
a('<tr><td>Projeto:</td><td><b>' + proj["nome"] + '</b></td></tr>')
a('<tr><td>Localidade:</td><td>' + proj.get("cidade", "-") + '</td></tr>')
a('<tr><td>Normas aplicadas:</td><td>NBR 7229 — Projeto e execução de fossas sépticas / NBR 13969 — Tanques sépticos e unidades de tratamento complementar</td></tr>')
a('<tr><td>Data de emissão:</td><td>' + hoje + '</td></tr>')
a('<tr><td>Responsável técnico:</td><td>' + RESP["nome"] + ' (' + RESP["titulo"] + ')</td></tr>')
a('</table></div>')

# 1. Objetivo
a('<h2>1. Objetivo</h2>')
a('<p>Este documento apresenta o dimensionamento do sistema de tratamento individual de esgoto sanitário para a edificação <b>' + proj["nome"] + '</b>, composto por Fossa Séptica (tratamento primário), Filtro Anaeróbio de fluxo ascendente (tratamento secundário) e Sumidouro (disposição final no solo).</p>')

# 2. Resumo de Capacidades
a('<h2>2. Unidades de Tratamento e Disposição Final</h2>')
a('<table><tr><th>Unidade de Tratamento</th><th>Norma</th><th>Volume / Área Calculada</th><th>Dimensão Adotada</th></tr>')
a('<tr><td>Fossa Séptica (Prismática / Circular)</td><td>NBR 7229</td><td>' + str(fossa["volume_calculado_l"]) + ' L</td><td><b>' + str(fossa["volume_adotado_l"]) + ' L</b> (DN ' + str(fossa["dn_adotado_mm"]) + ' mm)</td></tr>')
a('<tr><td>Filtro Anaeróbio (Fluxo Ascendente)</td><td>NBR 13969</td><td>' + str(filtro["volume_calculado_l"]) + ' L</td><td><b>' + str(filtro["volume_adotado_l"]) + ' L</b> (DN ' + str(filtro["dn_adotado_mm"]) + ' mm)</td></tr>')
a('<tr><td>Sumidouro / Poço de Infiltração</td><td>NBR 7229</td><td>' + str(sumid["area_infiltracao_necessaria_m2"]) + ' m2 de infiltração</td><td><b>DN ' + str(sumid["dn_adotado_mm"]) + ' mm x h = ' + str(sumid["profundidade_util_m"]) + ' m</b></td></tr>')
a('</table>')

# Assinatura
a('<div class="assinatura">' + RESP["nome"] + '<br>' + RESP["titulo"] + '</div>')
a('<div class="rodape">Memorial de Tratamento de Esgoto gerado automaticamente a partir do modelo BIM — revit-hydro-designer &middot; ' + hoje + '</div>')
a('</body></html>')

if not os.path.isdir(SAIDA):
    os.makedirs(SAIDA)

destino = os.path.join(SAIDA, "Memorial_Tratamento_" + proj["nome"].replace(" ", "_").replace("&", "e") + ".html")
fo = codecs.open(destino, "w", encoding="utf-8")
fo.write("\n".join(h))
fo.close()

print("Memorial de Tratamento de Esgoto gerado com sucesso:")
print("  " + destino)
