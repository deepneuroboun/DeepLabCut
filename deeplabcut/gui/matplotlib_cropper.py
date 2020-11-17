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
        self._img = img
        self._axes.imshow(img)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(sizer)
    
    def _line_select_callback(self, eclick, erelease):
        """
        docstring
        """
        x1, y1 = int(eclick.xdata), int(eclick.ydata)
        x2, y2 = int(erelease.xdata), int(erelease.ydata)
        cur_img = self._img[y1:y2, x1:x2, :]
        OtherFrame(title='Other Frame', parent=wx.GetTopLevelParent(self), img=cur_img)
        print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
        print(" The button you used were: %s %s" % (eclick.button, erelease.button))
        

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

class OtherFrame(wx.Frame):
    """
    docstring
    """
    def __init__(self, title, parent=None, img=None):
        """
        docstring
        """
        wx.Frame.__init__(self, parent=parent, title=title)
        Plot(self, img=img)
        self.Show()


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
