#!/usr/bin/python3
################################################################################
#
# Copyright (c) 2023-2026 Dawson Dean
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
################################################################################
#
# ML Experiment
#
################################################################################
import os
import sys
import math
import random
from os.path import isfile
import decimal  # For float-to-string workaround

import statistics
from scipy import stats
from scipy.stats import spearmanr
import numpy as np
#import xml.dom

import xmlTools as dxml
import tdfFile as tdf
import dataShow as DataShow
import mlJob as mlJob
import mlEngine as mlEngine
import tdfTimeFunctions as timefunc
import medGraph as MedGraph

# ROC
from sklearn import metrics
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error

# Cox Regression
import pandas as pd
#from sksurv.linear_model import CoxnetSurvivalAnalysis


NEWLINE_STR = "\n"

MIN_SEQUENCE_LENGTH_FOR_CORRELATION  = 4

g_FloatFractionInTrain = 0.80









################################################################################
#
# [UpdateOneJobFile]
#
# <><> TODO <><> Move this into mlJob once the format is finalized.
################################################################################
def UpdateOneJobFile(srcFilePathName, contentTransformList, destFilePathName):
    # Read the template file into an XML object that we can edit.
    fileH = open(srcFilePathName, "r")
    fileContentsText = fileH.read()
    fileH.close()

    # Parse the text string into am XML DOM
    jobFileXMLDOM = dxml.XMLTools_ParseStringToDOM(fileContentsText)
    if (jobFileXMLDOM is None):
        print("\n\nError. Cannot parse the file: " + srcFilePathName)
        return

    jobFileRootXMLNode = dxml.XMLTools_GetNamedElementInDocument(jobFileXMLDOM, 
                                mlJob.ROOT_ELEMENT_NAME)
    if (jobFileRootXMLNode is None):
        print("\n\nError. Invalid Job in the file: " + srcFilePathName)
        return
   
    # This loop applies each transform.
    # We often have to change several things in a single file to make a new file
    # that is internally consistent.
    for contentTransform in contentTransformList:
        xmlNode = dxml.XMLTools_GetChildNodeFromPath(jobFileRootXMLNode, 
                                                    contentTransform["xmlPath"])

        # Don't freak out if a node we want to edit is missing. There may be several transforms,
        # each changes a different type of file.
        if (xmlNode is None):
            continue
        nodeContentsStr = dxml.XMLTools_GetTextContents(xmlNode)

        # This is old code used for conditional transforms, that only change nodes with specific values.
        #oldVal = contentTransform["oldValue"].lower()
        #if ((oldVal != "") and (oldVal != nodeContentsStr.lower())):
        #   continue

        ###################
        if (contentTransform["op"].lower() == "set"):
            nodeContentsStr = contentTransform["newValue"]
        ###################
        elif (contentTransform["op"].lower() == "modify"):
            nodeContentsStr = nodeContentsStr.replace(contentTransform["oldValue"], 
                                                    contentTransform["newValue"])
        ###################
        elif (contentTransform["op"].lower() == "append"):
            pass
        ###################
        elif (contentTransform["op"].lower() == "increment"):
            pass

        dxml.XMLTools_SetTextContents(xmlNode, nodeContentsStr)
    # End - for contentTransform in contentTransformList:

    newContentsText = jobFileXMLDOM.toprettyxml(indent="", newl="", encoding=None)
    # The prettyprinter does not end with a newline. Add one if it is necessary.
    # But, don't always add one, or else they can accumulate with each pass 
    # through this code.
    if (not newContentsText.endswith("\n")):
        newContentsText = newContentsText + "\n"

    # Write the modified file to the new location.
    # This may be the same or different than the original template we edited.
    fileH = open(destFilePathName, "w+")
    fileH.write(newContentsText)
    fileH.close()
# End - UpdateOneJobFile





################################################################################
#
# [MakeTestJobWithNewInputs]
#
################################################################################
def MakeTestJobWithNewInputs(templateFilePathName, inputStr, outputVarName, 
                            valueFilterStr, newPropName, newPropValueStr, destFilePathName):
    # Do not overwrite a lab.
    # This is tricky - but once we run a test, the program may be stopped, crashed, whaveter,
    # and restart later. Do not repeat old work, since a single experiment of N tests may
    # take a long time to run (like 1 or 2 weeks). So, to re-do an experiment, requires
    # deleting the job files and reconstructing them.
    if os.path.exists(destFilePathName):
        return
    # End - if os.path.exists(destFilePathName):

    # Build the transform list
    contentTransformList = [
        {"op": "set", "xmlPath": "Network/InputLayer/InputValues", "newValue": inputStr},
        {"op": "set", "xmlPath": "Network/ResultValue", "newValue": outputVarName},
        {"op": "set", "xmlPath": "Data/ValueFilter", "newValue": valueFilterStr},
        {"op": "set", "xmlPath": "Training/NumEpochs", "newValue": "15"}
    ]
    if ((newPropValueStr is not None) and (newPropValueStr != "")):
        contentTransformList.append({"op": "set", "xmlPath": newPropName, "newValue": newPropValueStr})

    # Use the template to make a new job file
    UpdateOneJobFile(templateFilePathName, contentTransformList, destFilePathName)
# End - MakeTestJobWithNewInputs








################################################################################
#
# [MLExperiment_RunAllJobsInDirectory]
#
################################################################################
def MLExperiment_RunAllJobsInDirectory(dirPathName, fRecursive):
    # Run each job. This ASSUMES we run every job in the directory
    fileNameList = os.listdir(dirPathName)
    # Sort alphabetically
    fileNameList = sorted(fileNameList, key=lambda s: s.lower())
    for fileName in fileNameList:
        if (fileName.lower().endswith(".jpg")):
            continue
        if (fileName.lower().startswith("skip")):
            continue

        srcFilePathName = os.path.join(dirPathName, fileName)
        if (not os.path.exists(srcFilePathName)):
            continue

        # If this is a subdirectory, then we may or may not recurse on it.
        if (not isfile(srcFilePathName)):
            if (fRecursive):
                MLExperiment_RunAllJobsInDirectory(srcFilePathName, fRecursive)

            # Whether we recursed or not, we are done with this entry.
            continue
        # End - if (not isfile(srcFilePathName)):

        print("\n========================================\n" + srcFilePathName)

        # Read the job to see if it has completed
        fRunJob = True
        jobErr, job = mlJob.MLJob_ReadExistingMLJob(srcFilePathName)
        if (mlJob.JOB_E_NO_ERROR == jobErr):
            jobStatus, _, _ = job.GetJobStatus()
            if (mlJob.MLJOB_STATUS_DONE == jobStatus):
                fRunJob = False
        # End - if (mlJob.JOB_E_NO_ERROR == jobErr):

        if (fRunJob):
            mlEngine.MLEngine_RunJob(srcFilePathName, srcFilePathName, False)
        else:
            print("    Done")
    # End - for fileName in fileNameList:
# End - MLExperiment_RunAllJobsInDirectory






################################################################################
#
# [MLExperiment_GraphAllJobsInDirectory]
#
################################################################################
def MLExperiment_GraphAllJobsInDirectory(dirPathName, resultName, srcFileList,
                                        graphTitleStr, yAxisName, graphFilePathName, 
                                        optionsDict, fRecursive):
    resultList, jobFileNameList = MLExperiment_GetResultFromAllJobsInDirectoryImpl(dirPathName, srcFileList, 
                                                            resultName, [], [], optionsDict, fRecursive)

    # Make a graph of the results from each job
    if (len(resultList) > 0):
        graphFilePathName = os.path.join(dirPathName, graphFilePathName)
        DataShow.DrawBarGraph(graphTitleStr, 
                            "Job File", jobFileNameList, 
                            yAxisName, resultList,
                            "", graphFilePathName)
    # End - if (len(resultList) > 0):
# End - MLExperiment_GraphAllJobsInDirectory






################################################################################
#
# [MLExperiment_GetResultFromAllJobsInDirectoryImpl]
#
################################################################################
def MLExperiment_GetResultFromAllJobsInDirectoryImpl(dirPathName, srcFileList, resultName, 
                                                    resultList, fileNameList, optionsDict, fRecursive):
    srcFileNameListLen = len(srcFileList)

    # Collect results from each job
    fileNameList = os.listdir(dirPathName)
    for fileName in fileNameList:
        if (fileName.lower().endswith(".jpg")):
            continue
        if (fileName.lower().startswith("skip")):
            continue
        if ((srcFileNameListLen > 0) and (fileName not in srcFileList)):
            continue

        srcFilePathName = os.path.join(dirPathName, fileName)
        if (not os.path.exists(srcFilePathName)):
            continue

        if (not isfile(srcFilePathName)):
            if (fRecursive):
                resultList, fileNameList = MLExperiment_GetResultFromAllJobsInDirectoryImpl(srcFilePathName, 
                                                                        srcFileList, resultName,
                                                                        resultList, fileNameList, 
                                                                        optionsDict, fRecursive)

            # Whether we recursed or not, we are done with this entry.
            continue
        # End - if (not isfile(srcFilePathName)):

        # Read the job
        jobErr, job = mlJob.MLJob_ReadExistingMLJob(srcFilePathName)
        if (mlJob.JOB_E_NO_ERROR != jobErr):
            print("ERROR when opening a job file: " + srcFilePathName)
            sys.exit(0)

        # Get the testing results.
        resultName = resultName.lower()
        resultVal = 0
        if (resultName == "numtraindata"):
            resultVal = job.GetNumDataPointsPerEpoch()
            #resultVal = job.GetNumSequencesTrainedPerEpoch()
        elif (resultName == "numtrainpts"):
            resultVal = job.GetNumTimelinesTrainedPerEpoch()
        elif (resultName == "numtestdata"):
            resultVal = job.GetNumSequencesTested(-1)
        elif (resultName == "numtestwithin10"):
            numSequencesTested = job.GetNumSequencesTested(-1)
            testResults = job.GetTestResults(-1)
            totalNumAccurate = testResults["NumCorrectPredictions"] + testResults["NumPredictionsWithin2Percent"] + testResults["NumPredictionsWithin5Percent"] + testResults["NumPredictionsWithin10Percent"]
            if (numSequencesTested > 0):
                percentAccurate = float(totalNumAccurate) / float(numSequencesTested)
            else:
                percentAccurate = 0.0
            percentAccurate = percentAccurate * 100.0
            resultVal = round(percentAccurate)


        resultList.append(resultVal)
        # For readability (so the names don't overlap) make every other name 1-line lower
        if ((len(fileNameList) % 2) == 0):
            fileNameList.append(fileName)
        else:
            fileNameList.append("\n" + fileName)
    # End - for fileName in fileNameList:

    return resultList, fileNameList
# End - MLExperiment_GetResultFromAllJobsInDirectoryImpl







################################################################################
#
# [MLExperiment_RunJobsWithDifferentLR]
#
# Try a template job with different LR values.
################################################################################
def MLExperiment_RunJobsWithDifferentLR(labDirPathName,
                                        jobTemplateFilePathName,
                                        jobInputVariablesStr,
                                        outputVarName,
                                        valueFilterStr):
    newLRName = "Training/LearningRate"
    #MLExperiment_StartExperiment(labDirPathName)

    # Workaround for avoiding scientific notation when converting small floats to a string.
    ctx = decimal.Context()
    ctx.prec = 20

    # Now make a separate job for each test.
    experimentNum = 0
    LRList = [0.00001, 0.00005, 0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5, 10, 50]
    for currentLR in LRList:
        lrStr = format(ctx.create_decimal(repr(currentLR)), 'f')

        testJobFilePath = labDirPathName + outputVarName + "_test" + str(experimentNum) + ".txt"

        MakeTestJobWithNewInputs(jobTemplateFilePathName, jobInputVariablesStr, outputVarName, 
                                valueFilterStr, newLRName, lrStr, testJobFilePath)

        experimentNum += 1
    # End - for currentLR in LRList

    # Run each job. This ASSUMES we run every job in the directory
    MLExperiment_RunAllJobsInDirectory(labDirPathName, False)
# End - MLExperiment_RunJobsWithDifferentLR






################################################################################
# [ImportanceDictionarySortFunction]
################################################################################
def ImportanceDictionarySortFunction(dictItem):
    val = dictItem['av']
    if (math.isnan(val)):
        return 0 

    return abs(val)
# End - ImportanceDictionarySortFunction




################################################################################
# [SortFunction]
################################################################################
def SortFunction(item):
    if (math.isnan(item[1])):
        return 0 
    return abs(item[1])
# End - SortFunction




################################################################################
#
# [MakeNInputsToSingleOutputBarGraph]
#
################################################################################
def MakeNInputsToSingleOutputBarGraph(sortedList, outputVarname, numImportantVariables, 
                                    relationName, barGraphFilePathName):
    xValueList = []
    yValueList = []

    for entry in sortedList:
        inputName = entry[0]
        coeffFloat = round(entry[1], 4)
        yValueList.append(coeffFloat)
        if ((len(xValueList) % 2) == 0):
            xValueList.append(inputName)
        else:
            xValueList.append("\n" + inputName)

        if (len(xValueList) >= numImportantVariables):
            break
    # End for entry in sortedList:

    if (len(xValueList) <= 0):
        return

    # Make the bar graph
    graphTitleStr = relationName + " with " + outputVarname + " (Top " + str(len(xValueList)) + " of " + str(len(sortedList)) + ")"
    DataShow.DrawBarGraph(graphTitleStr,
                          " ", xValueList, 
                          relationName, yValueList, 
                          "", barGraphFilePathName)
# End - MakeNInputsToSingleOutputBarGraph





#####################################################
#
# [GetCorrelationBetweenTwoVars]
#
#####################################################
def GetCorrelationBetweenTwoVars(
                    tdfFilePathName, 
                    valueName1, 
                    valueName2,
                    criteriaStr,
                    minDaysInCriteria,
                    heterogenousTimelineResultFileInfo,
                    avgOfHomogenousTimelineResultFileInfo):
    listOfAllCorrelations = []

    fFoundIt, criteriaVarName, criteriaRelationID, criteriaValue1, criteriaValue2 = tdf.TDF_ParseCriteriaString(criteriaStr)
    # It is OK for fFoundIt to be false. That just means no criteria apply.
    # if (not fFoundIt): - print("Dont Panic Dude!")

    # It is possible we already found this correlation on a previous instance
    # of this program that crashed. In this case, we are running on a restarted
    # process, so do not waste time recomputing work that is already done.
    # Look for this pair in the result file
    foundIt1, heterogenousResultStr = heterogenousTimelineResultFileInfo.GetEdge(valueName1, valueName2)
    foundIt2, avgHomogenousResultStr = avgOfHomogenousTimelineResultFileInfo.GetEdge(valueName1, valueName2)
    if ((foundIt1) and (foundIt2)):
        return
    # End - if (foundIt)

    # Get information about the requested variables. This splits
    # complicated name values like "eGFR[-30]" into a name and an 
    # offset, like "eGFR" and "-30"
    functionObject1 = None
    functionObject2 = None
    labInfo1, nameStem1, valueOffset1, _, _, functionName1 = tdf.TDF_ParseOneVariableName(valueName1)
    if (labInfo1 is None):
        print("!Error! GetCorrelationBetweenTwoVars Cannot parse variable: " + valueName1)
        return
    labInfo2, nameStem2, valueOffset2, _, _, functionName2 = tdf.TDF_ParseOneVariableName(valueName2)
    if (labInfo2 is None):
        print("!Error! GetCorrelationBetweenTwoVars Cannot parse variable: " + valueName2)
        return
    if (functionName1 != ""):
        functionObject1 = timefunc.CreateTimeValueFunction(functionName1, tdf.TDF_TIME_GRANULARITY_DAYS, nameStem1)
        if (functionObject1 is None):
            print("\n\n\nERROR!! GetCorrelationBetweenTwoVars Undefined function1: " + functionName1)
            sys.exit(0)
            return
    if (functionName2 != ""):
        functionObject2 = timefunc.CreateTimeValueFunction(functionName2, tdf.TDF_TIME_GRANULARITY_DAYS, nameStem2)
        if (functionObject2 is None):
            print("\n\n\nERROR!! GetCorrelationBetweenTwoVars Undefined function2: " + functionName2)
            sys.exit(0)
            return

    var1Type = tdf.TDF_GetVariableType(nameStem1)
    var2Type = tdf.TDF_GetVariableType(nameStem2)

    # Open the file
    tdfFile = tdf.TDF_CreateTDFFileReader(tdfFilePathName, valueName1, valueName2, [ criteriaVarName ])
    if (tdfFile is None):
        return

    # Iterate over every patient to build a list of values.
    # These lists will span patients, so they are useful for boolean values
    # that are always true for one patient and never true for a different patient.
    list1 = []
    list2 = []
    fFoundTimeline = tdfFile.GotoFirstTimeline()
    while (fFoundTimeline):
        currentList1, currentList2 = tdfFile.GetSyncedPairOfValueListsForCurrentTimeline(
                                                    nameStem1, valueOffset1, functionObject1,
                                                    nameStem2, valueOffset2, functionObject2,
                                                    criteriaVarName, criteriaRelationID, criteriaValue1, criteriaValue2,
                                                    minDaysInCriteria)

        # There are 2 ways to combine results across different timelines
        # 1. Make 1 long list of variables - that spans across timelines, then find a correlation between 
        #   the 2 heterogenous lists
        # 2. Make a separate list of variables for each timeline, find a correlation for each timeline, 
        #   and then average the correlations for all timelines
        if (len(currentList1) > 0):
            try:
                # For Boolean, we can use the Point-biserial correlation coefficient.
                if ((var1Type == tdf.TDF_DATA_TYPE_BOOL) 
                        or (var2Type == tdf.TDF_DATA_TYPE_BOOL)):
                    correlation, _ = stats.pointbiserialr(list1, list2)
                else:
                    correlation, _ = spearmanr(list1, list2)
                if (not math.isnan(correlation)):
                    listOfAllCorrelations.append(correlation)
            except Exception:
                pass

            # Build up the lists that span all timelines
            list1.extend(currentList1)
            list2.extend(currentList2)
        # End - if (len(currentList1) > 0):

        fFoundTimeline = tdfFile.GotoNextTimeline()
    # End - while (fFoundTimeline):

    tdfFile.Shutdown()


    # We are done searching the entire file. 
    # If we were combining the lists of all patients, then get the correlation
    # for the total aggregate list now.
    correlationAcrossDifferentTimelines = 0
    if (len(list1) > MIN_SEQUENCE_LENGTH_FOR_CORRELATION):
        try:
            # For Boolean, we can use the Point-biserial correlation coefficient.
            if ((var1Type == tdf.TDF_DATA_TYPE_BOOL) 
                    or (var2Type == tdf.TDF_DATA_TYPE_BOOL)):
                correlationAcrossDifferentTimelines, _ = stats.pointbiserialr(list1, list2)
            else:
                correlationAcrossDifferentTimelines, _ = spearmanr(list1, list2)
        except Exception:
            correlationAcrossDifferentTimelines = 0
    # End - if (len(list1) > MIN_SEQUENCE_LENGTH_FOR_CORRELATION):

    if (not math.isnan(correlationAcrossDifferentTimelines)):
        heterogenousTimelineResultFileInfo.AppendEdge(valueName1, valueName2, str(correlationAcrossDifferentTimelines))


    # Get the average of correlations within single timelines.
    avgOfHomogenousTimelineCorrelations = 0
    if (len(listOfAllCorrelations) > 0):
        avgOfHomogenousTimelineCorrelations = sum(listOfAllCorrelations) / len(listOfAllCorrelations)
    if (not math.isnan(avgOfHomogenousTimelineCorrelations)):
        avgOfHomogenousTimelineResultFileInfo.AppendEdge(valueName1, valueName2, str(avgOfHomogenousTimelineCorrelations))
# End - GetCorrelationBetweenTwoVars





################################################################################
#
# [GetAccuracyForSingleInputAndOutputPair]
#
################################################################################
def GetAccuracyForSingleInputAndOutputPair(fullInputName, outputName, 
                            requirePropertyNameList, requirePropertyRelationList, requirePropertyValueList, 
                            tdfFilePathName, 
                            resultFilePathName):
    NumTimelines = 0
    numTrainDataSetsFound = 0
    numTestDataSetsFound = 0
    numDataSetsFound = 0

    resultFileInfo = MedGraph.MedGraphFile(resultFilePathName)
    # It is possible we already found this correlation on a previous instance
    # of this program that crashed. In this case, we are running on a restarted
    # process, so do not waste time recomputing work that is already done.
    # Look for this pair in the result file
    foundIt, resultStr = resultFileInfo.GetEdge(fullInputName, outputName)
    if (foundIt):
        return resultStr
    # End - if (foundIt):

    # Get information about the requested variables. This splits
    # complicated name values like "eGFR[-30]" into a name and an 
    # offset, like "eGFR" and "-30"
    inputLabInfo, inputNameStem, inputValueOffset, _, _, inputFunctionName = tdf.TDF_ParseOneVariableName(fullInputName)
    if (inputLabInfo is None):
        print("GetAccuracyForSingleInputAndOutputPair Error! Cannot parse variable: " + fullInputName)
        sys.exit(0)

    outputLabInfo, outputNameStem, outputValueOffset, _, _, outputFunctionName = tdf.TDF_ParseOneVariableName(outputName)
    if (outputLabInfo is None):
        print("GetAccuracyForSingleInputAndOutputPair Error! Cannot parse variable: " + outputName)
        sys.exit(0)

    inputFunctionObject = None
    if (inputFunctionName != ""):
        inputFunctionObject = timefunc.CreateTimeValueFunction(inputFunctionName, tdf.TDF_TIME_GRANULARITY_DAYS, inputNameStem)
        if (inputFunctionObject is None):
            print("GetAccuracyForSingleInputAndOutputPair Error! Undefined function: " + inputFunctionName)
            sys.exit(0)

    outputFunctionObject = None
    if (outputFunctionName != ""):
        outputFunctionObject = timefunc.CreateTimeValueFunction(outputFunctionName, tdf.TDF_TIME_GRANULARITY_DAYS, outputName)
        if (outputFunctionObject is None):
            print("GetAccuracyForSingleInputAndOutputPair Error! Undefined function: " + outputFunctionName)
            sys.exit(0)


    #print("Accuracy between " + fullInputName + " and " + outputName)
    srcTDF = tdf.TDF_CreateTDFFileReader(tdfFilePathName, fullInputName, outputName, requirePropertyNameList)

    totalTrainInputList = []
    totalTrainOutputList = []
    totalTestInputList = []
    totalTestOutputList = []

    # Iterate over every patient
    fFoundTimeline = srcTDF.GotoFirstTimeline()
    while (fFoundTimeline):
        NumTimelines += 1

        # Get a list of marker values
        inputList, outputList = srcTDF.GetSyncedPairOfValueListsForCurrentTimeline(
                                        inputNameStem, 
                                        inputValueOffset, 
                                        inputFunctionObject, 
                                        outputNameStem, 
                                        outputValueOffset, 
                                        outputFunctionObject,
                                        requirePropertyNameList,
                                        requirePropertyRelationList,
                                        requirePropertyValueList)

        if ((len(inputList) > 0) and (len(outputList) > 0)):
            if (random.random() <= g_FloatFractionInTrain):
                totalTrainInputList.extend(inputList)
                totalTrainOutputList.extend(outputList)
                numTrainDataSetsFound += 1
            else:
                totalTestInputList.extend(inputList)
                totalTestOutputList.extend(outputList)
                numTestDataSetsFound += 1

            numDataSetsFound += 1
        # End - if ((len(inputList) > 0) and (len(inputList) > 0)):

        fFoundTimeline = srcTDF.GotoNextTimeline()
    # End - while (fFoundTimeline):

    srcTDF.Shutdown() 

    # Use Linear Regression when mapping inputs to a continuous output.
    # Use Logistic regression when mapping inputs to a Boolean or class output
    score = 0
    if ((len(totalTrainInputList) == 0) or (len(totalTrainOutputList) == 0)
            or (len(totalTestInputList) == 0) or (len(totalTestOutputList) == 0)):
        score = 0
    ###################################################
    elif ((outputLabInfo['dataType'] == tdf.TDF_DATA_TYPE_INT) or (outputLabInfo['dataType'] == tdf.TDF_DATA_TYPE_FLOAT)):
        # Convert inputs to numpy.
        # LinearRegression.fit() takes 2 inputs of shape (n_samples, n_features)
        #   trainInputArray is a 2D Matrix with 1 column where each row has a single value
        #   trainOutputArray is also a 2-D matrix
        trainInputArray = np.array(totalTrainInputList).reshape(-1, 1)
        trainOutputArray = np.array(totalTrainOutputList).reshape(-1, 1)
        try:
            regressModel = LinearRegression()
        except Exception:
            print("GetAccuracyForSingleInputAndOutputPair Error! LinearRegression.fit() failed")
        regressModel.fit(trainInputArray, trainOutputArray)
        testInputArray = np.array(totalTestInputList).reshape(-1, 1)
        testOutputArray = np.array(totalTestOutputList).reshape(-1, 1)
        predictedTestOutput = regressModel.predict(testInputArray)  # [::, 1]
        score = mean_squared_error(testOutputArray, predictedTestOutput, squared=False)
    ###################################################
    elif (outputLabInfo['dataType'] == tdf.TDF_DATA_TYPE_BOOL):
        # Convert inputs to numpy.
        # LinearRegression.fit() takes inputs of shape (n_samples, n_features) and (n_samples)
        #   trainInputArray is a 2D Matrix with 1 column where each row has a single value
        #   trainOutputArray is a 1-D vector
        trainInputArray = np.array(totalTrainInputList).reshape(-1, 1)
        trainOutputArray = np.array(totalTrainOutputList)

        regressModel = LogisticRegression()
        try:
            regressModel.fit(trainInputArray, trainOutputArray)
        except Exception:
            print("GetAccuracyForSingleInputAndOutputPair Error! LogisticRegression.fit() failed")

        # This estimates the probabilities of each output.
        # LinearRegression.predict_proba() takes input of shape (n_samples, n_features)
        # The output is of shape (n_samples, n_classes), so there is a probability for each class.
        testInputArray = np.array(totalTestInputList).reshape(-1, 1)
        testOutputArray = np.array(totalTestOutputList)
        try:
            predictedTestOutput = regressModel.predict_proba(testInputArray)
            # The predicted output is of shape (n_samples, n_features)
            # For a boolean, we only care about the probability of true
            score = metrics.roc_auc_score(testOutputArray, predictedTestOutput[:, 1])
        except Exception:
            score = 0
    ###################################################
    else:
        print("GetAccuracyForSingleInputAndOutputPair Error! Undefined function: " + outputFunctionName)
        sys.exit(0)

    # Append the result to the file.
    resultFileInfo.AppendResult(fullInputName, outputName, score)

    return str(score)
# End - GetAccuracyForSingleInputAndOutputPair







################################################################################
#
# [GetCoxScoreForAllInputsAndOneOutput]
#
# There seems to be a bug in pyspark or Pandas Data Bricks or something else
# One workaround is to downgrade pandas
#   pip install -U pandas==1.5.3
# See https://stackoverflow.com/questions/75926636/databricks-issue-while-creating-spark-data-frame-from-pandas
#
################################################################################
def GetCoxScoreForAllInputsAndOneOutput(outputName, allSimpleInputsStr, allSimpleInputsList,
                                    ReqNameList, ReqRelationList, ReqValueList, 
                                    tdfFilePathName, 
                                    resultFilePathName):
    resultLine = outputName + ":"

    # Make sure the result file name exists.
    if (not os.path.isfile(resultFilePathName)):
        fileH = open(resultFilePathName, "a")
        fileH.close()

    # It is possible we already found this correlation on a previous instance
    # of this program that crashed. In this case, we are running on a restarted
    # process, so do not waste time recomputing work that is already done.
    # Look for this pair in the result file
    with open(resultFilePathName) as fileH:
        for line in fileH:
            line = line.lstrip()
            if (line.startswith(resultLine)):
                lineParts = line.split(':')
                resultValue = "Unknown"
                if (len(lineParts) > 1):
                    resultValue = lineParts[1].rstrip()

                return resultValue
            # End - if (line.startswith(resultLine)):
        # End - for line in fileH:
    # End - with open(resultFilePathName) as fileH:


    tdfFile = tdf.TDF_CreateTDFFileReader(tdfFilePathName, allSimpleInputsStr, outputName, ReqNameList)
    tdfFile.SetConvertResultsToBools(True)
    testNumInputs = tdfFile.GetNumInputValues()

    numInputVars = len(allSimpleInputsList)
    totalInputArray = np.empty([0, numInputVars])
    totalResultArray = np.empty([0, 1], dtype=int)
    if (testNumInputs != numInputVars):
        fooList = allSimpleInputsStr.split(";")
        fooNumInputValues = len(fooList)
        print("BAIL!!!!")
        print(">> numInputVars=" + str(numInputVars))
        print(">> testNumInputs=" + str(testNumInputs))
        print(">> allSimpleInputsStr=" + str(allSimpleInputsStr))
        print(">> allSimpleInputsList=" + str(allSimpleInputsList))
        print(">> fooNumInputValues=" + str(fooNumInputValues))
        print(">> fooList=" + str(fooList))
        for index in range(numInputVars):
            print(str(index) + ":" + str(allSimpleInputsList[index]) + " - " + str(fooList[index]))
        print(str(numInputVars) + ":" + str(allSimpleInputsList[numInputVars]))
        sys.exit(0)

    # Iterate over every patient to build a list of values.
    fFoundTimeline = tdfFile.GotoFirstTimeline()
    NumTimelinesFound = 0
    while (fFoundTimeline):
        # Get the data.
        # Be Careful! Normalize all inputs so the coefficients are comparable.
        # We must assume that the inputs are scaled to be the same, say all are between 0..1 or between 0...100.
        # If we do not do this scaling, then the coefficients will have different scales.
        numReturnedDataSets, inputArray, resultArray = tdfFile.GetDataForCurrentTimeline(False,  # fAddMinibatchDimension,
                                                                        False, [])  # Count missing instances
        if (numReturnedDataSets < 1):
            fFoundTimeline = tdfFile.GotoNextTimeline()
            continue

        # <><><><>
        # ValueError: all the input array dimensions for the concatenation axis must match exactly, but along dimension 1, the array at index 0 has size 134 and the array at index 1 has size 148
        try:
            totalInputArray = np.append(totalInputArray, inputArray, axis=0)
        except Exception:
            print("Exception!")

            print(">>> numInputVars=" + str(numInputVars))
            print(">>> totalInputArray.size=" + str(totalInputArray.size))
            print(">>> len(inputArray)=" + str(len(inputArray)))
            print(">>> len(inputArray[0])=" + str(len(inputArray[0])))
            print(">>> totalInputArray.size=" + str(totalInputArray.size))
            print(">>> totalInputArray=" + str(totalInputArray))
            print(">>> inputArray=" + str(inputArray))
            sys.exit(0)

        totalResultArray = np.append(totalResultArray, resultArray)

        NumTimelinesFound += 1
        fFoundTimeline = tdfFile.GotoNextTimeline()
    # End - while (fFoundTimeline):

    tdfFile.Shutdown()

    # Assemble the resuls in an array of pairs
    resultListArray = []
    for resultVal in totalResultArray:
        entryList = ((resultVal != 0), 100.0)
        resultListArray.append(entryList)
    # End - for resultVal in totalResultArray:

    if (len(resultListArray) > 0):
        # Assemble the inputs into a Pandas dataframe
        # This stackoverflow answer seems to be the best source.
        # https://stackoverflow.com/questions/68869020/valueerror-y-must-be-a-structured-array-with-the-first-field-being-a-binary-cla
        resultNPArray = np.array(resultListArray, dtype=[('Status', '?'), ('Survival_in_days', '<f8')])
        inputsDataFrame = pd.DataFrame(totalInputArray, columns=allSimpleInputsList)

        #estimator = CoxPHSurvivalAnalysis()
        #estimator = CoxnetSurvivalAnalysis()
        #estimator.fit(inputsDataFrame, resultNPArray)

        # The relative risk exp(β) can be:
        #   >1 (or β>0) for an increased risk of event (death).
        #   <1 (or β<0) for a reduced risk of event.
        numInputVars = len(allSimpleInputsList)
        coefficientList = estimator.coef_
        coeffStr = ""
        for inputVar, coeff in zip(allSimpleInputsList, coefficientList):
            coeffStr = coeffStr + inputVar + "=" + str(coeff) + ","
        # End - for inputVar in allSimpleInputsList:
        # Remove the last comma
        coeffStr = coeffStr[:-1]
    # End - if (len(resultListArray) > 0):
    else:
        coeffStr = ""

    # Append the result to the file.
    resultLine = resultLine + coeffStr + NEWLINE_STR
    fileH = open(resultFilePathName, "a")
    fileH.write(resultLine)
    fileH.close()

    return coeffStr
# End - GetCoxScoreForAllInputsAndOneOutput








#####################################################
#
# [GetStatsForList]
#
#####################################################
def GetStatsForList(valueList):
    # Compute the mean, which is the average of the values.
    # Make sure to treat these as floats to avoid truncation or rounding errors.
    #avgValue = 0
    refAvgValue = 0
    listLen = len(valueList)
    if (listLen > 0):
        #avgValue = float(sum(valueList)) / listLen
        refAvgValue = statistics.mean(valueList)
    #print("Derived avgValue=" + str(avgValue))
    #print("Reference refAvgValue=" + str(refAvgValue))

    # Next, compute the variance.
    # This is a measure of how far spread out the numbers are.
    # Intuitively, this is the average distance from members of the set and the mean.
    # This uses the "Sample Variance" where avgValue is the sample mean, not the
    # mean of some superset "population" from which the sample is drawn.
    # As a result, we divide by listLen-1, but if we used the "population mean" then
    # we would divide by listLen
    #variance = sum((x - avgValue) ** 2 for x in valueList) / listLen
    refVariance = np.var(valueList)
    #print("Derived variance=" + str(variance))
    #print("Reference variance=" + str(refVariance))

    # Standard deviation is simply the sqrt of the Variance
    #stdDev = math.sqrt(variance)
    refStdDev = np.std(valueList)
    #print("Derived stdDev=" + str(stdDev))
    #print("Reference stdDev=" + str(refStdDev))

    return listLen, refAvgValue, refVariance, refStdDev
# End - GetStatsForList



