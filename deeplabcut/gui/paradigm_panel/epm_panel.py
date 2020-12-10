import wx
import wx.lib.scrolledpanel as SP
import wx.lib.agw.floatspin as fs
from matplotlib.collections import PatchCollection
import matplotlib.patches as patches


class EPM(SP.ScrolledPanel):
    def __init__(self, parent):
        SP.ScrolledPanel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.SetupScrolling(scroll_x=True, scroll_y=True, scrollToTop=False)
        self.Layout()


    def addCheckButtons(self, paradigm, image_panel, img_size, cfg):
        """
        Adds buttons for OFT paradigm
        """
        self.axes = image_panel.get_axes()
        self.figure = image_panel.figure
        self.img_size = img_size
        self.cfg = cfg
        # This should be changed after demo
        center_label = 'Center'
        self.choiceBox = wx.BoxSizer(wx.VERTICAL)

        self.quartile = wx.CheckBox(self, id=wx.ID_ANY, label='Arms')
        self.center = wx.CheckBox(self, id=wx.ID_ANY, label=center_label)
        self.scaler = fs.FloatSpin(self, -1, size=(250, -1), value=1, min_val=0.3, max_val=1.5,
                                   digits=2, increment=0.05, style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        scaler_text = wx.StaticText(self, label="Adjust the " + center_label + " size")
        self.re_center = wx.Button(
            self, id=wx.ID_ANY, label="Reset " + center_label + " to default")
        self.choiceBox.Add(self.quartile, 0, wx.ALL, 5)
        self.choiceBox.Add(self.center, 0, wx.ALL, 5)
        self.choiceBox.Add(scaler_text, 0, wx.ALL, 5)
        self.choiceBox.Add(self.scaler, 0, wx.ALL, 5)
        self.choiceBox.Add(self.re_center, 0, wx.ALL, 5)


        self.SetSizerAndFit(self.choiceBox)
        self.Layout()

        self.scaler.Enable(False)
        self.re_center.Enable(False)

        self.Bind(wx.EVT_CHECKBOX, self.is_quartile, self.quartile)
        self.Bind(wx.EVT_CHECKBOX, self.is_central, self.center)
        self.scaler.Bind(wx.EVT_SPINCTRL, self.update_center)
        self.re_center.Bind(wx.EVT_BUTTON, self.reset_center)
        

        self.create_patch()


    def clearBoxer(self):
        self.choiceBox.Clear(True)
    

    
    def generate_patches(self, img_size):
        self.img_size = img_size
        self.create_quartile()
        self.create_center()
    

    def create_quartile(self):
        x, y, d = self.img_size
        starting_points = list(map(eval, self.cfg['quadrants']['start']))
        quadrants_y_len = list(map(eval, self.cfg['quadrants']['y_len']))
        quadrants_x_len = list(map(eval, self.cfg['quadrants']['x_len']))
        quadrants = []
        for i in range(len(starting_points)):
            quadrants.append(patches.Rectangle(starting_points[i],
                                               quadrants_y_len[i],
                                               quadrants_x_len[i],
                                               fill=False, color='w', lw=4))
        self.rect = PatchCollection(quadrants, match_original=True)
        regions = self.cfg['options']['vector-based'].keys()
        

    def create_center(self):
        x, y, d = self.img_size
        central_rect_y_len = eval(
            self.cfg['central_rect']['y_len']) * self.scaler.GetValue()
        central_rect_x_len = eval(
            self.cfg['central_rect']['x_len']) * self.scaler.GetValue()

        central_x, central_y = tuple(eval(self.cfg['central_rect']['start']))
        # Assumption : The maze center is at the center of the image
        central_rect_start = (central_y - central_rect_y_len / 2,
                              central_x - central_rect_x_len / 2)

        self.central_rect = patches.Rectangle(central_rect_start,
                                              central_rect_y_len,
                                              central_rect_x_len,
                                              fill=False, color='w', lw=4)
        cr = self.central_rect
        cr_vertices = cr.get_patch_transform().transform(cr.get_path().vertices[:-1])
        self.cfg['options']['center-based']['center'] = list(map(tuple, cr_vertices.tolist()))
    

    def create_patch(self):
        x, y, d = self.img_size
        # Since values are too generic it should be transformed into real values
        for analysis_type in self.cfg['options'].keys():
            for initial in self.cfg['options'][analysis_type].keys():
                self.cfg['options'][analysis_type][initial] = list(map(eval, self.cfg['options'][analysis_type][initial]))
        self.generate_patches(self.img_size)
    
    
        
    def is_quartile(self, evt):
        """
        Quartile Analsis
        """
        curBox = evt.GetEventObject()
        if(curBox.IsChecked()):
            self.axes.add_collection(self.rect)
            for text in self.axes.texts:
                text.set_visible(True)
        else:
            self.rect.remove()
            for text in self.axes.texts:
                text.set_visible(False)
        self.figure.canvas.draw()
    

    def is_central(self, evt):
        """
        Center analysis
        """
        curBox = evt.GetEventObject()
        if(curBox.IsChecked()):
            self.axes.add_patch(self.central_rect)
            self.scaler.Enable(True)
            self.re_center.Enable(True)
        else:
            self.central_rect.remove()
            self.scaler.Enable(False)
            self.re_center.Enable(False)
        self.figure.canvas.draw()
    
    
    def update_center(self, event):
        self.central_rect.remove()
        self.create_center()
        self.axes.add_patch(self.central_rect)
        self.figure.canvas.draw()

    def reset_center(self, event):
        self.scaler.SetToDefaultValue()
        self.central_rect.remove()
        self.create_center()
        self.axes.add_patch(self.central_rect)
        self.figure.canvas.draw()

