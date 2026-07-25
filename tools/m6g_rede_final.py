# -*- coding: utf-8 -*-
"""M6g - Rede ortogonal final: faixas + dois ramos a partir da coluna.

Evolucao do m6e. Naquele, cada peca ganhava seu proprio no na espinha; pecas
proximas em Y deixavam o trecho entre nos curto demais para o corpo do te
caber, e 6 de 12 conexoes falhavam com "failed to insert tee".

Aqui as pecas sao agrupadas em FAIXAS ao longo do eixo da espinha. Cada faixa
tem um unico no; dela sai um ramal em X que atende todas as pecas da faixa:

    coluna (Z)
      |
    no0 --- espinha (Y) ---> no da faixa 1 ---> no da faixa 2 ---> ...
                                  |                   |
                              ramal (X) ---+---+   ramal (X) ---+
                                           |   |                |
                                      descida  descida      descida
                                        (Z)      (Z)           (Z)

Todo encontro continua sendo de 90 graus, e os trechos ficam longos o bastante
para as conexoes caberem.

Corrige tambem a colocacao do reservatorio: NewFamilyInstance soma o Z do ponto
a cota do nivel, entao passar a cota do nivel dobrava a altura.
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
RAIZ = globals().get("RAIZ", "C:/Users/Shadow/Documents/00 - Claude - Revit")
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
TOL = 0.05          # ~15 mm: mesmo alinhamento
BANDA_MM = 900.0    # pecas dentro desta faixa em Y compartilham um no
MIN_SEG_MM = 250.0  # trecho menor que isto nao comporta conexao


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

pecas, res_inst = [], None
for p in (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures)
          .WhereElementIsNotElementType().ToElements()):
    try:
        f = p.Symbol.FamilyName
    except Exception:
        continue
    if "Reservatorio" in f:
        res_inst = p
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

if not pecas:
    raise Exception("nenhuma peca com conector de agua fria")

peso_total = sum([x["peso"] for x in pecas])
# O barrilete precisa ficar ACIMA de todos os pontos de utilizacao: chuveiros
# conectam a 3100 mm, o que deixava a "descida" com 200 mm e sem espaco.
z_top_peca = max([p["org"].Z for p in pecas])
z_barr = max(ft(H_BARRILETE), z_top_peca + ft(400.0))
print("barrilete em z = {0:.0f} mm (ponto mais alto: {1:.0f} mm)".format(
    mm(z_barr), mm(z_top_peca)))

# Publica a geometria adotada para o M9 calcular sobre o que foi realmente
# modelado. Antes o M9 assumia 2900 mm fixo e subestimava as descidas.
_geo = codecs.open(os.path.join(D, "rede_geometria.json"), "w", encoding="utf-8")
_geo.write(json.dumps({
    "z_barrilete_mm": round(mm(z_barr), 1),
    "z_ponto_mais_alto_mm": round(mm(z_top_peca), 1),
    "_sobre": "Escrito pelo roteador. O M9 le daqui a altura real do barrilete.",
}, indent=2))
_geo.close()


# ================================================= T0: corrigir reservatorio
t = Transaction(doc, "M6g - corrigir cota do reservatorio")
t.Start()
if res_inst is not None:
    try:
        pr = res_inst.Location.Point
        z_certo = nivel_topo.Elevation
        if abs(pr.Z - z_certo) > ft(50.0):
            res_inst.Location.Move(XYZ(0, 0, z_certo - pr.Z))
            print("reservatorio reposicionado: {0:.2f} m -> {1:.2f} m".format(
                mm(pr.Z) / 1000.0, mm(z_certo) / 1000.0))
    except Exception as e:
        print("aviso ao reposicionar: " + str(e)[:60])
t.Commit()

p_res = res_inst.Location.Point if res_inst is not None else XYZ(
    sum([x["org"].X for x in pecas]) / len(pecas),
    sum([x["org"].Y for x in pecas]) / len(pecas), nivel_topo.Elevation)
x_esp = p_res.X

# ------------------------------------------------------------- faixas
pecas.sort(key=lambda x: x["org"].Y)
faixas = []
for pc in pecas:
    if faixas and abs(mm(pc["org"].Y) - mm(faixas[-1]["y_ref"])) <= BANDA_MM:
        faixas[-1]["pecas"].append(pc)
    else:
        faixas.append({"y_ref": pc["org"].Y, "pecas": [pc]})
for fx in faixas:
    fx["y"] = sum([p["org"].Y for p in fx["pecas"]]) / len(fx["pecas"])
    fx["peso"] = sum([p["peso"] for p in fx["pecas"]])

# Uma espinha unica nao pode ir e voltar sobre a mesma linha. Divide-se em dois
# ramos a partir da coluna, cada um monotonico em Y - que e como um barrilete
# real se comporta quando ha consumo dos dois lados da prumada.
ramo_pos = sorted([f for f in faixas if f["y"] >= p_res.Y], key=lambda f: f["y"])
ramo_neg = sorted([f for f in faixas if f["y"] < p_res.Y], key=lambda f: -f["y"])
ramos = [r for r in (ramo_pos, ramo_neg) if r]

print("pecas: {0} | faixas: {1} | ramos: {2} | peso: {3:.2f}".format(
    len(pecas), len(faixas), len(ramos), peso_total))
for k, r in enumerate(ramos):
    print("  ramo {0}: {1}".format(k + 1, " -> ".join(
        ["y={0:.0f}({1}p)".format(mm(f["y"]), len(f["pecas"])) for f in r])))

# ============================================================ T1: tubos
t = Transaction(doc, "M6g - rede")
t.Start()
for cat in (BuiltInCategory.OST_PipeCurves, BuiltInCategory.OST_PipeFitting):
    for e in (FilteredElementCollector(doc).OfCategory(cat)
              .WhereElementIsNotElementType().ToElements()):
        try:
            if doc.GetElement(e.Id) is None:
                continue
            col = System.Collections.Generic.List[ElementId]()
            col.Add(e.Id)
            doc.Delete(col)
        except Exception:
            pass

erros = []


def tubo(p1, p2, d, rot):
    if p1.DistanceTo(p2) < ft(MIN_SEG_MM):
        return None
    try:
        pi = Pipe.Create(doc, sistema.Id, tipo_tubo.Id, nivel_base.Id, p1, p2)
        set_dn(pi, d)
        return pi
    except Exception as e:
        erros.append((rot, str(e)[:60]))
        return None


no0 = XYZ(x_esp, p_res.Y, z_barr)
coluna = tubo(XYZ(p_res.X, p_res.Y, nivel_topo.Elevation), no0,
              diametro(C * math.sqrt(peso_total)), "coluna")

for k, ramo in enumerate(ramos):
    peso_rest = sum([f["peso"] for f in ramo])
    p_ant = no0
    for i, fx in enumerate(ramo):
        p_no = XYZ(x_esp, fx["y"], z_barr)
        fx["p_no"] = p_no
        fx["esp"] = tubo(p_ant, p_no,
                         diametro(C * math.sqrt(max(peso_rest, 0.01))),
                         "espinha {0}.{1}".format(k + 1, i + 1))
        membros = sorted(fx["pecas"], key=lambda p: abs(p["org"].X - x_esp))
        fx["membros"] = membros
        peso_ramal = fx["peso"]
        p_cursor = p_no
        for j, pc in enumerate(membros):
            p_alvo = XYZ(pc["org"].X, fx["y"], z_barr)
            pc["ramal"] = tubo(p_cursor, p_alvo,
                               diametro(C * math.sqrt(max(peso_ramal, 0.01))),
                               "ramal {0}.{1}.{2}".format(k + 1, i + 1, j + 1))
            pc["p_ramal"] = p_alvo
            pc["desc"] = tubo(p_alvo, pc["org"],
                              diametro(C * math.sqrt(pc["peso"])),
                              "descida {0}.{1}.{2}".format(k + 1, i + 1, j + 1))
            p_cursor = p_alvo
            peso_ramal -= pc["peso"]
        p_ant = p_no
        peso_rest -= fx["peso"]
t.Commit()
print("tubos: " + str(FilteredElementCollector(doc).OfCategory(
    BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType().GetElementCount()))

# =================================================== T2: ligar as pecas
t = Transaction(doc, "M6g - ligar pecas")
t.Start()
ligadas, sem_ligar = 0, []
for fx in faixas:
    for pc in fx["pecas"]:
        d = pc.get("desc")
        if d is None:
            sem_ligar.append("sem descida (trecho curto demais)")
            continue
        cp = conector_af(pc["el"])
        ct = conector_perto(d, pc["org"])
        if cp is None or ct is None:
            sem_ligar.append("conector ausente")
            continue
        try:
            if not cp.IsConnected:
                cp.ConnectTo(ct)
            ligadas += 1
        except Exception as e:
            sem_ligar.append(str(e)[:40])
t.Commit()
print("pecas ligadas: {0} de {1}".format(ligadas, len(pecas)))
for s in sem_ligar:
    print("  ! " + s)

# =============================================== T3: tes e joelhos
t = Transaction(doc, "M6g - conexoes")
t.Start()
fit_ok, fit_falha = 0, []


def liga(a, b, ponto, rot, terceiro=None):
    global fit_ok
    if a is None or b is None:
        return
    ca = conector_perto(a, ponto)
    cb = conector_perto(b, ponto)
    if ca is None or cb is None:
        return
    try:
        if terceiro is not None:
            cc = conector_perto(terceiro, ponto)
            if cc is None:
                doc.Create.NewElbowFitting(ca, cb)
            else:
                doc.Create.NewTeeFitting(ca, cb, cc)
        else:
            doc.Create.NewElbowFitting(ca, cb)
        fit_ok += 1
    except Exception as e:
        fit_falha.append((rot, str(e)[:50]))


# pe da coluna: coluna mais o inicio de cada ramo
if coluna is not None and ramos:
    e1 = ramos[0][0].get("esp")
    e2 = ramos[1][0].get("esp") if len(ramos) > 1 else None
    if e2 is not None:
        liga(e1, e2, no0, "te no pe da coluna", terceiro=coluna)
    else:
        liga(coluna, e1, no0, "joelho no pe da coluna")

for k, ramo in enumerate(ramos):
    for i, fx in enumerate(ramo):
        membros = fx.get("membros", [])
        prox = ramo[i + 1].get("esp") if i + 1 < len(ramo) else None
        saida = None
        if membros:
            saida = membros[0].get("ramal") or membros[0].get("desc")
        if prox is not None:
            liga(fx.get("esp"), prox, fx["p_no"],
                 "te faixa {0}.{1}".format(k + 1, i + 1), terceiro=saida)
        else:
            liga(fx.get("esp"), saida, fx["p_no"], "joelho final " + str(k + 1))
        for j, pc in enumerate(membros):
            if pc.get("ramal") is None:
                continue
            prox_r = membros[j + 1].get("ramal") if j + 1 < len(membros) else None
            if prox_r is not None:
                liga(pc["ramal"], prox_r, pc["p_ramal"],
                     "te {0}.{1}.{2}".format(k + 1, i + 1, j + 1),
                     terceiro=pc.get("desc"))
            else:
                liga(pc["ramal"], pc.get("desc"), pc["p_ramal"],
                     "joelho {0}.{1}.{2}".format(k + 1, i + 1, j + 1))
t.Commit()

print("")
print("conexoes criadas : " + str(fit_ok))
print("falhas           : " + str(len(fit_falha)))
for (r, e) in fit_falha:
    print("  {0:26} {1}".format(r[:26], e))
if erros:
    print("erros de tubo:")
    for (r, e) in erros:
        print("  {0:26} {1}".format(r[:26], e))

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
