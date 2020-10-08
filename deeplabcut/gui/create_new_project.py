"""
DeepLabCut2.0 Toolbox (deeplabcut.org)
© A. & M. Mathis Labs
https://github.com/AlexEMG/DeepLabCut
Please see AUTHORS for contributors.

https://github.com/AlexEMG/DeepLabCut/blob/master/AUTHORS
Licensed under GNU Lesser General Public License v3.0

"""

import wx
import os,sys,pydoc,platform
import deeplabcut
import sys
from deeplabcut.gui import analysis_toolbox

deeplabcut_root = os.path.dirname(deeplabcut.__path__[0])
PARADIGM_PATH = os.path.join(deeplabcut_root, 'paradigms')
media_path = os.path.join(deeplabcut.__path__[0], 'gui' , 'media')
logo = os.path.join(media_path,'logo.png')

class CreateNewProject(wx.Panel):
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
        self.dir = None
        self.copy = False
        self.config = os.path.join(PARADIGM_PATH, cur_paradigm, 'config.yaml')
        self.loaded = False

        # design the panel
        self.sizer = wx.GridBagSizer(10, 15)

        text1 = wx.StaticText(self, label="DeepNeuroBoun\nSimple Step\nAnalyze Videos", style=wx.ALIGN_CENTRE)
        self.sizer.Add(text1, pos=(0, 0), flag=wx.TOP|wx.LEFT|wx.BOTTOM,border=15)

        # Add logo of DLC
        icon = wx.StaticBitmap(self, bitmap=wx.Bitmap(logo))
        self.sizer.Add(icon, pos=(0,2), flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT,border=5)

        line = wx.StaticLine(self)
        self.sizer.Add(line, pos=(1, 0), span=(1, 3),flag=wx.EXPAND|wx.BOTTOM, border=10)

        # Add all the options

        self.vids = wx.StaticText(self, label="Choose the videos:")
        self.sizer.Add(self.vids, pos=(2, 0), flag=wx.TOP|wx.LEFT, border=10)

        self.sel_vids = wx.Button(self, label="Load Videos")
        self.sizer.Add(self.sel_vids, pos=(2, 1), flag=wx.TOP, border=6)
        self.sel_vids.Bind(wx.EVT_BUTTON, self.select_videos)

        self.data = wx.StaticText(self, label="Choose the track data:")
        self.sizer.Add(self.data, pos=(3,0), flag=wx.TOP|wx.LEFT, border=10)

        self.sel_data = wx.Button(self, label="Load Data")
        self.sizer.Add(self.sel_data, pos=(3,1), flag=wx.TOP, border=6)
        self.sel_data.Bind(wx.EVT_BUTTON, self.select_data)

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
        # TODO: change help function for DeepNeuroBoun
        raise NotImplementedError



    def select_data(self,event):
        """
        Selects the data from the directory
        """
        cwd = os.getcwd() # current working directory is the one deeplapcut runs
        dlg = wx.FileDialog(self, "Select data to add to the project", cwd, "", "*.*", wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.data = dlg.GetPaths()
            self.data_filelist = self.data_filelist + self.data
            self.sel_data.SetLabel("Total %s Data selected" %len(self.data_filelist))

    def select_videos(self,event):
        """
        Selects the videos from the directory
        """
        cwd = os.getcwd()
        dlg = wx.FileDialog(self, "Select videos to add to the project", cwd, "", "*.*", wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.vids = dlg.GetPaths()
            self.videos_filelist = self.videos_filelist + self.vids
            self.sel_vids.SetLabel("Total %s Videos selected" %len(self.videos_filelist))

    def activate_change_wd(self,event):
        """
        Activates the option to change the working directory
        """
        self.change_wd = event.GetEventObject()
        if self.change_wd.GetValue() == True:
            self.sel_wd.Enable(True)
        else:
            self.sel_wd.Enable(False)

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
        analysis_toolbox.show(self.config, cur_list)


    def reset_project(self,event):
        # TODO : Resetting makes the videos disappear and reload all the stuff
        raise NotImplementedError

