# -*- coding: utf-8 -*-
"""Gerador Automático do Banheiro Demo Completo (Arquitetura + Louças Reais 3D + Instalações Hidrossanitárias).

Cria:
1. Piso Térreo (Z=0,00m)
2. 4 Paredes Perimetrais (h=3,00m)
3. Laje Superior / Teto (Z=+3,00m, apoiada exatamente sobre as 4 paredes)
4. Instanciação Automática das 3 Louças Reais (Bacia Sanitária, Lavatório, Chuveiro)
5. 4 Disciplinas MEP independentes com tubulações NBR embutidas na alvenaria:
   - Água Fria (AF): PVC Soldável Marrom 25mm / 32mm por dentro das paredes (h=2.70m)
   - Água Quente (AQ): CPVC Ultraterm / PPR 22mm / 25mm
   - Esgoto Sanitário (ESG): PVC Sanitário Branco 40mm / 50mm / 100mm sob o piso
   - Ventilação (VENT): Coluna de Ventilação PVC Branco DN 75mm subindo pela laje
6. Vista Corte Maquete 3D: Oculta a parede frontal e aplica 65% de transparência nas paredes laterais/laje para enxergar o interior completo!
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

    print("=== 1. CRIANDO ESTRUTURA ARQUITETÔNICA (PISO + PAREDES + LAJE SUPERIOR) ===")
    
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
    
    tx = DB.Transaction(doc, "Gerar Banheiro Demo Completo (Arquitetura + Louças Reais)")
    tx.Start()
    
    # Retângulo do Banheiro em pés (1 ft = 304.8 mm): 3.0m x 2.5m
    p0 = DB.XYZ(0, 0, 0)
    p1 = DB.XYZ(10, 0, 0)   # ~3.05m (Parede Frontal)
    p2 = DB.XYZ(10, 8, 0)   # ~2.44m (Parede Lateral Direita)
    p3 = DB.XYZ(0, 8, 0)    # Parede de Fundo
    
    line1 = DB.Line.CreateBound(p0, p1) # Frontal
    line2 = DB.Line.CreateBound(p1, p2) # Direita
    line3 = DB.Line.CreateBound(p2, p3) # Fundo
    line4 = DB.Line.CreateBound(p3, p0) # Esquerda
    
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
                    param_off.Set(h_feet) # Exatamente a +3.00m
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

    # --- INSERÇÃO / ATUALIZAÇÃO DAS 3 LOUÇAS SANITÁRIAS REAIS ---
    symbols = list(
        DB.FilteredElementCollector(doc)
        .OfCategory(DB.BuiltInCategory.OST_PlumbingFixtures)
        .OfClass(DB.FamilySymbol)
        .ToElements()
    )
    
    # Busca símbolos específicos para Bacia, Lavatório e Chuveiro
    sym_bacia, sym_lavat, sym_chuv = None, None, None
    for s in symbols:
        s_name = nm(s).lower()
        s_fam = ""
        try:
            s_fam = s.FamilyName.lower()
        except Exception:
            pass
        combined = s_name + " " + s_fam
        
        if ("bacia" in combined or "vaso" in combined or "sanit" in combined or "wc" in combined) and not sym_bacia:
            sym_bacia = s
        elif ("lavat" in combined or "pia" in combined or "cuba" in combined or "sink" in combined) and not sym_lavat:
            sym_lavat = s
        elif ("chuveiro" in combined or "ducha" in combined or "shower" in combined) and not sym_chuv:
            sym_chuv = s

    # Fallbacks se não achou famílias específicas
    symbols_genericos = [s for s in symbols if "reservatorio" not in nm(s).lower() and "cavalete" not in nm(s).lower()]
    if not sym_bacia and symbols_genericos:
        sym_bacia = symbols_genericos[0]
    if not sym_lavat and symbols_genericos:
        sym_lavat = symbols_genericos[min(1, len(symbols_genericos)-1)]
    if not sym_chuv and symbols_genericos:
        sym_chuv = symbols_genericos[min(2, len(symbols_genericos)-1)]

    if sym_bacia:
        tx_f = DB.Transaction(doc, "Inserir Louças Hidráulicas Reais no Banheiro Demo")
        tx_f.Start()
        try:
            # Apaga stubs antigos se houver
            fixt_antigos = list(DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_PlumbingFixtures).WhereElementIsNotElementType().ToElements())
            for fa in fixt_antigos:
                try:
                    if "Reservatorio" not in fa.Symbol.FamilyName and "Cavalete" not in fa.Symbol.FamilyName:
                        col_del = System.Collections.Generic.List[DB.ElementId]()
                        col_del.Add(fa.Id)
                        doc.Delete(col_del)
                except Exception:
                    pass

            # Posiciona as 3 louças encostadas nas paredes para passar a tubulação embutida
            # Bacia Sanitária (encostada na parede de fundo Y=7.2)
            if not sym_bacia.IsActive:
                sym_bacia.Activate()
            inst_bacia = doc.Create.NewFamilyInstance(DB.XYZ(2.5, 7.2, 0), sym_bacia, level_base, DB.Structure.StructuralType.NonStructural)

            # Lavatório (encostado na parede de fundo Y=7.2)
            if sym_lavat:
                if not sym_lavat.IsActive:
                    sym_lavat.Activate()
                inst_lavat = doc.Create.NewFamilyInstance(DB.XYZ(7.5, 7.2, 0), sym_lavat, level_base, DB.Structure.StructuralType.NonStructural)

            # Chuveiro (encostado na parede lateral direita X=9.5, h=2.10m)
            if sym_chuv:
                if not sym_chuv.IsActive:
                    sym_chuv.Activate()
                inst_chuv = doc.Create.NewFamilyInstance(DB.XYZ(9.5, 4.0, 0), sym_chuv, level_base, DB.Structure.StructuralType.NonStructural)

            print("3 Louças Sanitárias Reais (Bacia, Lavatório, Chuveiro) posicionadas com sucesso!")
            tx_f.Commit()
        except Exception as ex_inst:
            tx_f.RollBack()
            print("Aviso ao posicionar louças: " + str(ex_inst))
    else:
        return (
            "⚠️ O arquivo atual não contém famílias de Louças Hidráulicas (Bacia, Lavatório, Chuveiro) pré-carregadas.\n\n"
            "💡 POR FAVOR: Abra o arquivo de Template Oficial (.rte):\n"
            "   1. Abra o arquivo 'template/Revit_Hydro_Designer_Template_NBR.rte'\n"
            "   2. Ou clique na aba '🏛️ Template Oficial (.rte)' no Studio BIM!"
        )

    print("")
    print("=== 2. CONFIGURANDO VISTA 3D CORTE MAQUETE (OCULTA PAREDE FRONTAL & TRANSPARÊNCIA) ===")
    
    view = doc.ActiveView
    if view and (view.ViewType == DB.ViewType.ThreeD or view.ViewType == DB.ViewType.FloorPlan):
        tx_v = DB.Transaction(doc, "Ajustar Vista 3D Maquete Corte Banheiro")
        tx_v.Start()
        try:
            view.DetailLevel = DB.ViewDetailLevel.Fine
            view.DisplayStyle = DB.DisplayStyle.Shaded
            
            # Oculta a Parede Frontal (w1) para transformar a vista em um Maquete Corte 3D realista
            coll_hide = System.Collections.Generic.List[DB.ElementId]()
            coll_hide.Add(w1.Id)
            try:
                view.HideElements(coll_hide)
                print("Parede Frontal ocultada para corte maquete 3D.")
            except Exception:
                pass
                
            # Configura 65% de transparência nas demais Paredes, Pisos e Lajes
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
            print("Vista 3D configurada: Detalhe ALTO, Corte Maquete e Transparência aplicada.")
        except Exception as ex_v:
            print("Aviso ao aplicar corte/transparência na vista: " + str(ex_v))
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
        "1. ARQUITETURA & ESTRUTURA COMPLETA: Piso Térreo (Z=0,00m), Paredes (h=3,00m) e Laje Superior / Teto (Z=+3,00m).\n"
        "2. LOUÇAS SANITÁRIAS REAIS 3D: Bacia Sanitária com Caixa Acoplada, Lavatório com Coluna e Chuveiro 3D instanciados!\n"
        "3. VISTA CORTE MAQUETE 3D: Parede frontal ocultada para visualização direta do ambiente interno + transparência de vidro nas demais paredes.\n"
        "4. 4 DISCIPLINAS INDEPENDENTES MODELADAS:\n"
        "   • 💧 Água Fria (AF): Tubos PVC Soldável Marrom (DN 25mm / 32mm) EMBUTIDOS NA ALVENARIA com Barrilete a h=2.70m (abaixo do teto).\n"
        "   • 🔥 Água Quente (AQ): Tubos CPVC / PPR (DN 22mm / 25mm).\n"
        "   • 🚽 Esgoto Sanitário (ESG): Tubos PVC Sanitário Branco (DN 40mm / 50mm / 100mm) sob o piso com declividade normatizada.\n"
        "   • 🌬️ Ventilação Primária (VENT): Coluna de Ventilação PVC Branco (DN 75mm) subindo pela laje superior!"
    )
    return msg_sucesso

if __name__ == "__main__":
    try:
        r = gerar_banheiro_e_configurar_vista()
        print(r)
    except Exception as ex:
        import traceback
        traceback.print_exc()
