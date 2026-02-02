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
# GroupingFile
#
# This reads and writes named groups. 
# 
# There is no assumptions about ordering for the rows. Each pair is a separate line
# that is appended to the end of the file. This makes updates fast, since it just
# appends a single line to the file.
#
################################################################################
import os
import sys
#import math
#import random
#from os.path import isfile
#import decimal  # For float-to-string workaround
from datetime import datetime
import uuid as UUID
import copy
import shutil

import xml.dom
#import xml.dom.minidom
#from xml.dom.minidom import parseString
#from xml.dom.minidom import getDOMImplementation

import xmlTools as dxml
#import tdfFile as tdf
import dataShow as DataShow
import medHistogram as MedHistogram
#import timeValueMatrix as TVMatrixLib


#------------------------------------------------
# File Syntax
#
# This is an XML file with the following sections
#------------------------------------------------

GROUPINGFILE_FILE_DOC_ELEMENT_NAME                   = "GroupingFile"
GROUPINGFILE_FILE_HEAD_ELEMENT_NAME                  = "Head"
GROUPINGFILE_FILE_GROUPLIST_ELEMENT_NAME             = "Groups"

GROUPINGFILE_FILE_HEADER_UUID_ELEMENT_NAME           = "UUID"
GROUPINGFILE_FILE_HEADER_DERIVEDFROM_ELEMENT_NAME    = "DerivedFrom"
GROUPINGFILE_FILE_HEADER_DESC_ELEMENT_NAME           = "Description"
GROUPINGFILE_FILE_HEADER_CREATED_ELEMENT_NAME        = "Created"
GROUPINGFILE_FILE_HEADER_PADDING_ELEMENT_NAME        = "Padding"

# These are used for parsing, so they are case-normalized.
GROUPINGFILE_FILE_LOWERCASE_HEAD_OPEN_ELEMENT        = "<head>"
GROUPINGFILE_FILE_LOWERCASE_HEAD_CLOSE_ELEMENT       = "</head>"
GROUPINGFILE_FILE_LOWERCASE_DOC_CLOSE_ELEMENT        = "</groupingfile>"
GROUPINGFILE_FILE_LOWERCASE_GROUPS_OPEN_ELEMENT      = "<groups>"
GROUPINGFILE_FILE_LOWERCASE_GROUPS_CLOSE_ELEMENT     = "</groups>"

NEWLINE_STR = "\n"
VALUE1_VALUE2_SEPARATOR_CHAR = "~"

# The names of sections
GROUPINGFILE_FILE_SECTION_NONE_FILE_EMPTY         = -2
GROUPINGFILE_FILE_SECTION_NONE_FILE_COMPLETE      = -1
GROUPINGFILE_FILE_SECTION_HEADER                  = 0
GROUPINGFILE_FILE_SECTION_NONE                    = 1
GROUPINGFILE_FILE_SECTION_GROUPS                  = 2


g_GroupingFileHeaderPaddingStr = "\"____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\""



#------------------------------------------------
# These are the ops to make a filtered list from an original source list.
#------------------------------------------------
GROUPINGFILE_DERIVED_FILE_OP_MIN_GROUP_SIZE    = "minGroupSize"






################################################################################
#
# Class GroupingFile
#
################################################################################
class GroupingFile():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, filePathname):
        self.filePathName = filePathname
        self.CurrentSectionInFile = GROUPINGFILE_FILE_SECTION_NONE_FILE_EMPTY

        self.fileHeaderStr = ""
        self.fileUUID = str(UUID.uuid4())
        self.derivedFromFileUUID = ""
        self.createDateStr = ""
        self.descriptionStr = ""

        self.MainDict = {}
        self.fFileIsRead = False
        
        if (filePathname != ""):
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
    # [GroupingFile::WriteHeader]
    #
    #####################################################
    def WriteHeader(self, fileH):
        fileH.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + NEWLINE_STR)
        fileH.write("<" + GROUPINGFILE_FILE_DOC_ELEMENT_NAME + " version=\"0.1\" xmlns=\"http://www.dawsondean.com/ns/MedGroupList/\">" + NEWLINE_STR)
        fileH.write(NEWLINE_STR)

        fileH.write("<" + GROUPINGFILE_FILE_HEAD_ELEMENT_NAME + ">" + NEWLINE_STR)

        fileH.write("    <" + GROUPINGFILE_FILE_HEADER_UUID_ELEMENT_NAME + ">" + self.fileUUID 
                    + "</" + GROUPINGFILE_FILE_HEADER_UUID_ELEMENT_NAME + ">" + NEWLINE_STR)

        if (self.derivedFromFileUUID != ""):
            fileH.write("    <" + GROUPINGFILE_FILE_HEADER_DERIVEDFROM_ELEMENT_NAME + ">" + self.derivedFromFileUUID 
                        + "</" + GROUPINGFILE_FILE_HEADER_DERIVEDFROM_ELEMENT_NAME + ">" + NEWLINE_STR)

        fileH.write("    <" + GROUPINGFILE_FILE_HEADER_DESC_ELEMENT_NAME + ">" + self.descriptionStr 
                    + "</" + GROUPINGFILE_FILE_HEADER_DESC_ELEMENT_NAME + ">" + NEWLINE_STR)    

        if (self.createDateStr != ""):
            fileH.write("    <" + GROUPINGFILE_FILE_HEADER_CREATED_ELEMENT_NAME + ">" + self.createDateStr 
                    + "</" + GROUPINGFILE_FILE_HEADER_CREATED_ELEMENT_NAME + ">" + NEWLINE_STR)
        else:
            fileH.write("    <" + GROUPINGFILE_FILE_HEADER_CREATED_ELEMENT_NAME + ">" + datetime.today().strftime('%b-%d-%Y') + " "
                    + datetime.today().strftime('%H:%M') + "</" + GROUPINGFILE_FILE_HEADER_CREATED_ELEMENT_NAME + ">" + NEWLINE_STR)

        fileH.write("    <" + GROUPINGFILE_FILE_HEADER_PADDING_ELEMENT_NAME + ">" + g_GroupingFileHeaderPaddingStr 
                    + "</" + GROUPINGFILE_FILE_HEADER_PADDING_ELEMENT_NAME + ">" + NEWLINE_STR)

        fileH.write("</" + GROUPINGFILE_FILE_HEAD_ELEMENT_NAME + ">" + NEWLINE_STR)    
    # End of WriteHeader




    #####################################################
    #
    # [GroupingFile::WriteFooter]
    #
    # This closes a file. It is NOT atomic, but close to it.
    # Once this procedure returns, the file may remain open but
    # the data on disk should record that the action completed.
    #####################################################
    def WriteFooter(self, fileH):
        fileH.write("</" + GROUPINGFILE_FILE_DOC_ELEMENT_NAME + ">" + NEWLINE_STR + NEWLINE_STR + NEWLINE_STR)
        fileH.flush()
        self.CurrentSectionInFile = GROUPINGFILE_FILE_SECTION_NONE_FILE_COMPLETE
    # End of WriteFooter





    #####################################################
    #
    # [GroupingFile::WriteStartSection]
    #
    # Start a new section of the file
    # It is NOT atomic, but close to it. Once this procedure 
    # returns, the file may remain open but the data on disk
    #should record that the action completed.
    #####################################################
    def WriteStartSection(self, fileH, sectionID):
        if (GROUPINGFILE_FILE_SECTION_GROUPS == sectionID):
            fileH.write("<" + GROUPINGFILE_FILE_GROUPLIST_ELEMENT_NAME + ">" + NEWLINE_STR)
            fileH.flush()
            self.CurrentSectionInFile = GROUPINGFILE_FILE_SECTION_GROUPS
    # End of WriteStartSection




    #####################################################
    #
    # [GroupingFile::WriteStopSection]
    #
    # Close and Commit a new section of the file
    # It is NOT atomic, but close to it. Once this procedure 
    # returns, the file may remain open but the data on disk
    #should record that the action completed.
    #####################################################
    def WriteStopSection(self, fileH, sectionID):
        if (GROUPINGFILE_FILE_SECTION_GROUPS == sectionID):
            fileH.write("<" + GROUPINGFILE_FILE_GROUPLIST_ELEMENT_NAME + ">" + NEWLINE_STR)
            fileH.flush()
            self.CurrentSectionInFile = GROUPINGFILE_FILE_SECTION_NONE
    # End of WriteStopSection




    #####################################################
    #
    # [WriteToFile]
    #
    #####################################################
    def WriteToFile(self, newFilePath):
        # Open the dest file
        self.filePathName = newFilePath
        try:
            os.remove(newFilePath)
        except Exception:
            pass
        try:
            fileH = open(self.filePathName, "a+")
        except Exception:
            print("Error from opening Covar file. File=" + self.filePathName)
            return
            
        # Write a new fixed header to the dest file
        self.WriteHeader(fileH)
        self.WriteStartSection(fileH, GROUPINGFILE_FILE_SECTION_GROUPS)

        # Each iteration writes one group
        for _, (groupName, memberList) in enumerate(self.MainDict.items()):
            groupStr = str(groupName) + "::"
            for memberName in memberList:
                groupStr = groupStr + memberName + ","
            groupStr = groupStr[:-1]                
            fileH.write(groupStr + NEWLINE_STR)
        # End - while for _, (inputName, valueStr) in enumerate(self.MainDict.items()):

        self.WriteStopSection(fileH, GROUPINGFILE_FILE_SECTION_GROUPS)
        self.WriteFooter(fileH)
        fileH.close()
    # End - WriteToFile





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
            fileH.close()

        ###################
        # Open the file.
        try:
            #fileH = open(self.filePathName, 'rb') 
            fileH = open(self.filePathName, 'r') 
        except Exception:
            print("Error from opening Covar file. File=" + self.filePathName)
            return

        # Go to the start of the header
        startSectionLine = self.ReadFileSectionStart(fileH)
        if (self.CurrentSectionInFile != GROUPINGFILE_FILE_SECTION_HEADER):
            return
        self.fileHeaderStr = startSectionLine

        ####################
        # Read the file header
        self.ReadHeader(fileH)

        ####################
        # Read the next section start
        _ = self.ReadFileSectionStart(fileH)
        if (self.CurrentSectionInFile == GROUPINGFILE_FILE_SECTION_GROUPS):
            self.ReadFileGroupsSection(fileH)
            self.CurrentSectionInFile = GROUPINGFILE_FILE_SECTION_NONE

        fileH.close()
        self.fFileIsRead = True
    # End - ReadFile





    #####################################################
    # [ReadHeader]
    #####################################################
    def ReadHeader(self, fileH):
        # Warning! self.fileHeaderStr was initialized by our caller

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
            if (testStr == GROUPINGFILE_FILE_LOWERCASE_HEAD_CLOSE_ELEMENT):
                self.fileHeaderStr += currentLine
                self.CurrentSectionInFile = GROUPINGFILE_FILE_SECTION_NONE
                break
            elif (testStr == GROUPINGFILE_FILE_LOWERCASE_DOC_CLOSE_ELEMENT):
                self.CurrentSectionInFile = GROUPINGFILE_FILE_SECTION_NONE_FILE_COMPLETE
                break
            elif (testStr == GROUPINGFILE_FILE_LOWERCASE_GROUPS_OPEN_ELEMENT):
                self.CurrentSectionInFile = GROUPINGFILE_FILE_SECTION_GROUPS
                break
            else:
                self.fileHeaderStr += currentLine
        # End - while True

        headerXMLDOM = dxml.XMLTools_ParseStringToDOM(self.fileHeaderStr)
        if (headerXMLDOM is None):
            print("ReadHeader. Error from parsing string: [" + self.fileHeaderStr + "]")

        headXMLNode = dxml.XMLTools_GetNamedElementInDocument(headerXMLDOM, "Head")
        if (headXMLNode is None):
            print("ReadHeader. Head elements is missing: [" + self.fileHeaderStr + "]")

        self.fileUUID = dxml.XMLTools_GetChildNodeTextAsStr(headXMLNode, GROUPINGFILE_FILE_HEADER_UUID_ELEMENT_NAME, "")
        self.derivedFromFileUUID = dxml.XMLTools_GetChildNodeTextAsStr(headXMLNode, GROUPINGFILE_FILE_HEADER_DERIVEDFROM_ELEMENT_NAME, "")
        self.createDateStr = dxml.XMLTools_GetChildNodeTextAsStr(headXMLNode, GROUPINGFILE_FILE_HEADER_CREATED_ELEMENT_NAME, "")
        self.descriptionStr = dxml.XMLTools_GetChildNodeTextAsStr(headXMLNode, GROUPINGFILE_FILE_HEADER_DESC_ELEMENT_NAME, "")
    # End - ReadHeader






    #####################################################
    # [ReadFileSectionStart]
    #####################################################
    def ReadFileSectionStart(self, fileH):
        startLine = ""

        ####################
        # Read to the next section start
        self.CurrentSectionInFile = GROUPINGFILE_FILE_SECTION_NONE
        while True: 
            # Get next line from file 
            try:
                currentLine = fileH.readline() 
            except Exception:
                print("Error from reading MedGroupList file")
                break

            # Quit if we hit the end of the file.
            if (currentLine == ""):
                break

            # Check for the start of a section
            testStr = currentLine.rstrip().lstrip().lower()
            if (testStr == GROUPINGFILE_FILE_LOWERCASE_HEAD_OPEN_ELEMENT):
                startLine = currentLine
                self.CurrentSectionInFile = GROUPINGFILE_FILE_SECTION_HEADER
                break
            elif (testStr == GROUPINGFILE_FILE_LOWERCASE_GROUPS_OPEN_ELEMENT):
                startLine = currentLine
                self.CurrentSectionInFile = GROUPINGFILE_FILE_SECTION_GROUPS
                break
        # End - Read the next section start

        return startLine
    # End - ReadFileSectionStart







    #####################################################
    # [ReadFileGroupsSection]
    #####################################################
    def ReadFileGroupsSection(self, fileH):
        # Each iteration reads one line of the <line> section.
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
            if (currentLine.lower() == GROUPINGFILE_FILE_LOWERCASE_GROUPS_CLOSE_ELEMENT):
                break


            lineParts = currentLine.split(':')
            if (len(lineParts) <= 2):
                continue
            groupName = lineParts[0].lstrip().rstrip()
            groupMembersListStr = lineParts[2].lstrip().rstrip()


            groupMembersList = []
            lineParts = groupMembersListStr.split(',')
            for memberName in lineParts:
                groupMembersList.append(memberName)

            # Add the value
            self.MainDict[groupName] = groupMembersList
        # End - while True
    # End - ReadFileGroupsSection




    #####################################################
    # [AddGroup]
    #####################################################
    def AddGroup(self, groupID, memberList):
        if (not self.fFileIsRead):
            self.ReadFile()

        self.MainDict[str(groupID)] = memberList
    # End - AddGroup





    #####################################################
    # MakeHistogramOfGroupSizes
    #####################################################
    def MakeHistogramOfGroupSizes(self):
        preFlight = MedHistogram.Preflight()
        for _, (groupName, memberList) in enumerate(self.MainDict.items()):
            numEntriesInSrcGroup = len(memberList)
            preFlight.AddValue(numEntriesInSrcGroup)
        # End - for _, (groupName, memberList) in enumerate(self.MainDict.items()):

        fIntType = False  # True
        fDiscardValuesOutOfRange = False
        numBuckets = 15
        histogram = MedHistogram.TDFHistogram()
        histogram.InitWithPreflight(fIntType, fDiscardValuesOutOfRange, numBuckets, preFlight)
        for _, (groupName, memberList) in enumerate(self.MainDict.items()):
            numEntriesInSrcGroup = len(memberList)
            histogram.AddValue(numEntriesInSrcGroup)
        # End - for _, (groupName, memberList) in enumerate(self.MainDict.items()):

        return histogram
    # End - MakeHistogramOfGroupSizes





    #####################################################
    # MakeDerivedGroupingFile
    #####################################################
    def MakeDerivedGroupingFile(self, srcGroupingFile, opName, thresholdNum):
        self.derivedFromFileUUID = srcGroupingFile.fileUUID
        self.descriptionStr = srcGroupingFile.descriptionStr

        # Each iteration filters one group
        for _, (groupName, memberList) in enumerate(srcGroupingFile.MainDict.items()):
            numEntriesInSrcGroup = len(memberList)
            if ((GROUPINGFILE_DERIVED_FILE_OP_MIN_GROUP_SIZE == opName) and (numEntriesInSrcGroup >= thresholdNum)):
                self.MainDict[groupName] = copy.deepcopy(memberList)
            # End - if ((GROUPINGFILE_DERIVED_FILE_OP_MIN_GROUP_SIZE == opName) and (numEntriesInSrcGroup >= threshold)):
        # End - for _, (groupName, memberList) in enumerate(self.MainDict.items()):
    # End - MakeDerivedGroupingFile






    #####################################################
    #
    # [DrawOneAverageSequence]
    #
    #####################################################
    def DrawOneAverageSequence(self, tvMatrix, memberList, 
                            minValue, maxValue, fHigherIsHealthier, 
                            lastHealthyValue, valueErrorRange, curveFilePathName):
        # Initialize a list of sequences that start at each GFR in the range we are interested in.
        dayInAvgList = [0]
        sumForDayInAvgList = [0.0]
        countForDayInAvgList = [0.0]

        # Add each member ID to the range
        for memberID in memberList:
            # This finds the list of values for this groupID, and then trims off the healthy
            # values and normalizes all days to 0.
            dayList, valueList = tvMatrix.GetSequenceValuesAfterDiseaseStarts(memberID, 
                                               fHigherIsHealthier, lastHealthyValue, valueErrorRange)
            # Skip any list that did not have sick values.
            if ((dayList is None) or (valueList is None)):
                continue

            # Add each value in the current curve to the aggregate list
            numNewValues = len(valueList)
            for index in range(numNewValues):
                currentDay = dayList[index]
                currentValue = valueList[index]

                numKnownDays = len(dayInAvgList)
                foundMatchingDay = False
                foundLaterDay = False
                for knownDayNum in range(numKnownDays):
                    if (currentDay == dayInAvgList[knownDayNum]):
                        foundMatchingDay = True
                        break
                    elif (currentDay < dayInAvgList[knownDayNum]):
                        foundLaterDay = True
                        break
                # End - for knownDayNum in range(numKnownDays):

                if (foundMatchingDay):
                    sumForDayInAvgList[knownDayNum] += currentValue
                    countForDayInAvgList[knownDayNum] += 1
                elif (foundLaterDay):
                    dayInAvgList.insert(knownDayNum, currentDay)
                    sumForDayInAvgList.insert(knownDayNum, currentValue)
                    countForDayInAvgList.insert(knownDayNum, 1)
                else:
                    dayInAvgList.append(currentDay)
                    sumForDayInAvgList.append(currentValue)
                    countForDayInAvgList.append(1)
            # End - for index in range(numNewValues):
        # End - for memberID in memberList:


        # Convert the totals and counts to averages.
        numAvgEntries = len(dayInAvgList)
        avgValList = [0.0] * numAvgEntries
        for valIndex in range(numAvgEntries):
            if (countForDayInAvgList[valIndex] > 0):
                avgValList[valIndex] = round(float(float(sumForDayInAvgList[valIndex]) / float(countForDayInAvgList[valIndex])), 1)
        # End - for valIndex in range(numAvgEntries):            


        # Draw it on curveFilePathName
        DataShow.DrawLineGraph("", "Day", dayInAvgList, "GFR", avgValList, False, curveFilePathName)
    # End - DrawOneAverageSequence







    #####################################################
    #
    # [DrawAllAverageSequences]
    #
    #####################################################
    def DrawAllAverageSequences(self, tvMatrix, 
                            minValue, maxValue, fHigherIsHealthier, 
                            lastHealthyValue, valueErrorRange,
                            curveFilePathNameDir):
        # Create a new empty directory or else empty an existing directory
        if os.path.exists(curveFilePathNameDir):
            try:
                shutil.rmtree(curveFilePathNameDir)
            except OSError as e:
                pass
        try:
            os.mkdir(curveFilePathNameDir)
        except OSError as e:
            raise Exception()            
            sys.exit(0)

        # Draw one average Curve for each group.
        # Each group is one clique of closely related sequences.
        groupNumNum = 0
        for _, (groupName, memberList) in enumerate(self.MainDict.items()):
            curveFilePathName = curveFilePathNameDir + str(groupNumNum) + ".jpg"
            self.DrawOneAverageSequence(tvMatrix, memberList, 
                                        minValue, maxValue, fHigherIsHealthier, 
                                        lastHealthyValue, valueErrorRange,
                                        curveFilePathName)

            groupNumNum += 1
        # End - for _, (groupName, memberList) in enumerate(self.MainDict.items()):
    # End - DrawAllAverageSequences


# End - class GroupingFile







################################################################################
# 
################################################################################
def CreateDerivedGroupingFile(srcGroupingFile, opName, thresholdNum):
    groupFile = GroupingFile("")
    groupFile.MakeDerivedGroupingFile(srcGroupingFile, opName, thresholdNum)
    return groupFile
# End - CreateDerivedGroupingFile




################################################################################
#
################################################################################
def CreateEmptyGroupingFile(filePath):
    try:
        os.remove(filePath) 
    except Exception:
        pass

    groupFile = GroupingFile(filePath)
    return groupFile
# End - CreateEmptyGroupingFile




################################################################################
#
################################################################################
def OpenExistingGroupingFile(filePath):
    groupFile = GroupingFile(filePath)
    return groupFile
# End - OpenExistingGroupingFile



