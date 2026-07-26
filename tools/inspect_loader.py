# -*- coding: utf-8 -*-
import sys
import pyrevit.loader
print("pyrevit.loader contents:", dir(pyrevit.loader))
try:
    from pyrevit.loader import session_utils
    print("session_utils:", dir(session_utils))
except Exception as ex:
    print("session_utils error:", ex)
