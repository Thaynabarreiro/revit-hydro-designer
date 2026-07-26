# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Element, Transaction, XYZ
from Autodesk.Revit.DB.Plumbing import Pipe, PipeType, PipingSystemType

print("Testing tank stub vector math...")
res_inst = None
for p in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_PlumbingFixtures).WhereElementIsNotElementType().ToElements():
    if "Reservatorio" in p.Symbol.FamilyName:
        res_inst = p
        break

if res_inst:
    p_center = res_inst.Location.Point
    cm = res_inst.MEPModel.ConnectorManager
    c_res = None
    for c in cm.Connectors:
        if str(c.PipeSystemType) == "DomesticColdWater" and abs(c.Radius * 304.8 * 2 - 50.0) < 10.0:
            dir_v = c.CoordinateSystem.BasisZ
            vec_c = c.Origin - p_center
            if dir_v.DotProduct(vec_c) > 0:
                c_res = c
                break
    if c_res:
        print("Selected connector origin:", c_res.Origin)
        print("Direction:", c_res.CoordinateSystem.BasisZ)
    else:
        print("Connector not matched")
