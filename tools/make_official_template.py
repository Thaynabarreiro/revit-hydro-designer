# -*- coding: utf-8 -*-
"""Script para converter o projeto real HID_CT_PROJETO TIOS_AP_00_RV00 no Template Oficial do Revit Hydro Designer (.rte / .rvt).

Este script remove todas as instâncias de tubos, conexões, acessórios e louças,
mantendo intactos os Tipos de Tubo, Regras de Preferência de Roteamento, Sistemas
Hidrossanitários, Famílias de Peças, Modelos de Vista e Parâmetros Compartilhados.
"""
import os
import sys
import shutil

if "RAIZ" in globals():
    RAIZ = globals()["RAIZ"]
elif "__file__" in globals():
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    RAIZ = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
else:
    RAIZ = os.environ.get("HYDRO_PROJECT_ROOT", os.getcwd())

from pyrevit import revit, DB

def criar_template_oficial():
    doc = revit.doc
    if not doc:
        return "Erro: Nenhum documento ativo no Revit."
        
    print("=== INICIANDO PURGA DO MODELO PARA CRIAÇÃO DO TEMPLATE OFICIAL ===")
    
    # Categorias de instâncias de modelo a limpar
    cats_para_limpar = [
        DB.BuiltInCategory.OST_PipeCurves,
        DB.BuiltInCategory.OST_PipeFitting,
        DB.BuiltInCategory.OST_PipeAccessory,
        DB.BuiltInCategory.OST_PlumbingFixtures,
        DB.BuiltInCategory.OST_FlexPipeCurves,
        DB.BuiltInCategory.OST_MechanicalEquipment,
        DB.BuiltInCategory.OST_Dimensions,
        DB.BuiltInCategory.OST_TextNotes,
        DB.BuiltInCategory.OST_Lines
    ]
    
    ids_para_deletar = []
    
    for cat in cats_para_limpar:
        collector = DB.FilteredElementCollector(doc).OfCategory(cat).WhereElementIsNotElementType().ToElementIds()
        for elem_id in collector:
            # Evita deletar elementos travados ou de sistema fixo
            el = doc.GetElement(elem_id)
            if el and not el.Pinned:
                ids_para_deletar.append(elem_id)
                
    print("Encontradas {0} instâncias para limpeza no template...".format(len(ids_para_deletar)))
    
    tx = DB.Transaction(doc, "Purga de Instâncias para Template Hydro Designer")
    tx.Start()
    
    deletados = 0
    for elem_id in ids_para_deletar:
        try:
            el = doc.GetElement(elem_id)
            if el:
                doc.Delete(elem_id)
                deletados += 1
        except Exception:
            pass
            
    tx.Commit()
    print("Purga concluída: {0} instâncias removidas.".format(deletados))
    
    # Pasta de saída do Template
    pasta_template = os.path.join(RAIZ, "template")
    if not os.path.exists(pasta_template):
        os.makedirs(pasta_template)
        
    caminho_template_rvt = os.path.join(pasta_template, "Revit_Hydro_Designer_Template_NBR.rvt")
    caminho_template_rte = os.path.join(pasta_template, "Revit_Hydro_Designer_Template_NBR.rte")
    
    try:
        opt = DB.SaveAsOptions()
        opt.OverwriteExistingFile = True
        doc.SaveAs(caminho_template_rvt, opt)
        print("Template RVT salvo em: {0}".format(caminho_template_rvt))
        
        # Também salvar cópia .rte se suportado
        try:
            shutil.copyfile(caminho_template_rvt, caminho_template_rte)
            print("Cópia RTE gerada em: {0}".format(caminho_template_rte))
        except Exception:
            pass
            
        return "✅ Template Oficial criado com sucesso em:\\n{0}".format(caminho_template_rvt)
    except Exception as ex:
        return "⚠️ Modelo purgado com sucesso, porém falha ao salvar SaveAs automático: {0}".format(str(ex))

try:
    res = criar_template_oficial()
    print(res)
except Exception as ex:
    import traceback
    traceback.print_exc()
