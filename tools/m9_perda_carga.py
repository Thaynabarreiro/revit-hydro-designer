# -*- coding: utf-8 -*-
"""M9 - Verificacao de pressao com perda de carga.

Fecha a lacuna mais seria do sistema. Ate aqui os diametros saiam do criterio
de velocidade, que nao e restritivo em residencia - por isso TODO trecho vinha
DN 20. Quem manda em agua fria e a perda de carga.

O que faz:
  1. Reconstroi logicamente a topologia ortogonal (espinha -> ramal -> descida),
     a mesma do m6e, a partir das pecas do modelo.
  2. Para cada trecho: vazao pelo metodo dos pesos, perda distribuida por
     Fair-Whipple-Hsiao e perda localizada por comprimentos equivalentes.
  3. Acumula ao longo do caminho de cada peca e compara a pressao disponivel
     com a exigida.
  4. Se faltar pressao, aumenta o diametro dos trechos daquele caminho e
     recalcula. Itera ate passar ou esgotar os diametros comerciais.

Nao altera o modelo Revit: e verificacao e dimensionamento. Grava
data/verificacao_pressao.json, consumido pelo memorial.
"""
import codecs
import json
import math
import os

from Autodesk.Revit.DB import (
    BuiltInCategory,
    Element,
    FilteredElementCollector,
    Level,
    StorageType,
    UnitTypeId,
    UnitUtils,
    XYZ,
)

RAIZ = "C:/Users/Shadow/Documents/00 - Claude - Revit"
D_DIR = os.path.join(RAIZ, "data")


def ler(n):
    f = codecs.open(os.path.join(D_DIR, n), "r", encoding="utf-8")
    x = json.loads(f.read())
    f.close()
    return x


CFG = ler("config_projeto.json")
FAM = ler("familias_unmep.json")
NORMA = ler("pecas_br.json")
PC = ler("perda_carga_br.json")

AF = CFG["agua_fria"]
C = AF["coef_C"]
DIAMS = sorted(AF["diametros_comerciais_mm"])
P_PESO = FAM["parametros"]["peso"]
P_PMIN = FAM["parametros"]["pressao_min"]

H_BARRILETE = 2900.0
TOL = 0.05
KPA = PC["kpa_por_mca"]
EQ = PC["comprimentos_equivalentes_m"]


def nm(e):
    try:
        return Element.Name.__get__(e)
    except Exception:
        return "(?)"


def mm(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.Millimeters)


def m(v):
    return mm(v) / 1000.0


def eqv(peca, dn):
    """Comprimento equivalente de uma peca, em metros."""
    tab = EQ.get(peca, {})
    return tab.get(str(int(dn)), 0.0)


def perda_unitaria(q_ls, dn_mm):
    """J em m/m, Fair-Whipple-Hsiao."""
    if q_ls <= 0:
        return 0.0
    q = q_ls / 1000.0          # m3/s
    d = dn_mm / 1000.0         # m
    return PC["K"] * (q ** PC["expoente_Q"]) * (d ** PC["expoente_D"])


def velocidade(q_ls, dn_mm):
    a = math.pi * (dn_mm / 1000.0) ** 2 / 4.0
    return (q_ls / 1000.0) / a if a > 0 else 0.0


def d_por_velocidade(q_ls):
    if q_ls <= 0:
        return DIAMS[0]
    dt = math.sqrt(4.0 * (q_ls / 1000.0) / (math.pi * AF["velocidade_max_ms"])) * 1000.0
    for d in DIAMS:
        if d >= dt and d >= AF["diametro_min_ramal_mm"]:
            return d
    return DIAMS[-1]


def proximo_d(dn):
    for d in DIAMS:
        if d > dn:
            return d
    return None


# ------------------------------------------------------------- modelo
niveis = sorted(FilteredElementCollector(doc).OfClass(Level).ToElements(),
                key=lambda x: x.Elevation)
nivel_topo = niveis[-1]

pecas, p_res = [], None
for p in (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures)
          .WhereElementIsNotElementType().ToElements()):
    try:
        f = p.Symbol.FamilyName
    except Exception:
        continue
    if "Reservatorio" in f:
        p_res = p.Location.Point
        continue
    if "Cavalete" in f:
        continue
    try:
        cm = p.MEPModel.ConnectorManager
        con = None
        for c in cm.Connectors:
            if str(c.PipeSystemType) == "DomesticColdWater":
                con = c
        if con is None:
            continue
    except Exception:
        continue

    peso, pmin = None, None
    for portador in (p, p.Symbol):
        try:
            if peso is None:
                pr = portador.LookupParameter(P_PESO)
                if pr and pr.StorageType == StorageType.Double:
                    peso = pr.AsDouble()
            if pmin is None:
                pr2 = portador.LookupParameter(P_PMIN)
                if pr2 and pr2.StorageType == StorageType.Double:
                    pmin = pr2.AsDouble()   # em mca, conforme UnMEP
        except Exception:
            pass
    pecas.append({"org": con.Origin, "peso": peso or 0.3, "pmin_mca": pmin or 1.0,
                  "fam": p.Symbol.FamilyName})

if not pecas:
    raise Exception("nenhuma peca com conector de agua fria")

if p_res is None:
    p_res = XYZ(sum([x["org"].X for x in pecas]) / len(pecas),
                sum([x["org"].Y for x in pecas]) / len(pecas),
                nivel_topo.Elevation)

peso_total = sum([x["peso"] for x in pecas])
x_esp = p_res.X
z_barr_m = H_BARRILETE / 1000.0

# A instancia do reservatorio pode estar com deslocamento somado a cota do
# nivel (NewFamilyInstance interpreta o Z do ponto como offset em familias
# baseadas em nivel). A cota de projeto e a do nivel superior.
z_res_instancia = m(p_res.Z)
z_res_m = m(nivel_topo.Elevation)
if abs(z_res_instancia - z_res_m) > 0.05:
    print("!! ATENCAO: reservatorio modelado em z = {0:.2f} m, mas o nivel "
          "'{1}' esta em {2:.2f} m.".format(
              z_res_instancia, nm(nivel_topo), z_res_m))
    print("   O calculo usa a cota do NIVEL (conservador). "
          "Corrigir a colocacao no M5.")
    print("")

pecas.sort(key=lambda x: abs(x["org"].Y - p_res.Y))

print("=== M9 VERIFICACAO DE PRESSAO ===")
print("pecas: {0} | peso total: {1:.2f}".format(len(pecas), peso_total))
print("reservatorio em z = {0:.2f} m | barrilete em z = {1:.2f} m".format(
    z_res_m, z_barr_m))
print("")

# --------------------------------------------- topologia (mesma do m6e)
# trechos: coluna, espinha_i, ramal_i, descida_i
trechos = {}
trechos["coluna"] = {"tipo": "coluna", "L": z_res_m - z_barr_m,
                     "peso": peso_total, "pecas_fitting": ["saida_reservatorio"]}

y_ant = p_res.Y
peso_rest = peso_total
caminhos = []   # para cada peca, a lista de chaves de trecho

for i, pc in enumerate(pecas):
    o = pc["org"]
    k_esp = "espinha_" + str(i)
    L_esp = abs(m(o.Y) - m(y_ant))
    trechos[k_esp] = {"tipo": "espinha", "L": L_esp, "peso": peso_rest,
                      "pecas_fitting": ["te_passagem_direta"]}

    tem_ramal = abs(o.X - x_esp) > TOL
    k_ram = "ramal_" + str(i)
    if tem_ramal:
        trechos[k_ram] = {"tipo": "ramal", "L": abs(m(o.X) - m(x_esp)),
                          "peso": pc["peso"],
                          "pecas_fitting": ["te_saida_lateral", "joelho_90"]}

    k_desc = "descida_" + str(i)
    trechos[k_desc] = {"tipo": "descida", "L": abs(z_barr_m - m(o.Z)),
                       "peso": pc["peso"],
                       "pecas_fitting": [] if tem_ramal else ["te_saida_lateral"]}

    caminho = ["coluna"] + ["espinha_" + str(j) for j in range(i + 1)]
    if tem_ramal:
        caminho.append(k_ram)
    caminho.append(k_desc)
    caminhos.append(caminho)

    pc["z_m"] = m(o.Z)
    y_ant = o.Y
    peso_rest -= pc["peso"]

# diametro inicial: criterio de velocidade
for k, t in trechos.items():
    t["Q"] = C * math.sqrt(max(t["peso"], 0.01))
    t["dn"] = d_por_velocidade(t["Q"])


def calcular():
    """Perda em cada trecho e pressao disponivel em cada peca."""
    for t in trechos.values():
        dn = t["dn"]
        t["v"] = velocidade(t["Q"], dn)
        t["J"] = perda_unitaria(t["Q"], dn)
        t["L_eq"] = sum([eqv(p, dn) for p in t["pecas_fitting"]])
        t["L_tot"] = t["L"] + t["L_eq"]
        t["dH"] = t["J"] * t["L_tot"]

    res = []
    for i, pc in enumerate(pecas):
        perda = sum([trechos[k]["dH"] for k in caminhos[i]])
        estatica = z_res_m - pc["z_m"]
        disp = estatica - perda
        res.append({"i": i, "estatica": estatica, "perda": perda,
                    "disp": disp, "exig": pc["pmin_mca"],
                    "ok": disp >= pc["pmin_mca"]})
    return res


# --------------------------------------------------------- iteracao
# A cada passo sobe UM diametro: o do trecho que mais perde carga no caminho
# da peca critica. Subir o caminho inteiro de uma vez superdimensiona
# grosseiramente (a coluna ia parar em DN 110 num sobrado unifamiliar).
it = 0
MAX_IT = 60
while it < MAX_IT:
    r = calcular()
    ruins = [x for x in r if not x["ok"]]
    if not ruins:
        break
    it += 1
    # peca com maior deficit
    pior = min(ruins, key=lambda x: x["disp"] - x["exig"])
    candidatos = [(trechos[k]["dH"], k) for k in caminhos[pior["i"]]
                  if proximo_d(trechos[k]["dn"]) is not None]
    if not candidatos:
        break
    candidatos.sort(reverse=True)
    alvo = candidatos[0][1]
    trechos[alvo]["dn"] = proximo_d(trechos[alvo]["dn"])

r = calcular()

# ---------------------------------------------------------- relatorio
print("=== TRECHOS ===")
print("{0:14} {1:>7} {2:>7} {3:>7} {4:>7} {5:>8} {6:>8}".format(
    "trecho", "Q(L/s)", "DN", "v(m/s)", "L(m)", "Leq(m)", "dH(mca)"))
ordem = ["coluna"] + sorted([k for k in trechos if k != "coluna"],
                            key=lambda k: (k.split("_")[0], int(k.split("_")[1])))
for k in ordem:
    t = trechos[k]
    print("{0:14} {1:7.3f} {2:7.0f} {3:7.2f} {4:7.2f} {5:8.2f} {6:8.3f}".format(
        k, float(t["Q"]), float(t["dn"]), float(t["v"]), float(t["L"]), float(t["L_eq"]), float(t["dH"])))

print("")
print("=== PRESSAO NAS PECAS ===")
print("{0:34} {1:>9} {2:>9} {3:>9} {4:>9}  {5}".format(
    "peca", "est(mca)", "perda", "disp", "exig", "status"))
for i, pc in enumerate(pecas):
    x = r[i]
    print("{0:34} {1:9.2f} {2:9.3f} {3:9.2f} {4:9.2f}  {5}".format(
        pc["fam"][:34], float(x["estatica"]), float(x["perda"]), float(x["disp"]), float(x["exig"]),
        "OK" if x["ok"] else "INSUFICIENTE"))

crit = min(r, key=lambda x: x["disp"] - x["exig"])
falhas = [x for x in r if not x["ok"]]

print("")
print("iteracoes de aumento de diametro: " + str(it))
print("pecas fora do criterio: {0} de {1}".format(len(falhas), len(pecas)))
print("peca critica: {0} (folga {1:.2f} mca)".format(
    pecas[crit["i"]]["fam"][:40], crit["disp"] - crit["exig"]))

# altura minima do reservatorio para a peca critica passar
z_min = pecas[crit["i"]]["z_m"] + crit["exig"] + crit["perda"]
print("altura minima do reservatorio: {0:.2f} m (atual {1:.2f} m)".format(
    z_min, z_res_m))

# ------------------------------------------------------------- saida
saida = {
    "formula": PC["formula"],
    "K": PC["K"],
    "reservatorio_z_m": round(z_res_m, 3),
    "reservatorio_z_min_m": round(z_min, 3),
    "iteracoes": it,
    "trechos": [{
        "nome": k, "tipo": trechos[k]["tipo"],
        "Q_ls": round(trechos[k]["Q"], 4),
        "dn_mm": trechos[k]["dn"],
        "v_ms": round(trechos[k]["v"], 3),
        "L_m": round(trechos[k]["L"], 3),
        "L_eq_m": round(trechos[k]["L_eq"], 3),
        "J_m_m": round(trechos[k]["J"], 6),
        "dH_mca": round(trechos[k]["dH"], 4),
    } for k in ordem],
    "pecas": [{
        "familia": pecas[i]["fam"],
        "peso": pecas[i]["peso"],
        "estatica_mca": round(r[i]["estatica"], 3),
        "perda_mca": round(r[i]["perda"], 4),
        "disponivel_mca": round(r[i]["disp"], 3),
        "disponivel_kpa": round(r[i]["disp"] * KPA, 1),
        "exigida_mca": round(r[i]["exig"], 3),
        "atende": r[i]["ok"],
    } for i in range(len(pecas))],
    "resumo": {
        "pecas_fora": len(falhas),
        "total": len(pecas),
        "diametros_usados": sorted(set([trechos[k]["dn"] for k in trechos])),
    },
}

f = codecs.open(os.path.join(D_DIR, "verificacao_pressao.json"), "w", encoding="utf-8")
f.write(json.dumps(saida, indent=2, ensure_ascii=False))
f.close()

print("")
print("diametros usados: " + ", ".join([str(int(d)) for d in saida["resumo"]["diametros_usados"]]))
print("-> data/verificacao_pressao.json")
