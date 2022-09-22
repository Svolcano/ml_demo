import os
import numpy as np
import pandas as pd
import csv
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from keras import models, losses, metrics, activations, optimizers
from keras import layers
import tensorflow as tf


step = 2
scope = 5
target = 0.12

data_root_path = "D:/小任务数据/export"
internal_data_root_path = "D:/小任务数据/internal"
washed_data_root_path = "D:/小任务数据/washed"


def time_it(func):
    def inner(*argc, **kwargs):
        st = time.time()
        r = func(*argc, **kwargs)
        et = time.time()
        print("***** function: {} cost {:.2f}".format(func.__name__, et - st))
        return r

    return inner


def analysis_header(header):
    header = header.strip().replace("*", "").split(" ")
    return "_".join(header[:2])


def read_data_from_file(file_path):
    try:
        with open(file_path, encoding="gbk") as rh:
            lines = rh.readlines()
            header = lines[0]
            new_name = analysis_header(header)
            # print(new_name)
            data = []
            for line in lines[2:-1]:
                stock_info = line.strip().split("\t")
                price = float(stock_info[4])
                deal_amount = int(stock_info[5])
                t = stock_info[0]
                data.append((t, price, deal_amount))
            data_len = len(data) - scope
            target_data = []
            for idx, row in enumerate(data):
                if idx < scope:
                    continue
                price = row[1]
                deal_amount = row[2]
                if price == 0 or deal_amount == 0:
                    continue
                next_day_idx = idx + step
                if next_day_idx < data_len:
                    next_price = data[next_day_idx][1]
                    next_deal_amount = data[next_day_idx][2]
                    price_ratio = (next_price - price) / price
                    deal_amount_ratio = (next_deal_amount - deal_amount) / deal_amount
                    # print(price_ratio, deal_amount_ratio)
                    if price_ratio > target and deal_amount_ratio > target:
                        target_data.append(
                            data[idx + 1 - scope : idx + 1 + scope + 1] + [1, new_name]
                        )
                    else:
                        target_data.append(
                            data[idx + 1 - scope : idx + 1 + scope + 1] + [0, new_name]
                        )
        # df = pd.DataFrame(target_data)
        # df.to_pickle(os.path.join(internal_data_root_path, new_name+'.pkl'))
        if len(target_data) > 10:
            return wash_data(target_data)
    except Exception as e:
        print(e)
        print(file_path)
    return None, None

@time_it
def load_data(root_path="D:\小任务数据\export"):
    all_files = os.listdir(root_path)
    file_paths = [os.path.join(root_path, file_name) for file_name in all_files]
    total_data = []
    total_label = []

    with ThreadPoolExecutor(max_workers=40) as pool:
        tasks = []
        for fp in file_paths:
            t_obj = pool.submit(read_data_from_file, fp)
            tasks.append(t_obj)
        for t in as_completed(tasks):
            data, label = t.result()
            if data is not None:
                total_data.append(data)
                total_label.append(label)
                
    data = np.vstack(total_data)
    label = np.hstack(total_label)
    # print(np.unique(label))



    # model = build_model(train.shape[1])
    # history = model.fit(train, train_label, epochs=80, batch_size=20000, validation_data=(test, test_label))

    # result = model.evaluate(val, val_label)
    # print(result)
    # print(model.predict(val))

def wash_data(total_datas):
    df = pd.DataFrame(total_datas)
    data = df[range(11)]
    
    label = df[11]
    data = data.apply(lambda x: [i[1] for i in x])
    
    data = data.to_numpy()
    label = label.to_numpy()

    mm = data.max()
    mmin = data.min()
    data -= mmin
    std =  mm - mmin
    try:
        data /= std
    except Exception as e:
        print(std)
    return data, label


@time_it
def test():
    r = read_data_from_file("D:\小任务数据\export\SH#688630.txt")
    return r


def build_model(shape):
    model = models.Sequential()
    model.add(layers.Dense(64, activation=activations.relu, input_shape=(shape,)))
    model.add(layers.Dense(64, activation=activations.relu))
    # model.add(layers.Dense(64, activation=activations.relu))
    model.add(layers.Dense(1, activation=activations.sigmoid))
    model.compile(
        optimizer="rmsprop", loss=losses.binary_crossentropy, metrics=[metrics.accuracy]
    )
    return model


if __name__ == "__main__":
    load_data()
