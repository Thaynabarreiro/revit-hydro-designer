# -*- coding: utf-8 -*-
"""Force pyRevit session reload to refresh UI ribbon icons."""
try:
    from pyrevit.loader import sessionmgr
    sessionmgr.reload_pyrevit()
    print("pyRevit session reloaded successfully.")
except Exception as e1:
    try:
        from pyrevit import loader
        loader.load_pyrevit()
        print("pyRevit loaded successfully.")
    except Exception as e2:
        print("Reload error:", e1, e2)
