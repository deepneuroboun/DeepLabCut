import wx
import wx.lib.agw.aui as aui

import matplotlib as mpl
import matplotlib.image as mpimg
from matplotlib.widgets import RectangleSelector, PolygonSelector, EllipseSelector
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.path import Path
import numpy as np

class Plot(wx.Panel):

    def __init__(self, parent, dpi=None, img=None, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.figure = mpl.figure.Figure(dpi=dpi, figsize=(2,2))
        self.canvas = FigureCanvas(self, -1, self.figure)
        # Axes Configuration
        self._axes = self.figure.gca()
        self._rect_selector = RectangleSelector(self._axes, self._line_select_callback,
                                    drawtype='box', useblit=True,
                                    button=[1], minspanx=5, minspany=5,
                                    spancoords='pixels', interactive=True)
        self._rect_selector.set_active(False)
        self._img = img
        self._cur_shown = self._axes.imshow(img)
        (y, x, _) = img.shape
        self._x1 = 0
        self._x2 = x
        self._y1 = 0
        self._y2 = y
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.customregionplots = {}
    
    def _line_select_callback(self, eclick, erelease):
        """
        docstring
        """
        self._x1, self._y1 = int(eclick.xdata), int(eclick.ydata)
        self._x2, self._y2 = int(erelease.xdata), int(erelease.ydata)
        
    
    def add_rs(self):
        return RectangleSelector(self._axes, self._line_select_callback,
                                 drawtype='box', useblit=True,
                                 button=[1], minspanx=5, minspany=5,
                                 spancoords='pixels', interactive=True)

    def set_active_rs(self, state):
        """
        docstring
        """
        self._rect_selector.set_active(state)

    

    def show_cropped_image(self):
        cur_img = self._img[self._y1:self._y2, self._x1:self._x2, :]

        self._cur_shown.remove()
        self._cur_shown = self._axes.imshow(cur_img)
        self._axes.relim()
        self.figure.canvas.draw_idle()
        self._img = cur_img
        
        return ((self._x1, self._x2, self._y1, self._y2), cur_img.shape)

        

    def get_axes(self):
        """
        docstring
        """
        return self._axes
    
    
    def poly_start_select(self):
        self.roi = PolygonSelector(self._axes, self.poly_onselect,
            lineprops= dict(color ="w", linewidth = 5), markerprops=dict(mec="w",mfc="k"))

    def poly_onselect(self,verts):
        self.canvas.draw()
        self.cur_vertices = verts
    
    def rect_start_select(self):
        self.roi = RectangleSelector(self._axes, self.rect_onselect,drawtype= 'box', interactive= True, spancoords='pixels',
             lineprops= dict(color ="w", linewidth = 8), rectprops= dict(edgecolor = 'white', fill = False, ))
    

    def rect_onselect(self,eclick,erelease):
        self.canvas.draw()
        self.cur_vertices = self.roi.geometry
    
    def ellipse_start_select(self):
        self.roi = EllipseSelector(self._axes, self.ellipse_onselect, drawtype= 'line', interactive= True, spancoords='pixels',
             lineprops= dict(color ="w", linewidth = 8), rectprops= dict(edgecolor = 'white', fill = False, ))
    
    def ellipse_onselect(self,eclick,erelease):
        self.canvas.draw()
        self.cur_vertices = self.roi.geometry
    
    def draw_ROI(self, vertex_coor,roi_name):
        
        if self.current_pol == "Other":
            draw = [list(item) for item in vertex_coor]
            draw.append(vertex_coor[0])
        
        elif self.current_pol == "Rectangle":
            draw = [list(reversed(list(vertex_coor[:,item]))) for item in range(np.shape(vertex_coor)[1])]
        
        elif self.current_pol == "Ellipse":
            draw = [list(vertex_coor[:,item]) for item in range(np.shape(vertex_coor)[1])]


        xs, ys = zip(*draw)
        self.customregionplots[roi_name] = self._axes.plot(xs,ys,"w",linewidth = 5)
        self.canvas.draw()
        self.roi.set_visible(False)