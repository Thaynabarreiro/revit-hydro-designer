# -*- coding: utf-8 -*-
"""M6e - Rede de agua fria com roteamento ORTOGONAL.

Substitui o traçado em cadeia (que encadeava peca a peca por proximidade e
produzia angulos arbitrarios, impedindo a criacao de tes).

Topologia de barrilete real:

    reservatorio
         | coluna (vertical)
         v
    no0 --- espinha (corre em Y, no X do reservatorio) ---> ...
              |            |              |
           ramal(X)     ramal(X)       ramal(X)
              |            |              |
           descida(Z)   descida(Z)     descida(Z)
              |            |              |
            peca         peca           peca

Como espinha (Y), ramal (X) e descida (Z) sao mutuamente perpendiculares,
todo encontro e de 90 graus - e o Revit consegue criar te e joelho.

Dimensionamento: cada trecho da espinha carrega o peso acumulado das pecas
ainda por servir; ramal e descida carregam o peso da propria peca.
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


CFG = ler("config_projeto.json")
FAM = ler("familias_pecas.json")
AF = CFG["agua_fria"]
P_PESO = FAM["parametros"]["peso"]

H_BARRILETE = 2900.0
C = AF["coef_C"]
TOL = 0.05  # ~15 mm: abaixo disso considera-se mesmo alinhamento


def nm(e):
    try:
        return Element.Name.__get__(e)
    except Exception:
        return "(?)"


def mm(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.Millimeters)


def ft(v):
    return UnitUtils.ConvertToInternalUnits(v, UnitTypeId.Millimeters)


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


def conector_perto(pipe, p):
    melhor, dmin = None, 1e9
    try:
        cons = pipe.ConnectorManager.Connectors
    except Exception:
        return None, 1e9
    for c in cons:
        d = c.Origin.DistanceTo(p)
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


# ------------------------------------------------------------ contexto
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
    pecas.append({"el": p, "org": c.Origin, "peso": peso or 0.3})

if p_res is None:
    p_res = XYZ(sum([x["org"].X for x in pecas]) / len(pecas),
                sum([x["org"].Y for x in pecas]) / len(pecas),
                nivel_topo.Elevation)

peso_total = sum([x["peso"] for x in pecas])
z_barr = ft(H_BARRILETE)
x_esp = p_res.X          # a espinha corre no X do reservatorio

# ordena pela coordenada Y: a espinha percorre o eixo Y
pecas.sort(key=lambda x: abs(x["org"].Y - p_res.Y))

print("pecas: {0} | peso: {1:.2f} | Q: {2:.3f} L/s".format(
    len(pecas), peso_total, C * math.sqrt(peso_total)))
print("espinha em X = {0:.0f} mm, altura {1:.0f} mm".format(mm(x_esp), H_BARRILETE))

# =========================================================== T1: tubos
t = Transaction(doc, "M6e - rede ortogonal")
t.Start()

antigos = []
for cat in (BuiltInCategory.OST_PipeCurves, BuiltInCategory.OST_PipeFitting):
    for e in (FilteredElementCollector(doc).OfCategory(cat)
              .WhereElementIsNotElementType().ToElements()):
        antigos.append(e.Id)
for i in antigos:
    try:
        if doc.GetElement(i) is None:
            continue
        col = System.Collections.Generic.List[ElementId]()
        col.Add(i)
        doc.Delete(col)
    except Exception:
        pass

erros = []


def tubo(p1, p2, d, rotulo):
    if p1.DistanceTo(p2) < ft(2.0):
        return None
    try:
        pi = Pipe.Create(doc, sistema.Id, tipo_tubo.Id, nivel_base.Id, p1, p2)
        set_dn(pi, d)
        return pi
    except Exception as e:
        erros.append((rotulo, str(e)[:60]))
        return None


# coluna de descida do reservatorio ate o plano do barrilete
no0 = XYZ(x_esp, p_res.Y, z_barr)
coluna = tubo(XYZ(p_res.X, p_res.Y, nivel_topo.Elevation), no0,
              diametro(C * math.sqrt(peso_total)), "coluna")

# espinha + ramais + descidas
peso_rest = peso_total
y_ant = p_res.Y
esp_ant = None
nos = []

for i, pc in enumerate(pecas):
    o = pc["org"]
    y_i = o.Y
    d_esp = diametro(C * math.sqrt(max(peso_rest, 0.01)))
    d_peca = diametro(C * math.sqrt(pc["peso"]))

    # trecho de espinha ate a altura desta peca (corre em Y)
    p_no = XYZ(x_esp, y_i, z_barr)
    esp = tubo(XYZ(x_esp, y_ant, z_barr), p_no, d_esp, "espinha " + str(i + 1))

    # ramal perpendicular (corre em X) - so se a peca nao estiver na espinha
    if abs(o.X - x_esp) > TOL:
        p_ramal = XYZ(o.X, y_i, z_barr)
        ramal = tubo(p_no, p_ramal, d_peca, "ramal " + str(i + 1))
    else:
        p_ramal, ramal = p_no, None

    # descida vertical ate o conector da peca
    desc = tubo(p_ramal, o, d_peca, "descida " + str(i + 1))

    nos.append({"esp_ant": esp_ant, "esp": esp, "ramal": ramal, "desc": desc,
                "p_no": p_no, "p_ramal": p_ramal, "org": o,
                "peso_acum": round(peso_rest, 2), "pc": pc})

    esp_ant = esp
    y_ant = y_i
    peso_rest -= pc["peso"]

t.Commit()
n_tubos = FilteredElementCollector(doc).OfCategory(
    BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType().GetElementCount()
print("tubos criados: " + str(n_tubos))

# ================================================== T2: ligar as pecas
t = Transaction(doc, "M6e - ligar pecas")
t.Start()
ligadas, nao_ligadas = 0, []
for i, n in enumerate(nos):
    d = n["desc"]
    if d is None:
        nao_ligadas.append((i + 1, "sem descida"))
        continue
    cp = conector_af(n["pc"]["el"])
    ct, dist = conector_perto(d, n["org"])
    if cp is None or ct is None:
        nao_ligadas.append((i + 1, "conector ausente"))
        continue
    try:
        if not cp.IsConnected:
            cp.ConnectTo(ct)
        ligadas += 1
    except Exception as e:
        nao_ligadas.append((i + 1, str(e)[:50]))
t.Commit()
print("pecas ligadas: {0} de {1}".format(ligadas, len(nos)))

# ============================================== T3: tes e joelhos
t = Transaction(doc, "M6e - tes e joelhos")
t.Start()
fit_ok, fit_falha = 0, []


def liga(a, b, ponto, rotulo, terceiro=None):
    global fit_ok
    if a is None or b is None:
        fit_falha.append((rotulo, "tubo ausente"))
        return
    ca, _ = conector_perto(a, ponto)
    cb, _ = conector_perto(b, ponto)
    if ca is None or cb is None:
        fit_falha.append((rotulo, "conector ausente"))
        return
    try:
        if terceiro is not None:
            cc, _ = conector_perto(terceiro, ponto)
            if cc is None:
                fit_falha.append((rotulo, "3o conector ausente"))
                return
            doc.Create.NewTeeFitting(ca, cb, cc)
        else:
            doc.Create.NewElbowFitting(ca, cb)
        fit_ok += 1
    except Exception as e:
        fit_falha.append((rotulo, str(e)[:60]))


# pe da coluna: coluna (Z) + primeira espinha (Y) -> joelho
if nos:
    liga(coluna, nos[0]["esp"], no0, "pe da coluna")

for i, n in enumerate(nos):
    p_no = n["p_no"]
    saida = n["ramal"] if n["ramal"] is not None else n["desc"]
    prox_esp = nos[i + 1]["esp"] if i + 1 < len(nos) else None

    if prox_esp is not None:
        # espinha entra, espinha sai, ramal/descida deriva -> te
        liga(n["esp"], prox_esp, p_no, "te no no " + str(i + 1), terceiro=saida)
    else:
        # ultimo no: espinha termina no ramal/descida -> joelho
        liga(n["esp"], saida, p_no, "joelho no no final")

    # fim do ramal: ramal (X) + descida (Z) -> joelho
    if n["ramal"] is not None and n["desc"] is not None:
        liga(n["ramal"], n["desc"], n["p_ramal"], "joelho ramal " + str(i + 1))

t.Commit()

# ---------------------------------------------------------- relatorio
print("")
print("=== CONEXOES ===")
print("  criadas : " + str(fit_ok))
print("  falhas  : " + str(len(fit_falha)))
for (r, e) in fit_falha:
    print("    {0:24} {1}".format(r[:24], e))

if erros:
    print("")
    print("=== ERROS DE CRIACAO DE TUBO ===")
    for (r, e) in erros:
        print("  {0:20} {1}".format(r, e))

if nao_ligadas:
    print("")
    print("=== PECAS NAO LIGADAS ===")
    for (i, m) in nao_ligadas:
        print("  peca {0}: {1}".format(i, m))

comp = 0.0
for p in (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PipeCurves)
          .WhereElementIsNotElementType().ToElements()):
    try:
        comp += p.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble()
    except Exception:
        pass

print("")
print("tubos       : " + str(FilteredElementCollector(doc).OfCategory(
    BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType().GetElementCount()))
print("conexoes    : " + str(FilteredElementCollector(doc).OfCategory(
    BuiltInCategory.OST_PipeFitting).WhereElementIsNotElementType().GetElementCount()))
print("comprimento : {0:.2f} m".format(mm(comp) / 1000.0))
print("warnings    : " + str(len(doc.GetWarnings())))

o = SaveOptions()
o.Compact = True
doc.Save(o)
print("salvo.")
