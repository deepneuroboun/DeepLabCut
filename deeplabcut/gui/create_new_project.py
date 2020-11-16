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
import deeplabcut
from deeplabcut.gui import analysis_toolbox

deeplabcut_root = os.path.dirname(deeplabcut.__path__[0])
PARADIGM_PATH = os.path.join(deeplabcut_root, 'paradigms')
media_path = os.path.join(deeplabcut.__path__[0], 'gui' , 'media')
logo = os.path.join(media_path,'logo.png')
bounneuro_logo = os.path.join(media_path, 'bounneuro.png')

class CreateNewProject(wx.Panel):
    SCALE = 5
    def __init__(self, parent, gui_size, cur_paradigm):
        wx.Panel.__init__(self, parent)
        self.gui_size = gui_size
        self.parent = parent
        h=gui_size[0]
        w=gui_size[1]
        wx.Panel.__init__(self, parent, -1,style=wx.SUNKEN_BORDER,size=(h,w))
        # variable initilization
        self.videos_filelist = []
        self.data_filelist = []
        self.filelist = []
        self.dir = None
        self.copy = False
        self.config = os.path.join(PARADIGM_PATH, cur_paradigm, 'config.yaml')
        self.loaded = False
        self.cur_paradigm = cur_paradigm

        # design the panel
        self.sizer = wx.GridBagSizer(10, 15)

        text1 = wx.StaticText(self, label="DeepNeuroBoun\nLoad Videos or Tracking Data", style=wx.ALIGN_CENTRE)
        self.sizer.Add(text1, pos=(0, 0), flag=wx.TOP|wx.LEFT|wx.BOTTOM,border=15)

        # Add logo of DLC
        icon = wx.StaticBitmap(self, bitmap=wx.Bitmap(logo))
        self.sizer.Add(icon, pos=(0,2), flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT,border=5)

        # Add bounneuro logo
        boun_image = wx.Image(bounneuro_logo, type=wx.BITMAP_TYPE_PNG)
        boun = wx.StaticBitmap(self, bitmap=wx.Bitmap(boun_image.Scale(boun_image.GetWidth() // self.SCALE, boun_image.GetHeight() // self.SCALE, wx.IMAGE_QUALITY_HIGH)))
        self.sizer.Add(boun, pos=(5,2), flag=wx.BOTTOM|wx.RIGHT|wx.ALIGN_RIGHT,border=5)

        line = wx.StaticLine(self)
        self.sizer.Add(line, pos=(1, 0), span=(1, 3),flag=wx.EXPAND|wx.BOTTOM, border=10)

        # Add all the options

        self.vids_or_data = wx.StaticText(self, label="Choose videos or tracking data:")
        self.sizer.Add(self.vids_or_data, pos=(2, 0), flag=wx.TOP|wx.LEFT, border=10)

        self.sel_vids_or_data = wx.Button(self, label="Load")
        self.sizer.Add(self.sel_vids_or_data, pos=(2, 1), flag=wx.TOP, border=6)
        self.sel_vids_or_data.Bind(wx.EVT_BUTTON, self.select_videos_or_data)


#

        self.help_button = wx.Button(self, label='Help')
        self.sizer.Add(self.help_button, pos=(4, 0), flag=wx.LEFT, border=10)
        self.help_button.Bind(wx.EVT_BUTTON, self.help_function)

        self.ok = wx.Button(self, label="Ok")
        self.sizer.Add(self.ok, pos=(4, 2))
        self.ok.Bind(wx.EVT_BUTTON, self.analyze_file)


        self.reset = wx.Button(self, label="Reset")
        self.sizer.Add(self.reset, pos=(4, 1),flag=wx.BOTTOM|wx.RIGHT, border=10)
        self.reset.Bind(wx.EVT_BUTTON, self.reset_project)

        self.sizer.AddGrowableRow(2)
        self.sizer.AddGrowableRow(3)
        self.sizer.AddGrowableCol(1)

        self.SetSizer(self.sizer)
        self.sizer.Fit(self)

    def help_function(self,event):
        wx.MessageBox('Select either videos or tracking data.\n\nSupported video formats are mp4 and avi.\nSupported tracking data formats are csv and h5.\n\nIf you load videos, you will be directed to the video analysis screen.\nIf you load tracking data, you will be directed to the analysis toolbox.', 'Help', wx.OK | wx.ICON_INFORMATION)





    def select_videos_or_data(self,event):
        """
        Selects the videos or the tracking data from the directory
        """
        cwd = os.path.expanduser('~')
        dlg = wx.FileDialog(self, "Select videos or tracking data to add to the project", cwd, "", "*.*", wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.vids_or_data = dlg.GetPaths()
        self.filelist = self.filelist + self.vids_or_data
        video = not False in [point.lower().endswith(('.mp4','.avi')) for point in self.filelist] #may need to extend video types
        track = not False in [point.lower().endswith(('.h5','.csv')) for point in self.filelist]

        if video:
            if any(item in self.videos_filelist for item in self.filelist):
                wx.MessageBox('Already selected!', 'Error', wx.OK | wx.ICON_INFORMATION)
            else:
                self.videos_filelist += self.filelist
                self.sel_vids_or_data.SetLabel("Total %s Videos selected" %len(self.videos_filelist))
        elif track:
            if any(item in self.videos_filelist for item in self.filelist):
                wx.MessageBox('Already selected!', 'Error', wx.OK | wx.ICON_INFORMATION)
            else:
                self.data_filelist += self.filelist
                self.sel_vids_or_data.SetLabel("Total %s files of tracking data selected" %len(self.data_filelist))
        else:
            wx.MessageBox('Not supported', 'Error', wx.OK | wx.ICON_INFORMATION)
        
        if len(self.videos_filelist) > 0 and len(self.data_filelist) > 0:
            wx.MessageBox('Cannot choose both videos and data. Please only choose one type', 'Error', wx.OK | wx.ICON_INFORMATION)
            self.videos_filelist, self.data_filelist = [], []
            self.sel_vids_or_data.SetLabel("Load")
        self.filelist = []
        self.vids_or_data = None


    def select_working_dir(self,event):
        cwd = os.getcwd()
        dlg = wx.DirDialog(self, "Choose the directory where your project will be saved:",cwd, style = wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.dir = dlg.GetPath()

    def analyze_file(self,event):
        wx.MessageBox('Analysis', 'Info', wx.OK | wx.ICON_INFORMATION)
        cur_list = []
        if (self.data_filelist):
            cur_list = self.data_filelist
        if (self.videos_filelist):
            cur_list = self.videos_filelist
        analysis_toolbox.show(self.config, self.cur_paradigm, cur_list, wx.GetTopLevelParent(self))


    def reset_project(self,event):
        self.data_filelist = []
        self.videos_filelist = []
        self.sel_vids_or_data.SetLabel("Load")

