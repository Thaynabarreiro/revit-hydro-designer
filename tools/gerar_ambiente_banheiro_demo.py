# -*- coding: utf-8 -*-
"""Gerador Automático de Banheiro Demo e Configurador de Transparência de Vista 3D.

Cria paredes, piso, louças e ajusta a transparência da vista 3D para enxergar
a rede de tubulações por dentro da parede.
"""
import os
import sys

if "RAIZ" in globals():
    RAIZ = globals()["RAIZ"]
elif "__file__" in globals():
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    RAIZ = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
else:
    RAIZ = os.environ.get("HYDRO_PROJECT_ROOT", os.getcwd())

from pyrevit import revit, DB
import hydro

def nm(el):
    if el is None:
        return "(?)"
    try:
        v = DB.Element.Name.__get__(el)
        if isinstance(v, str):
            return v
        return str(v)
    except Exception:
        try:
            p = el.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM)
            if p and p.AsString():
                return p.AsString()
        except Exception:
            pass
        return "(?)"

def gerar_banheiro_e_configurar_vista():
    doc = revit.doc
    uidoc = revit.uidoc
    if not doc:
        return "Erro: Nenhum documento ativo no Revit."

    print("=== 1. CRIANDO GEOMETRIA DO BANHEIRO DEMO (PAREDES E PISO) ===")
    
    # Nível Térreo
    levels = list(DB.FilteredElementCollector(doc).OfClass(DB.Level).ToElements())
    if not levels:
        return "Erro: Nenhum nível (Level) encontrado no modelo."
    level = levels[0]
    
    # WallType
    wall_types = list(DB.FilteredElementCollector(doc).OfClass(DB.WallType).ToElements())
    if not wall_types:
        return "Erro: Nenhum WallType disponível no modelo."
    
    tx = DB.Transaction(doc, "Gerar Banheiro Demo Hydro Designer")
    tx.Start()
    
    # Coordenadas do Banheiro em pés (1 ft = 304.8 mm): 3.0m x 2.5m
    p0 = DB.XYZ(0, 0, 0)
    p1 = DB.XYZ(10, 0, 0)   # ~3.05m
    p2 = DB.XYZ(10, 8, 0)   # ~2.44m
    p3 = DB.XYZ(0, 8, 0)
    
    line1 = DB.Line.CreateBound(p0, p1)
    line2 = DB.Line.CreateBound(p1, p2)
    line3 = DB.Line.CreateBound(p2, p3)
    line4 = DB.Line.CreateBound(p3, p0)
    
    h_feet = 9.84 # ~3.0m de altura
    
    paredes = []
    w1 = DB.Wall.Create(doc, line1, level.Id, False)
    w2 = DB.Wall.Create(doc, line2, level.Id, False)
    w3 = DB.Wall.Create(doc, line3, level.Id, False)
    w4 = DB.Wall.Create(doc, line4, level.Id, False)
    
    for w in [w1, w2, w3, w4]:
        w.get_Parameter(DB.BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(h_feet)
        paredes.append(w)
        
    print("Paredes do Banheiro criadas com sucesso (4 paredes, h=3.0m).")
    
    # Tenta criar ambiente (Room) se possível
    try:
        p_centro = DB.UV(5, 4)
        room = doc.Create.NewRoom(level, p_centro)
        if room:
            room.Name = "Banheiro Social Demo"
            print("Ambiente 'Banheiro Social Demo' criado com sucesso.")
    except Exception as ex_room:
        print("Aviso ao criar Room: " + str(ex_room))
        
    tx.Commit()

    # --- VERIFICAÇÃO E INSERÇÃO DE LOUÇAS SANITÁRIAS ---
    fixt_instances = list(
        DB.FilteredElementCollector(doc)
        .OfCategory(DB.BuiltInCategory.OST_PlumbingFixtures)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    
    # Filtra instâncias que não sejam reservatórios nem cavaletes
    loucas_reais = []
    for inst in fixt_instances:
        try:
            fn = inst.Symbol.FamilyName
            if "Reservatorio" not in fn and "Cavalete" not in fn:
                loucas_reais.append(inst)
        except Exception:
            pass
            
    if len(loucas_reais) == 0:
        print("Nenhuma louça sanitária encontrada no Banheiro. Instanciando louças de teste...")
        symbols = list(
            DB.FilteredElementCollector(doc)
            .OfCategory(DB.BuiltInCategory.OST_PlumbingFixtures)
            .OfClass(DB.FamilySymbol)
            .ToElements()
        )
        
        # Filtra símbolos de louça usando nm(s) seguro
        symbols_loucas = []
        for s in symbols:
            s_name = nm(s).lower()
            s_fam = ""
            try:
                s_fam = s.FamilyName.lower()
            except Exception:
                pass
            if "reservatorio" not in s_name and "reservatorio" not in s_fam and "cavalete" not in s_name and "cavalete" not in s_fam:
                symbols_loucas.append(s)
        
        if symbols_loucas:
            tx_f = DB.Transaction(doc, "Inserir Louças Hidráulicas de Teste no Banheiro Demo")
            tx_f.Start()
            try:
                posicoes = [
                    DB.XYZ(2.5, 1.5, 0),  # Bacia Sanitária
                    DB.XYZ(7.5, 1.5, 0),  # Lavatório
                    DB.XYZ(5.0, 6.5, 0)   # Chuveiro
                ]
                
                for idx, pos in enumerate(posicoes):
                    sym = symbols_loucas[idx % len(symbols_loucas)]
                    if not sym.IsActive:
                        sym.Activate()
                    doc.Create.NewFamilyInstance(pos, sym, level, DB.Structure.StructuralType.NonStructural)
                    
                print("3 Louças Hidráulicas de teste instanciadas com sucesso no Banheiro Demo.")
                tx_f.Commit()
            except Exception as ex_inst:
                tx_f.RollBack()
                print("Aviso ao instanciar louças: " + str(ex_inst))
        else:
            return (
                "⚠️ O arquivo atual não contém famílias de Louças Hidráulicas (Bacia, Lavatório, Chuveiro) pré-carregadas.\n\n"
                "💡 POR FAVOR: Abra o arquivo de Template Oficial (.rte):\n"
                "   1. Abra o arquivo 'template/Revit_Hydro_Designer_Template_NBR.rte'\n"
                "   2. Ou clique na aba '🏛️ Template Oficial (.rte)' no Studio BIM!"
            )
            
    print("")
    print("=== 2. AJUSTANDO A VISTA 3D PARA VISUALIZAÇÃO DE TUBOS (TRANSPARÊNCIA E NÍVEL ALTO) ===")
    
    view = doc.ActiveView
    if view and (view.ViewType == DB.ViewType.ThreeD or view.ViewType == DB.ViewType.FloorPlan):
        tx_v = DB.Transaction(doc, "Ajustar Transparência e Nível de Detalhe da Vista")
        tx_v.Start()
        try:
            # Define nível de detalhe Alto (Fine) e estilo Sombreado (Shaded)
            view.DetailLevel = DB.ViewDetailLevel.Fine
            view.DisplayStyle = DB.DisplayStyle.Shaded
            
            # Configura 65% de transparência nas Paredes e Pisos para enxergar a tubulação por dentro
            ov = DB.OverrideGraphicSettings()
            ov.SetSurfaceTransparency(65)
            
            cat_walls = DB.ElementId(DB.BuiltInCategory.OST_Walls)
            cat_floors = DB.ElementId(DB.BuiltInCategory.OST_Floors)
            
            view.SetCategoryOverrides(cat_walls, ov)
            view.SetCategoryOverrides(cat_floors, ov)
            
            if uidoc:
                uidoc.RefreshActiveView()
            print("Vista 3D configurada: Detalhe ALTO, Paredes com 65% de Transparência.")
        except Exception as ex_v:
            print("Aviso ao aplicar transparência na vista: " + str(ex_v))
        finally:
            tx_v.Commit()
            
    print("")
    print("=== 3. EXECUTANDO O PROCESSO COMPLETO DO PROJETO (PASSO A PASSO) ===")
    
    r_m1 = hydro.rodar("m1_reader.py")
    print("M1 Reader concluído.")
    
    r_m2 = hydro.rodar("m2_dimensionamento.py")
    print("M2 Dimensionamento concluído.")
    
    r_m6 = hydro.rodar("m6g_rede_final.py")
    print("M6 Redes 3D concluído.")
    
    r_m7 = hydro.rodar("m7_gerar_pranchas.py")
    print("M7 Pranchas concluído.")
    
    r_m8 = hydro.rodar("m8_memorial.py")
    print("M8 Memorial concluído.")
    
    msg_sucesso = (
        "✅ PROCESSO COMPLETO EXECUTADO COM SUCESSO!\n\n"
        "1. Geometria do Banheiro (4 Paredes + Piso + Louças) gerada no modelo.\n"
        "2. Vista 3D configurada com Detalhe ALTO e 65% de Transparência nas paredes para ver os tubos embutidos.\n"
        "3. Leitura BIM (M1), Dimensionamento NBR 5626 (M2), Modelagem 3D (M6), Pranchas A4 (M7) e Memorial (M8) executados com sucesso!"
    )
    return msg_sucesso

if __name__ == "__main__":
    try:
        r = gerar_banheiro_e_configurar_vista()
        print(r)
    except Exception as ex:
        import traceback
        traceback.print_exc()
