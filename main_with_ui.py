import wx
import os
from wx.adv import DatePickerCtrl
from datetime import datetime
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed


def cos_similarity(v1, v2):
    if len(v1) != len(v2):
        return 0
    v1 = np.array(v1)
    v2 = np.array(v2)
    cos_sim = v1.dot(v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return cos_sim


def list_all_files(root_path):
    all_file_names = os.listdir(root_path)
    file_paths = [os.path.join(root_path, file_name) for file_name in all_file_names]
    return file_paths, all_file_names


def analysis_header(header):
    header = header.strip().replace("*", "").split(" ")
    code, name = header[:2]
    return code, name


def get_v2(data, s, e):
    start_idx = None
    end_idx = None
    found = 0
    for idx, item in enumerate(data):
        dt, price = item
        if start_idx is None and dt >= s:
            start_idx = idx
            found += 1
        if end_idx is None and dt >= e:
            end_idx = idx
            found += 1
        if found == 2:
            break
    if found != 2:
        return None
    return [data[i] for i in range(start_idx, end_idx + 1)]


def has_simlarity(file_path, v1, start_date, end_date):
    code, name, data = read_data_from_file(file_path)
    v1_lenght = len(v1)
    if len(data) < v1_lenght:
        return None
    v2_info = get_v2(data, start_date, end_date)
    if not v2_info:
        return None
    v2 = [a[1] for a in v2_info]
    sim = cos_similarity(v1, v2)
    if sim < 0.95:
        return None
    else:
        return code, name, v2_info


def search(file_paths, v1, start_date, end_date):
    result = []
    with ThreadPoolExecutor(max_workers=40) as pool:
        tasks = []
        for fp in file_paths:
            t_obj = pool.submit(has_simlarity, fp, v1, start_date, end_date)
            tasks.append(t_obj)
        for t in as_completed(tasks):
            ret = t.result()
            if ret:
                result.append(ret)

    return result


def read_data_from_file(file_path):
    try:
        with open(file_path, encoding="gbk") as rh:
            lines = rh.readlines()
            header = lines[0]
            code, name = analysis_header(header)
            # print(new_name)
            data = []
            for line in lines[2:-1]:
                stock_info = line.strip().split("\t")
                t = stock_info[0]
                dt = datetime.strptime(t, "%Y/%m/%d").date()
                price = float(stock_info[4])
                data.append((dt, price))
            return [code, name, data]
    except Exception as e:
        print(e)
    return []


class MainFrame(wx.Frame):
    def __init__(self, parent, title, default_size=(800, 600)):
        wx.Frame.__init__(self, parent=parent, title=title)
        self.SetMinSize(default_size)

        self.data_path = None
        self.log_ctl = None
        self.stock_code = None
        self.stock_code_ctl = None
        self.start_date = None
        self.start_date_ctl = None
        self.end_date = None
        self.end_date_ctl = None
        self.all_file_names = None
        self.all_file_pathes = None
        self.op_counter = 1
        self.error_prefix = "!!!!!!!!!"
        self.file_name_tpl = "SH#{}.txt"

        # self.Bind(wx.EVT_SIZE, self.max_log)
        self.panel = wx.Panel(self)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        title_sizer = self.place_title_sizer()
        config_sizer = self.place_config_sizer()
        log_sizer = self.place_log_sizer()
        info_sizer = self.place_stock_choser_info()

        self.main_sizer.Add(title_sizer, 0, wx.CENTER)
        self.main_sizer.Add(
            wx.StaticLine(
                self.panel,
            ),
            0,
            wx.ALL | wx.EXPAND,
            5,
        )
        self.main_sizer.Add(config_sizer, 0, wx.ALL | wx.EXPAND, 5)

        self.main_sizer.Add(
            wx.StaticLine(
                self.panel,
            ),
            0,
            wx.ALL | wx.EXPAND,
            5,
        )
        self.main_sizer.Add(info_sizer, 0, wx.ALL | wx.EXPAND, 5)

        self.main_sizer.Add(
            wx.StaticLine(
                self.panel,
            ),
            0,
            wx.ALL | wx.EXPAND,
            5,
        )
        self.main_sizer.Add(log_sizer, 0, wx.ALL | wx.EXPAND, 5)

        self.panel.SetSizer(self.main_sizer)
        self.main_sizer.Fit(self)

    def wxdate2pydate(self, date):
        assert isinstance(date, wx.DateTime)
        if date.IsValid():
            ymd = date.Format("%Y-%m-%d")
            return datetime.strptime(ymd, "%Y-%m-%d").date()
        else:
            return None

    def place_stock_choser_info(self):
        info_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(self.panel, label="股票编码：")
        self.stock_code_ctl = wx.TextCtrl(self.panel, size=(100, 25), value="600225")
        label2 = wx.StaticText(self.panel, label="时间区间：")
        self.start_date_ctl = DatePickerCtrl(
            self.panel, dt=datetime.strptime("2022-07-10", "%Y-%m-%d").date()
        )
        self.end_date_ctl = DatePickerCtrl(
            self.panel, dt=datetime.strptime("2022-07-25", "%Y-%m-%d").date()
        )

        btn = wx.Button(self.panel, label="找到相似区间")
        btn.Bind(wx.EVT_BUTTON, self.on_find_similary)

        info_sizer.Add(label1, 0, wx.ALL, border=5)
        info_sizer.Add(self.stock_code_ctl, 0, wx.ALL, border=5)
        info_sizer.Add(label2, 0, wx.ALL, border=5)
        info_sizer.Add(self.start_date_ctl, 0, wx.ALL, border=5)
        info_sizer.Add(self.end_date_ctl, 0, wx.ALL, border=5)
        info_sizer.Add(btn, 0, wx.ALL, border=5)

        return info_sizer

    def found_v1(self, data, s, e):
        start_idx = None
        end_idx = None
        found = 0
        for idx, item in enumerate(data):
            dt, price = item
            if start_idx is None and dt >= s:
                start_idx = idx
                found += 1
            if end_idx is None and dt >= e:
                end_idx = idx
                found += 1
            if found == 2:
                break
        if found != 2:
            self.error("无法找到满足条件额数据")
            return None
        self.log(
            "根据条件解析数据为：{}".format(
                ",".join(
                    [
                        str((str(data[i][0]), str(data[i][1])))
                        for i in range(start_idx, end_idx + 1)
                    ]
                )
            )
        )
        return [data[i][1] for i in range(start_idx, end_idx + 1)]

    def on_find_similary(self, e):
        if not self.data_path:
            if self.path_ctl:
                self.data_path = self.path_ctl.GetValue()
            if not self.data_path:
                self.error("请先选择数据文件夹")
                return
        if not self.all_file_names:
            if self.data_path:
                self.all_file_pathes, self.all_file_names = list_all_files(
                    self.data_path
                )
            if not self.all_file_names:
                self.error("选择的目录下没有文件无法计算")
                return
        self.stock_code = self.stock_code_ctl.GetValue()
        chosed_file = self.file_name_tpl.format(self.stock_code)
        if chosed_file not in self.all_file_names:
            self.error(" 请检查输入的股票代码是否正确， 文件 {} 不存在".format(chosed_file))
            return
        ret = read_data_from_file(os.path.join(self.data_path, chosed_file))
        if not ret:
            self.error(" 文件 {} 读取失败".format(chosed_file))
            return
        _, name, data = ret
        self.start_date = self.start_date_ctl.GetValue()
        self.end_date = self.end_date_ctl.GetValue()
        if self.start_date:
            self.start_date = self.wxdate2pydate(self.start_date)
        if self.end_date:
            self.end_date = self.wxdate2pydate(self.end_date)

        diff = (self.end_date - self.start_date).days
        if diff < 3 or diff > 20:
            self.error("时间区间的范围请设定在 3 到 20 天")
            return
        op_log = "【操作 {} 】区间（向量）相似计算:\n股票代码:{} {} \n时间区间: {} ~ {}, 共计 {} 天\n".format(
            self.op_counter, self.stock_code, name, self.start_date, self.end_date, diff
        )
        self.log(op_log)
        self.op_counter += 1
        v1 = self.found_v1(data, self.start_date, self.end_date)
        if not v1:
            return
        else:
            self.log("")
            ret = search(self.all_file_pathes, v1, self.start_date, self.end_date)
            self.log(self.format(ret))

    def format(self, out):
        result = []
        c = 1
        for item in out:
            code, name, found_data = item
            d = "".join(["{} , {}\t".format(*d) for d in found_data])
            s = "{}\t{} {} {}".format(c, code, name, d)
            result.append(s)
            c += 1
        return "\n".join(result)

    def place_log_sizer(self):
        log_sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self.panel, label="执行记录：")
        self.log_ctl = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE)
        self.log_ctl.SetMinSize((750, 400))
        op_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn = wx.Button(self.panel, label="日志清理")
        btn.Bind(wx.EVT_BUTTON, self.on_log_clear)
        op_sizer.Add(label, 0, wx.ALL, 5)
        op_sizer.Add(btn, 0, wx.ALL, 5)
        log_sizer.Add(op_sizer)
        log_sizer.Add(self.log_ctl, 0, wx.ALL, 5)
        return log_sizer

    def max_log(self, e):
        return 
        # w, h = self.GetSize()
        # self.log_ctl.SetSize((w - 10, h))
        # self.Refresh()


    def on_log_clear(self, e):
        if self.log_ctl:
            self.log_ctl.Clear()

    def place_title_sizer(self):
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self.panel, label="Simple tool")
        title_sizer.Add(title, 0, wx.ALL, 5)
        return title_sizer

    def place_config_sizer(self):
        config_sizer = wx.BoxSizer(wx.HORIZONTAL)
        config_btn = wx.Button(self.panel, label="数据路径")
        config_btn.Bind(wx.EVT_BUTTON, self.on_open_path)
        self.path_ctl = wx.TextCtrl(
            self.panel, size=(200, 25), style=wx.TE_READONLY, value="D:\小任务数据\export"
        )
        config_sizer.Add(config_btn)
        config_sizer.Add(self.path_ctl)
        return config_sizer

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

    def on_open_path(self, e):
        with wx.DirDialog(
            None,
            message="打开数据文件夹",
            defaultPath="",
            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
        ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                data_path = dlg.GetPath()
                self.data_path = data_path
                self.path_ctl.SetLabelText(data_path)
                self.log("选择数据文件路径：{}".format(self.data_path))
                self.all_file_pathes, self.all_file_names = list_all_files(
                    self.data_path
                )
                if not self.all_file_names:
                    self.error("选择的路径下不存在任何文件")


app = wx.App(False)
fm = MainFrame(None, "Tool")
fm.Show()
app.MainLoop()