# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Element

res_list = (FilteredElementCollector(doc)
            .OfCategory(BuiltInCategory.OST_PlumbingFixtures)
            .WhereElementIsNotElementType()
            .ToElements())

for p in res_list:
    try:
        f = p.Symbol.FamilyName
        if "Reservatorio" in f:
            print("Found reservoir instance: {0}".format(f))
            print("  Location Point: Z = {0:.2f} m".format(p.Location.Point.Z * 0.3048))
            cm = p.MEPModel.ConnectorManager
            for i, c in enumerate(cm.Connectors):
                print("  Connector {0}: System={1} | Origin=(X={2:.2f}, Y={3:.2f}, Z={4:.2f} m) | Radius={5:.1f} mm".format(
                    i+1, str(c.PipeSystemType), c.Origin.X * 0.3048, c.Origin.Y * 0.3048, c.Origin.Z * 0.3048, c.Radius * 304.8 * 2
                ))
    except Exception as ex:
        print("Error:", ex)
