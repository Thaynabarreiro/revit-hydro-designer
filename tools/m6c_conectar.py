# -*- coding: utf-8 -*-
"""M6c - Rede por coordenada + ligacao dos conectores (abordagem B).

Por que assim:
  Pipe.Create a PARTIR de um conector faz o Revit resolver a conexao na hora;
  quando nao consegue, abre dialogo modal e trava o script inteiro.
  Aqui os tubos sao criados por coordenada (rapido e comprovado), ancorados
  exatamente na origem do conector da peca, e a ligacao e feita depois com
  ConnectTo - um par por vez, com try/except individual.
  Assim uma peca que nao liga vira um item de relatorio, nao um travamento.

Etapa 1 deste arquivo: tubos + ligacao peca<->sub-ramal.
Os tes entre barrilete e sub-ramal ficam para o m6d.
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

RAIZ = "C:/Users/Shadow/Documents/00 - Claude - Revit"
D = os.path.join(RAIZ, "data")


def ler(n):
    f = codecs.open(os.path.join(D, n), "r", encoding="utf-8")
    x = json.loads(f.read())
    f.close()
    return x


CFG = ler("config_projeto.json")
FAM = ler("familias_unmep.json")
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


def conector_perto(pipe, ponto):
    melhor, dmin = None, 1e9
    for c in pipe.ConnectorManager.Connectors:
        d = c.Origin.DistanceTo(ponto)
        if d < dmin:
            melhor, dmin = c, d
    return melhor, dmin


def set_dn(pipe, d):
    try:
        p = pipe.get_Parameter(BuiltInParameter.RBS_PIPE_DIAMETER_PARAM)
        if p and not p.IsReadOnly:
            p.Set(ft(d))
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
        if "AAF" in (s.Abbreviation or ""):
            sistema = s
    except Exception:
        pass

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
    p_res = XYZ(sum([x["org"].X for x in pecas]) / len(pecas),
                sum([x["org"].Y for x in pecas]) / len(pecas),
                nivel_topo.Elevation)

peso_total = sum([x["peso"] for x in pecas])
pecas.sort(key=lambda x: math.sqrt((x["org"].X - p_res.X) ** 2 +
                                   (x["org"].Y - p_res.Y) ** 2))
z_barr = ft(H_BARRILETE)

print("pecas: {0} | peso: {1:.2f} | Q: {2:.3f} L/s".format(
    len(pecas), peso_total, C * math.sqrt(peso_total)))

# ================================================ T1: limpar + criar tubos
t = Transaction(doc, "M6c - rede por coordenada")
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

erros = []

# sub-ramais: comecam EXATAMENTE na origem do conector da peca
for i, pc in enumerate(pecas):
    o = pc["org"]
    alvo = XYZ(o.X, o.Y, z_barr)
    pc["no"] = alvo
    try:
        tubo = Pipe.Create(doc, sistema.Id, tipo_tubo.Id, nivel_base.Id, o, alvo)
        set_dn(tubo, diametro(C * math.sqrt(pc["peso"])))
        pc["vert"] = tubo
    except Exception as e:
        pc["vert"] = None
        erros.append(("sub-ramal " + str(i + 1), str(e)[:60]))

# coluna + barrilete
no0 = XYZ(p_res.X, p_res.Y, z_barr)
try:
    coluna = Pipe.Create(doc, sistema.Id, tipo_tubo.Id, nivel_base.Id,
                         XYZ(p_res.X, p_res.Y, nivel_topo.Elevation), no0)
    set_dn(coluna, diametro(C * math.sqrt(peso_total)))
except Exception as e:
    coluna = None
    erros.append(("coluna", str(e)[:60]))

peso_rest = peso_total
p_ant = no0
for i, pc in enumerate(pecas):
    if pc.get("vert") is None:
        continue
    try:
        b = Pipe.Create(doc, sistema.Id, tipo_tubo.Id, nivel_base.Id, p_ant, pc["no"])
        set_dn(b, diametro(C * math.sqrt(max(peso_rest, 0.01))))
        pc["barr"] = b
        pc["peso_acum"] = round(peso_rest, 2)
        p_ant = pc["no"]
        peso_rest -= pc["peso"]
    except Exception as e:
        pc["barr"] = None
        erros.append(("barrilete " + str(i + 1), str(e)[:60]))

t.Commit()
print("tubos criados: " + str(FilteredElementCollector(doc).OfCategory(
    BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType().GetElementCount()))

# ================================================ T2: ligar peca <-> tubo
t = Transaction(doc, "M6c - ligar conectores")
t.Start()

ligadas, nao_ligadas = [], []
for i, pc in enumerate(pecas):
    if pc.get("vert") is None:
        nao_ligadas.append((pc["fam"], "sem sub-ramal"))
        continue
    cpeca = conector_af(pc["el"])
    if cpeca is None:
        nao_ligadas.append((pc["fam"], "sem conector"))
        continue
    ctubo, dist = conector_perto(pc["vert"], pc["org"])
    if ctubo is None:
        nao_ligadas.append((pc["fam"], "tubo sem conector"))
        continue
    if dist > ft(5.0):
        nao_ligadas.append((pc["fam"], "conector a {0:.1f} mm".format(mm(dist))))
        continue
    try:
        if not cpeca.IsConnected:
            cpeca.ConnectTo(ctubo)
        ligadas.append(pc["fam"])
    except Exception as e:
        nao_ligadas.append((pc["fam"], str(e)[:50]))

t.Commit()

# ------------------------------------------------------------ relatorio
print("")
print("=== LIGACAO PECA <-> SUB-RAMAL ===")
print("  ligadas     : {0} de {1}".format(len(ligadas), len(pecas)))
if nao_ligadas:
    print("  nao ligadas :")
    for (f, m) in nao_ligadas:
        print("    {0:50} {1}".format(f[:50], m))

if erros:
    print("")
    print("=== ERROS DE CRIACAO ===")
    for (r, e) in erros:
        print("  {0:20} {1}".format(r, e))

# guarda os ids para a etapa dos tes (m6d)
saida = {"nos": []}
for pc in pecas:
    if pc.get("vert") is None or pc.get("barr") is None:
        continue
    # nome de familia NAO entra: vem do .NET com acento e o json do
    # IronPython nao consegue codificar. A etapa dos tes so precisa dos ids.
    saida["nos"].append({
        "vert": eid(pc["vert"].Id),
        "barr": eid(pc["barr"].Id),
        "no": [pc["no"].X, pc["no"].Y, pc["no"].Z],
        "peso_acum": pc.get("peso_acum"),
    })
saida["coluna"] = eid(coluna.Id) if coluna is not None else None
saida["no0"] = [no0.X, no0.Y, no0.Z]

f = codecs.open(os.path.join(D, "rede_ids.json"), "w", encoding="utf-8")
f.write(json.dumps(saida, indent=2))
f.close()

print("")
print("nos gravados para a etapa de tes: " + str(len(saida["nos"])))
print("warnings: " + str(len(doc.GetWarnings())))
