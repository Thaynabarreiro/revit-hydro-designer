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

fixtures = (FilteredElementCollector(doc)
            .OfCategory(BuiltInCategory.OST_PlumbingFixtures)
            .WhereElementIsNotElementType()
            .ToElements())

el = fixtures[0]
print("Testing LookupParameter on element {0}:".format(Element.Name.__get__(el)))

for k, name in P.items():
    p = el.LookupParameter(name)
    print("Key: {0:20} Name: {1:45} Found: {2}".format(k, repr(name), p is not None))
    if p is not None:
        print("   StorageType: {0}, IsReadOnly: {1}".format(p.StorageType, p.IsReadOnly))
