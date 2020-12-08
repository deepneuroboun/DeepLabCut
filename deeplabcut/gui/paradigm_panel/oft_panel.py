import wx
import wx.lib.scrolledpanel as SP
import wx.lib.agw.floatspin as fs


class OFT(SP.ScrolledPanel):
    def __init__(self, parent):
        SP.ScrolledPanel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.SetupScrolling(scroll_x=True, scroll_y=True, scrollToTop=False)
        self.Layout()


    def addCheckButtons(self, paradigm, image_panel):
        """
        Adds radio buttons for each bodypart on the right panel
        """
        # This should be changed after demo
        if paradigm in ['OFT','EPM']: #TODO: temporary solution to make the code run. need something else for EPM
            center_label = 'Center'
        if paradigm == 'MWM':
            center_label = 'Target'
        # END CHANGE
        self.choiceBox = wx.BoxSizer(wx.VERTICAL)

        self.quartile = wx.CheckBox(self, id=wx.ID_ANY, label='Quartile')
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
        # Should be changed after demo
        if paradigm == 'MWM':
            self.target_rs = image_panel.add_rs()
            self.target_rs_on = 0
            self.target_crop_btn = wx.Button(self, id=wx.ID_ANY, label='Select Target')
            self.target_crop_btn.Bind(wx.EVT_BUTTON, self.target_crop)
            self.choiceBox.Add(self.target_crop_btn, 0, wx.ALL, 5)
        # END CHANGE


        self.SetSizerAndFit(self.choiceBox)
        self.Layout()
        return(self.choiceBox, [self.quartile, self.center], self.scaler, self.re_center)

    def clearBoxer(self):
        self.choiceBox.Clear(True)
    

    def target_crop(self, evt):
        labels = ['Select Target', 'Finish Target']
        btn = evt.GetEventObject()
        self.target_rs_on = 1 - self.target_rs_on
        btn.SetLabel(labels[self.target_rs_on])
        self.target_rs.set_active(bool(self.target_rs_on))
        if not bool(self.target_rs_on):
            main_frame = wx.GetTopLevelParent(self)
            