# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Element
from Autodesk.Revit.DB.Plumbing import PipeType, PipingSystemType

print("=== CHECKING HOT WATER PIPING SYSTEMS AND PIPE TYPES ===")
systems = FilteredElementCollector(doc).OfClass(PipingSystemType).ToElements()
print("Piping Systems ({0}):".format(len(systems)))
for s in systems:
    try:
        print("  System Name: {0:35} | Abbr: {1} | SystemType: {2}".format(
            Element.Name.__get__(s), s.Abbreviation, s.SystemClassification
        ))
    except Exception as ex:
        print("  Error:", ex)

pipe_types = FilteredElementCollector(doc).OfClass(PipeType).ToElements()
print("Pipe Types ({0}):".format(len(pipe_types)))
for pt in pipe_types:
    try:
        print("  PipeType: {0}".format(Element.Name.__get__(pt)))
    except Exception:
        pass
