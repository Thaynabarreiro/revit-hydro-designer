# -*- coding: utf-8 -*-
"""M6b - Rede de agua fria FISICAMENTE CONECTADA.

Diferenca para o m6_rede_agua_fria.py: em vez de desenhar tubos soltos nas
coordenadas, parte do CONECTOR de cada peca e cria tes/joelhos reais nos nos.
Com isso o Revit passa a reconhecer a rede como um sistema unico e calcula
vazao sozinho - o que tambem mata os warnings de fluxo.

Topologia:
    reservatorio -> coluna de descida -> no_0
    no_0 -> barrilete -> no_1 -> ... -> no_n
    cada no_i tem um sub-ramal descendo/subindo ate o conector da peca
    nos intermediarios viram TE; o ultimo vira JOELHO
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
    PipeSystemType,
    StorageType,
    Transaction,
    UnitTypeId,
    UnitUtils,
    XYZ,
)
from Autodesk.Revit.DB.Plumbing import Pipe, PipeType, PipingSystemType
from Autodesk.Revit.DB.Structure import StructuralType
import System

# Aceita RAIZ injetada pelo chamador (os botoes pyRevit descobrem a raiz a
# partir da propria localizacao). O literal e apenas o fallback do bridge.
_this_dir = os.path.dirname(os.path.abspath(__file__))
_auto_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
RAIZ = globals().get("RAIZ", os.environ.get("HYDRO_PROJECT_ROOT", _auto_root))
D = os.path.join(RAIZ, "data")


def ler(n):
    f = codecs.open(os.path.join(D, n), "r", encoding="utf-8")
    x = json.loads(f.read())
    f.close()
    return x


NORMA = ler("pecas_br.json")
CFG = ler("config_projeto.json")
FAM = ler("familias_pecas.json")
DIM = ler("dimensionamento.json")

AF = CFG["agua_fria"]
P_PESO = FAM["parametros"]["peso"]
H_BARRILETE = 2900.0


def nm(e):
    try:
        return Element.Name.__get__(e)
    except Exception:
        return "(?)"


def mm(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.Millimeters)


def ft(v):
    return UnitUtils.ConvertToInternalUnits(v, UnitTypeId.Millimeters)


def diametro(q_ls):
    if q_ls <= 0:
        return AF["diametros_comerciais_mm"][0]
    dt = math.sqrt(4.0 * (q_ls / 1000.0) / (math.pi * AF["velocidade_max_ms"])) * 1000.0
    for d in sorted(AF["diametros_comerciais_mm"]):
        if d >= dt and d >= AF["diametro_min_ramal_mm"]:
            return d
    return sorted(AF["diametros_comerciais_mm"])[-1]


def conector_af(elem):
    """Conector de agua fria domestica de uma peca."""
    try:
        cm = elem.MEPModel.ConnectorManager
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


def conector_perto(pipe, ponto):
    """Conector de um tubo mais proximo de um ponto."""
    melhor, dmin = None, 1e9
    for c in pipe.ConnectorManager.Connectors:
        d = c.Origin.DistanceTo(ponto)
        if d < dmin:
            melhor, dmin = c, d
    return melhor


def set_dn(pipe, d_mm):
    try:
        p = pipe.get_Parameter(BuiltInParameter.RBS_PIPE_DIAMETER_PARAM)
        if p and not p.IsReadOnly:
            p.Set(ft(d_mm))
    except Exception:
        pass


# ---------------------------------------------------------- contexto
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
        ab = s.Abbreviation or ""
    except Exception:
        ab = ""
    if "AAF" in ab:
        sistema = s
if sistema is None:
    raise Exception("sistema de agua fria nao encontrado")

print("tipo: " + nm(tipo_tubo) + " | sistema: " + nm(sistema))

# ------------------------------------------------------------- pecas
pecas, infra = [], []
for p in (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures)
          .WhereElementIsNotElementType().ToElements()):
    try:
        f = p.Symbol.FamilyName
    except Exception:
        continue
    if "Reservatorio" in f or "Cavalete" in f:
        infra.append(p)
        continue
    c = conector_af(p)
    if c is None:
        print("  !! sem conector AF: " + f[:50])
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
    pecas.append({"el": p, "con": c, "org": c.Origin, "peso": peso or 0.3, "fam": f})

print("pecas com conector AF: " + str(len(pecas)))
peso_total = sum([x["peso"] for x in pecas])
C = AF["coef_C"]
print("peso total: {0:.2f} | Q: {1:.3f} L/s".format(peso_total, C * math.sqrt(peso_total)))

# reservatorio como origem da coluna
p_res = None
for i in infra:
    try:
        if "Reservatorio" in i.Symbol.FamilyName:
            p_res = i.Location.Point
    except Exception:
        pass
if p_res is None:
    cx = sum([x["org"].X for x in pecas]) / len(pecas)
    cy = sum([x["org"].Y for x in pecas]) / len(pecas)
    p_res = XYZ(cx, cy, nivel_topo.Elevation)

# ------------------------------------------------- limpar rede anterior
t = Transaction(doc, "M6b - rede conectada")
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
print("rede anterior removida: " + str(rem))

z_barr = ft(H_BARRILETE)
criados, erros, fittings = [], [], []

# ordena por distancia ao reservatorio (define a ordem do barrilete)
pecas.sort(key=lambda x: math.sqrt((x["org"].X - p_res.X) ** 2 +
                                   (x["org"].Y - p_res.Y) ** 2))

# ------------------------------------------- 1. sub-ramais (do conector)
for i, pc in enumerate(pecas):
    o = pc["org"]
    alvo = XYZ(o.X, o.Y, z_barr)
    try:
        tubo = Pipe.Create(doc, tipo_tubo.Id, nivel_base.Id, pc["con"], alvo)
        set_dn(tubo, diametro(C * math.sqrt(pc["peso"])))
        pc["vert"] = tubo
        pc["no"] = alvo
        criados.append(("sub-ramal " + str(i + 1), mm(o.DistanceTo(alvo))))
    except Exception as e:
        pc["vert"] = None
        erros.append(("sub-ramal " + str(i + 1), str(e)[:70]))

doc.Regenerate()

# --------------------------------------------------- 2. coluna + barrilete
no0 = XYZ(p_res.X, p_res.Y, z_barr)
q_total = C * math.sqrt(peso_total)

try:
    coluna = Pipe.Create(doc, sistema.Id, tipo_tubo.Id, nivel_base.Id,
                         XYZ(p_res.X, p_res.Y, nivel_topo.Elevation), no0)
    set_dn(coluna, diametro(q_total))
    criados.append(("coluna de descida", mm(nivel_topo.Elevation - z_barr)))
except Exception as e:
    coluna = None
    erros.append(("coluna", str(e)[:70]))

barr = []
peso_rest = peso_total
p_ant = no0
ant_tubo = coluna
for i, pc in enumerate(pecas):
    if pc.get("vert") is None:
        continue
    try:
        b = Pipe.Create(doc, sistema.Id, tipo_tubo.Id, nivel_base.Id, p_ant, pc["no"])
        set_dn(b, diametro(C * math.sqrt(max(peso_rest, 0.01))))
        barr.append((b, pc, ant_tubo, p_ant))
        criados.append(("barrilete " + str(i + 1) + " (peso {0:.2f})".format(peso_rest),
                        mm(p_ant.DistanceTo(pc["no"]))))
        ant_tubo = b
        p_ant = pc["no"]
        peso_rest -= pc["peso"]
    except Exception as e:
        erros.append(("barrilete " + str(i + 1), str(e)[:70]))

doc.Regenerate()

# ------------------------------------------------------ 3. conexoes
# no_0: coluna + primeiro trecho do barrilete -> joelho
if coluna is not None and barr:
    try:
        c1 = conector_perto(coluna, no0)
        c2 = conector_perto(barr[0][0], no0)
        doc.Create.NewElbowFitting(c1, c2)
        fittings.append("joelho no pe da coluna")
    except Exception as e:
        erros.append(("joelho coluna", str(e)[:70]))

# nos intermediarios: te (barrilete que chega + barrilete que sai + sub-ramal)
for k in range(len(barr)):
    b_atual, pc, _, _ = barr[k]
    b_prox = barr[k + 1][0] if k + 1 < len(barr) else None
    vert = pc.get("vert")
    if vert is None:
        continue
    no = pc["no"]
    try:
        c_chega = conector_perto(b_atual, no)
        c_vert = conector_perto(vert, no)
        if b_prox is not None:
            c_sai = conector_perto(b_prox, no)
            doc.Create.NewTeeFitting(c_chega, c_sai, c_vert)
            fittings.append("te no no " + str(k + 1))
        else:
            doc.Create.NewElbowFitting(c_chega, c_vert)
            fittings.append("joelho no no final")
    except Exception as e:
        erros.append(("conexao no " + str(k + 1), str(e)[:70]))

doc.Regenerate()
t.Commit()

# ----------------------------------------------------------- relatorio
print("")
print("=== TRECHOS (" + str(len(criados)) + ") ===")
for (r, c) in criados:
    print("  {0:38} {1:8.0f} mm".format(r, c))

print("")
print("=== CONEXOES CRIADAS (" + str(len(fittings)) + ") ===")
for f in fittings:
    print("  " + f)

if erros:
    print("")
    print("=== ERROS (" + str(len(erros)) + ") ===")
    for (r, e) in erros:
        print("  {0:26} {1}".format(r[:26], e))

print("")
print("tubos    : " + str(FilteredElementCollector(doc).OfCategory(
    BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType().GetElementCount()))
print("conexoes : " + str(FilteredElementCollector(doc).OfCategory(
    BuiltInCategory.OST_PipeFitting).WhereElementIsNotElementType().GetElementCount()))
print("warnings : " + str(len(doc.GetWarnings())))

# quantos conectores de peca ficaram efetivamente ligados
lig = 0
for pc in pecas:
    try:
        if pc["con"].IsConnected:
            lig += 1
    except Exception:
        pass
print("pecas conectadas a rede: {0} de {1}".format(lig, len(pecas)))
