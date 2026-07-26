# -*- coding: utf-8 -*-
from pyrevit import forms

components = [
    forms.Label("PROJETO"),
    forms.TextBox("nome", default="Casa A&R"),
    forms.Label("Cidade"),
    forms.TextBox("cidade", default="Porto Alegre"),
    forms.Button("Salvar")
]

form = forms.FlexForm("Test Form", components)
res = form.show()
print("Form result:", res)
print("Form values:", form.values if hasattr(form, "values") else "No values")
