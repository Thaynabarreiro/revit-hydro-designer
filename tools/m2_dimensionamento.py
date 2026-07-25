# -*- coding: utf-8 -*-
"""M2/M3/M4 - Dimensionamento de agua fria, reservatorio e hidrometro.

Le:  data/pontos_consumo.json  (saida do M1)
     data/pecas_br.json        (base normativa)
     data/config_projeto.json  (parametros DESTE projeto)

Grava: data/dimensionamento.json

Nao toca no modelo Revit - so calcula. A modelagem e o M5/M6.
"""
import codecs
import json
import math
import os
import re
import unicodedata

RAIZ = globals().get("RAIZ", "C:/Users/Shadow/Documents/00 - Claude - Revit")
D = os.path.join(RAIZ, "data")


def ler(nome):
    f = codecs.open(os.path.join(D, nome), "r", encoding="utf-8")
    dados = json.loads(f.read())
    f.close()
    return dados


def normalizar(t):
    if not t:
        return ""
    t = unicodedata.normalize("NFKD", unicode(t))
    return "".join([c for c in t if not unicodedata.combining(c)]).lower()


CONS = ler("pontos_consumo.json")
NORMA = ler("pecas_br.json")
CFG = ler("config_projeto.json")

TIPOS = NORMA["tipos"]
memorial = []   # cada passo do calculo, para o memorial do M8


def passo(titulo, formula, resultado, obs=""):
    memorial.append({
        "titulo": titulo, "formula": formula,
        "resultado": resultado, "obs": obs,
    })
    print("")
    print("### " + titulo)
    print("    " + formula)
    print("    => " + resultado)
    if obs:
        print("    obs: " + obs)


print("=== M2 DIMENSIONAMENTO - " + CFG["projeto"]["nome"] + " ===")

# ------------------------------------------- 1. pecas complementares
pontos = list(CONS["pontos_consumo"])
complementares = []

# Contagem do que o levantamento ja trouxe, por tipo. Quando o reader le o
# modelo MEP, as pecas complementares ja foram colocadas la pelo M5 e portanto
# ja estao contadas - somar de novo dobraria a carga delas.
ja_no_modelo = {}
for p in pontos:
    ja_no_modelo[p["tipo_peca"]] = ja_no_modelo.get(p["tipo_peca"], 0) + 1

for pc in CFG.get("pecas_complementares", []):
    tipo = pc["tipo"]
    if tipo not in TIPOS:
        print("!! tipo desconhecido em pecas_complementares: " + tipo)
        continue
    quantidade = pc.get("quantidade", 1)
    presentes = ja_no_modelo.get(tipo, 0)
    if presentes >= quantidade:
        print("   = {0}: {1} ja no modelo, nao sera somada".format(tipo, presentes))
        ja_no_modelo[tipo] = presentes - quantidade
        continue
    quantidade -= presentes
    ja_no_modelo[tipo] = 0

    dados = TIPOS[tipo]
    for _ in range(quantidade):
        registro = {
            "id": None,
            "familia": "(complementar)",
            "ambiente": pc.get("ambiente", "(nao definido)"),
            "tipo_peca": tipo,
            "confianca": "adicionada por configuracao",
            "motivo": pc.get("motivo", ""),
            "desc": dados["desc"],
            "vazao_ls": dados["vazao_ls"],
            "peso": dados["peso"],
            "pressao_min_kpa": dados["pressao_min_kpa"],
            "esgoto_uhc": dados["esgoto_uhc"],
            "origem": "complementar",
        }
        pontos.append(registro)
        complementares.append(registro)

for p in pontos:
    p.setdefault("origem", "modelo")

print("")
print("pontos do modelo arquitetonico : " + str(len(CONS["pontos_consumo"])))
print("pontos complementares          : " + str(len(complementares)))
for c in complementares:
    print("   + {0} em {1}  ({2})".format(c["tipo_peca"], c["ambiente"], c["motivo"]))
print("TOTAL                          : " + str(len(pontos)))

# ------------------------------------------------------ 2. ocupacao
oc = CFG["ocupacao"]
excluir = oc.get("regex_excluir_dormitorio")
dorms = [a for a in CONS["ambientes"]
         if re.search(oc["regex_dormitorio"], normalizar(a["nome"]))
         and not (excluir and re.search(excluir, normalizar(a["nome"])))]

if oc.get("moradores_override"):
    moradores = oc["moradores_override"]
    origem_ocup = "definido manualmente na configuracao"
else:
    moradores = len(dorms) * oc["pessoas_por_dormitorio"]
    origem_ocup = "{0} dormitorio(s) x {1} pessoa(s)".format(
        len(dorms), oc["pessoas_por_dormitorio"])

passo("Ocupacao",
      "dormitorios identificados: " + ", ".join([d["nome"] for d in dorms]),
      "{0} moradores".format(moradores),
      origem_ocup)

# -------------------------------------------------- 3. consumo diario
cd = moradores * oc["consumo_per_capita_l_dia"]
passo("Consumo diario",
      "CD = {0} hab x {1} L/hab.dia".format(moradores, oc["consumo_per_capita_l_dia"]),
      "CD = {0} L/dia".format(cd))

# --------------------------------------------------- 4. reservatorio
rv = CFG["reservacao"]
vol_necessario = cd * rv["dias_reserva"] + rv.get("reserva_incendio_l", 0)

comerciais = sorted(rv["volumes_comerciais_l"])
vol_adotado = None
for v in comerciais:
    if v >= vol_necessario:
        vol_adotado = v
        break
if vol_adotado is None:
    vol_adotado = comerciais[-1]

passo("Volume de reservacao",
      "V = CD x dias + incendio = {0} x {1} + {2}".format(
          cd, rv["dias_reserva"], rv.get("reserva_incendio_l", 0)),
      "V necessario = {0} L  ->  adotado {1} L".format(vol_necessario, vol_adotado),
      "tipo de reservacao: " + rv["tipo"])

if rv["tipo"] == "inferior_superior":
    # pratica corrente: 40% superior / 60% inferior
    v_sup = round(vol_adotado * 0.4)
    v_inf = vol_adotado - v_sup
    passo("Divisao dos reservatorios",
          "superior = 40% | inferior = 60%",
          "superior {0} L / inferior {1} L".format(v_sup, v_inf),
          "exige conjunto de recalque (sistema AR)")
else:
    v_sup, v_inf = vol_adotado, 0

# ------------------------------------------------- 5. vazao de projeto
af = CFG["agua_fria"]
peso_total = sum([p["peso"] for p in pontos])
C = af["coef_C"]
q_ls = C * math.sqrt(peso_total)
q_m3h = q_ls * 3.6

passo("Vazao de projeto (metodo dos pesos)",
      "Q = C x raiz(soma dos pesos) = {0} x raiz({1})".format(C, round(peso_total, 2)),
      "Q = {0} L/s  ({1} m3/h)".format(round(q_ls, 3), round(q_m3h, 2)),
      "soma dos pesos considera as {0} pecas (modelo + complementares)".format(len(pontos)))

# ---------------------------------------------------- 6. hidrometro
escolhido = None
for h in sorted(CFG["hidrometro"]["modelos"], key=lambda x: x["q_max_m3h"]):
    if h["q_max_m3h"] >= q_m3h:
        escolhido = h
        break
if escolhido is None:
    escolhido = CFG["hidrometro"]["modelos"][-1]

passo("Hidrometro",
      "menor modelo com Q_max >= {0} m3/h".format(round(q_m3h, 2)),
      "{0} (DN {1} mm)".format(escolhido["nome"], escolhido["dn_mm"]),
      "folga de {0}%".format(round((escolhido["q_max_m3h"] / q_m3h - 1) * 100)))


# ------------------------------------- 7. diametro do ramal de entrada
def diametro_por_velocidade(q_litros_s, v_max, comerciais_mm, d_min_mm):
    """D = raiz(4Q / pi.v). Retorna o menor diametro comercial que atende."""
    q_m3s = q_litros_s / 1000.0
    d_teorico_mm = math.sqrt(4.0 * q_m3s / (math.pi * v_max)) * 1000.0
    for d in sorted(comerciais_mm):
        if d >= d_teorico_mm and d >= d_min_mm:
            return d, d_teorico_mm
    return sorted(comerciais_mm)[-1], d_teorico_mm


d_ramal, d_teorico = diametro_por_velocidade(
    q_ls, af["velocidade_max_ms"], af["diametros_comerciais_mm"],
    af["diametro_min_ramal_mm"])

v_real = (q_ls / 1000.0) / (math.pi * (d_ramal / 1000.0) ** 2 / 4.0)

passo("Ramal de entrada / alimentador predial",
      "D = raiz(4Q / pi.v) com Q = {0} L/s e v_max = {1} m/s".format(
          round(q_ls, 3), af["velocidade_max_ms"]),
      "D teorico = {0} mm  ->  adotado DN {1} mm".format(round(d_teorico, 1), d_ramal),
      "velocidade real = {0} m/s (limite {1})".format(
          round(v_real, 2), af["velocidade_max_ms"]))

# ------------------------------ 8. dimensionamento por ambiente (sub-ramais)
print("")
print("### Sub-ramais por ambiente")
sub_ramais = []
por_amb = {}
for p in pontos:
    por_amb.setdefault(p["ambiente"], []).append(p)

for amb in sorted(por_amb.keys()):
    lst = por_amb[amb]
    peso_amb = sum([x["peso"] for x in lst])
    q_amb = C * math.sqrt(peso_amb)
    d_amb, d_teo = diametro_por_velocidade(
        q_amb, af["velocidade_max_ms"], af["diametros_comerciais_mm"],
        af["diametro_min_ramal_mm"])
    sub_ramais.append({
        "ambiente": amb, "n_pecas": len(lst),
        "peso": round(peso_amb, 2), "vazao_ls": round(q_amb, 3),
        "diametro_mm": d_amb,
    })
    print("  {0:22} {1} peca(s)  peso={2:<5} Q={3:.3f} L/s  ->  DN {4} mm".format(
        amb, len(lst), round(peso_amb, 2), q_amb, d_amb))

# -------------------------------------------- 9. pressao no ponto critico
# altura disponivel = fundo do reservatorio ate o ponto mais alto de consumo
niveis_z = [p.get("xyz_mm", [0, 0, 0])[2] for p in pontos
            if p.get("xyz_mm") and len(p.get("xyz_mm")) == 3]
z_mais_alto = max(niveis_z) if niveis_z else 0

pressao_min_exigida = max([p["pressao_min_kpa"] for p in pontos])
# 1 mca = 9,81 kPa
altura_min_m = pressao_min_exigida / 9.81

passo("Pressao minima e altura do reservatorio",
      "peca mais exigente: {0} kPa = {1} mca".format(
          pressao_min_exigida, round(altura_min_m, 2)),
      "fundo do reservatorio deve estar >= {0} m acima do ponto mais desfavoravel".format(
          round(altura_min_m, 2)),
      "ponto de consumo mais alto no modelo: z = {0} mm. Nao inclui perda de carga - entra no M9.".format(
          round(z_mais_alto)))

# ------------------------------------------------------------- saida
resultado = {
    "projeto": CFG["projeto"],
    "ocupacao": {
        "dormitorios": [d["nome"] for d in dorms],
        "moradores": moradores,
        "origem": origem_ocup,
        "consumo_per_capita_l_dia": oc["consumo_per_capita_l_dia"],
        "consumo_diario_l": cd,
    },
    "reservacao": {
        "dias": rv["dias_reserva"],
        "volume_necessario_l": vol_necessario,
        "volume_adotado_l": vol_adotado,
        "tipo": rv["tipo"],
        "volume_superior_l": v_sup,
        "volume_inferior_l": v_inf,
    },
    "agua_fria": {
        "n_pontos": len(pontos),
        "peso_total": round(peso_total, 2),
        "coef_C": C,
        "vazao_projeto_ls": round(q_ls, 3),
        "vazao_projeto_m3h": round(q_m3h, 3),
        "diametro_ramal_mm": d_ramal,
        "diametro_teorico_mm": round(d_teorico, 2),
        "velocidade_real_ms": round(v_real, 2),
    },
    "hidrometro": escolhido,
    "sub_ramais": sub_ramais,
    "pressao": {
        "min_exigida_kpa": pressao_min_exigida,
        "altura_min_m": round(altura_min_m, 2),
    },
    "pontos_consumo": pontos,
    "memorial": memorial,
}

f = codecs.open(os.path.join(D, "dimensionamento.json"), "w", encoding="utf-8")
f.write(json.dumps(resultado, indent=2, ensure_ascii=False))
f.close()

print("")
print("=" * 60)
print("RESUMO")
print("  moradores           : {0}".format(moradores))
print("  consumo diario      : {0} L/dia".format(cd))
print("  reservatorio        : {0} L ({1} dias)".format(vol_adotado, rv["dias_reserva"]))
print("  pontos de consumo   : {0}".format(len(pontos)))
print("  peso total          : {0}".format(round(peso_total, 2)))
print("  vazao de projeto    : {0} L/s = {1} m3/h".format(round(q_ls, 3), round(q_m3h, 2)))
print("  hidrometro          : {0} DN {1}".format(escolhido["nome"], escolhido["dn_mm"]))
print("  ramal de entrada    : DN {0} mm (v = {1} m/s)".format(d_ramal, round(v_real, 2)))
print("=" * 60)
print("-> data/dimensionamento.json")
