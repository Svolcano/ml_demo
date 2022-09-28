from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import (
    NavigationToolbar2WxAgg as NavigationToolbar2Wx,
)
import wx
from wx.adv import DatePickerCtrl
from datetime import datetime
from tools.const import g_win_default_size, g_border_size


class Mywin(wx.Frame):
    def __init__(self, parent, title, data, default_size=g_win_default_size):
        wx.Frame.__init__(self, parent, title=title)
        self.SetMinSize(default_size)
        self.data = data
        self.title = title
        self.InitUI()

    def InitUI(self):
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.CreateCtrls()
        self.DoLayout()
        self.Show(True)

    def CreateCtrls(self):
        """
        ...
        """

        self.figure = Figure()
        self.axes121 = self.figure.add_subplot(121)
        self.axes122 = self.figure.add_subplot(122)

        # ------------

        self.canvas = FigureCanvas(self, -1, self.figure)

        # ------------

        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()

    def DoLayout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)
        self.Fit()
        self.Centre()

    def Draw(self):
        x = [str(a[0]) for a in self.data]
        print(x)
        y = [a[1] for a in self.data]
        z = [a[2] for a in self.data]
        self.axes121.plot(x, y, "g", marker="D", markersize=g_border_size)
        # self.axes.set_xticklabels(rotation=45)
        self.axes121.set_xlabel("date")
        self.axes121.set_ylabel("price")
        self.axes122.plot(x, z, "g", marker="D", markersize=g_border_size)
        # self.axes.set_xticklabels(rotation=45)
        self.axes122.set_xlabel("date")
        self.axes122.set_ylabel("deal_amount")
        # self.axes122.ticklabel_format(style='plain')
        self.axes122.get_yaxis().get_major_formatter().set_scientific(False)
        self.figure.autofmt_xdate(rotation=270)

    def OnPaint(self, e):
        self.Draw()


class Page2(wx.Panel):
    def __init__(self, parent, data_path=".", stock_data={}):
        super(Page2, self).__init__(parent)
        self.log_ctl = None
        self.base_date = None
        self.base_date_ctl = None
        self.days = 0
        self.days_ctl = None
        self.days_config = {}
        self.op_counter = 1
        self.error_prefix = "!!!!!!!!!"
        # self.file_name_tpl = "SH#{}.txt"
        self.list_ctl = None
        self.data_path = data_path
        self.stock_data = stock_data
        self.searched_data = {}

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        title_sizer = self.place_title_sizer()
        log_sizer = self.place_log_sizer()
        info_sizer = self.place_stock_choser_info()
        list_sizer = self.place_similary_info()

        self.main_sizer.Add(title_sizer, 0, wx.LEFT)
        self.main_sizer.Add(
            wx.StaticLine(
                self,
            ),
            0,
            wx.ALL | wx.EXPAND,
            g_border_size,
        )
        self.main_sizer.Add(info_sizer, 0, wx.ALL | wx.EXPAND, g_border_size)

        self.main_sizer.Add(
            wx.StaticLine(
                self,
            ),
            0,
            wx.ALL | wx.EXPAND,
            g_border_size,
        )
        self.main_sizer.Add(list_sizer, 0, wx.ALL | wx.EXPAND, g_border_size)
        self.main_sizer.Add(
            wx.StaticLine(
                self,
            ),
            0,
            wx.ALL | wx.EXPAND,
            g_border_size,
        )
        self.main_sizer.Add(log_sizer, 0, wx.ALL | wx.EXPAND, g_border_size)
        self.SetSizer(self.main_sizer)
        self.log('在"{}"找到\t[{}]\t个股票文件'.format(self.data_path, len(self.stock_data)))

    def place_similary_info(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.list_ctl = wx.ListCtrl(self, style=wx.LC_SINGLE_SEL | wx.LC_REPORT)
        self.list_ctl.SetMinSize((750, 200))
        self.list_ctl.InsertColumn(0, "序号", width=40)
        self.list_ctl.InsertColumn(1, "股票编码", width=100)
        self.list_ctl.InsertColumn(2, "股票名称", width=200)
        self.list_ctl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_item_select)
        sizer.Add(self.list_ctl, 0, wx.ALL | wx.EXPAND, g_border_size)
        return sizer

    def on_item_select(self, e):
        list_item = e.Item
        idx = list_item.GetId()
        code_item = self.list_ctl.GetItem(idx, 1)
        code = code_item.GetText()
        name, dt_price_deal = self.searched_data[code]
        Mywin(None, "{}, {}".format(code, name), dt_price_deal)

    def wxdate2pydate(self, date):
        assert isinstance(date, wx.DateTime)
        if date.IsValid():
            ymd = date.Format("%Y-%m-%d")
            return datetime.strptime(ymd, "%Y-%m-%d").date()
        else:
            return None

    def place_stock_choser_info(self):
        outer_sizer = wx.BoxSizer(wx.VERTICAL)
        info_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label2 = wx.StaticText(self, label="基准时间：")
        self.base_date_ctl = DatePickerCtrl(
            self, dt=datetime.strptime("2022-07-10", "%Y-%m-%d").date()
        )

        #
        search_btn = wx.Button(self, label="检索")
        search_btn.Bind(wx.EVT_BUTTON, self.on_find_similary)
        info_sizer.Add(label2, 0, wx.ALL, border=g_border_size)
        info_sizer.Add(self.base_date_ctl, 0, wx.ALL, border=g_border_size)
        outer_sizer.Add(info_sizer, 0, wx.ALL, border=g_border_size)

        # days_config

        self.day_list_ctl = wx.ListCtrl(self, style=wx.LC_REPORT)
        self.day_list_ctl.SetMinSize((750, 200))
        self.day_list_ctl.InsertColumn(0, "天", width=40)
        self.day_list_ctl.InsertColumn(1, "价格上限", width=100)
        self.day_list_ctl.InsertColumn(2, "价格下限", width=120)
        self.day_list_ctl.InsertColumn(3, "成交量上限", width=120)
        self.day_list_ctl.InsertColumn(4, "成交量下限", width=120)

        day_btn = wx.Button(self, label="增加")
        day_del_btn = wx.Button(self, label="删除")
        list_sizer = wx.BoxSizer(wx.HORIZONTAL)

        def _add_item(sizer, label, ctl):
            sizer.Add(label, 0, wx.ALL, border=g_border_size)
            sizer.Add(ctl, 0, wx.ALL, border=g_border_size)

        p_up_l = wx.StaticText(self, label="价格上限:")
        p_up_ctl = wx.TextCtrl(self, size=(80, 25), value="0.6")

        p_down_l = wx.StaticText(self, label="价格下限:")
        p_down_ctl = wx.TextCtrl(self, size=(80, 25), value="-0.6")

        d_up_l = wx.StaticText(self, label="成交量上限:")
        d_up_ctl = wx.TextCtrl(self, size=(80, 25), value="0.8")

        d_down_l = wx.StaticText(self, label="成交量下限:")
        d_down_ctl = wx.TextCtrl(self, size=(80, 25), value="0.1")
        _add_item(list_sizer, p_up_l, p_up_ctl)
        _add_item(list_sizer, p_down_l, p_down_ctl)
        _add_item(list_sizer, d_up_l, d_up_ctl)
        _add_item(list_sizer, d_down_l, d_down_ctl)
        list_sizer.Add(day_btn, 0, wx.ALL, border=g_border_size)
        list_sizer.Add(day_del_btn, 0, wx.ALL, border=g_border_size)

        def on_add_list_item(e):
            p_up = p_up_ctl.GetValue()
            if p_up:
                p_up = float(p_up)
            p_down = p_down_ctl.GetValue()
            if p_down:
                p_down = float(p_down)
            d_up = d_up_ctl.GetValue()
            if d_up:
                d_up = float(d_up)
            d_down = d_down_ctl.GetValue()
            if d_down:
                d_down = float(d_down)
            if p_up and p_down and d_up and d_down:
                self.days += 1
                config = [p_up, p_down, d_up, d_down]
                self.days_config[self.days] = config
                self.day_list_ctl.Append([self.days] + config)

        def on_del_list_item(e):
            last_id = self.day_list_ctl.GetItemCount()
            if last_id:
                self.day_list_ctl.DeleteItem(last_id - 1)

        day_btn.Bind(wx.EVT_BUTTON, on_add_list_item)
        day_del_btn.Bind(wx.EVT_BUTTON, on_del_list_item)
        outer_sizer.Add(list_sizer, 0, wx.ALL, border=g_border_size)
        outer_sizer.Add(self.day_list_ctl, 0, wx.ALL, border=g_border_size)
        outer_sizer.Add(search_btn, 0, wx.ALL, border=g_border_size)
        return outer_sizer

    def on_find_similary(self, e):
        self.searched_data = {}
        if self.days < 2 or self.days > 10:
            wx.MessageBox("天数应该在2~10天")
            return
        self.base_date = self.base_date_ctl.GetValue()
        if self.base_date:
            self.base_date = self.wxdate2pydate(self.base_date)
        op_log = "【操作 {} 】区间相似搜索,基准时间: {},开始搜索....".format(
            self.op_counter, self.base_date
        )
        self.log(op_log)
        self.op_counter += 1
        self.search()

    def search(self):
        for code in self.stock_data:
            name, found_data = self.stock_data[code]
            found_base_date = False
            count = 0
            picked_data = []
            base_data = None
            error = False
            for item in found_data:
                dt, price, deal_amount = item
                if dt >= self.base_date and base_data is None:
                    found_base_date = 1
                    base_data = (price, deal_amount)

                if found_base_date:
                    if count == 0:
                        count += 1
                        continue
                    if count > self.days:
                        break
                    picked_data.append(item)
                    p_up, p_down, d_up, d_down = self.days_config[count]
                    base_price, base_deal = base_data
                    is_match = (
                        price > (1 + p_down) * base_price
                        and price < (1 + p_up) * base_price
                        and deal_amount > (1 + d_down) * base_deal
                        and deal_amount < (1 + d_up) * base_deal
                    )
                    # print(
                    #     code, name, base_data, item, self.days_config[count], is_match
                    # )
                    count += 1
                    if is_match:
                        continue
                    else:
                        error = True
                if error:
                    break
            if error is False:
                self.searched_data[code] = (name, picked_data)

        idx = 1
        for code in self.searched_data:
            name, _ = self.searched_data[code]
            self.list_ctl.Append([idx, code, name])
            idx += 1
        self.log("搜索完成")

    def place_log_sizer(self):
        log_sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, label="执行记录：")
        self.log_ctl = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.log_ctl.SetMinSize((750, 200))
        op_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn = wx.Button(self, label="日志清理")
        btn.Bind(wx.EVT_BUTTON, self.on_log_clear)
        op_sizer.Add(label, 0, wx.ALL, g_border_size)
        op_sizer.Add(btn, 0, wx.ALL, g_border_size)
        log_sizer.Add(op_sizer, 0, wx.ALL | wx.EXPAND, g_border_size)
        log_sizer.Add(self.log_ctl, 0, wx.ALL | wx.EXPAND, g_border_size)
        return log_sizer

    def on_log_clear(self, e):
        if self.log_ctl:
            self.log_ctl.Clear()

    def place_title_sizer(self):
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, label=" 数据路径：{}".format(self.data_path))
        title_sizer.Add(title, 0, wx.ALL, g_border_size)
        return title_sizer

    def log(self, msg):
        old_msg = self.log_ctl.GetValue()
        new_msg = "{}\n{}".format(old_msg, msg)
        self.log_ctl.SetValue(new_msg)
        self.log_ctl.ShowPosition(self.log_ctl.GetLastPosition())

    def error(self, msg):
        old_msg = self.log_ctl.GetValue()
        new_msg = "{}\n{}\t{}".format(old_msg, self.error_prefix, msg)
        self.log_ctl.SetValue(new_msg)
        self.log_ctl.ShowPosition(self.log_ctl.GetLastPosition())
