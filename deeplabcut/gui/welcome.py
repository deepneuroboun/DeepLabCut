"""
DeepLabCut2.0 Toolbox (deeplabcut.org)
© A. & M. Mathis Labs
https://github.com/AlexEMG/DeepLabCut
Please see AUTHORS for contributors.

https://github.com/AlexEMG/DeepLabCut/blob/master/AUTHORS
Licensed under GNU Lesser General Public License v3.0

"""

import wx
import wx.adv
import os
import deeplabcut

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

##         design the panel
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        #if editing this text make sure you add the '\n' to get the new line. The sizer is unable to format lines correctly.
        description = "Allah belanizi versin cocuklar!\nBaciniz yok!!!\nBakalim istedigimiz sekilde mi oldu???"

        self.proj_name = wx.StaticText(self, label=description,style=wx.ALIGN_CENTRE)
        main_sizer.Add(self.proj_name, proportion=1, flag=wx.EXPAND, border=10)



        # Add image of DLC
        icon_sizer = wx.BoxSizer(wx.HORIZONTAL)
        icon_image = wx.Image(dlc, type=wx.BITMAP_TYPE_PNG)
        boun_image = wx.Image(bounneuro, type=wx.BITMAP_TYPE_PNG)

        icon = wx.StaticBitmap(self, bitmap=wx.Bitmap(icon_image.Scale(icon_image.GetWidth() // self.SCALE, icon_image.GetHeight() // self.SCALE, wx.IMAGE_QUALITY_HIGH)))
        boun = wx.StaticBitmap(self, bitmap=wx.Bitmap(boun_image.Scale(boun_image.GetWidth() // self.SCALE, boun_image.GetHeight() // self.SCALE, wx.IMAGE_QUALITY_HIGH)))

        icon_sizer.Add(boun, proportion=1, flag=wx.EXPAND)
        icon_sizer.Add(icon, proportion=0, flag=wx.ALIGN_RIGHT | wx.EXPAND)

        main_sizer.Add(icon_sizer, proportion=0, flag=wx.EXPAND, border=10)





        self.SetSizer(main_sizer)
        main_sizer.Fit(self)


