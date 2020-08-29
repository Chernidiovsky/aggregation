import pandas as pd
import numpy as np
from utils import reformat, locationKM, locationAgg, streetGrp, streetKM, getClusterInfo, getTaskInfo, revStreet


class ShopsAggregation:
    def __init__(self, inputDf, clusterSize, taskSize, method):
        """

        inputDf: 输入df，所有店铺的经纬度、街道名称
        clusterSize: cluster大组里面的包含多少个店铺
        taskSize: task小组里面的包含多少个店铺
        method: 聚类使用哪种方式，
                'street'表示第2、3层聚类使用街道名称
                'streetKM'表示第2、3层聚类使用经纬度+街道哑变量的KMean
                'agg'表示第2、3层聚类分别使用经纬度的KMean和凝聚聚类
        """
        columns = ["cust_code", "lng", "lat", "street"]
        try:
            inputDf = inputDf[[columns]]
        except:
            raise Exception("invalid columns.")
        if len(inputDf) == 0:
            raise Exception("inputDf is empty.")
        self.inputDf = pd.DataFrame(data=[reformat(r) for r in inputDf.values.tolist()], columns=columns)
        self.outputCol = ["cust_code", "lng", "lat", "street", "cluster_id", "task_id"]
        self.outputDf = pd.DataFrame(data=None, columns=self.outputCol)
        self.clusterSize = float(clusterSize)
        self.taskSize = float(taskSize)
        self.method = method
        
    def aggregate(self):
        i = 1  # task分组序号
        
        # 第一层 分出cluster
        yClusters, clustersDf = locationKM(self.inputDf, self.clusterSize)
        for cluster in set(yClusters):
            clusterDf = clustersDf[clustersDf["aggregate_id"] == cluster]
            
            # 第二层 分出task
            if self.method == "street":
                yTasks, tasksDf = streetGrp(clusterDf)
            elif self.method == "streetKM":
                yTasks, tasksDf = streetKM(clusterDf, self.taskSize)
            else:
                yTasks, tasksDf = locationKM(clusterDf, self.taskSize)
            for task in set(yTasks):
                taskDf = tasksDf[tasksDf["aggregate_id"] == task]
                if len(taskDf.values) > self.taskSize:
                    
                    # 第三层 对task组内店铺数超量的再次划分
                    if self.method == "street":
                        yMainTasks, mainTasksDf = streetGrp(taskDf)
                    elif self.method == "streetKM":
                        yMainTasks, mainTasksDf = streetKM(taskDf, self.taskSize)
                    else:
                        yMainTasks, mainTasksDf = locationAgg(taskDf, self.taskSize)
                    for mainTask in set(yMainTasks):
                        mainTaskDf = mainTasksDf[mainTasksDf["aggregate_id"] == mainTask]
                        data = mainTaskDf[["cust_code", "lng", "lat", "street"]].values
                        ones = np.ones((len(data),))
                        clusterOnes = (ones * cluster)
                        taskOnes = (ones * i)
                        data = np.c_[data, clusterOnes, taskOnes]
                        mainTaskDf = pd.DataFrame(data=data, columns=self.outputCol)
                        self.outputDf = self.outputDf.append(mainTaskDf)
                        i += 1
                else:
                    data = taskDf[["cust_code", "lng", "lat", "street"]].values
                    ones = np.ones((len(data),))
                    clusterOnes = (ones * cluster)
                    taskOnes = (ones * i)
                    data = np.c_[data, clusterOnes, taskOnes]
                    taskDf = pd.DataFrame(data=data, columns=self.outputCol)
                    self.outputDf = self.outputDf.append(taskDf)
                    i += 1

    def overlapCut(self):  # 重叠点、密集点，均匀分组
        taskId = 1
        outputDf = pd.DataFrame(data=None, columns=self.outputCol)
        for mti in set(self.outputDf["task_id"].values):
            df = self.outputDf[self.outputDf["task_id"] == mti]
            if np.std(df["lng"]) > np.std(df["lat"]):  # 根据经度、维度的std决定是横切分还是竖切分
                df = df.sort_values(by=["lng", "lat"])
            else:
                df = df.sort_values(by=["lat", "lng"])

            data = df[["cust_code", "lng", "lat", "street", "cluster_id"]].values
            mtiLen = float(len(data))
            if mtiLen > self.taskSize:
                grpSize = np.ceil(mtiLen / np.ceil(mtiLen / self.taskSize))
                grpIndex = 0
                temp = []
                for i in range(int(mtiLen)):
                    if grpIndex < np.floor(i / grpSize):
                        grpIndex = np.floor(i / grpSize)
                        taskId += 1
                    temp.append(taskId)
                data = np.c_[data, np.array(temp)]
                taskId += 1
            else:
                ones = np.ones((len(df.values),))
                mainTaskId = (ones * taskId)
                data = np.c_[data, mainTaskId]
                taskId += 1
            df = pd.DataFrame(data=data, columns=self.outputCol)
            outputDf = outputDf.append(df)
        self.outputDf = outputDf

    def groupInfo(self):
        self.outputDf = getClusterInfo(self.outputDf)
        self.outputDf = getTaskInfo(self.outputDf)
        self.outputDf["street"] = self.outputDf["street"].apply(revStreet)