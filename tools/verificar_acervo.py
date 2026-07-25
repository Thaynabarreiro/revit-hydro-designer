# -*- coding: utf-8 -*-
"""Verificacao de acervo - o template tem o que o projeto vai precisar?

Roda ANTES de gerar qualquer coisa. Confere no modelo aberto:

  1. as familias de peca mapeadas em familias_pecas.json
  2. as familias de infraestrutura (reservatorio, hidrometro, fossa...)
  3. o tipo de reservatorio do volume calculado e o cavalete do DN calculado
  4. o sistema de tubulacao de agua fria
  5. os tipos de tubulacao e se tem routing preferences completas
  6. os parametros de calculo nas familias

Sem isso, uma familia ausente vira falha no meio da geracao ou, pior, peca
errada colocada em silencio.

Grava data/acervo.json e devolve um resumo no stdout.
"""
import codecs
import json
import os

from Autodesk.Revit.DB import (
    BuiltInCategory,
    Element,
    FilteredElementCollector,
    RoutingPreferenceRuleGroupType,
    StorageType,
)
from Autodesk.Revit.DB.Plumbing import PipeType, PipingSystemType

RAIZ = globals().get("RAIZ", "C:/Users/Shadow/Documents/00 - Claude - Revit")
D = os.path.join(RAIZ, "data")


def ler(n):
    f = codecs.open(os.path.join(D, n), "r", encoding="utf-8")
    x = json.loads(f.read())
    f.close()
    return x


FAM = ler("familias_pecas.json")
NORMA = ler("pecas_br.json")

try:
    DIM = ler("dimensionamento.json")
except Exception:
    DIM = None


def nm(e):
    try:
        return Element.Name.__get__(e)
    except Exception:
        return "(?)"


# ------------------------------------------------ catalogo do modelo
simbolos = []
for s in (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures)
          .WhereElementIsElementType().ToElements()):
    try:
        simbolos.append((s.FamilyName, nm(s), s))
    except Exception:
        pass

familias = set([f for (f, t, s) in simbolos])


def achar(prefixo, tipo=None):
    """Familia por prefixo; opcionalmente um tipo especifico dentro dela."""
    if not prefixo:
        return None
    for (f, t, s) in simbolos:
        if f.startswith(prefixo) and (tipo is None or t == tipo):
            return (f, t)
    return None


ok, faltando, avisos = [], [], []

# ----------------------------------------------- 1. pecas mapeadas
usados = set()
for chave, dados in FAM.get("pecas", {}).items():
    prefixo = dados.get("familia")
    if not prefixo:
        # sem familia especifica: precisa da generica com o tipo da norma
        tipo_gen = NORMA["tipos"].get(chave, {}).get("tipo_generico")
        alvo = achar(FAM.get("generica_af_parede"), tipo_gen) or \
            achar(FAM.get("generica_af_piso"), tipo_gen)
        if alvo:
            ok.append((chave, "generica :: " + str(tipo_gen)))
            usados.add(alvo[0])
        else:
            faltando.append((chave, "familia generica com o tipo '{0}'".format(tipo_gen)))
        continue
    alvo = achar(prefixo)
    if alvo:
        ok.append((chave, alvo[0]))
        usados.add(alvo[0])
    else:
        faltando.append((chave, prefixo))

# --------------------------------------- 2 e 3. infraestrutura
for chave, dados in FAM.get("infraestrutura", {}).items():
    prefixo = dados.get("familia")
    alvo = achar(prefixo)
    if not alvo:
        faltando.append((chave, prefixo))
        continue
    ok.append((chave, alvo[0]))
    usados.add(alvo[0])

    # o tipo exato que o dimensionamento pediu existe?
    if DIM and chave == "reservatorio":
        vol = str(DIM.get("reservacao", {}).get("volume_adotado_l", ""))
        tipo = dados.get("tipo_por_volume", {}).get(vol)
        if tipo and not achar(prefixo, tipo):
            avisos.append("reservatorio de {0} L: tipo '{1}' nao existe na familia"
                          .format(vol, tipo))
    if DIM and chave == "hidrometro":
        dn = str(DIM.get("hidrometro", {}).get("dn_mm", ""))
        tipo = dados.get("tipo_por_dn", {}).get(dn)
        if tipo and not achar(prefixo, tipo):
            avisos.append("cavalete DN {0}: tipo '{1}' nao existe na familia"
                          .format(dn, tipo))

# ------------------------------------------------ 4. sistema de AF
sis_af = None
for s in FilteredElementCollector(doc).OfClass(PipingSystemType).ToElements():
    try:
        if "AAF" in (s.Abbreviation or ""):
            sis_af = s
    except Exception:
        pass
if sis_af is None:
    for s in FilteredElementCollector(doc).OfClass(PipingSystemType).ToElements():
        n = nm(s)
        if "gua Fria" in n or "gua fria" in n:
            sis_af = s
if sis_af is None:
    faltando.append(("sistema de agua fria", "PipingSystemType com sigla AAF"))

# ------------------------------------- 5. tipos de tubulacao prontos
GRUPOS = ["Segments", "Elbows", "Junctions", "Crosses",
          "Transitions", "Unions", "MechanicalJoints", "Caps"]
tipos_prontos, tipos_incompletos = [], []
for tp in FilteredElementCollector(doc).OfClass(PipeType).ToElements():
    cont = []
    for g in GRUPOS:
        gg = getattr(RoutingPreferenceRuleGroupType, g, None)
        try:
            cont.append(tp.RoutingPreferenceManager.GetNumberOfRules(gg))
        except Exception:
            cont.append(0)
    if cont[0] > 0 and cont[1] > 0:
        tipos_prontos.append(nm(tp))
    else:
        tipos_incompletos.append(nm(tp))

if not tipos_prontos:
    faltando.append(("tipo de tubulacao utilizavel",
                     "nenhum com segmento e curvas configurados"))

# ------------------------------------- 6. parametros de calculo
P = FAM.get("parametros", {})
param_faltando = []
amostra = None
for (f, t, s) in simbolos:
    if f in usados:
        amostra = s
        break
if amostra is not None:
    for chave in ("peso", "vazao", "pressao_min"):
        nome_p = P.get(chave)
        if not nome_p:
            continue
        achou = False
        for portador in (amostra,):
            try:
                pr = portador.LookupParameter(nome_p)
                if pr is not None and pr.StorageType == StorageType.Double:
                    achou = True
            except Exception:
                pass
        if not achou:
            param_faltando.append(nome_p)

# ------------------------------------------------------------ saida
resultado = {
    "modelo": doc.Title,
    "familias_no_modelo": len(familias),
    "ok": [{"peca": a, "familia": b} for (a, b) in ok],
    "faltando": [{"peca": a, "esperado": b} for (a, b) in faltando],
    "avisos": avisos,
    "tipos_tubulacao_prontos": tipos_prontos,
    "tipos_tubulacao_incompletos": tipos_incompletos,
    "sistema_agua_fria": nm(sis_af) if sis_af is not None else None,
    "parametros_ausentes": param_faltando,
    "apto": len(faltando) == 0 and len(tipos_prontos) > 0 and sis_af is not None,
}

f = codecs.open(os.path.join(D, "acervo.json"), "w", encoding="utf-8")
f.write(json.dumps(resultado, indent=2, ensure_ascii=False))
f.close()

print("=== VERIFICACAO DE ACERVO ===")
print("modelo: " + doc.Title)
print("familias de peca no modelo: " + str(len(familias)))
print("")
print("encontradas   : {0}".format(len(ok)))
print("faltando      : {0}".format(len(faltando)))
print("avisos        : {0}".format(len(avisos)))
print("tipos de tubo : {0} prontos, {1} incompletos".format(
    len(tipos_prontos), len(tipos_incompletos)))
print("sistema AF    : " + (nm(sis_af) if sis_af is not None else "NAO ENCONTRADO"))

if faltando:
    print("")
    print("--- FALTANDO ---")
    for (a, b) in faltando:
        print("  {0:20} esperava: {1}".format(a, b))

if avisos:
    print("")
    print("--- AVISOS ---")
    for a in avisos:
        print("  " + a)

if param_faltando:
    print("")
    print("--- PARAMETROS DE CALCULO AUSENTES ---")
    for p in param_faltando:
        print("  " + p)

print("")
print("APTO A GERAR: " + ("SIM" if resultado["apto"] else "NAO"))
print("-> data/acervo.json")
