# -*- coding: utf-8 -*-
import os, sys, json, clr
clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")
clr.AddReference("WindowsBase")
clr.AddReference("System.Xaml")

import System
from System.Windows import (
    Window, WindowStartupLocation, Thickness, HorizontalAlignment, VerticalAlignment,
    GridLength, GridUnitType, TextWrapping
)
from System.Windows.Controls import (
    Grid, StackPanel, Border, TextBlock, TextBox, ComboBox,
    Button, ScrollViewer, ColumnDefinition, RowDefinition, WrapPanel, Orientation,
    ListBox, ListBoxItem
)
from System.Windows.Media import SolidColorBrush, ColorConverter

from pyrevit import revit, DB
import hydro

def hex_b(hex_code):
    return SolidColorBrush(ColorConverter.ConvertFromString(hex_code))

class HydroStudioInteractiveWindow(Window):
    def __init__(self):
        self.Title = "Revit Hydro Designer — Studio BIM"
        self.Width = 1260
        self.Height = 840
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.Background = hex_b("#f8fafc")
        self.active_tab = "CFG"
        
        self.carregar_config_projeto()
        
        main_grid = Grid()
        col_side = ColumnDefinition()
        col_side.Width = GridLength(280)
        col_main = ColumnDefinition()
        col_main.Width = GridLength(1, GridUnitType.Star)
        main_grid.ColumnDefinitions.Add(col_side)
        main_grid.ColumnDefinitions.Add(col_main)
        
        # --- LEFT SIDEBAR ---
        sidebar = Border()
        sidebar.Background = hex_b("#ffffff")
        sidebar.BorderBrush = hex_b("#e2e8f0")
        sidebar.BorderThickness = Thickness(0, 0, 1, 0)
        sidebar.Padding = Thickness(20)
        
        side_stack = StackPanel()
        
        logo_panel = StackPanel()
        logo_panel.Orientation = Orientation.Horizontal
        logo_panel.Margin = Thickness(0, 0, 0, 20)
        
        logo_icon = Border()
        logo_icon.Width = 40
        logo_icon.Height = 40
        logo_icon.CornerRadius = System.Windows.CornerRadius(10)
        logo_icon.Background = hex_b("#e0f2fe")
        logo_icon.BorderBrush = hex_b("#bae6fd")
        logo_icon.BorderThickness = Thickness(1)
        
        tb_icon = TextBlock()
        tb_icon.Text = "💧"
        tb_icon.FontSize = 20
        tb_icon.HorizontalAlignment = HorizontalAlignment.Center
        tb_icon.VerticalAlignment = VerticalAlignment.Center
        logo_icon.Child = tb_icon
        logo_panel.Children.Add(logo_icon)
        
        logo_text_stack = StackPanel()
        logo_text_stack.Margin = Thickness(12, 0, 0, 0)
        
        tb_title = TextBlock()
        tb_title.Text = "HYDRO DESIGNER"
        tb_title.FontWeight = System.Windows.FontWeights.Bold
        tb_title.FontSize = 14
        tb_title.Foreground = hex_b("#0284c7")
        
        tb_sub = TextBlock()
        tb_sub.Text = "BIM · Hidrossanitário & Pluvial"
        tb_sub.FontSize = 11
        tb_sub.Foreground = hex_b("#64748b")
        
        logo_text_stack.Children.Add(tb_title)
        logo_text_stack.Children.Add(tb_sub)
        logo_panel.Children.Add(logo_text_stack)
        side_stack.Children.Add(logo_panel)
        
        status_card = Border()
        status_card.Background = hex_b("#dcfce7")
        status_card.BorderBrush = hex_b("#86efac")
        status_card.BorderThickness = Thickness(1)
        status_card.CornerRadius = System.Windows.CornerRadius(8)
        status_card.Padding = Thickness(10, 8, 10, 8)
        status_card.Margin = Thickness(0, 0, 0, 15)
        
        tb_status = TextBlock()
        tb_status.Text = "● Revit 2027 Connected"
        tb_status.FontWeight = System.Windows.FontWeights.SemiBold
        tb_status.FontSize = 12
        tb_status.Foreground = hex_b("#15803d")
        status_card.Child = tb_status
        side_stack.Children.Add(status_card)
        
        btn_sync = Button()
        btn_sync.Content = "📍 Ler Seleção Atual do Revit"
        btn_sync.Background = hex_b("#0284c7")
        btn_sync.Foreground = hex_b("#ffffff")
        btn_sync.FontWeight = System.Windows.FontWeights.SemiBold
        btn_sync.Padding = Thickness(10, 8, 10, 8)
        btn_sync.Margin = Thickness(0, 0, 0, 15)
        btn_sync.Click += self.on_sync_from_revit
        side_stack.Children.Add(btn_sync)
        
        disc_items = [
            ("⚙️ Configurações do Projeto", "CFG"),
            ("💧 Água Fria (AF)", "AF"),
            ("🔥 Água Quente (AQ)", "AQ"),
            ("🚽 Esgoto & Ventilação (ESG)", "ESG"),
            ("🌧️ Águas Pluviais (PLUV)", "PLUV"),
            ("🌱 Tratamento no Lote (TRAT)", "TRAT"),
            ("⚡ Moto-Bomba & Recalque", "REC"),
            ("🔍 Auditoria & Acervo", "AUDIT"),
            ("📄 Memoriais & Exportação", "DOC")
        ]
        
        self.btn_map = {}
        for name, code in disc_items:
            b_btn = Button()
            b_btn.Content = name
            b_btn.Tag = code
            b_btn.HorizontalContentAlignment = HorizontalAlignment.Left
            b_btn.Padding = Thickness(12, 10, 12, 10)
            b_btn.Margin = Thickness(0, 0, 0, 6)
            b_btn.FontSize = 12
            b_btn.FontWeight = System.Windows.FontWeights.SemiBold
            b_btn.Background = hex_b("#f1f5f9")
            b_btn.Foreground = hex_b("#0f172a")
            b_btn.BorderBrush = hex_b("#e2e8f0")
            b_btn.Click += self.on_change_tab
            side_stack.Children.Add(b_btn)
            self.btn_map[code] = b_btn
            
        sidebar.Child = side_stack
        Grid.SetColumn(sidebar, 0)
        main_grid.Children.Add(sidebar)
        
        self.main_content = ScrollViewer()
        self.main_content.Padding = Thickness(25)
        Grid.SetColumn(self.main_content, 1)
        main_grid.Children.Add(self.main_content)
        self.Content = main_grid
        
        self.render_tab("CFG")

    def carregar_config_projeto(self):
        path_cfg = os.path.join(hydro.DATA, "config_projeto.json")
        if os.path.exists(path_cfg):
            try:
                with open(path_cfg, "r") as f:
                    c = json.load(f)
                self.cfg_nome = c.get("projeto", {}).get("nome", "Casa Unifamiliar Henrique & Suelen")
                hab = c.get("ocupacao", {}).get("habitantes") or c.get("ocupacao", {}).get("moradores_override") or 6
                self.cfg_hab = str(hab)
                dias = c.get("reservacao", {}).get("dias_autonomia", 2)
                self.cfg_dias = str(dias)
                return
            except Exception:
                pass
        self.cfg_nome = "Casa Unifamiliar Henrique & Suelen"
        self.cfg_hab = "6"
        self.cfg_dias = "2"

    def salvar_config_projeto(self, sender, args):
        self.cfg_nome = self.txt_nome.Text
        self.cfg_hab = self.txt_hab.Text
        self.cfg_dias = self.txt_dias.Text
        path_cfg = os.path.join(hydro.DATA, "config_projeto.json")
        try:
            if os.path.exists(path_cfg):
                with open(path_cfg, "r") as f:
                    c = json.load(f)
            else:
                c = {}
            hab_val = int(self.cfg_hab) if self.cfg_hab.isdigit() else 6
            dias_val = float(self.cfg_dias) if self.cfg_dias else 2.0
            
            c.setdefault("projeto", {})["nome"] = self.cfg_nome
            c.setdefault("ocupacao", {})["habitantes"] = hab_val
            c.setdefault("ocupacao", {})["moradores_override"] = hab_val
            c.setdefault("reservacao", {})["dias_autonomia"] = dias_val
            
            with open(path_cfg, "w") as f:
                json.dump(c, f, indent=2, ensure_ascii=False)
            self.status_txt.Text = "💾 Configurações do Projeto salvas com sucesso em config_projeto.json!"
            
            # Recalcula dinamicamente M2 com o novo numero de habitantes
            try:
                hydro.rodar("m2_dimensionamento.py")
            except Exception:
                pass
            self.render_tab("CFG")
        except Exception as ex:
            self.status_txt.Text = "Aviso ao salvar configurações: " + str(ex)

    def highlight_tab(self, code):
        for c, btn in self.btn_map.items():
            if c == code:
                btn.Background = hex_b("#e0f2fe")
                btn.Foreground = hex_b("#0284c7")
                btn.BorderBrush = hex_b("#38bdf8")
            else:
                btn.Background = hex_b("#f1f5f9")
                btn.Foreground = hex_b("#0f172a")
                btn.BorderBrush = hex_b("#e2e8f0")

    def on_change_tab(self, sender, args):
        code = str(sender.Tag)
        self.render_tab(code)

    def on_sync_from_revit(self, sender, args):
        uidoc = revit.uidoc
        if not uidoc:
            self.status_txt.Text = "Revit UIDocument não encontrado."
            return
        selected_ids = uidoc.Selection.GetElementIds()
        if selected_ids and len(selected_ids) > 0:
            info = []
            for elem_id in selected_ids:
                el = revit.doc.GetElement(elem_id)
                if el:
                    cat_name = el.Category.Name if el.Category else "Elemento"
                    info.append("• [ID: {0}] {1} ({2})".format(elem_id.IntegerValue, el.Name, cat_name))
            self.status_txt.Text = "📍 Elementos selecionados no Revit:\n" + "\n".join(info)
        else:
            self.status_txt.Text = "Nenhum elemento selecionado no modelo do Revit."

    def zoom_elemento_revit(self, elem_id_int):
        uidoc = revit.uidoc
        doc = revit.doc
        if not uidoc or not doc:
            return
        try:
            elem_id = DB.ElementId(System.Int64(elem_id_int))
            el = doc.GetElement(elem_id)
            if el:
                coll = System.Collections.Generic.List[DB.ElementId]()
                coll.Add(elem_id)
                uidoc.Selection.SetElementIds(coll)
                uidoc.ShowElements(elem_id)
                tx = DB.Transaction(doc, "Destacar Elemento Studio BIM")
                tx.Start()
                try:
                    ov = DB.OverrideGraphicSettings()
                    c = DB.Color(0, 210, 255)
                    ov.SetProjectionLineColor(c)
                    ov.SetProjectionLineWeight(8)
                    doc.ActiveView.SetElementOverrides(elem_id, ov)
                    uidoc.RefreshActiveView()
                except Exception:
                    pass
                finally:
                    tx.Commit()
                self.status_txt.Text = "📍 Elemento [ID: {0}] {1} destacado em Ciano no Revit!".format(elem_id_int, el.Name)
        except Exception as ex:
            self.status_txt.Text = "Aviso ao destacar elemento: " + str(ex)

    def atribuir_ambiente_peca(self, elem_id_int, ambiente_nome):
        path_pontos = os.path.join(hydro.DATA, "pontos_consumo.json")
        if not os.path.exists(path_pontos):
            return
        try:
            with open(path_pontos, "r") as f:
                data = json.load(f)
            revisar = data.get("revisar", [])
            pontos = data.get("pontos_consumo", [])
            
            alvo = None
            novos_revisar = []
            for r in revisar:
                if r.get("id") == elem_id_int:
                    alvo = r
                else:
                    novos_revisar.append(r)
                    
            if alvo:
                alvo["ambiente"] = ambiente_nome
                alvo["confianca"] = "atribuido manualmente pelo usuario"
                pontos.append(alvo)
                data["revisar"] = novos_revisar
                data["pontos_consumo"] = pontos
                with open(path_pontos, "w") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self.status_txt.Text = "✅ Louça [ID: {0}] atribuída com sucesso ao {1}!".format(elem_id_int, ambiente_nome)
                self.render_tab(self.active_tab)
        except Exception as ex:
            self.status_txt.Text = "Aviso ao atribuir ambiente: " + str(ex)

    def carregar_card_ambientes_lidos(self):
        path_pontos = os.path.join(hydro.DATA, "pontos_consumo.json")
        if not os.path.exists(path_pontos):
            return None
        try:
            with open(path_pontos, "r") as f:
                data = json.load(f)
            pontos = data.get("pontos_consumo", [])
        except Exception:
            return None
            
        if not pontos:
            return None
            
        card = Border()
        card.Background = hex_b("#ffffff")
        card.BorderBrush = hex_b("#cbd5e1")
        card.BorderThickness = Thickness(1)
        card.CornerRadius = System.Windows.CornerRadius(12)
        card.Padding = Thickness(20)
        card.Margin = Thickness(0, 0, 0, 20)
        
        c_stack = StackPanel()
        
        header = TextBlock()
        header.Text = "🏡 Ambientes & Louças Identificados no Modelo ({0} Pontos de Consumo)".format(len(pontos))
        header.FontSize = 14
        header.FontWeight = System.Windows.FontWeights.Bold
        header.Foreground = hex_b("#0f172a")
        header.Margin = Thickness(0, 0, 0, 12)
        c_stack.Children.Add(header)
        
        por_amb = {}
        for p in pontos:
            amb = p.get("ambiente", "Sem Ambiente")
            por_amb.setdefault(amb, []).append(p)
            
        for amb_nome in sorted(por_amb.keys()):
            lista_pecas = por_amb[amb_nome]
            peso_total_amb = sum([pt.get("peso", 0.3) for pt in lista_pecas])
            
            amb_box = Border()
            amb_box.Background = hex_b("#f8fafc")
            amb_box.BorderBrush = hex_b("#e2e8f0")
            amb_box.BorderThickness = Thickness(1)
            amb_box.CornerRadius = System.Windows.CornerRadius(8)
            amb_box.Padding = Thickness(12)
            amb_box.Margin = Thickness(0, 0, 0, 8)
            
            a_stack = StackPanel()
            
            tb_title = TextBlock()
            tb_title.Text = "📍 {0} ({1} peça(s) · Peso Total: {2:.2f})".format(
                amb_nome.title(), len(lista_pecas), peso_total_amb
            )
            tb_title.FontSize = 12
            tb_title.FontWeight = System.Windows.FontWeights.SemiBold
            tb_title.Foreground = hex_b("#0284c7")
            a_stack.Children.Add(tb_title)
            
            desc_pecas = []
            for pt in lista_pecas:
                desc_pecas.append("{0} [Peso: {1}]".format(pt.get("desc", "Peça"), pt.get("peso", 0.3)))
                
            tb_pecas = TextBlock()
            tb_pecas.Text = "   • " + "\n   • ".join(desc_pecas)
            tb_pecas.FontSize = 11
            tb_pecas.Foreground = hex_b("#475569")
            tb_pecas.Margin = Thickness(0, 4, 0, 0)
            a_stack.Children.Add(tb_pecas)
            
            amb_box.Child = a_stack
            c_stack.Children.Add(amb_box)
            
        card.Child = c_stack
        return card

    def carregar_card_loucas_pendentes(self):
        path_pontos = os.path.join(hydro.DATA, "pontos_consumo.json")
        if not os.path.exists(path_pontos):
            return None
        try:
            with open(path_pontos, "r") as f:
                data = json.load(f)
            revisar = data.get("revisar", [])
        except Exception:
            return None
            
        if not revisar:
            return None
            
        card = Border()
        card.Background = hex_b("#fffbe6")
        card.BorderBrush = hex_b("#ffe58f")
        card.BorderThickness = Thickness(1)
        card.CornerRadius = System.Windows.CornerRadius(10)
        card.Padding = Thickness(15)
        card.Margin = Thickness(0, 0, 0, 15)
        
        c_stack = StackPanel()
        
        lbl_t = TextBlock()
        lbl_t.Text = "⚠️ {0} Louça(s) Pendente(s) de Atribuição de Ambiente".format(len(revisar))
        lbl_t.FontSize = 13
        lbl_t.FontWeight = System.Windows.FontWeights.Bold
        lbl_t.Foreground = hex_b("#d48806")
        lbl_t.Margin = Thickness(0, 0, 0, 10)
        c_stack.Children.Add(lbl_t)
        
        for item_rev in revisar[:5]:
            p_panel = StackPanel()
            p_panel.Margin = Thickness(0, 0, 0, 10)
            
            tb_desc = TextBlock()
            tb_desc.Text = "• [ID: {0}] {1}".format(
                item_rev.get("id"), item_rev.get("familia", "Peça")
            )
            tb_desc.FontSize = 11
            tb_desc.FontWeight = System.Windows.FontWeights.SemiBold
            p_panel.Children.Add(tb_desc)
            
            btn_row = WrapPanel()
            btn_row.Margin = Thickness(0, 4, 0, 0)
            
            e_id = item_rev.get("id")
            
            b_rev = Button()
            b_rev.Content = "📍 Ver no Revit"
            b_rev.Background = hex_b("#0284c7")
            b_rev.Foreground = hex_b("#ffffff")
            b_rev.Padding = Thickness(8, 4, 8, 4)
            b_rev.Margin = Thickness(0, 0, 8, 4)
            b_rev.Click += lambda s, e, elem_id=e_id: self.zoom_elemento_revit(elem_id)
            btn_row.Children.Add(b_rev)
            
            ambientes_rapidos = ["Banheiro 1", "Banheiro Suíte", "Cozinha", "Lavanderia", "Lavabo"]
            for amb_nome in ambientes_rapidos:
                b_amb = Button()
                b_amb.Content = amb_nome
                b_amb.Background = hex_b("#ffffff")
                b_amb.Foreground = hex_b("#0f172a")
                b_amb.BorderBrush = hex_b("#cbd5e1")
                b_amb.Padding = Thickness(8, 4, 8, 4)
                b_amb.Margin = Thickness(0, 0, 6, 4)
                b_amb.Click += lambda s, e, elem_id=e_id, a_nome=amb_nome: self.atribuir_ambiente_peca(elem_id, a_nome)
                btn_row.Children.Add(b_amb)
                
            p_panel.Children.Add(btn_row)
            c_stack.Children.Add(p_panel)
            
        card.Child = c_stack
        return card

    def on_select_element_in_app(self, sender, args):
        if not sender.SelectedItem:
            return
        elem_id_int = getattr(sender.SelectedItem, "Tag", None)
        if not elem_id_int:
            return
        self.zoom_elemento_revit(elem_id_int)

    def carregar_elementos_identificados(self, code="AF"):
        lst = ListBox()
        lst.Height = 180
        lst.Margin = Thickness(0, 10, 0, 15)
        lst.SelectionChanged += self.on_select_element_in_app
        
        if code == "AQ":
            json_pontos = os.path.join(hydro.DATA, "pontos_consumo_aq.json")
            json_rede = os.path.join(hydro.DATA, "rede_ids_aq.json")
            tag_p = "🔥 [Água Quente - Ponto ID: {0}]"
            tag_r = "🔥 [Água Quente - Tubo ID: {0}]"
        elif code == "ESG":
            json_pontos = os.path.join(hydro.DATA, "pontos_consumo_esg.json")
            json_rede = os.path.join(hydro.DATA, "rede_ids_esg.json")
            tag_p = "🚽 [Esgoto - Peça Sanitária ID: {0}]"
            tag_r = "🚽 [Esgoto - Prumada/Ramal ID: {0}]"
        elif code == "PLUV":
            json_pontos = os.path.join(hydro.DATA, "pontos_consumo_pluv.json")
            json_rede = os.path.join(hydro.DATA, "rede_ids_pluv.json")
            tag_p = "🌧️ [Pluvial - Calha/Ralo ID: {0}]"
            tag_r = "🌧️ [Pluvial - Condutor ID: {0}]"
        elif code == "TRAT":
            json_pontos = os.path.join(hydro.DATA, "pontos_consumo_esg.json")
            json_rede = os.path.join(hydro.DATA, "rede_ids_esg.json")
            tag_p = "🌱 [Tratamento - Ponto ID: {0}]"
            tag_r = "🌱 [Tratamento - Efluente ID: {0}]"
        elif code == "REC":
            json_pontos = os.path.join(hydro.DATA, "pontos_consumo.json")
            json_rede = os.path.join(hydro.DATA, "rede_ids.json")
            tag_p = "⚡ [Moto-Bomba - Recalque ID: {0}]"
            tag_r = "⚡ [Moto-Bomba - Tubo ID: {0}]"
        else: # "AF"
            json_pontos = os.path.join(hydro.DATA, "pontos_consumo.json")
            json_rede = os.path.join(hydro.DATA, "rede_ids.json")
            tag_p = "💧 [Água Fria - Louça ID: {0}]"
            tag_r = "💧 [Água Fria - Barrilete ID: {0}]"

        if not os.path.exists(json_pontos):
            json_pontos = os.path.join(hydro.DATA, "pontos_consumo.json")
            
        items_added = 0
        if os.path.exists(json_pontos):
            try:
                with open(json_pontos, "r") as f:
                    data = json.load(f)
                for pt in data.get("pontos_consumo", []):
                    item = ListBoxItem()
                    item.Content = (tag_p + " {1} — {2}").format(
                        pt.get("id"), pt.get("ambiente", "Ambiente"), pt.get("desc", "Peça")
                    )
                    item.Tag = pt.get("id")
                    item.FontSize = 11
                    lst.Items.Add(item)
                    items_added += 1
            except Exception:
                pass
                
        if os.path.exists(json_rede):
            try:
                with open(json_rede, "r") as f:
                    data_r = json.load(f)
                for no in data_r.get("nos", []):
                    b_id = no.get("barr")
                    if b_id:
                        item = ListBoxItem()
                        item.Content = (tag_r + " Tubulação Principal").format(b_id)
                        item.Tag = b_id
                        item.FontSize = 11
                        lst.Items.Add(item)
                        items_added += 1
            except Exception:
                pass
                
        if items_added == 0:
            item = ListBoxItem()
            item.Content = "(Nenhum elemento desta disciplina identificado ainda. Clique em 'Dimensionar' para calcular)"
            item.FontSize = 11
            lst.Items.Add(item)
            
        return lst

    def render_tab(self, code):
        self.active_tab = code
        self.highlight_tab(code)
        stack = StackPanel()
        
        # Le métricas calculadas em tempo real de config_projeto.json / dimensionamento.json
        hab_num = int(self.cfg_hab) if self.cfg_hab.isdigit() else 6
        dias_num = float(self.cfg_dias) if self.cfg_dias else 2.0
        
        cd_calculado = hab_num * 150.0
        vres_calculado = cd_calculado * dias_num
        
        if code == "CFG":
            tb_h = TextBlock()
            tb_h.Text = "Configurações do Projeto & Leitura BIM"
            tb_h.FontSize = 22
            tb_h.FontWeight = System.Windows.FontWeights.Bold
            tb_h.Foreground = hex_b("#0f172a")
            tb_h.Margin = Thickness(0, 0, 0, 15)
            stack.Children.Add(tb_h)
            
            form_card = Border()
            form_card.Background = hex_b("#ffffff")
            form_card.BorderBrush = hex_b("#cbd5e1")
            form_card.BorderThickness = Thickness(1)
            form_card.CornerRadius = System.Windows.CornerRadius(12)
            form_card.Padding = Thickness(20)
            form_card.Margin = Thickness(0, 0, 0, 20)
            
            fs = StackPanel()
            
            lbl1 = TextBlock()
            lbl1.Text = "Nome do Projeto / Cliente:"
            lbl1.FontSize = 12
            lbl1.FontWeight = System.Windows.FontWeights.SemiBold
            lbl1.Foreground = hex_b("#475569")
            lbl1.Margin = Thickness(0, 0, 0, 4)
            fs.Children.Add(lbl1)
            
            self.txt_nome = TextBox()
            self.txt_nome.Text = self.cfg_nome
            self.txt_nome.Padding = Thickness(8, 6, 8, 6)
            self.txt_nome.Margin = Thickness(0, 0, 0, 12)
            fs.Children.Add(self.txt_nome)
            
            lbl2 = TextBlock()
            lbl2.Text = "Número de Moradores (Habitantes):"
            lbl2.FontSize = 12
            lbl2.FontWeight = System.Windows.FontWeights.SemiBold
            lbl2.Foreground = hex_b("#475569")
            lbl2.Margin = Thickness(0, 0, 0, 4)
            fs.Children.Add(lbl2)
            
            self.txt_hab = TextBox()
            self.txt_hab.Text = self.cfg_hab
            self.txt_hab.Padding = Thickness(8, 6, 8, 6)
            self.txt_hab.Margin = Thickness(0, 0, 0, 12)
            fs.Children.Add(self.txt_hab)
            
            lbl3 = TextBlock()
            lbl3.Text = "Dias de Reservação d'Água (Autonomia):"
            lbl3.FontSize = 12
            lbl3.FontWeight = System.Windows.FontWeights.SemiBold
            lbl3.Foreground = hex_b("#475569")
            lbl3.Margin = Thickness(0, 0, 0, 4)
            fs.Children.Add(lbl3)
            
            self.txt_dias = TextBox()
            self.txt_dias.Text = self.cfg_dias
            self.txt_dias.Padding = Thickness(8, 6, 8, 6)
            self.txt_dias.Margin = Thickness(0, 0, 0, 15)
            fs.Children.Add(self.txt_dias)
            
            btn_save = Button()
            btn_save.Content = "💾 Salvar Configurações do Projeto"
            btn_save.Background = hex_b("#059669")
            btn_save.Foreground = hex_b("#ffffff")
            btn_save.FontWeight = System.Windows.FontWeights.SemiBold
            btn_save.Padding = Thickness(12, 8, 12, 8)
            btn_save.Click += self.salvar_config_projeto
            fs.Children.Add(btn_save)
            
            form_card.Child = fs
            stack.Children.Add(form_card)
            
            card_pendentes = self.carregar_card_loucas_pendentes()
            if card_pendentes:
                stack.Children.Add(card_pendentes)
                
            action_bar = Border()
            action_bar.Background = hex_b("#ffffff")
            action_bar.BorderBrush = hex_b("#cbd5e1")
            action_bar.BorderThickness = Thickness(1)
            action_bar.CornerRadius = System.Windows.CornerRadius(12)
            action_bar.Padding = Thickness(15)
            action_bar.Margin = Thickness(0, 0, 0, 20)
            ab_stack = WrapPanel()
            
            b1 = Button()
            b1.Content = "📋 Executar Leitura de Ambientes e Peças (M1)"
            b1.Background = hex_b("#0284c7")
            b1.Foreground = hex_b("#ffffff")
            b1.FontWeight = System.Windows.FontWeights.SemiBold
            b1.Padding = Thickness(15, 10, 15, 10)
            b1.Click += lambda s, e: self.exec_tool("m1_reader.py", "Leitura do Modelo Arquitetônico (M1)")
            ab_stack.Children.Add(b1)
            
            action_bar.Child = ab_stack
            stack.Children.Add(action_bar)
            
            card_ambientes = self.carregar_card_ambientes_lidos()
            if card_ambientes:
                stack.Children.Add(card_ambientes)

        elif code == "AF":
            tb_h = TextBlock()
            tb_h.Text = "Água Fria (AF)"
            tb_h.FontSize = 22
            tb_h.FontWeight = System.Windows.FontWeights.Bold
            tb_h.Foreground = hex_b("#0f172a")
            tb_h.Margin = Thickness(0, 0, 0, 15)
            stack.Children.Add(tb_h)
            
            m_panel = WrapPanel()
            m_panel.Margin = Thickness(0, 0, 0, 15)
            m_data = [
                ("Consumo Diário Total", "{0:,.0f} L/dia".format(cd_calculado).replace(",", "."), "per capita: 150 L/hab.dia", "#0284c7"),
                ("Volume Reservatório", "{0:,.0f} L".format(vres_calculado).replace(",", "."), "60% inferior / 40% superior", "#d97706"),
                ("Vazão de Projeto Q", "1.42 L/s", "Q = 0,3·√ΣP (NBR 5626)", "#059669"),
                ("Diâmetro Barrilete", "DN 32 mm", "v ≤ 3,0 m/s", "#475569")
            ]
            for title, val, note, color in m_data:
                m_card = Border()
                m_card.Width = 200
                m_card.Background = hex_b("#ffffff")
                m_card.BorderBrush = hex_b("#e2e8f0")
                m_card.BorderThickness = Thickness(1)
                m_card.CornerRadius = System.Windows.CornerRadius(10)
                m_card.Padding = Thickness(15)
                m_card.Margin = Thickness(0, 0, 12, 12)
                
                ms = StackPanel()
                t_lbl = TextBlock()
                t_lbl.Text = title
                t_lbl.FontSize = 11
                t_lbl.Foreground = hex_b("#64748b")
                v_lbl = TextBlock()
                v_lbl.Text = val
                v_lbl.FontSize = 20
                v_lbl.FontWeight = System.Windows.FontWeights.Bold
                v_lbl.Foreground = hex_b(color)
                v_lbl.Margin = Thickness(0, 4, 0, 4)
                n_lbl = TextBlock()
                n_lbl.Text = note
                n_lbl.FontSize = 10
                n_lbl.Foreground = hex_b("#94a3b8")
                
                ms.Children.Add(t_lbl)
                ms.Children.Add(v_lbl)
                ms.Children.Add(n_lbl)
                m_card.Child = ms
                m_panel.Children.Add(m_card)
            stack.Children.Add(m_panel)
            
            lbl_tree = TextBlock()
            lbl_tree.Text = "📍 Elementos & Trechos Água Fria (Clique para Destacar no Revit):"
            lbl_tree.FontSize = 12
            lbl_tree.FontWeight = System.Windows.FontWeights.SemiBold
            lbl_tree.Foreground = hex_b("#0f172a")
            stack.Children.Add(lbl_tree)
            
            stack.Children.Add(self.carregar_elementos_identificados("AF"))
            
            action_bar = Border()
            action_bar.Background = hex_b("#ffffff")
            action_bar.BorderBrush = hex_b("#cbd5e1")
            action_bar.BorderThickness = Thickness(1)
            action_bar.CornerRadius = System.Windows.CornerRadius(12)
            action_bar.Padding = Thickness(15)
            ab_stack = WrapPanel()
            
            b1 = Button()
            b1.Content = "⚡ Calcula & Dimensiona Água Fria"
            b1.Background = hex_b("#0284c7")
            b1.Foreground = hex_b("#ffffff")
            b1.FontWeight = System.Windows.FontWeights.SemiBold
            b1.Padding = Thickness(15, 10, 15, 10)
            b1.Margin = Thickness(0, 0, 10, 0)
            b1.Click += lambda s, e: self.exec_tool("m2_dimensionamento.py", "Dimensionamento Água Fria")
            ab_stack.Children.Add(b1)
            
            b2 = Button()
            b2.Content = "📦 Gera Rede 3D Água Fria no Revit"
            b2.Background = hex_b("#059669")
            b2.Foreground = hex_b("#ffffff")
            b2.FontWeight = System.Windows.FontWeights.SemiBold
            b2.Padding = Thickness(15, 10, 15, 10)
            b2.Margin = Thickness(0, 0, 10, 0)
            b2.Click += lambda s, e: self.exec_tool("m6g_rede_final.py", "Modelagem 3D AF")
            ab_stack.Children.Add(b2)
            
            b3 = Button()
            b3.Content = "📐 Gera Pranchas A4 Água Fria"
            b3.Background = hex_b("#475569")
            b3.Foreground = hex_b("#ffffff")
            b3.FontWeight = System.Windows.FontWeights.SemiBold
            b3.Padding = Thickness(15, 10, 15, 10)
            b3.Click += lambda s, e: self.exec_tool("m7_gerar_pranchas.py", "Pranchas AF")
            ab_stack.Children.Add(b3)
            
            action_bar.Child = ab_stack
            stack.Children.Add(action_bar)

        elif code == "AQ":
            tb_h = TextBlock()
            tb_h.Text = "Água Quente (AQ)"
            tb_h.FontSize = 22
            tb_h.FontWeight = System.Windows.FontWeights.Bold
            tb_h.Foreground = hex_b("#0f172a")
            tb_h.Margin = Thickness(0, 0, 0, 15)
            stack.Children.Add(tb_h)
            
            m_panel = WrapPanel()
            m_panel.Margin = Thickness(0, 0, 0, 15)
            m_data = [
                ("Consumo Água Quente", "{0:,.0f} L/dia".format(cd_calculado * 0.40).replace(",", "."), "per capita: 60 L/hab.dia", "#d97706"),
                ("Volume Boiler / Aquecedor", "{0:,.0f} L".format(cd_calculado * 0.50).replace(",", "."), "Acumulação / Solar", "#0284c7"),
                ("Vazão de Projeto Q_aq", "0.85 L/s", "NBR 7198", "#059669"),
                ("Tubulação Adotada", "CPVC / PPR", "Resistente a 80°C", "#475569")
            ]
            for title, val, note, color in m_data:
                m_card = Border()
                m_card.Width = 200
                m_card.Background = hex_b("#ffffff")
                m_card.BorderBrush = hex_b("#e2e8f0")
                m_card.BorderThickness = Thickness(1)
                m_card.CornerRadius = System.Windows.CornerRadius(10)
                m_card.Padding = Thickness(15)
                m_card.Margin = Thickness(0, 0, 12, 12)
                
                ms = StackPanel()
                t_lbl = TextBlock()
                t_lbl.Text = title
                t_lbl.FontSize = 11
                t_lbl.Foreground = hex_b("#64748b")
                v_lbl = TextBlock()
                v_lbl.Text = val
                v_lbl.FontSize = 20
                v_lbl.FontWeight = System.Windows.FontWeights.Bold
                v_lbl.Foreground = hex_b(color)
                v_lbl.Margin = Thickness(0, 4, 0, 4)
                n_lbl = TextBlock()
                n_lbl.Text = note
                n_lbl.FontSize = 10
                n_lbl.Foreground = hex_b("#94a3b8")
                
                ms.Children.Add(t_lbl)
                ms.Children.Add(v_lbl)
                ms.Children.Add(n_lbl)
                m_card.Child = ms
                m_panel.Children.Add(m_card)
            stack.Children.Add(m_panel)
            
            lbl_tree = TextBlock()
            lbl_tree.Text = "📍 Pontos de Água Quente (Chuveiros, Misturadores, Pias AQ):"
            lbl_tree.FontSize = 12
            lbl_tree.FontWeight = System.Windows.FontWeights.SemiBold
            lbl_tree.Foreground = hex_b("#0f172a")
            stack.Children.Add(lbl_tree)
            
            stack.Children.Add(self.carregar_elementos_identificados("AQ"))
            
            action_bar = Border()
            action_bar.Background = hex_b("#ffffff")
            action_bar.BorderBrush = hex_b("#cbd5e1")
            action_bar.BorderThickness = Thickness(1)
            action_bar.CornerRadius = System.Windows.CornerRadius(12)
            action_bar.Padding = Thickness(15)
            ab_stack = WrapPanel()
            
            b1 = Button()
            b1.Content = "⚡ Calcula Água Quente (NBR 7198)"
            b1.Background = hex_b("#d97706")
            b1.Foreground = hex_b("#ffffff")
            b1.FontWeight = System.Windows.FontWeights.SemiBold
            b1.Padding = Thickness(15, 10, 15, 10)
            b1.Margin = Thickness(0, 0, 10, 0)
            b1.Click += lambda s, e: self.exec_tool("m2_dimensionamento_aq.py", "Dimensionamento Água Quente")
            ab_stack.Children.Add(b1)
            
            b2 = Button()
            b2.Content = "📦 Gera Rede 3D CPVC/PPR no Revit"
            b2.Background = hex_b("#059669")
            b2.Foreground = hex_b("#ffffff")
            b2.FontWeight = System.Windows.FontWeights.SemiBold
            b2.Padding = Thickness(15, 10, 15, 10)
            b2.Margin = Thickness(0, 0, 10, 0)
            b2.Click += lambda s, e: self.exec_tool("m6_rede_agua_quente.py", "Modelagem 3D AQ")
            ab_stack.Children.Add(b2)
            
            action_bar.Child = ab_stack
            stack.Children.Add(action_bar)
            
        elif code == "ESG":
            tb_h = TextBlock()
            tb_h.Text = "Esgoto & Ventilação (ESG)"
            tb_h.FontSize = 22
            tb_h.FontWeight = System.Windows.FontWeights.Bold
            tb_h.Foreground = hex_b("#0f172a")
            tb_h.Margin = Thickness(0, 0, 0, 15)
            stack.Children.Add(tb_h)
            
            m_panel = WrapPanel()
            m_panel.Margin = Thickness(0, 0, 0, 15)
            m_data = [
                ("Total de UHC", "26 UHC", "NBR 8160 Tab. 3", "#0284c7"),
                ("Prumada Esgoto", "DN 100 mm", "PVC série normal", "#d97706"),
                ("Coluna Ventilação", "DN 75 mm", "Ventilação primária", "#059669"),
                ("Caixa de Gordura", "180 L", "CGD dupla", "#475569")
            ]
            for title, val, note, color in m_data:
                m_card = Border()
                m_card.Width = 200
                m_card.Background = hex_b("#ffffff")
                m_card.BorderBrush = hex_b("#e2e8f0")
                m_card.BorderThickness = Thickness(1)
                m_card.CornerRadius = System.Windows.CornerRadius(10)
                m_card.Padding = Thickness(15)
                m_card.Margin = Thickness(0, 0, 12, 12)
                
                ms = StackPanel()
                t_lbl = TextBlock()
                t_lbl.Text = title
                t_lbl.FontSize = 11
                t_lbl.Foreground = hex_b("#64748b")
                v_lbl = TextBlock()
                v_lbl.Text = val
                v_lbl.FontSize = 20
                v_lbl.FontWeight = System.Windows.FontWeights.Bold
                v_lbl.Foreground = hex_b(color)
                v_lbl.Margin = Thickness(0, 4, 0, 4)
                n_lbl = TextBlock()
                n_lbl.Text = note
                n_lbl.FontSize = 10
                n_lbl.Foreground = hex_b("#94a3b8")
                
                ms.Children.Add(t_lbl)
                ms.Children.Add(v_lbl)
                ms.Children.Add(n_lbl)
                m_card.Child = ms
                m_panel.Children.Add(m_card)
            stack.Children.Add(m_panel)
            
            lbl_tree = TextBlock()
            lbl_tree.Text = "📍 Elementos & Trechos Esgoto (Clique para Destacar no Revit):"
            lbl_tree.FontSize = 12
            lbl_tree.FontWeight = System.Windows.FontWeights.SemiBold
            lbl_tree.Foreground = hex_b("#0f172a")
            stack.Children.Add(lbl_tree)
            
            stack.Children.Add(self.carregar_elementos_identificados("ESG"))
            
            action_bar = Border()
            action_bar.Background = hex_b("#ffffff")
            action_bar.BorderBrush = hex_b("#cbd5e1")
            action_bar.BorderThickness = Thickness(1)
            action_bar.CornerRadius = System.Windows.CornerRadius(12)
            action_bar.Padding = Thickness(15)
            ab_stack = WrapPanel()
            
            b1 = Button()
            b1.Content = "⚡ Calcula Esgoto NBR 8160"
            b1.Background = hex_b("#0284c7")
            b1.Foreground = hex_b("#ffffff")
            b1.FontWeight = System.Windows.FontWeights.SemiBold
            b1.Padding = Thickness(15, 10, 15, 10)
            b1.Margin = Thickness(0, 0, 10, 0)
            b1.Click += lambda s, e: self.exec_tool("m2_dimensionamento_esg.py", "Dimensionamento Esgoto")
            ab_stack.Children.Add(b1)
            
            b2 = Button()
            b2.Content = "📦 Gera Rede 3D por Gravidade (com Shaft)"
            b2.Background = hex_b("#059669")
            b2.Foreground = hex_b("#ffffff")
            b2.FontWeight = System.Windows.FontWeights.SemiBold
            b2.Padding = Thickness(15, 10, 15, 10)
            b2.Margin = Thickness(0, 0, 10, 0)
            b2.Click += lambda s, e: self.exec_tool("m6_rede_esgoto.py", "Modelagem 3D Esgoto")
            ab_stack.Children.Add(b2)
            
            b3 = Button()
            b3.Content = "📐 Pranchas ESG (Cozinha / Banheiro)"
            b3.Background = hex_b("#475569")
            b3.Foreground = hex_b("#ffffff")
            b3.FontWeight = System.Windows.FontWeights.SemiBold
            b3.Padding = Thickness(15, 10, 15, 10)
            b3.Click += lambda s, e: self.exec_tool("m7_gerar_pranchas.py", "Pranchas Esgoto")
            ab_stack.Children.Add(b3)
            
            action_bar.Child = ab_stack
            stack.Children.Add(action_bar)
            
        elif code == "PLUV":
            tb_h = TextBlock()
            tb_h.Text = "Águas Pluviais (PLUV)"
            tb_h.FontSize = 22
            tb_h.FontWeight = System.Windows.FontWeights.Bold
            tb_h.Foreground = hex_b("#0f172a")
            tb_h.Margin = Thickness(0, 0, 0, 15)
            stack.Children.Add(tb_h)
            
            m_panel = WrapPanel()
            m_panel.Margin = Thickness(0, 0, 0, 15)
            m_data = [
                ("Intensidade IDF (i)", "156,0 mm/h", "Porto Alegre / SFS", "#0284c7"),
                ("Vazão de Projeto Q", "6,50 L/s", "Q = (i · A) / 3600", "#d97706"),
                ("Condutores Verticais", "2x DN 100", "NBR 10844 / DTU 60.11", "#059669"),
                ("Área de Cobertura", "150 m²", "Área de contribuição", "#475569")
            ]
            for title, val, note, color in m_data:
                m_card = Border()
                m_card.Width = 200
                m_card.Background = hex_b("#ffffff")
                m_card.BorderBrush = hex_b("#e2e8f0")
                m_card.BorderThickness = Thickness(1)
                m_card.CornerRadius = System.Windows.CornerRadius(10)
                m_card.Padding = Thickness(15)
                m_card.Margin = Thickness(0, 0, 12, 12)
                
                ms = StackPanel()
                t_lbl = TextBlock()
                t_lbl.Text = title
                t_lbl.FontSize = 11
                t_lbl.Foreground = hex_b("#64748b")
                v_lbl = TextBlock()
                v_lbl.Text = val
                v_lbl.FontSize = 20
                v_lbl.FontWeight = System.Windows.FontWeights.Bold
                v_lbl.Foreground = hex_b(color)
                v_lbl.Margin = Thickness(0, 4, 0, 4)
                n_lbl = TextBlock()
                n_lbl.Text = note
                n_lbl.FontSize = 10
                n_lbl.Foreground = hex_b("#94a3b8")
                
                ms.Children.Add(t_lbl)
                ms.Children.Add(v_lbl)
                ms.Children.Add(n_lbl)
                m_card.Child = ms
                m_panel.Children.Add(m_card)
            stack.Children.Add(m_panel)
            
            lbl_tree = TextBlock()
            lbl_tree.Text = "📍 Elementos Pluviais (Calhas, Ralos Cobertura, Condutores):"
            lbl_tree.FontSize = 12
            lbl_tree.FontWeight = System.Windows.FontWeights.SemiBold
            lbl_tree.Foreground = hex_b("#0f172a")
            stack.Children.Add(lbl_tree)
            
            stack.Children.Add(self.carregar_elementos_identificados("PLUV"))
            
            action_bar = Border()
            action_bar.Background = hex_b("#ffffff")
            action_bar.BorderBrush = hex_b("#cbd5e1")
            action_bar.BorderThickness = Thickness(1)
            action_bar.CornerRadius = System.Windows.CornerRadius(12)
            action_bar.Padding = Thickness(15)
            ab_stack = WrapPanel()
            
            b1 = Button()
            b1.Content = "⚡ Calcula Pluvial (NBR 10844 / DTU 60.11)"
            b1.Background = hex_b("#0284c7")
            b1.Foreground = hex_b("#ffffff")
            b1.FontWeight = System.Windows.FontWeights.SemiBold
            b1.Padding = Thickness(15, 10, 15, 10)
            b1.Margin = Thickness(0, 0, 10, 0)
            b1.Click += lambda s, e: self.exec_tool("m2_dimensionamento_pluv.py", "Dimensionamento Pluvial")
            ab_stack.Children.Add(b1)
            
            b2 = Button()
            b2.Content = "📐 Gera Pranchas Pluvial/Cobertura"
            b2.Background = hex_b("#475569")
            b2.Foreground = hex_b("#ffffff")
            b2.FontWeight = System.Windows.FontWeights.SemiBold
            b2.Padding = Thickness(15, 10, 15, 10)
            b2.Click += lambda s, e: self.exec_tool("m7_gerar_pranchas.py", "Pranchas Pluvial")
            ab_stack.Children.Add(b2)
            
            action_bar.Child = ab_stack
            stack.Children.Add(action_bar)

        elif code == "TRAT":
            tb_h = TextBlock()
            tb_h.Text = "Tratamento no Lote (TRAT)"
            tb_h.FontSize = 22
            tb_h.FontWeight = System.Windows.FontWeights.Bold
            tb_h.Foreground = hex_b("#0f172a")
            tb_h.Margin = Thickness(0, 0, 0, 15)
            stack.Children.Add(tb_h)
            
            m_panel = WrapPanel()
            m_panel.Margin = Thickness(0, 0, 0, 15)
            m_data = [
                ("Contribuição Esgoto", "{0:,.0f} L/dia".format(cd_calculado * 0.80).replace(",", "."), "80% do consumo de água", "#0284c7"),
                ("Fossa Séptica", "2.000 L", "NBR 7229 (Prisma / Cilíndrica)", "#d97706"),
                ("Filtro Anaeróbio", "1.200 L", "NBR 13969 (Leito filtrante)", "#059669"),
                ("Sumidouro / Vala", "12,5 m²", "Área de infiltração", "#475569")
            ]
            for title, val, note, color in m_data:
                m_card = Border()
                m_card.Width = 200
                m_card.Background = hex_b("#ffffff")
                m_card.BorderBrush = hex_b("#e2e8f0")
                m_card.BorderThickness = Thickness(1)
                m_card.CornerRadius = System.Windows.CornerRadius(10)
                m_card.Padding = Thickness(15)
                m_card.Margin = Thickness(0, 0, 12, 12)
                
                ms = StackPanel()
                t_lbl = TextBlock()
                t_lbl.Text = title
                t_lbl.FontSize = 11
                t_lbl.Foreground = hex_b("#64748b")
                v_lbl = TextBlock()
                v_lbl.Text = val
                v_lbl.FontSize = 20
                v_lbl.FontWeight = System.Windows.FontWeights.Bold
                v_lbl.Foreground = hex_b(color)
                v_lbl.Margin = Thickness(0, 4, 0, 4)
                n_lbl = TextBlock()
                n_lbl.Text = note
                n_lbl.FontSize = 10
                n_lbl.Foreground = hex_b("#94a3b8")
                
                ms.Children.Add(t_lbl)
                ms.Children.Add(v_lbl)
                ms.Children.Add(n_lbl)
                m_card.Child = ms
                m_panel.Children.Add(m_card)
            stack.Children.Add(m_panel)
            
            lbl_tree = TextBlock()
            lbl_tree.Text = "📍 Dispositivos de Tratamento no Lote:"
            lbl_tree.FontSize = 12
            lbl_tree.FontWeight = System.Windows.FontWeights.SemiBold
            lbl_tree.Foreground = hex_b("#0f172a")
            stack.Children.Add(lbl_tree)
            
            stack.Children.Add(self.carregar_elementos_identificados("TRAT"))
            
            action_bar = Border()
            action_bar.Background = hex_b("#ffffff")
            action_bar.BorderBrush = hex_b("#cbd5e1")
            action_bar.BorderThickness = Thickness(1)
            action_bar.CornerRadius = System.Windows.CornerRadius(12)
            action_bar.Padding = Thickness(15)
            ab_stack = WrapPanel()
            
            b1 = Button()
            b1.Content = "🌱 Dimensionar Fossa Séptica, Filtro & Sumidouro"
            b1.Background = hex_b("#059669")
            b1.Foreground = hex_b("#ffffff")
            b1.FontWeight = System.Windows.FontWeights.SemiBold
            b1.Padding = Thickness(15, 10, 15, 10)
            b1.Click += lambda s, e: self.exec_tool("m2_dimensionamento_trat.py", "Dimensionamento Tratamento")
            ab_stack.Children.Add(b1)
            
            action_bar.Child = ab_stack
            stack.Children.Add(action_bar)

        elif code == "REC":
            tb_h = TextBlock()
            tb_h.Text = "Moto-Bomba & Recalque"
            tb_h.FontSize = 22
            tb_h.FontWeight = System.Windows.FontWeights.Bold
            tb_h.Foreground = hex_b("#0f172a")
            tb_h.Margin = Thickness(0, 0, 0, 15)
            stack.Children.Add(tb_h)
            
            m_panel = WrapPanel()
            m_panel.Margin = Thickness(0, 0, 0, 20)
            m_data = [
                ("Vazão de Recalque", "0,33 L/s", "Tempo enchimento: 1.5 h", "#0284c7"),
                ("Altura Manométrica AMT", "18,0 mca", "Geométrica + perdas carga", "#d97706"),
                ("Potência Calculada", "0,50 CV", "Schneider BC-92S (0,37 kW)", "#059669"),
            ]
            for title, val, note, color in m_data:
                m_card = Border()
                m_card.Width = 200
                m_card.Background = hex_b("#ffffff")
                m_card.BorderBrush = hex_b("#e2e8f0")
                m_card.BorderThickness = Thickness(1)
                m_card.CornerRadius = System.Windows.CornerRadius(10)
                m_card.Padding = Thickness(15)
                m_card.Margin = Thickness(0, 0, 12, 12)
                
                ms = StackPanel()
                t_lbl = TextBlock()
                t_lbl.Text = title
                t_lbl.FontSize = 11
                t_lbl.Foreground = hex_b("#64748b")
                v_lbl = TextBlock()
                v_lbl.Text = val
                v_lbl.FontSize = 20
                v_lbl.FontWeight = System.Windows.FontWeights.Bold
                v_lbl.Foreground = hex_b(color)
                v_lbl.Margin = Thickness(0, 4, 0, 4)
                n_lbl = TextBlock()
                n_lbl.Text = note
                n_lbl.FontSize = 10
                n_lbl.Foreground = hex_b("#94a3b8")
                
                ms.Children.Add(t_lbl)
                ms.Children.Add(v_lbl)
                ms.Children.Add(n_lbl)
                m_card.Child = ms
                m_panel.Children.Add(m_card)
            stack.Children.Add(m_panel)
            
            action_bar = Border()
            action_bar.Background = hex_b("#ffffff")
            action_bar.BorderBrush = hex_b("#cbd5e1")
            action_bar.BorderThickness = Thickness(1)
            action_bar.CornerRadius = System.Windows.CornerRadius(12)
            action_bar.Padding = Thickness(15)
            ab_stack = WrapPanel()
            
            b1 = Button()
            b1.Content = "⚡ Dimensionar Conjunto Elevatório (Moto-Bomba)"
            b1.Background = hex_b("#0284c7")
            b1.Foreground = hex_b("#ffffff")
            b1.FontWeight = System.Windows.FontWeights.SemiBold
            b1.Padding = Thickness(15, 10, 15, 10)
            b1.Click += lambda s, e: self.exec_tool("m2_dimensionamento_bomba.py", "Dimensionamento Moto-Bomba")
            ab_stack.Children.Add(b1)
            
            action_bar.Child = ab_stack
            stack.Children.Add(action_bar)
            
        elif code == "AUDIT":
            tb_h = TextBlock()
            tb_h.Text = "Auditoria, Acervo & Template Oficial"
            tb_h.FontSize = 22
            tb_h.FontWeight = System.Windows.FontWeights.Bold
            tb_h.Foreground = hex_b("#0f172a")
            tb_h.Margin = Thickness(0, 0, 0, 15)
            stack.Children.Add(tb_h)
            
            action_bar = Border()
            action_bar.Background = hex_b("#ffffff")
            action_bar.BorderBrush = hex_b("#cbd5e1")
            action_bar.BorderThickness = Thickness(1)
            action_bar.CornerRadius = System.Windows.CornerRadius(12)
            action_bar.Padding = Thickness(15)
            ab_stack = WrapPanel()
            
            b1 = Button()
            b1.Content = "🔍 Executar Auditoria de Interferências & Regras"
            b1.Background = hex_b("#0284c7")
            b1.Foreground = hex_b("#ffffff")
            b1.FontWeight = System.Windows.FontWeights.SemiBold
            b1.Padding = Thickness(15, 10, 15, 10)
            b1.Margin = Thickness(0, 0, 10, 10)
            b1.Click += lambda s, e: self.exec_tool("m0_audit_bridge.py", "Auditoria de Modelo")
            ab_stack.Children.Add(b1)
            
            b2 = Button()
            b2.Content = "📚 Verificar Acervo de Famílias no Template"
            b2.Background = hex_b("#475569")
            b2.Foreground = hex_b("#ffffff")
            b2.FontWeight = System.Windows.FontWeights.SemiBold
            b2.Padding = Thickness(15, 10, 15, 10)
            b2.Margin = Thickness(0, 0, 10, 10)
            b2.Click += lambda s, e: self.exec_tool("verificar_acervo.py", "Verificação do Acervo")
            ab_stack.Children.Add(b2)
            
            b3 = Button()
            b3.Content = "🏛️ Convert Modelo Atual em Template Oficial (.rte / .rvt)"
            b3.Background = hex_b("#d97706")
            b3.Foreground = hex_b("#ffffff")
            b3.FontWeight = System.Windows.FontWeights.SemiBold
            b3.Padding = Thickness(15, 10, 15, 10)
            b3.Margin = Thickness(0, 0, 10, 10)
            b3.Click += lambda s, e: self.exec_tool("make_official_template.py", "Criação de Template Oficial (.rte)")
            ab_stack.Children.Add(b3)
            
            action_bar.Child = ab_stack
            stack.Children.Add(action_bar)

        elif code == "DOC":
            tb_h = TextBlock()
            tb_h.Text = "Memoriais & Exportação (HTML, PDF, DOCX)"
            tb_h.FontSize = 22
            tb_h.FontWeight = System.Windows.FontWeights.Bold
            tb_h.Foreground = hex_b("#0f172a")
            tb_h.Margin = Thickness(0, 0, 0, 15)
            stack.Children.Add(tb_h)
            
            action_bar = Border()
            action_bar.Background = hex_b("#ffffff")
            action_bar.BorderBrush = hex_b("#cbd5e1")
            action_bar.BorderThickness = Thickness(1)
            action_bar.CornerRadius = System.Windows.CornerRadius(12)
            action_bar.Padding = Thickness(15)
            ab_stack = WrapPanel()
            
            b1 = Button()
            b1.Content = "📄 Gerar Memorial Hidráulico (AF/AQ)"
            b1.Background = hex_b("#0284c7")
            b1.Foreground = hex_b("#ffffff")
            b1.FontWeight = System.Windows.FontWeights.SemiBold
            b1.Padding = Thickness(15, 10, 15, 10)
            b1.Margin = Thickness(0, 0, 10, 0)
            b1.Click += lambda s, e: self.exec_tool("m8_memorial.py", "Memorial Hidráulico")
            ab_stack.Children.Add(b1)
            
            b2 = Button()
            b2.Content = "🚽 Gerar Memorial Sanitário (ESG)"
            b2.Background = hex_b("#059669")
            b2.Foreground = hex_b("#ffffff")
            b2.FontWeight = System.Windows.FontWeights.SemiBold
            b2.Padding = Thickness(15, 10, 15, 10)
            b2.Margin = Thickness(0, 0, 10, 0)
            b2.Click += lambda s, e: self.exec_tool("m8_memorial_esg.py", "Memorial Sanitário")
            ab_stack.Children.Add(b2)
            
            b3 = Button()
            b3.Content = "🌧️ Gerar Memorial Pluvial (PLUV)"
            b3.Background = hex_b("#d97706")
            b3.Foreground = hex_b("#ffffff")
            b3.FontWeight = System.Windows.FontWeights.SemiBold
            b3.Padding = Thickness(15, 10, 15, 10)
            b3.Click += lambda s, e: self.exec_tool("m8_memorial_pluv.py", "Memorial Pluvial")
            ab_stack.Children.Add(b3)
            
            action_bar.Child = ab_stack
            stack.Children.Add(action_bar)
            
        # Live Feedback Status Box
        self.status_box = Border()
        self.status_box.Background = hex_b("#f1f5f9")
        self.status_box.BorderBrush = hex_b("#cbd5e1")
        self.status_box.BorderThickness = Thickness(1)
        self.status_box.CornerRadius = System.Windows.CornerRadius(8)
        self.status_box.Padding = Thickness(12)
        self.status_box.Margin = Thickness(0, 20, 0, 0)
        
        self.status_txt = TextBlock()
        self.status_txt.Text = "Pronto. Clique em um elemento na lista para destacá-lo no Revit ou em um botão para calcular."
        self.status_txt.FontSize = 11
        self.status_txt.Foreground = hex_b("#475569")
        self.status_txt.TextWrapping = TextWrapping.Wrap
        self.status_box.Child = self.status_txt
        
        stack.Children.Add(self.status_box)
        self.main_content.Content = stack

    def exec_tool(self, script_name, description):
        self.status_txt.Text = "⏳ Executando {0} no Revit... por favor aguarde.".format(description)
        try:
            res = hydro.rodar(script_name)
            self.status_txt.Text = "✅ {0} concluído com sucesso!\n\n{1}".format(description, str(res)[:300])
            self.render_tab(self.active_tab)
        except Exception as ex:
            self.status_txt.Text = "⚠️ Aviso ao executar {0}: {1}".format(description, str(ex))

win = HydroStudioInteractiveWindow()
win.ShowDialog()
