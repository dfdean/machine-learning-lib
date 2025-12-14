#!/usr/bin/python3
################################################################################
#
# Copyright (c) 2023-2025 Dawson Dean
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
# Histograms
#
################################################################################
import os
#import sys
#import math
#import random
#from os.path import isfile
#import decimal  # For float-to-string workaround
from datetime import datetime

#import statistics
#from scipy import stats
#from scipy.stats import spearmanr
#import numpy as np

import xmlTools as dxml
import tdfFile as tdf
import dataShow as DataShow

HISTOGRAM_UNREALISTIC_LARGE_NUMBER = 1000000
HISTOGRAM_UNREALISTIC_SMALL_NUMBER = -1000000


#------------------------------------------------
# File Syntax
#
# This is an XML file with the following sections
#------------------------------------------------

MEDHISTOGRAM_FILE_HEADER_HEAD_ELEMENT_NAME      = "Head"

MEDHISTOGRAM_FILE_DATA_ELEMENT_NAME             = "BucketList"

MEDHISTOGRAM_FILE_BUCKET_ELEMENT_NAME           = "Bucket"
MEDHISTOGRAM_FILE_BUCKET_ELEMENT_ID_ATTR        = "Id"
MEDHISTOGRAM_FILE_BUCKET_ELEMENT_Weight_ATTR    = "Wt"

NEWLINE_STR = "\n"
MEDHISTOGRAM_FILE_COMMENT_LINE_PREFIX   = "#"







################################################################################
#
# This preflights the data before setting up a histogram.
# It does a full pass over the data to find min/max and averages so we can make
# a better histogram.
################################################################################
class Preflight():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self):
        self.varType = tdf.TDF_DATA_TYPE_INT
        self.numVals = 0
        self.minVal = HISTOGRAM_UNREALISTIC_LARGE_NUMBER
        self.maxVal = HISTOGRAM_UNREALISTIC_SMALL_NUMBER
        self.TotalValues = 0
    # End -  __init__

    #####################################################
    # [Preflight::
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return

    #####################################################
    #
    # [Preflight::AddValue]
    #
    #####################################################
    def AddValue(self, value):
        self.minVal = min(value, self.minVal)
        self.maxVal = max(value, self.maxVal)
        self.numVals += 1
        self.TotalValues += value
    # End - AddValue

    #####################################################
    # [TDFHistogram::GetNumValues]
    #####################################################
    def GetNumValues(self):
        return self.numVals
    # End - GetNumValues()

    #####################################################
    # [TDFHistogram::GetMinMax]
    #####################################################
    def GetMinMax(self):
        return self.minVal, self.maxVal
    # End - GetMinMax()

    #####################################################
    # [TDFHistogram::GetAverageVal]
    #####################################################
    def GetAverageVal(self):
        if (self.numVals <= 0):
            return 0.0

        return self.TotalValues / self.numVals
    # End - GetAverageVal()


    #####################################################
    # [TDFHistogram::Print]
    #####################################################
    def Print(self):
        print("    Count=" + str(self.numVals))
        print("    Min=" + str(self.minVal))
        print("    Max=" + str(self.maxVal))
        print("    Average=" + str(self.GetAverageVal()))
    # End - Print()


# End - class Preflight








################################################################################
#
#
################################################################################
class TDFHistogram():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self):
        self.varName = ""
        self.varType = tdf.TDF_DATA_TYPE_INT
        self.DiscardValuesOutOfRange = False

        self.numVals = 0
        self.minVal = HISTOGRAM_UNREALISTIC_LARGE_NUMBER
        self.maxVal = HISTOGRAM_UNREALISTIC_SMALL_NUMBER

        self.numClasses = 1
        self.ClassSize = 1

        self.minObservedValue = HISTOGRAM_UNREALISTIC_LARGE_NUMBER
        self.maxObservedValue = HISTOGRAM_UNREALISTIC_SMALL_NUMBER
        self.totalValue = 0

        self.histogramBucketWeights = []
        self.histogramBucketCounts = []
    # End -  __init__



    #####################################################
    # [TDFHistogram::
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return



    #####################################################
    #
    # [TDFHistogram::InitEx]
    #
    #####################################################
    def InitEx(self, fIntType, fDiscardValuesOutOfRange, numBuckets, minVal, maxVal):
        self.varName = ""
        if (fIntType):
            self.varType = tdf.TDF_DATA_TYPE_INT
        else:
            self.varType = tdf.TDF_DATA_TYPE_FLOAT

        self.DiscardValuesOutOfRange = fDiscardValuesOutOfRange
        self.numClasses = numBuckets
        self.minVal = minVal
        self.maxVal = maxVal

        if (self.varType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
            valRange = float(self.maxVal - self.minVal)
            self.ClassSize = float(valRange) / float(self.numClasses)
            # If the valueRange is 0, then the classSize must still be non-zero.
            if (self.ClassSize == 0):
                self.ClassSize = 1
        else:
            self.ClassSize = 1

        self.numVals = 0
        self.totalValue = 0
        self.histogramBucketWeights = [0] * self.numClasses        
        self.histogramBucketCounts = [0] * self.numClasses        
    # End - InitEx




    #####################################################
    #
    # [TDFHistogram::InitWithPreflight]
    #
    #####################################################
    def InitWithPreflight(self, fIntType, fDiscardValuesOutOfRange, numBuckets, preflightInfo):
        self.varName = ""
        if (fIntType):
            self.varType = tdf.TDF_DATA_TYPE_INT
        else:
            self.varType = tdf.TDF_DATA_TYPE_FLOAT

        minVal, maxVal = preflightInfo.GetMinMax()

        self.DiscardValuesOutOfRange = fDiscardValuesOutOfRange
        self.numClasses = numBuckets
        self.minVal = minVal
        self.maxVal = maxVal

        if (self.varType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
            valRange = float(self.maxVal - self.minVal)
            self.ClassSize = float(valRange) / float(self.numClasses)
            # If the valueRange is 0, then the classSize must still be non-zero.
            if (self.ClassSize == 0):
                self.ClassSize = 1
        else:
            self.ClassSize = 1

        self.numVals = 0
        self.totalValue = 0
        self.histogramBucketWeights = [0] * self.numClasses        
        self.histogramBucketCounts = [0] * self.numClasses        
    # End - InitWithPreflight





    #####################################################
    #
    # [TDFHistogram::WriteToFile]
    #
    #####################################################
    def WriteToFile(self, filePathName):
        try:
            fileH = os.remove(filePathName)
        except Exception:
            pass
        try:
            fileH = open(filePathName, "w+")
        except Exception:
            print("WriteToFile Error! Cannot open file: " + filePathName)
            return

        ###################
        # Write the header
        fileH.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + NEWLINE_STR)
        fileH.write("<MedHistogram version=\"0.1\" xmlns=\"http://www.dawsondean.com/ns/MedHistogram/\">" + NEWLINE_STR)
        fileH.write(NEWLINE_STR)
        fileH.write("<" + MEDHISTOGRAM_FILE_HEADER_HEAD_ELEMENT_NAME + ">" + NEWLINE_STR)    
        fileH.write("    <Comment>" + "" + "</Comment>" + NEWLINE_STR)
        fileH.write("    <Created>" + datetime.today().strftime('%b-%d-%Y') + " "
                + datetime.today().strftime('%H:%M') + "</Created>" + NEWLINE_STR)
        fileH.write("    <VarName>" + str(self.varName) + "</VarName>" + NEWLINE_STR)
        fileH.write("    <VarType>" + str(self.varType) + "</VarType>" + NEWLINE_STR)
        fileH.write("    <DiscardValuesOutOfRange>" + str(self.DiscardValuesOutOfRange) + "</DiscardValuesOutOfRange>" + NEWLINE_STR)
        fileH.write("    <Min>" + str(self.minVal) + "</Min>" + NEWLINE_STR)
        fileH.write("    <Max>" + str(self.maxVal) + "</Max>" + NEWLINE_STR)
        fileH.write("    <ClassSize>" + str(self.ClassSize) + "</ClassSize>" + NEWLINE_STR)
        fileH.write("    <NumClasses>" + str(self.numClasses) + "</NumClasses>" + NEWLINE_STR)
        fileH.write("    <NumVals>" + str(self.numVals) + "</NumVals>" + NEWLINE_STR)
        fileH.write("    <TotalVals>" + str(self.totalValue) + "</TotalVals>" + NEWLINE_STR)
        fileH.write("    <MinObservedValue>" + str(self.minObservedValue) + "</MinObservedValue>" + NEWLINE_STR)
        fileH.write("    <MaxObservedValue>" + str(self.maxObservedValue) + "</MaxObservedValue>" + NEWLINE_STR)
        fileH.write("</" + MEDHISTOGRAM_FILE_HEADER_HEAD_ELEMENT_NAME + ">" + NEWLINE_STR)    
        fileH.write(NEWLINE_STR)

        ###################
        # Write the body
        fileH.write("<" + MEDHISTOGRAM_FILE_DATA_ELEMENT_NAME + ">" + NEWLINE_STR)    
        for bucketNum in range(self.numClasses):
            weight = self.histogramBucketWeights[bucketNum]
            count = self.histogramBucketCounts[bucketNum]

            bucketElementStr = "    <" + MEDHISTOGRAM_FILE_BUCKET_ELEMENT_NAME
            bucketElementStr = bucketElementStr + " " + MEDHISTOGRAM_FILE_BUCKET_ELEMENT_ID_ATTR + "=\"" + str(bucketNum) + "\""
            bucketElementStr = bucketElementStr + " " + MEDHISTOGRAM_FILE_BUCKET_ELEMENT_Weight_ATTR + "=\"" + str(weight) + "\">"
            fileH.write(bucketElementStr)    

            fileH.write(str(count))    

            fileH.write("</" + MEDHISTOGRAM_FILE_BUCKET_ELEMENT_NAME + ">" + NEWLINE_STR)    
        # End - for index in range(self.numClasses):

        ###################
        # Write the footer
        fileH.write("</" + MEDHISTOGRAM_FILE_DATA_ELEMENT_NAME + ">" + NEWLINE_STR)    
        fileH.write(NEWLINE_STR + "</MedHistogram>" + NEWLINE_STR)
        fileH.write(NEWLINE_STR + NEWLINE_STR)

        fileH.close()
    # End - WriteToFile






    #####################################################
    #
    # [TDFHistogram::ReadFromFile]
    #
    #####################################################
    def ReadFromFile(self, filePathName):
        ###################
        # Open the file.
        try:
            fileH = open(filePathName, "r")
        except Exception:
            print("ReadFromFile Error! Cannot open file: " + filePathName)
            return


        # Get the first line from file. This tells us if this is a new XML file or an old text file.
        try:
            firstLine = fileH.readline()
        except Exception:
            print("Error from reading Lab file.")
            firstLine = ""

        firstLine = firstLine.lstrip().rstrip()
        if (firstLine.startswith("<?xml")):
            fileContentsStr = firstLine
            for line in fileH:
                fileContentsStr += line
            # End - for line in fileH:
            fileH.close()

            fileXMLDOM = dxml.XMLTools_ParseStringToDOM(fileContentsStr)
            if (fileXMLDOM is None):
                print("ReadFromFile. Error from parsing string:")

            self.ReadFromXMLFile(fileXMLDOM)
        else:
            self.ReadFromOldNonXMLFile(firstLine, fileH)
            fileH.close()
    # End - ReadFromFile






    #####################################################
    #
    # [TDFHistogram::ReadFromXMLFile]
    #
    #####################################################
    def ReadFromXMLFile(self, fileXMLDOM):
        headerNode = dxml.XMLTools_GetNamedElementInDocument(fileXMLDOM, MEDHISTOGRAM_FILE_HEADER_HEAD_ELEMENT_NAME)
        bucketListNode = dxml.XMLTools_GetNamedElementInDocument(fileXMLDOM, MEDHISTOGRAM_FILE_DATA_ELEMENT_NAME)
        if (headerNode is None):
            print("ReadFromXMLFile. Head elements is missing: [" + self.fileHeaderStr + "]")

        # Parse the header sections that we are aware of.
        self.DiscardValuesOutOfRange = dxml.XMLTools_GetChildNodeTextAsBool(headerNode, "DiscardValuesOutOfRange", False)
        self.varType = dxml.XMLTools_GetChildNodeTextAsInt(headerNode, "VarType", tdf.TDF_DATA_TYPE_INT)
        self.minVal = dxml.XMLTools_GetChildNodeTextAsFloat(headerNode, "Min", HISTOGRAM_UNREALISTIC_LARGE_NUMBER)
        self.maxVal = dxml.XMLTools_GetChildNodeTextAsFloat(headerNode, "Max", HISTOGRAM_UNREALISTIC_SMALL_NUMBER)
        self.numClasses = dxml.XMLTools_GetChildNodeTextAsInt(headerNode, "NumClasses", 1)
        self.InitEx((self.varType == tdf.TDF_DATA_TYPE_INT), 
                     self.DiscardValuesOutOfRange, 
                     self.numClasses, 
                     self.minVal, 
                     self.maxVal)

        # Initialize some values that may have been clobbered by the constructor method.
        self.ClassSize = dxml.XMLTools_GetChildNodeTextAsFloat(headerNode, "ClassSize", 1)
        self.minObservedValue = dxml.XMLTools_GetChildNodeTextAsFloat(headerNode, "MinObservedValue", HISTOGRAM_UNREALISTIC_LARGE_NUMBER)
        self.maxObservedValue = dxml.XMLTools_GetChildNodeTextAsFloat(headerNode, "MaxObservedValue", HISTOGRAM_UNREALISTIC_SMALL_NUMBER)        
        self.varName = dxml.XMLTools_GetChildNodeTextAsStr(headerNode, "VarName", "MissingVar")
        self.numVals = dxml.XMLTools_GetChildNodeTextAsInt(headerNode, "SumOfVals", 0)
        self.totalValue = dxml.XMLTools_GetChildNodeTextAsFloat(headerNode, "TotalVals", 0.0)
        self.Comment = dxml.XMLTools_GetChildNodeTextAsStr(headerNode, "Comment", "")

        # Now read each bucket
        bucketNode = dxml.XMLTools_GetChildNode(bucketListNode, MEDHISTOGRAM_FILE_BUCKET_ELEMENT_NAME)
        while (bucketNode is not None):
            bucketNumStr = dxml.XMLTools_GetAttribute(bucketNode, MEDHISTOGRAM_FILE_BUCKET_ELEMENT_ID_ATTR)
            weightStr = dxml.XMLTools_GetAttribute(bucketNode, MEDHISTOGRAM_FILE_BUCKET_ELEMENT_Weight_ATTR)
            countStr = dxml.XMLTools_GetTextContents(bucketNode)

            bucketNum = int(bucketNumStr.lstrip().rstrip())
            count = int(countStr.lstrip().rstrip())
            weight = float(weightStr.lstrip().rstrip())

            self.histogramBucketWeights[bucketNum] = weight
            self.histogramBucketCounts[bucketNum] = count

            bucketNode = dxml.XMLTools_GetPeerNode(bucketNode, MEDHISTOGRAM_FILE_BUCKET_ELEMENT_NAME)
        # End - while (bucketNode is not None):
    # End - ReadFromXMLFile






    #####################################################
    #
    # [TDFHistogram::ReadFromOldNonXMLFile]
    #
    #####################################################
    def ReadFromOldNonXMLFile(self, firstLine, fileH):
        lineNum = 0

        # The first line is the header, which lets 
        saveName = 0
        saveNumVals = 0
        saveTotalVals = 0
        assignmentList = firstLine.split(",")
        for assignment in assignmentList:
            words = assignment.split("=")
            if (len(words) < 2):
                continue

            propName = words[0].lstrip().rstrip()
            propValue = words[1].lstrip().rstrip()

            if (propName == "Vers"):
                continue
            elif (propName == "VarName"):
                saveName = propValue
            elif (propName == "VarType"):
                self.varType = int(propValue)
            elif (propName == "DiscardValuesOutOfRange"):
                if ((propValue == "False") or (propValue == "F")):
                    self.DiscardValuesOutOfRange = False
                else:
                    self.DiscardValuesOutOfRange = True
            elif (propName == "Min"):
                self.minVal = float(propValue)
            elif (propName == "Max"):
                self.maxVal = float(propValue)
            elif (propName == "BucketSize"):
                self.ClassSize = float(propValue)
            elif (propName == "NumClasses"):
                self.numClasses = int(propValue)
            elif (propName == "NumVals"):
                saveNumVals = int(propValue)
            elif (propName == "TotalVals"):
                saveTotalVals = int(propValue)
            elif (propName == "MaxObservedValue"):
                self.maxObservedValue = float(propValue)
            elif (propName == "MinObservedValue"):
                self.minObservedValue = float(propValue)
        # End - for assignment in assignmentList:

        self.InitEx((self.varType == tdf.TDF_DATA_TYPE_INT), 
                    self.DiscardValuesOutOfRange, 
                    self.numClasses, 
                    self.minVal, 
                    self.maxVal)
        self.varName = saveName
        self.numVals = saveNumVals
        self.totalValue = saveTotalVals


        # Now, read every other line in the file
        for line in fileH:
            line = line.lstrip().rstrip()
            words = line.split(":")
            bucketNum = int(words[0].lstrip().rstrip())
            weightCountStr = words[1].lstrip().rstrip()
            words2 = weightCountStr.split("/")
            weight = float(words2[0].lstrip().rstrip())
            count = int(words2[1].lstrip().rstrip())
            self.histogramBucketWeights[bucketNum] = weight
            self.histogramBucketCounts[bucketNum] = count

            lineNum += 1
        # End - for line in fileH:
    # End - ReadFromOldNonXMLFile




    #####################################################
    #
    # [TDFHistogram::AddValue]
    #
    #####################################################
    def AddValue(self, value):
        # Allow values less than 0, that may be common for things like velocities

        # Record what we see before we start to either ignore or clip values.
        if (value > self.maxObservedValue):
            self.maxObservedValue = value
        if (value < self.minObservedValue):
            self.minObservedValue = value

        # Optionally clip the value so it can fit in a bucket.
        if ((self.DiscardValuesOutOfRange) and ((value < self.minVal) or (value > self.maxVal))):
            return
        elif (value < self.minVal):
            value = self.minVal
        elif (value > self.maxVal):
            value = self.maxVal

        # Find which buck this value maps to
        offset = value - self.minVal
        bucketNum = round(offset / self.ClassSize)
        if (bucketNum >= self.numClasses):
            bucketNum = self.numClasses - 1

        self.numVals += 1
        self.totalValue += value
        self.histogramBucketWeights[bucketNum] += value
        self.histogramBucketCounts[bucketNum] += 1
    # End - AddValue



    #####################################################
    #
    # [TDFHistogram::AddWeightedValue]
    #
    #####################################################
    def AddWeightedValue(self, value, weight):
        # Allow values less than 0, that may be common for things like velocities

        # Record what we see before we start to either ignore or clip values.
        if (value > self.maxObservedValue):
            self.maxObservedValue = value
        if (value < self.minObservedValue):
            self.minObservedValue = value

        # Optionally clip the value so it can fit in a bucket.
        if ((self.DiscardValuesOutOfRange) and ((value < self.minVal) or (value > self.maxVal))):
            return
        elif (value < self.minVal):
            value = self.minVal
        elif (value > self.maxVal):
            value = self.maxVal

        # Find which buck this value maps to
        offset = value - self.minVal
        bucketNum = round(offset / self.ClassSize)
        if (bucketNum >= self.numClasses):
            bucketNum = self.numClasses - 1

        self.numVals += 1
        self.totalValue += value
        self.histogramBucketWeights[bucketNum] += weight
        self.histogramBucketCounts[bucketNum] += 1
    # End - AddWeightedValue



    #####################################################
    #
    # [TDFHistogram::AverageAllValues]
    #
    #####################################################
    def AverageAllValues(self):
        for bucketNum in range(self.numClasses):
            weight = self.histogramBucketWeights[bucketNum]
            count = self.histogramBucketCounts[bucketNum]

            if (count > 0):
                weight = weight / count
                count = 1
            else:
                weight = 0
                count = 0

            self.histogramBucketWeights[bucketNum] = weight
            self.histogramBucketCounts[bucketNum] = count
        # End - for index in range(self.numClasses):
    # End - AverageAllValues


    #####################################################
    # [TDFHistogram::GetNumBuckets]
    #####################################################
    def GetNumBuckets(self):
        return self.numClasses
    # End - GetNumBuckets()

    #####################################################
    # [TDFHistogram::GetBuckets]
    #####################################################
    def GetBuckets(self):
        return self.histogramBucketWeights
    # End - GetBuckets()

    #####################################################
    # [TDFHistogram::GetTotalNumVals]
    #####################################################
    def GetTotalNumVals(self):
        return self.numVals
    # End - GetTotalNumVals()

    #####################################################
    # [TDFHistogram::GetMeanValue]
    #####################################################
    def GetMeanValue(self):
        if (self.numVals <= 0):
            return 0
        return round((self.totalValue / self.numVals), 1)
    # End - GetMeanValue




    #####################################################
    #
    # [TDFHistogram::GetBucketsAsPercentages]
    #
    #####################################################
    def GetBucketsAsPercentages(self):
        resultArray = self.histogramBucketWeights

        sumOfElements = sum(resultArray)
        scaledList = [(float(x) / sumOfElements) * 100.0 for x in resultArray]
        return scaledList
    # End - GetBucketsAsPercentages()




    #####################################################
    #
    # [TDFHistogram::DrawBarGraph]
    #
    #####################################################
    def DrawBarGraph(self, graphTitleStr, xLabelStr, yLabelStr, graphFilePath):
        xAxisList = []
        for index in range(self.numClasses):
            bucketNameFloat = self.minVal + (self.ClassSize * index)
            bucketNameFloat = round(bucketNameFloat, 1)
            bucketNameStr = str(bucketNameFloat)
            if ((index % 2) == 0):
                bucketNameStr = "\n" + bucketNameStr
            xAxisList.append(bucketNameStr)
        # End - for index in range(self.numClasses)

        DataShow.DrawBarGraph(graphTitleStr, 
                        xLabelStr, xAxisList, 
                        yLabelStr, self.histogramBucketCounts, 
                        "", graphFilePath)
    # End - DrawBarGraph()



    #####################################################
    #
    # [TDFHistogram::PrintStats]
    #
    #####################################################
    def PrintStats(self):
        print("Num values: " + str(self.numVals))
        print("Mean value: " + str(self.GetMeanValue()))
        print("Max Value: " + str(self.maxObservedValue))
        print("Min Value: " + str(self.minObservedValue))
    # End - PrintStats()

# End - class TDFHistogram






##########################################################################################################
#
# [TDFHistogram_ReadFromFile]
#
##########################################################################################################
def TDFHistogram_ReadFromFile(filePathName):
    newHist = TDFHistogram()
    newHist.ReadFromFile(filePathName)
    
    return newHist
# End - TDFHistogram_ReadFromFile()


