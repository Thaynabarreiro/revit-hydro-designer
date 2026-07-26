# -*- coding: utf-8 -*-
"""M8 AQ - Gerador de memorial de calculo de Agua Quente (NBR 7198).

Le: data/dimensionamento_aq.json + data/verificacao_pressao_aq.json
Gera: memoriais/Memorial_AguaQuente_<nome_projeto>.html
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


R_AQ = ler_json(os.path.join(D, "dimensionamento_aq.json"))
VP_AQ = ler_json(os.path.join(D, "verificacao_pressao_aq.json"))
CFGP = ler_json(os.path.join(D, "config_projeto.json"))
RESP = CFGP.get("responsavel_tecnico", {"nome": "", "titulo": ""})

proj = R_AQ["projeto"]
aq = R_AQ["agua_quente"]
hoje = datetime.now().strftime("%d/%m/%Y")

CSS = """
@page { size: A4; margin: 22mm 18mm; }
* { box-sizing: border-box; }
body { font-family: Calibri, 'Segoe UI', Arial, sans-serif; font-size: 10.5pt;
       color: #1a1a1a; line-height: 1.55; margin: 0; padding: 24px; max-width: 900px; }
h1 { font-size: 19pt; margin: 0 0 4px; color: #8c1d1d; }
h2 { font-size: 13pt; margin: 26px 0 8px; color: #8c1d1d;
     border-bottom: 2px solid #8c1d1d; padding-bottom: 3px; }
h3 { font-size: 11pt; margin: 16px 0 6px; color: #a33838; }
.sub { color: #55606a; font-size: 10pt; margin-bottom: 18px; }
.capa { border: 1px solid #dac9c9; border-left: 5px solid #8c1d1d;
        padding: 18px 20px; margin-bottom: 22px; background: #fdf8f8; }
.capa table { border: 0; margin: 0; }
.capa td { border: 0; padding: 2px 14px 2px 0; }
.capa td:first-child { color: #55606a; width: 160px; }
table { border-collapse: collapse; width: 100%; margin: 10px 0 14px; font-size: 9.8pt; }
th { background: #8c1d1d; color: #fff; text-align: left; padding: 6px 9px; font-weight: 600; }
td { border-bottom: 1px solid #eedded; padding: 5px 9px; }
tr:nth-child(even) td { background: #fdf8f8; }
.formula { background: #fdf3f3; border-left: 3px solid #b85c5c;
           padding: 9px 13px; margin: 9px 0; font-family: Consolas, monospace;
           font-size: 9.8pt; white-space: pre-wrap; }
.res { background: #f7e8e8; border-left: 3px solid #8c1d1d; padding: 9px 13px;
       margin: 9px 0; font-weight: 600; }
.aviso { background: #fff6e5; border-left: 3px solid #d08700; padding: 11px 14px;
          margin: 14px 0; font-size: 9.8pt; }
.assinatura { margin-top: 55px; padding-top: 7px; border-top: 1px solid #333;
              width: 320px; text-align: center; font-size: 9.8pt; }
.rodape { margin-top: 30px; padding-top: 9px; border-top: 1px solid #dde4e9;
          color: #77828b; font-size: 8.5pt; }
"""

h = []
a = h.append

a('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">')
a('<title>Memorial de Cálculo - Água Quente - ' + proj["nome"] + '</title>')
a('<style>' + CSS + '</style></head><body>')

# Capa
a('<h1>Memorial de Cálculo — Instalações Prediais de Água Quente</h1>')
a('<div class="sub">Dimensionamento e Verificação de Perda de Carga conforme NBR 7198 / NBR 5626</div>')
a('<div class="capa"><table>')
a('<tr><td>Projeto:</td><td><b>' + proj["nome"] + '</b></td></tr>')
a('<tr><td>Localidade:</td><td>' + proj.get("cidade", "-") + '</td></tr>')
a('<tr><td>Norma aplicada:</td><td>NBR 7198 — Projeto e execução de instalações prediais de água quente</td></tr>')
a('<tr><td>Data de emissão:</td><td>' + hoje + '</td></tr>')
a('<tr><td>Responsável técnico:</td><td>' + RESP["nome"] + ' (' + RESP["titulo"] + ')</td></tr>')
a('</table></div>')

# 1. Objetivo
a('<h2>1. Objetivo</h2>')
a('<p>Este documento apresenta o dimensionamento do sistema predial de água quente da edificação <b>' + proj["nome"] + '</b>, contemplando o levantamento dos pontos de consumo atendidos, a vazão de projeto por pesos relativos, a especificação da fonte de aquecimento e a verificação de pressão e perda de carga.</p>')

# 2. Fonte de Aquecimento
a('<h2>2. Fonte de Aquecimento</h2>')
a('<div class="res">Fonte de aquecimento adotada: ' + aq["fonte_aquecimento"].replace("_", " ").title() + '</div>')
a('<div class="formula">Potência nominal necessária: ' + str(aq["potencia_estimada_kw"]) + ' kW\n' +
  'Vazão de projeto de água quente (Q): ' + str(aq["vazao_projeto_ls"]) + ' L/s (' + str(aq["vazao_projeto_m3h"]) + ' m3/h)\n' +
  'Elevação de temperatura (Delta T): ' + str(aq["delta_t_c"]) + ' °C (Água a 60 °C no aquecedor / 40 °C na mistura)</div>')

# 3. Pontos de Consumo de Água Quente
a('<h2>3. Levantamento dos Pontos de Consumo de Água Quente</h2>')
a('<table><tr><th>Ambiente</th><th>Peça / Equipamento</th><th>Vazão (L/s)</th><th>Peso</th></tr>')
for p in R_AQ.get("pontos_consumo_aq", []):
    a('<tr><td>' + p["ambiente"] + '</td><td>' + p.get("desc", p["tipo_peca"]) + '</td><td>' + str(p["vazao_ls"]) + '</td><td>' + str(p["peso"]) + '</td></tr>')
a('<tr><td colspan="3"><b>Total de Pesos Água Quente (Σ P_aq)</b></td><td><b>' + str(aq["peso_total"]) + '</b></td></tr>')
a('</table>')

# 4. Verificação de Perda de Carga
a('<h2>4. Verificação de Perda de Carga e Pressão (Água Quente)</h2>')
a('<p>' + VP_AQ.get("formula", "") + '</p>')
a('<table><tr><th>Trecho / Peça</th><th>Ambiente</th><th>Vazão (L/s)</th><th>DN (mm)</th><th>Perda (mca)</th><th>Pressão Disp. (mca)</th><th>Situação</th></tr>')
for tr in VP_AQ.get("trechos_aq", []):
    sit = '<span style="color:#2e7d4f;font-weight:bold;">ATENDE</span>' if tr["atende"] else '<span style="color:#c0392b;font-weight:bold;">NÃO ATENDE</span>'
    a('<tr><td>' + tr["nome"] + ' (' + tr["peca"] + ')</td><td>' + tr["ambiente"] + '</td><td>' + str(tr["Q_ls"]) + '</td><td>' + str(tr["dn_mm"]) + '</td><td>' + str(tr["dH_mca"]) + '</td><td>' + str(tr["pressao_disponivel_mca"]) + '</td><td>' + sit + '</td></tr>')
a('</table>')

# Assinatura
a('<div class="assinatura">' + RESP["nome"] + '<br>' + RESP["titulo"] + '</div>')
a('<div class="rodape">Memorial de Água Quente gerado automaticamente a partir do modelo BIM — revit-hydro-designer &middot; ' + hoje + '</div>')
a('</body></html>')

if not os.path.isdir(SAIDA):
    os.makedirs(SAIDA)

destino = os.path.join(SAIDA, "Memorial_AguaQuente_" + proj["nome"].replace(" ", "_").replace("&", "e") + ".html")
fo = codecs.open(destino, "w", encoding="utf-8")
fo.write("\n".join(h))
fo.close()

print("Memorial de Agua Quente gerado com sucesso:")
print("  " + destino)
