# -*- coding: utf-8 -*-
import math
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Element

res_list = (FilteredElementCollector(doc)
            .OfCategory(BuiltInCategory.OST_PlumbingFixtures)
            .WhereElementIsNotElementType()
            .ToElements())

for p in res_list:
    try:
        f = p.Symbol.FamilyName
        if "Reservatorio" in f:
            p_center = p.Location.Point
            print("Reservoir center: X={0:.2f}, Y={1:.2f}, Z={2:.2f} m".format(
                p_center.X * 0.3048, p_center.Y * 0.3048, p_center.Z * 0.3048
            ))
            cm = p.MEPModel.ConnectorManager
            for i, c in enumerate(cm.Connectors):
                o = c.Origin
                dist_h = math.sqrt((o.X - p_center.X)**2 + (o.Y - p_center.Y)**2) * 0.3048
                try:
                    dir_z = c.CoordinateSystem.BasisZ
                    dir_str = "Dir=(X={0:.2f}, Y={1:.2f}, Z={2:.2f})".format(dir_z.X, dir_z.Y, dir_z.Z)
                except Exception:
                    dir_str = "No Dir"
                print("  Con {0}: Origin=(X={1:.2f}, Y={2:.2f}, Z={3:.2f} m) | Dist_H={4:.2f} m | Radius={5:.1f} mm | {6}".format(
                    i+1, o.X * 0.3048, o.Y * 0.3048, o.Z * 0.3048, dist_h, c.Radius * 304.8 * 2, dir_str
                ))
    except Exception as ex:
        print("Error:", ex)
