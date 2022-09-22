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
from collections import Counter
import random
import matplotlib.pyplot as plt
from datetime import datetime
import pickle


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
            t_target_data = []
            f_target_data = []
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
                        t_target_data.append(
                            data[idx + 1 - scope : idx + 1 + scope + 1] + [1, new_name]
                        )
                    else:
                        f_target_data.append(
                            data[idx + 1 - scope : idx + 1 + scope + 1] + [0, new_name]
                        )
        # df = pd.DataFrame(target_data)
        # df.to_pickle(os.path.join(internal_data_root_path, new_name+'.pkl'))
        tl = len(t_target_data)
        fl = len(f_target_data)
        if tl or fl:
            if tl and fl:
                t = tl * 3
                if t > fl:
                    t = fl
                target_data = t_target_data + random.sample(f_target_data, t)
            else:
                if tl:
                    target_data = t_target_data
                else:
                    t = 100
                    if t > fl:
                        t = fl
                    target_data = random.sample(f_target_data, t)
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

    save_washed_data(total_data, total_label)
    return total_data, total_label


def wash_data(total_datas):
    df = pd.DataFrame(total_datas)
    data = df[range(11)]

    label = df[11]
    data = data.apply(lambda x: [i[1] for i in x])

    data = data.to_numpy()
    label = label.to_numpy()
    data = data.astype("float32")
    label = label.astype("float32")
    mm = data.max()
    mmin = data.min()
    data -= mmin
    std = mm - mmin
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
    model.compile(optimizer="adam", loss=losses.binary_crossentropy, metrics=["acc"])
    # metric accuracy : dict_keys(['loss', 'accuracy', 'val_loss', 'val_accuracy'])
    # metric acc : dict_keys(['loss', 'acc', 'val_loss', 'val_acc'])
    return model


def paint(history):
    plt.subplot(1, 2, 1)
    history_dict = history.history
    print(history_dict.keys())
    loss_values = history_dict["loss"]
    val_loss = history_dict["val_loss"]
    epochs = range(1, len(loss_values) + 1)
    plt.plot(epochs, loss_values, "bo", label="Training loss")
    plt.plot(epochs, val_loss, "b", label="Testing loss")
    plt.title("Training vs Test loss")
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.legend()

    plt.subplot(1, 2, 2)
    acc = history_dict["acc"]
    val_acc = history_dict["val_acc"]
    epochs = range(1, len(acc) + 1)
    plt.plot(epochs, acc, "bo", label="Training acc")
    plt.plot(epochs, val_acc, "b", label="Testing acc")
    plt.title("Training vs Test accuracy")
    plt.xlabel("Epochs")
    plt.ylabel("Acc")
    plt.legend()
    plt.show()


def save_washed_data(total_data, total_label):
    data = {"data": total_data, "label": total_label}
    with open("./ml_demo/washed_data.pkl", "wb") as wh:
        pickle.dump(data, wh)


def load_washed_data(data_path="./ml_demo/washed_data.pkl"):
    # data = {
    #     'data': total_data,
    #     'label':total_label
    # }
    with open("./ml_demo/washed_data.pkl", "rb") as rh:
        data = pickle.load(rh)
        return data["data"], data["label"]


def train():
    data_path = "./ml_demo/washed_data.pkl"
    if os.path.exists(data_path):
        print("load data from pickle")
        total_data, total_label = load_washed_data(data_path)
    else:
        print("load data from csv")
        total_data, total_label = load_data()
    model_name = "ml_model_{}_v{}.h5".format(datetime.now().strftime("%Y_%m_%d"), 1)
    data = np.vstack(total_data)
    label = np.hstack(total_label)
    label = label.astype("float32")
    data_len = data.shape[0]
    train_size = int(data_len * 0.8)
    test_size = data_len - train_size
    val_size = int(train_size * 0.2)
    train_size = train_size - val_size
    split_size = [train_size, test_size, val_size]
    # print(split_size)
    train_data, test_data, val_data = tf.split(data, split_size, axis=0)
    # print(train_data.shape, test_data.shape, val_data.shape)
    train_label, test_label, val_label = tf.split(label, split_size, axis=0)
    # print(
    #     Counter(train_label.numpy()),
    #     Counter(test_label.numpy()),
    #     Counter(val_label.numpy()),
    # )
    model = build_model(train_data.shape[1])
    history = model.fit(
        train_data,
        train_label,
        epochs=11,
        batch_size=64,
        validation_data=(test_data, test_label),
    )
    paint(history)
    model.save(model_name)

    del model
    loaded_model = models.load_model(model_name)
    print(loaded_model.summary())
    loss, acc = loaded_model.evaluate(val_data, val_label, verbose=2)
    print(loss, acc)


if __name__ == "__main__":
    train()
