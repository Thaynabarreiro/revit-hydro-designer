# -*- coding: utf-8 -*-
"""Test opening WPF WebBrowser window INSIDE Revit."""
import clr
clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")
clr.AddReference("WindowsBase")

from System.Windows import Window, WindowStartupLocation
from System.Windows.Controls import Grid, WebBrowser

class HydroWebDialog(Window):
    def __init__(self, url):
        self.Title = "Hydro Design Hub — BIM Studio (Inside Revit)"
        self.Width = 1100
        self.Height = 750
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        
        grid = Grid()
        self.wb = WebBrowser()
        grid.Children.Add(self.wb)
        self.Content = grid
        
        self.wb.Navigate(url)

try:
    win = HydroWebDialog("https://github.com/Thaynabarreiro/hydro-design-hub")
    win.Show()
    print("WPF Web Window opened inside Revit successfully!")
except Exception as ex:
    print("Error opening WPF Web Window inside Revit:", ex)
