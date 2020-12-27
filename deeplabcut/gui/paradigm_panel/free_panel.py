import wx
import wx.lib.scrolledpanel as SP
import wx.lib.agw.floatspin as fs
from matplotlib.collections import PatchCollection
import matplotlib.patches as patches


class Free(SP.ScrolledPanel):
    def __init__(self, parent):
        SP.ScrolledPanel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.SetupScrolling(scroll_x=True, scroll_y=True, scrollToTop=False)
        self.Layout()


    def addCheckButtons(self, paradigm, image_panel, img_size, cfg):
        """
        Adds buttons for Free Selection
        """
        self.axes = image_panel.get_axes()
        self.figure = image_panel.figure
        self.img_size = img_size
        self.cfg = cfg
        self.user_regions = {}
        

        self.choiceBox = wx.BoxSizer(wx.VERTICAL)
        buttons = ["Rectangle","Ellipse","Other"]
        for elem in buttons:
            setattr(self,elem,wx.Button(self,label = elem))
        self.roi_txt = wx.StaticText(self, label ="Pick Region Type")
        self.choiceBox.Add(self.roi_txt, flag = wx.ALL, border = 10)
        self.Rectangle.Enable(False)
        self.choiceBox.Add(self.Rectangle, flag = wx.ALL, border = 10)
        self.Ellipse.Enable(False)
        self.choiceBox.Add(self.Ellipse, flag = wx.ALL, border = 10)
        self.Other.Enable(False) 
        self.choiceBox.Add(self.Other, flag = wx.ALL, border = 10)
        self.roi_done = wx.Button(self, label = 'Done')
        self.choiceBox.Add(self.roi_done, flag = wx.ALL, border = 10)
        self.roi_done.Enable(False)

        self.choiceBox.AddStretchSpacer(3)
        self.all_roi_list = wx.StaticText(self, label = "Selected Custom Regions")
        self.choiceBox.Add(self.all_roi_list, flag = wx.ALL, border = 10)
        self.regions = wx.ComboBox(self,wx.ID_ANY,choices = [], style=wx.CB_DROPDOWN | wx.CB_DROPDOWN)
        self.choiceBox.Add(self.regions, flag = wx.ALL, border = 10)
        self.remove_roi = wx.Button(self, label = "Remove Region")
        self.remove_roi.Enable(False)
        self.choiceBox.Add(self.remove_roi, flag = wx.ALL, border = 10)

        self.choiceBox.AddStretchSpacer(3)
        self.analysis_text = wx.StaticText(self, label = "Analyses")
        self.choiceBox.Add(self.analysis_text, flag = wx.ALL, border = 10)
        self.regioncheck = wx.CheckBox(self, label = "Region")
        self.choiceBox.Add(self.regioncheck, flag = wx.ALL, border = 10)
        self.speedcheck = wx.CheckBox(self, label = "Speed")
        self.choiceBox.Add(self.speedcheck, flag = wx.ALL, border = 10)
        self.positioncheck = wx.CheckBox(self, label = "Position")
        self.choiceBox.Add(self.positioncheck, flag = wx.ALL, border = 10)


        self.SetSizerAndFit(self.choiceBox)
        self.Layout()

        self.create_patch()
    

    
    
    def target_crop(self, evt):
        labels = ['Select Target', 'Finish Target']
        btn = evt.GetEventObject()
        self.target_rs_on = 1 - self.target_rs_on
        btn.SetLabel(labels[self.target_rs_on])
        self.target_rs.set_active(bool(self.target_rs_on))
        if not bool(self.target_rs_on):
            main_frame = wx.GetTopLevelParent(self)
    
    def generate_patches(self, img_size):
        self.img_size = img_size

    

    def create_patch(self):
        x, y, d = self.img_size
        # Since values are too generic it should be transformed into real values
        self.generate_patches(self.img_size)
    
    def help(self,event):
        wx.MessageBox("Here you can define custom regions and choose some default analyses. \n\n"\
            "If you are defining a rectangle, you need to hold and drag over the region you want to define.\n"\
            "Pressing shift while drawing a rectangle gives a square.\n\n"\
            "If you are defining an ellipse, you need to hold and drag over the region you want to define.\n"\
            "Pressing shift while drawing an ellipse gives a circle.\n\n"\
            "If you choose the other option, you can define a custom polygon by clicking on the where you want the vertices to be.\n"\
            "You need to connect the last vertex point to the first one.\n\n"\
            "You can restart drawing after pressing esc. "\
            "After drawing the region, you can move it around. "\
            "To move the custom polygon around you need to press shift and hold.\n\n"\
            "If you want to delete a region after naming it, select it under Custom Selected Regions, and click on Remove Region.",'Info', wx.OK | wx.ICON_INFORMATION)