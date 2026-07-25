# -*- coding: utf-8 -*-
"""M0 - Auditoria de modelo hidrossanitario (versao bridge).

Mesma logica do botao pyRevit, mas adaptada para rodar via pyRevit Routes:
- `doc` ja vem injetado no namespace
- motor e IronPython 2.7 (sem f-strings)
- saida vai para arquivo .md + resumo no stdout capturado
"""
import codecs
import os
import re
from collections import Counter

from Autodesk.Revit.DB import (
    BuiltInCategory,
    BuiltInParameter,
    Element,
    ElementId,
    FamilyInstance,
    FilteredElementCollector,
    ImportInstance,
    Level,
    RoutingPreferenceRuleGroupType,
    StorageType,
    UnitTypeId,
    UnitUtils,
    View,
    ViewSheet,
    ViewType,
)
from Autodesk.Revit.DB.Plumbing import PipeSegment, PipeType, PipingSystemType

PASTA_SAIDA = r"C:\Users\Shadow\Documents\00 - Claude - Revit\auditoria"

CATEGORIAS_HIDRO = [
    ("Pecas hidrossanitarias", BuiltInCategory.OST_PlumbingFixtures),
    ("Equipamentos mecanicos", BuiltInCategory.OST_MechanicalEquipment),
    ("Acessorios de tubulacao", BuiltInCategory.OST_PipeAccessory),
    ("Conexoes de tubulacao", BuiltInCategory.OST_PipeFitting),
    ("Sprinklers", BuiltInCategory.OST_Sprinklers),
    ("Tubulacao", BuiltInCategory.OST_PipeCurves),
    ("Tubulacao flexivel", BuiltInCategory.OST_FlexPipeCurves),
]

# Os membros do enum sao PLURAIS - confirmado por System.Enum.GetNames no Revit 2027.
GRUPOS_ROUTING = [
    "Segments", "Elbows", "Junctions", "Crosses",
    "Transitions", "Unions", "MechanicalJoints", "Caps",
]

linhas = []


def add(texto=""):
    linhas.append(texto)


def mm(valor):
    try:
        return UnitUtils.ConvertFromInternalUnits(valor, UnitTypeId.Millimeters)
    except Exception:
        return valor * 304.8


def nome(el):
    """el.Name falha por ambiguidade em varias classes no IronPython.
    Element.Name.__get__(el) e o acessor confiavel."""
    try:
        return Element.Name.__get__(el)
    except Exception:
        pass
    try:
        return el.Name
    except Exception:
        return "(sem nome)"


def eid(element_id):
    """ElementId.IntegerValue foi trocado por .Value nas versoes novas."""
    try:
        return element_id.Value
    except Exception:
        return element_id.IntegerValue


def coletar(cat):
    return list(
        FilteredElementCollector(doc)
        .OfCategory(cat)
        .WhereElementIsNotElementType()
        .ToElements()
    )


add("# Auditoria de modelo - M0")
add()
add("**Modelo:** `{0}`".format(doc.Title))
add()
add("**Revit:** {0} build {1}".format(
    doc.Application.VersionNumber, doc.Application.VersionBuild))
add()

# ----------------------------------------------- 1. tipos de tubulacao
add("## 1. Tipos de tubulacao e routing preferences")
add()

tipos_tubo = list(FilteredElementCollector(doc).OfClass(PipeType).ToElements())

if not tipos_tubo:
    add("> Nenhum tipo de tubulacao encontrado.")
    add()
else:
    add("| Tipo | " + " | ".join(GRUPOS_ROUTING) + " | Pronto? |")
    add("|---|" + "---|" * (len(GRUPOS_ROUTING) + 1))
    for tipo in tipos_tubo:
        cont = []
        for g_nome in GRUPOS_ROUTING:
            grupo = getattr(RoutingPreferenceRuleGroupType, g_nome, None)
            if grupo is None:
                cont.append("-")
                continue
            try:
                cont.append(str(tipo.RoutingPreferenceManager.GetNumberOfRules(grupo)))
            except Exception:
                cont.append("?")
        ok = cont[0] not in ("0", "-", "?") and cont[1] not in ("0", "-", "?")
        add("| {0} | {1} | {2} |".format(
            nome(tipo), " | ".join(cont), "OK" if ok else "INCOMPLETO"))
    add()

# ------------------------------------------------------- 2. diametros
add("## 2. Diametros disponiveis (pipe segments)")
add()
segmentos = list(FilteredElementCollector(doc).OfClass(PipeSegment).ToElements())
if not segmentos:
    add("> Nenhum segmento carregado.")
    add()
else:
    for seg in segmentos:
        try:
            tam = sorted([mm(s.NominalDiameter) for s in seg.GetSizes()])
            txt = ", ".join(["{0:.0f}".format(t) for t in tam])
            add("- **{0}** ({1} bitolas): {2} mm".format(nome(seg), len(tam), txt))
        except Exception:
            add("- **{0}**: (nao foi possivel ler as bitolas)".format(nome(seg)))
    add()

# --------------------------------------------------------- 3. sistemas
add("## 3. Sistemas de tubulacao")
add()
sistemas = list(FilteredElementCollector(doc).OfClass(PipingSystemType).ToElements())
uso = Counter()
for tubo in coletar(BuiltInCategory.OST_PipeCurves):
    try:
        p = tubo.get_Parameter(BuiltInParameter.RBS_PIPING_SYSTEM_TYPE_PARAM)
        if p:
            st = doc.GetElement(p.AsElementId())
            if st is not None:
                uso[nome(st)] += 1
    except Exception:
        pass

if sistemas:
    add("| Sistema | Abreviacao | Tubos |")
    add("|---|---|---|")
    for s in sorted(sistemas, key=nome):
        try:
            ab = s.Abbreviation
        except Exception:
            ab = ""
        add("| {0} | {1} | {2} |".format(nome(s), ab, uso.get(nome(s), 0)))
    add()

# --------------------------------------------------- 4. familias
add("## 4. Familias e tipos por categoria")
add()
achou = False
for rotulo, cat in CATEGORIAS_HIDRO:
    els = coletar(cat)
    if not els:
        continue
    achou = True
    por_fam = Counter()
    for el in els:
        try:
            sym = getattr(el, "Symbol", None)
            if sym is not None:
                chave = "{0} :: {1}".format(sym.FamilyName, nome(sym))
            else:
                t = doc.GetElement(el.GetTypeId())
                chave = nome(t) if t else "(tipo desconhecido)"
        except Exception:
            chave = "(erro)"
        por_fam[chave] += 1

    add("### {0} - {1} elementos".format(rotulo, len(els)))
    add()
    add("| Familia :: Tipo | Qtd |")
    add("|---|---|")
    for chave, qtd in por_fam.most_common():
        add("| {0} | {1} |".format(chave, qtd))
    add()

if not achou:
    add("> Nenhum elemento hidrossanitario encontrado.")
    add()

# ------------------------------------------------------- 5. parametros
add("## 5. Parametros preenchidos nas pecas hidrossanitarias")
add()
pecas = coletar(BuiltInCategory.OST_PlumbingFixtures)
preench = Counter()
for peca in pecas[:200]:
    try:
        for p in peca.Parameters:
            if p.IsReadOnly or not p.HasValue:
                continue
            if p.StorageType == StorageType.String:
                if not (p.AsString() or "").strip():
                    continue
            elif p.StorageType == StorageType.ElementId:
                if eid(p.AsElementId()) == -1:
                    continue
            preench[p.Definition.Name] += 1
    except Exception:
        pass

if preench:
    add("Amostra de {0} peca(s) de {1}.".format(min(200, len(pecas)), len(pecas)))
    add()
    add("| Parametro | Pecas com valor |")
    add("|---|---|")
    for k, v in preench.most_common(40):
        add("| {0} | {1} |".format(k, v))
    add()
else:
    add("> Nenhuma peca hidrossanitaria com parametros preenchidos.")
    add()

# ----------------------------------------------------- 6. nomenclatura
add("## 6. Nomenclatura")
add()
niveis = sorted(
    FilteredElementCollector(doc).OfClass(Level).ToElements(),
    key=lambda l: l.Elevation)
add("### Niveis")
add()
for n in niveis:
    add("- `{0}` - {1:.0f} mm".format(nome(n), mm(n.Elevation)))
add()

folhas = list(FilteredElementCollector(doc).OfClass(ViewSheet).ToElements())
add("### Folhas ({0})".format(len(folhas)))
add()
for f in sorted(folhas, key=lambda x: x.SheetNumber)[:40]:
    add("- `{0}` - {1}".format(f.SheetNumber, f.Name))
if len(folhas) > 40:
    add("- ... e mais {0}".format(len(folhas) - 40))
add()

vistas = [v for v in FilteredElementCollector(doc).OfClass(View).ToElements()
          if not v.IsTemplate and v.ViewType != ViewType.Internal]
pref = Counter()
for v in vistas:
    m = re.match(r"^([A-Za-z0-9]+)[\s_\-]", nome(v))
    pref[m.group(1) if m else "(sem prefixo)"] += 1

add("### Vistas ({0}) - prefixos".format(len(vistas)))
add()
add("| Prefixo | Vistas |")
add("|---|---|")
for k, v in pref.most_common(20):
    add("| {0} | {1} |".format(k, v))
add()

# ------------------------------------------------------ 7. health check
add("## 7. Health check")
add()
avisos = list(doc.GetWarnings())
add("- **Warnings:** {0}".format(len(avisos)))
if avisos:
    tipos_av = Counter()
    for a in avisos:
        try:
            tipos_av[a.GetDescriptionText()] += 1
        except Exception:
            pass
    add()
    add("| Warning | Ocorrencias |")
    add("|---|---|")
    for k, v in tipos_av.most_common(15):
        add("| {0} | {1} |".format(k[:110], v))
    add()

in_place = []
for i in FilteredElementCollector(doc).OfClass(FamilyInstance).ToElements():
    try:
        if i.Symbol.Family.IsInPlace:
            in_place.append(i)
    except Exception:
        pass
add("- **Familias in-place:** {0}".format(len(in_place)))

imports = list(FilteredElementCollector(doc).OfClass(ImportInstance).ToElements())
nao_vinc = [i for i in imports if not i.IsLinked]
add("- **CAD importado (nao vinculado):** {0}".format(len(nao_vinc)))
for imp in nao_vinc[:10]:
    t = doc.GetElement(imp.GetTypeId())
    add("  - `{0}`".format(nome(t) if t else "?"))

em_folha = set()
for f in folhas:
    try:
        for vid in f.GetAllPlacedViews():
            em_folha.add(eid(vid))
    except Exception:
        pass
orfas = [v for v in vistas if eid(v.Id) not in em_folha]
add("- **Vistas fora de folha:** {0} de {1}".format(len(orfas), len(vistas)))

grupos = coletar(BuiltInCategory.OST_IOSModelGroups)
add("- **Grupos de modelo:** {0}".format(len(grupos)))
add()
add("---")
add()
add("_Gerado por revit-hydro-designer (M0)._")

# ------------------------------------------------------------ gravacao
if not os.path.isdir(PASTA_SAIDA):
    os.makedirs(PASTA_SAIDA)

seguro = re.sub(r"[^A-Za-z0-9_\-]", "_", doc.Title)
destino = os.path.join(PASTA_SAIDA, "auditoria_{0}.md".format(seguro))

f = codecs.open(destino, "w", encoding="utf-8")
f.write("\n".join(linhas))
f.close()

print("OK -> " + destino)
print("tipos_tubo={0} sistemas={1} pecas={2} warnings={3} inplace={4} cad={5} orfas={6}/{7}".format(
    len(tipos_tubo), len(sistemas), len(pecas), len(avisos),
    len(in_place), len(nao_vinc), len(orfas), len(vistas)))
