import wx
import wx.lib.agw.aui as aui

import matplotlib as mpl
import matplotlib.image as mpimg
from matplotlib.widgets import RectangleSelector
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

class Plot(wx.Panel):

    def __init__(self, parent, dpi=None, img=None, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.figure = mpl.figure.Figure(dpi=dpi, figsize=(2,2))
        self.canvas = FigureCanvas(self, -1, self.figure)
        # Axes Configuration
        self._axes = self.figure.gca()
        self._rect_selector = RectangleSelector(self._axes, self._line_select_callback,
                                    drawtype='box', useblit=True,
                                    button=[1, 3], minspanx=5, minspany=5,
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
    
    def _line_select_callback(self, eclick, erelease):
        """
        docstring
        """
        self._x1, self._y1 = int(eclick.xdata), int(eclick.ydata)
        self._x2, self._y2 = int(erelease.xdata), int(erelease.ydata)
        
    

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

    

class PlotNotebook(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.nb = aui.AuiNotebook(self)
        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def add(self, name='plot', img=None):
        page = Plot(self.nb, img=img)
        self.nb.AddPage(page, name)
        return page.figure


def demo():
    app = wx.App()
    frame = wx.Frame(None, -1, 'Plotter')
    plotter = PlotNotebook(frame)
    image_source = ".\\media\\dlc_1-01.png"
    img = mpimg.imread(image_source)
    fig = plotter.add('figure 1', img)
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    demo()
