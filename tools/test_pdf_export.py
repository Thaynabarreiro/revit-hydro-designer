# -*- coding: utf-8 -*-
from xhtml2pdf import pisa

html_file = r"c:\Users\Shadow\Documents\00 - Claude - Revit\memoriais\Memorial_Hidraulico_Henrique_e_Suelen.html"
pdf_file = r"c:\Users\Shadow\Documents\00 - Claude - Revit\memoriais\Memorial_Hidraulico_Henrique_e_Suelen.pdf"

with open(html_file, "r", encoding="utf-8") as f:
    html_content = f.read()

with open(pdf_file, "wb") as pdf_out:
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_out)

print("PDF Created:", not pisa_status.err)
