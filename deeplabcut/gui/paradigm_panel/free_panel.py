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
        

        self.choiceBox = wx.BoxSizer(wx.VERTICAL)
        buttons = ["square","rectangle","circle","other"]
        for elem in buttons:
            setattr(self,elem,wx.Button(self,label = elem))
        self.square.Enable(False)
        self.choiceBox.Add(self.square, flag = wx.ALL, border = 10)
        self.rectangle.Enable(False)
        self.choiceBox.Add(self.rectangle, flag = wx.ALL, border = 10)
        self.circle.Enable(False)
        self.choiceBox.Add(self.circle, flag = wx.ALL, border = 10)
        self.other.Enable(False) 
        self.choiceBox.Add(self.other, flag = wx.ALL, border = 10)
      
        




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