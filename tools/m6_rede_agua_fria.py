# -*- coding: utf-8 -*-
"""M5b + M6 - Infraestrutura e rede de agua fria.

1. Coloca reservatorio (volume do M2) e cavalete de hidrometro (DN do M2).
2. Traca a rede de agua fria com topologia real:
      cavalete -> alimentador predial -> reservatorio
      reservatorio -> coluna de descida -> barrilete -> ramais -> sub-ramais
3. Dimensiona cada trecho por peso acumulado (criterio de velocidade).

Idempotente: apaga os tubos de AF criados por rodadas anteriores antes de
recriar, para poder iterar sem duplicar rede.
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
TIPOS = NORMA["tipos"]

# alturas de referencia (mm, absolutas)
H_BARRILETE = 2900.0      # distribuicao sob o forro
H_PONTO_AGUA = 700.0      # altura do ponto de agua nas pecas


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
    """Menor diametro comercial que atende ao limite de velocidade."""
    if q_ls <= 0:
        return AF["diametros_comerciais_mm"][0]
    d_teo = math.sqrt(4.0 * (q_ls / 1000.0) / (math.pi * AF["velocidade_max_ms"])) * 1000.0
    for d in sorted(AF["diametros_comerciais_mm"]):
        if d >= d_teo and d >= AF["diametro_min_ramal_mm"]:
            return d
    return sorted(AF["diametros_comerciais_mm"])[-1]


# --------------------------------------------------------- niveis
niveis = sorted(FilteredElementCollector(doc).OfClass(Level).ToElements(),
                key=lambda x: x.Elevation)
nivel_base = niveis[0]
nivel_topo = niveis[-1]
print("nivel base: {0} ({1:.0f} mm) | topo: {2} ({3:.0f} mm)".format(
    nm(nivel_base), mm(nivel_base.Elevation), nm(nivel_topo), mm(nivel_topo.Elevation)))

# ----------------------------------------------- pecas ja colocadas
pecas = list(FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures)
             .WhereElementIsNotElementType().ToElements())
print("pecas no modelo: " + str(len(pecas)))

# Nome do parametro vem do JSON: literal acentuado no script e corrompido
# pelo bridge e o LookupParameter nunca casa.
P_PESO = FAM["parametros"]["peso"]

pontos = []
sem_peso = []
for p in pecas:
    try:
        loc = p.Location.Point
    except Exception:
        continue
    try:
        fam = p.Symbol.FamilyName
    except Exception:
        fam = "?"
    if "Reservatorio" in fam or "Cavalete" in fam:
        continue  # infraestrutura, nao e ponto de consumo
    # Nas familias especificas o peso e parametro de INSTANCIA;
    # nas genericas e de TIPO. Tenta os dois antes de desistir.
    peso, origem_peso = None, "?"
    for portador, rotulo in ((p, "instancia"), (p.Symbol, "tipo")):
        try:
            pr = portador.LookupParameter(P_PESO)
            if pr and pr.StorageType == StorageType.Double:
                peso, origem_peso = pr.AsDouble(), rotulo
                break
        except Exception:
            pass
    if peso is None:
        peso = 0.3
        origem_peso = "PADRAO (nao encontrado)"
        sem_peso.append(fam)
    pontos.append({"el": p, "xy": (loc.X, loc.Y), "fam": fam,
                   "peso": peso, "origem_peso": origem_peso})

print("pontos de consumo: " + str(len(pontos)))
if not pontos:
    raise Exception("nenhum ponto de consumo - rode o M5 primeiro")

print("")
print("=== PESOS LIDOS ===")
for p in pontos:
    print("  {0:52} {1}  ({2})".format(p["fam"][:52], p["peso"], p["origem_peso"]))
if sem_peso:
    print("  !! sem peso legivel: " + ", ".join(sorted(set(sem_peso))))

peso_total = sum([p["peso"] for p in pontos])
C = AF["coef_C"]
q_total = C * math.sqrt(peso_total)
print("")
print("peso total: {0:.2f} | Q total: {1:.3f} L/s".format(peso_total, q_total))


# ------------------------------------------------- tipo e sistema
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
    for s in FilteredElementCollector(doc).OfClass(PipingSystemType).ToElements():
        if "gua Fria" in nm(s) or "gua fria" in nm(s):
            sistema = s
if sistema is None:
    raise Exception("sistema de agua fria nao encontrado")

print("tipo de tubo: " + nm(tipo_tubo))
print("sistema: " + nm(sistema))

# --------------------------------------- limpar rede anterior (idempotencia)
antigos = []
for pi in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PipeCurves) \
        .WhereElementIsNotElementType().ToElements():
    antigos.append(pi.Id)
for fi in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PipeFitting) \
        .WhereElementIsNotElementType().ToElements():
    antigos.append(fi.Id)

t = Transaction(doc, "M6 - rede de agua fria")
t.Start()

# Um a um: apagar um tubo ja remove suas conexoes em cascata, entao um
# Delete em lote falha inteiro ao topar num id que ja sumiu.
removidos = 0
for i in antigos:
    try:
        if doc.GetElement(i) is None:
            continue
        col = System.Collections.Generic.List[ElementId]()
        col.Add(i)
        doc.Delete(col)
        removidos += 1
    except Exception:
        pass
if removidos:
    print("rede anterior removida: " + str(removidos) + " elementos")

# infraestrutura de rodadas anteriores tambem sai, para nao empilhar
inf_antiga = []
for p in (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures)
          .WhereElementIsNotElementType().ToElements()):
    try:
        f = p.Symbol.FamilyName
    except Exception:
        continue
    if "Reservatorio" in f or "Cavalete" in f:
        inf_antiga.append(p.Id)
for i in inf_antiga:
    try:
        if doc.GetElement(i) is None:
            continue
        col = System.Collections.Generic.List[ElementId]()
        col.Add(i)
        doc.Delete(col)
    except Exception:
        pass
if inf_antiga:
    print("infraestrutura anterior removida: " + str(len(inf_antiga)))


def criar_tubo(p1, p2, d_mm, rotulo):
    """Cria um trecho e devolve o objeto Pipe (ou None)."""
    if p1.DistanceTo(p2) < ft(1.0):
        return None
    try:
        pipe = Pipe.Create(doc, sistema.Id, tipo_tubo.Id, nivel_base.Id, p1, p2)
        pr = pipe.get_Parameter(BuiltInParameter.RBS_PIPE_DIAMETER_PARAM)
        if pr and not pr.IsReadOnly:
            pr.Set(ft(d_mm))
        criados.append((rotulo, d_mm, mm(p1.DistanceTo(p2))))
        return pipe
    except Exception as e:
        erros.append((rotulo, str(e)[:70]))
        return None


criados, erros = [], []

# ------------------------------------------- infraestrutura: reservatorio
cx = sum([p["xy"][0] for p in pontos]) / len(pontos)
cy = sum([p["xy"][1] for p in pontos]) / len(pontos)

vol = str(DIM["reservacao"]["volume_adotado_l"])
info_res = FAM["infraestrutura"]["reservatorio"]
tipo_res = info_res["tipo_por_volume"].get(vol)

sym_res = None
for s in (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures)
          .WhereElementIsElementType().ToElements()):
    try:
        f = s.FamilyName
    except Exception:
        continue
    if f.startswith(info_res["familia"]) and (tipo_res is None or nm(s) == tipo_res):
        sym_res = s
        break

p_res = XYZ(cx, cy, nivel_topo.Elevation)
if sym_res is not None:
    if not sym_res.IsActive:
        sym_res.Activate()
        doc.Regenerate()
    doc.Create.NewFamilyInstance(p_res, sym_res, nivel_topo, StructuralType.NonStructural)
    print("reservatorio colocado: " + sym_res.FamilyName + " :: " + nm(sym_res))
else:
    print("!! reservatorio " + vol + " L nao encontrado")

# ------------------------------------------- infraestrutura: hidrometro
dn_hid = str(DIM["hidrometro"]["dn_mm"])
info_hid = FAM["infraestrutura"]["hidrometro"]
tipo_hid = info_hid["tipo_por_dn"].get(dn_hid)

sym_hid = None
for s in (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures)
          .WhereElementIsElementType().ToElements()):
    try:
        f = s.FamilyName
    except Exception:
        continue
    if f.startswith(info_hid["familia"]) and (tipo_hid is None or nm(s) == tipo_hid):
        sym_hid = s
        break

# cavalete afastado da casa, no limite do terreno
raio = max([math.sqrt((p["xy"][0] - cx) ** 2 + (p["xy"][1] - cy) ** 2) for p in pontos])
p_hid = XYZ(cx + raio + ft(4000), cy, nivel_base.Elevation)
if sym_hid is not None:
    if not sym_hid.IsActive:
        sym_hid.Activate()
        doc.Regenerate()
    doc.Create.NewFamilyInstance(p_hid, sym_hid, nivel_base, StructuralType.NonStructural)
    print("hidrometro colocado: " + sym_hid.FamilyName + " :: " + nm(sym_hid))
else:
    print("!! cavalete DN " + dn_hid + " nao encontrado")

# =============================================================== REDE
z_barr = ft(H_BARRILETE)
z_ponto = ft(H_PONTO_AGUA)
z_res = nivel_topo.Elevation

d_alim = diametro(q_total)

# 1) alimentador predial: cavalete -> base da coluna -> topo (reservatorio)
p_a1 = XYZ(p_hid.X, p_hid.Y, z_ponto)
p_a2 = XYZ(p_res.X, p_res.Y, z_ponto)
criar_tubo(p_a1, p_a2, d_alim, "alimentador predial (horizontal)")
criar_tubo(p_a2, XYZ(p_res.X, p_res.Y, z_res), d_alim, "alimentador predial (subida)")

# 2) coluna de descida do reservatorio ate o barrilete
criar_tubo(XYZ(p_res.X, p_res.Y, z_res), XYZ(p_res.X, p_res.Y, z_barr),
           diametro(q_total), "coluna de descida")

# 3) barrilete + ramais: da coluna ate cada peca, no plano do barrilete
#    ordena por distancia para o trecho troncal servir o peso acumulado
pontos.sort(key=lambda p: math.sqrt((p["xy"][0] - p_res.X) ** 2 + (p["xy"][1] - p_res.Y) ** 2))

peso_restante = peso_total
p_ant = XYZ(p_res.X, p_res.Y, z_barr)

for i, p in enumerate(pontos):
    q_tramo = C * math.sqrt(max(peso_restante, 0.01))
    d_tramo = diametro(q_tramo)

    # trecho do barrilete ate a vertical desta peca
    p_sobre = XYZ(p["xy"][0], p["xy"][1], z_barr)
    criar_tubo(p_ant, p_sobre, d_tramo,
               "barrilete {0} (peso acum. {1:.2f})".format(i + 1, peso_restante))

    # sub-ramal: descida ate o ponto de agua
    q_peca = C * math.sqrt(p["peso"])
    criar_tubo(p_sobre, XYZ(p["xy"][0], p["xy"][1], z_ponto), diametro(q_peca),
               "sub-ramal {0} (peso {1:.2f})".format(i + 1, p["peso"]))

    peso_restante -= p["peso"]
    p_ant = p_sobre

doc.Regenerate()
t.Commit()

# ------------------------------------------------------------ relatorio
print("")
print("=== TRECHOS CRIADOS (" + str(len(criados)) + ") ===")
for (rot, d, comp) in criados:
    print("  DN {0:<4} {1:8.0f} mm   {2}".format(d, comp, rot))

if erros:
    print("")
    print("=== ERROS (" + str(len(erros)) + ") ===")
    for (rot, e) in erros:
        print("  {0:34} {1}".format(rot[:34], e))

comp_total = sum([c[2] for c in criados])
print("")
print("comprimento total de tubulacao: {0:.2f} m".format(comp_total / 1000.0))
print("tubos no modelo: " + str(
    FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PipeCurves)
    .WhereElementIsNotElementType().GetElementCount()))
print("conexoes geradas: " + str(
    FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PipeFitting)
    .WhereElementIsNotElementType().GetElementCount()))
