# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Element

fixtures = (FilteredElementCollector(doc)
            .OfCategory(BuiltInCategory.OST_PlumbingFixtures)
            .WhereElementIsNotElementType()
            .ToElements())

print("Checking ALL connectors on {0} fixtures:".format(len(fixtures)))
for p in fixtures:
    try:
        f = p.Symbol.FamilyName
        cm = p.MEPModel.ConnectorManager
        systems = [str(c.PipeSystemType) for c in cm.Connectors]
        print("  Fixture: {0:45} | Systems: {1}".format(f, systems))
    except Exception as ex:
        pass
