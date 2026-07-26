# -*- coding: utf-8 -*-
"""M1 - Reader: le o modelo arquitetonico e extrai os pontos de consumo.

Saida: data/pontos_consumo.json com cada peca classificada, associada a um
ambiente e com vazao/peso da norma ja atribuidos.

Itens ambiguos NAO sao chutados - vao para uma lista REVISAR com o motivo.
"""
import codecs
import json
import os
import re
import unicodedata
from collections import Counter

from Autodesk.Revit.DB import (
    BuiltInCategory,
    Element,
    FilteredElementCollector,
    UnitTypeId,
    UnitUtils,
)

_this_dir = os.path.dirname(os.path.abspath(__file__))
_auto_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
RAIZ = globals().get("RAIZ", os.environ.get("HYDRO_PROJECT_ROOT", _auto_root))
ARQ_NORMA = os.path.join(RAIZ, "data", "pecas_br.json")
ARQ_SAIDA = os.path.join(RAIZ, "data", "pontos_consumo.json")


def nm(el):
    # Guarda contra None: Element.Name.__get__(None) devolve o objeto-propriedade
    # em vez de levantar, e ele nao e serializavel em JSON.
    if el is None:
        return "(?)"
    try:
        v = Element.Name.__get__(el)
        return v if isinstance(v, (str, bytes)) or type(v).__name__ in ('str', 'unicode') else "(?)"
    except Exception:
        return "(?)"


def mm(v):
    try:
        return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.Millimeters)
    except Exception:
        return v * 304.8


def m2(v):
    try:
        return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.SquareMeters)
    except Exception:
        return v * 0.092903


def eid(element_id):
    """No Revit 2027 o Id vem como long, que o json do IronPython nao serializa."""
    try:
        return int(element_id.Value)
    except Exception:
        return int(element_id.IntegerValue)


def normalizar(texto):
    """minusculo, sem acento - para as regex da base baterem."""
    if not texto:
        return ""
    txt = unicodedata.normalize("NFKD", unicode(texto))
    txt = "".join([c for c in txt if not unicodedata.combining(c)])
    return txt.lower()


# ------------------------------------------------------- base da norma
f = codecs.open(ARQ_NORMA, "r", encoding="utf-8")
NORMA = json.loads(f.read())
f.close()

TIPOS = NORMA["tipos"]
REGRAS = NORMA["classificacao"]
REGRAS_AMB = NORMA["ambiente_para_tipo"]


def classificar(nome_familia, nome_tipo):
    """Retorna (tipo, motivo, prioridade).

    prioridade = indice da regra que casou. Menor = regra mais especifica,
    usada para decidir quem manda quando varias pecas formam um mesmo ponto.
    """
    alvo = normalizar(nome_familia + " " + nome_tipo)
    for i, regra in enumerate(REGRAS):
        if re.search(regra["regex"], alvo):
            return regra["tipo"], regra.get("motivo", ""), i
    return "DESCONHECIDO", "nenhuma regra casou", 9999


def desambiguar_por_ambiente(nome_ambiente):
    alvo = normalizar(nome_ambiente)
    for regra in REGRAS_AMB:
        if re.search(regra["regex"], alvo):
            return regra["tipo"]
    return None


# ------------------------------------------------------------ ambientes
# Os ambientes vem do VINCULO da arquitetura; as pecas vem do modelo MEP.
# Essa e a divisao que o projeto adotou: o modelo MEP e dono das pecas, a
# arquitetura entra so como contexto. Ler ambientes do documento ativo
# funcionava quando o arquitetonico estava aberto, e passou a devolver zero
# assim que o fluxo mudou para o modelo hidro.
from Autodesk.Revit.DB import RevitLinkInstance

doc_ambientes = doc
TR_LINK = None
for li in FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements():
    ld = li.GetLinkDocument()
    if ld is None:
        continue
    n_salas = (FilteredElementCollector(ld).OfCategory(BuiltInCategory.OST_Rooms)
               .WhereElementIsNotElementType().GetElementCount())
    if n_salas:
        doc_ambientes = ld
        TR_LINK = li.GetTotalTransform()
        break

if doc_ambientes is not doc:
    print("ambientes lidos do vinculo: " + doc_ambientes.Title)
else:
    print("ambientes lidos do proprio documento")

ambientes = []
for r in (FilteredElementCollector(doc_ambientes)
          .OfCategory(BuiltInCategory.OST_Rooms)
          .WhereElementIsNotElementType()
          .ToElements()):
    try:
        if not r.Area or r.Area <= 0:
            continue  # ambiente nao colocado
        ambientes.append({
            "id": eid(r.Id),
            "nome": nm(r),
            "area_m2": round(m2(r.Area), 2),
            "nivel": nm(doc_ambientes.GetElement(r.LevelId)),
            "_el": r,
        })
    except Exception:
        pass


def ambiente_do_ponto(ponto):
    """Descobre em qual ambiente uma coordenada cai.

    O ponto vem do modelo MEP (coordenadas do host); os ambientes vivem no
    vinculo. IsPointInRoom espera coordenadas do documento do ambiente, entao
    o ponto e levado de volta pela transformacao inversa do vinculo.
    """
    p = ponto
    if TR_LINK is not None:
        try:
            p = TR_LINK.Inverse.OfPoint(ponto)
        except Exception:
            p = ponto
    for amb in ambientes:
        try:
            if amb["_el"].IsPointInRoom(p):
                return amb
        except Exception:
            continue
    return None


# ------------------------------------------------------- coleta bruta
brutos = []
ignorados = Counter()

for peca in (FilteredElementCollector(doc)
             .OfCategory(BuiltInCategory.OST_PlumbingFixtures)
             .WhereElementIsNotElementType()
             .ToElements()):
    try:
        simbolo = peca.Symbol
        fam = simbolo.FamilyName
        tip = nm(simbolo)
    except Exception:
        fam, tip = "(?)", "(?)"

    tipo, motivo, prio = classificar(fam, tip)

    if tipo == "IGNORAR":
        ignorados[fam + " (" + motivo + ")"] += 1
        continue

    try:
        loc = peca.Location.Point
        xyz = [round(mm(loc.X), 1), round(mm(loc.Y), 1), round(mm(loc.Z), 1)]
    except Exception:
        loc, xyz = None, None

    amb = ambiente_do_ponto(loc) if loc is not None else None

    brutos.append({
        "id": eid(peca.Id),
        "familia": fam,
        "tipo_familia": tip,
        "ambiente": amb["nome"] if amb else "(fora de ambiente)",
        "nivel": amb["nivel"] if amb else "(?)",
        "xyz_mm": xyz,
        "_tipo": tipo,
        "_prio": prio,
        "_motivo": motivo,
    })

# ------------------------------------------------------- clusterizacao
# Familias distintas muito proximas sao a MESMA louca modelada em partes
# (cuba + torneira + cuba shared). Sem isso a rede sai superdimensionada.
RAIO = NORMA.get("raio_cluster_mm", 700)

usado = set()
clusters = []

for i, a in enumerate(brutos):
    if i in usado or not a["xyz_mm"]:
        continue
    grupo = [a]
    usado.add(i)
    for j, b in enumerate(brutos):
        if j in usado or not b["xyz_mm"]:
            continue
        if b["ambiente"] != a["ambiente"]:
            continue
        dx = a["xyz_mm"][0] - b["xyz_mm"][0]
        dy = a["xyz_mm"][1] - b["xyz_mm"][1]
        if (dx * dx + dy * dy) ** 0.5 <= RAIO:
            grupo.append(b)
            usado.add(j)
    clusters.append(grupo)

# pecas sem coordenada nao entram em cluster
for i, a in enumerate(brutos):
    if i not in usado:
        clusters.append([a])
        usado.add(i)

# ----------------------------------------------- classificacao final
pontos = []
revisar = []

for grupo in clusters:
    # a regra mais especifica (menor indice) manda no cluster inteiro
    lider = sorted(grupo, key=lambda x: x["_prio"])[0]
    nome_amb = lider["ambiente"]

    if lider["_tipo"] in ("REVISAR", "DESCONHECIDO"):
        sugerido = desambiguar_por_ambiente(nome_amb)
        tipo_final = sugerido
        confianca = "inferido pelo ambiente" if sugerido else "nao resolvido"
    else:
        tipo_final = lider["_tipo"]
        confianca = "regra de nome"

    registro = {
        "id": lider["id"],
        "familia": lider["familia"],
        "tipo_familia": lider["tipo_familia"],
        "ambiente": nome_amb,
        "nivel": lider["nivel"],
        "xyz_mm": lider["xyz_mm"],
        "tipo_peca": tipo_final,
        "confianca": confianca,
        "motivo": lider["_motivo"],
        "familias_agrupadas": [g["familia"] for g in grupo],
        "ids_agrupados": [g["id"] for g in grupo],
    }

    if tipo_final and tipo_final in TIPOS:
        dados = TIPOS[tipo_final]
        registro["desc"] = dados["desc"]
        registro["vazao_ls"] = dados["vazao_ls"]
        registro["peso"] = dados["peso"]
        registro["pressao_min_kpa"] = dados["pressao_min_kpa"]
        registro["esgoto_uhc"] = dados["esgoto_uhc"]
        pontos.append(registro)
    else:
        revisar.append(registro)

# --------------------------------------------------------------- saida
peso_total = sum([p["peso"] for p in pontos])
vazao_max = sum([p["vazao_ls"] for p in pontos])

# Vazao de projeto pelo metodo dos pesos: Q = C * sqrt(soma dos pesos)
# C = 0,30 L/s (NBR 5626) - VALIDAR
C = 0.30
vazao_projeto = C * (peso_total ** 0.5)

resultado = {
    "modelo": doc.Title,
    "norma": NORMA["norma"],
    "resumo": {
        "ambientes_colocados": len(ambientes),
        "pontos_identificados": len(pontos),
        "pontos_a_revisar": len(revisar),
        "peso_total": round(peso_total, 2),
        "vazao_soma_simples_ls": round(vazao_max, 3),
        "vazao_projeto_ls": round(vazao_projeto, 3),
        "coef_C": C,
    },
    "ambientes": [{k: v for k, v in a.items() if k != "_el"} for a in ambientes],
    "pontos_consumo": pontos,
    "revisar": revisar,
    "ignorados": dict(ignorados),
}

if not os.path.isdir(os.path.dirname(ARQ_SAIDA)):
    os.makedirs(os.path.dirname(ARQ_SAIDA))

f = codecs.open(ARQ_SAIDA, "w", encoding="utf-8")
f.write(json.dumps(resultado, indent=2, ensure_ascii=False))
f.close()

# ------------------------------------------------------------ relatorio
print("=== M1 READER ===")
print("modelo: " + doc.Title)
print("ambientes colocados: " + str(len(ambientes)))
print("")
print("--- PONTOS DE CONSUMO IDENTIFICADOS (" + str(len(pontos)) + ") ---")
por_amb = {}
for p in pontos:
    por_amb.setdefault(p["ambiente"], []).append(p)
for amb in sorted(por_amb.keys()):
    print("  " + amb + ":")
    for p in por_amb[amb]:
        agrup = ""
        if len(p["familias_agrupadas"]) > 1:
            agrup = "  (agrupou {0} familias)".format(len(p["familias_agrupadas"]))
        print("    - {0:18} peso={1:<5} vazao={2} L/s   [{3}]{4}".format(
            p["tipo_peca"], p["peso"], p["vazao_ls"], p["confianca"], agrup))

print("")
print("--- A REVISAR (" + str(len(revisar)) + ") ---")
for r in revisar:
    print("    ? {0} :: {1}".format(r["familia"], r["tipo_familia"]))
    print("      ambiente={0}  motivo={1}".format(r["ambiente"], r["motivo"]))

print("")
print("--- IGNORADOS ---")
for k, v in ignorados.most_common():
    print("    x {0} x{1}".format(k, v))

print("")
print("peso total = {0}".format(round(peso_total, 2)))
print("vazao de projeto = {0} L/s  (Q = {1} * raiz({2}))".format(
    round(vazao_projeto, 3), C, round(peso_total, 2)))
print("")
print("-> " + ARQ_SAIDA)
