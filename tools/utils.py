import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import re


def analysis_header(header):
    header = header.strip().replace("*", "").split(" ")
    code, name = header[:2]
    return code, name

def filter_data_by_date(stock_infos, start_date, end_date):
    try:
        new_stock_infos = {}
        for code in stock_infos:
            name, data = stock_infos[code]
            found_s = False
            found_end = False
            found = 0
            found_data = []
            for line in data:
                dt, price, _ = line
                if found_s is False and dt >= start_date:
                    found += 1
                    found_s = True
                if found_end is False and dt >= end_date:
                    found += 1
                    found_end = True
                if found_s:
                    found_data.append((dt, price))
                if found == 2:
                    break
            if found == 2: 
                new_stock_infos[code] = (name, found_data)
    except Exception as e:
        print(e)
    return new_stock_infos


def load_data(root_path):
    file_paths = [
        os.path.join(root_path, file_name)
        for file_name in os.listdir(root_path)
        if re.match("^SH.*?\.txt$", file_name)
    ]
    thread_num_threshhold = 30
    thread_num = len(file_paths) // 10
    if thread_num > thread_num_threshhold:
        thread_num = thread_num_threshhold
    result = {}
    with ThreadPoolExecutor(max_workers=thread_num) as pool:
        tasks = []
        for fp in file_paths:
            t_obj = pool.submit(read_file, fp)
            tasks.append(t_obj)
        for t in as_completed(tasks):
            ret = t.result()
            if ret:
                result.update(ret)
    return result


def read_file(file_path):
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
                deal_amount = int(stock_info[5])
                data.append((dt, price, deal_amount))
            return {code: (name, data)}
    except Exception as e:
        print(e)
    return {}
