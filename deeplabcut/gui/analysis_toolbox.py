"""
DeepNeuroBoun Toolbox
© Behavioral Neuroscience Lab, Bogazici University
https://github.com/deepneuroboun/DeepLabCut

Licensed under GNU Lesser General Public License v3.0
"""

import os
import os.path
import glob
from pathlib import Path
import cv2
import wx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib
from deeplabcut.utils.auxiliaryfunctions import read_config
from deeplabcut.utils.plotting import plot_trajectories
from .matplotlib_cropper import Plot
from .paradigm_panel.panel import paradigm_selector

# ###########################################################################
# Class for GUI MainFrame
# ###########################################################################




class WidgetPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)

class MainFrame(wx.Frame):
    """Contains the main GUI and button boxes"""

    def __init__(self, parent, config, paradigm, filelist):
        # Settting the GUI size and panels design
        # Gets the number of displays
        displays = (wx.Display(i) for i in range(wx.Display.GetCount()))
        screenSizes = [display.GetGeometry().GetSize()
                       for display in displays]  # Gets the size of each display
        index = 0  # For display 1.
        screenWidth = screenSizes[index][0]
        screenHeight = screenSizes[index][1]
        self.gui_size = (screenWidth*0.7, screenHeight*0.85)

        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title='DeepNeuroBoun - Labeling ToolBox',
                          size=wx.Size(self.gui_size), pos=wx.DefaultPosition, style=wx.RESIZE_BORDER | wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText(
            "First, push the crop button and select the interested area with mouse...")

        # This sets the minimum size of the GUI. It can scale now!
        self.SetSizeHints(wx.Size(self.gui_size))
###################################################################################################################################################

# Spliting the frame into top and bottom panels. Bottom panels contains the widgets. The top panel is for showing images and plotting!

        topSplitter = wx.SplitterWindow(self)
        vSplitter = wx.SplitterWindow(topSplitter)

        # Load Images
        self.analysis_files, self.img_files = self._get_images_h5(filelist)
        self.img = mpimg.imread(self.img_files[0])
        self.img_size = self.img.shape
        self.cur_crop = (0, self.img_size[0], 0, self.img_size[1])
        # Dummy Part Finished
        self.image_panel = Plot(vSplitter, img=self.img)
        self.choice_panel = paradigm_selector(vSplitter, paradigm)
        vSplitter.SplitVertically(
            self.image_panel, self.choice_panel, sashPosition=self.gui_size[0]*0.8)
        vSplitter.SetSashGravity(1)
        self.widget_panel = WidgetPanel(topSplitter)
        topSplitter.SplitHorizontally(
            vSplitter, self.widget_panel, sashPosition=self.gui_size[1]*0.83)  # 0.9
        topSplitter.SetSashGravity(1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(topSplitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

###################################################################################################################################################
# Add Buttons to the WidgetPanel and bind them to their respective functions.

        widgetsizer = wx.WrapSizer(orient=wx.HORIZONTAL, flags=wx.EXPAND)

        # Buttons
        self.ok = wx.Button(self.widget_panel, id=wx.ID_ANY, label="OK")
        self.quit = wx.Button(self.widget_panel, id=wx.ID_ANY, label="Quit")
        self.crop = wx.Button(self.widget_panel, id=wx.ID_ANY, label="Crop")

        # Flags
        flags_all = wx.SizerFlags(1)
        flags_all.Border(wx.ALL, 10)

        # Alignment and Locations
        widgetsizer.Add(self.ok, flags_all)
        widgetsizer.Add(self.crop, flags_all)
        widgetsizer.AddStretchSpacer(10)
        widgetsizer.Add(self.quit, flags_all)

        # Function Binding
        self.quit.Bind(wx.EVT_BUTTON, self.quitButton)
        self.ok.Bind(wx.EVT_BUTTON, self.okButton)
        self.crop.Bind(wx.EVT_BUTTON, self.crop_button)

        self.widget_panel.SetSizer(widgetsizer)
        self.widget_panel.SetSizerAndFit(widgetsizer)
        self.widget_panel.Layout()

###############################################################################################################################
# Variables initialization
        self.currentDirectory = os.getcwd()
        self.index = []
        self.iter = []
        self.file = 0
        self.updatedCoords = []
        self.dataFrame = None
        self.config_file = config
        self.filelist = filelist
        self.new_labels = False
        self.drs = []
        self.view_locked = False
        self.crop_btn_change = 0
        self.paradigm = paradigm
        self.cfg = read_config(self.config_file, is_paradigm=True)
        self.choice_panel.addCheckButtons(
            self.paradigm, self.image_panel, self.img_size, self.cfg)
    
    def _get_images_h5(self, file_list):
        analysis_files = []
        img_files = []
        for cur_file in file_list:
            splitter = os.path.splitext(cur_file)
            name = splitter[0]
            cur_ext = splitter[1]
            if cur_ext == 'csv' or cur_ext == 'h5':
                analysis_files.append(cur_file)
            else:
               vidcap = cv2.VideoCapture(cur_file)
               _, img = vidcap.read()
               img_file_name = "%s.%s" % (name, "jpg")
               cv2.imwrite(img_file_name, img)
               img_files.append(img_file_name)
               vidcap.release()
        
        return analysis_files, img_files

               
        
        


###############################################################################################################################
# BUTTONS FUNCTIONS FOR HOTKEYS
    def okButton(self, event):
        res = plot_trajectories(
            self.config_file, self.filelist, self.cfg['options'], videotype='.MP4', crop=self.cur_crop)
        # plot_thread = Thread(target=plotting.plot_trajectories,
        #         args=(self.config_file, self.filelist, self.options),
        #         kwargs={'videotype': '.MP4'})
        # plot_thread.start()
        # dlg = AnalysisDialog()
        # dlg.ShowModal()
        wx.MessageBox(res, 'Info', wx.OK | wx.ICON_INFORMATION)

    def quitButton(self, event):
        """
        Asks user for its inputs and then quits the GUI
        """
        self.statusbar.SetStatusText("Qutting now!")

        self.Destroy()
        

    def crop_button(self, event):
        """
        docstring
        """
        labels = ["Crop", "Done"]
        self.crop_btn_change = 1 - self.crop_btn_change
        btn = event.GetEventObject()
        btn.SetLabel(labels[self.crop_btn_change])
        self.image_panel.set_active_rs(bool(self.crop_btn_change))
        if not bool(self.crop_btn_change):
            # x1, x2, y1, y2
            coords, self.img_size = self.image_panel.show_cropped_image()
            # Crop Parameters
            x1, x2, y1, y2 = self.cur_crop
            cx1, cx2, cy1, cy2 = coords
            x2, y2 = x1 + cx2, y1 + cy2
            x1, y1 = x1 + cx1, y1 + cy1
            self.cur_crop = (x1, x2, y1, y2)
            # needs generating patches for the new image
            self.choice_panel.generate_patches(self.img_size)




def show(config, paradigm, files=[], parent=None):
    frame = MainFrame(parent, config, paradigm, files).Show()
