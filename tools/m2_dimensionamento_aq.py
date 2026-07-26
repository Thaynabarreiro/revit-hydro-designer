# -*- coding: utf-8 -*-
"""M2 AQ - Dimensionamento do sistema de agua quente (NBR 7198 / NBR 5626).

Le:  data/pontos_consumo.json
     data/pecas_br.json
     data/config_projeto.json

Grava: data/dimensionamento_aq.json
"""
import codecs
import json
import math
import os
import re

_this_dir = os.path.dirname(os.path.abspath(__file__))
_auto_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
RAIZ = globals().get("RAIZ", os.environ.get("HYDRO_PROJECT_ROOT", _auto_root))
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
AQ_CFG = CFG.get("agua_quente", {
    "fonte_aquecimento": "aquecedor_passagem",
    "temperatura_uso_c": 40,
    "temperatura_armazenamento_c": 60,
    "coef_C": 0.30,
    "velocidade_max_ms": 3.0,
    "diametro_min_ramal_mm": 22,
    "diametros_comerciais_mm": [15, 22, 28, 35, 42, 54]
})

print("=== M2 AQ DIMENSIONAMENTO DE AGUA QUENTE - " + CFG["projeto"]["nome"] + " ===")

# Fixtures requiring hot water
TIPOS_AQ = ["chuveiro", "lavatorio", "pia", "bide", "banheira"]

pontos_aq = [p for p in CONS["pontos_consumo"] if p["tipo_peca"] in TIPOS_AQ]

print("pontos totais de consumo  : " + str(len(CONS["pontos_consumo"])))
print("pontos de agua quente (AQ): " + str(len(pontos_aq)))
for p in pontos_aq:
    print("   - {0:18} em {1}".format(p["tipo_peca"], p["ambiente"]))

# 1. Ocupacao e consumo diario de agua quente
oc = CFG["ocupacao"]
dorm_count = len([a for a in CONS["ambientes"] if re.search(oc["regex_dormitorio"], a["nome"].lower()) and not re.search(oc.get("regex_excluir_dormitorio", "banho"), a["nome"].lower())])
moradores = oc.get("moradores_override") or (dorm_count * oc.get("pessoas_por_dormitorio", 2))

# Consumo diario medio de agua quente: ~40 L/hab/dia (NBR 7198)
q_per_capita_aq = 40.0
cd_aq = moradores * q_per_capita_aq

# 2. Vazao de projeto de agua quente
peso_total_aq = sum([p["peso"] for p in pontos_aq])
C = AQ_CFG.get("coef_C", 0.30)
q_ls_aq = C * math.sqrt(max(peso_total_aq, 0.01)) if pontos_aq else 0.0
q_m3h_aq = q_ls_aq * 3.6

# 3. Dimensionamento da fonte de aquecimento
fonte = AQ_CFG.get("fonte_aquecimento", "aquecedor_passagem")
delta_t = AQ_CFG.get("temperatura_uso_c", 40) - 20 # Temp agua fria ~20°C

# Potencia calorifica necessaria (kW) para aquecedor de passagem: P = Q(L/s) * dt * 4.184
potencia_kw = q_ls_aq * delta_t * 4.184 if q_ls_aq > 0 else 0.0

resultado = {
    "projeto": CFG["projeto"],
    "agua_quente": {
        "n_pontos": len(pontos_aq),
        "peso_total": round(peso_total_aq, 2),
        "coef_C": C,
        "vazao_projeto_ls": round(q_ls_aq, 3),
        "vazao_projeto_m3h": round(q_m3h_aq, 3),
        "consumo_diario_aq_l": cd_aq,
        "fonte_aquecimento": fonte,
        "potencia_estimada_kw": round(potencia_kw, 1),
        "delta_t_c": delta_t,
        "diametro_min_mm": AQ_CFG.get("diametro_min_ramal_mm", 22)
    },
    "pontos_consumo_aq": pontos_aq
}

f = codecs.open(os.path.join(D, "dimensionamento_aq.json"), "w", encoding="utf-8")
f.write(json.dumps(resultado, indent=2, ensure_ascii=False))
f.close()

print("")
print("=" * 60)
print("RESUMO AGUA QUENTE (NBR 7198)")
print("  moradores             : {0}".format(moradores))
print("  pontos de consumo AQ  : {0}".format(len(pontos_aq)))
print("  peso total AQ         : {0}".format(round(peso_total_aq, 2)))
print("  vazao de projeto AQ   : {0:.3f} L/s ({1:.2f} m3/h)".format(q_ls_aq, q_m3h_aq))
print("  consumo diario AQ     : {0} L/dia".format(cd_aq))
print("  fonte de aquecimento  : {0}".format(fonte))
print("  potencia aquecedor    : {0:.1f} kW (deltaT = {1} C)".format(potencia_kw, delta_t))
print("=" * 60)
print("-> data/dimensionamento_aq.json")
