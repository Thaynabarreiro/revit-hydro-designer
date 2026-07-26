# -*- coding: utf-8 -*-
from docx import Document
from htmldocx import HtmlToDocx
import re

_this_dir = os.path.dirname(os.path.abspath(__file__))
_proj_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
html_file = os.path.join(_proj_root, "memoriais", "Memorial_Hidraulico_Henrique_e_Suelen.html")
docx_file = os.path.join(_proj_root, "memoriais", "Memorial_Hidraulico_Henrique_e_Suelen.docx")

doc = Document()
html_parser = HtmlToDocx()

with open(html_file, "r", encoding="utf-8") as f:
    html_content = f.read()

# Fix 3-digit hex colors to 6-digit hex colors for htmldocx parser
html_clean = re.sub(r'#([0-9a-fA-F])([0-9a-fA-F])([0-9a-fA-F])\b', r'#\1\1\2\2\3\3', html_content)

html_parser.add_html_to_document(html_clean, doc)
doc.save(docx_file)

print("DOCX Created successfully.")
