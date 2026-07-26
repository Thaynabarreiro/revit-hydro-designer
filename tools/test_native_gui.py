# -*- coding: utf-8 -*-
"""Hydro Design Hub — Native WPF Studio Window for pyRevit inside Revit.
Provides the exact light theme UI/UX of hydro-design-hub directly inside Revit.
"""
import os
import json
import math
import codecs
import clr

clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")
clr.AddReference("WindowsBase")
clr.AddReference("System.Xaml")

import System
from System.Windows import (
    Window, WindowStartupLocation, Thickness, HorizontalAlignment, VerticalAlignment,
    GridLength, GridUnitType, TextWrapping, Visibility
)
from System.Windows.Controls import (
    Grid, StackPanel, Border, TextBlock, TextBox, ComboBox, ComboBoxItem,
    Button, ScrollViewer, TabControl, TabItem, ColumnDefinition, RowDefinition,
    WrapPanel, Orientation
)
from System.Windows.Media import SolidColorBrush, ColorConverter, FontFamily

_this_dir = os.path.dirname(os.path.abspath(__file__))
_auto_root = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "tools" else _this_dir
RAIZ = globals().get("RAIZ", os.environ.get("HYDRO_PROJECT_ROOT", _auto_root))
D = os.path.join(RAIZ, "data")

def hex_brush(hex_code):
    return SolidColorBrush(ColorConverter.ConvertFromString(hex_code))

class HydroStudioWindow(Window):
    def __init__(self):
        self.Title = "Revit Hydro Designer — Studio BIM"
        self.Width = 1180
        self.Height = 780
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.Background = hex_brush("#f8fafc")
        
        # Main Grid Layout: Left Sidebar + Right Content Area
        main_grid = Grid()
        col_side = ColumnDefinition()
        col_side.Width = GridLength(280)
        col_main = ColumnDefinition()
        col_main.Width = GridLength(1, GridUnitType.Star)
        main_grid.ColumnDefinitions.Add(col_side)
        main_grid.ColumnDefinitions.Add(col_main)
        
        # --- LEFT SIDEBAR ---
        sidebar = Border()
        sidebar.Background = hex_brush("#ffffff")
        sidebar.BorderBrush = hex_brush("#e2e8f0")
        sidebar.BorderThickness = Thickness(0, 0, 1, 0)
        sidebar.Padding = Thickness(20)
        
        side_stack = StackPanel()
        
        # Header Logo Badge
        logo_panel = StackPanel()
        logo_panel.Orientation = Orientation.Horizontal
        logo_panel.Margin = Thickness(0, 0, 0, 20)
        
        logo_icon = Border()
        logo_icon.Width = 40
        logo_icon.Height = 40
        logo_icon.CornerRadius = System.Windows.CornerRadius(10)
        logo_icon.Background = hex_brush("#e0f2fe")
        logo_icon.BorderBrush = hex_brush("#bae6fd")
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
        tb_title.Foreground = hex_brush("#0284c7")
        
        tb_sub = TextBlock()
        tb_sub.Text = "BIM · Hidrossanitário & Pluvial"
        tb_sub.FontSize = 11
        tb_sub.Foreground = hex_brush("#64748b")
        
        logo_text_stack.Children.Add(tb_title)
        logo_text_stack.Children.Add(tb_sub)
        logo_panel.Children.Add(logo_text_stack)
        
        side_stack.Children.Add(logo_panel)
        
        # Status Badge Revit Connected
        status_card = Border()
        status_card.Background = hex_brush("#dcfce7")
        status_card.BorderBrush = hex_brush("#86efac")
        status_card.BorderThickness = Thickness(1)
        status_card.CornerRadius = System.Windows.CornerRadius(8)
        status_card.Padding = Thickness(10, 8, 10, 8)
        status_card.Margin = Thickness(0, 0, 0, 20)
        
        tb_status = TextBlock()
        tb_status.Text = "● Revit 2027 Connected"
        tb_status.FontWeight = System.Windows.FontWeights.SemiBold
        tb_status.FontSize = 12
        tb_status.Foreground = hex_brush("#15803d")
        status_card.Child = tb_status
        side_stack.Children.Add(status_card)
        
        # Active Project Selector
        tb_proj_lbl = TextBlock()
        tb_proj_lbl.Text = "PROJETO ATIVO"
        tb_proj_lbl.FontSize = 10
        tb_proj_lbl.FontWeight = System.Windows.FontWeights.Bold
        tb_proj_lbl.Foreground = hex_brush("#64748b")
        tb_proj_lbl.Margin = Thickness(0, 0, 0, 5)
        side_stack.Children.Add(tb_proj_lbl)
        
        self.cb_proj = ComboBox()
        self.cb_proj.Padding = Thickness(8, 6, 8, 6)
        self.cb_proj.Margin = Thickness(0, 0, 0, 25)
        self.cb_proj.Items.Add("Residência Unifamiliar — Porto Alegre")
        self.cb_proj.Items.Add("Edifício Aurora 12 Pav. — São Paulo")
        self.cb_proj.Items.Add("Maison Lumière — Lyon (FR)")
        self.cb_proj.SelectedIndex = 0
        side_stack.Children.Add(self.cb_proj)
        
        # Navigation Menu Info
        tb_nav_lbl = TextBlock()
        tb_nav_lbl.Text = "DISCIPLINAS BIM"
        tb_nav_lbl.FontSize = 10
        tb_nav_lbl.FontWeight = System.Windows.FontWeights.Bold
        tb_nav_lbl.Foreground = hex_brush("#64748b")
        tb_nav_lbl.Margin = Thickness(0, 0, 0, 10)
        side_stack.Children.Add(tb_nav_lbl)
        
        disc_list = [
          ("💧 Água Fria & Quente", "HID"),
          ("🚽 Esgoto & Ventilação", "ESG"),
          ("🌧️ Pluvial & Tratamento", "PLUV / TRAT"),
          ("⚡ Moto-Bomba & Recalque", "REC"),
          ("📄 Memoriais & Exportação", "DOC"),
        ]
        for name, code in disc_list:
            btn_item = Border()
            btn_item.Background = hex_brush("#f1f5f9")
            btn_item.CornerRadius = System.Windows.CornerRadius(8)
            btn_item.Padding = Thickness(12, 10, 12, 10)
            btn_item.Margin = Thickness(0, 0, 0, 6)
            
            sp_item = StackPanel()
            sp_item.Orientation = Orientation.Horizontal
            
            tb_n = TextBlock()
            tb_n.Text = name
            tb_n.FontSize = 12
            tb_n.FontWeight = System.Windows.FontWeights.Medium
            tb_n.Foreground = hex_brush("#0f172a")
            
            sp_item.Children.Add(tb_n)
            btn_item.Child = sp_item
            side_stack.Children.Add(btn_item)
            
        sidebar.Child = side_stack
        Grid.SetColumn(sidebar, 0)
        main_grid.Children.Add(sidebar)
        
        # --- RIGHT CONTENT AREA ---
        main_content = ScrollViewer()
        main_content.Padding = Thickness(25)
        
        content_stack = StackPanel()
        
        # Top Banner Title
        tb_main_header = TextBlock()
        tb_main_header.Text = "Água Fria & Quente (HID)"
        tb_main_header.FontSize = 22
        tb_main_header.FontWeight = System.Windows.FontWeights.Bold
        tb_main_header.Foreground = hex_brush("#0f172a")
        tb_main_header.Margin = Thickness(0, 0, 0, 15)
        content_stack.Children.Add(tb_main_header)
        
        # Metric Cards Grid (Consumo, Volume, Vazão, Barrilete)
        metrics_panel = WrapPanel()
        metrics_panel.Margin = Thickness(0, 0, 0, 20)
        
        metrics_data = [
            ("Consumo Diário Total", "1.800 L/dia", "per capita: 150 L/hab.dia", "#0284c7"),
            ("Volume Reservatório", "3.600 L", "60% inferior / 40% superior", "#d97706"),
            ("Vazão de Projeto Q", "1.42 L/s", "Q = 0,3·√ΣP", "#059669"),
            ("Diâmetro Barrilete", "DN 32 mm", "v ≤ 3,0 m/s (NBR 5626)", "#475569")
        ]
        
        for title, val, note, color in metrics_data:
            m_card = Border()
            m_card.Width = 200
            m_card.Background = hex_brush("#ffffff")
            m_card.BorderBrush = hex_brush("#e2e8f0")
            m_card.BorderThickness = Thickness(1)
            m_card.CornerRadius = System.Windows.CornerRadius(10)
            m_card.Padding = Thickness(15)
            m_card.Margin = Thickness(0, 0, 12, 12)
            
            m_stack = StackPanel()
            
            t_lbl = TextBlock()
            t_lbl.Text = title
            t_lbl.FontSize = 11
            t_lbl.Foreground = hex_brush("#64748b")
            
            v_lbl = TextBlock()
            v_lbl.Text = val
            v_lbl.FontSize = 20
            v_lbl.FontWeight = System.Windows.FontWeights.Bold
            v_lbl.Foreground = hex_brush(color)
            v_lbl.Margin = Thickness(0, 4, 0, 4)
            
            n_lbl = TextBlock()
            n_lbl.Text = note
            n_lbl.FontSize = 10
            n_lbl.Foreground = hex_brush("#94a3b8")
            
            m_stack.Children.Add(t_lbl)
            m_stack.Children.Add(v_lbl)
            m_stack.Children.Add(n_lbl)
            m_card.Child = m_stack
            metrics_panel.Children.Add(m_card)
            
        content_stack.Children.Add(metrics_panel)
        
        # Action Buttons Glass Bar (Calcula, Gera 3D, Gera Pranchas)
        action_bar = Border()
        action_bar.Background = hex_brush("#ffffff")
        action_bar.BorderBrush = hex_brush("#cbd5e1")
        action_bar.BorderThickness = Thickness(1)
        action_bar.CornerRadius = System.Windows.CornerRadius(12)
        action_bar.Padding = Thickness(15)
        
        ab_stack = WrapPanel()
        
        btn_calc = Button()
        btn_calc.Content = "⚡ Calcula & Dimensiona AF/AQ"
        btn_calc.Background = hex_brush("#0284c7")
        btn_calc.Foreground = hex_brush("#ffffff")
        btn_calc.FontWeight = System.Windows.FontWeights.SemiBold
        btn_calc.Padding = Thickness(15, 10, 15, 10)
        btn_calc.Margin = Thickness(0, 0, 10, 0)
        btn_calc.Click += self.on_calc
        ab_stack.Children.Add(btn_calc)
        
        btn_3d = Button()
        btn_3d.Content = "📦 Gera Rede 3D Ortogonal no Revit"
        btn_3d.Background = hex_brush("#059669")
        btn_3d.Foreground = hex_brush("#ffffff")
        btn_3d.FontWeight = System.Windows.FontWeights.SemiBold
        btn_3d.Padding = Thickness(15, 10, 15, 10)
        btn_3d.Margin = Thickness(0, 0, 10, 0)
        btn_3d.Click += self.on_3d
        ab_stack.Children.Add(btn_3d)
        
        btn_pranchas = Button()
        btn_pranchas.Content = "📐 Gera Pranchas A4 por Ambiente"
        btn_pranchas.Background = hex_brush("#475569")
        btn_pranchas.Foreground = hex_brush("#ffffff")
        btn_pranchas.FontWeight = System.Windows.FontWeights.SemiBold
        btn_pranchas.Padding = Thickness(15, 10, 15, 10)
        btn_pranchas.Click += self.on_pranchas
        ab_stack.Children.Add(btn_pranchas)
        
        action_bar.Child = ab_stack
        content_stack.Children.Add(action_bar)
        
        main_content.Content = content_stack
        Grid.SetColumn(main_content, 1)
        main_grid.Children.Add(main_content)
        
        self.Content = main_grid

    def on_calc(self, sender, args):
        import hydro
        print(hydro.rodar("m2_dimensionamento.py"))
        
    def on_3d(self, sender, args):
        import hydro
        print(hydro.rodar("m6g_rede_final.py"))
        
    def on_pranchas(self, sender, args):
        import hydro
        print(hydro.rodar("m7_gerar_pranchas.py"))

if __name__ == "__main__":
    win = HydroStudioWindow()
    win.ShowDialog()
