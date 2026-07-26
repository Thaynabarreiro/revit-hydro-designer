# -*- coding: utf-8 -*-
import codecs, json, os
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Element

_this_dir = os.path.dirname(os.path.abspath(__file__))
_auto_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
RAIZ = globals().get("RAIZ", os.environ.get("HYDRO_PROJECT_ROOT", _auto_root))
f = codecs.open(os.path.join(RAIZ, "data", "familias_pecas.json"), "r", encoding="utf-8")
FAM = json.loads(f.read())
f.close()

P = FAM["parametros"]

alvos = []
for p in (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures)
          .WhereElementIsNotElementType().ToElements()):
    try:
        f = p.Symbol.FamilyName
    except Exception:
        continue
    if "Reservatorio" in f or "Cavalete" in f:
        continue
    try:
        cm = p.MEPModel.ConnectorManager
        con = None
        for c in cm.Connectors:
            if str(c.PipeSystemType) == "DomesticColdWater":
                con = c
        if con is None:
            continue
    except Exception:
        continue
    alvos.append({"el": p, "org": con.Origin, "fam": f})

print("Found {0} alvos in doc".format(len(alvos)))
for i, item in enumerate(alvos):
    el = item["el"]
    print("--- Alvo {0}: {1} (ID: {2}) ---".format(i, item["fam"], el.Id))
    for k in ["trecho", "pressao_calculada", "pressao_excedente", "comprimento_equiv", "diametro_af"]:
        nome = P.get(k)
        p_param = el.LookupParameter(nome)
        print("  Key: {0:20} ParamName: {1:45} Found: {2}".format(k, repr(nome), p_param is not None))
