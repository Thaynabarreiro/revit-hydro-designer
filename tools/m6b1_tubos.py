# -*- coding: utf-8 -*-
"""M6b etapa 1 - cria os tubos a partir dos CONECTORES das pecas.

Separado da etapa 2 (conexoes) de proposito: cada requisicao fica curta,
cabe no timeout do bridge, e um crash perde no maximo uma etapa.

Grava data/rede_ids.json com os ids criados, que a etapa 2 consome.
"""
import codecs
import json
import math
import os

from Autodesk.Revit.DB import (
    BuiltInCategory,
    BuiltInParameter,
    Element,
    ElementId,
    FilteredElementCollector,
    Level,
    StorageType,
    Transaction,
    UnitTypeId,
    UnitUtils,
    XYZ,
)
from Autodesk.Revit.DB.Plumbing import Pipe, PipeType, PipingSystemType
import System

# Aceita RAIZ injetada pelo chamador (os botoes pyRevit descobrem a raiz a
# partir da propria localizacao). O literal e apenas o fallback do bridge.
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


NORMA = ler("pecas_br.json")
CFG = ler("config_projeto.json")
FAM = ler("familias_pecas.json")

AF = CFG["agua_fria"]
P_PESO = FAM["parametros"]["peso"]
H_BARRILETE = 2900.0
C = AF["coef_C"]


def nm(e):
    try:
        return Element.Name.__get__(e)
    except Exception:
        return "(?)"


def mm(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.Millimeters)


def ft(v):
    return UnitUtils.ConvertToInternalUnits(v, UnitTypeId.Millimeters)


def eid(i):
    try:
        return int(i.Value)
    except Exception:
        return int(i.IntegerValue)


def diametro(q):
    if q <= 0:
        return AF["diametros_comerciais_mm"][0]
    dt = math.sqrt(4.0 * (q / 1000.0) / (math.pi * AF["velocidade_max_ms"])) * 1000.0
    for d in sorted(AF["diametros_comerciais_mm"]):
        if d >= dt and d >= AF["diametro_min_ramal_mm"]:
            return d
    return sorted(AF["diametros_comerciais_mm"])[-1]


def conector_af(el):
    try:
        cm = el.MEPModel.ConnectorManager
    except Exception:
        return None
    if cm is None:
        return None
    for c in cm.Connectors:
        try:
            if str(c.PipeSystemType) == "DomesticColdWater":
                return c
        except Exception:
            pass
    return None


def set_dn(pipe, d):
    try:
        p = pipe.get_Parameter(BuiltInParameter.RBS_PIPE_DIAMETER_PARAM)
        if p and not p.IsReadOnly:
            p.Set(ft(d))
    except Exception:
        pass


niveis = sorted(FilteredElementCollector(doc).OfClass(Level).ToElements(),
                key=lambda x: x.Elevation)
nivel_base, nivel_topo = niveis[0], niveis[-1]

tipo_tubo = None
for t in FilteredElementCollector(doc).OfClass(PipeType).ToElements():
    if "Marrom" in nm(t):
        tipo_tubo = t
if tipo_tubo is None:
    tipo_tubo = list(FilteredElementCollector(doc).OfClass(PipeType).ToElements())[0]

sistema = None
for s in FilteredElementCollector(doc).OfClass(PipingSystemType).ToElements():
    try:
        if "AAF" in (s.Abbreviation or ""):
            sistema = s
    except Exception:
        pass
if sistema is None:
    raise Exception("sistema AF nao encontrado")

# ------------------------------------------------------------- pecas
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
    c = conector_af(p)
    if c is None:
        continue
    peso = None
    for portador in (p, p.Symbol):
        try:
            pr = portador.LookupParameter(P_PESO)
            if pr and pr.StorageType == StorageType.Double:
                peso = pr.AsDouble()
                break
        except Exception:
            pass
    pecas.append({"el": p, "org": c.Origin, "peso": peso or 0.3, "fam": f})

if p_res is None:
    cx = sum([x["org"].X for x in pecas]) / len(pecas)
    cy = sum([x["org"].Y for x in pecas]) / len(pecas)
    p_res = XYZ(cx, cy, nivel_topo.Elevation)

peso_total = sum([x["peso"] for x in pecas])
print("pecas: {0} | peso total: {1:.2f} | Q: {2:.3f} L/s".format(
    len(pecas), peso_total, C * math.sqrt(peso_total)))

pecas.sort(key=lambda x: math.sqrt((x["org"].X - p_res.X) ** 2 +
                                   (x["org"].Y - p_res.Y) ** 2))

z_barr = ft(H_BARRILETE)

# ============================================ T1: limpar rede anterior
t = Transaction(doc, "M6b1 - limpar rede")
t.Start()
antigos = []
for cat in (BuiltInCategory.OST_PipeCurves, BuiltInCategory.OST_PipeFitting):
    for e in (FilteredElementCollector(doc).OfCategory(cat)
              .WhereElementIsNotElementType().ToElements()):
        antigos.append(e.Id)
rem = 0
for i in antigos:
    try:
        if doc.GetElement(i) is None:
            continue
        col = System.Collections.Generic.List[ElementId]()
        col.Add(i)
        doc.Delete(col)
        rem += 1
    except Exception:
        pass
t.Commit()
print("rede anterior removida: " + str(rem))

# ============================================ T2: sub-ramais
t = Transaction(doc, "M6b1 - sub-ramais")
t.Start()
saida = {"sub_ramais": [], "barrilete": [], "coluna": None, "nos": []}
erros = []

for i, pc in enumerate(pecas):
    con = conector_af(pc["el"])
    if con is None:
        erros.append(("sub-ramal " + str(i + 1), "conector sumiu"))
        pc["vert"] = None
        continue
    o = con.Origin
    alvo = XYZ(o.X, o.Y, z_barr)
    try:
        tubo = Pipe.Create(doc, tipo_tubo.Id, nivel_base.Id, con, alvo)
        set_dn(tubo, diametro(C * math.sqrt(pc["peso"])))
        pc["vert"] = tubo
        pc["no"] = alvo
        saida["sub_ramais"].append(eid(tubo.Id))
        saida["nos"].append([alvo.X, alvo.Y, alvo.Z])
    except Exception as e:
        pc["vert"] = None
        erros.append(("sub-ramal " + str(i + 1), str(e)[:60]))
t.Commit()
print("sub-ramais criados: " + str(len(saida["sub_ramais"])))

# ============================================ T3: coluna + barrilete
t = Transaction(doc, "M6b1 - coluna e barrilete")
t.Start()
no0 = XYZ(p_res.X, p_res.Y, z_barr)
try:
    coluna = Pipe.Create(doc, sistema.Id, tipo_tubo.Id, nivel_base.Id,
                         XYZ(p_res.X, p_res.Y, nivel_topo.Elevation), no0)
    set_dn(coluna, diametro(C * math.sqrt(peso_total)))
    saida["coluna"] = eid(coluna.Id)
except Exception as e:
    erros.append(("coluna", str(e)[:60]))

peso_rest = peso_total
p_ant = no0
for i, pc in enumerate(pecas):
    if pc.get("vert") is None:
        continue
    try:
        b = Pipe.Create(doc, sistema.Id, tipo_tubo.Id, nivel_base.Id, p_ant, pc["no"])
        set_dn(b, diametro(C * math.sqrt(max(peso_rest, 0.01))))
        saida["barrilete"].append({
            "id": eid(b.Id),
            "vert_id": eid(pc["vert"].Id),
            "no": [pc["no"].X, pc["no"].Y, pc["no"].Z],
            "peso_acum": round(peso_rest, 2),
        })
        p_ant = pc["no"]
        peso_rest -= pc["peso"]
    except Exception as e:
        erros.append(("barrilete " + str(i + 1), str(e)[:60]))
t.Commit()
print("trechos de barrilete: " + str(len(saida["barrilete"])))

saida["no0"] = [no0.X, no0.Y, no0.Z]

f = codecs.open(os.path.join(D, "rede_ids.json"), "w", encoding="utf-8")
f.write(json.dumps(saida, indent=2))
f.close()

if erros:
    print("")
    print("=== ERROS ===")
    for (r, e) in erros:
        print("  {0:20} {1}".format(r, e))

print("")
print("tubos no modelo: " + str(FilteredElementCollector(doc).OfCategory(
    BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType().GetElementCount()))
print("-> data/rede_ids.json")
