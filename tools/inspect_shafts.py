# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Element, RevitLinkInstance

print("=== SEARCHING FOR SHAFTS AND VERTICAL OPENINGS IN MODEL ===")
doc_list = [doc]

links = FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements()
for l in links:
    try:
        ldoc = l.GetLinkDocument()
        if ldoc is not None:
            doc_list.append(ldoc)
    except Exception:
        pass

shafts_found = []
for d in doc_list:
    try:
        title = d.Title
        # 1. Shaft openings category
        shaft_elems = FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_ShaftOpening).ToElements()
        for s in shaft_elems:
            bb = s.get_BoundingBox(None)
            if bb:
                shafts_found.append({"doc": title, "type": "Shaft Opening", "bb": bb, "center": (bb.Min + bb.Max) * 0.5})
                
        # 2. Rooms named Shaft / Duto
        rooms = FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_Rooms).ToElements()
        for r in rooms:
            try:
                nm = Element.Name.__get__(r).lower()
                if "shaft" in nm or "duto" in nm or "prumada" in nm or "servico" in nm:
                    bb = r.get_BoundingBox(None)
                    if bb:
                        shafts_found.append({"doc": title, "type": "Room " + nm, "bb": bb, "center": (bb.Min + bb.Max) * 0.5})
            except Exception:
                pass
    except Exception as ex:
        print("Error inspecting doc:", ex)

print("Found {0} shaft spaces:".format(len(shafts_found)))
for s in shafts_found:
    c = s["center"]
    print("  Doc: {0:20} | Type: {1:20} | Center: (X={2:.2f}, Y={3:.2f} m)".format(
        s["doc"], s["type"], c.X * 0.3048, c.Y * 0.3048
    ))
