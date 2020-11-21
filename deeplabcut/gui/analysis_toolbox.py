"""
DeepLabCut2.0 Toolbox (deeplabcut.org)
© A. & M. Mathis Labs
https://github.com/AlexEMG/DeepLabCut

Please see AUTHORS for contributors.
https://github.com/AlexEMG/DeepLabCut/blob/master/AUTHORS
Licensed under GNU Lesser General Public License v3.0
"""

import os
import os.path
import glob
from pathlib import Path
import cv2
import wx
import wx.lib.scrolledpanel as SP
import wx.lib.agw.floatspin as fs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
import matplotlib.colors as mcolors
import matplotlib.image as mpimg
import matplotlib
from deeplabcut.utils.auxiliaryfunctions import read_config
from deeplabcut.utils.plotting import plot_trajectories
from deeplabcut.gui.matplotlib_cropper import Plot

# ###########################################################################
# Class for GUI MainFrame
# ###########################################################################




class WidgetPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)


class ScrollPanel(SP.ScrolledPanel):
    def __init__(self, parent):
        SP.ScrolledPanel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.SetupScrolling(scroll_x=True, scroll_y=True, scrollToTop=False)
        self.Layout()

    def on_focus(self, event):
        pass

    def addCheckButtons(self, paradigm):
        """
        Adds radio buttons for each bodypart on the right panel
        """
        if paradigm == 'OFT':
            center_label = 'Center'
        if paradigm == 'MWM':
            center_label = 'Target'
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

        self.SetSizerAndFit(self.choiceBox)
        self.Layout()
        return(self.choiceBox, [self.quartile, self.center], self.scaler, self.re_center)

    def clearBoxer(self):
        self.choiceBox.Clear(True)


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
            "Looking for a folder to start analyzing. Click 'Load frame' to begin.")

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
        self.choice_panel = ScrollPanel(vSplitter)
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
        self.axes = self.image_panel.get_axes()
        self.figure = self.image_panel.figure
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


# Preview Image
        self.paradigm = paradigm
        self.previewImage()
    
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
            self.config_file, self.filelist, self.cfg['options'], videotype='.MP4')
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
            x1, y1 = x1 + cx1, y1 + cy1
            x2, y2 = x2 - cx2, y2 + cy2
            self.cur_crop = (x1, x2, y1, y2)
            # needs generating patches for the new image
            self.createCenter()
            self.createQuartile()

    def previewImage(self):
        """
        Show the DirDialog and ask the user to change the directory where machine labels are stored
        """
        self.statusbar.SetStatusText(
            "First, push the crop button and select the interested area with mouse...")
        cwd = os.path.join(os.getcwd())

# Reading config file and its variables
        self.cfg = read_config(self.config_file, is_paradigm=True)
        self.scorer = self.cfg['scorer']
        self.bodyparts = self.cfg['bodyparts']
        self.videos = self.cfg['video_sets'].keys()
        self.markerSize = self.cfg['dotsize']
        self.alpha = self.cfg['alphavalue']
        self.colormap = plt.get_cmap(self.cfg['colormap'])
        self.colormap = self.colormap.reversed()
        self.project_path = self.cfg['project_path']

# the first checkbox is for quartile and the second checkbox is the central analysis
# This the part in order to activate different paradigms (OFT, MWM)
        self.choiceBox, self.checkBoxes, self.Scaler, self.Recenter = self.choice_panel.addCheckButtons(self.paradigm)
        self.Scaler.Enable(False)
        self.Recenter.Enable(False)
        self.Bind(wx.EVT_CHECKBOX, self.isQuartile, self.checkBoxes[0])
        self.Bind(wx.EVT_CHECKBOX, self.isCentral, self.checkBoxes[1])
        self.Scaler.Bind(wx.EVT_SPINCTRL, self.updateCenter)
        self.Recenter.Bind(wx.EVT_BUTTON, self.resetcenter)
        self.createPatch()


    # Analysis Patches
    def createPatch(self):
        x, y, d = self.img_size
        # Since values are too generic it should be transformed into real values
        for analysis_type in self.cfg['options'].keys():
            for initial in self.cfg['options'][analysis_type].keys():
                self.cfg['options'][analysis_type][initial] = list(map(eval, self.cfg['options'][analysis_type][initial]))
        self.createQuartile()
        self.createCenter()

    def createCenter(self):

        x, y, d = self.img_size
        central_rect_y_len = eval(
            self.cfg['central_rect']['y_len']) * self.Scaler.GetValue()
        central_rect_x_len = eval(
            self.cfg['central_rect']['x_len']) * self.Scaler.GetValue()

        central_x, central_y = tuple(eval(self.cfg['central_rect']['start']))
        # Assumption : The maze center is at the center of the image
        central_rect_start = (central_x - central_rect_x_len / 2,
                              central_y - central_rect_y_len / 2)

        self.central_rect = patches.Rectangle(central_rect_start,
                                              central_rect_y_len,
                                              central_rect_x_len,
                                              fill=False, color='w', lw=4)
        cr = self.central_rect
        cr_vertices = cr.get_patch_transform().transform(cr.get_path().vertices[:-1])
        self.cfg['options']['center-based']['center'] = list(map(tuple, cr_vertices.tolist()))

    def createQuartile(self):

        x, y, d = self.img_size
        starting_points = list(map(eval, self.cfg['quadrants']['start']))
        quadrants_y_len = eval(self.cfg['quadrants']['y_len'])
        quadrants_x_len = eval(self.cfg['quadrants']['x_len'])
        quadrants = []
        for starting_point in starting_points:
            quadrants.append(patches.Rectangle(starting_point,
                                               quadrants_y_len,
                                               quadrants_x_len,
                                               fill=False, color='w', lw=4))
        self.rect = PatchCollection(quadrants, match_original=True)
        regions = self.cfg['options']['vector-based'].keys()
        # TODO: needs dynamic x and y positions for labels
        x = [150, 450, 450, 150]
        y = [150, 150, 450, 450]

        for region in zip(x,y,regions):
            x, y, label = region
            self.axes.text(x, y, label, fontsize=30, color='white')
        for text in self.axes.texts:
            text.set_visible(False)

    # Quartile Analysis showing to the plot

    def isQuartile(self, evt):
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

    # Center analysis showing to the plot

    def isCentral(self, evt):
        curBox = evt.GetEventObject()
        if(curBox.IsChecked()):
            self.axes.add_patch(self.central_rect)
            self.Scaler.Enable(True)
            self.Recenter.Enable(True)
        else:
            self.central_rect.remove()
            self.Scaler.Enable(False)
            self.Recenter.Enable(False)
        self.figure.canvas.draw()

    def updateCenter(self, event):
        self.central_rect.remove()
        self.createCenter()
        self.axes.add_patch(self.central_rect)
        self.figure.canvas.draw()

    def resetcenter(self, event):
        self.Scaler.SetToDefaultValue()
        self.central_rect.remove()
        self.createCenter()
        self.axes.add_patch(self.central_rect)
        self.figure.canvas.draw()


def show(config, paradigm, files=[], parent=None):
    frame = MainFrame(parent, config, paradigm, files).Show()
