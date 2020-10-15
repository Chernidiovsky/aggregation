# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.preprocessing import StandardScaler
from math import log, tan, pi, floor, ceil
import pypinyin
import matplotlib.pyplot as plt
from csvToKml import getKML
import sys
sys.setdefaultencoding('utf-8')

AVG_TASK_POINT = 200


def pinyin(word):
    s = ''
    for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
        s += ''.join(i)
    return s


def planeProjection(lng, lat):
    # 地球周长
    length = 6381372 * pi * 2
    # 平面展开后，x轴等于周长
    width = length
    # y轴约等于周长一半
    height = length / 2
    # 米勒投影中的一个常数，范围大约在正负2.3之间
    mill = 2.3
    # 将经纬度从度数转换为弧度
    lng = float(lng) * pi / 180
    lat = float(lat) * pi / 180
    # 米勒投影的转换
    lat = 1.25 * log(tan(0.25 * pi + 0.4 * lat))
    # 弧度转为实际距离
    lng = (width / 2) + (width / (2 * pi)) * lng
    lat = (height / 2) - (height / (2 * mill)) * lat
    return lng, lat


def getKMeans(xDf, avg):
    X = xDf.values
    X = StandardScaler().fit_transform(X)
    X_uni = np.array(list(set([tuple(t) for t in X.tolist()])))
    n_clusters = int(floor(len(X_uni) / avg))
    if n_clusters <= 1:
        Y_uni = np.zeros_like(X_uni[:, 0])
    else:
        Y_uni = KMeans(n_clusters=n_clusters).fit_predict(X_uni)
    temp = []
    for x in X.tolist():
        for x_uni, y_uni in zip(X_uni.tolist(), Y_uni.tolist()):
            if x == x_uni:
                temp.append(y_uni)
                break
    Y = np.array(temp)  # 去重叠后的聚类结果映射至去重叠前，输出和输入长度及顺序一致
    return Y


def getAggCluster(xDf, avg):
    X = xDf.values
    X = StandardScaler().fit_transform(X)
    X_uni = np.array(list(set([tuple(t) for t in X.tolist()])))
    n_clusters = int(ceil(1. * len(X_uni) / avg))
    if n_clusters <= 1:
        Y_uni = np.zeros_like(X_uni[:, 0])
    else:
        Y_uni = AgglomerativeClustering(n_clusters=n_clusters).fit_predict(X_uni)
    temp = []
    for x in X.tolist():
        for x_uni, y_uni in zip(X_uni.tolist(), Y_uni.tolist()):
            if x == x_uni:
                temp.append(y_uni)
                break
    Y = np.array(temp)  # 去重叠后的聚类结果映射至去重叠前，输出和输入长度及顺序一致
    return Y


def getDBSCAN(xDf, avg):
    X = xDf.values
    X = StandardScaler().fit_transform(X)
    X_uni = np.array(list(set([tuple(t) for t in X.tolist()])))
    n_clusters = int(ceil(1. * len(X_uni) / avg))
    if n_clusters <= 1:
        Y_uni = np.zeros_like(X_uni[:, 0])
    else:
        Y_uni = DBSCAN(eps=0.02, min_samples=2).fit_predict(X_uni)
    temp = []
    for x in X.tolist():
        for x_uni, y_uni in zip(X_uni.tolist(), Y_uni.tolist()):
            if x == x_uni:
                temp.append(y_uni)
                break  # 去重叠后的聚类结果映射至去重叠前，输出和输入长度及顺序一致
    Y = np.array(temp)
    # temp2 = []
    # i = len([y for y in temp if y > -1])
    # print(i)
    # for y in temp:
    #     if y == -1:
    #         temp2.append(i)
    #         i += 1
    #     else:
    #         temp2.append(y)  # 噪点单独编一组
    # Y = np.array(temp2)
    return Y


def colorMakerIndex(k):
    colors = ["k", "r", "y", "g", "b", "c", "m"]
    markers = [".", ",", "o", "v", "^", "<", ">", "1", "2", "3", "4", "8", "s", "p", "P", "*", "h", "H", "+", "x", "X",
               "D", "d", "|", "_"]
    i = k % len(colors)
    j = k % len(markers)
    return colors[i], markers[j]


def plotGroups(df):
    clusterId = set(df["cluster_id"].values.tolist())
    print(len(clusterId))
    for idx, cluster in enumerate(clusterId):
        subDf = df[df["cluster_id"] == cluster][["lng", "lat"]]
        print("%s: %s" % (cluster, len(subDf)))
        xLng, yLat = subDf["lng"], subDf["lat"]
        c, m = colorMakerIndex(idx)
        plt.scatter(xLng, yLat, c=c, marker=m)
    plt.show()


def districtClustering(district, clusterType):
    df = pd.read_csv("shenzhen.csv", encoding="utf-8")
    df = df[df["district"] == district]
    print(len(df))
    data = []
    for row in df.values:
        lng, lat = planeProjection(row[1], row[2])
        data.append([lng, lat])
    projDf = pd.DataFrame(data=data, columns=["lng", "lat"])

    if clusterType == "agg":
        yClusters = getAggCluster(projDf, AVG_TASK_POINT)
    elif clusterType == "km":
        yClusters = getKMeans(projDf, AVG_TASK_POINT)
    else:
        yClusters = getDBSCAN(projDf, AVG_TASK_POINT)

    data = df[["cust_code", "lng", "lat"]].values
    data = np.c_[data, yClusters]
    df = pd.DataFrame(data=data, columns=["cust_code", "lng", "lat", "cluster_id"])
    fileName = "%s_%s.csv" % (clusterType, pinyin(district))
    df.to_csv(fileName, encoding="utf-8")
    plotGroups(df)
    return fileName