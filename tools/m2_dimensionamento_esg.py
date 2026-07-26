# -*- coding: utf-8 -*-
"""M2 ESG - Dimensionamento de esgoto sanitario e ventilacao (NBR 8160).

Le:  data/pontos_consumo.json
     data/pecas_br.json
     data/config_projeto.json

Grava: data/dimensionamento_esg.json
"""
import codecs
import json
import math
import os

if "RAIZ" in globals():
    RAIZ = globals()["RAIZ"]
elif "__file__" in globals():
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    RAIZ = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
else:
    RAIZ = os.environ.get("HYDRO_PROJECT_ROOT", os.getcwd())
D = os.path.join(RAIZ, "data")


def ler(nome):
    f = codecs.open(os.path.join(D, nome), "r", encoding="utf-8")
    dados = json.loads(f.read())
    f.close()
    return dados


CONS = ler("pontos_consumo.json")
NORMA = ler("pecas_br.json")
CFG = ler("config_projeto.json")

TIPOS = NORMA["tipos"]

print("=== M2 ESG DIMENSIONAMENTO DE ESGOTO SANITARIO - " + CFG["projeto"]["nome"] + " ===")

pontos_esg = []
for p in CONS["pontos_consumo"]:
    tp = p["tipo_peca"]
    info_norma = TIPOS.get(tp, {})
    uhc = info_norma.get("esgoto_uhc", 1)
    dn_min = info_norma.get("diam_esgoto_mm", 40)
    
    if dn_min > 0 and uhc > 0:
        registro = dict(p)
        registro["uhc"] = uhc
        registro["dn_esgoto_mm"] = dn_min
        pontos_esg.append(registro)

print("pontos totais com esgoto: " + str(len(pontos_esg)))

# Agrupamento por ambiente (sub-colectores / caixas sifonadas / caixas de gordura)
por_amb = {}
for p in pontos_esg:
    por_amb.setdefault(p["ambiente"], []).append(p)

ambientes_esg = []
total_uhc = 0

for amb, lista in por_amb.items():
    uhc_amb = sum([x["uhc"] for x in lista])
    total_uhc += uhc_amb
    tem_pia = any([x["tipo_peca"] == "pia" for x in lista])
    tem_bacia = any(["bacia" in x["tipo_peca"] for x in lista])
    
    # Diametro do ramal do ambiente NBR 8160
    if tem_bacia or uhc_amb > 10:
        dn_ramal = 100
    elif tem_pia or uhc_amb > 6:
        dn_ramal = 50
    else:
        dn_ramal = 40
        
    ambientes_esg.append({
        "ambiente": amb,
        "n_pecas": len(lista),
        "uhc_total": uhc_amb,
        "dn_ramal_mm": dn_ramal,
        "exige_caixa_gordura": tem_pia,
        "exige_caixa_sifonada": not tem_pia and not (tem_bacia and len(lista) == 1)
    })
    print("  {0:24} {1} pecas | {2} UHC | DN {3} mm | Gordura: {4} | Sifonada: {5}".format(
        amb, len(lista), uhc_amb, dn_ramal, "Sim" if tem_pia else "Nao", "Sim" if not tem_pia else "Nao"))

# Dimensionamento da Caixa de Gordura (NBR 8160)
# Para 1 cozinha unifamiliar: Caixa de Gordura Simples (capacidade de retencao 18 L)
vol_gordura_l = 18.0

# Dimensionamento do Tubo de Queda / Prumada de Esgoto Principal (DN 100 atende ate 500 UHC em predios ate 3 pavimentos)
dn_tubo_queda = 100 if total_uhc <= 500 else 150
dn_coluna_ventilacao = 75 if total_uhc <= 100 else 100

resultado = {
    "projeto": CFG["projeto"],
    "esgoto": {
        "norma": "NBR 8160 - Sistemas prediais de esgoto sanitário",
        "n_pontos": len(pontos_esg),
        "uhc_total": total_uhc,
        "dn_tubo_queda_mm": dn_tubo_queda,
        "dn_coluna_ventilacao_mm": dn_coluna_ventilacao,
        "caixa_gordura_retencao_l": vol_gordura_l,
        "declividade_min_dn100": "1.0%",
        "declividade_min_dn50": "2.0%"
    },
    "ambientes_esg": ambientes_esg,
    "pontos_esg": pontos_esg
}

f = codecs.open(os.path.join(D, "dimensionamento_esg.json"), "w", encoding="utf-8")
f.write(json.dumps(resultado, indent=2, ensure_ascii=False))
f.close()

print("")
print("=" * 60)
print("RESUMO ESGOTO SANITARIO (NBR 8160)")
print("  pontos de esgoto       : {0}".format(len(pontos_esg)))
print("  total UHC              : {0} UHC".format(total_uhc))
print("  tubo de queda principal: DN {0} mm".format(dn_tubo_queda))
print("  coluna de ventilacao   : DN {0} mm".format(dn_coluna_ventilacao))
print("  caixa de gordura       : {0} L".format(vol_gordura_l))
print("=" * 60)
print("-> data/dimensionamento_esg.json")
