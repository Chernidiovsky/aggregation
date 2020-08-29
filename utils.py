import pandas as pd
import numpy as np
from math import log, tan, pi, floor, ceil, radians, sin, cos, atan2, sqrt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
import re


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


def reformat(row):
    [custCode, lng, lat, street] = row
    lng, lat = planeProjection(lng, lat)
    street = custCode if street == "" else street
    return [custCode, lng, lat, street]


def revStreet(street):
    return "" if re.sub("[^\d]", "", street) == street and len(street) == 12 else street


def getKMeans(x, avg):
    x = StandardScaler().fit_transform(x)
    xUniq = np.array(list(set([tuple(t) for t in x.tolist()])))
    n = int(floor(len(xUniq) / avg))
    if n <= 1:
        yUniq = np.zeros_like(xUniq[:, 0])
    else:
        yUniq = KMeans(n_clusters=n).fit_predict(xUniq)
    temp = []
    for x in x.tolist():
        for xu, yu in zip(xUniq.tolist(), yUniq.tolist()):
            if x == xu:
                temp.append(yu)
                break
    Y = np.array(temp)  # 去重叠后的聚类结果映射至去重叠前，输出和输入长度及顺序一致
    return Y


def getAggCluster(x, avg):
    x = StandardScaler().fit_transform(x)
    xUniq = np.array(list(set([tuple(t) for t in x.tolist()])))
    n = int(ceil(1.2 * len(xUniq) / avg))
    if n <= 1:
        yUniq = np.zeros_like(xUniq[:, 0])
    else:
        yUniq = AgglomerativeClustering(n_clusters=n).fit_predict(xUniq)
    temp = []
    for x in x.tolist():
        for xu, yu in zip(xUniq.tolist(), yUniq.tolist()):
            if x == xu:
                temp.append(yu)
                break
    y = np.array(temp)  # 去重叠后的聚类结果映射至去重叠前，输出和输入长度及顺序一致
    return y


def locationKM(df, avg):  # 经纬度聚类
    x = df[["lng", "lat"]].values
    y = getKMeans(x, avg)
    data = df[["cust_code", "street"]].values
    data = np.c_[data, y, x]
    columns = ["cust_code", "street", "aggregate_id", "lng", "lat"]
    df = pd.DataFrame(data=data, columns=columns)
    return y, df


def streetKM(df, avg):  # 经纬度+街道哑变量聚类
    columns_dummy = ["lng", "lat"]
    x = df[columns_dummy].values
    df_dummy = pd.get_dummies(df[["street"]], columns=["street"])
    columns_dummy = df_dummy.columns.tolist()
    x = np.c_[x, df_dummy.values]  # X包含lng、lat和street的dummies
    x = StandardScaler().fit_transform(x)
    y = getKMeans(x, avg)
    data = df[["cust_code", "street"]].values
    data = np.c_[data, y, x]  # 附带X，为第三层聚类备用
    columns = ["cust_code", "street", "aggregate_id", "lng", "lat"]
    columns.extend(columns_dummy)
    df = pd.DataFrame(data=data, columns=columns)
    return y, df


def streetGrp(df):  # 依据街道分组
    streets = df["street"].values
    df["aggregate_id"] = df["street"]
    df = df[["cust_code", "street", "aggregate_id", "lng", "lat"]]
    return streets, df


def locationAgg(df, avg):
    x = df[["lng", "lat"]].values
    y = getAggCluster(x, avg)
    data = df[["cust_code", "street"]].values
    data = np.c_[data, y, x]
    columns = ["cust_code", "street", "aggregate_id", "lng", "lat"]
    df = pd.DataFrame(data=data, columns=columns)
    return y, df


def distanceCalc(lng1, lat1, lng2, lat2):
    R = 6373.0
    dLng = radians(lng2) - radians(lng1)
    dLat = radians(lat2) - radians(lat1)
    a = (sin(dLat/2))**2 + cos(lat1) * cos(lat2) * (sin(dLng/2))**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c  # kilometer


def groupDensity(n, r):
    if n <= 5:
        d = n / 100
    elif r == 0:
        d = 1000 * n
    else:
        d = float(n) / r
    return d


def getClusterInfo(df):  # 获取cluster的中心经纬度和半径
    columns = df.columns.tolist()
    columns.extend(["cluster_center_lng", "cluster_center_lat", "cluster_radius"])
    outputDf = pd.DataFrame(data=None, columns=columns)
    for value in set(df["cluster_id"].values):
        data = df[df["cluster_id"] == value].values
        coordinates = data[:, [1, 2]].astype(float).tolist()
        lngList = [x[0] for x in coordinates]
        latList = [x[1] for x in coordinates]
        lngList.sort()
        latList.sort()
        lngMin, lngMax = lngList[0], lngList[-1]
        latMin, latMax = latList[0], latList[-1]
        lngMid = (lngMin + lngMax) / 2
        latMid = (latMin + latMax) / 2
        radiusMax = 0
        for x in coordinates:
            radius = distanceCalc(x[0], x[1], lngMid, latMid)
            if radius > radiusMax:
                radiusMax = radius
        one = np.ones((len(data),))
        data = np.c_[data, one * lngMid, one * latMid, one * radiusMax]
        segDf = pd.DataFrame(data=data, columns=columns)
        outputDf = outputDf.append(segDf)
    return outputDf


def getTaskInfo(df):
    columns = df.columns.tolist()
    columns.extend(["task_center_lng", "task_center_lat", "task_radius", "task_size", "task_density"])
    outputDf = pd.DataFrame(data=None, columns=columns)
    for value in set(df["task_id"].values):
        data = df[df["task_id"] == value].values
        coordinates = data[:, [1, 2]].astype(float).tolist()
        size = len(coordinates)
        lngList = [x[0] for x in coordinates]
        latList = [x[1] for x in coordinates]
        lngList.sort()
        latList.sort()
        lngMin, lngMax = lngList[0], lngList[-1]
        latMin, latMax = latList[0], latList[-1]
        lngMid = (lngMin + lngMax) / 2
        latMid = (latMin + latMax) / 2
        radiusMax = 0
        for x in coordinates:
            radius = distanceCalc(x[0], x[1], lngMid, latMid)
            if radius > radiusMax:
                radiusMax = radius
        density = groupDensity(size, radiusMax)
        one = np.ones((len(data),))
        data = np.c_[data, one * lngMid, one * latMid, one * radiusMax, one * size, one * density]
        segDf = pd.DataFrame(data=data, columns=columns)
        outputDf = outputDf.append(segDf)
    return outputDf
