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
import cv2
import wx
import wx.lib.scrolledpanel as SP
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
import matplotlib.colors as mcolors
import matplotlib
from mpl_toolkits.axes_grid1 import make_axes_locatable
from pathlib import Path
import argparse
from deeplabcut.generate_training_dataset import auxfun_drag_label
from deeplabcut.utils import auxiliaryfunctions
from deeplabcut.utils import plotting
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
from deeplabcut.gui.AnalysisDialog import AnalysisDialog
from threading import Thread

# ###########################################################################
# Class for GUI MainFrame
# ###########################################################################
class ImagePanel(wx.Panel):

    def __init__(self, parent,config,gui_size,**kwargs):
        h=gui_size[0]/2
        w=gui_size[1]/3
        wx.Panel.__init__(self, parent, -1,style=wx.SUNKEN_BORDER,size=(h,w))

        self.figure = matplotlib.figure.Figure()
        self.axes = self.figure.add_subplot(1, 1, 1)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.orig_xlim = None
        self.orig_ylim = None
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()

    def getfigure(self):
        return(self.figure)

    def drawplot(self,img,img_name,itr,index,bodyparts,cmap,keep_view=False):
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()
        self.axes.clear()

        # convert the image to RGB as you are showing the image with matplotlib
        im = cv2.imread(img)[...,::-1]
        ax = self.axes.imshow(im,cmap=cmap)
        self.orig_xlim = self.axes.get_xlim()
        self.orig_ylim = self.axes.get_ylim()
        divider = make_axes_locatable(self.axes)
        colorIndex = np.linspace(np.min(im),np.max(im),len(bodyparts))
        cax = divider.append_axes("right", size="5%", pad=0.05)
        cbar = self.figure.colorbar(ax, cax=cax,spacing='proportional', ticks=colorIndex)
        cbar.set_ticklabels(bodyparts[::-1])
        if keep_view:
            self.axes.set_xlim(xlim)
            self.axes.set_ylim(ylim)
        self.toolbar = NavigationToolbar(self.canvas)
        return(self.figure,self.axes,self.canvas,self.toolbar)

    def resetView(self):
        self.axes.set_xlim(self.orig_xlim)
        self.axes.set_ylim(self.orig_ylim)

    def getColorIndices(self,img,bodyparts):
        """
        Returns the colormaps ticks and . The order of ticks labels is reversed.
        """
        im = cv2.imread(img)
        norm = mcolors.Normalize(vmin=0, vmax=np.max(im))
        ticks = np.linspace(0,np.max(im),len(bodyparts))[::-1]
        return norm, ticks, im.shape



class WidgetPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1,style=wx.SUNKEN_BORDER)


class ScrollPanel(SP.ScrolledPanel):
    def __init__(self, parent):
        SP.ScrolledPanel.__init__(self, parent, -1,style=wx.SUNKEN_BORDER)
        self.SetupScrolling(scroll_x=True, scroll_y=True, scrollToTop=False)
        self.Layout()
    def on_focus(self,event):
        pass

    def addCheckButtons(self,bodyparts,fileIndex,markersize):
        """
        Adds radio buttons for each bodypart on the right panel
        """
        self.choiceBox = wx.BoxSizer(wx.VERTICAL)

        self.quartile = wx.CheckBox(self, id=wx.ID_ANY, label = 'Quartile')
        self.center = wx.CheckBox(self, id=wx.ID_ANY, label = 'Center')

        self.choiceBox.Add(self.quartile, 0, wx.ALL, 5 )
        self.choiceBox.Add(self.center, 0, wx.ALL, 5)

        self.SetSizerAndFit(self.choiceBox)
        self.Layout()
        return(self.choiceBox,[self.quartile, self.center])

    def clearBoxer(self):
        self.choiceBox.Clear(True)

class MainFrame(wx.Frame):
    """Contains the main GUI and button boxes"""

    def __init__(self, parent, config, filelist):
# Settting the GUI size and panels design
        displays = (wx.Display(i) for i in range(wx.Display.GetCount())) # Gets the number of displays
        screenSizes = [display.GetGeometry().GetSize() for display in displays] # Gets the size of each display
        index = 0 # For display 1.
        screenWidth = screenSizes[index][0]
        screenHeight = screenSizes[index][1]
        self.gui_size = (screenWidth*0.7,screenHeight*0.85)

        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = 'DeepNeuroBoun - Labeling ToolBox',
                            size = wx.Size(self.gui_size), pos = wx.DefaultPosition, style = wx.RESIZE_BORDER|wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText("Looking for a folder to start analyzing. Click 'Load frame' to begin.")

        self.SetSizeHints(wx.Size(self.gui_size)) #  This sets the minimum size of the GUI. It can scale now!
###################################################################################################################################################

# Spliting the frame into top and bottom panels. Bottom panels contains the widgets. The top panel is for showing images and plotting!

        topSplitter = wx.SplitterWindow(self)
        vSplitter = wx.SplitterWindow(topSplitter)

        self.image_panel = ImagePanel(vSplitter, config,self.gui_size)
        self.choice_panel = ScrollPanel(vSplitter)
        vSplitter.SplitVertically(self.image_panel,self.choice_panel, sashPosition=self.gui_size[0]*0.8)
        vSplitter.SetSashGravity(1)
        self.widget_panel = WidgetPanel(topSplitter)
        topSplitter.SplitHorizontally(vSplitter, self.widget_panel,sashPosition=self.gui_size[1]*0.83)#0.9
        topSplitter.SetSashGravity(1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(topSplitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

###################################################################################################################################################
# Add Buttons to the WidgetPanel and bind them to their respective functions.

        widgetsizer = wx.WrapSizer(orient=wx.HORIZONTAL, flags=wx.EXPAND)


        widgetsizer.AddStretchSpacer(15)
        self.ok = wx.Button(self.widget_panel, id=wx.ID_ANY, label="OK")
        self.quit = wx.Button(self.widget_panel, id=wx.ID_ANY, label="Quit")

        widgetsizer.Add(self.ok, 1, wx.ALL|wx.ALIGN_LEFT|wx.EXPAND, 15)
        widgetsizer.Add(self.quit , 1, wx.ALL|wx.EXPAND, 15)

        self.quit.Bind(wx.EVT_BUTTON, self.quitButton)
        self.ok.Bind(wx.EVT_BUTTON, self.okButton)

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
        self.buttonCounter = []
        self.bodyparts2plot = []
        self.drs = []
        self.num = []
        self.view_locked=False
        # Workaround for MAC - xlim and ylim changed events seem to be triggered too often so need to make sure that the
        # xlim and ylim have actually changed before turning zoom off
        self.prezoom_xlim=[]
        self.prezoom_ylim=[]

# TODO: correct hardcoded part
        self.labeled_data_path = 'labeled-data/MAH00131_shortened'

# Preview Image
        self.previewImage()

###############################################################################################################################
# BUTTONS FUNCTIONS FOR HOTKEYS
    def okButton(self, event):
        plot_thread = Thread(target=plotting.plot_trajectories, 
                args=(self.config_file, self.filelist, self.options), 
                kwargs={'videotype': '.MP4'})
        plot_thread.start()
        dlg = AnalysisDialog()
        dlg.ShowModal()
        wx.MessageBox(True, 'Info', wx.OK | wx.ICON_INFORMATION)



    def quitButton(self, event):
        """
        Asks user for its inputs and then quits the GUI
        """
        self.statusbar.SetStatusText("Qutting now!")

        self.Destroy()




    def previewImage(self):
        """
        Show the DirDialog and ask the user to change the directory where machine labels are stored
        """
        self.statusbar.SetStatusText("Looking for a folder to start labeling...")
        cwd = os.path.join(os.getcwd())

# Reading config file and its variables
        self.cfg = auxiliaryfunctions.read_config(self.config_file, is_paradigm=True)
        self.scorer = self.cfg['scorer']
        self.bodyparts = self.cfg['bodyparts']
        self.videos = self.cfg['video_sets'].keys()
        self.markerSize = self.cfg['dotsize']
        self.alpha = self.cfg['alphavalue']
        self.colormap = plt.get_cmap(self.cfg['colormap'])
        self.colormap = self.colormap.reversed()
        self.project_path=self.cfg['project_path']
        self.dir = os.path.join(self.project_path, self.labeled_data_path)
        self.index =np.sort([fn for fn in glob.glob(os.path.join(self.dir,'*.png')) if ('labeled.png' not in fn)])
        self.statusbar.SetStatusText('Working on folder: {}'.format(os.path.split(str(self.dir))[-1]))
        self.relativeimagenames=['labeled'+n.split('labeled')[1] for n in self.index]#[n.split(self.project_path+'/')[1] for n in self.index]

# Reading the existing dataset,if already present
        self.dataFrame = pd.read_hdf(os.path.join(self.dir,'CollectedData_'+self.scorer+'.h5'),'df_with_missing')
        self.dataFrame.sort_index(inplace=True)

# Finds the first empty row in the dataframe and sets the iteration to that index
        for idx,j in enumerate(self.dataFrame.index):
            values = self.dataFrame.loc[j,:].values
            if np.prod(np.isnan(values)) == 1:
                self.iter = idx
                break
            else:
                self.iter = 0


# Reading the image name
        self.img = self.index[self.iter]
        img_name = Path(self.index[self.iter]).name
        self.norm,self.colorIndex, img_size = self.image_panel.getColorIndices(self.img,self.bodyparts)
        # In order to show the borders to the user for analysis
        self.createPatch(img_size)

# checks for unique bodyparts
        if len(self.bodyparts)!=len(set(self.bodyparts)):
          print("Error - bodyparts must have unique labels! Please choose unique bodyparts in config.yaml file and try again. Quitting for now!")
          self.Close(True)

        self.figure,self.axes,self.canvas,self.toolbar = self.image_panel.drawplot(self.img,img_name,self.iter,self.index,self.bodyparts,self.colormap)

# the first checkbox is for quartile and the second checkbox is the central analysis
        self.choiceBox,self.checkBoxes = self.choice_panel.addCheckButtons(self.bodyparts,self.file,self.markerSize)

        self.Bind(wx.EVT_CHECKBOX, self.isQuartile, self.checkBoxes[0])
        self.Bind(wx.EVT_CHECKBOX, self.isCentral, self.checkBoxes[1])

        self.buttonCounter = MainFrame.plot(self,self.img)

    # Analysis Patches
    def createPatch(self, img_size):
        x, y, d = img_size
        self.central_rect = patches.Rectangle((y/4, x/4), y/2, x/2, fill=False, color='w', lw=4)
        starting_points = [(0,0), (y/2, 0), (0, x/2), (y/2,x/2)]
        quadrants = []
        for starting_point in starting_points:
            quadrants.append(patches.Rectangle(starting_point, y/2, x/2, fill=False, color='w', lw=4))
        self.rect = PatchCollection(quadrants, match_original=True)
        self.options = {
                'vector-based': {
                    'start' : [(x/2, y/2), (x/2, y/2), (x/2, y/2), (x/2, y/2)],
                    'end' : [(0, y/2), (x/2, 0), (x, y/2), (x/2, y)]
                    },
                'center-based': {
                    'start' : [(x/4, y/4), (3*x/4, y/4), (3*x/4, 3*y/4), (x/4, 3*y/4)],
                    'end' : [(3*x/4, y/4), (3*x/4, 3*y/4), (x/4, 3*y/4), (x/4, y/4)]
                    }
                }


    # Quartile Analysis showing to the plot
    def isQuartile(self, evt):
        curBox = evt.GetEventObject()
        if(curBox.IsChecked()):
            self.axes.add_collection(self.rect)
        else:
            self.rect.remove()
        self.figure.canvas.draw()



    # Center analysis showing to the plot
    def isCentral(self, evt):
        curBox = evt.GetEventObject()
        if(curBox.IsChecked()):
            self.axes.add_patch(self.central_rect)
        else:
            self.central_rect.remove()
        self.figure.canvas.draw()


    def getLabels(self,img_index):
        """
        Returns a list of x and y labels of the corresponding image index
        """
        self.previous_image_points = []
        for bpindex, bp in enumerate(self.bodyparts):
            image_points = [[self.dataFrame[self.scorer][bp]['x'].values[self.iter],self.dataFrame[self.scorer][bp]['y'].values[self.iter],bp,bpindex]]
            self.previous_image_points.append(image_points)
        return(self.previous_image_points)

    def plot(self,img):
        """
        Plots and call auxfun_drag class for moving and removing points.
        """
        self.drs= []
        self.updatedCoords = []
        for bpindex, bp in enumerate(self.bodyparts):
            color = self.colormap(self.norm(self.colorIndex[bpindex]))
            self.points = [self.dataFrame[self.scorer][bp]['x'].values[self.iter],self.dataFrame[self.scorer][bp]['y'].values[self.iter]]
            circle = [patches.Circle((self.points[0], self.points[1]), radius=self.markerSize, fc = color, alpha=self.alpha)]
            self.axes.add_patch(circle[0])
            self.dr = auxfun_drag_label.DraggablePoint(circle[0],self.bodyparts[bpindex])
            self.dr.connect()
            self.dr.coords = MainFrame.getLabels(self,self.iter)[bpindex]
            self.drs.append(self.dr)
            self.updatedCoords.append(self.dr.coords)
            if np.isnan(self.points)[0] == False:
                self.buttonCounter.append(bpindex)
        self.figure.canvas.draw()

        return(self.buttonCounter)


def show(config, files=[]):
    app = wx.App()
    frame = MainFrame(None, config, files).Show()
    app.MainLoop()


