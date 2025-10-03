#####################################################################################
# 
# Copyright (c) 2025 Dawson Dean
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#####################################################################################
#
# K-Means Clustering
#
################################################################################
import os
import sys
import math
import copy
from datetime import datetime

import statistics
from scipy import stats
from scipy.stats import spearmanr

# Normally we have to set the search path to load these.
# But, this .py file is always in the same directories as these imported modules.
import xmlTools as dxml
import tdfFile as tdf
import mlExperiment as MLExperiment
import medGraph as MedGraph




################################################################################
#
################################################################################
class KMeansCluster():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, numFeatures):
        super().__init__()

        self.numFeatures = numFeatures
        self.inputDataPoints = []
        self.trueDataPointLabels = []

        self.centroidPoints = []
        self.centroidForEachDataPoint = []
    # End -  __init__




    #####################################################
    # [KMeansCluster::
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return




    #####################################################
    #
    # [KMeansCluster::AddDataPoint]
    #
    # newDataPoint is a list of features. All data points have features
    # in the same order
    #####################################################
    def AddDataPoint(self, newDataPoint):
       self.inputDataPoints.append(newDataPoint)
    # End - AddDataPoint




    #####################################################
    #
    # [KMeansCluster::AddDataPointWithLabel]
    #
    # newDataPoint is a list of features. All data points have features
    # in the same order
    #####################################################
    def AddDataPoint(self, newDataPoint, trueDataPointLabel):
       self.inputDataPoints.append(newDataPoint)
       self.trueDataPointLabels.append(trueDataPointLabel)
    # End - AddDataPointWithLabel





    #####################################################
    #
    # [KMeansCluster::MakeClusters]
    #
    #
    # There are several clustering algorithms. See:
    #   https://scikit-learn.org/stable/modules/clustering.html
    #
    # This uses K-Means to partition a set of points into K groups.
    # Params:
    #   dataSet: This is a 2D matrix. Each row is a data point. Each column is
    #           different attribute. It has shape (numDataPoints x numFeatures)
    #   numDataPoints
    #   numFeatures
    #   numCentroids
    #
    # Alternate between:
    #   (1) assigning data points to clusters based on the current centroids 
    #   (2) chosing centroids (points which are the center of a cluster) based on the current assignment of data points to clusters
    #
    # https://stanford.edu/~cpiech/cs221/handouts/kmeans.html
    #####################################################
    def MakeClusters(self, numCentroids):
        maxIterations = 20

        numDataPoints = len(self.inputDataPoints)
        # Partition the input variables into clusters
        if (numCentroids < 0):
            numCentroids = 6

        # Get the min and max values for each feature
        minValues = [100000] * self.numFeatures
        maxValues = [-100000] * self.numFeatures
        for dataPoint in self.inputDataPoints
            for featureNum in range(self.numFeatures):
                minValues[featureNum] = min(dataPoint[featureNum], minValues[featureNum])
                maxValues[featureNum] = max(dataPoint[featureNum], maxValues[featureNum])
        # End - for dataPoint in self.inputDataPoints

        # Make random centroids
        self.centroidPoints = []
        for centroidNum in range(numCentroids):
            currentPoint = [0] * self.numFeatures
            for featureNum in range(self.numFeatures):
                currentPoint[featureNum] = random.uniform(minValues[featureNum], maxValues[featureNum])
            self.centroidPoints.append(currentPoint)
        # End - for centroidNum in range(numCentroids):
        self.centroidForEachDataPoint = [-1] * numDataPoints

        # Run the main k-means algorithm
        numIterations = 0
        while (numIterations < maxIterations):
            # Save old centroids for convergence test
            oldCentroidList = self.centroidForEachDataPoint.copy()
            numDataPointsForCentroid = [0] * numCentroids

            ########################
            # Assign labels to each datapoint based on centroids
            for pointNum in range(numDataPoints):
                currentPoint = np.array(self.inputDataPoints[pointNum])
                closestCentroid = -1
                closestDistance = 10000000
                for centroidNum in range(numCentroids):
                    currentCentroid = np.array(self.centroidPoints[centroidNum])
                    distance = np.sqrt(sum((currentPoint - currentCentroid) ** 2))
                    if ((closestCentroid == -1) or (distance < closestDistance)):
                        closestCentroid = centroidNum
                        closestDistance = distance
                # End - for centroidNum in range(numCentroids)

                self.centroidForEachDataPoint[pointNum] = closestCentroid
                numDataPointsForCentroid[closestCentroid] += 1
            # End - for pointNum in range(numDataPoints):

            # If no points changed their centroids, then we are done
            if (oldCentroidList == self.centroidForEachDataPoint):
                break


            ########################
            # Reposition the centroids to the geomtric mean of their associated points.
            # Each centroid is the geometric mean of the points associated with that centroid
            for centroidNum in range(numCentroids):
                # If a centroid is empty (no points have that centroid's label) then randomly re-initialize it.
                if ((numIterations > 0) and (numDataPointsForCentroid[centroidNum] == 0)):
                    currentPoint = [0] * self.numFeatures
                    for featureNum in range(self.numFeatures):
                        currentPoint[featureNum] = random.uniform(minValues[featureNum], maxValues[featureNum])
                    # End - for featureNum in range(self.numFeatures):
                    self.centroidPoints[centroidNum] = currentPoint
                # End - if (numDataPointsForCentroid[centroidNum] == 0):
                else:
                    productOfFeaturesForCurrentCentroid = [1] * self.numFeatures
                    numDataPointsForCurrentCentroid = 0
                    for pointNum in range(numDataPoints):
                        if (self.centroidForEachDataPoint[pointNum] == centroidNum):
                            for featureNum in range(self.numFeatures):
                                productOfFeaturesForCurrentCentroid[featureNum] *= dataSet[pointNum][featureNum]
                            numDataPointsForCurrentCentroid += 1
                        # End - if (self.centroidForEachDataPoint[pointNum] == centroidNum):
                    # End - for pointNum in range(numDataPoints):

                    if (numDataPointsForCurrentCentroid > 0):
                        for featureNum in range(self.numFeatures):
                        try:
                            self.centroidPoints[centroidNum][featureNum] = (productOfFeaturesForCurrentCentroid[featureNum] / numDataPointsForCurrentCentroid)
                        except Exception:
                            self.centroidPoints[centroidNum][featureNum] = 0
                    # End - if (numDataPointsForCurrentCentroid > 0):
            # End - for centroidNum in range(numCentroids)


            numIterations += 1
        # End - while not shouldStop(oldCentroids, centroids, iterations):
    # End - MakeClusters




    #####################################################
    #
    # [KMeansCluster::GetClusterScore]
    #
    # There are a number of scores to evaluate clustering. Many of these use true labels,
    # which are the gold standard of how items should be partitioned.
    # Many of these evaluate the patitioning algorithm, which can have variable performance
    # depending on parameters like the number of clusters. Here, I assume the algorighm is
    # "good enough" and use the metrics to pmeasure how useful each input is for partitioning.
    # See https://scikit-learn.org/stable/modules/clustering.html#clustering-performance-evaluation
    #####################################################
    def GetClusterScore(self):
        intPredictedGroups = [int(i) for i in self.trueDataPointLabels]
        score = metrics.adjusted_mutual_info_score(self.centroidForEachDataPoint, intPredictedGroups)  
        return score
    # End - GetClusterScore






    #####################################################
    #
    # [KMeansCluster::ClusterTDFFile]
    #
    #####################################################
    def ClusterTDFFile(self, tdfFilePathName, fullInputName, outputName, numCentroids):
        NumTimelines = 0
        requirePropertyNameList = []
        requirePropertyRelationList = []
        requirePropertyValueList = []

        self.numFeatures = 1
        self.inputDataPoints = []
        self.trueDataPointLabels = []

        # Get information about the requested variables. This splits
        # complicated name values like "eGFR[-30]" into a name and an 
        # offset, like "eGFR" and "-30"
        labInfo1, nameStem1, inputValueOffset, _, _, _ = tdf.TDF_ParseOneVariableName(fullInputName)
        if (labInfo1 is None):
            print("!Error! ClusterTDFFile Cannot parse variable: " + valueName1)
            return
        labInfo2, outputNameStem, outputValueOffset, _, _, _ = tdf.TDF_ParseOneVariableName(outputName)
        if (labInfo2 is None):
            print("!Error! ClusterTDFFile Cannot parse variable: " + outputName)
            return None, None
        var1Type = tdf.TDF_GetVariableType(inputNameStem)
        var2Type = tdf.TDF_GetVariableType(outputNameStem)

        srcTDF = tdf.TDF_CreateTDFFileReader(tdfFilePathName, fullInputName, outputName, requirePropertyNameList)
        fFoundTimeline = srcTDF.GotoFirstTimeline()    
        while (fFoundTimeline):
            NumTimelines += 1

            # Get a list of marker values
            currentInputList, currentOutputList = srcTDF.GetSyncedPairOfValueListsForCurrentTimeline(
                                    inputNameStem, 
                                    inputValueOffset, 
                                    None,  # inputFunctionObject, 
                                    outputNameStem, 
                                    outputValueOffset, 
                                    None,  # voutputFunctionObject,
                                    requirePropertyNameList,
                                    requirePropertyRelationList,
                                    requirePropertyValueList)
            if ((len(currentInputList) > 0) and (len(currentOutputList) > 0)):
                self.inputDataPoints.extend(currentInputList)
                self.trueDataPointLabels.extend(currentOutputList)


            fFoundTimeline = srcTDF.GotoNextTimeline()
        # End - while (fFoundTimeline):

        srcTDF.Shutdown() 

        self.MakeClusters(numCentroids)
    # End - ClusterTDFFile







    #####################################################
    #
    # [KMeansCluster::ClusterCovarFile]
    #
    # 0. Initially, there are no groups of nodes
    # 1. Sort all edges by weight in descending order, so look at the higherst covariance first
    # 2. Loop until each node is assigned to one group:
    #    2.1. Take the highest weight edge and remove it from the list of edges
    #    2.2. If neither point adjacent to the edge is in a group, then start a new group that contains those two nodes adjacent to the edge
    #    2.3. If only one point adjacent to the edge is in a group, then add the other point to that same group
    #    2.4. If both points adjacent to the edge are in different groups, then combine the groups
    #####################################################
    def ClusterCovarFile(self, MedGraphFilePathName, threshold):
        dictOfGroups = {}
        groupForEachVar = {}
        numGroups = 0

        resultFileInfo = MedGraph.MedGraphFile(MedGraphFilePathName)
        if (resultFileInfo is None):
            raise Exception()
            return

        # Get all variables. Initially each variable is not in a group.
        varList = resultFileInfo.GetAllNodeNames()
        for varName in varList:
            groupForEachVar[varName] = -1

        # Get a list of all covariances, and sort it in descending order.
        covarList = resultFileInfo.GetAllEdgesAsDict()
        sortedList = sorted(covarList, reverse=True, key=lambda d: d['c'])

        print("ClusterCovarFile List")
        for index in range(20):
            print(">> " + str(index) + ": " + str(sortedList[index]['c']))

        # Iterate the list of covariances. 
        index = 0
        while (True):
            covarInfo = sortedList[index]

            # Do not consider really weak correlations
            if (covarInfo['c'] < threshold):
                break

            var1 = covarInfo['i']
            var2 = covarInfo['o']

            # If neither point adjacent to the edge is in a group, then start a new group that contains those two nodes adjacent to the edge
            if ((groupForEachVar[var1] < 0) and (groupForEachVar[var2] < 0)):
                groupForEachVar[var1] = numGroups
                groupForEachVar[var2] = numGroups
                newGroupList = []
                newGroupList.append(var1)
                newGroupList.append(var2)
                dictOfGroups[numGroups] = newGroupList
                numGroups += 1
            # If only one point adjacent to the edge is in a group, then add the other point to that same group
            elif ((groupForEachVar[var1] > 0) and (groupForEachVar[var2] < 0)):
                groupNum = groupForEachVar[var1]
                groupList = dictOfGroups[groupNum]
                groupForEachVar[var2] = groupNum
                groupList.append(var2)
            elif ((groupForEachVar[var1] < 0) and (groupForEachVar[var2] > 0)):
                groupNum = groupForEachVar[var2]
                groupList = dictOfGroups[groupNum]
                groupForEachVar[var1] = groupNum
                groupList.append(var1)
            elif ((groupForEachVar[var1] > 0) and (groupForEachVar[var2] > 0) and (groupForEachVar[var1] == groupForEachVar[var2])):
                pass
            elif ((groupForEachVar[var1] > 0) and (groupForEachVar[var2] > 0) and (groupForEachVar[var1] != groupForEachVar[var2])):
                groupNum1 = groupForEachVar[var2]
                groupNum2 = groupForEachVar[var2]

                groupList1 = dictOfGroups[groupNum1]
                groupList2 = dictOfGroups[groupNum2]
                for group2VarName in groupList2:
                    groupForEachVar[group2VarName] = groupNum1
                    groupList1.append(group2VarName)
                # End - for group2VarName in groupList2:


            # Check if every node is assigned to a group.
            fFoundUnassignedVar = False
            for varName, groupNum in groupForEachVar.items():
                if (groupNum < 0):
                    fFoundUnassignedVar = True
                    break
            for varName, groupNum in groupForEachVar.items():

            # If every node is assigned to a group, then we are done.
            # Otherwise, keep looking.
            if (not fFoundUnassignedVar):
                break

            index += 1
        # End - while (True):
    # End - ClusterCovarFile




# End - class KMeansCluster






################################################################################
# 
################################################################################
def MakeKMeansCluster():
    newKMeans = KMeansCluster()
    return newKMeans
# End - ReadKMeansCluster



