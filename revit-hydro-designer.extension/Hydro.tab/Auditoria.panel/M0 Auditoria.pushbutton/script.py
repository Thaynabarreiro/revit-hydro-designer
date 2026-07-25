#! python3
# -*- coding: utf-8 -*-
"""M0 - Auditoria de modelo hidrossanitario.

Extrai as convencoes reais de um projeto (tipos de tubulacao, sistemas, familias,
parametros, nomenclatura) e faz um health check do modelo.

Serve para dois fins:
  1. Ensinar ao gerador automatico qual padrao seguir (fase M0 do plano).
  2. Auditoria de maquete / QA-QC - entregavel de portfolio por si so.

Autora: Thayna Barreiro
"""

import codecs
import os
import re
from collections import Counter, defaultdict

from pyrevit import revit, script

import hydro

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

doc = revit.doc
output = script.get_output()

# Onde o relatorio .md e gravado. Ajuste se mover o projeto.
PASTA_SAIDA = os.path.join(hydro.RAIZ, "auditoria")

# Categorias que interessam a um projeto hidrossanitario.
CATEGORIAS_HIDRO = [
    ("Pecas hidrossanitarias", BuiltInCategory.OST_PlumbingFixtures),
    ("Equipamentos mecanicos", BuiltInCategory.OST_MechanicalEquipment),
    ("Acessorios de tubulacao", BuiltInCategory.OST_PipeAccessory),
    ("Conexoes de tubulacao", BuiltInCategory.OST_PipeFitting),
    ("Sprinklers", BuiltInCategory.OST_Sprinklers),
    ("Tubulacao", BuiltInCategory.OST_PipeCurves),
    ("Tubulacao flexivel", BuiltInCategory.OST_FlexPipeCurves),
]

# Grupos de regra de routing preference que importam para gerar tubulacao.
# Os membros do enum sao PLURAIS - confirmado via System.Enum.GetNames no Revit 2027.
GRUPOS_ROUTING = [
    "Segments",
    "Elbows",
    "Junctions",
    "Crosses",
    "Transitions",
    "Unions",
    "MechanicalJoints",
    "Caps",
]

linhas = []


def add(texto=""):
    """Acumula uma linha no relatorio markdown."""
    linhas.append(texto)


def mm(valor_interno):
    """Converte pes (unidade interna do Revit) para milimetros."""
    try:
        return UnitUtils.ConvertFromInternalUnits(valor_interno, UnitTypeId.Millimeters)
    except Exception:
        return valor_interno * 304.8


def nome(elemento):
    """Nome de um elemento, tolerante a falha.

    `elemento.Name` falha por ambiguidade em varias classes (PipeType,
    PipingSystemType, FamilySymbol). Element.Name.__get__ e o acessor confiavel.
    """
    try:
        return Element.Name.__get__(elemento)
    except Exception:
        pass
    try:
        return elemento.Name
    except Exception:
        return "(sem nome)"


def coletar(categoria):
    # list() e obrigatorio: ToElements() devolve um IList do .NET, que no
    # CPython (Python.NET) nao aceita fatiamento nem indexacao negativa.
    return list(
        FilteredElementCollector(doc)
        .OfCategory(categoria)
        .WhereElementIsNotElementType()
        .ToElements()
    )


# ---------------------------------------------------------------- cabecalho
add("# Auditoria de modelo - M0")
add()
add("**Modelo:** `{0}`".format(doc.Title))
add()
add("**Caminho:** `{0}`".format(doc.PathName or "(nao salvo)"))
add()

# ------------------------------------------------- 1. tipos de tubulacao
add("## 1. Tipos de tubulacao e routing preferences")
add()
add("Se um tipo nao tiver regras de conexao configuradas, o gerador automatico")
add("nao consegue criar a rede com ele. Esta e a checagem do risco 4 do plano.")
add()

tipos_tubo = list(FilteredElementCollector(doc).OfClass(PipeType).ToElements())

if not tipos_tubo:
    add("> **Nenhum tipo de tubulacao encontrado.** O template nao esta preparado")
    add("> para modelagem hidraulica.")
    add()
else:
    add("| Tipo | " + " | ".join(GRUPOS_ROUTING) + " | Pronto? |")
    add("|---|" + "---|" * (len(GRUPOS_ROUTING) + 1))

    for tipo in tipos_tubo:
        contagens = []
        for nome_grupo in GRUPOS_ROUTING:
            grupo = getattr(RoutingPreferenceRuleGroupType, nome_grupo, None)
            if grupo is None:
                contagens.append("-")
                continue
            try:
                contagens.append(str(tipo.RoutingPreferenceManager.GetNumberOfRules(grupo)))
            except Exception:
                contagens.append("?")

        # Um tipo so serve se tiver segmento definido e pelo menos uma curva.
        tem_segmento = contagens[0] not in ("0", "-", "?")
        tem_curva = contagens[1] not in ("0", "-", "?")
        pronto = "OK" if (tem_segmento and tem_curva) else "INCOMPLETO"

        add("| {0} | {1} | {2} |".format(nome(tipo), " | ".join(contagens), pronto))
    add()

# ------------------------------------------------------- 2. diametros
add("## 2. Diametros disponiveis (pipe segments)")
add()

segmentos = list(FilteredElementCollector(doc).OfClass(PipeSegment).ToElements())

if not segmentos:
    add("> Nenhum segmento de tubulacao carregado.")
    add()
else:
    for seg in segmentos:
        try:
            tamanhos = sorted(mm(s.NominalDiameter) for s in seg.GetSizes())
            legivel = ", ".join("{0:.0f}".format(t) for t in tamanhos)
        except Exception:
            legivel = "(nao foi possivel ler)"
        add("- **{0}** ({1} bitolas): {2} mm".format(
            nome(seg), len(tamanhos) if legivel != "(nao foi possivel ler)" else "?", legivel
        ))
    add()

# --------------------------------------------------------- 3. sistemas
add("## 3. Sistemas de tubulacao (PipingSystemType)")
add()
add("Estes sao os sistemas que o gerador vai reproduzir: agua fria, agua quente,")
add("esgoto, ventilacao, pluvial.")
add()

sistemas = list(FilteredElementCollector(doc).OfClass(PipingSystemType).ToElements())
uso_sistema = Counter()

for tubo in coletar(BuiltInCategory.OST_PipeCurves):
    try:
        param = tubo.get_Parameter(BuiltInParameter.RBS_PIPING_SYSTEM_TYPE_PARAM)
        if param:
            tipo_sis = doc.GetElement(param.AsElementId())
            if tipo_sis is not None:
                uso_sistema[nome(tipo_sis)] += 1
    except Exception:
        pass

if sistemas:
    add("| Sistema | Abreviacao | Tubos no modelo |")
    add("|---|---|---|")
    for sis in sorted(sistemas, key=nome):
        try:
            abrev = sis.Abbreviation
        except Exception:
            abrev = ""
        add("| {0} | {1} | {2} |".format(nome(sis), abrev, uso_sistema.get(nome(sis), 0)))
    add()
else:
    add("> Nenhum sistema de tubulacao definido.")
    add()

# --------------------------------------------------- 4. familias hidro
add("## 4. Familias e tipos por categoria")
add()

inventario = {}

for rotulo, categoria in CATEGORIAS_HIDRO:
    elementos = coletar(categoria)
    if not elementos:
        continue

    por_familia = Counter()
    for el in elementos:
        try:
            simbolo = getattr(el, "Symbol", None)
            if simbolo is not None:
                chave = "{0} :: {1}".format(simbolo.FamilyName, nome(simbolo))
            else:
                tipo = doc.GetElement(el.GetTypeId())
                chave = nome(tipo) if tipo else "(tipo desconhecido)"
        except Exception:
            chave = "(erro ao ler tipo)"
        por_familia[chave] += 1

    inventario[rotulo] = por_familia

    add("### {0} - {1} elementos".format(rotulo, len(elementos)))
    add()
    add("| Familia :: Tipo | Qtd |")
    add("|---|---|")
    for chave, qtd in por_familia.most_common():
        add("| {0} | {1} |".format(chave, qtd))
    add()

if not inventario:
    add("> Nenhum elemento hidrossanitario encontrado neste modelo.")
    add()

# ------------------------------------------------------- 5. parametros
add("## 5. Parametros preenchidos nas pecas hidrossanitarias")
add()
add("Mostra quais parametros voce de fato usa. O gerador deve preencher os mesmos.")
add()

pecas = coletar(BuiltInCategory.OST_PlumbingFixtures)
preenchidos = Counter()
total_pecas = len(pecas)

for peca in pecas[:200]:  # amostra: 200 pecas ja e representativo
    try:
        for p in peca.Parameters:
            if p.IsReadOnly or not p.HasValue:
                continue
            if p.StorageType == StorageType.String:
                if not (p.AsString() or "").strip():
                    continue
            elif p.StorageType == StorageType.ElementId:
                if p.AsElementId() == ElementId.InvalidElementId:
                    continue
            preenchidos[p.Definition.Name] += 1
    except Exception:
        pass

if preenchidos:
    add("Amostra de {0} peca(s) de um total de {1}.".format(
        min(200, total_pecas), total_pecas))
    add()
    add("| Parametro | Pecas com valor |")
    add("|---|---|")
    for param_nome, qtd in preenchidos.most_common(40):
        add("| {0} | {1} |".format(param_nome, qtd))
    add()
else:
    add("> Nenhuma peca hidrossanitaria com parametros preenchidos.")
    add()

# ----------------------------------------------------- 6. nomenclatura
add("## 6. Nomenclatura")
add()

niveis = sorted(
    FilteredElementCollector(doc).OfClass(Level).ToElements(),
    key=lambda l: l.Elevation,
)
add("### Niveis")
add()
for nivel in niveis:
    add("- `{0}` - elevacao {1:.0f} mm".format(nome(nivel), mm(nivel.Elevation)))
add()

folhas = list(FilteredElementCollector(doc).OfClass(ViewSheet).ToElements())
add("### Folhas ({0})".format(len(folhas)))
add()
if folhas:
    for folha in sorted(folhas, key=lambda f: f.SheetNumber)[:40]:
        add("- `{0}` - {1}".format(folha.SheetNumber, folha.Name))
    if len(folhas) > 40:
        add("- ... e mais {0} folha(s)".format(len(folhas) - 40))
else:
    add("> Nenhuma folha no modelo.")
add()

# Vistas: detectar padroes de nomenclatura por prefixo.
vistas = [
    v for v in FilteredElementCollector(doc).OfClass(View).ToElements()
    if not v.IsTemplate and v.ViewType != ViewType.Internal
]
prefixos = Counter()
for vista in vistas:
    match = re.match(r"^([A-Za-z0-9]+)[\s_\-]", nome(vista))
    prefixos[match.group(1) if match else "(sem prefixo)"] += 1

add("### Vistas ({0}) - prefixos detectados".format(len(vistas)))
add()
add("| Prefixo | Vistas |")
add("|---|---|")
for prefixo, qtd in prefixos.most_common(20):
    add("| {0} | {1} |".format(prefixo, qtd))
add()

# ------------------------------------------------------ 7. health check
add("## 7. Health check do modelo")
add()

avisos = doc.GetWarnings()
add("- **Warnings:** {0}".format(len(avisos)))

if avisos:
    por_tipo = Counter()
    for aviso in avisos:
        try:
            por_tipo[aviso.GetDescriptionText()] += 1
        except Exception:
            pass
    add()
    add("| Warning | Ocorrencias |")
    add("|---|---|")
    for descricao, qtd in por_tipo.most_common(15):
        add("| {0} | {1} |".format(descricao[:110], qtd))
    add()

# Familias in-place: dificultam coordenacao e quantitativos.
in_place = []
for inst in FilteredElementCollector(doc).OfClass(FamilyInstance).ToElements():
    try:
        if inst.Symbol.Family.IsInPlace:
            in_place.append(inst)
    except Exception:
        pass
add("- **Familias in-place:** {0}".format(len(in_place)))

# CAD importado (nao vinculado) e um classico de auditoria.
importados = list(FilteredElementCollector(doc).OfClass(ImportInstance).ToElements())
nao_vinculados = [i for i in importados if not i.IsLinked]
add("- **CAD importado (nao vinculado):** {0}".format(len(nao_vinculados)))
for imp in nao_vinculados[:10]:
    add("  - `{0}`".format(nome(doc.GetElement(imp.GetTypeId())) or "?"))

# Vistas orfas: nao estao em nenhuma folha.
em_folha = set()
for folha in folhas:
    try:
        for vid in folha.GetAllPlacedViews():
            em_folha.add(vid.IntegerValue)
    except Exception:
        pass
orfas = [v for v in vistas if v.Id.IntegerValue not in em_folha]
add("- **Vistas fora de folha:** {0} de {1}".format(len(orfas), len(vistas)))

# Grupos podem esconder inconsistencia entre instancias.
grupos = coletar(BuiltInCategory.OST_IOSModelGroups)
add("- **Grupos de modelo:** {0}".format(len(grupos)))
add()

# ----------------------------------------------------------- gravacao
add("---")
add()
add("_Relatorio gerado pela extensao revit-hydro-designer (M0)._")

conteudo = "\n".join(linhas)

if not os.path.isdir(PASTA_SAIDA):
    os.makedirs(PASTA_SAIDA)

nome_seguro = re.sub(r"[^A-Za-z0-9_\-]", "_", doc.Title)
destino = os.path.join(PASTA_SAIDA, "auditoria_{0}.md".format(nome_seguro))

with codecs.open(destino, "w", encoding="utf-8") as arquivo:
    arquivo.write(conteudo)

# ------------------------------------------------------------- na tela
output.print_md("# Auditoria M0 concluida")
output.print_md("**Modelo:** {0}".format(doc.Title))
output.print_md("")
output.print_md("| Indicador | Valor |")
output.print_md("|---|---|")
output.print_md("| Tipos de tubulacao | {0} |".format(len(tipos_tubo)))
output.print_md("| Sistemas de tubulacao | {0} |".format(len(sistemas)))
output.print_md("| Pecas hidrossanitarias | {0} |".format(total_pecas))
output.print_md("| Warnings | {0} |".format(len(avisos)))
output.print_md("| Familias in-place | {0} |".format(len(in_place)))
output.print_md("| CAD importado | {0} |".format(len(nao_vinculados)))
output.print_md("| Vistas fora de folha | {0} / {1} |".format(len(orfas), len(vistas)))
output.print_md("")
output.print_md("Relatorio completo gravado em:")
output.print_md("`{0}`".format(destino))
