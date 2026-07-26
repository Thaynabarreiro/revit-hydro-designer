# -*- coding: utf-8 -*-
"""M2 PLUV - Dimensionamento de Aguas Pluviais (NBR 10844 / DTU 60.11).

Le: data/config_projeto.json + data/pluviometria.json
Gera: data/dimensionamento_pluv.json
"""
import codecs
import json
import math
import os
import unicodedata

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


def normalizar(texto):
    if not texto:
        return ""
    txt = unicodedata.normalize("NFKD", str(texto))
    txt = "".join([c for c in txt if not unicodedata.combining(c)])
    return txt.lower().strip()


CFG = ler("config_projeto.json")
PLUV_DB = ler("pluviometria.json")

proj = CFG["projeto"]
pais = proj.get("pais", "BR")
cidade_input = proj.get("cidade", "Porto Alegre")
cidade_norm = normalizar(cidade_input)

db_pais = PLUV_DB.get(pais, PLUV_DB.get("BR"))
cidades_db = db_pais.get("cidades", {})

info_cidade = cidades_db.get(cidade_norm)
if not info_cidade:
    # Fuzzy match
    for k, v in cidades_db.items():
        if k in cidade_norm or cidade_norm in k:
            info_cidade = v
            break

if info_cidade:
    I_pluv = info_cidade["intensidade_mm_h"]
    origem_dados = "Base Pluviométrica (" + pais + " - " + str(info_cidade.get("estado") or info_cidade.get("region") or "") + ")"
else:
    I_pluv = db_pais.get("padrao_pais", 150.0)
    origem_dados = "Valor Padrão Regional (" + pais + ")"

print("=== M2 PLUV DIMENSIONAMENTO DE AGUAS PLUVIAIS - " + proj["nome"] + " ===")
print("  Pais                   : " + pais)
print("  Cidade informada       : " + cidade_input)
print("  Intensidade Pluv (I)   : " + str(I_pluv) + " mm/h (" + origem_dados + ")")

# Area de contribuicao de cobertura estimada (m2)
area_cobertura_m2 = 150.0

# Vazao total de projeto Q (L/s)
# BR (NBR 10844): Q (L/s) = (I * A) / 3600
# FR (DTU 60.11): Q (L/s) = A * DTU_L_S_M2
if pais == "FR":
    dtu_rate = info_cidade.get("dtu_l_s_m2", 0.05) if info_cidade else 0.05
    q_pluv_ls = area_cobertura_m2 * dtu_rate
else:
    q_pluv_ls = (I_pluv * area_cobertura_m2) / 3600.0

q_pluv_lmin = q_pluv_ls * 60.0

# Numero de prumadas / condutores verticais
n_condutores = int(math.ceil(q_pluv_ls / 3.5)) or 2
q_por_condutor = q_pluv_ls / n_condutores

dn_condutor_mm = 100 if q_por_condutor > 1.5 else 75
dn_coletor_horizontal_mm = 100 if q_pluv_ls <= 4.5 else 150

resultado = {
    "projeto": proj,
    "pluvial": {
        "norma": "NBR 10844 (Brasil)" if pais == "BR" else "DTU 60.11 (França)",
        "pais": pais,
        "cidade": cidade_input,
        "origem_dados": origem_dados,
        "intensidade_mm_h": I_pluv,
        "area_cobertura_m2": area_cobertura_m2,
        "vazao_total_ls": round(q_pluv_ls, 2),
        "vazao_total_lmin": round(q_pluv_lmin, 1),
        "n_condutores_verticais": n_condutores,
        "vazao_por_condutor_ls": round(q_por_condutor, 2),
        "dn_condutor_mm": dn_condutor_mm,
        "dn_coletor_horizontal_mm": dn_coletor_horizontal_mm,
        "declividade_min_coletor": "0.5%"
    }
}

f = codecs.open(os.path.join(D, "dimensionamento_pluv.json"), "w", encoding="utf-8")
f.write(json.dumps(resultado, indent=2, ensure_ascii=False))
f.close()

print("")
print("=" * 60)
print("RESUMO AGUAS PLUVIAIS (" + pais + ")")
print("  cidade / intensidade  : {0} ({1} mm/h)".format(cidade_input, I_pluv))
print("  origem                : {0}".format(origem_dados))
print("  area de cobertura     : {0} m2".format(area_cobertura_m2))
print("  vazao de projeto Q    : {0:.2f} L/s ({1:.1f} L/min)".format(q_pluv_ls, q_pluv_lmin))
print("  condutores verticais  : {0} x DN {1} mm".format(n_condutores, dn_condutor_mm))
print("  coletor enterrado     : DN {0} mm (declividade 0.5%)".format(dn_coletor_horizontal_mm))
print("=" * 60)
print("-> data/dimensionamento_pluv.json")
