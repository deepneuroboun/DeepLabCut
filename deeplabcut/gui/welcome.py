"""
DeepLabCut2.0 Toolbox (deeplabcut.org)
© A. & M. Mathis Labs
https://github.com/AlexEMG/DeepLabCut
Please see AUTHORS for contributors.

https://github.com/AlexEMG/DeepLabCut/blob/master/AUTHORS
Licensed under GNU Lesser General Public License v3.0

"""

import os
import wx
import wx.adv
import deeplabcut
from deeplabcut.gui.create_new_project import CreateNewProject

media_path = os.path.join(deeplabcut.__path__[0], 'gui' , 'media')
dlc = os.path.join(media_path,'dlc_1-01.png')
bounneuro = os.path.join(media_path, 'bounneuro.png')

class Welcome(wx.Panel):
    SCALE = 5

    def __init__(self, parent,gui_size):
        wx.Panel.__init__(self, parent)
        h=gui_size[0]
        w=gui_size[1]
        wx.Panel.__init__(self, parent, -1,style=wx.SUNKEN_BORDER,size=(h,w))

        self.opened_paradigms = {}
##         design the panel
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        #if editing this text make sure you add the '\n' to get the new line. The sizer is unable to format lines correctly.
        description = "Welcome to modified version of DeepLabCut2.0!\nThis program is modified for Behavioral Neuroscience Lab.\nJust select the experimental paradigms from the options below."

        self.parent = parent
        self.gui_size = gui_size
        self.proj_name = wx.StaticText(self, label=description,style=wx.ALIGN_CENTRE)
        main_sizer.Add(self.proj_name, proportion=3, flag=wx.EXPAND, border=10)

        # Experimental Paradigms
        lines = [["OFT", "EPM"], ["WYM", "MWM", "FST"]]
        is_active = [[True, False],[False, True, False]]
        line_sizers = [None] * len(lines)

        for i, line in enumerate(lines):
            line_sizers[i] = wx.BoxSizer(wx.HORIZONTAL)
            control = is_active[i]
            for j, elem in enumerate(line):
                cur_button = wx.Button(self, label=elem, size=wx.Size(100,200))
                cur_button.Bind(wx.EVT_BUTTON, self.goto_paradigm)
                if(not control[j]):
                    cur_button.Disable()
                line_sizers[i].Add(cur_button, flag=wx.ALL, border=10)
            main_sizer.Add(line_sizers[i], proportion=1, flag=wx.ALIGN_CENTER)




        # Add images of DLC and Boun Neuro
        icon_sizer = wx.BoxSizer(wx.HORIZONTAL)
        icon_image = wx.Image(dlc, type=wx.BITMAP_TYPE_PNG)
        boun_image = wx.Image(bounneuro, type=wx.BITMAP_TYPE_PNG)

        icon = wx.StaticBitmap(self, bitmap=wx.Bitmap(icon_image.Scale(icon_image.GetWidth() // self.SCALE, icon_image.GetHeight() // self.SCALE, wx.IMAGE_QUALITY_HIGH)))
        boun = wx.StaticBitmap(self, bitmap=wx.Bitmap(boun_image.Scale(boun_image.GetWidth() // self.SCALE, boun_image.GetHeight() // self.SCALE, wx.IMAGE_QUALITY_HIGH)))

        icon_sizer.Add(boun, proportion=1, flag=wx.EXPAND)
        icon_sizer.Add(icon, proportion=0)

        main_sizer.Add(icon_sizer, proportion=0, flag=wx.EXPAND, border=10)



        self.SetSizer(main_sizer)
        main_sizer.Fit(self)

    def goto_paradigm(self, event):
        """
        docstring
        """
        cur_notebook = self.parent
        btn = event.GetEventObject()
        cur_paradigm = btn.GetLabelText()
        if self.opened_paradigms.get(cur_paradigm):
            self.parent.SetSelection(self.opened_paradigms[cur_paradigm])
            return
        paradigm_page = CreateNewProject(cur_notebook, self.gui_size, btn.GetLabelText())
        cur_notebook.AddPage(paradigm_page, btn.GetLabelText(), select=True)
        self.opened_paradigms[cur_paradigm] = cur_notebook.GetPageCount() - 1


