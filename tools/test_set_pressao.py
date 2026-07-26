# -*- coding: utf-8 -*-
import codecs, json, os
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Element, Transaction

if "RAIZ" in globals():
    RAIZ = globals()["RAIZ"]
elif "__file__" in globals():
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    RAIZ = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
else:
    RAIZ = os.environ.get("HYDRO_PROJECT_ROOT", os.getcwd())
f = codecs.open(os.path.join(RAIZ, "data", "familias_pecas.json"), "r", encoding="utf-8")
FAM = json.loads(f.read())
f.close()

P = FAM["parametros"]

fixtures = (FilteredElementCollector(doc)
            .OfCategory(BuiltInCategory.OST_PlumbingFixtures)
            .WhereElementIsNotElementType()
            .ToElements())

el = fixtures[0]
t = Transaction(doc, "test set")
t.Start()
p_pc = el.LookupParameter(P["pressao_calculada"])
if p_pc:
    print("Before Set: AsDouble={0}, AsValueString={1}".format(p_pc.AsDouble(), p_pc.AsValueString()))
    p_pc.Set(4.147)
    doc.Regenerate()
    print("After Set: AsDouble={0}, AsValueString={1}".format(p_pc.AsDouble(), p_pc.AsValueString()))
t.Commit()
