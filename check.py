# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from clusteringFunc import districtClustering
from csvToKml import getKML


def setColor(inList):
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple',
              'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
    set_in = set(inList)
    outList = []
    for x in inList:
        for setId, i in zip(set_in, range(len(set_in))):
            if x == setId:
                outList.append(colors[i % len(colors)])
    return outList


outputDf = districtClustering(u"宝安区", "agg")
getKML(outputDf[["cust_code", "lng", "lat", "cluster_id"]])
clustersX = np.array(outputDf[["lng", "lat"]].values).astype(float)
clusters = np.array(outputDf["main_task_id"].values)
plt.scatter(clustersX[:, 0], clustersX[:, 1], marker='o', c=setColor(clusters), edgecolors='none')
plt.show()