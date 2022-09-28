import wx
from main_page import MainPage
from page2 import Page2
from tools.utils import load_data

def get_path():
    with wx.DirDialog(
        None,
        message="打开数据文件夹",
        defaultPath="",
        style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
    ) as dlg:
        if dlg.ShowModal() == wx.ID_OK:
            data_path = dlg.GetPath()
            return data_path

class MainFrame(wx.Frame):

    def __init__(self, parent, title, default_size=(800, 600), data_path="."):
        wx.Frame.__init__(self, parent, title=title)
        self.data_all = load_data(data_path)

        self.SetMinSize(default_size)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        # self.Bind(wx.EVT_SIZE, self.on_size)
        self.screen_w, self.screen_h = wx.DisplaySize()
        
        self.scroll = wx.ScrolledWindow(self, size=default_size)
        self.nb = wx.Notebook(self.scroll, size=default_size)
        self.nb.AddPage(MainPage(self.nb, data_path=data_path,stock_data=self.data_all), "图形相似对比筛选")
        self.nb.AddPage(Page2(self.nb,data_path=data_path,stock_data=self.data_all), "数据涨幅筛选")
        self.scroll.SetVirtualSize((self.screen_w, self.screen_h))
        self.scroll.SetScrollRate(20,20)
        sizer.Add(self.scroll, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer)
        sizer.Layout()
        sizer.Fit(self)

    
    # def on_size(self, e):
        
    #     client_size = self.GetClientSize()
    #     print(client_size, self.screen_w, self.screen_h)
    #     self.scroll.SetSize(0, 0, client_size.Width, client_size.Height)
    #     self.nb.SetSize(0, 0, self.screen_w, self.screen_h)

        

app = wx.App(False)
default_size=(800, 600)
data_path = get_path()
frame = MainFrame(None, title="Notebook Demo", data_path=data_path)
frame.Show()
app.MainLoop()
