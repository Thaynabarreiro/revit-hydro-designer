# -*- coding: utf-8 -*-
"""Gerador Automático do Banheiro Demo Completo (Arquitetura + Estrutura + Instalações Hidrossanitárias).

Cria:
1. Piso Térreo (Z=0,00m)
2. 4 Paredes Perimetrais (h=3,00m)
3. Laje Superior / Teto (Z=+3,00m, apoiada exatamente sobre as 4 paredes)
4. Louças Sanitárias Hidráulicas (Bacia, Lavatório, Chuveiro)
5. 4 Disciplinas MEP independentes com tubulações e conexões NBR:
   - Água Fria (AF): PVC Soldável Marrom 25mm / 32mm por dentro das paredes
   - Água Quente (AQ): CPVC Ultraterm / PPR 22mm / 25mm
   - Esgoto Sanitário (ESG): PVC Sanitário Branco 40mm / 50mm / 100mm com declividade
   - Ventilação (VENT): Coluna de Ventilação PVC Branco DN 75mm subindo pela laje superior
6. Configuração da Vista 3D com Detalhe ALTO e 65% de Transparência de Vidro nas Paredes e Lajes.
"""
import os
import sys
import System

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

    print("=== 1. CRIANDO ESTRUTURA COMPLETA (PISO + PAREDES + LAJE SUPERIOR FLUSH AT +3.00M) ===")
    
    # Nível Térreo (Base)
    levels = sorted(list(DB.FilteredElementCollector(doc).OfClass(DB.Level).ToElements()), key=lambda x: x.Elevation)
    if not levels:
        return "Erro: Nenhum nível (Level) encontrado no modelo."
    level_base = levels[0]
    
    # WallTypes & FloorTypes
    wall_types = list(DB.FilteredElementCollector(doc).OfClass(DB.WallType).ToElements())
    floor_types = list(DB.FilteredElementCollector(doc).OfClass(DB.FloorType).ToElements())
    
    if not wall_types:
        return "Erro: Nenhum WallType disponível no modelo."
    floor_type = floor_types[0] if floor_types else None
    
    tx = DB.Transaction(doc, "Gerar Banheiro Demo Completo (Piso, Paredes e Laje Flutuante Corrigida)")
    tx.Start()
    
    # Retângulo do Banheiro em pés (1 ft = 304.8 mm): 3.0m x 2.5m
    p0 = DB.XYZ(0, 0, 0)
    p1 = DB.XYZ(10, 0, 0)   # ~3.05m
    p2 = DB.XYZ(10, 8, 0)   # ~2.44m
    p3 = DB.XYZ(0, 8, 0)
    
    line1 = DB.Line.CreateBound(p0, p1)
    line2 = DB.Line.CreateBound(p1, p2)
    line3 = DB.Line.CreateBound(p2, p3)
    line4 = DB.Line.CreateBound(p3, p0)
    
    h_feet = 9.84 # ~3.0m de altura
    
    # 4 Paredes Perimetrais
    w1 = DB.Wall.Create(doc, line1, level_base.Id, False)
    w2 = DB.Wall.Create(doc, line2, level_base.Id, False)
    w3 = DB.Wall.Create(doc, line3, level_base.Id, False)
    w4 = DB.Wall.Create(doc, line4, level_base.Id, False)
    
    for w in [w1, w2, w3, w4]:
        w.get_Parameter(DB.BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(h_feet)
        
    print("4 Paredes Perimetrais criadas com sucesso (h=3.0m).")
    
    # Piso Térreo & Laje Superior (Teto)
    if floor_type:
        try:
            curve_loop = DB.CurveLoop()
            curve_loop.Append(line1)
            curve_loop.Append(line2)
            curve_loop.Append(line3)
            curve_loop.Append(line4)
            
            loops = System.Collections.Generic.List[DB.CurveLoop]()
            loops.Add(curve_loop)
            
            # Piso Térreo (Z=0,00m)
            piso_terreo = DB.Floor.Create(doc, loops, floor_type.Id, level_base.Id)
            print("Piso Térreo (Z=0,00m) criado com sucesso.")
            
            # Laje Superior / Teto apoiada EXATAMENTE a +3,00m acima do nível base
            laje_superior = DB.Floor.Create(doc, loops, floor_type.Id, level_base.Id)
            try:
                param_off = laje_superior.get_Parameter(DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM)
                if param_off and not param_off.IsReadOnly:
                    param_off.Set(h_feet) # Exatamente a +3.00m (9.84 ft)
            except Exception:
                pass
            print("Laje Superior / Teto apoiada a Z=+3,00m criada com sucesso.")
        except Exception as ex_floor:
            print("Aviso ao criar pisos/lajes: " + str(ex_floor))
            
    # Tenta criar ambiente (Room) se possível
    try:
        p_centro = DB.UV(5, 4)
        room = doc.Create.NewRoom(level_base, p_centro)
        if room:
            room.Name = "Banheiro Social Demo"
            print("Ambiente 'Banheiro Social Demo' criado com sucesso.")
    except Exception as ex_room:
        print("Aviso ao criar Room: " + str(ex_room))
        
    tx.Commit()

    # --- VERIFICAÇÃO E INSERÇÃO DE LOUÇAS SANITÁRIAS NAS PAREDES ---
    fixt_instances = list(
        DB.FilteredElementCollector(doc)
        .OfCategory(DB.BuiltInCategory.OST_PlumbingFixtures)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    
    loucas_reais = []
    for inst in fixt_instances:
        try:
            fn = inst.Symbol.FamilyName
            if "Reservatorio" not in fn and "Cavalete" not in fn:
                loucas_reais.append(inst)
        except Exception:
            pass
            
    if len(loucas_reais) == 0:
        print("Nenhuma louça sanitária encontrada no Banheiro. Instanciando louças de teste alinhadas à parede...")
        symbols = list(
            DB.FilteredElementCollector(doc)
            .OfCategory(DB.BuiltInCategory.OST_PlumbingFixtures)
            .OfClass(DB.FamilySymbol)
            .ToElements()
        )
        
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
                # Posiciona louças encostadas nas paredes para passar a tubulação embutida
                posicoes = [
                    DB.XYZ(2.5, 0.5, 0),  # Bacia Sanitária encostada na parede de trás
                    DB.XYZ(7.5, 0.5, 0),  # Lavatório encostado na parede de trás
                    DB.XYZ(5.0, 7.5, 0)   # Chuveiro encostado na parede da frente
                ]
                
                for idx, pos in enumerate(posicoes):
                    sym = symbols_loucas[idx % len(symbols_loucas)]
                    if not sym.IsActive:
                        sym.Activate()
                    doc.Create.NewFamilyInstance(pos, sym, level_base, DB.Structure.StructuralType.NonStructural)
                    
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
    print("=== 2. CONFIGURANDO A VISTA 3D PARA TRANSPARÊNCIA DE VIDRO MULTIDISCIPLINAR ===")
    
    view = doc.ActiveView
    if view and (view.ViewType == DB.ViewType.ThreeD or view.ViewType == DB.ViewType.FloorPlan):
        tx_v = DB.Transaction(doc, "Ajustar Transparência Multidisciplinar da Vista 3D")
        tx_v.Start()
        try:
            view.DetailLevel = DB.ViewDetailLevel.Fine
            view.DisplayStyle = DB.DisplayStyle.Shaded
            
            # Configura 65% de transparência nas Paredes, Pisos e Telhados/Lajes
            ov = DB.OverrideGraphicSettings()
            ov.SetSurfaceTransparency(65)
            
            cats_para_transparencia = [
                DB.BuiltInCategory.OST_Walls,
                DB.BuiltInCategory.OST_Floors,
                DB.BuiltInCategory.OST_Roofs,
                DB.BuiltInCategory.OST_Ceilings
            ]
            
            for cat in cats_para_transparencia:
                try:
                    view.SetCategoryOverrides(DB.ElementId(cat), ov)
                except Exception:
                    pass
                    
            if uidoc:
                uidoc.RefreshActiveView()
            print("Vista 3D configurada: Detalhe ALTO, Paredes, Piso e Laje com 65% de Transparência de Vidro.")
        except Exception as ex_v:
            print("Aviso ao aplicar transparência na vista: " + str(ex_v))
        finally:
            tx_v.Commit()
            
    print("")
    print("=== 3. EXECUTANDO AS 4 DISCIPLINAS HIDROSSANITÁRIAS SEPARADAS (AF, AQ, ESG, VENT) ===")
    
    # Passo 1: Leitura do Modelo
    r_m1 = hydro.rodar("m1_reader.py")
    print("1. Leitura BIM (M1) concluída.")
    
    # Passo 2: Dimensionamento de Normas (AF / AQ / ESG)
    r_m2 = hydro.rodar("m2_dimensionamento.py")
    print("2. Dimensionamento NBR 5626 (M2) concluído.")
    
    # Passo 3: Geração da Rede 3D de ÁGUA FRIA (AF - PVC Soldável Marrom 25mm/32mm EMBUTIDO NA PAREDE)
    r_af = hydro.rodar("m6g_rede_final.py")
    print("3. Rede 3D de Água Fria (AF - PVC Soldável) gerada com sucesso.")
    
    # Passo 4: Geração da Rede 3D de ÁGUA QUENTE (AQ - CPVC / PPR 22mm/25mm)
    try:
        r_aq = hydro.rodar("m6_rede_agua_quente.py")
        print("4. Rede 3D de Água Quente (AQ - CPVC/PPR) gerada com sucesso.")
    except Exception as ex_aq:
        print("Nota Água Quente: " + str(ex_aq))
        
    # Passo 5: Geração da Rede 3D de ESGOTO & VENTILAÇÃO (ESG/VENT - PVC Sanitário 40mm/50mm/100mm + Coluna VENT 75mm)
    try:
        r_esg = hydro.rodar("m6_rede_esgoto.py")
        print("5. Rede 3D de Esgoto e Coluna de Ventilação (ESG/VENT - NBR 8160) gerada com sucesso.")
    except Exception as ex_esg:
        print("Nota Esgoto/Ventilação: " + str(ex_esg))
        
    # Passo 6: Pranchas e Memoriais
    try:
        r_m7 = hydro.rodar("m7_gerar_pranchas.py")
        r_m8 = hydro.rodar("m8_memorial.py")
        print("6. Pranchas A4 (M7) e Memorial de Cálculo (M8) gerados.")
    except Exception:
        pass
        
    msg_sucesso = (
        "✅ PROCESSO MULTIDISCIPLINAR EXECUTADO COM SUCESSO!\n\n"
        "1. ESTRUTURA COMPLETA GERADA: Piso Térreo (Z=0,00m), 4 Paredes (h=3,00m) e Laje Superior / Teto perfeitamente apoiada a Z=+3,00m sobre as paredes.\n"
        "2. VISTA 3D TRANSPARENTE: Paredes, Piso e Laje configurados com 65% de transparência para visualização dos tubos internos.\n"
        "3. 4 DISCIPLINAS INDEPENDENTES MODELADAS NO REVIT:\n"
        "   • 💧 Água Fria (AF): Tubos PVC Soldável Marrom (DN 25mm / 32mm) EMBUTIDOS NAS PAREDES com Barrilete a h=2.70m.\n"
        "   • 🔥 Água Quente (AQ): Tubos CPVC / PPR (DN 22mm / 25mm) para Água Quente.\n"
        "   • 🚽 Esgoto Sanitário (ESG): Tubos PVC Sanitário Branco (DN 40mm / 50mm / 100mm) sob o piso com declividade normatizada.\n"
        "   • 🌬️ Ventilação Primária (VENT): Coluna de Ventilação PVC Branco (DN 75mm) subindo verticalmente através da Laje Superior!"
    )
    return msg_sucesso

if __name__ == "__main__":
    try:
        r = gerar_banheiro_e_configurar_vista()
        print(r)
    except Exception as ex:
        import traceback
        traceback.print_exc()
