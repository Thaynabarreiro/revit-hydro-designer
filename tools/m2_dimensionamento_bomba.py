# -*- coding: utf-8 -*-
"""M2 BOMBA - Dimensionamento de Conjunto Moto-Bomba de Recalque (NBR 5626).

Calcula vazao de recalque, altura manometrica total (AMT), potencia em CV/kW,
e seleciona bomba comercial para sistemas com reservatorio inferior e superior.
"""
import codecs
import json
import math
import os

_this_dir = os.path.dirname(os.path.abspath(__file__))
_auto_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
RAIZ = globals().get("RAIZ", os.environ.get("HYDRO_PROJECT_ROOT", _auto_root))
D = os.path.join(RAIZ, "data")


def ler(nome):
    f = codecs.open(os.path.join(D, nome), "r", encoding="utf-8")
    dados = json.loads(f.read())
    f.close()
    return dados


CFG = ler("config_projeto.json")
R_AF = ler("dimensionamento.json")

rv = CFG.get("reservacao", {})
oc = R_AF.get("ocupacao", {})
cd_litros = oc.get("consumo_diario_l", 600.0)

print("=== M2 BOMBA DIMENSIONAMENTO DE RECALQUE - " + CFG["projeto"]["nome"] + " ===")

# Tempo de funcionamento continuo da bomba por dia (1.5 h padrao NBR 5626)
tempo_funcionamento_h = 1.5
q_bomba_m3h = (cd_litros / 1000.0) / tempo_funcionamento_h
q_bomba_ls = q_bomba_m3h / 3.6

# Alturas geometricas
h_geometria_recalque_m = 6.5 # Altura do reservatorio inferior ate o reservatorio superior (m)
h_geometria_succao_m = 1.5 # Altura de succao (m)
h_perda_carga_est_m = 1.5 # Perda de carga estimada nos tubos e conexoes (mca)

altura_manometrica_total_mca = h_geometria_recalque_m + h_geometria_succao_m + h_perda_carga_est_m

# Rendimento do conjunto moto-bomba (eta ~ 50% para bombas pequenas)
rendimento = 0.50

# Potencia (CV): P_CV = (gamma * Q * AMT) / (75 * eta)
# gamma = 1.0 kgf/L, Q em L/s, AMT em mca
potencia_cv = (1.0 * q_bomba_ls * altura_manometrica_total_mca) / (75.0 * rendimento)
potencia_kw = potencia_cv * 0.7355

# Selecao comercial de bomba
MOTOBOMBAS_COMERCIAIS = [
    {"modelo": "Schneider BC-92S 0.25 CV", "potencia_cv": 0.25, "dn_succao_mm": 25, "dn_recalque_mm": 25},
    {"modelo": "Schneider BC-92S 0.50 CV", "potencia_cv": 0.50, "dn_succao_mm": 25, "dn_recalque_mm": 25},
    {"modelo": "Schneider BC-92S 0.75 CV", "potencia_cv": 0.75, "dn_succao_mm": 32, "dn_recalque_mm": 25},
    {"modelo": "Schneider BC-92S 1.00 CV", "potencia_cv": 1.00, "dn_succao_mm": 32, "dn_recalque_mm": 25},
    {"modelo": "Dancor CP-4R 1.50 CV", "potencia_cv": 1.50, "dn_succao_mm": 40, "dn_recalque_mm": 32},
    {"modelo": "Dancor CP-4R 2.00 CV", "potencia_cv": 2.00, "dn_succao_mm": 40, "dn_recalque_mm": 32}
]

bomba_selecionada = MOTOBOMBAS_COMERCIAIS[0]
for b in MOTOBOMBAS_COMERCIAIS:
    if b["potencia_cv"] >= potencia_cv:
        bomba_selecionada = b
        break

resultado = {
    "projeto": CFG["projeto"],
    "bomba_recalque": {
        "norma": "NBR 5626 - Sistemas de Recalque e Elevação de Água",
        "consumo_diario_l": cd_litros,
        "tempo_operacao_h": tempo_funcionamento_h,
        "vazao_bomba_ls": round(q_bomba_ls, 3),
        "vazao_bomba_m3h": round(q_bomba_m3h, 2),
        "altura_geometria_m": h_geometria_recalque_m + h_geometria_succao_m,
        "altura_manometrica_total_mca": round(altura_manometrica_total_mca, 2),
        "potencia_calculada_cv": round(potencia_cv, 2),
        "potencia_calculada_kw": round(potencia_kw, 2),
        "bomba_recomendada": bomba_selecionada
    }
}

f = codecs.open(os.path.join(D, "dimensionamento_bomba.json"), "w", encoding="utf-8")
f.write(json.dumps(resultado, indent=2, ensure_ascii=False))
f.close()

print("")
print("=" * 60)
print("RESUMO SISTEMA DE RECALQUE E MOTO-BOMBA (NBR 5626)")
print("  vazao de recalque     : {0:.3f} L/s ({1:.2f} m3/h)".format(q_bomba_ls, q_bomba_m3h))
print("  altura manometrica AMT: {0:.2f} mca".format(altura_manometrica_total_mca))
print("  potencia calculada    : {0:.2f} CV ({1:.2f} kW)".format(potencia_cv, potencia_kw))
print("  bomba recomendada     : {0}".format(bomba_selecionada["modelo"]))
print("  tubos de succao/recalq: Succao DN {0} mm | Recalque DN {1} mm".format(
    bomba_selecionada["dn_succao_mm"], bomba_selecionada["dn_recalque_mm"]))
print("=" * 60)
print("-> data/dimensionamento_bomba.json")
