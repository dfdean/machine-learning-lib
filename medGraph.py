#!/usr/bin/python3
################################################################################
#
# Copyright (c) 2025-2026 Dawson Dean
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
# MedGraphFile
#
# This reads and writes weighted directional graphs. It is used for:
#   - Covariances between lots of nodes. Each edge is a R-squared value between 2 items
#   - Word Embeddings. Each edge is a weighted relevance between two words
# 
# This is an XML file, but it may be large and written at several times. As a result,
# onht the header is XML, and most of the file is a list of edges which have the form:
#   startNodeName~stopNodeName: resultValue
#   startNodeName~stopNodeName: resultValue
#   startNodeName~stopNodeName: resultValue
#   ......
#
# There is no assumptions about ordering for the rows. Each pair is a separate line
# that is appended to the end of the file. This makes updates fast, since it just
# appends a single line to the file.
#
# The runtime state is a dict of dicts. This makes reading the file slower but
# runtime lookup faster.
################################################################################
import os
import sys
import math
from datetime import datetime
import uuid as UUID

import xmlTools as dxml
import tdfFile as tdf
import medHistogram as MedHistogram
import groupingFile as GroupingFile

#------------------------------------------------
# File Syntax
#
# This is an XML file with the following sections
#------------------------------------------------

MEDGRAPH_FILE_DOC_ELEMENT_NAME                  = "MedGraph"
MEDGRAPH_FILE_HEAD_ELEMENT_NAME                 = "Head"
MEDGRAPH_FILE_EDGES_ELEMENT_NAME                = "Edges"

MEDGRAPH_FILE_HEADER_UUID_ELEMENT_NAME          = "UUID"
MEDGRAPH_FILE_HEADER_DERIVEDFROM_ELEMENT_NAME   = "DerivedFrom"
MEDGRAPH_FILE_HEADER_DESC_ELEMENT_NAME          = "Description"
MEDGRAPH_FILE_HEADER_CREATED_ELEMENT_NAME       = "Created"
MEDGRAPH_FILE_HEADER_PADDING_ELEMENT_NAME       = "Padding"
MEDGRAPH_FILE_HEADER_THRESHOLD_NAME             = "Threshold"

# These are used for parsing, so they are case-normalized.
MEDGRAPH_FILE_LOWERCASE_HEAD_OPEN_ELEMENT       = "<head>"
MEDGRAPH_FILE_LOWERCASE_HEAD_CLOSE_ELEMENT      = "</head>"
MEDGRAPH_FILE_LOWERCASE_DOC_CLOSE_ELEMENT       = "</medgraph>"
MEDGRAPH_FILE_LOWERCASE_EDGES_OPEN_ELEMENT      = "<edges>"
MEDGRAPH_FILE_LOWERCASE_EDGES_CLOSE_ELEMENT     = "</edges>"

# The names of sections
MEDGRAPH_FILE_SECTION_NONE_FILE_EMPTY       = -2
MEDGRAPH_FILE_SECTION_NONE_FILE_COMPLETE    = -1
MEDGRAPH_FILE_SECTION_HEADER                = 0
MEDGRAPH_FILE_SECTION_NONE                  = 1
MEDGRAPH_FILE_SECTION_EDGES                 = 2

NEWLINE_STR = "\n"
VALUE1_VALUE2_SEPARATOR_CHAR = "~"

g_GraphFileHeaderPaddingStr = "\"____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\""



################################################################################
#
# Class MedGraphFile
#
# This stores simple name/value pairs for the results of a lengthy experiment.
# For example, finding all correlation values over a large data set may take up to 
# a week of CPU time. This allows intermediate values to be saved and restored
# so if a job crashes, it can resume where it left off when it is restarted.
#
# Each name is the combination of an input and output name. It stores a floating
# point number for each input/output combination.
################################################################################
class MedGraphFile():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, filePathname, derivedFromUUID):
        self.filePathName = filePathname

        self.fileHeaderStr = ""
        self.fileUUID = str(UUID.uuid4())
        self.derivedFromFileUUID = derivedFromUUID
        self.createDateStr = ""
        self.CurrentSectionInFile = MEDGRAPH_FILE_SECTION_NONE_FILE_EMPTY
        self.descriptionStr = ""
        self.thresholdValue = ""

        self.MainDict = {}
        self.fFileIsRead = False

        self.WriteBuffer = ""
        self.NumBufferedLines = 0
        self.MaxBufferedLines = 1
        
        if (self.filePathName != ""):
            self.ReadFile()
    # End -  __init__




    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return



    #####################################################
    #
    # Accessor Methods
    #
    #####################################################
    def SetDerivedFileUUID(self, newValue):
        self.derivedFromFileUUID = newValue

    def SetDescriptionStr(self, newValue):
        self.descriptionStr = newValue




    #####################################################
    #
    # [MedGraph::CheckState]
    #
    #####################################################
    def CheckState(self, tvMatrix):
        if (not self.fFileIsRead):
            self.ReadFile()

        for _, (startNodeName, rowDict) in enumerate(self.MainDict.items()):
            if (not tvMatrix.FindRowID(startNodeName)):
                print("MedGraph::CheckState Fail. Cannot find node in tvMatrix. NodeName=" + startNodeName)
                sys.exit(0)

            for _, (stopNodeName, covarStr) in enumerate(rowDict.items()):
                if (not tvMatrix.FindRowID(stopNodeName)):
                    print("MedGraph::CheckState Fail. Cannot find node in tvMatrix. NodeName=" + stopNodeName)
                    sys.exit(0)
            # End - for _, (stopNodeName, covar) in enumerate(rowDict.items()):
        # End - for _, (startNodeName, rowDict) in enumerate(self.MainDict.items()):

        print("MedGraph::CheckState Success")
    # End - CheckState




    #####################################################
    #
    # [MedGraph::WriteHeader]
    #
    #####################################################
    def WriteHeader(self, fileH):
        fileH.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + NEWLINE_STR)
        fileH.write("<" + MEDGRAPH_FILE_DOC_ELEMENT_NAME + " version=\"0.1\" xmlns=\"http://www.dawsondean.com/ns/MedGraph/\">" + NEWLINE_STR)
        fileH.write(NEWLINE_STR)

        fileH.write("<" + MEDGRAPH_FILE_HEAD_ELEMENT_NAME + ">" + NEWLINE_STR)

        fileH.write("    <" + MEDGRAPH_FILE_HEADER_UUID_ELEMENT_NAME + ">" + self.fileUUID 
                    + "</" + MEDGRAPH_FILE_HEADER_UUID_ELEMENT_NAME + ">" + NEWLINE_STR)

        if (self.derivedFromFileUUID != ""):
            fileH.write("    <" + MEDGRAPH_FILE_HEADER_DERIVEDFROM_ELEMENT_NAME + ">" + self.derivedFromFileUUID 
                        + "</" + MEDGRAPH_FILE_HEADER_DERIVEDFROM_ELEMENT_NAME + ">" + NEWLINE_STR)

        fileH.write("    <" + MEDGRAPH_FILE_HEADER_DESC_ELEMENT_NAME + ">" + self.descriptionStr 
                    + "</" + MEDGRAPH_FILE_HEADER_DESC_ELEMENT_NAME + ">" + NEWLINE_STR)    

        if (self.thresholdValue != ""):
            fileH.write("    <" + MEDGRAPH_FILE_HEADER_THRESHOLD_NAME + ">" + self.thresholdValue 
                        + "</" + MEDGRAPH_FILE_HEADER_THRESHOLD_NAME + ">" + NEWLINE_STR)

        if (self.createDateStr != ""):
            fileH.write("    <" + MEDGRAPH_FILE_HEADER_CREATED_ELEMENT_NAME + ">" + self.createDateStr 
                    + "</" + MEDGRAPH_FILE_HEADER_CREATED_ELEMENT_NAME + ">" + NEWLINE_STR)
        else:
            fileH.write("    <" + MEDGRAPH_FILE_HEADER_CREATED_ELEMENT_NAME + ">" + datetime.today().strftime('%b-%d-%Y') + " "
                    + datetime.today().strftime('%H:%M') + "</" + MEDGRAPH_FILE_HEADER_CREATED_ELEMENT_NAME + ">" + NEWLINE_STR)

        fileH.write("    <" + MEDGRAPH_FILE_HEADER_PADDING_ELEMENT_NAME + ">" + g_GraphFileHeaderPaddingStr 
                    + "</" + MEDGRAPH_FILE_HEADER_PADDING_ELEMENT_NAME + ">" + NEWLINE_STR)

        fileH.write("</" + MEDGRAPH_FILE_HEAD_ELEMENT_NAME + ">" + NEWLINE_STR)    
    # End of WriteHeader




    #####################################################
    #
    # [MedGraph::WriteFooter]
    #
    # This closes a file. It is NOT atomic, but close to it.
    # Once this procedure returns, the file may remain open but
    # the data on disk should record that the action completed.
    #####################################################
    def WriteFooter(self, fileH):
        fileH.write("</" + MEDGRAPH_FILE_DOC_ELEMENT_NAME + ">" + NEWLINE_STR + NEWLINE_STR + NEWLINE_STR)
        fileH.flush()
        self.CurrentSectionInFile = MEDGRAPH_FILE_SECTION_NONE_FILE_COMPLETE
    # End of WriteFooter




    #####################################################
    #
    # [MedGraph::WriteStartSection]
    #
    # Start a new section of the file
    # It is NOT atomic, but close to it. Once this procedure 
    # returns, the file may remain open but the data on disk
    #should record that the action completed.
    #####################################################
    def WriteStartSection(self, fileH, sectionID):
        if (MEDGRAPH_FILE_SECTION_EDGES == sectionID):
            fileH.write("<" + MEDGRAPH_FILE_EDGES_ELEMENT_NAME + ">" + NEWLINE_STR)
            fileH.flush()
            self.CurrentSectionInFile = MEDGRAPH_FILE_SECTION_EDGES
    # End of WriteStartSection




    #####################################################
    #
    # [MedGraph::WriteStopSection]
    #
    # Close and Commit a new section of the file
    # It is NOT atomic, but close to it. Once this procedure 
    # returns, the file may remain open but the data on disk
    #should record that the action completed.
    #####################################################
    def WriteStopSection(self, fileH, sectionID):
        if (MEDGRAPH_FILE_SECTION_EDGES == sectionID):
            fileH.write("</" + MEDGRAPH_FILE_EDGES_ELEMENT_NAME + ">" + NEWLINE_STR)
            fileH.flush()
            self.CurrentSectionInFile = MEDGRAPH_FILE_SECTION_NONE
    # End of WriteStopSection





    #####################################################
    # [ReadFile]
    #####################################################
    def ReadFile(self):
        self.MainDict = {}
        self.fFileIsRead = False

        # Make sure the result file name exists.
        if (not os.path.isfile(self.filePathName)):
            fileH = open(self.filePathName, "a")
            self.WriteHeader(fileH)
            self.WriteStartSection(fileH, MEDGRAPH_FILE_SECTION_EDGES)
            fileH.close()

        ###################
        # Open the file.
        try:
            fileH = open(self.filePathName, 'r') 
        except Exception:
            print("Error from opening Covar file. File=" + self.filePathName)
            return

        # Go to the start of the header
        startSectionLine = self.ReadFileSectionStart(fileH)
        if (self.CurrentSectionInFile != MEDGRAPH_FILE_SECTION_HEADER):
            return
        self.fileHeaderStr = startSectionLine

        ####################
        # Read the file header and parse its fields. This may affect how we parse
        # the body.
        self.ReadHeader(fileH)

        ####################
        # Read the next section start
        _ = self.ReadFileSectionStart(fileH)
        if (self.CurrentSectionInFile == MEDGRAPH_FILE_SECTION_EDGES):
            self.ReadFileEdgesSection(fileH)
            self.CurrentSectionInFile = MEDGRAPH_FILE_SECTION_NONE

        fileH.close()
        self.fFileIsRead = True
    # End - ReadFile






    #####################################################
    # [ReadHeader]
    #####################################################
    def ReadHeader(self, fileH):
        # Warning! self.fileHeaderStr was already initialized when we found the header.

        ####################
        # Read the file header as a series of text lines and create a single
        # large text string for just the header. Stop at the body
        while True: 
            # Get next line from file 
            try:
                currentLine = fileH.readline() 
            except Exception:
                print("Error from reading Lab file. lineNum=" + str(self.lineNum))
                continue

            # Quit if we hit the end of the file.
            if (currentLine == ""):
                break

            # Check for the end of the header or file.
            testStr = currentLine.lstrip().rstrip().lower()
            if (testStr == MEDGRAPH_FILE_LOWERCASE_HEAD_CLOSE_ELEMENT):
                self.fileHeaderStr += currentLine
                self.CurrentSectionInFile = MEDGRAPH_FILE_SECTION_NONE
                break
            elif (testStr == MEDGRAPH_FILE_LOWERCASE_DOC_CLOSE_ELEMENT):
                self.CurrentSectionInFile = MEDGRAPH_FILE_SECTION_NONE_FILE_COMPLETE
                break
            elif (testStr == MEDGRAPH_FILE_LOWERCASE_EDGES_OPEN_ELEMENT):
                self.CurrentSectionInFile = MEDGRAPH_FILE_SECTION_EDGES
                break
            else:
                self.fileHeaderStr += currentLine
        # End - while True


        headerXMLDOM = dxml.XMLTools_ParseStringToDOM(self.fileHeaderStr)
        if (headerXMLDOM is None):
            print("ReadHeader. Error from parsing string:")
            return

        headXMLNode = dxml.XMLTools_GetNamedElementInDocument(headerXMLDOM, MEDGRAPH_FILE_HEAD_ELEMENT_NAME)
        if (headXMLNode is None):
            print("ReadHeader. Head elements is missing: [" + self.fileHeaderStr + "]")
            return

        self.fileUUID = dxml.XMLTools_GetChildNodeTextAsStr(headXMLNode, MEDGRAPH_FILE_HEADER_UUID_ELEMENT_NAME, "")
        self.derivedFromFileUUID = dxml.XMLTools_GetChildNodeTextAsStr(headXMLNode, MEDGRAPH_FILE_HEADER_DERIVEDFROM_ELEMENT_NAME, "")
    # End - ReadHeader







    #####################################################
    # [ReadFileSectionStart]
    #####################################################
    def ReadFileSectionStart(self, fileH):
        startLine = ""

        ####################
        # Read to the next section start
        self.CurrentSectionInFile = MEDGRAPH_FILE_SECTION_NONE
        while True: 
            # Get next line from file 
            try:
                currentLine = fileH.readline() 
            except Exception:
                print("Error from reading MedGraph file")
                break

            # Quit if we hit the end of the file.
            if (currentLine == ""):
                break

            # Check for the start of a section
            testStr = currentLine.rstrip().lstrip().lower()
            if (testStr == MEDGRAPH_FILE_LOWERCASE_HEAD_OPEN_ELEMENT):
                startLine = currentLine
                self.CurrentSectionInFile = MEDGRAPH_FILE_SECTION_HEADER
                break
            elif (testStr == MEDGRAPH_FILE_LOWERCASE_EDGES_OPEN_ELEMENT):
                startLine = currentLine
                self.CurrentSectionInFile = MEDGRAPH_FILE_SECTION_EDGES
                break
        # End - Read the next section start

        return startLine
    # End - ReadFileSectionStart






    #####################################################
    # [ReadFileEdgesSection]
    #####################################################
    def ReadFileEdgesSection(self, fileH):
        # Each iteration reads one line of the <Edges> section.
        while True: 
            # Get next line from file 
            try:
                currentLine = fileH.readline() 
            except Exception:
                print("Error from reading Lab file.")
                continue

            # Quit if we hit the end of the file.
            if (currentLine == ""):
                break
            currentLine = currentLine.lstrip().rstrip()

            # Skip blank lines and comments
            if ((currentLine == "") or (currentLine.startswith("#"))):
                continue

            # Check for the end of the section.
            if (currentLine.lower() == MEDGRAPH_FILE_LOWERCASE_EDGES_CLOSE_ELEMENT):
                break

            lineParts = currentLine.split(':')
            if (len(lineParts) <= 1):
                continue
            nodeNameListStr = lineParts[0].lstrip().rstrip()
            valueStr = lineParts[1].lstrip().rstrip()

            nodeNamesArray = nodeNameListStr.split('~')
            if (len(nodeNamesArray) <= 1):
                continue
            startNodeName = nodeNamesArray[0].lstrip().rstrip()
            stopNodeName = nodeNamesArray[1].lstrip().rstrip()

            # Add the value to a new row
            if (startNodeName in self.MainDict):
                rowDict = self.MainDict[startNodeName]
            else:
                rowDict = {}

            rowDict[stopNodeName] = valueStr
            self.MainDict[startNodeName] = rowDict
        # End - while True
    # End - ReadFileEdgesSection







    #####################################################
    #
    # [ImportAndFix]
    #
    # OK, a bit embarassing here. This is used to repair a file
    # that was incorrectly written without having to regenerate 
    # all of the data. It is used for fixing bugs.
    # This should not have to be used during normal operation.
    #####################################################
    def ImportAndFix(self, newFilePath, oldFilePath):
        self.MainDict = {}
        self.fFileIsRead = False

        # Open the src file
        try:
            srcFileH = open(oldFilePath, 'r') 
        except Exception:
            print("Error from opening Covar file. File=" + oldFilePath)
            return

        # Open the dest file
        self.filePathName = newFilePath
        try:
            os.remove(newFilePath)
        except Exception:
            pass
        try:
            destFileH = open(self.filePathName, "a+")
        except Exception:
            print("Error from opening Covar file. File=" + oldFilePath)
            return
            
        # Go to the start of the header in the src file
        _ = self.ReadFileSectionStart(srcFileH)
        if (self.CurrentSectionInFile != MEDGRAPH_FILE_SECTION_HEADER):
            return

        ####################
        # Read the file header as a series of text lines and create a single
        # large text string for just the header. Stop at the body
        while True: 
            # Get next line from file 
            try:
                currentLine = srcFileH.readline() 
            except Exception:
                print("Error from reading Lab file. lineNum=" + str(self.lineNum))
                continue

            # Quit if we hit the end of the file.
            if (currentLine == ""):
                break

            # Check for the end of the header or file.
            testStr = currentLine.lstrip().rstrip().lower()
            if (testStr == MEDGRAPH_FILE_LOWERCASE_HEAD_CLOSE_ELEMENT):
                self.CurrentSectionInFile = MEDGRAPH_FILE_SECTION_NONE
                break
            elif (testStr == MEDGRAPH_FILE_LOWERCASE_DOC_CLOSE_ELEMENT):
                self.CurrentSectionInFile = MEDGRAPH_FILE_SECTION_NONE_FILE_COMPLETE
                break
            elif (testStr == MEDGRAPH_FILE_LOWERCASE_EDGES_OPEN_ELEMENT):
                self.CurrentSectionInFile = MEDGRAPH_FILE_SECTION_EDGES
                break
        # End - while True

        # Fix the header
        self.createDateStr = "Jan-01-2026 13:00"
        self.descriptionStr = "Covariance Between All Rows in CKDTVMatrixFilteredTimelineLengthOver10.txt"

        # Write a new fixed header to the dest file
        self.WriteHeader(destFileH)
        self.WriteStartSection(destFileH, MEDGRAPH_FILE_SECTION_EDGES)

        # Each iteration reads one line of the <Edges> section.
        while True: 
            # Get next line from file 
            try:
                currentLine = srcFileH.readline() 
            except Exception:
                print("Error from reading Lab file.")
                continue

            # Quit if we hit the end of the file.
            if (currentLine == ""):
                break

            destFileH.write(currentLine)
        # End - while True

        self.WriteStopSection(destFileH, MEDGRAPH_FILE_SECTION_EDGES)
        self.WriteFooter(destFileH)
        destFileH.close()
    # End - ImportAndFix






    #####################################################
    #
    # [AppendEdge]
    #
    #####################################################
    def AppendEdge(self, startNodeName, stopNodeName, resultValue):
        # Add a value to the persistent state.
        resultLine = startNodeName + VALUE1_VALUE2_SEPARATOR_CHAR + stopNodeName + ":" + str(resultValue) + NEWLINE_STR
        self.WriteBuffer += resultLine
        self.NumBufferedLines += 1
        if (self.NumBufferedLines >= self.MaxBufferedLines):
            self.Flush()

        # Add the value to a row in the runtime state
        if (startNodeName in self.MainDict):
            rowDict = self.MainDict[startNodeName]
        else:
            rowDict = {}
        rowDict[stopNodeName] = str(resultValue)
        self.MainDict[startNodeName] = rowDict
    # End - AppendEdge






    #####################################################
    #
    # [Flush]
    #
    #####################################################
    def Flush(self):
        if ((self.WriteBuffer == "") or (self.NumBufferedLines <= 0)):
            return

        destFileH = open(self.filePathName, "a")
        if (destFileH is None):
            print("Flush Error opening dest file: " + self.filePathName)
            return

        destFileH.write(self.WriteBuffer)
        destFileH.flush()
        destFileH.close()

        self.WriteBuffer = ""
        self.NumBufferedLines = 0
    # End - Flush








    #####################################################
    #
    # [GetEdge]
    #
    #####################################################
    def GetEdge(self, startNodeName, stopNodeName):
        if (not self.fFileIsRead):
            self.ReadFile()

        # Otherwise, look for the name pair in the loaded dictionary
        if (startNodeName not in self.MainDict):
            return False, ""

        rowDict = self.MainDict[startNodeName]
        if (stopNodeName not in rowDict):
            return False, ""

        return True, rowDict[stopNodeName]
    # End - GetEdge





    #####################################################
    # [GetAllNodeNames]
    #####################################################
    def GetAllNodeNames(self):
        resultList = []

        if (not self.fFileIsRead):
            self.ReadFile()

        for _, (startNodeName, _) in enumerate(self.MainDict.items()):
            resultList.append(startNodeName)

        return resultList
    # End - GetAllNodeNames




    #####################################################
    # [GetAllEdgesAsDict]
    #####################################################
    def GetAllEdgesAsDict(self):
        resultList = []

        if (not self.fFileIsRead):
            self.ReadFile()

        for _, (startNodeName, rowDict) in enumerate(self.MainDict.items()):
            for _, (stopNodeName, covar) in enumerate(rowDict.items()):
                if ((covar > -2) and (covar < 2)):
                    resultList.append({'i': startNodeName, 'o': stopNodeName, 'c': covar})
            # End - for _, (stopNodeName, covar) in enumerate(rowDict.items()):
        # End - for _, (startNodeName, rowDict) in enumerate(self.MainDict.items()):

        return resultList
    # End - GetAllEdgesAsDict




    #####################################################
    #
    # [FinishWritingToFile]
    #
    #####################################################
    def FinishWritingToFile(self):
        if ((self.WriteBuffer == "") or (self.NumBufferedLines <= 0)):
            return

        destFileH = open(self.filePathName, "a")
        if (destFileH is None):
            print("FlushBufferedResultsToFile Error opening dest file: " + self.filePathName)
            return

        destFileH.write(self.WriteBuffer)
        self.WriteBuffer = ""
        self.NumBufferedLines = 0

        self.WriteStopSection(destFileH, MEDGRAPH_FILE_SECTION_EDGES)
        self.WriteFooter(destFileH)

        #destFileH.flush()
        destFileH.close()
    # End - FinishWritingToFile





    #####################################################
    # MakeHistogramOfEdgeValues
    #####################################################
    def MakeHistogramOfEdgeValues(self):
        if (not self.fFileIsRead):
            self.ReadFile()

        preFlight = MedHistogram.Preflight()
        for _, (startNodeName, rowDict) in enumerate(self.MainDict.items()):
            for _, (stopNodeName, covarStr) in enumerate(rowDict.items()):
                try:
                    covar = float(covarStr)
                except Exception:
                    continue
                if ((covar > -2) and (covar < 2)):
                    preFlight.AddValue(covar)
            # End - for _, (stopNodeName, covar) in enumerate(rowDict.items()):
        # End - for _, (startNodeName, rowDict) in enumerate(self.MainDict.items()):
                
        fIntType = False  # True
        fDiscardValuesOutOfRange = False
        numBuckets = 15
        histogram = MedHistogram.TDFHistogram()
        histogram.InitWithPreflight(fIntType, fDiscardValuesOutOfRange, numBuckets, preFlight)

        for _, (startNodeName, rowDict) in enumerate(self.MainDict.items()):
            for _, (stopNodeName, covarStr) in enumerate(rowDict.items()):
                try:
                    covar = float(covarStr)
                except Exception:
                    continue
                if ((covar > -2) and (covar < 2)):
                    histogram.AddValue(covar)
            # End - for _, (stopNodeName, covar) in enumerate(rowDict.items()):
        # End - for _, (startNodeName, rowDict) in enumerate(self.MainDict.items()):


        return histogram
    # End - MakeHistogramOfEdgeValues





    #####################################################
    #
    # GroupNodesIntoCliques
    #
    # NOTE: correlations range between -1..0..1 so they may be negative.
    # We do not use abs(), since we want things that closely correlate, not
    # are negative predictors and negatively correlate.
    #####################################################
    def GroupNodesIntoCliques(self, thresholdForGroupAssociation, minCliqueSize, dictFilePathName):
        currentGroups = {}
        nextGroupID = 1

        if (not self.fFileIsRead):
            self.ReadFile()

        # Look at every node in the list and add it to one group.
        matchingGroupID = -100
        matchingGroupEdgeWeight = 0
        for _, (startNodeName, rowDict) in enumerate(self.MainDict.items()):
            # Examine each current group to see if there is one close to this node
            for _, (groupID, groupInfo) in enumerate(currentGroups.items()):
                groupMembers = groupInfo['m']

                # Skip empty groups. This should not happen
                if (len(groupMembers) <= 0):
                    print("ACK. Found empty group.")
                    continue

                # The new node has to be close to all members in the group.
                # Otherwise, you add nodes that are close to a node on the periphery of the group but
                # not the rest of the growp and it slowly expands to cover the whole graph.
                fNodeBelongsInCurrentGroup = True
                weakestMatchWeight = 0
                for memberNodeName in groupMembers:
                    fFoundEdge, edgeWeightStr = self.GetEdge(startNodeName, memberNodeName)
                    if (not fFoundEdge):
                        fFoundEdge, edgeWeightStr = self.GetEdge(memberNodeName, startNodeName)

                    if (not fFoundEdge):
                        print("GroupNodesIntoCliques Error. No edge found.")
                        fNodeBelongsInCurrentGroup = False
                        break

                    try:
                        edgeWeightFloat = float(edgeWeightStr)
                    except Exception:
                        print("GroupNodesIntoCliques Error. Invalid Edge Weight.")
                        fNodeBelongsInCurrentGroup = False
                        break

                    if ((edgeWeightFloat == tdf.TDF_INVALID_VALUE) or (math.isnan(edgeWeightFloat))):
                        continue

                    if (edgeWeightFloat < thresholdForGroupAssociation):
                        fNodeBelongsInCurrentGroup = False
                        break

                    if ((weakestMatchWeight == 0) or (edgeWeightFloat < weakestMatchWeight)):
                        weakestMatchWeight = edgeWeightFloat
                # End - for memberNodeName in groupMembers:

                # If there is a match, then stop looking for more groups.
                # One node may be close to two separate groups, BUT the other nodes in those 
                # groups are not close to each other or else they would not have formed separate groups.
                # Really, we should pick the closest neighbor.
                if ((fNodeBelongsInCurrentGroup) and (weakestMatchWeight > 0)):
                    if ((matchingGroupEdgeWeight == 0) or (weakestMatchWeight > matchingGroupEdgeWeight)):
                        matchingGroupID = groupID
                        matchingGroupEdgeWeight = weakestMatchWeight
            # End - for _, (groupID, groupInfo) in enumerate(rowDict.items()):


            # If there are no matching groups, then make a new group
            if (matchingGroupID < 0):
                newGroupMembersList = [startNodeName]
                newGroupInfo = {'id': nextGroupID, 'm': newGroupMembersList}
                currentGroups[nextGroupID] = newGroupInfo
                nextGroupID += 1
            # If there is one matching group, then add the node to this group
            else:
                groupInfo = currentGroups[matchingGroupID]
                groupMembers = groupInfo['m']
                groupMembers.append(startNodeName)
        # End - for _, (startNodeName, rowDict) in enumerate(self.MainDict.items()):


        # Make a Dict that has groupID for each node
        groupListFile = GroupingFile.CreateEmptyGroupingFile(dictFilePathName)
        for _, (groupID, groupInfo) in enumerate(currentGroups.items()):
            groupMembers = groupInfo['m']
            if (len(groupMembers) > minCliqueSize):
                groupListFile.AddGroup(groupID, groupMembers)
        # End - for _, (startNodeName, rowDict) in enumerate(self.MainDict.items()):

        groupListFile.SetDerivedFileUUID(self.fileUUID)
        groupListFile.SetDescriptionStr("All Groups")
        groupListFile.WriteToFile(dictFilePathName)

        return groupListFile
    # End - GroupNodesIntoCliques


# End - class MedGraphFile
################################################################################




#####################################################
#
#####################################################
def MedGraph_FixGraphFile(oldFilePath, newFilePath):
    newGraph = MedGraphFile("", "")
    newGraph.ImportAndFix(newFilePath, oldFilePath)
# End - MedGraph_FixGraphFile



#####################################################
#
#####################################################
def MedGraph_OpenExistingGraph(filePath, derivedFromUUID):
    graph = MedGraphFile(filePath, derivedFromUUID)
    return graph
# End - MedGraph_OpenExistingGraph





