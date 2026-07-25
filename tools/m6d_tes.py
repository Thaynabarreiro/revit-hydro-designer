# -*- coding: utf-8 -*-
"""M6d - Cria os tes e joelhos nos nos do barrilete.

Etapa final da abordagem B: os tubos ja existem e as pecas ja estao ligadas
aos sub-ramais (m6c). Aqui so se resolvem as juncoes barrilete <-> sub-ramal.

Cada no e tratado isoladamente: uma falha vira linha de relatorio, nao
travamento. Le os ids de data/rede_ids.json.
"""
import codecs
import json
import os

import System
from Autodesk.Revit.DB import (
    BuiltInCategory,
    ElementId,
    FilteredElementCollector,
    SaveOptions,
    Transaction,
    XYZ,
)

D = "C:/Users/Shadow/Documents/00 - Claude - Revit/data"

f = codecs.open(os.path.join(D, "rede_ids.json"), "r", encoding="utf-8")
R = json.loads(f.read())
f.close()


def el(i):
    """ElementId(int) e AMBIGUO no Revit 2027 (colide com BuiltInParameter
    e BuiltInCategory). Tem que ser Int64."""
    if i is None:
        return None
    try:
        return doc.GetElement(ElementId(System.Int64(i)))
    except Exception:
        return None


def conector_perto(pipe, xyz):
    p = XYZ(xyz[0], xyz[1], xyz[2])
    melhor, dmin = None, 1e9
    for c in pipe.ConnectorManager.Connectors:
        d = c.Origin.DistanceTo(p)
        if d < dmin:
            melhor, dmin = c, d
    return melhor


nos = R["nos"]
coluna = el(R.get("coluna"))
print("nos: {0} | coluna: {1}".format(len(nos), "ok" if coluna is not None else "ausente"))

t = Transaction(doc, "M6d - tes e joelhos")
t.Start()

ok, falhas = 0, []

# joelho no pe da coluna (coluna + primeiro trecho do barrilete)
if coluna is not None and nos:
    b0 = el(nos[0]["barr"])
    if b0 is not None:
        try:
            doc.Create.NewElbowFitting(conector_perto(coluna, R["no0"]),
                                       conector_perto(b0, R["no0"]))
            ok += 1
            print("  pe da coluna: joelho OK")
        except Exception as e:
            falhas.append(("pe da coluna", str(e)[:70]))
            print("  pe da coluna: FALHOU - " + str(e)[:55])

# nos do barrilete
for k, n in enumerate(nos):
    vert = el(n["vert"])
    barr = el(n["barr"])
    prox = el(nos[k + 1]["barr"]) if k + 1 < len(nos) else None
    if vert is None or barr is None:
        falhas.append((k + 1, "tubo nao encontrado"))
        continue
    try:
        c_chega = conector_perto(barr, n["no"])
        c_vert = conector_perto(vert, n["no"])
        if prox is not None:
            doc.Create.NewTeeFitting(c_chega, conector_perto(prox, n["no"]), c_vert)
            tipo = "te"
        else:
            doc.Create.NewElbowFitting(c_chega, c_vert)
            tipo = "joelho"
        ok += 1
        print("  no {0}: {1} OK  (peso acum. {2})".format(k + 1, tipo, n.get("peso_acum")))
    except Exception as e:
        falhas.append((k + 1, str(e)[:70]))
        print("  no {0}: FALHOU - {1}".format(k + 1, str(e)[:55]))

t.Commit()

print("")
print("=== RESULTADO ===")
print("  conexoes criadas : " + str(ok))
print("  falhas           : " + str(len(falhas)))
for (k, e) in falhas:
    print("    no {0}: {1}".format(k, e))

print("")
print("tubos    : " + str(FilteredElementCollector(doc).OfCategory(
    BuiltInCategory.OST_PipeCurves).WhereElementIsNotElementType().GetElementCount()))
print("conexoes : " + str(FilteredElementCollector(doc).OfCategory(
    BuiltInCategory.OST_PipeFitting).WhereElementIsNotElementType().GetElementCount()))
print("warnings : " + str(len(doc.GetWarnings())))

o = SaveOptions()
o.Compact = True
doc.Save(o)
print("salvo.")
