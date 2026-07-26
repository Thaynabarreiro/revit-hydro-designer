# -*- coding: utf-8 -*-
"""M5a - Coloca as pecas hidrossanitarias no modelo hidro.

Le a arquitetura ATRAVES DO VINCULO (com transformacao de coordenadas),
identifica os pontos de consumo e coloca as familias correspondentes
no modelo hidro, no nivel correto.

Depois disso a engenheira ajusta a vontade - adiciona, remove, move.
O calculo (M2) passa a ler o modelo hidro, nao mais o vinculo.

Nenhum texto acentuado em literal: vem tudo de JSON (ver nota no m8_memorial).
"""
import codecs
import json
import math
import os
import re
import unicodedata

from Autodesk.Revit.DB import (
    BuiltInCategory,
    Element,
    FilteredElementCollector,
    Level,
    RevitLinkInstance,
    StorageType,
    Transaction,
    UnitTypeId,
    UnitUtils,
    XYZ,
)
from Autodesk.Revit.DB.Structure import StructuralType

# Aceita RAIZ injetada pelo chamador (os botoes pyRevit descobrem a raiz a
# partir da propria localizacao). O literal e apenas o fallback do bridge.
_this_dir = os.path.dirname(os.path.abspath(__file__))
_auto_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
RAIZ = globals().get("RAIZ", os.environ.get("HYDRO_PROJECT_ROOT", _auto_root))
D = os.path.join(RAIZ, "data")


def ler(nome):
    f = codecs.open(os.path.join(D, nome), "r", encoding="utf-8")
    x = json.loads(f.read())
    f.close()
    return x


NORMA = ler("pecas_br.json")
CFG = ler("config_projeto.json")
FAM = ler("familias_pecas.json")

TIPOS = NORMA["tipos"]
REGRAS = NORMA["classificacao"]
REGRAS_AMB = NORMA["ambiente_para_tipo"]
RAIO = NORMA.get("raio_cluster_mm", 700)


def nm(e):
    try:
        return Element.Name.__get__(e)
    except Exception:
        return "(?)"


def mm(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.Millimeters)


def ft(v):
    return UnitUtils.ConvertToInternalUnits(v, UnitTypeId.Millimeters)


def norm(t):
    if not t:
        return ""
    t = unicodedata.normalize("NFKD", unicode(t))
    return "".join([c for c in t if not unicodedata.combining(c)]).lower()


def classificar(fam, tip):
    alvo = norm(fam + " " + tip)
    for i, r in enumerate(REGRAS):
        if re.search(r["regex"], alvo):
            return r["tipo"], r.get("motivo", ""), i
    return "DESCONHECIDO", "", 9999


def por_ambiente(nome_amb):
    alvo = norm(nome_amb)
    for r in REGRAS_AMB:
        if re.search(r["regex"], alvo):
            return r["tipo"]
    return None


# ------------------------------------------------------------- vinculo
link = None
for li in FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements():
    ld = li.GetLinkDocument()
    if ld and "Casa A&R" in ld.Title:
        link = li
if link is None:
    raise Exception("vinculo da arquitetura nao carregado")

ldoc = link.GetLinkDocument()
TR = link.GetTotalTransform()
print("vinculo: " + ldoc.Title)

# ------------------------------------------------------------ ambientes
ambientes = []
for r in (FilteredElementCollector(ldoc).OfCategory(BuiltInCategory.OST_Rooms)
          .WhereElementIsNotElementType().ToElements()):
    try:
        if not r.Area or r.Area <= 0:
            continue
        ambientes.append({"nome": nm(r), "el": r})
    except Exception:
        pass
print("ambientes no vinculo: " + str(len(ambientes)))


def ambiente_de(p_link):
    for a in ambientes:
        try:
            if a["el"].IsPointInRoom(p_link):
                return a["nome"]
        except Exception:
            pass
    return "(fora de ambiente)"


# ---------------------------------------------------- coleta + cluster
brutos = []
for pf in (FilteredElementCollector(ldoc).OfCategory(BuiltInCategory.OST_PlumbingFixtures)
           .WhereElementIsNotElementType().ToElements()):
    try:
        s = pf.Symbol
        fam, tip = s.FamilyName, nm(s)
    except Exception:
        continue
    t, motivo, prio = classificar(fam, tip)
    if t == "IGNORAR":
        continue
    try:
        p = pf.Location.Point
    except Exception:
        continue
    brutos.append({"fam": fam, "tip": tip, "p_link": p, "p_host": TR.OfPoint(p),
                   "amb": ambiente_de(p), "tipo": t, "prio": prio})

usado, clusters = set(), []
for i, a in enumerate(brutos):
    if i in usado:
        continue
    grupo = [a]
    usado.add(i)
    for j, b in enumerate(brutos):
        if j in usado or b["amb"] != a["amb"]:
            continue
        d = math.sqrt((mm(a["p_host"].X) - mm(b["p_host"].X)) ** 2 +
                      (mm(a["p_host"].Y) - mm(b["p_host"].Y)) ** 2)
        if d <= RAIO:
            grupo.append(b)
            usado.add(j)
    clusters.append(grupo)

pontos = []
for g in clusters:
    lider = sorted(g, key=lambda x: x["prio"])[0]
    t = lider["tipo"]
    if t in ("REVISAR", "DESCONHECIDO"):
        t = por_ambiente(lider["amb"])
    if not t or t not in TIPOS:
        continue
    pontos.append({"tipo": t, "amb": lider["amb"], "p": lider["p_host"],
                   "origem": "modelo", "n_agrup": len(g)})

print("pontos de consumo (do vinculo): " + str(len(pontos)))

# ------------------------------------------------- pecas complementares
centro_amb = {}
for a in ambientes:
    try:
        centro_amb[a["nome"]] = TR.OfPoint(a["el"].Location.Point)
    except Exception:
        pass

for pc in CFG.get("pecas_complementares", []):
    t = pc["tipo"]
    if t not in TIPOS:
        continue
    amb = pc.get("ambiente", "")
    base = centro_amb.get(amb)
    for k in range(pc.get("quantidade", 1)):
        if base is not None:
            # desloca 600 mm para nao sobrepor o que ja existe no ambiente
            p = XYZ(base.X + ft(600 * (k + 1)), base.Y, base.Z)
        else:
            # sem ambiente (ex.: torneira externa): joga na origem deslocada
            p = XYZ(ft(2000 * (k + 1)), ft(-2000), 0)
        pontos.append({"tipo": t, "amb": amb or "(externo)", "p": p,
                       "origem": "complementar", "n_agrup": 1})

print("total com complementares: " + str(len(pontos)))

# ------------------------------------------------------------- niveis
niveis = sorted(FilteredElementCollector(doc).OfClass(Level).ToElements(),
                key=lambda x: x.Elevation)
nivel_base = niveis[0]
print("nivel de colocacao: " + nm(nivel_base) + " ({0:.0f} mm)".format(mm(nivel_base.Elevation)))


# ------------------------------------------------- resolver familias
def achar_simbolo(nome_familia, nome_tipo=None):
    for s in (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures)
              .WhereElementIsElementType().ToElements()):
        try:
            f = s.FamilyName
        except Exception:
            continue
        if not f.startswith(nome_familia):
            continue
        if nome_tipo is None or nm(s) == nome_tipo:
            return s
    return None


VIS = FAM.get("visibilidade_padrao", {})


def aplicar_visibilidade(inst):
    for chave, val in VIS.items():
        try:
            p = inst.LookupParameter(chave)
            if p and not p.IsReadOnly and p.StorageType == StorageType.Integer:
                p.Set(int(val))
        except Exception:
            pass


# ------------------------------------------------------- colocacao
t = Transaction(doc, "M5 - colocar pecas hidrossanitarias")
t.Start()

colocadas, falhas, usou_generica = [], [], []

for pt in pontos:
    tipo = pt["tipo"]
    mapa = FAM["pecas"].get(tipo, {})
    simbolo = None
    via = "especifica"

    if mapa.get("familia"):
        simbolo = achar_simbolo(mapa["familia"])

    if simbolo is None:
        # fallback: familia generica, com o tipo que identifica a peca
        tipo_gen = TIPOS[tipo].get("tipo_generico")
        if tipo_gen:
            simbolo = achar_simbolo(FAM["generica_af_parede"], tipo_gen)
            if simbolo is None:
                simbolo = achar_simbolo(FAM["generica_af_piso"], tipo_gen)
            via = "generica"

    if simbolo is None:
        falhas.append((tipo, pt["amb"], "familia nao encontrada"))
        continue

    try:
        if not simbolo.IsActive:
            simbolo.Activate()
            doc.Regenerate()
        p = XYZ(pt["p"].X, pt["p"].Y, nivel_base.Elevation)
        inst = doc.Create.NewFamilyInstance(p, simbolo, nivel_base,
                                            StructuralType.NonStructural)
        aplicar_visibilidade(inst)
        colocadas.append((tipo, pt["amb"], simbolo.FamilyName, via, pt["origem"]))
        if via == "generica":
            usou_generica.append((tipo, simbolo.FamilyName + " :: " + nm(simbolo)))
    except Exception as e:
        falhas.append((tipo, pt["amb"], str(e)[:70]))

doc.Regenerate()
t.Commit()

# ------------------------------------------------------------ relatorio
print("")
print("=== PECAS COLOCADAS (" + str(len(colocadas)) + ") ===")
por_amb = {}
for (tp, amb, fam, via, orig) in colocadas:
    por_amb.setdefault(amb, []).append((tp, fam, via, orig))
for amb in sorted(por_amb.keys()):
    print("  " + amb + ":")
    for (tp, fam, via, orig) in por_amb[amb]:
        marca = "" if orig == "modelo" else "  [complementar]"
        gen = "" if via == "especifica" else "  [generica]"
        print("    - {0:18} {1}{2}{3}".format(tp, fam[:48], gen, marca))

if usou_generica:
    print("")
    print("=== USARAM FAMILIA GENERICA ===")
    for (tp, f) in usou_generica:
        print("  {0:18} -> {1}".format(tp, f))

if falhas:
    print("")
    print("=== FALHAS (" + str(len(falhas)) + ") ===")
    for (tp, amb, err) in falhas:
        print("  {0:18} {1:22} {2}".format(tp, amb, err))

print("")
print("instancias de peca no modelo hidro agora: " + str(
    FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures)
    .WhereElementIsNotElementType().GetElementCount()))
