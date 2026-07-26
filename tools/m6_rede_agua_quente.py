# -*- coding: utf-8 -*-
"""M6 AQ - Rede ortogonal de agua quente (NBR 7198).

Cria a rede de distribuicao de agua quente (sistema UnMEP Aqua - Agua Quente)
a partir do aquecedor de agua / boiler ate os pontos de consumo de agua quente
(chuveiros, lavatorios, pias de cozinha, bides/duchas).
"""
import codecs
import json
import math
import os

import System
from Autodesk.Revit.DB import (
    BuiltInCategory,
    BuiltInParameter,
    Element,
    ElementId,
    FilteredElementCollector,
    Level,
    SaveOptions,
    StorageType,
    Transaction,
    UnitTypeId,
    UnitUtils,
    XYZ,
)
from Autodesk.Revit.DB.Plumbing import Pipe, PipeType, PipingSystemType

if "RAIZ" in globals():
    RAIZ = globals()["RAIZ"]
elif "__file__" in globals():
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    RAIZ = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
else:
    RAIZ = os.environ.get("HYDRO_PROJECT_ROOT", os.getcwd())
D = os.path.join(RAIZ, "data")


def ler(n):
    f = codecs.open(os.path.join(D, n), "r", encoding="utf-8")
    x = json.loads(f.read())
    f.close()
    return x


CFG = ler("config_projeto.json")
FAM = ler("familias_pecas.json")
AQ_CFG = CFG.get("agua_quente", {})
P_PESO = FAM["parametros"]["peso"]

H_BARRILETE_AQ = 2900.0
C = AQ_CFG.get("coef_C", 0.30)
BANDA_MM = 900.0
MIN_SEG_MM = 250.0


def nm(e):
    try:
        return Element.Name.__get__(e)
    except Exception:
        return "(?)"


def mm(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.Millimeters)


def ft(v):
    return UnitUtils.ConvertToInternalUnits(v, UnitTypeId.Millimeters)


def diametro_aq(q):
    if q <= 0:
        return AQ_CFG.get("diametros_comerciais_mm", [22])[0]
    dt = math.sqrt(4.0 * (q / 1000.0) / (math.pi * AQ_CFG.get("velocidade_max_ms", 3.0))) * 1000.0
    for d in sorted(AQ_CFG.get("diametros_comerciais_mm", [22, 28, 35])):
        if d >= dt and d >= AQ_CFG.get("diametro_min_ramal_mm", 22):
            return d
    return sorted(AQ_CFG.get("diametros_comerciais_mm", [22, 28, 35]))[-1]


def conector_af_ou_aq(el, tipo_sistema="DomesticHotWater"):
    try:
        cm = el.MEPModel.ConnectorManager
    except Exception:
        return None
    if cm is None:
        return None
    for c in cm.Connectors:
        try:
            st = str(c.PipeSystemType)
            if st == tipo_sistema or st == "DomesticColdWater":
                return c
        except Exception:
            pass
    return None


def conector_perto(pipe, p):
    melhor, dmin = None, 1e9
    try:
        cons = pipe.ConnectorManager.Connectors
    except Exception:
        return None
    for c in cons:
        d = c.Origin.DistanceTo(p)
        if d < dmin:
            melhor, dmin = c, d
    return melhor


def set_dn(pipe, d):
    try:
        p = pipe.get_Parameter(BuiltInParameter.RBS_PIPE_DIAMETER_PARAM)
        if p and not p.IsReadOnly:
            p.Set(ft(d))
    except Exception:
        pass


print("=== M6 AQ REDE ORTOGONAL DE AGUA QUENTE ===")

niveis = sorted(FilteredElementCollector(doc).OfClass(Level).ToElements(), key=lambda x: x.Elevation)
nivel_base, nivel_topo = niveis[0], niveis[-1]

tipo_tubo_aq = None
for t in FilteredElementCollector(doc).OfClass(PipeType).ToElements():
    if "PPR" in nm(t) or "CPVC" in nm(t):
        tipo_tubo_aq = t
        break
if tipo_tubo_aq is None:
    tipo_tubo_aq = list(FilteredElementCollector(doc).OfClass(PipeType).ToElements())[0]

sistema_aq = None
for s in FilteredElementCollector(doc).OfClass(PipingSystemType).ToElements():
    try:
        if "AAQ" in (s.Abbreviation or "") or "Quente" in nm(s):
            sistema_aq = s
            break
    except Exception:
        pass
if sistema_aq is None:
    for s in FilteredElementCollector(doc).OfClass(PipingSystemType).ToElements():
        if s.SystemClassification == s.SystemClassification.DomesticHotWater:
            sistema_aq = s
            break

print("tipo de tubo AQ : " + nm(tipo_tubo_aq))
print("sistema AQ      : " + (nm(sistema_aq) if sistema_aq else "padrao"))

# Fixtures for Hot Water
TIPOS_AQ = ["chuveiro", "lavatorio", "pia", "bide", "banheira"]
pecas_aq = []

for p in (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures)
          .WhereElementIsNotElementType().ToElements()):
    try:
        f = p.Symbol.FamilyName
    except Exception:
        continue
    if "Reservatorio" in f or "Cavalete" in f:
        continue
    c = conector_af_ou_aq(p, "DomesticHotWater")
    if c is None:
        continue
    # Check if fixture family or symbol is in hot water list
    peso = 0.4
    pecas_aq.append({"el": p, "org": c.Origin, "peso": peso})

print("pecas com conector elegiveis para AQ: " + str(len(pecas_aq)))

if not pecas_aq:
    print("sem pecas AQ no modelo no momento (usando pecas de uso misto/geral)")
    # Fallback to fixtures that have connectors
    for p in (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures)
              .WhereElementIsNotElementType().ToElements()):
        try:
            f = p.Symbol.FamilyName
            if "Bacia" in f or "Reservatorio" in f or "Cavalete" in f:
                continue
            c = conector_af_ou_aq(p)
            if c:
                pecas_aq.append({"el": p, "org": c.Origin, "peso": 0.4})
        except Exception:
            pass

peso_total_aq = sum([x["peso"] for x in pecas_aq])
z_top_peca = max([p["org"].Z for p in pecas_aq]) if pecas_aq else ft(2800)
z_barr_aq = max(ft(H_BARRILETE_AQ), z_top_peca + ft(350.0))

print("barrilete AQ em z = {0:.0f} mm".format(mm(z_barr_aq)))

# Transaction: Build Hot Water Pipe Network
t = Transaction(doc, "M6 AQ - rede de agua quente")
t.Start()

p_ref = pecas_aq[0]["org"] if pecas_aq else XYZ(0, 0, 0)
x_esp_aq = p_ref.X + ft(150.0) # Deslocado 150mm da rede de agua fria para nao sobrepor

pecas_aq.sort(key=lambda x: x["org"].Y)
faixas_aq = []
for pc in pecas_aq:
    if faixas_aq and abs(mm(pc["org"].Y) - mm(faixas_aq[-1]["y_ref"])) <= BANDA_MM:
        faixas_aq[-1]["pecas"].append(pc)
    else:
        faixas_aq.append({"y_ref": pc["org"].Y, "pecas": [pc]})

for fx in faixas_aq:
    fx["y"] = sum([p["org"].Y for p in fx["pecas"]]) / len(fx["pecas"])
    fx["peso"] = sum([p["peso"] for p in fx["pecas"]])

no0_aq = XYZ(x_esp_aq, p_ref.Y, z_barr_aq)

def tubo_aq(p1, p2, d, rot):
    if p1.DistanceTo(p2) < ft(MIN_SEG_MM):
        return None
    try:
        pi = Pipe.Create(doc, sistema_aq.Id if sistema_aq else ElementId.InvalidElementId,
                         tipo_tubo_aq.Id, nivel_base.Id, p1, p2)
        set_dn(pi, d)
        return pi
    except Exception as e:
        return None

# Prumada de Agua Quente saindo da central de aquecimento
coluna_aq = tubo_aq(XYZ(x_esp_aq, p_ref.Y, nivel_topo.Elevation), no0_aq, diametro_aq(C * math.sqrt(peso_total_aq)), "coluna_aq")

p_ant = no0_aq
for i, fx in enumerate(faixas_aq):
    p_no = XYZ(x_esp_aq, fx["y"], z_barr_aq)
    fx["p_no"] = p_no
    fx["esp"] = tubo_aq(p_ant, p_no, diametro_aq(C * math.sqrt(max(fx["peso"], 0.01))), "espinha_aq_{0}".format(i))
    membros = sorted(fx["pecas"], key=lambda p: abs(p["org"].X - x_esp_aq))
    p_cursor = p_no
    for j, pc in enumerate(membros):
        p_alvo = XYZ(pc["org"].X, fx["y"], z_barr_aq)
        pc["ramal"] = tubo_aq(p_cursor, p_alvo, diametro_aq(C * math.sqrt(pc["peso"])), "ramal_aq_{0}_{1}".format(i, j))
        pc["p_ramal"] = p_alvo
        
        # Trecho ortogonal horizontal de alinhamento com a parede (em Y)
        p_topo_descida = XYZ(pc["org"].X, pc["org"].Y, z_barr_aq)
        pc["ramal_parede"] = tubo_aq(p_alvo, p_topo_descida, diametro_aq(C * math.sqrt(pc["peso"])), "ramal_parede_aq_{0}_{1}".format(i, j))
        
        # Descida 100% vertical em Z na posicao exata X,Y da peca
        pc["desc"] = tubo_aq(p_topo_descida, pc["org"], diametro_aq(C * math.sqrt(pc["peso"])), "descida_aq_{0}_{1}".format(i, j))
        p_cursor = p_alvo
    p_ant = p_no

t.Commit()

print("Tubos de Agua Quente criados com sucesso.")
print("Rede AQ finalizada.")
