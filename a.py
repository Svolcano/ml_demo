# sample_one.py

"""

Link : https://matplotlib.org/3.3.1/gallery/user_interfaces/embedding_in_wx5_sgskip.html

"""

import os
import sys
from numpy import arange, sin, pi
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar2Wx
import wx

# class MyCanvasPanel
# class MyFrame
# class MyApp

#---------------------------------------------------------------------------

class MyCanvasPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        #------------

        # Simplified init method.
        self.CreateCtrls()
        self.DoLayout()

    #-----------------------------------------------------------------------

    def CreateCtrls(self):
        """
        ...
        """

        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)

        #------------

        self.canvas = FigureCanvas(self, -1, self.figure)

        #------------

        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()


    def DoLayout(self):
        """
        ...
        """

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)
        self.Fit()


    def Draw(self):
        """
        ...
        """

        t = arange(0.0, 3.0, 0.01)
        s = sin(2 * pi * t)
        self.axes.plot(t, s)

#---------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, -1,
                          title,
                          size=(620, 620))

        #------------

        # Return icons folder.
        self.icons_dir = wx.GetApp().GetIconsDir()

        #------------

        # Simplified init method.
        self.SetProperties()
        self.CreateCtrls()

    #-----------------------------------------------------------------------

    def SetProperties(self):
        """
        ...
        """

        self.SetMinSize((620, 620))

        #------------

        frameIcon = wx.Icon(os.path.join(self.icons_dir,
                                         "wxwin.ico"),
                            type=wx.BITMAP_TYPE_ICO)
        self.SetIcon(frameIcon)


    def CreateCtrls(self):
        """
        ...
        """

        self.panel = MyCanvasPanel(self)
        self.panel.Draw()

#---------------------------------------------------------------------------

class MyApp(wx.App):
    def OnInit(self):

        #------------

        self.installDir = os.path.split(os.path.abspath(sys.argv[0]))[0]

        #------------

        frame = MyFrame("Sample one")
        self.SetTopWindow(frame)
        frame.Show(True)

        return True

    #-----------------------------------------------------------------------

    def GetInstallDir(self):
        """
        Return the installation directory for my application.
        """

        return self.installDir


    def GetIconsDir(self):
        """
        Return the icons directory for my application.
        """

        icons_dir = os.path.join(self.installDir, "icons")
        return icons_dir

#---------------------------------------------------------------------------

def main():
    app = MyApp(False)
    app.MainLoop()

#---------------------------------------------------------------------------

if __name__ == "__main__" :
    main()