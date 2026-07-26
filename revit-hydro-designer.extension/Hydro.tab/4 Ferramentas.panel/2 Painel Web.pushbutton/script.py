# -*- coding: utf-8 -*-
import os, sys, clr
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
    Button, ScrollViewer, ColumnDefinition, RowDefinition, WrapPanel, Orientation
)
from System.Windows.Media import SolidColorBrush, ColorConverter

import hydro

def hex_b(hex_code):
    return SolidColorBrush(ColorConverter.ConvertFromString(hex_code))

class HydroStudioInteractiveWindow(Window):
    def __init__(self):
        self.Title = "Revit Hydro Designer — Studio BIM"
        self.Width = 1180
        self.Height = 780
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.Background = hex_b("#f8fafc")
        self.active_tab = "CFG"
        
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
        status_card.Margin = Thickness(0, 0, 0, 20)
        
        tb_status = TextBlock()
        tb_status.Text = "● Revit Connected"
        tb_status.FontWeight = System.Windows.FontWeights.SemiBold
        tb_status.FontSize = 12
        tb_status.Foreground = hex_b("#15803d")
        status_card.Child = tb_status
        side_stack.Children.Add(status_card)
        
        disc_items = [
            ("⚙️ Configurações do Projeto", "CFG"),
            ("💧 Água Fria & Quente", "HID"),
            ("🚽 Esgoto & Ventilação", "ESG"),
            ("🌧️ Pluvial & Tratamento", "PLUV"),
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

    def render_tab(self, code):
        self.highlight_tab(code)
        stack = StackPanel()
        
        if code == "CFG":
            tb_h = TextBlock()
            tb_h.Text = "Configurações do Projeto & Leitura BIM"
            tb_h.FontSize = 22
            tb_h.FontWeight = System.Windows.FontWeights.Bold
            tb_h.Foreground = hex_b("#0f172a")
            tb_h.Margin = Thickness(0, 0, 0, 15)
            stack.Children.Add(tb_h)
            
            # Form Inputs Card
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
            self.txt_nome.Text = "Casa Unifamiliar Henrique & Suelen"
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
            self.txt_hab.Text = "6"
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
            self.txt_dias.Text = "2"
            self.txt_dias.Padding = Thickness(8, 6, 8, 6)
            self.txt_dias.Margin = Thickness(0, 0, 0, 15)
            fs.Children.Add(self.txt_dias)
            
            form_card.Child = fs
            stack.Children.Add(form_card)
            
            action_bar = Border()
            action_bar.Background = hex_b("#ffffff")
            action_bar.BorderBrush = hex_b("#cbd5e1")
            action_bar.BorderThickness = Thickness(1)
            action_bar.CornerRadius = System.Windows.CornerRadius(12)
            action_bar.Padding = Thickness(15)
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

        elif code == "HID":
            tb_h = TextBlock()
            tb_h.Text = "Água Fria & Quente (HID)"
            tb_h.FontSize = 22
            tb_h.FontWeight = System.Windows.FontWeights.Bold
            tb_h.Foreground = hex_b("#0f172a")
            tb_h.Margin = Thickness(0, 0, 0, 15)
            stack.Children.Add(tb_h)
            
            m_panel = WrapPanel()
            m_panel.Margin = Thickness(0, 0, 0, 20)
            m_data = [
                ("Consumo Diário Total", "1.800 L/dia", "per capita: 150 L/hab.dia", "#0284c7"),
                ("Volume Reservatório", "3.600 L", "60% inferior / 40% superior", "#d97706"),
                ("Vazão de Projeto Q", "1.42 L/s", "Q = 0,3·√ΣP", "#059669"),
                ("Diâmetro Barrilete", "DN 32 mm", "v ≤ 3,0 m/s (NBR 5626)", "#475569")
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
            b1.Content = "⚡ Calcula & Dimensiona AF/AQ"
            b1.Background = hex_b("#0284c7")
            b1.Foreground = hex_b("#ffffff")
            b1.FontWeight = System.Windows.FontWeights.SemiBold
            b1.Padding = Thickness(15, 10, 15, 10)
            b1.Margin = Thickness(0, 0, 10, 0)
            b1.Click += lambda s, e: self.exec_tool("m2_dimensionamento.py", "Dimensionamento AF/AQ")
            ab_stack.Children.Add(b1)
            
            b2 = Button()
            b2.Content = "📦 Gera Rede 3D Ortogonal no Revit"
            b2.Background = hex_b("#059669")
            b2.Foreground = hex_b("#ffffff")
            b2.FontWeight = System.Windows.FontWeights.SemiBold
            b2.Padding = Thickness(15, 10, 15, 10)
            b2.Margin = Thickness(0, 0, 10, 0)
            b2.Click += lambda s, e: self.exec_tool("m6g_rede_final.py", "Modelagem 3D AF/AQ")
            ab_stack.Children.Add(b2)
            
            b3 = Button()
            b3.Content = "📐 Gera Pranchas A4 por Ambiente"
            b3.Background = hex_b("#475569")
            b3.Foreground = hex_b("#ffffff")
            b3.FontWeight = System.Windows.FontWeights.SemiBold
            b3.Padding = Thickness(15, 10, 15, 10)
            b3.Click += lambda s, e: self.exec_tool("m7_gerar_pranchas.py", "Pranchas A4")
            ab_stack.Children.Add(b3)
            
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
            m_panel.Margin = Thickness(0, 0, 0, 20)
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
            b3.Content = "📐 Pranchas ESG (Cozinha 04/001 / Banheiro 08/001)"
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
            tb_h.Text = "Pluvial & Tratamento (PLUV / TRAT)"
            tb_h.FontSize = 22
            tb_h.FontWeight = System.Windows.FontWeights.Bold
            tb_h.Foreground = hex_b("#0f172a")
            tb_h.Margin = Thickness(0, 0, 0, 15)
            stack.Children.Add(tb_h)
            
            m_panel = WrapPanel()
            m_panel.Margin = Thickness(0, 0, 0, 20)
            m_data = [
                ("Intensidade IDF (i)", "156,0 mm/h", "Porto Alegre / SFS", "#0284c7"),
                ("Vazão de Projeto Q", "6,50 L/s", "Q = (i · A) / 3600", "#d97706"),
                ("Condutores Verticais", "2x DN 100", "NBR 10844 / DTU 60.11", "#059669"),
                ("Fossa Séptica", "2.000 L", "NBR 7229 / NBR 13969", "#475569")
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
            b1.Content = "⚡ Calcula Pluvial NBR 10844 / DTU 60.11"
            b1.Background = hex_b("#0284c7")
            b1.Foreground = hex_b("#ffffff")
            b1.FontWeight = System.Windows.FontWeights.SemiBold
            b1.Padding = Thickness(15, 10, 15, 10)
            b1.Margin = Thickness(0, 0, 10, 0)
            b1.Click += lambda s, e: self.exec_tool("m2_dimensionamento_pluv.py", "Dimensionamento Pluvial")
            ab_stack.Children.Add(b1)
            
            b2 = Button()
            b2.Content = "🌱 Dimensionar Tratamento (Fossa/Filtro/Sumidouro)"
            b2.Background = hex_b("#d97706")
            b2.Foreground = hex_b("#ffffff")
            b2.FontWeight = System.Windows.FontWeights.SemiBold
            b2.Padding = Thickness(15, 10, 15, 10)
            b2.Margin = Thickness(0, 0, 10, 0)
            b2.Click += lambda s, e: self.exec_tool("m2_dimensionamento_trat.py", "Dimensionamento Tratamento")
            ab_stack.Children.Add(b2)
            
            b3 = Button()
            b3.Content = "📐 Gera Pranchas Pluvial/Cobertura (13/001)"
            b3.Background = hex_b("#475569")
            b3.Foreground = hex_b("#ffffff")
            b3.FontWeight = System.Windows.FontWeights.SemiBold
            b3.Padding = Thickness(15, 10, 15, 10)
            b3.Click += lambda s, e: self.exec_tool("m7_gerar_pranchas.py", "Pranchas Pluvial")
            ab_stack.Children.Add(b3)
            
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
            tb_h.Text = "Auditoria e Verificação do Modelo BIM"
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
            b1.Margin = Thickness(0, 0, 10, 0)
            b1.Click += lambda s, e: self.exec_tool("m0_audit_bridge.py", "Auditoria de Modelo")
            ab_stack.Children.Add(b1)
            
            b2 = Button()
            b2.Content = "📚 Verificar Acervo de Famílias no Template"
            b2.Background = hex_b("#475569")
            b2.Foreground = hex_b("#ffffff")
            b2.FontWeight = System.Windows.FontWeights.SemiBold
            b2.Padding = Thickness(15, 10, 15, 10)
            b2.Click += lambda s, e: self.exec_tool("verificar_acervo.py", "Verificação do Acervo")
            ab_stack.Children.Add(b2)
            
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
        self.status_txt.Text = "Pronto. Clique em qualquer botão para executar no modelo do Revit."
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
        except Exception as ex:
            self.status_txt.Text = "⚠️ Aviso ao executar {0}: {1}".format(description, str(ex))

win = HydroStudioInteractiveWindow()
win.ShowDialog()
