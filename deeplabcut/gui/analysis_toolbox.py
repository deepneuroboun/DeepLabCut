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
import matplotlib.image as mpimg
import matplotlib
from deeplabcut.utils.auxiliaryfunctions import read_config
from deeplabcut.utils.plotting import plot_trajectories
from .matplotlib_cropper import Plot
from .paradigm_panel.panel import paradigm_selector
import math

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
        self.paradigm = paradigm
        self.show_p = []

###################################################################################################################################################
# Add Buttons to the WidgetPanel and bind them to their respective functions.

        widgetsizer = wx.WrapSizer(orient=wx.HORIZONTAL, flags=wx.EXPAND)

        # Buttons
        self.ok = wx.Button(self.widget_panel, id=wx.ID_ANY, label="Analyse")
        self.quit = wx.Button(self.widget_panel, id=wx.ID_ANY, label="Quit")
        self.crop = wx.Button(self.widget_panel, id=wx.ID_ANY, label="Crop")
        self.region = wx.Button(self.widget_panel, id= wx.ID_ANY, label = "Define New Region")
        self.help = wx.Button(self.widget_panel, id = wx.ID_ANY, label = "Help")
        self.px2cm = wx.Button(self.widget_panel, id = wx.ID_ANY, label = "Pixel to Cm Conversion") 
        self.ratiotxt = wx.StaticText(self.widget_panel, label ="")       
    
        # Flags
        flags_all = wx.SizerFlags(1)
        flags_all.Border(wx.ALL, 10)

        # Alignment and Locations
        widgetsizer.Add(self.help, flags_all)
        widgetsizer.Add(self.crop, flags_all)
        widgetsizer.Add(self.region,flags_all)
        widgetsizer.Add(self.px2cm, flags_all)
        widgetsizer.Add(self.ratiotxt, flags_all)
        widgetsizer.AddStretchSpacer(10)
        widgetsizer.Add(self.ok, flags_all)
        widgetsizer.Add(self.quit, flags_all)
        # Function Binding
        self.quit.Bind(wx.EVT_BUTTON, self.quitButton)
        self.ok.Bind(wx.EVT_BUTTON, self.okButton)
        self.crop.Bind(wx.EVT_BUTTON, self.crop_button)
        self.region.Bind(wx.EVT_BUTTON, self.which_region)
        self.px2cm.Bind(wx.EVT_BUTTON, self.get_ratio)
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
        self.redefine = False
        self.crop_btn_change = 0
        self.paradigm = paradigm
        self.coords = []
        self.cfg = read_config(self.config_file, is_paradigm=True)
        self.choice_panel.addCheckButtons(
            self.paradigm, self.image_panel, self.img_size, self.cfg)

        self.choice_panel.Rectangle.Bind(wx.EVT_BUTTON, self.select_polygon)
        self.choice_panel.Ellipse.Bind(wx.EVT_BUTTON, self.select_polygon)
        self.choice_panel.Other.Bind(wx.EVT_BUTTON, self.select_polygon)
        self.choice_panel.roi_done.Bind(wx.EVT_BUTTON, self.accept_ROI)
        self.choice_panel.remove_roi.Bind(wx.EVT_BUTTON, self.delete_region)
        self.choice_panel.regions.Bind(wx.EVT_COMBOBOX, self.show_region_choice) 
        self.help.Bind(wx.EVT_BUTTON, self.choice_panel.help)


        self.choice_panel.Layout()

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
            self.config_file, self.filelist, self.cfg['options'], videotype='.MP4', crop=self.cur_crop, ratio = self.ratio)
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
    
    def which_region(self,event):
        
        """ Enables polygon buttons for user selection"""

        self.choice_panel.Rectangle.Enable(True)
        self.choice_panel.Ellipse.Enable(True)
        self.choice_panel.Other.Enable(True)
        self.StatusBar.SetStatusText("Please select which polygon you want to use for region selection.")
    
    def select_polygon(self,event):

        """ Allows user to draw/drag on the canvas depending on the polygon they picked."""

        self.image_panel.current_pol = event.GetEventObject().GetLabelText()
        self.choice_panel.Rectangle.Enable(False)
        self.choice_panel.Ellipse.Enable(False)
        self.choice_panel.Other.Enable(False)
        self.StatusBar.SetStatusText("Now pick the vertices")
        self.region_draw(self.image_panel.current_pol)
    
    def region_draw(self,current_pol):

        """ Draws the picked region"""

        if self.image_panel.current_pol == "Other":
            self.image_panel.poly_start_select()
        elif self.image_panel.current_pol == "Rectangle":
            self.image_panel.rect_start_select()
        elif self.image_panel.current_pol == "Ellipse":
            self.image_panel.ellipse_start_select()
        

        self.choice_panel.roi_done.Enable(True)
    
    def accept_ROI(self,event):

        """Asks user to name the region, and adds it to the analysis list"""

        keep_asking = True
        while keep_asking:
            self.roi_input = wx.TextEntryDialog(self, 'Please enter the region name:',"ROI","", 
                    style=wx.OK)
            
            self.roi_input.ShowModal()
            if self.roi_input.GetValue() in self.choice_panel.user_regions:
                wx.MessageBox(self,'That name is used! Please pick another name', 'Error', wx.OK | wx.ICON_INFORMATION)
            else:
                keep_asking = False
        
        self.choice_panel.user_regions[self.roi_input.GetValue()] = self.image_panel.cur_vertices
        self.image_panel.cur_region_name = self.roi_input.GetValue()
        self.choice_panel.regions.Append(self.roi_input.GetValue())
        self.choice_panel.remove_roi.Enable(True)
        self.roi_input.Destroy()
        self.choice_panel.Rectangle.Enable(False)
        self.choice_panel.Ellipse.Enable(False)
        self.choice_panel.Other.Enable(False)
        self.choice_panel.roi_done.Enable(False)

        self.image_panel.draw_ROI(self.image_panel.cur_vertices,self.image_panel.cur_region_name)
    
    def delete_region(self,event):

        msg = wx.MessageDialog(None,"Are you sure you want to delete {}".format(self.choice_panel.regions.GetValue()), "Remove Region?",wx.YES_NO | wx.ICON_WARNING)
        
        if msg.ShowModal() == wx.ID_YES:

            self.choice_panel.user_regions.pop(self.choice_panel.regions.GetValue())
            to_rm =self.image_panel.customregionplots.get(self.choice_panel.regions.GetValue()).pop(0)
            to_rm.remove()
            self.image_panel.customregionplots.pop(self.choice_panel.regions.GetValue())
            self.image_panel.canvas.draw_idle()
            self.choice_panel.regions.Delete(self.choice_panel.regions.GetSelection())
            self.choice_panel.regions.SetValue("")
        
        if self.choice_panel.regions.GetItems() == []:

            self.choice_panel.remove_roi.Enable(False)
    
    def show_region_choice(self,event):
        try:
            self.tmp_plot.set_color('w')
        except:
            pass
        self.tmp_plot, = (self.image_panel.customregionplots.get(self.choice_panel.regions.GetValue()))
        self.tmp_plot.set_color('r')
        self.image_panel.canvas.draw_idle()
    
    def ask_cm_and_compute(self,event):

        ix,iy = event.xdata, event.ydata

        self.coords.append([ix,iy])

        self.show_p.append(self.image_panel._axes.plot(ix,iy,'ro'))
        self.image_panel.canvas.draw()

        if len(self.coords) == 2:

            keep_asking = True
            self.image_panel.canvas.mpl_disconnect(self.cid)
            
            while keep_asking:
                cm_dlg = wx.TextEntryDialog(self,"Please enter the distance between points in cm","Enter Distance",style=wx.OK)
                cm_dlg.ShowModal()

                try:
                    self.cm = int(cm_dlg.GetValue())

                    if self.cm >0:
                        keep_asking = False
                    else:
                        wx.MessageBox("Please enter a number bigger than zero","Error", wx.OK | wx.ICON_INFORMATION)
                except:
                    wx.MessageBox('Please enter a number', 'Error', wx.OK | wx.ICON_INFORMATION)
                
            cm_dlg.Destroy()
            self.ratio = self.cm/(math.sqrt(abs(((self.coords[0][0] - self.coords[1][0]) ** 2) + ((self.coords[0][1] - self.coords[1][1]) ** 2))))
            self.px2cm.SetLabel("Redefine the Ratio")
            self.redefine = True
            self.ratiotxt.SetLabel("Cm to Pixel Ratio is {}".format(self.ratio))
            for item in self.show_p:
                item[0].remove()
            self.show_p.clear()
            self.image_panel.canvas.draw_idle()


        
    def get_ratio(self,event):

        if self.redefine:

            self.coords.clear()
            self.redefine = False

        self.cid = self.image_panel.canvas.mpl_connect('button_press_event',self.ask_cm_and_compute)
        
        
        


        



def show(config, paradigm, files=[], parent=None):
    frame = MainFrame(parent, config, paradigm, files).Show()
