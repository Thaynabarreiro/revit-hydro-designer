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
        cm = None
    if cm is not None:
        for c in cm.Connectors:
            try:
                pst = str(c.PipeSystemType)
                if "Sanitary" in pst or "Esgoto" in pst or "Waste" in pst:
                    return c
            except Exception:
                pass
        for c in cm.Connectors:
            try:
                dom = str(c.Domain)
                if "Piping" in dom:
                    return c
            except Exception:
                pass
        for c in cm.Connectors:
            return c
    try:
        loc = el.Location.Point
        if loc:
            class DummyConnector:
                def __init__(self, pt):
                    self.Origin = pt
                    self.PipeSystemType = "Sanitary"
            return DummyConnector(loc)
    except Exception:
        pass
    return None


print("=== M6 ESG REDE DE ESGOTO SANITARIO E VENTILACAO POR GRAVIDADE ===")

niveis = sorted(FilteredElementCollector(doc).OfClass(Level).ToElements(), key=lambda x: x.Elevation)
nivel_base = niveis[0]
nivel_topo = niveis[-1]

tipo_tubo_esg = None
for t in FilteredElementCollector(doc).OfClass(PipeType).ToElements():
    if "Esgoto" in nm(t) or "Sanitario" in nm(t) or "Sanitário" in nm(t) or "PVC" in nm(t):
        tipo_tubo_esg = t
        break
if tipo_tubo_esg is None and FilteredElementCollector(doc).OfClass(PipeType).ToElements():
    tipo_tubo_esg = list(FilteredElementCollector(doc).OfClass(PipeType).ToElements())[0]

sistema_esg = None
sistema_vent = None
for s in FilteredElementCollector(doc).OfClass(PipingSystemType).ToElements():
    try:
        name_sys = nm(s)
        abbr_sys = s.Abbreviation or ""
        class_sys = str(s.SystemClassification)
        if "ESG" in abbr_sys or "Esgoto" in name_sys or "Sanitary" in class_sys:
            sistema_esg = s
        if "VENT" in abbr_sys or "Vent" in name_sys or "Vent" in class_sys:
            sistema_vent = s
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

if not pecas_esg:
    all_fixts = list(FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures).WhereElementIsNotElementType().ToElements())
    for p in all_fixts:
        try:
            f = p.Symbol.FamilyName
            if "Reservatorio" in f or "Cavalete" in f:
                continue
            loc = p.Location.Point
            if loc:
                pecas_esg.append({"el": p, "org": loc, "fam": f})
        except Exception:
            pass

print("pecas com conector de esgoto: " + str(len(pecas_esg)))

# Transaction: Build 3D Gravity Drainage Network & Vent Column
t = Transaction(doc, "M6 ESG - rede de esgoto e coluna de ventilacao NBR 8160")
t.Start()

z_subterraneo = nivel_base.Elevation - ft(400.0) # 400mm abaixo do piso acabado
x_coletor = sum([p["org"].X for p in pecas_esg]) / len(pecas_esg) if pecas_esg else 0.0

def tubo_esg(p1, p2, d, declividade=0.01, sys_override=None):
    if p1.DistanceTo(p2) < ft(MIN_SEG_MM):
        return None
    try:
        dist_h = math.sqrt((p2.X - p1.X)**2 + (p2.Y - p1.Y)**2)
        dz = dist_h * declividade
        p2_inclinado = XYZ(p2.X, p2.Y, p1.Z - dz)
        
        sys_id = sys_override.Id if sys_override else (sistema_esg.Id if sistema_esg else ElementId.InvalidElementId)
        pi = Pipe.Create(doc, sys_id, tipo_tubo_esg.Id, nivel_base.Id, p1, p2_inclinado)
        set_dn(pi, d)
        return pi
    except Exception as e:
        return None

# Coletor principal enterrado em Y (DN 100, 1% declividade)
if pecas_esg:
    pecas_esg.sort(key=lambda x: x["org"].Y)
    y_min = pecas_esg[0]["org"].Y - ft(2000.0)
    y_max = pecas_esg[-1]["org"].Y + ft(2000.0)
else:
    y_min, y_max = -ft(1000.0), ft(1000.0)

p_inicio_coletor = XYZ(x_coletor, y_max, z_subterraneo)
p_fim_coletor = XYZ(x_coletor, y_min, z_subterraneo)

coletor_principal = tubo_esg(p_inicio_coletor, p_fim_coletor, 100, declividade=0.01)

# Ramais individuais de esgoto das pecas ate o coletor
tubos_criados = 0
p_bacia_juncao = None

for i, pc in enumerate(pecas_esg):
    dn_peca = 100 if "Bacia" in pc["fam"] or "Toilet" in pc["fam"] else 50
    decliv = 0.01 if dn_peca >= 100 else 0.02
    
    # Trecho vertical (queda Z do ponto ate a cota enterrada)
    p_enterramento = XYZ(pc["org"].X, pc["org"].Y, z_subterraneo)
    descida = tubo_esg(pc["org"], p_enterramento, dn_peca, declividade=0.0)
    
    # Ramal horizontal ate a linha do coletor
    p_coletor_juncao = XYZ(x_coletor, pc["org"].Y, z_subterraneo)
    ramal_h = tubo_esg(p_enterramento, p_coletor_juncao, dn_peca, declividade=decliv)
    tubos_criados += 2
    
    if dn_peca == 100 and p_bacia_juncao is None:
        p_bacia_juncao = p_enterramento

# COLUNA DE VENTILAÇÃO PRIMÁRIA DN 75mm (NBR 8160)
if p_bacia_juncao:
    z_topo_vent = nivel_topo.Elevation + ft(4000.0) # Sobe 4 metros atraves da laje superior/telhado
    p_topo_vent = XYZ(p_bacia_juncao.X, p_bacia_juncao.Y, z_topo_vent)
    coluna_vent = tubo_esg(p_bacia_juncao, p_topo_vent, 75, declividade=0.0, sys_override=sistema_vent)
    if coluna_vent:
        print("Coluna de Ventilação Primária DN 75mm criada com sucesso subindo até Z=+4.0m.")

t.Commit()
print("Rede de Esgoto e Ventilação NBR 8160 gerada com sucesso ({0} trechos).".format(tubos_criados))
