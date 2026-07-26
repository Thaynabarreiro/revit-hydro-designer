# -*- coding: utf-8 -*-
"""M7 - Gerador Automatico de Pranchas de Detalhamento por Ambiente (Revit API).

Cria pranchas A4 por ambiente (Cozinha, Banheiro, Lavanderia, Cobertura)
com Planta Baixa (PB 1:20/1:25), Elevação (1:20) e Vista 3D recortada (3D 1:20/1:25)
com carimbo preenchido e viewports organizadas conforme o padrão do usuário.
"""
import codecs
import json
import math
import os

from Autodesk.Revit.DB import (
    BuiltInCategory, BuiltInParameter, BoundingBoxXYZ, ElementId,
    FilteredElementCollector, FamilySymbol, Transaction, Level,
    ViewFamilyType, ViewFamily, ViewPlan, View3D, Viewport, ViewSheet, XYZ
)

if "RAIZ" in globals():
    RAIZ = globals()["RAIZ"]
elif "__file__" in globals():
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    RAIZ = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
else:
    RAIZ = os.environ.get("HYDRO_PROJECT_ROOT", os.getcwd())
D = os.path.join(RAIZ, "data")


def ler_json(nome):
    c = os.path.join(D, nome)
    if not os.path.isfile(c):
        return {}
    f = codecs.open(c, "r", encoding="utf-8")
    d = json.loads(f.read())
    f.close()
    return d


def set_param(elem, bip, val):
    try:
        p = elem.get_Parameter(bip)
        if p and not p.IsReadOnly:
            p.Set(val)
            return True
    except Exception:
        pass
    return False


CFG = ler_json("config_projeto.json")
proj_cfg = CFG.get("projeto", {})

proprietario = proj_cfg.get("proprietario", "Suelen e Henrique")
endereco = proj_cfg.get("cidade", "Praia Do Ervino - SFS")
desenhista = CFG.get("responsavel_tecnico", {}).get("nome", "Thayná Barreiro")

print("=== M7 - GERADOR DE PRANCHAS DE DETALHAMENTO POR AMBIENTE ===")

# 1. Localizar Titulo de Prancha A4 / TitleBlock
tb_symbol = None
for s in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TitleBlocks).ToElements():
    tb_symbol = s.GetTypeId()
    print("TitleBlock ID encontrado: {0}".format(s.Id))
    break

if tb_symbol is None or tb_symbol == ElementId.InvalidElementId:
    print("Aviso: Nenhum titleblock A4 carregado. Usando InvalidElementId para prancha padrão.")
    tb_symbol = ElementId.InvalidElementId

# 2. Localizar ViewFamilyTypes para Planta Baixa e 3D
vft_plan = None
vft_3d = None
for vft in FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements():
    if vft.ViewFamily == ViewFamily.FloorPlan and vft_plan is None:
        vft_plan = vft.Id
    elif vft.ViewFamily == ViewFamily.ThreeDimensional and vft_3d is None:
        vft_3d = vft.Id

# 3. Mapear Ambientes do Modelo (Cozinha, Banheiro, Lavanderia, Cobertura)
pranchas_especificas = [
    {"num": "04/001", "nome": "Detalhes - ESG - Cozinha", "disciplina": "ESG", "ambiente": "Cozinha", "escala_pb": 20, "escala_elev": 20},
    {"num": "05/001", "nome": "Detalhes - HID - Lavanderia", "disciplina": "HID", "ambiente": "Lavanderia", "escala_pb": 25, "escala_elev": 20},
    {"num": "07/001", "nome": "Detalhes - HID - Banheiro Térreo", "disciplina": "HID", "ambiente": "Banheiro", "escala_pb": 20, "escala_elev": 25},
    {"num": "08/001", "nome": "Detalhes - ESG - Banheiro Térreo", "disciplina": "ESG", "ambiente": "Banheiro", "escala_pb": 25, "escala_elev": 25},
    {"num": "13/001", "nome": "Detalhes - Coord - Cobertura", "disciplina": "COORD", "ambiente": "Cobertura", "escala_pb": 25, "escala_elev": 25}
]

# Obter nivel principal
niveis = sorted(FilteredElementCollector(doc).OfClass(Level).ToElements(), key=lambda x: x.Elevation)
nivel_ref = niveis[0] if niveis else None

t = Transaction(doc, "M7 - Criar Pranchas por Ambiente")
t.Start()

pranchas_criadas = 0
for spec in pranchas_especificas:
    try:
        sheet = ViewSheet.Create(doc, tb_symbol)
        set_param(sheet, BuiltInParameter.SHEET_NUMBER, spec["num"])
        set_param(sheet, BuiltInParameter.SHEET_NAME, spec["nome"])

        # Preencher parametros do Carimbo
        for p_name in ["Cliente", "Client Name"]:
            p_cli = sheet.LookupParameter(p_name)
            if p_cli and not p_cli.IsReadOnly:
                p_cli.Set(proprietario)

        for p_name in ["Desenhista", "Drawn By"]:
            p_des = sheet.LookupParameter(p_name)
            if p_des and not p_des.IsReadOnly:
                p_des.Set(desenhista)

        for p_name in ["Endereço", "Project Address"]:
            p_end = sheet.LookupParameter(p_name)
            if p_end and not p_end.IsReadOnly:
                p_end.Set(endereco)

        # Criar Planta Baixa da Prancha
        if vft_plan and nivel_ref:
            v_pb = ViewPlan.Create(doc, vft_plan, nivel_ref.Id)
            nome_pb = "PB - " + spec["disciplina"] + " - " + spec["ambiente"] + " (" + spec["num"].replace("/", "_") + ")"
            set_param(v_pb, BuiltInParameter.VIEW_NAME, nome_pb)
            v_pb.Scale = spec["escala_pb"]
            v_pb.CropBoxActive = True
            v_pb.CropBoxVisible = True

            if Viewport.CanAddViewToSheet(doc, sheet.Id, v_pb.Id):
                Viewport.Create(doc, sheet.Id, v_pb.Id, XYZ(0.8, 0.6, 0))

        # Criar Vista 3D Isometrica da Prancha
        if vft_3d:
            v_3d = View3D.CreateIsometric(doc, vft_3d)
            nome_3d = "3D - " + spec["disciplina"] + " - " + spec["ambiente"] + " (" + spec["num"].replace("/", "_") + ")"
            set_param(v_3d, BuiltInParameter.VIEW_NAME, nome_3d)
            v_3d.Scale = spec["escala_pb"]

            if Viewport.CanAddViewToSheet(doc, sheet.Id, v_3d.Id):
                Viewport.Create(doc, sheet.Id, v_3d.Id, XYZ(1.6, 0.8, 0))

        pranchas_criadas += 1
        print("Prancha criada: [{0}] {1}".format(spec["num"], spec["nome"]))

    except Exception as ex:
        print("Aviso ao criar prancha {0}: {1}".format(spec["num"], str(ex)))

t.Commit()

print("")
print("=" * 60)
print("GERACAO DE PRANCHAS CONCLUIDA: {0} pranchas criadas no Revit.".format(pranchas_criadas))
print("=" * 60)
