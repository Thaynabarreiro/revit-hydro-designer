# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Element

print("=== INSPECTION OF PLUMBING FIXTURE PARAMETERS ===")
fixtures = (FilteredElementCollector(doc)
            .OfCategory(BuiltInCategory.OST_PlumbingFixtures)
            .WhereElementIsNotElementType()
            .ToElements())

print("Found {0} fixtures".format(len(fixtures)))
if len(fixtures) > 0:
    el = fixtures[0]
    print("Element ID: {0}, Name: {1}, Symbol: {2}".format(el.Id, Element.Name.__get__(el), el.Symbol.FamilyName))
    print("--- Instance Parameters ---")
    for p in el.Parameters:
        try:
            print("  {0:40} | Storage: {1} | ReadOnly: {2} | Value: {3}".format(
                p.Definition.Name, p.StorageType, p.IsReadOnly, p.AsValueString() or p.AsString() or p.AsDouble() or p.AsInteger()
            ))
        except Exception as ex:
            print("  {0:40} | Error: {1}".format(p.Definition.Name, ex))
