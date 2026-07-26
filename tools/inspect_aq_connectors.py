# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Element

fixtures = (FilteredElementCollector(doc)
            .OfCategory(BuiltInCategory.OST_PlumbingFixtures)
            .WhereElementIsNotElementType()
            .ToElements())

print("Checking DomesticHotWater connectors on {0} fixtures:".format(len(fixtures)))
aq_count = 0
for p in fixtures:
    try:
        f = p.Symbol.FamilyName
        cm = p.MEPModel.ConnectorManager
        con_aq = None
        for c in cm.Connectors:
            if str(c.PipeSystemType) == "DomesticHotWater":
                con_aq = c
                break
        if con_aq:
            aq_count += 1
            print("  AQ Fixture: {0:40} | Connector Origin: Z={1:.2f}".format(f, con_aq.Origin.Z))
    except Exception as ex:
        pass
print("Total fixtures with Hot Water connector: {0}".format(aq_count))
