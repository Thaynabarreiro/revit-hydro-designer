# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Element

print("=== SEARCHING FOR SANITARY DRAINAGE (ESG) INFRASTRUCTURE FAMILIES ===")
symbols = (FilteredElementCollector(doc)
           .OfCategory(BuiltInCategory.OST_PlumbingFixtures)
           .WhereElementIsElementType()
           .ToElements())

esg_families = {}
for s in symbols:
    try:
        fam = s.FamilyName
        if "ESG" in fam or "Gordura" in fam or "Caixa" in fam or "Ralo" in fam or "Siphoned" in fam or "Fossa" in fam:
            esg_families.setdefault(fam, []).append(Element.Name.__get__(s))
    except Exception:
        pass

print("Found {0} sanitary family symbols:".format(len(esg_families)))
for fam, types in esg_families.items():
    print("  Family: {0}".format(fam))
    for t in types[:3]:
        print("    Type: {0}".format(t))
