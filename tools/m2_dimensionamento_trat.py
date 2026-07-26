# -*- coding: utf-8 -*-
"""M2 TRAT - Dimensionamento de Tratamento de Esgoto no Lote (NBR 7229 / NBR 13969).

Calcula os volumes e dimensoes de:
  - Fossa Septica Prismatic/Circular (NBR 7229)
  - Filtro Anaerobio de Fluxo Ascendente (NBR 13969)
  - Sumidouro / Poco de Infiltracao (NBR 7229)
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
oc = CFG["ocupacao"]
moradores = oc.get("moradores_override") or 4
c_diario = oc.get("consumo_per_capita_l_dia", 150)

print("=== M2 TRAT DIMENSIONAMENTO DE TRATAMENTO DE ESGOTO - " + CFG["projeto"]["nome"] + " ===")

# 1. Fossa Septica (NBR 7229): V = 1000 + N * (C * T + K * Lf)
# N = moradores, C = 150 L/hab.dia, T = 1.0 dia (detencao), K = 57 (acumulacao de lodo), Lf = 1 (lodo fresco)
T_detencao = 1.0
K_lodo = 57.0
Lf_lodo = 1.0

v_fossa_litros = 1000.0 + moradores * (c_diario * T_detencao + K_lodo * Lf_lodo)
v_fossa_adotado = math.ceil(v_fossa_litros / 500.0) * 500.0 # Arredonda para multiplo de 500 L
dn_fossa_adotado_mm = 2000 if v_fossa_adotado >= 2000 else 1500

# 2. Filtro Anaerobio (NBR 13969): Vu = 1.6 * N * C * T
v_filtro_litros = 1.6 * moradores * c_diario * T_detencao
v_filtro_adotado = math.ceil(v_filtro_litros / 200.0) * 200.0
dn_filtro_adotado_mm = 1500 if v_filtro_adotado >= 1000 else 1200

# 3. Sumidouro / Poco de Infiltracao (NBR 7229)
# Area de Infiltracao A = (N * C) / Ci
# Ci = taxa de percolacao do solo (L/m2.dia) -> Solo medio/arenoso ~50 L/m2.dia
ci_percolacao = 50.0
area_infiltracao_m2 = (moradores * c_diario) / ci_percolacao
# Sumidouro circular: A = pi * D * h -> h = A / (pi * D)
dn_sumidouro_mm = 2000
h_sumidouro_m = area_infiltracao_m2 / (math.pi * (dn_sumidouro_mm / 1000.0))

resultado = {
    "projeto": CFG["projeto"],
    "tratamento": {
        "normas": "NBR 7229 (Fossa Séptica e Sumidouro) / NBR 13969 (Filtro Anaeróbio)",
        "moradores": moradores,
        "consumo_per_capita_l_dia": c_diario,
        "fossa_septica": {
            "volume_calculado_l": round(v_fossa_litros, 1),
            "volume_adotado_l": v_fossa_adotado,
            "dn_adotado_mm": dn_fossa_adotado_mm
        },
        "filtro_anaerobio": {
            "volume_calculado_l": round(v_filtro_litros, 1),
            "volume_adotado_l": v_filtro_adotado,
            "dn_adotado_mm": dn_filtro_adotado_mm
        },
        "sumidouro": {
            "area_infiltracao_necessaria_m2": round(area_infiltracao_m2, 2),
            "taxa_percolacao_solo_l_m2_dia": ci_percolacao,
            "dn_adotado_mm": dn_sumidouro_mm,
            "profundidade_util_m": round(h_sumidouro_m, 2)
        }
    }
}

f = codecs.open(os.path.join(D, "dimensionamento_tratamento.json"), "w", encoding="utf-8")
f.write(json.dumps(resultado, indent=2, ensure_ascii=False))
f.close()

print("")
print("=" * 60)
print("RESUMO TRATAMENTO DE ESGOTO NO LOTE (NBR 7229 / NBR 13969)")
print("  moradores / consumo   : {0} hab. / {1} L/hab.dia".format(moradores, c_diario))
print("  fossa septica         : {0} L -> **{1} L** (DN {2} mm)".format(
    round(v_fossa_litros, 1), v_fossa_adotado, dn_fossa_adotado_mm))
print("  filtro anaerobio      : {0} L -> **{1} L** (DN {2} mm)".format(
    round(v_filtro_litros, 1), v_filtro_adotado, dn_filtro_adotado_mm))
print("  sumidouro             : area {0:.2f} m2 (DN {1} mm x h={2:.2f} m)".format(
    area_infiltracao_m2, dn_sumidouro_mm, h_sumidouro_m))
print("=" * 60)
print("-> data/dimensionamento_tratamento.json")
