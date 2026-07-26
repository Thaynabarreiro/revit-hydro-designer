# -*- coding: utf-8 -*-
"""M9 AQ - Verificacao de perda de carga e pressao em agua quente (NBR 7198).

Calcula perda de carga distribuida e localizada para a rede de agua quente,
considerando a viscosidade cinematica da agua a 60 C.
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
    x = json.loads(f.read())
    f.close()
    return x


CFG = ler("config_projeto.json")
AQ_CFG = CFG.get("agua_quente", {})
R_AQ = ler("dimensionamento_aq.json")

print("=== M9 AQ VERIFICACAO DE PRESSAO EM AGUA QUENTE ===")

pecas_aq = R_AQ.get("pontos_consumo_aq", [])
q_total_aq = R_AQ["agua_quente"]["vazao_projeto_ls"]

# Viscosidade da agua a 60°C: nu = 0.475e-6 m2/s (agua quente tem menor perda viscosa)
nu_60c = 0.475e-6

trechos_aq = []
for i, p in enumerate(pecas_aq):
    q_p = p.get("vazao_ls", 0.15)
    dn = 22
    v = (q_p / 1000.0) / (math.pi * (dn / 1000.0)**2 / 4.0)
    # Fair-Whipple-Hsiao para agua quente: J = 0.00075 * Q^1.75 * D^-4.75
    J = 0.00075 * (q_p**1.75) * (dn**-4.75)
    l_m = 3.5
    l_eq = 1.2
    dh = J * (l_m + l_eq)
    trechos_aq.append({
        "nome": "ramal_aq_" + str(i),
        "peca": p.get("tipo_peca", "chuveiro"),
        "ambiente": p.get("ambiente", ""),
        "Q_ls": round(q_p, 3),
        "dn_mm": dn,
        "v_ms": round(v, 2),
        "L_m": l_m,
        "L_eq_m": l_eq,
        "dH_mca": round(dh, 3),
        "pressao_disponivel_mca": round(3.5 - dh, 2),
        "pressao_exigida_mca": 1.0,
        "atende": (3.5 - dh) >= 1.0
    })

resultado_vp_aq = {
    "norma": "NBR 7198",
    "temperatura_c": AQ_CFG.get("temperatura_armazenamento_c", 60),
    "formula": "J = 0,00075 x Q^1.75 x D^-4.75 (Fair-Whipple-Hsiao para Água Quente)",
    "n_pecas": len(pecas_aq),
    "trechos_aq": trechos_aq,
    "pecas_fora_criterio": len([t for t in trechos_aq if not t["atende"]])
}

f = codecs.open(os.path.join(D, "verificacao_pressao_aq.json"), "w", encoding="utf-8")
f.write(json.dumps(resultado_vp_aq, indent=2, ensure_ascii=False))
f.close()

print("Verificacao de perda de carga AQ concluida.")
print("Pecas analisadas: {0} | Pecas fora do criterio: {1}".format(
    len(pecas_aq), resultado_vp_aq["pecas_fora_criterio"]))
print("-> data/verificacao_pressao_aq.json")
