# -*- coding: utf-8 -*-
"""Reload pyRevit UI session and tab buttons."""
try:
    from pyrevit.loader import session_mgr
    session_mgr.reload_pyrevit()
    print("pyRevit UI reloaded successfully.")
except Exception as e:
    print("Aviso ao recarregar UI: " + str(e))
