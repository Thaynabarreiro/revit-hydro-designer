# -*- coding: utf-8 -*-
import os
from xhtml2pdf import pisa

if "RAIZ" in globals():
    RAIZ = globals()["RAIZ"]
elif "__file__" in globals():
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    RAIZ = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
else:
    RAIZ = os.environ.get("HYDRO_PROJECT_ROOT", os.getcwd())
_proj_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
html_file = os.path.join(_proj_root, "memoriais", "Memorial_Hidraulico_Henrique_e_Suelen.html")
pdf_file = os.path.join(_proj_root, "memoriais", "Memorial_Hidraulico_Henrique_e_Suelen.pdf")

with open(html_file, "r", encoding="utf-8") as f:
    html_content = f.read()

with open(pdf_file, "wb") as pdf_out:
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_out)

print("PDF Created:", not pisa_status.err)
