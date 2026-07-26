# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Element

print("=== SEARCHING FOR HOT WATER (AQ) FAMILIES IN TEMPLATE ===")
symbols = (FilteredElementCollector(doc)
           .OfCategory(BuiltInCategory.OST_PlumbingFixtures)
           .WhereElementIsElementType()
           .ToElements())

aq_families = {}
for s in symbols:
    try:
        fam = s.FamilyName
        if "AQ" in fam or "Quente" in fam or "Misturador" in fam or "Ducha" in fam:
            aq_families.setdefault(fam, []).append(Element.Name.__get__(s))
    except Exception:
        pass

print("Found {0} hot water family symbols:".format(len(aq_families)))
for fam, types in aq_families.items():
    print("  Family: {0}".format(fam))
    for t in types[:3]:
        print("    Type: {0}".format(t))
