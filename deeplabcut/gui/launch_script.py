"""
DeepLabCut2.0 Toolbox (deeplabcut.org)
© A. & M. Mathis Labs
https://github.com/AlexEMG/DeepLabCut
Please see AUTHORS for contributors.

https://github.com/AlexEMG/DeepLabCut/blob/master/AUTHORS
Licensed under GNU Lesser General Public License v3.0

"""

import wx
from deeplabcut.gui.welcome import Welcome


class MainFrame(wx.Frame):
    def __init__(self):
        #        wx.Frame.__init__(self, None, title="DeepLabCut")
        # Gets the number of displays
        displays = (wx.Display(i) for i in range(wx.Display.GetCount()))
        screenSizes = [display.GetGeometry().GetSize()
                       for display in displays]  # Gets the size of each display
        index = 0  # For display Last
        screenWidth = screenSizes[index][0]
        screenHeight = screenSizes[index][1]
        self.gui_size = (screenWidth*0.7, screenHeight*0.55)
        wx.Frame.__init__(self, None, wx.ID_ANY, "DeepLabCut", size=wx.Size(
            self.gui_size), pos=wx.DefaultPosition, style=wx.RESIZE_BORDER | wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        # This sets the minimum size of the GUI. It can scale now!
        self.SetSizeHints(wx.Size(self.gui_size))
        # Here we create a panel and a notebook on the panel
        self.panel = wx.Panel(self)
        self.nb = wx.Notebook(self.panel)
        # create the page windows as children of the notebook and add the pages to the notebook with the label to show on the tab
        page1 = Welcome(self.nb, self.gui_size)
        self.nb.AddPage(page1, "Welcome")


        self.sizer = wx.BoxSizer()
        self.sizer.Add(self.nb, 1, wx.EXPAND)
        self.panel.SetSizer(self.sizer)


def launch_dlc():
    app = wx.App()
    frame = MainFrame().Show()
    app.MainLoop()


if __name__ == '__main__':
    launch_dlc()
