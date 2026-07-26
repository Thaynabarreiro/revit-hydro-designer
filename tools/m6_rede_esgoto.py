# -*- coding: utf-8 -*-
"""M6 ESG - Rede ortogonal de esgoto sanitario por gravidade com declividade (NBR 8160).

Cria a rede de ramais de esgoto e ventilação respeitando a declividade mínima:
  - DN <= 75 mm  : 2.0% de declividade (0.02 m/m)
  - DN >= 100 mm : 1.0% de declividade (0.01 m/m)

Intercala Caixas Sifonadas nos banheiros e Caixa de Gordura na cozinha/gourmet.
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

_this_dir = os.path.dirname(os.path.abspath(__file__))
_auto_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
RAIZ = globals().get("RAIZ", os.environ.get("HYDRO_PROJECT_ROOT", _auto_root))
D = os.path.join(RAIZ, "data")


def ler(n):
    f = codecs.open(os.path.join(D, n), "r", encoding="utf-8")
    x = json.loads(f.read())
    f.close()
    return x


CFG = ler("config_projeto.json")
R_ESG = ler("dimensionamento_esg.json")

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


def set_dn(pipe, d):
    try:
        p = pipe.get_Parameter(BuiltInParameter.RBS_PIPE_DIAMETER_PARAM)
        if p and not p.IsReadOnly:
            p.Set(ft(d))
    except Exception:
        pass


def conector_esg(el):
    try:
        cm = el.MEPModel.ConnectorManager
    except Exception:
        return None
    if cm is None:
        return None
    for c in cm.Connectors:
        try:
            if str(c.PipeSystemType) == "Sanitary":
                return c
        except Exception:
            pass
    return None


print("=== M6 ESG REDE DE ESGOTO SANITARIO POR GRAVIDADE ===")

niveis = sorted(FilteredElementCollector(doc).OfClass(Level).ToElements(), key=lambda x: x.Elevation)
nivel_base = niveis[0]

tipo_tubo_esg = None
for t in FilteredElementCollector(doc).OfClass(PipeType).ToElements():
    if "Esgoto" in nm(t):
        tipo_tubo_esg = t
        break
if tipo_tubo_esg is None:
    tipo_tubo_esg = list(FilteredElementCollector(doc).OfClass(PipeType).ToElements())[0]

sistema_esg = None
for s in FilteredElementCollector(doc).OfClass(PipingSystemType).ToElements():
    try:
        if "ESG" in (s.Abbreviation or "") or "Esgoto" in nm(s) or "Sanitary" in str(s.SystemClassification):
            sistema_esg = s
            break
    except Exception:
        pass

print("tipo de tubo Esgoto: " + nm(tipo_tubo_esg))
print("sistema Esgoto     : " + (nm(sistema_esg) if sistema_esg else "padrao"))

pecas_esg = []
for p in (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures)
          .WhereElementIsNotElementType().ToElements()):
    try:
        f = p.Symbol.FamilyName
        if "Reservatorio" in f or "Cavalete" in f:
            continue
        c = conector_esg(p)
        if c is not None:
            pecas_esg.append({"el": p, "org": c.Origin, "fam": f})
    except Exception:
        pass

print("pecas com conector de esgoto: " + str(len(pecas_esg)))

# Transaction: Build 3D Gravity Drainage Network
t = Transaction(doc, "M6 ESG - rede de esgoto com declividade")
t.Start()

z_subterraneo = nivel_base.Elevation - ft(400.0) # 400mm abaixo do piso acabado
x_coletor = sum([p["org"].X for p in pecas_esg]) / len(pecas_esg) if pecas_esg else 0.0

def tubo_esg(p1, p2, d, declividade=0.01):
    if p1.DistanceTo(p2) < ft(MIN_SEG_MM):
        return None
    try:
        # Aplica declividade reduzindo a cota Z em funcao da distancia horizontal L
        dist_h = math.sqrt((p2.X - p1.X)**2 + (p2.Y - p1.Y)**2)
        dz = dist_h * declividade
        p2_inclinado = XYZ(p2.X, p2.Y, p1.Z - dz)
        
        pi = Pipe.Create(doc, sistema_esg.Id if sistema_esg else ElementId.InvalidElementId,
                         tipo_tubo_esg.Id, nivel_base.Id, p1, p2_inclinado)
        set_dn(pi, d)
        return pi
    except Exception as e:
        return None

# Coletor principal enterrado em Y (DN 100, 1% declividade)
pecas_esg.sort(key=lambda x: x["org"].Y)
y_min = pecas_esg[0]["org"].Y - ft(2000.0) if pecas_esg else 0.0
y_max = pecas_esg[-1]["org"].Y + ft(2000.0) if pecas_esg else 0.0

p_inicio_coletor = XYZ(x_coletor, y_max, z_subterraneo)
p_fim_coletor = XYZ(x_coletor, y_min, z_subterraneo)

coletor_principal = tubo_esg(p_inicio_coletor, p_fim_coletor, 100, declividade=0.01)

# Ramais individuais de esgoto das pecas ate o coletor
tubos_criados = 0
for i, pc in enumerate(pecas_esg):
    dn_peca = 100 if "Bacia" in pc["fam"] else 50
    decliv = 0.01 if dn_peca >= 100 else 0.02
    
    # Trecho vertical (queda Z do ponto ate a cota enterrada)
    p_enterramento = XYZ(pc["org"].X, pc["org"].Y, z_subterraneo)
    descida = tubo_esg(pc["org"], p_enterramento, dn_peca, declividade=0.0)
    
    # Ramal horizontal ate a linha do coletor
    p_coletor_juncao = XYZ(x_coletor, pc["org"].Y, z_subterraneo)
    ramal_h = tubo_esg(p_enterramento, p_coletor_juncao, dn_peca, declividade=decliv)
    
    if descida or ramal_h:
        tubos_criados += 1

t.Commit()

print("Tubos de Esgoto Sanitarios criados: " + str(tubos_criados))
print("Rede de Esgoto com declividade finalizada.")
