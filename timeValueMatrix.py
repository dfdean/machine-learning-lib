####################################################################################
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
# Time-Value Matrix
#
# The file is xml file format that is designed to store time-series of data for medical 
# applications. All Elements have close tags, and comments are standard XML comments.
#
##########################################
#
# XML Syntax
# ------------
#
# <TimeValueMatrix>
#   <Head>
#   </Head>
#
#   <TimeValueMatrixData>
#       <Value> xxxxxxx </Value>
#       <Value> xxxxxxx </Value>
#       .....
#   </TimeValueMatrixData>
#
# </TimeValueMatrix>
#
################################################################################
import os
import sys
import math
import copy
from datetime import datetime
import uuid as UUID

import statistics
from scipy import stats
from scipy.stats import spearmanr

# Normally we have to set the search path to load these.
# But, this .py file is always in the same directories as these imported modules.
import xmlTools as dxml
import tdfFile as tdf
import medGraph as MedGraph
import medHistogram as MedHistogram

TVMATRIX_DEBUG = True


#------------------------------------------------
# File Syntax
#
# This is an XML file with the following sections
#------------------------------------------------
TVMATRIX_FILE_DOC_ELEMENT_NAME                  = "TimeValueMatrix"
TVMATRIX_FILE_HEAD_ELEMENT_NAME                 = "Head"
TVMATRIX_FILE_DATA_ELEMENT_NAME                 = "TimeValueMatrixData"

TVMATRIX_FILE_HEADER_UUID_ELEMENT_NAME          = "UUID"
TVMATRIX_FILE_HEADER_DERIVEDFROM_ELEMENT_NAME   = "DerivedFrom"
TVMATRIX_FILE_HEADER_DESC_ELEMENT_NAME          = "Comment"
TVMATRIX_FILE_HEADER_CREATED_ELEMENT_NAME       = "Created"
TVMATRIX_FILE_HEADER_VALUENAME_ELEMENT_NAME     = "ValueName"

# These are used for parsing, so they are case-normalized.
TVMATRIX_FILE_LOWERCASE_HEAD_ELEMENT            = "<head>"
TVMATRIX_FILE_LOWERCASE_HEAD_CLOSE_ELEMENT      = "</head>"
TVMATRIX_FILE_LOWERCASE_DATA_ELEMENT            = "<timevaluematrixdata>"
TVMATRIX_FILE_LOWERCASE_DATA_CLOSE_ELEMENT      = "</timevaluematrixdata>"

TV_MATRIX_COMMENT_LINE_PREFIX   = "#"
NEWLINE_STR = "\n"

# These separate variables in a list, or rows of variables in a sequence.
TIMEVALUE_ID_DATA_SEPARATOR     = ")"
TIMEVALUE_LIST_SEPARATOR        = ";"
TIMEVALUE_PART_SEPARATOR        = "/"



#------------------------------------------------
# These are the ops to make a filtered table from an original source table.
# They may either select matrix rows or else trim matrix rows.
#------------------------------------------------
TV_MATRIX_DERIVED_TABLE_OP_DELTA                = "delta"
TV_MATRIX_DERIVED_TABLE_OP_VELOCITY             = "velocity"
TV_MATRIX_DERIVED_TABLE_OP_TOTAL_DELTA          = "totalddela"
TV_MATRIX_DERIVED_TABLE_OP_TOTAL_VELOCITY       = "totalvelocity"
TV_MATRIX_DERIVED_TABLE_OP_DELTA_DAYS           = "deltaDays"
TV_MATRIX_DERIVED_TABLE_OP_MIN_TIMELINE_SIZE    = "minLength"
TV_MATRIX_DERIVED_TABLE_OP_MIN_TOTAL_DURATION   = "totalDuration"
TV_MATRIX_DERIVED_TABLE_OP_MIN_VALUE_AT_END     = "minValueAtEnd"
TV_MATRIX_DERIVED_TABLE_OP_MAX_VALUE_AT_END     = "maxValueAtEnd"
TV_MATRIX_DERIVED_TABLE_OP_MIN_VALUE_AT_START   = "minValueAtStart"
TV_MATRIX_DERIVED_TABLE_OP_MAX_VALUE_AT_START   = "maxValueAtStart"
TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MIN_VALUE_AT_START   = "lastBeforeMinValueAtStart"
TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MAX_VALUE_AT_START   = "lastBeforeMaxValueAtStart"
TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MIN_VALUE_AT_STRETCH_OF_90DAYS   = "lastBeforeMinValueAtStretchOf90Days"
TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MAX_VALUE_AT_STRETCH_OF_90DAYS   = "lastBeforeMaxValueAtStretchOf90Days"

TV_MATRIX_COMPARISON_LESS_THAN              = "<"
TV_MATRIX_COMPARISON_GREATER_THAN           = ">"
TV_MATRIX_COMPARISON_GREATER_THAN_EQUAL     = ">="

MIN_NUMBER_VALUES_FOR_COVARIANT = 3



#------------------------------------------------
# These are ops for MakeTimeValueMatrixFromSelectionsOfTDF
#------------------------------------------------
TV_MATRIX_TDF_SELECT_ALL                        = "All"
TV_MATRIX_TDF_SELECT_BELOW_MAX_THEN_REBOUND     = "BelowMaxThenRebound"
TV_MATRIX_TDF_SELECT_BELOW_MAX_AND_STAYOVER_MIN = "BelowMaxStayOverMin"
TV_MATRIX_TDF_SELECT_BELOW_MAX_AND_BELOW_MIN    = "BelowMaxAndBelowMin"


#------------------------------------------------
# These are ops for xxxxx
#------------------------------------------------
TV_MATRIX_TIMELINE_PROPERTY_LENGTH              = "len"
TV_MATRIX_TIMELINE_PROPERTY_DURATION            = "dur"





################################################################################
#
################################################################################
class TimeValueMatrix():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self):
        super().__init__()

        self.tvMatrixFilePathName = ""
        self.valueName = ""
        self.fileUUID = str(UUID.uuid4())
        self.derivedFromFileUUID = ""

        self.timelineList = []
    # End -  __init__



    #####################################################
    # [TimeValueMatrix::
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return



    #####################################################
    #
    # Accessor Methods
    #
    #####################################################
    def GetFileUUID(self):
        return self.fileUUID

    def SetDerivedFileUUID(self, newValue):
        self.derivedFromFileUUID = newValue

    def GetNumRows(self):
        return len(self.timelineList)




    #####################################################
    #
    # [TimeValueMatrix::CheckState]
    #
    #####################################################
    def CheckState(self):
        for timelineEntry in self.timelineList:
            self.CheckEntry(timelineEntry)
    # End - CheckState()





    #####################################################
    #
    # [TimeValueMatrix::CheckEntry]
    #
    #####################################################
    def CheckEntry(self, timelineEntry):
        dayNumList = timelineEntry['d']
        prevDay = -1
        for currentDay in dayNumList:
            if (currentDay < 0):
                print("TimeValueMatrix::CheckEntry Error! Negative Day")
                raise Exception()
                sys.exit(0)
            if (currentDay < prevDay):
                print("TimeValueMatrix::CheckEntry Error! Out of order entries")
                raise Exception()
                sys.exit(0)
            prevDay = currentDay
        # End - for currentDay in dayNumList:

        valueList = timelineEntry['v'] 
        for currentVal in valueList:
            if (currentVal == tdf.TDF_INVALID_VALUE):
                print("TimeValueMatrix::CheckEntry Error! Invalid Value")
                raise Exception()
                sys.exit(0)
        # End - for currentVal in valueList:
    # End - CheckEntry()





    #####################################################
    #
    # [TimeValueMatrix::Copy]
    #
    #####################################################
    def Copy(self, srcTVMatrix):
        self.tvMatrixFilePathName = srcTVMatrix.tvMatrixFilePathName
        self.valueName = srcTVMatrix.valueName
        self.timelineList = copy.deepcopy(srcTVMatrix.timelineList)
    # End - Copy



    #####################################################
    #
    # [TimeValueMatrix::Equal]
    #
    #####################################################
    def Equal(self, srcTVMatrix, exceptIfDifferent):
        if ((self.tvMatrixFilePathName != srcTVMatrix.tvMatrixFilePathName) 
            or (self.valueName != srcTVMatrix.valueName)):
            if (exceptIfDifferent):
                raise Exception()
            return False

        if (len(self.timelineList) != len(srcTVMatrix.timelineList)):
            if (exceptIfDifferent):
                raise Exception()
            return False

        for entry1, entry2 in zip(self.timelineList, srcTVMatrix.timelineList):
            if (entry1 != entry2):
                if (exceptIfDifferent):
                    raise Exception()
                return False

            for key, value in entry1.items():
                if (key not in entry2):
                    if (exceptIfDifferent):
                        raise Exception()
                    return False

                if (entry1[key] != entry2[key]):
                    if (exceptIfDifferent):
                        raise Exception()
                    return False
        # End - for entry1, entry2 in zip(self.timelineList, srcTVMatrix.timelineList):
                
        return True
    # End - Equal





    #####################################################
    #
    # [TimeValueMatrix::MakeFromTDF]
    #
    # This creates a new TVMatrix for 1 specific value in a TDF file.
    #####################################################
    def MakeFromTDF(self, tvMatrixFilePathName, valueName):
        fOnlyOneValuePerDay = False
        fUniqueValues = False
        currentTimelineID = -1

        fCarryForwardPreviousDataValues = False
        srcTDF = tdf.TDF_CreateTDFFileReaderEx(tvMatrixFilePathName, valueName, "", [], 
                                                tdf.TDF_TIME_GRANULARITY_SECONDS, 
                                                fCarryForwardPreviousDataValues)
        if (srcTDF is None):
            print("MakeFromTDF Error opening src file: " + srcFilePathName)
            return
 
        # Save the parameters. This may also clobber a previous file state.
        self.timelineList = []
        self.valueName = valueName
        self.derivedFromFileUUID = srcTDF.GetFileUUIDStr()

        # Iterate over every timeline
        fFoundTimeline = srcTDF.GotoFirstTimeline()
        while (fFoundTimeline):
            currentTimelineID = srcTDF.GetCurrentTimelineID()
            if (currentTimelineID < 0):
                print("ERROR! Bad currentTimelineID: " + str(currentTimelineID))
                sys.exit(0)
            
            # Split it up into entries
            entryList = srcTDF.GetRawValues(valueName, fUniqueValues, fOnlyOneValuePerDay)
            numEntries = len(entryList)
            if (numEntries <= 0):
                fFoundTimeline = srcTDF.GotoNextTimeline()
                continue

            dayNumList = [0] * numEntries
            secNumList = [0] * numEntries
            contextStrList = [""] * numEntries
            valueList = [0.0] * numEntries
            entryNum = 0
            for currentEntry in entryList:
                dayNumList[entryNum] = currentEntry['Day']
                secNumList[entryNum] = currentEntry['Sec']
                contextStrList[entryNum] = ""
                valueList[entryNum] = currentEntry['Val']

                entryNum += 1
            # End - for currentEntry in entryList:

            # Assemble the lists into a single timeline entry
            timelineEntry = {'ID': str(currentTimelineID), 'd': dayNumList, 's': secNumList, 'c': contextStrList, 'v': valueList}
            if (TVMATRIX_DEBUG):
                self.CheckEntry(timelineEntry)
            self.timelineList.append(timelineEntry)

            fFoundTimeline = srcTDF.GotoNextTimeline()
        # End - while (fFoundTimeline):

        srcTDF.Shutdown()
    # End - MakeFromTDF





    #####################################################
    #
    # [TimeValueMatrix::MakeFromTDFAndSelectRanges]
    #
    # This creates a new TVMatrix for 1 specific value in a TDF file.
    #   TV_MATRIX_TDF_SELECT_ALL                        = "All"
    #   TV_MATRIX_TDF_SELECT_BELOW_MAX_THEN_REBOUND     = "BelowMaxThenRebound"
    #   TV_MATRIX_TDF_SELECT_BELOW_MAX_AND_STAYOVER_MIN = "BelowMaxStayOverMin"
    #   TV_MATRIX_TDF_SELECT_BELOW_MAX_AND_BELOW_MIN    = "BelowMaxAndBelowMin"
    #####################################################
    def MakeFromTDFAndSelectRanges(self, tvMatrixFilePathName, valueName, selectOp, maxValue, minValue):
        fOnlyOneValuePerDay = False
        fUniqueValues = False
        currentTimelineID = -1
        totalNumSequencesSaved = 0

        fCarryForwardPreviousDataValues = False
        srcTDF = tdf.TDF_CreateTDFFileReaderEx(tvMatrixFilePathName, valueName, "", [], 
                                                tdf.TDF_TIME_GRANULARITY_SECONDS, 
                                                fCarryForwardPreviousDataValues)
        if (srcTDF is None):
            print("MakeFromTDF Error opening src file: " + srcFilePathName)
            return
 
        # Save the parameters. This may also clobber a previous file state.
        self.timelineList = []
        self.valueName = valueName
        self.derivedFromFileUUID = srcTDF.GetFileUUIDStr()

        # Iterate over every timeline
        fFoundTimeline = srcTDF.GotoFirstTimeline()
        while (fFoundTimeline):
            currentTimelineID = srcTDF.GetCurrentTimelineID()
            if (currentTimelineID < 0):
                print("ERROR! Bad currentTimelineID: " + str(currentTimelineID))
                sys.exit(0)
            
            # Split it up into entries
            entryList = srcTDF.GetRawValues(valueName, fUniqueValues, fOnlyOneValuePerDay)
            numEntries = len(entryList)
            if (numEntries <= 0):
                fFoundTimeline = srcTDF.GotoNextTimeline()
                continue

            # Make a list. We may not need to use all of these so we may trim them at the end
            dayNumList = [0] * numEntries
            secNumList = [0] * numEntries
            contextStrList = [""] * numEntries
            valueList = [0.0] * numEntries
            numSavedEntries = 0

            # Look at each new value and add it to the current entry
            fResetList = False
            fSaveList = False
            fStartAboveMax = False
            fDroppedBelowMin = False
            for currentEntry in entryList:
                # First, decide whether to include this value in the results list.
                fAddValueToList = False
                if (selectOp == TV_MATRIX_TDF_SELECT_ALL):
                    fAddValueToList = True
                if (currentEntry['Val'] >= maxValue):
                    fStartAboveMax = True
                if ((currentEntry['Val'] <= maxValue) and (currentEntry['Val'] >= minValue)):
                    fAddValueToList = True
                if (currentEntry['Val'] < minValue):
                    fDroppedBelowMin = True
                else:
                    fDroppedBelowMin = False

                # Optionally add the value to the current list.
                # Note: This does not Save the list, it merely adds a value to the runtime state
                # We may still discard this entire list later without saving it if we hit some veto condition.
                if (fAddValueToList):
                    dayNumList[numSavedEntries] = currentEntry['Day']
                    secNumList[numSavedEntries] = currentEntry['Sec']
                    contextStrList[numSavedEntries] = ""
                    valueList[numSavedEntries] = currentEntry['Val']
                    numSavedEntries += 1
                # End - if (fAddValueToList):                

                # Now, save or discard some lists 
                if ((selectOp == TV_MATRIX_TDF_SELECT_BELOW_MAX_THEN_REBOUND) and (currentEntry['Val'] >= maxValue)):
                    fSaveList = True
                    fResetList = True
                if ((selectOp == TV_MATRIX_TDF_SELECT_BELOW_MAX_AND_STAYOVER_MIN) and (currentEntry['Val'] < minValue)):
                    fSaveList = False
                    fResetList = True
                if ((selectOp == TV_MATRIX_TDF_SELECT_BELOW_MAX_AND_STAYOVER_MIN) and (currentEntry['Val'] >= maxValue)):
                    fSaveList = False
                    fResetList = True
                if ((selectOp == TV_MATRIX_TDF_SELECT_BELOW_MAX_AND_BELOW_MIN) and (currentEntry['Val'] < minValue)):
                    fSaveList = True
                    fResetList = True


                # Optionally save the list
                if (fSaveList):
                   if (numSavedEntries > 0):
                        # Trim the sequence to the final size
                        dayNumList = dayNumList[:numSavedEntries]
                        secNumList = secNumList[:numSavedEntries]
                        contextStrList = contextStrList[:numSavedEntries]
                        valueList = valueList[:numSavedEntries]

                        # Assemble the lists into a single timeline entry
                        nameStr = str(currentTimelineID) + "_" + str(totalNumSequencesSaved)
                        timelineEntry = {'ID': nameStr, 'd': dayNumList, 's': secNumList, 
                                            'c': contextStrList, 'v': valueList}
                        if (TVMATRIX_DEBUG):
                            self.CheckEntry(timelineEntry)
                        self.timelineList.append(timelineEntry)

                        # Make new lists that are not shared and also are not truncated
                        dayNumList = [0] * numEntries
                        secNumList = [0] * numEntries
                        contextStrList = [""] * numEntries
                        valueList = [0.0] * numEntries

                        totalNumSequencesSaved += 1
                        numSavedEntries = 0
                   # End - if (numSavedEntries > 0):

                   fSaveList = False
                # End - if (fSaveList):

                # Optionally reset the list
                if (fResetList):
                    numSavedEntries = 0
                    fStartAboveMax = False
                    fDroppedBelowMin = False
                    fResetList = False
                # End - if (fResetList):
            # End - for currentEntry in entryList:

            # Add the last entry we were working on when we stopped finding new values
            if ((selectOp == TV_MATRIX_TDF_SELECT_BELOW_MAX_AND_BELOW_MIN) and (not fDroppedBelowMin)):
                numSavedEntries = 0
            if (numSavedEntries > 0):
                # Trim the sequence to the final size
                dayNumList = dayNumList[:numSavedEntries]
                secNumList = secNumList[:numSavedEntries]
                contextStrList = contextStrList[:numSavedEntries]
                valueList = valueList[:numSavedEntries]

                # Assemble the lists into a single timeline entry
                nameStr = str(currentTimelineID) + "_" + str(totalNumSequencesSaved)
                timelineEntry = {'ID': str(nameStr), 'd': dayNumList, 's': secNumList, 
                                    'c': contextStrList, 'v': valueList}
                if (TVMATRIX_DEBUG):
                    self.CheckEntry(timelineEntry)
                self.timelineList.append(timelineEntry)

                totalNumSequencesSaved += 1
                numSavedEntries = 0
            # End - if (numSavedEntries > 0):

            fFoundTimeline = srcTDF.GotoNextTimeline()
        # End - while (fFoundTimeline):

        srcTDF.Shutdown()
    # End - MakeFromTDFAndSelectRanges







    #####################################################
    #
    # [TimeValueMatrix::ReadFromFile]
    #
    #####################################################
    def ReadFromFile(self, tvMatrixFilePathName):
        srcFileHandle = None

        # Save the parameters. This may also clobber a previous file state.
        self.tvMatrixFilePathName = tvMatrixFilePathName
        self.valueName = ""
        self.timelineList = []

        # Open the file.
        try:
            srcFileHandle = open(self.tvMatrixFilePathName, 'rb') 
        except Exception:
            print("Error from opening TDF file. File=" + self.tvMatrixFilePathName)
            return

        # Read the file header as a series of text lines
        self.ReadHeader(srcFileHandle)

        ####################
        # Skip ahead to the data
        while True: 
            # Get next line from file 
            try:
                binaryLine = srcFileHandle.readline() 
            except UnicodeDecodeError as err:
                print("Unicode Error from reading Lab file. err=" + str(err))
                continue
            except Exception:
                print("Error from reading Lab file")
                continue

            # Convert the text from Unicode to ASCII. 
            try:
                currentLine = binaryLine.decode("ascii", "ignore")
            except UnicodeDecodeError as err:
                print("Unicode Error from converting string. err=" + str(err))
                continue
            except Exception:
                print("Error from converting string")
                continue

            # Remove whitespace, including the trailing newline.
            currentLine = currentLine.rstrip().lstrip().lower()
            if (currentLine == TVMATRIX_FILE_LOWERCASE_DATA_ELEMENT):
                break
        # End - Skip ahread to the data


        ####################
        # Read the data
        while True: 
            # Get next line from file 
            try:
                binaryLine = srcFileHandle.readline() 
            except UnicodeDecodeError as err:
                print("Unicode Error from reading Lab file. err=" + str(err))
                continue
            except Exception:
                print("Error from reading Lab file.")
                continue

            # Convert the text from Unicode to ASCII. 
            try:
                currentLine = binaryLine.decode("ascii", "ignore")
            except UnicodeDecodeError as err:
                print("Unicode Error from converting string. err=" + str(err))
                continue
            except Exception:
                print("Error from converting string.")
                continue

            # Stop when we hit the end of the file
            if (currentLine is None):
                break

            # Remove whitespace, including the trailing newline.
            currentLine = currentLine.lstrip().rstrip()
            if (currentLine == ""):
                continue

            # Skip comments.
            if (currentLine.startswith(TV_MATRIX_COMMENT_LINE_PREFIX)):
                continue

            # Stop when we hit the end of the data section.
            if ((currentLine.lower() == TVMATRIX_FILE_LOWERCASE_DATA_CLOSE_ELEMENT)):
                break


            # Split it up into ID and data
            partsList = currentLine.split(TIMEVALUE_ID_DATA_SEPARATOR)
            if (len(partsList) < 2):
                continue
            IDStr = partsList[0].lstrip().rstrip()
            dataList = partsList[1].lstrip().rstrip()

            # Split it up into entries
            entryList = dataList.split(TIMEVALUE_LIST_SEPARATOR)
            numEntries = len(entryList)
            if (numEntries <= 0):
                continue

            dayNumList = [0] * numEntries
            secNumList = [0] * numEntries
            contextStrList = [""] * numEntries
            valueList = [0.0] * numEntries
            entryNum = 0
            for entryStr in entryList:
                entryPartStrList = entryStr.split(TIMEVALUE_PART_SEPARATOR)

                dayNum, secInDay = tdf.TDF_ParseTimeStampIntoDaysSecs(entryPartStrList[0])
                dayNumList[entryNum] = dayNum
                secNumList[entryNum] = secInDay
                contextStrList[entryNum] = entryPartStrList[1]
                valueList[entryNum] = float(entryPartStrList[2])

                entryNum += 1
            # End - for entryStr in entryList

            # Assemble the lists into a single timeline entry
            timelineEntry = {'ID': IDStr, 'd': dayNumList, 's': secNumList, 'c': contextStrList, 'v': valueList}
            self.timelineList.append(timelineEntry)

            if (TVMATRIX_DEBUG):
                self.CheckEntry(timelineEntry)
        # End - Read the data

        if (TVMATRIX_DEBUG):
            self.CheckState()
    # End - ReadFromFile






    #####################################################
    #
    # [TimeValueMatrix::ReadHeader]
    #
    #####################################################
    def ReadHeader(self, srcFileHandle):
        # Read the file header as a series of text lines and create a single
        # large text string for just the header. Stop at the body, which may
        # be quite large, and may not fit in in memory all at once.
        fileHeaderStr = ""
        fInHeader = False
        while True: 
            # Get next line from file 
            try:
                binaryLine = srcFileHandle.readline() 
            except UnicodeDecodeError as err:
                print("Unicode Error from reading Lab file. err=" + str(err))
                continue
            except Exception:
                print("Error from reading Lab file.")
                continue

            # Convert the text from Unicode to ASCII. 
            try:
                currentLine = binaryLine.decode("ascii", "ignore")
            except UnicodeDecodeError as err:
                print("Unicode Error from converting string. err=" + str(err))
                continue
            except Exception:
                print("Error from converting string")
                continue

            # Extract the valueName.
            currentLine = currentLine.rstrip().lstrip()
            if (currentLine.lower().startswith(TVMATRIX_FILE_LOWERCASE_HEAD_ELEMENT)):
                fInHeader = True
            elif (currentLine.lower().startswith(TVMATRIX_FILE_LOWERCASE_HEAD_CLOSE_ELEMENT)):
                fInHeader = False
                fileHeaderStr += currentLine
                break

            if (fInHeader):
                fileHeaderStr += currentLine
        # End - Read the file header


        # Parse the text string into am XML DOM
        headerDOM = dxml.XMLTools_ParseStringToDOM(fileHeaderStr)
        if (headerDOM is None):
            return

        headXMLNode = dxml.XMLTools_GetNamedElementInDocument(headerDOM, TVMATRIX_FILE_HEAD_ELEMENT_NAME)
        if (headXMLNode is None):
            return

        self.fileUUID = dxml.XMLTools_GetChildNodeTextAsStr(headXMLNode, TVMATRIX_FILE_HEADER_UUID_ELEMENT_NAME, "")
        self.derivedFromFileUUID = dxml.XMLTools_GetChildNodeTextAsStr(headXMLNode, TVMATRIX_FILE_HEADER_DERIVEDFROM_ELEMENT_NAME, "")
        self.valueName = dxml.XMLTools_GetChildNodeTextAsStr(headXMLNode, TVMATRIX_FILE_HEADER_VALUENAME_ELEMENT_NAME, "")
    # End - ReadHeader







    #####################################################
    #
    # [TimeValueMatrix::WriteToFile]
    #
    #####################################################
    def WriteToFile(self, tvMatrixPathName, comment):
        destFileH = open(tvMatrixPathName, "w+")
        if (destFileH is None):
            print("WriteToFile Error opening dest file: " + tvMatrixPathName)
            return

        # Save the parameters. This may also clobber a previous file state.
        self.tvMatrixFilePathName = tvMatrixPathName

        self.WriteFileHeader(destFileH, comment)

        ##################################
        # Iterate over every timeline
        for timelineEntry in self.timelineList:
            dayNumList = timelineEntry['d'] 
            secNumList = timelineEntry['s'] 
            contextStrList = timelineEntry['c'] 
            valueList = timelineEntry['v'] 
            numItems = len(dayNumList)
            if ((numItems != len(secNumList)) or (numItems != len(contextStrList)) 
                    or (numItems != len(valueList))):
                raise Exception()

            timelineStr = str(timelineEntry['ID']) + TIMEVALUE_ID_DATA_SEPARATOR
            for index in range(numItems):
                currentTimeCode = tdf.TDF_MakeTimeStampSimple(dayNumList[index], secNumList[index])
                timelineStr = timelineStr + str(currentTimeCode) + TIMEVALUE_PART_SEPARATOR
                timelineStr = timelineStr + contextStrList[index] + TIMEVALUE_PART_SEPARATOR
                timelineStr = timelineStr + str(valueList[index]) + TIMEVALUE_LIST_SEPARATOR
            # End - for index in range(valueList)

            if (timelineStr != ""):
                timelineStr = timelineStr[:-1]
                destFileH.write(timelineStr + NEWLINE_STR)
        # End - for timeline in self.timelineList
        
        ##################################
        destFileH.write(NEWLINE_STR + "</" + TVMATRIX_FILE_DATA_ELEMENT_NAME + ">" + NEWLINE_STR)    
        destFileH.write(NEWLINE_STR + "</" + TVMATRIX_FILE_DOC_ELEMENT_NAME + ">" + NEWLINE_STR)
        destFileH.write(NEWLINE_STR + NEWLINE_STR)

        destFileH.flush()
        destFileH.close()
    # End - WriteToFile






    #####################################################
    #
    # [TimeValueMatrix::WriteFileHeader]
    #
    #####################################################
    def WriteFileHeader(self, destFileH, comment):
        ##################################
        destFileH.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + NEWLINE_STR)
        destFileH.write("<" + TVMATRIX_FILE_DOC_ELEMENT_NAME + " version=\"0.1\" xmlns=\"http://www.dawsondean.com/ns/TimeValueMatrix/\">" + NEWLINE_STR)
        destFileH.write(NEWLINE_STR)
        destFileH.write("<" + TVMATRIX_FILE_HEAD_ELEMENT_NAME + ">" + NEWLINE_STR)
        destFileH.write("    <" + TVMATRIX_FILE_HEADER_UUID_ELEMENT_NAME + ">" + self.fileUUID 
                    + "</" + TVMATRIX_FILE_HEADER_UUID_ELEMENT_NAME + ">" + NEWLINE_STR)
        if (self.derivedFromFileUUID != ""):
            destFileH.write("    <" + TVMATRIX_FILE_HEADER_DERIVEDFROM_ELEMENT_NAME + ">" + self.derivedFromFileUUID 
                        + "</" + TVMATRIX_FILE_HEADER_DERIVEDFROM_ELEMENT_NAME + ">" + NEWLINE_STR)
        destFileH.write("    <" + TVMATRIX_FILE_HEADER_DESC_ELEMENT_NAME + ">" + comment 
                    + "</" + TVMATRIX_FILE_HEADER_DESC_ELEMENT_NAME + ">" + NEWLINE_STR)
        destFileH.write("    " + "<" + TVMATRIX_FILE_HEADER_VALUENAME_ELEMENT_NAME + ">" + self.valueName 
                    + "</" + TVMATRIX_FILE_HEADER_VALUENAME_ELEMENT_NAME + ">" + NEWLINE_STR)
        destFileH.write("    <" + TVMATRIX_FILE_HEADER_CREATED_ELEMENT_NAME + ">" 
                    + datetime.today().strftime('%b-%d-%Y') + " "
                    + datetime.today().strftime('%H:%M') 
                    + "</" + TVMATRIX_FILE_HEADER_CREATED_ELEMENT_NAME + ">" + NEWLINE_STR)
        destFileH.write("</" + TVMATRIX_FILE_HEAD_ELEMENT_NAME + ">" + NEWLINE_STR)    
        destFileH.write(NEWLINE_STR)
        destFileH.write("<" + TVMATRIX_FILE_DATA_ELEMENT_NAME + ">" + NEWLINE_STR)    
    # End - WriteToFile






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
            
        # Skip over the header
        while True: 
            # Get next line from file 
            try:
                currentLine = srcFileH.readline() 
            except Exception:
                print("Error from reading Lab file")
                continue

            # Quit if we hit the end of the file.
            if (currentLine == ""):
                break

            # Check for the end of the header or file.
            testStr = currentLine.rstrip().lstrip().lower()
            if (testStr == TVMATRIX_FILE_LOWERCASE_DATA_ELEMENT):
                break
        # End - while True

        # Fix the header
        self.createDateStr = "Aug-22-2025 13:54"
        commentStr = "Covariance Between All Rows in CKDTVMatrixFilteredTimelineLengthOver10.txt"

        # Write a new fixed header to the dest file
        self.WriteFileHeader(destFileH, commentStr)

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

        destFileH.close()
    # End - ImportAndFix






    #####################################################
    #
    # [TimeValueMatrix::GetStats]
    #
    #####################################################
    def GetStats(self, headerStr, resultFilePathName, fPrintToConsole):
        totalNumSequences = 0
        minSequenceSize = 1000000
        maxSequenceSize = 0
        sumAllSequenceSizes = 0
        minSequenceDuration = 1000000
        maxSequenceDuration = 0
        sumAllSequenceDurations = 0

        ##################################
        # Iterate over every timeline
        for timelineEntry in self.timelineList:
            dayNumList = timelineEntry['d'] 

            numItems = len(dayNumList)
            minSequenceSize = min(minSequenceSize, numItems)
            maxSequenceSize = max(maxSequenceSize, numItems)
            sumAllSequenceSizes += numItems

            if (numItems > 0):
                currentDuration = dayNumList[numItems - 1] - dayNumList[0]
            else:
                currentDuration = 0
            minSequenceDuration = min(minSequenceDuration, currentDuration)
            maxSequenceDuration = max(maxSequenceDuration, currentDuration)
            sumAllSequenceDurations += currentDuration

            totalNumSequences += 1
        # End - for timeline in self.timelineList

        # Collect the stats into a dict we can return.
        avgSequenceLen = 0
        avgSequenceDuration = 0
        if (totalNumSequences > 0):
            avgSequenceLen = round(float(sumAllSequenceSizes / totalNumSequences))
            avgSequenceDuration = round(float(sumAllSequenceDurations / totalNumSequences))

        statsDict = {'NumSeq': totalNumSequences, 'AvgLen': avgSequenceLen, 'MinLen': minSequenceSize, 'MaxLen': maxSequenceSize, 'AvgDur': avgSequenceDuration, 'MinDur': minSequenceDuration, 'MaxDur': maxSequenceDuration}

        # Optionally print the results to a file
        if (resultFilePathName != ""):
            fileH = open(resultFilePathName, "a+")
            fileH.write("\n" + headerStr + "\n")
            for index, (valName, value) in enumerate(statsDict.items()):
                fileH.write(valName + ": " + str(value) + "\n")
            # End - for index, (valName, value) in enumerate(statsDict.items()):
            fileH.write("\n\n\n")
            fileH.close()
        # End - if (resultFilePathName != ""):


        # Optionally print the results to the console
        if (fPrintToConsole):
            print("\n" + headerStr + "\n")
            print("   Total Num Rows=" + str(totalNumSequences))
            print("   Total Num Entries=" + str(sumAllSequenceSizes))
            print("   Avg Entries Per Row=" + str(avgSequenceLen))
            print("   Min Entries Per Row=" + str(minSequenceSize))
            print("   Max Entries Per Row=" + str(maxSequenceSize))
            print("   Avg Duration Per Row=" + str(avgSequenceDuration))
            print("   Min Duration Per Row=" + str(minSequenceDuration))
            print("   Max Duration Per Row=" + str(maxSequenceDuration))

        return statsDict
    # End - GetStats





    #####################################################
    #
    # MakeDerivedValueList
    #
    # Make a new list that made from derived values of the original list.
    # For example, it will take list of absolute timestamps and create a list of 
    # relative time differences.
    #####################################################
    def MakeDerivedValueList(self, srcTVMatrix, opName):
        if (len(srcTVMatrix.timelineList) <= 0):
            return

        self.derivedFromFileUUID = srcTVMatrix.fileUUID
        self.fileUUID = str(UUID.uuid4())

        for srcRow in srcTVMatrix.timelineList:
            numEntriesInSrcRow = len(srcRow['v'])
            srcDayNumList = srcRow['d'] 
            srcSecNumList = srcRow['s'] 
            srcContextStrList = srcRow['c'] 
            srcValueList = srcRow['v'] 
            srcListID = srcRow['ID'] 

            # Skip rows with only 1 element or empty rows. These cannot have diffs.
            if (opName in [TV_MATRIX_DERIVED_TABLE_OP_DELTA, TV_MATRIX_DERIVED_TABLE_OP_VELOCITY,
                        TV_MATRIX_DERIVED_TABLE_OP_DELTA_DAYS,
                        TV_MATRIX_DERIVED_TABLE_OP_TOTAL_DELTA, TV_MATRIX_DERIVED_TABLE_OP_TOTAL_VELOCITY]):
                if (numEntriesInSrcRow <= 1):
                    continue

            # Make the dest row
            if (opName in [TV_MATRIX_DERIVED_TABLE_OP_DELTA, TV_MATRIX_DERIVED_TABLE_OP_VELOCITY, TV_MATRIX_DERIVED_TABLE_OP_DELTA_DAYS]):
                numEntriesInDestRow = numEntriesInSrcRow - 1
            elif (opName in [TV_MATRIX_DERIVED_TABLE_OP_TOTAL_DELTA, TV_MATRIX_DERIVED_TABLE_OP_TOTAL_VELOCITY]):
                numEntriesInDestRow = 1

            destDayNumList = [0] * numEntriesInDestRow
            destSecNumList = [0] * numEntriesInDestRow 
            destContextStrList = [""]  * numEntriesInDestRow
            destValueList = [0.0] * numEntriesInDestRow

            ################################
            if (opName in [TV_MATRIX_DERIVED_TABLE_OP_DELTA, TV_MATRIX_DERIVED_TABLE_OP_VELOCITY, TV_MATRIX_DERIVED_TABLE_OP_DELTA_DAYS]):
                for destEntryNum in range(numEntriesInDestRow):
                    destDayNumList[destEntryNum] = srcDayNumList[destEntryNum + 1]
                    destSecNumList[destEntryNum] = srcSecNumList[destEntryNum + 1]
                    destContextStrList[destEntryNum] = srcContextStrList[destEntryNum + 1]
                    if (opName in [TV_MATRIX_DERIVED_TABLE_OP_DELTA]):
                        destValueList[destEntryNum] = srcValueList[destEntryNum + 1] - srcValueList[destEntryNum]
                    elif (opName in [TV_MATRIX_DERIVED_TABLE_OP_DELTA_DAYS]):
                        destValueList[destEntryNum] = srcDayNumList[destEntryNum + 1] - srcDayNumList[destEntryNum]
                    elif (opName in [TV_MATRIX_DERIVED_TABLE_OP_VELOCITY]):
                        deltaValue = float(srcValueList[destEntryNum + 1] - srcValueList[destEntryNum])
                        deltaDays = float(srcDayNumList[destEntryNum + 1] - srcDayNumList[destEntryNum])
                        if (deltaDays > 0.0):
                            destValueList[destEntryNum] = round(float(deltaValue / deltaDays), 1)
                        else:
                            destValueList[destEntryNum] = 0
                # End - for destEntryNum in range(numEntriesInDestRow):
            ################################
            elif (opName in [TV_MATRIX_DERIVED_TABLE_OP_TOTAL_DELTA, TV_MATRIX_DERIVED_TABLE_OP_TOTAL_VELOCITY]):            
                destDayNumList[0] = srcDayNumList[numEntriesInSrcRow - 1]
                destSecNumList[0] = srcSecNumList[numEntriesInSrcRow - 1]
                destContextStrList[0] = srcContextStrList[numEntriesInSrcRow - 1]
                if (opName in [TV_MATRIX_DERIVED_TABLE_OP_TOTAL_DELTA]):
                    destValueList[0] = srcValueList[numEntriesInSrcRow - 1] - srcValueList[0]
                elif (opName in [TV_MATRIX_DERIVED_TABLE_OP_TOTAL_VELOCITY]):
                    deltaValue = float(srcValueList[numEntriesInSrcRow - 1] - srcValueList[0])
                    deltaDays = float(srcDayNumList[numEntriesInSrcRow - 1] - srcDayNumList[0])
                    if (deltaDays > 0.0):
                        destValueList[0] = round(float(deltaValue / deltaDays), 1)
                    else:
                        destValueList[0] = 0

            # Assemble the lists into a single timeline entry
            timelineEntry = {'ID': srcListID, 'd': destDayNumList, 's': destSecNumList, 'c': destContextStrList, 'v': destValueList}
            self.timelineList.append(timelineEntry)
        # End - for srcRow in srcTVMatrix.timelineList:
    # End - MakeDerivedValueList






    #####################################################
    #
    # [SelectValues]
    #
    #####################################################
    def SelectValues(self, compareOp, threshold):
        resultRow = None
        newTimelineList = []

        self.derivedFromFileUUID = self.fileUUID
        self.fileUUID = str(UUID.uuid4())


        if (len(self.timelineList) <= 0):
            return

        for srcRow in self.timelineList:
            numEntriesInSrcRow = len(srcRow['v'])
            if (numEntriesInSrcRow <= 0):
                continue

            # Do some special operators that look at the entire row rather than specific elements.
            if (compareOp in [TV_MATRIX_DERIVED_TABLE_OP_MIN_TIMELINE_SIZE, TV_MATRIX_DERIVED_TABLE_OP_MIN_TOTAL_DURATION]):
                timelineEntry = self.SelectTimelineWithGlobalProperty(srcRow, compareOp, threshold)
                if (timelineEntry is not None):
                    newTimelineList.append(timelineEntry)
                continue
            # End - if (compareOp in [TV_MATRIX_DERIVED_TABLE_OP_MIN_TIMELINE_SIZE, TV_MATRIX_DERIVED_TABLE_OP_MIN_TOTAL_DURATION])

            # Do some special ops that trim the end of a row, but do not look at every element
            if (compareOp in [TV_MATRIX_DERIVED_TABLE_OP_MIN_VALUE_AT_END, TV_MATRIX_DERIVED_TABLE_OP_MAX_VALUE_AT_END]):
                timelineEntry = self.TrimValuesFromEnd(srcRow, compareOp, threshold)
                if (timelineEntry is not None):
                    newTimelineList.append(timelineEntry)
                continue
            # End - if (compareOp in [TV_MATRIX_DERIVED_TABLE_OP_MIN_VALUE_AT_END, TV_MATRIX_DERIVED_TABLE_OP_MAX_VALUE_AT_END])

            # Do some special ops that trim the beginning of a row, but do not look at every element
            if (compareOp in [TV_MATRIX_DERIVED_TABLE_OP_MIN_VALUE_AT_START, TV_MATRIX_DERIVED_TABLE_OP_MAX_VALUE_AT_START, TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MIN_VALUE_AT_START, TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MAX_VALUE_AT_START]):
                timelineEntry = self.TrimValuesFromFront(srcRow, compareOp, threshold)
                if (timelineEntry is not None):
                    newTimelineList.append(timelineEntry)
                continue
            # End - if (compareOp in [TV_MATRIX_DERIVED_TABLE_OP_MIN_VALUE_AT_START, TV_MATRIX_DERIVED_TABLE_OP_MAX_VALUE_AT_START, TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MIN_VALUE_AT_START, TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MAX_VALUE_AT_START])


            # Do some special ops that trim the beginning of a row, but do not look at every element
            if (compareOp in [TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MIN_VALUE_AT_STRETCH_OF_90DAYS, TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MAX_VALUE_AT_STRETCH_OF_90DAYS]):
                timelineEntry = self.TrimValuesFromFrontOfStretch(srcRow, compareOp, threshold, 90)
                if (timelineEntry is not None):
                    newTimelineList.append(timelineEntry)
                continue
            # End - if (compareOp in [TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MIN_VALUE_AT_STRETCH_OF_90DAYS, TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MAX_VALUE_AT_STRETCH_OF_90DAYS])


            # Otherwise, we will filter individual elements. This may keep the full row, or just parts of
            # it, or else remove the row entirely.
            srcDayNumList = srcRow['d'] 
            srcSecNumList = srcRow['s'] 
            srcContextStrList = srcRow['c'] 
            srcValueList = srcRow['v'] 
            srcListID = srcRow['ID'] 
            destDayNumList = []
            destSecNumList = []
            destContextStrList = []
            destValueList = []
            for srcEntryNum in range(numEntriesInSrcRow):
                currentVal = srcValueList[srcEntryNum]
                
                # Do the filtering here.
                fUseCurrentValue = False
                if ((compareOp == TV_MATRIX_COMPARISON_LESS_THAN) and (currentVal < threshold)):
                    fUseCurrentValue = True
                elif ((compareOp == TV_MATRIX_COMPARISON_GREATER_THAN) and (currentVal > threshold)):
                    fUseCurrentValue = True
                elif ((compareOp == TV_MATRIX_COMPARISON_GREATER_THAN_EQUAL) and (currentVal >= threshold)):
                    fUseCurrentValue = True


                if (fUseCurrentValue):
                    destDayNumList.append(srcDayNumList[srcEntryNum])
                    destSecNumList.append(srcSecNumList[srcEntryNum])
                    destContextStrList.append(srcContextStrList[srcEntryNum])
                    destValueList.append(srcValueList[srcEntryNum])
                # End - if (fUseCurrentValue)
            # End - for srcEntryNum in range(numEntriesInSrcRow):

            if (len(destValueList) <= 0):
                continue
            
            # Assemble the lists into a single timeline entry
            timelineEntry = {'ID': srcListID, 'd': destDayNumList, 's': destSecNumList, 'c': destContextStrList, 'v': destValueList}
            newTimelineList.append(timelineEntry)
        # End - for srcRow in self.timelineList:

        self.timelineList = newTimelineList
    # End - SelectValues





    #####################################################
    #
    # [SelectTimelineWithGlobalProperty]
    #
    #####################################################
    def SelectTimelineWithGlobalProperty(self, srcRow, compareOp, threshold):
        resultRow = None

        srcDayNumList = srcRow['d'] 
        srcListID = srcRow['ID'] 
        numEntriesInSrcRow = len(srcDayNumList)

        # Do some special operators that look at the entire row rather than specific elements.
        if (compareOp == TV_MATRIX_DERIVED_TABLE_OP_MIN_TIMELINE_SIZE):
            if (numEntriesInSrcRow >= threshold):
                destDayNumList = copy.deepcopy(srcDayNumList)
                destSecNumList = copy.deepcopy(srcRow['s'])
                destContextStrList = copy.deepcopy(srcRow['c'])
                destValueList = copy.deepcopy(srcRow['v'])
                timelineEntry = {'ID': srcListID, 'd': destDayNumList, 's': destSecNumList, 'c': destContextStrList, 'v': destValueList}

                return timelineEntry
            # End - if (numEntriesInSrcRow >= threshold):
        # End - if (opName == TV_MATRIX_DERIVED_TABLE_OP_MIN_TIMELINE_SIZE):
        elif (compareOp == TV_MATRIX_DERIVED_TABLE_OP_MIN_TOTAL_DURATION):
            totalDuration = srcDayNumList[numEntriesInSrcRow - 1] - srcDayNumList[0]
            if (totalDuration >= threshold):
                destDayNumList = copy.deepcopy(srcDayNumList)
                destSecNumList = copy.deepcopy(srcRow['s'])
                destContextStrList = copy.deepcopy(srcRow['c'])
                destValueList = copy.deepcopy(srcRow['v'])
                timelineEntry = {'ID': srcListID, 'd': destDayNumList, 's': destSecNumList, 'c': destContextStrList, 'v': destValueList}

                return timelineEntry
            # End - if (totalDuration >= threshold):
        # End - elif (opName == TV_MATRIX_DERIVED_TABLE_OP_MIN_TOTAL_DURATION):

        return None
    # End - SelectTimelineWithGlobalProperty





    #####################################################
    #
    # [TrimValuesFromEnd]
    #
    #####################################################
    def TrimValuesFromEnd(self, srcRow, compareOp, threshold):
        resultRow = None
        lastValidEntryIndex = -1

        srcListID = srcRow['ID'] 
        destDayNumList = copy.deepcopy(srcRow['d'])
        destSecNumList = copy.deepcopy(srcRow['s'])
        destContextStrList = copy.deepcopy(srcRow['c'])
        destValueList = copy.deepcopy(srcRow['v'])
        numEntriesInSrcRow = len(destValueList)
        
        # Look for the last useful value
        for lastValidEntryIndex in range(numEntriesInSrcRow - 1, 0, -1):
            currentVal = destValueList[lastValidEntryIndex]
            if ((compareOp == TV_MATRIX_DERIVED_TABLE_OP_MIN_VALUE_AT_END) and (currentVal >= threshold)):
                break
            elif ((compareOp == TV_MATRIX_DERIVED_TABLE_OP_MAX_VALUE_AT_END) and (currentVal < threshold)):
                break
        # End - for lastValidEntryIndex in range(numEntriesInSrcRow - 1, 0, -1):

        # Quit if there is no useful range.
        if (lastValidEntryIndex < 0):
            return None

        # Trim the timelines to end at a useful range
        destDayNumList = destDayNumList[:lastValidEntryIndex + 1]
        destSecNumList = destSecNumList[:lastValidEntryIndex+ 1]
        destContextStrList = destContextStrList[:lastValidEntryIndex + 1]
        destValueList = destValueList[:lastValidEntryIndex + 1]

        # Assemble the lists into a single timeline entry
        timelineEntry = {'ID': srcListID, 'd': destDayNumList, 's': destSecNumList, 'c': destContextStrList, 'v': destValueList}
        return timelineEntry
    # End - TrimValuesFromEnd




    #####################################################
    #
    # [TrimValuesFromFront]
    #
    #####################################################
    def TrimValuesFromFront(self, srcRow, compareOp, threshold):
        resultRow = None
        firstValidEntryIndex = -1

        srcListID = srcRow['ID'] 
        destDayNumList = copy.deepcopy(srcRow['d'])
        destSecNumList = copy.deepcopy(srcRow['s'])
        destContextStrList = copy.deepcopy(srcRow['c'])
        destValueList = copy.deepcopy(srcRow['v'])
        numEntriesInSrcRow = len(destValueList)
        
        # Look for the first useful value
        for firstValidEntryIndex in range(numEntriesInSrcRow):
            currentVal = destValueList[firstValidEntryIndex]
            if ((compareOp in [TV_MATRIX_DERIVED_TABLE_OP_MIN_VALUE_AT_START, TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MIN_VALUE_AT_START]) and (currentVal >= threshold)):
                break
            elif ((compareOp in [TV_MATRIX_DERIVED_TABLE_OP_MAX_VALUE_AT_START, TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MAX_VALUE_AT_START]) and (currentVal < threshold)):
                break
        # End - for firstValidEntryIndex in range(numEntriesInSrcRow):

        if ((firstValidEntryIndex < 0) or (firstValidEntryIndex >= (numEntriesInSrcRow - 1))):
            return None

        if ((firstValidEntryIndex > 0) and (compareOp in [TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MIN_VALUE_AT_START, TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MAX_VALUE_AT_START])):
            firstValidEntryIndex = firstValidEntryIndex - 1

        # Trim the timelines to start at a useful range
        destDayNumList = destDayNumList[firstValidEntryIndex:]
        destSecNumList = destSecNumList[firstValidEntryIndex:]
        destContextStrList = destContextStrList[firstValidEntryIndex:]
        destValueList = destValueList[firstValidEntryIndex:]

        # Assemble the lists into a single timeline entry
        timelineEntry = {'ID': srcListID, 'd': destDayNumList, 's': destSecNumList, 'c': destContextStrList, 'v': destValueList}
        return timelineEntry
    # End - TrimValuesFromFront





    #####################################################
    #
    # [TrimValuesFromFrontOfStretch]
    #
    #####################################################
    def TrimValuesFromFrontOfStretch(self, srcRow, compareOp, threshold, minDuration):
        resultRow = None

        srcListID = srcRow['ID'] 
        destDayNumList = copy.deepcopy(srcRow['d'])
        destSecNumList = copy.deepcopy(srcRow['s'])
        destContextStrList = copy.deepcopy(srcRow['c'])
        destValueList = copy.deepcopy(srcRow['v'])
        numEntriesInSrcRow = len(destValueList)

        # Search until we find a stretch
        firstValidEntryIndex = 0
        while (firstValidEntryIndex < numEntriesInSrcRow):
            # Look for the first useful value
            while (firstValidEntryIndex < numEntriesInSrcRow):
                currentVal = destValueList[firstValidEntryIndex]
                if ((compareOp == TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MIN_VALUE_AT_STRETCH_OF_90DAYS) and (currentVal >= threshold)):
                    break
                elif ((compareOp == TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MAX_VALUE_AT_STRETCH_OF_90DAYS) and (currentVal < threshold)):
                    break

                firstValidEntryIndex += 1
            # End - while (firstValidEntryIndex < numEntriesInSrcRow):

            # Quit if there is no useful start of a range.
            if ((firstValidEntryIndex < 0) or (firstValidEntryIndex >= numEntriesInSrcRow)):
                return None

            # Look for the last useful value
            lastValidEntryIndex = firstValidEntryIndex + 1
            while (lastValidEntryIndex < numEntriesInSrcRow):
                currentVal = destValueList[lastValidEntryIndex]
                if ((compareOp == TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MIN_VALUE_AT_STRETCH_OF_90DAYS) and (currentVal < threshold)):
                    break
                elif ((compareOp == TV_MATRIX_DERIVED_TABLE_OP_LAST_BEFORE_MAX_VALUE_AT_STRETCH_OF_90DAYS) and (currentVal >= threshold)):
                    break

                lastValidEntryIndex += 1
            # End - while (lastValidEntryIndex < numEntriesInSrcRow):

            # If this stretch is long enough, then we found one.
            if (lastValidEntryIndex >= numEntriesInSrcRow):
                break
            totalDuration = destDayNumList[lastValidEntryIndex] - destDayNumList[firstValidEntryIndex]
            if (totalDuration >= minDuration):
                break

            # Otherwise, start looking for the next stretch
            firstValidEntryIndex = lastValidEntryIndex
        # End - while (firstValidEntryIndex < numEntriesInSrcRow):

        if (firstValidEntryIndex >= numEntriesInSrcRow):
            return None

        if (firstValidEntryIndex >= 0):
            firstValidEntryIndex = firstValidEntryIndex - 1

        if (firstValidEntryIndex >= lastValidEntryIndex):
            return None

        # Trim the timelines to start at a useful range
        destDayNumList = destDayNumList[firstValidEntryIndex:]
        destSecNumList = destSecNumList[firstValidEntryIndex:]
        destContextStrList = destContextStrList[firstValidEntryIndex:]
        destValueList = destValueList[firstValidEntryIndex:]

        # Assemble the lists into a single timeline entry
        timelineEntry = {'ID': srcListID, 'd': destDayNumList, 's': destSecNumList, 'c': destContextStrList, 'v': destValueList}
        return timelineEntry
    # End - TrimValuesFromFrontOfStretch







    #####################################################
    #
    # MakeHistogramOfValues
    #
    #####################################################
    def MakeHistogramOfValues(self):
        preFlight = MedHistogram.Preflight()
        for srcRow in self.timelineList:
            srcValueList = srcRow['v'] 
            for currentVal in srcValueList:
                preFlight.AddValue(currentVal)
            # End - for currentVal in srcValueList:
        # End - for srcRow in self.timelineList:
                
        fIntType = False # True
        fDiscardValuesOutOfRange = False
        numBuckets = 15
        histogram = MedHistogram.TDFHistogram()
        histogram.InitWithPreflight(fIntType, fDiscardValuesOutOfRange, numBuckets, preFlight)

        for srcRow in self.timelineList:
            srcValueList = srcRow['v'] 
            for currentVal in srcValueList:
                histogram.AddValue(currentVal)
        # End - for srcRow in self.timelineList:

        return histogram
    # End - MakeHistogramOfValues





    #####################################################
    #
    # MakeHistogramOfValuesInvsOutTimePeriod
    #
    #####################################################
    def MakeHistogramOfValuesInvsOutTimePeriod(self, startDayInSecs, stopDayInSecs):
        ###############################################
        # Preflight the data
        preFlight = MedHistogram.Preflight()
        for srcRow in self.timelineList:
            srcValueList = srcRow['v'] 
            srcDayNumList = srcRow['d'] 
            srcSecList = srcRow['s'] 

            fInDayTime = True
            dayValueSum = 0
            dayValueCount = 0
            dayMinValue = 100000000
            dayMaxValue = 0
            nightValueSum = 0
            nightValueCount = 0
            nightMinValue = 100000000
            nightMaxValue = 0
            for currentSec, currentVal in zip(srcSecList, srcValueList):
                # Check if this is in the night or day
                fCurrentIsDaytimeValue = False
                if ((currentSec >= startDayInSecs) and (currentSec <= stopDayInSecs)):
                    fCurrentIsDaytimeValue = True

                # Add this to the total for night or day
                if (fCurrentIsDaytimeValue):
                    # Check if we are transitioning from night to day.
                    # If so, record the previous day/night and start a new day
                    if (not fInDayTime):
                        # Compute the biggest change between the previous daya nd night
                        if ((dayValueCount > 0) and (dayValueCount > 0)):
                            delta1 = abs(dayMaxValue - nightMinValue)
                            delta2 = abs(nightMaxValue - dayMinValue)
                            biggestDelta = max(delta1, delta2)
                            preFlight.AddValue(biggestDelta)

                        # Reset to start a new day/night cycle
                        fInDayTime = True
                        dayValueSum = 0
                        dayValueCount = 0
                        nightValueSum = 0
                        nightValueCount = 0
                        dayMinValue = 100000000
                        dayMaxValue = 0
                        nightMinValue = 100000000
                        nightMaxValue = 0
                    # End - if (not fInDayTime):

                    dayMinValue = min(dayMinValue, currentVal)
                    dayMaxValue = max(dayMaxValue, currentVal)
                    dayValueSum += currentVal
                    dayValueCount += 1
                else:  # if (not fCurrentIsDaytimeValue):
                    # Check if we are transitioning from night to day.
                    # If so, record the previous day/night and start a new day
                    if (fInDayTime):
                        fInDayTime = False
                    # End - if (not fInDayTime):

                    nightMinValue = min(nightMinValue, currentVal)
                    nightMaxValue = max(nightMaxValue, currentVal)
                    nightValueSum += currentVal
                    nightValueCount += 1
                # End if (not fCurrentIsDaytimeValue)):
            # End - for currentSec, currentVal in zip(srcSecList, srcValueList):
        # End - for srcRow in self.timelineList:
                



        # Make a new histogram from the preflight data
        fIntType = False   # True
        fDiscardValuesOutOfRange = False
        numBuckets = 15
        histogram = MedHistogram.TDFHistogram()
        histogram.InitWithPreflight(fIntType, fDiscardValuesOutOfRange, numBuckets, preFlight)




        ###############################################
        # Make the histogram
        preFlight = MedHistogram.Preflight()
        for srcRow in self.timelineList:
            srcValueList = srcRow['v'] 
            srcDayNumList = srcRow['d'] 
            srcSecList = srcRow['s'] 

            fInDayTime = True
            dayValueSum = 0
            dayValueCount = 0
            dayMinValue = 100000000
            dayMaxValue = 0
            nightValueSum = 0
            nightValueCount = 0
            nightMinValue = 100000000
            nightMaxValue = 0
            for currentSec, currentVal in zip(srcSecList, srcValueList):
                # Check if this is in the night or day
                fCurrentIsDaytimeValue = False
                if ((currentSec >= startDayInSecs) and (currentSec <= stopDayInSecs)):
                    fCurrentIsDaytimeValue = True

                # Add this to the total for night or day
                if (fCurrentIsDaytimeValue):
                    # Check if we are transitioning from night to day.
                    # If so, record the previous day/night and start a new day
                    if (not fInDayTime):
                        # Compute the biggest change between the previous daya nd night
                        if ((dayValueCount > 0) and (dayValueCount > 0)):
                            delta1 = abs(dayMaxValue - nightMinValue)
                            delta2 = abs(nightMaxValue - dayMinValue)
                            biggestDelta = max(delta1, delta2)
                            histogram.AddValue(biggestDelta)

                        # Reset to start a new day/night cycle
                        fInDayTime = True
                        dayValueSum = 0
                        dayValueCount = 0
                        nightValueSum = 0
                        nightValueCount = 0
                        dayMinValue = 100000000
                        dayMaxValue = 0
                        nightMinValue = 100000000
                        nightMaxValue = 0
                    # End - if (not fInDayTime):

                    dayMinValue = min(dayMinValue, currentVal)
                    dayMaxValue = max(dayMaxValue, currentVal)
                    dayValueSum += currentVal
                    dayValueCount += 1
                else:  # if (not fCurrentIsDaytimeValue):
                    # Check if we are transitioning from night to day.
                    # If so, record the previous day/night and start a new day
                    if (fInDayTime):
                        fInDayTime = False
                    # End - if (not fInDayTime):

                    nightMinValue = min(nightMinValue, currentVal)
                    nightMaxValue = max(nightMaxValue, currentVal)
                    nightValueSum += currentVal
                    nightValueCount += 1
                # End if (not fCurrentIsDaytimeValue)):
            # End - for currentSec, currentVal in zip(srcSecList, srcValueList):
        # End - for srcRow in self.timelineList:
                

        return histogram
    # End - MakeHistogramOfValuesInvsOutTimePeriod





    #####################################################
    #
    # MakeHistogramOfTimelineProperties
    #
    #####################################################
    def MakeHistogramOfTimelineProperties(self, propertyName):
        preFlight = MedHistogram.Preflight()
        for srcRow in self.timelineList:
            srcValueList = srcRow['v'] 
            if (propertyName == TV_MATRIX_TIMELINE_PROPERTY_LENGTH):
                value = len(srcValueList)
            if (propertyName == TV_MATRIX_TIMELINE_PROPERTY_DURATION):
                dayNumList = srcRow['d'] 
                listLen = len(dayNumList)
                value = dayNumList[listLen - 1] - dayNumList[0]
            else:
                value = 0

            preFlight.AddValue(value)
            # End - for currentVal in srcValueList:
        # End - for srcRow in self.timelineList:
                
        fIntType = False # True
        fDiscardValuesOutOfRange = False
        numBuckets = 20
        histogram = MedHistogram.TDFHistogram()
        histogram.InitWithPreflight(fIntType, fDiscardValuesOutOfRange, numBuckets, preFlight)

        for srcRow in self.timelineList:
            srcValueList = srcRow['v'] 
            if (propertyName == TV_MATRIX_TIMELINE_PROPERTY_LENGTH):
                value = len(srcValueList)
            if (propertyName == TV_MATRIX_TIMELINE_PROPERTY_DURATION):
                dayNumList = srcRow['d'] 
                listLen = len(dayNumList)
                value = dayNumList[listLen - 1] - dayNumList[0]
            else:
                value = 0

            histogram.AddValue(value)
        # End - for srcRow in self.timelineList:

        return histogram
    # End - MakeHistogramOfTimelineProperties




    #####################################################
    #
    # MakeHistogramOfTimelineLengthsEx
    #
    #####################################################
    def MakeHistogramOfTimelineLengthsEx(self, numBuckets, minVal, maxVal):
        fIntType = False # True
        fDiscardValuesOutOfRange = False
        histogram = MedHistogram.TDFHistogram()
        histogram.InitEx(fIntType, fDiscardValuesOutOfRange, numBuckets, minVal, maxVal)

        for srcRow in self.timelineList:
            srcValueList = srcRow['v'] 
            histogram.AddValue(len(srcValueList))
        # End - for srcRow in self.timelineList:

        return histogram
    # End - MakeHistogramOfTimelineLengthsEx





    #####################################################
    #
    # [TimeValueMatrix::MakeTimesRelativeToZero]
    #
    #####################################################
    def MakeTimesRelativeToZero(self, timelineEntry):
        offset = 0

        dayNumList = timelineEntry['d'] 
        numItems = len(dayNumList)

        if (numItems <= 0):
            return
        offset = dayNumList[0]

        for index in range(len(dayNumList)):
            dayNumList[index] = dayNumList[index] - offset
        # End - for index in range(valueList)

        if ('ld' in timelineEntry):
            timelineEntry['ld'] = timelineEntry['ld'] - offset
     # End - MakeTimesRelativeToZero






    #####################################################
    #
    # [TimeValueMatrix::DiscardHealthyItemsFromBeginning]
    #
    # Discard "Healthy" items that are from the beginning.
    # This leaves every timeline starting at with disease.
    #
    # Note, it may get better than disease if it recovers
    # Note, this may remove timelines that never get disease
    #####################################################
    def DiscardHealthyItemsFromBeginning(self, timelineEntry, fHigherIsHealthier, threshold):
        fFoundSickValue = False
        fHaveLastHealthValue = False

        dayNumList = timelineEntry['d'] 
        secNumList = timelineEntry['s'] 
        contextStrList = timelineEntry['c'] 
        valueList = timelineEntry['v'] 
        numItems = len(valueList)

        # Look for the first sick entry
        for firstSickIndex in range(numItems):
            # Decide if this item is healthy.
            fItemIsHealthy = False
            if ((fHigherIsHealthier) and ((valueList[firstSickIndex] > threshold))):
                fItemIsHealthy = True
            elif ((not fHigherIsHealthier) and ((valueList[firstSickIndex] < threshold))):
                fItemIsHealthy = True

            # If not, then we found the first sick item so stop looking
            if (not fItemIsHealthy):
                fFoundSickValue = True
                break
        # End - for firstSickIndex in range(numItems):


        if (fFoundSickValue):
            # Record the last healthy value before it started to get sick.
            if (firstSickIndex > 0):
                timelineEntry['l'] = True
                timelineEntry['ld'] = dayNumList[firstSickIndex - 1]
                # Trim the list to start at the sick values
                timelineEntry['d'] = dayNumList[firstSickIndex:]
                timelineEntry['s'] = secNumList[firstSickIndex:]
                timelineEntry['c'] = contextStrList[firstSickIndex:]
                timelineEntry['v'] = valueList[firstSickIndex:]
            else:
                timelineEntry['l'] = False
                timelineEntry['ld'] = 0
        else:
            timelineEntry['l'] = False
            timelineEntry['ld'] = 0
            
            timelineEntry['d'] = []
            timelineEntry['s'] = []
            timelineEntry['c'] = []
            timelineEntry['v'] = []

        # Ignore the real value, all healthy values look alike
        timelineEntry['lv'] = threshold
    # End - DiscardHealthyItemsFromBeginning






    #####################################################
    #
    # [TimeValueMatrix::CombineMultipleEntriesFromSameDay]
    #
    #####################################################
    def CombineMultipleEntriesFromSameDay(self, timelineEntry, fHigherIsHealthier):
        dayNumList = timelineEntry['d'] 
        secNumList = timelineEntry['s'] 
        contextStrList = timelineEntry['c'] 
        valueList = timelineEntry['v'] 

        numItems = len(valueList)
        lastValidEntry = 0
        srcIndex = 1
        while (srcIndex < numItems):
            # If the days are the same, then merge days
            if (dayNumList[lastValidEntry] == dayNumList[srcIndex]):
                if (fHigherIsHealthier):
                    valueList[lastValidEntry] = min(valueList[lastValidEntry], valueList[srcIndex])
                else:
                    valueList[lastValidEntry] = max(valueList[lastValidEntry], valueList[srcIndex])
                srcIndex += 1
            # Otherwise, they are different, so just shift
            else:
                destIndex = lastValidEntry + 1
                dayNumList[destIndex] = dayNumList[srcIndex]
                valueList[destIndex] = valueList[srcIndex]
                secNumList[destIndex] = secNumList[srcIndex]
                contextStrList[destIndex] = contextStrList[srcIndex]
                lastValidEntry += 1
                srcIndex += 1
        # End - while (srcIndex < numItems)

        # Cutting makes a new list, so the old uncut list, is still in the entry.
        # Update that.
        if ((lastValidEntry + 1) < numItems):
            timelineEntry['d'] = dayNumList[:lastValidEntry + 1]
            timelineEntry['s'] = secNumList[:lastValidEntry + 1]
            timelineEntry['c'] = contextStrList[:lastValidEntry + 1]
            timelineEntry['v'] = valueList[:lastValidEntry + 1]
    # End - CombineMultipleEntriesFromSameDay







    #####################################################
    #
    # [TimeValueMatrix::StartBothListsAtSameDiseaseLevel
    #
    # Find the index in both lists that correspond to the same
    # level of disease.
    #
    #####################################################
    def StartBothListsAtSameDiseaseLevel(self, timelineEntry1, timelineEntry2, 
                                    fHigherIsHealthier, lastHealthyValue, valueErrorRange):
        offset = 0
        startOffset1 = 0
        startOffset2 = 0
        fRemoveFromList1 = False

        # Discard healthy values in both lists
        self.DiscardHealthyItemsFromBeginning(timelineEntry1, fHigherIsHealthier, lastHealthyValue)
        if (len(timelineEntry1['v']) < MIN_NUMBER_VALUES_FOR_COVARIANT):
            return
        self.DiscardHealthyItemsFromBeginning(timelineEntry2, fHigherIsHealthier, lastHealthyValue)
        if (len(timelineEntry2['v']) < MIN_NUMBER_VALUES_FOR_COVARIANT):
            return

        # Get the list of values
        valueList1 = timelineEntry1['v'] 
        valueList2 = timelineEntry2['v']
        numItems1 = len(valueList1)
        numItems2 = len(valueList2)
        startValue1 = valueList1[0]
        startValue2 = valueList2[0]

        # If they both start with the same level of disease then then we are done
        if (abs(startValue2 - startValue1) < valueErrorRange):
            return

        # Find the list that starts with the healthier state. This is the one we will trim off.
        # We want both lists to start equally sick.
        if ((fHigherIsHealthier) and (startValue1 > startValue2)):
            # Look through list 1 until it is as sick as the start of list 2
            fRemoveFromList1 = True
            referenceValue = startValue2
            searchList = valueList1
        elif ((not fHigherIsHealthier) and (startValue1 < startValue2)):
            # Look through list 1 until it is as sick as the start of list 2
            fRemoveFromList1 = True
            referenceValue = startValue2
            searchList = valueList1
        else:
            # Look through list 2 until it is as sick as the start of list 1
            fRemoveFromList1 = False
            referenceValue = startValue1
            searchList = valueList2

        # Scan through the healthier list, and find where it turns sick enough
        numItemsToSearch = len(searchList)
        indexThatIsSickEnough = 1
        foundStartIndex = False
        while (indexThatIsSickEnough < numItemsToSearch):
            if (abs(searchList[indexThatIsSickEnough] - referenceValue) < valueErrorRange):
                foundStartIndex = True
                break
            elif ((fHigherIsHealthier) and ((searchList[indexThatIsSickEnough] < referenceValue))):
                foundStartIndex = True
                break
            elif ((not fHigherIsHealthier) and ((searchList[indexThatIsSickEnough] > referenceValue))):
                foundStartIndex = True
                break

            indexThatIsSickEnough += 1
        # End - while (indexThatIsSickEnough < numItemsToSearch):


        # Make sure there is work to do. If the healthier list never got sick enough, 
        # then we cannot compare them.
        if (not foundStartIndex):
            if (fRemoveFromList1):
                timelineEntry1['d'] = []
                timelineEntry1['s'] = []
                timelineEntry1['c'] = []
                timelineEntry1['v'] = []
            else:
                timelineEntry2['d'] = []
                timelineEntry2['s'] = []
                timelineEntry2['c'] = []
                timelineEntry2['v'] = []
            return
        # End - if (not foundStartIndex):


        if (fRemoveFromList1):
            dayNumList = timelineEntry1['d'] 
            secNumList = timelineEntry1['s'] 
            contextStrList = timelineEntry1['c'] 
            valueList = timelineEntry1['v'] 

            if (indexThatIsSickEnough > 0):
                timelineEntry1['l'] = True
                timelineEntry1['ld'] = dayNumList[indexThatIsSickEnough - 1]
                timelineEntry1['lv'] = valueList[indexThatIsSickEnough - 1]
            else:
                timelineEntry1['l'] = False
                timelineEntry1['ld'] = 0
                timelineEntry1['lv'] = 0

            timelineEntry1['d'] = dayNumList[indexThatIsSickEnough:]
            timelineEntry1['s'] = secNumList[indexThatIsSickEnough:]
            timelineEntry1['c'] = contextStrList[indexThatIsSickEnough:]
            timelineEntry1['v'] = valueList[indexThatIsSickEnough:]
        else:
            dayNumList = timelineEntry2['d'] 
            secNumList = timelineEntry2['s'] 
            contextStrList = timelineEntry2['c'] 
            valueList = timelineEntry2['v'] 

            if (indexThatIsSickEnough > 0):
                timelineEntry2['l'] = True
                timelineEntry2['ld'] = dayNumList[indexThatIsSickEnough - 1]
                timelineEntry2['lv'] = valueList[indexThatIsSickEnough - 1]
            else:
                timelineEntry2['l'] = False
                timelineEntry2['ld'] = 0
                timelineEntry2['lv'] = 0

            timelineEntry2['d'] = dayNumList[indexThatIsSickEnough:]
            timelineEntry2['s'] = secNumList[indexThatIsSickEnough:]
            timelineEntry2['c'] = contextStrList[indexThatIsSickEnough:]
            timelineEntry2['v'] = valueList[indexThatIsSickEnough:]
        # End - else
    # End - StartBothListsAtSameDiseaseLevel








    #####################################################
    #
    # [TimeValueMatrix::InterpolateDataPoints]
    #
    #####################################################
    def InterpolateDataPoints(self, timelineEntry1, timelineEntry2, 
                            fNarrowTimelinesToSickValues,
                            fHigherIsHealthier, lastHealthyValue, valueErrorRange):
        if (TVMATRIX_DEBUG):
            self.CheckEntry(timelineEntry1)
            self.CheckEntry(timelineEntry2)

        # Simplify the lists by combining values from the same day into a single entry
        self.CombineMultipleEntriesFromSameDay(timelineEntry1, fHigherIsHealthier)
        if (len(timelineEntry1['v']) < MIN_NUMBER_VALUES_FOR_COVARIANT):
            return
        self.CombineMultipleEntriesFromSameDay(timelineEntry2, fHigherIsHealthier)
        if (len(timelineEntry2['v']) < MIN_NUMBER_VALUES_FOR_COVARIANT):
            return
        if (TVMATRIX_DEBUG):
            self.CheckEntry(timelineEntry1)
            self.CheckEntry(timelineEntry2)

        # Shorten the lists so they both start at the same disease level. We don't care about 
        # how long a list was healthy, we only compare them whern they start getting sick.
        # This will also shorten the healthier list so both lists start at the same level
        # of disease.
        if (fNarrowTimelinesToSickValues):
            self.StartBothListsAtSameDiseaseLevel(timelineEntry1, timelineEntry2, 
                                        fHigherIsHealthier, lastHealthyValue, valueErrorRange)
            if ((len(timelineEntry1['v']) < MIN_NUMBER_VALUES_FOR_COVARIANT)
                    or (len(timelineEntry2['v']) < MIN_NUMBER_VALUES_FOR_COVARIANT)):
                return
            if (TVMATRIX_DEBUG):
                self.CheckEntry(timelineEntry1)
                self.CheckEntry(timelineEntry2)
        # End - if (fNarrowTimelinesToSickValues)

        # We don't care about absolute times, so make all times start at day 0        
        self.MakeTimesRelativeToZero(timelineEntry1)
        self.MakeTimesRelativeToZero(timelineEntry2)

        if (TVMATRIX_DEBUG):
            self.CheckEntry(timelineEntry1)
            self.CheckEntry(timelineEntry2)

        dayNumList1 = timelineEntry1['d'] 
        numItems1 = len(dayNumList1)
        secNumList1 = timelineEntry1['s'] 
        contextStrList1 = timelineEntry1['c'] 
        valueList1 = timelineEntry1['v'] 

        dayNumList2 = timelineEntry2['d'] 
        numItems2 = len(dayNumList2)
        secNumList2 = timelineEntry2['s'] 
        contextStrList2 = timelineEntry2['c'] 
        valueList2 = timelineEntry2['v'] 

        # The two lists may sample at different times.
        # Add interpolated values so both lists have values on the same days.
        # We stop when either list hits the end. Do not try to make the lists the same size.
        index1 = 0
        index2 = 0
        while ((index1 < numItems1) and (index2 < numItems2)):
            # If the days line up, then we are ok, go on to the next pair of days
            if (dayNumList1[index1] == dayNumList2[index2]):
                index1 += 1
                index2 += 1
                continue

            # Insert a new value BEFORE the current date in list 2 if there is a value to interpolate with
            if ((dayNumList1[index1] < dayNumList2[index2]) and ((index2 > 0) or ('ld' in timelineEntry2))):
                fInsertIntoList1 = False
                insertIndex = index2
                # List 2 will now have an entry with the same date as the current entry in list1
                newDate = dayNumList1[index1]
                numItems2 += 1

                # Get the days we will interpolate between to make the new list entry.
                currentValue = valueList2[index2]
                currentDay = dayNumList2[index2]
                currentSecs = secNumList2[index2]
                currentContext = contextStrList2[index2]
                if (index2 > 0):
                    prevValue = valueList2[index2 - 1]
                    prevDay = dayNumList2[index2 - 1]
                else:
                    prevValue = timelineEntry2['lv']
                    prevDay = timelineEntry2['ld']
            # Insert a new value BEFORE the current date in list 1 if there is a value to interpolate with
            elif ((dayNumList2[index2] < dayNumList1[index1]) and ((index1 > 0)or ('ld' in timelineEntry1))):
                fInsertIntoList1 = True
                insertIndex = index1
                # List 1 will now have an entry with the same date as the current entry in list2
                newDate = dayNumList2[index2]
                numItems1 += 1

                # Get the days we will interpolate between to make the new list entry.
                currentValue = valueList1[index1]
                currentDay = dayNumList1[index1]
                currentSecs = secNumList1[index1]
                currentContext = contextStrList1[index1]
                if (index1 > 0):
                    prevValue = valueList1[index1 - 1]
                    prevDay = dayNumList1[index1 - 1]
                else:
                    prevValue = timelineEntry1['lv']
                    prevDay = timelineEntry1['ld']
            # End - elif (dayNumList2[index2] < dayNumList1[index1]):
            #####################################################
            # Otherwise, leave the values unaligned
            else:
                index1 += 1
                index2 += 1
                continue

            # At this point, do an insertion.
            # <><><><>
            totalDimeDelta = currentDay - prevDay
            # Hang a breakpoint here
            if (totalDimeDelta <= 0):
                totalDimeDelta = totalDimeDelta

            timeDeltaUntilNewInsertionDate = newDate - prevDay
            fractionOfChangeToNewDate = float(float(timeDeltaUntilNewInsertionDate) / float(totalDimeDelta))

            totalValueChange = currentValue - prevValue
            newInterpolatedValue = prevValue + round((totalValueChange * fractionOfChangeToNewDate), 2)

            if (fInsertIntoList1):
                dayNumList1.insert(insertIndex, newDate)
                secNumList1.insert(insertIndex, currentSecs)
                contextStrList1.insert(insertIndex, currentContext)
                valueList1.insert(insertIndex, newInterpolatedValue)
            else:
                dayNumList2.insert(insertIndex, newDate)
                secNumList2.insert(insertIndex, currentSecs)
                contextStrList2.insert(insertIndex, currentContext)
                valueList2.insert(insertIndex, newInterpolatedValue)

            # After inserting into list A, look at the next element in list B.
            # Look at the item we previously looked at in list A, which is now A past the item we inserted.
            # So, uh, gee, just advance both indexes.
            index2 += 1
            index1 += 1
        # End - while ((index1 < numItems1) and (index2 < numItems2)):


        newLength = min(index1, index2)
        # Now, discard any values that extended beyond the other list
        if (numItems1 > newLength):
            dayNumList1 = dayNumList1[:newLength]
            secNumList1 = secNumList1[:newLength]
            contextStrList1 = contextStrList1[:newLength]
            valueList1 = valueList1[:newLength]
        if (numItems2 > newLength):
            dayNumList2 = dayNumList2[:newLength]
            secNumList2 = secNumList2[:newLength]
            contextStrList2 = contextStrList2[:newLength]
            valueList2 = valueList2[:newLength]

        timelineEntry1['d'] = dayNumList1
        timelineEntry1['s'] = secNumList1
        timelineEntry1['c'] = contextStrList1
        timelineEntry1['v'] = valueList1

        timelineEntry2['d'] = dayNumList2
        timelineEntry2['s'] = secNumList2
        timelineEntry2['c'] = contextStrList2
        timelineEntry2['v'] = valueList2
    # End - InterpolateDataPoints






    #####################################################
    #
    # TimeValueMatrix:GetCovarianceBetweenTwoRows
    #
    #####################################################
    def GetCovarianceBetweenTwoRows(self, rowNum1, rowNum2, 
                            fNarrowTimelinesToSickValues,
                            fHigherIsHealthier, lastHealthyValue, valueErrorRange):
        if ((rowNum1 < 0) or (rowNum2 < 0) or (rowNum1 >= len(self.timelineList)) 
                or (rowNum2 >= len(self.timelineList))):
            return tdf.TDF_INVALID_VALUE

        timelineEntry1 = copy.deepcopy(self.timelineList[rowNum1])
        timelineEntry2 = copy.deepcopy(self.timelineList[rowNum2])
        self.InterpolateDataPoints(timelineEntry1, timelineEntry2, 
                    fNarrowTimelinesToSickValues,
                    fHigherIsHealthier, lastHealthyValue, valueErrorRange)

        if ((len(timelineEntry1['v']) < MIN_NUMBER_VALUES_FOR_COVARIANT)
                or (len(timelineEntry2['v']) < MIN_NUMBER_VALUES_FOR_COVARIANT)):
            return tdf.TDF_INVALID_VALUE

        try:
            correlation, _ = spearmanr(timelineEntry1['v'], timelineEntry2['v'])
        except:
            correlation = tdf.TDF_INVALID_VALUE
            pass
    
        return correlation
    # End - GetCovarianceBetweenTwoRows






    #####################################################
    # TimeValueMatrix:GetCovarianceBetweenAllRows
    #####################################################
    def GetCovarianceBetweenAllRows(self, correlationResultFilePathName, 
                            fNarrowTimelinesToSickValues,
                            fHigherIsHealthier, lastHealthyValue, valueErrorRange):
        resultFileInfo = MedGraph.MedGraph_OpenExistingGraph(correlationResultFilePathName, self.fileUUID)
        if (resultFileInfo is None):
            raise Exception()
            return

        numRows = len(self.timelineList)
        for stopRow in range(numRows):
            if (len(self.timelineList[stopRow]['v']) < MIN_NUMBER_VALUES_FOR_COVARIANT):
                continue

            for startRow in range(stopRow):
                startRowIDStr = self.timelineList[startRow]['ID']
                stopRowIDStr = self.timelineList[stopRow]['ID']

                if (len(self.timelineList[startRow]['v']) < MIN_NUMBER_VALUES_FOR_COVARIANT):
                    continue

                # It is possible we already found this correlation on a previous instance
                # of this program that crashed. In this case, we are running on a restarted
                # process, so do not waste time recomputing work that is already done.
                # Look for this pair in the result file
                foundIt, resultStr = resultFileInfo.GetEdge(startRowIDStr, stopRowIDStr)
                if (foundIt):
                    continue

                correlation = self.GetCovarianceBetweenTwoRows(startRow, stopRow,
                                            fNarrowTimelinesToSickValues,
                                            fHigherIsHealthier, lastHealthyValue, valueErrorRange)
                # Append the result to the file.
                # NOTE! Do this even if it is TDF_INVALID_VALUE so we do not
                # spend the work repeating a failed computation if we restart.
                resultFileInfo.AppendEdge(startRowIDStr, stopRowIDStr, correlation)
            # End - for startRow in range(stopRow):
        # End - for str(stopRow) in range(numRows):

        resultFileInfo.FinishWritingToFile()
    # End - GetCovarianceBetweenAllRows






    #####################################################
    #
    # TimeValueMatrix:FindRowID
    #
    #####################################################
    def FindRowID(self, rowIDStr):
        fFoundRow = False

        # Look for the row with this ID.
        # <><> FIXME BUGBUG This is slow, and the linear search really should be
        # replaced with a hash lookup using the ID as the key.
        for entry in self.timelineList:
            if (entry['ID'] == rowIDStr):
                fFoundRow = True
                break
        # End - for entry in self.timelineList:

        return fFoundRow
    # End - FindRowID




    #####################################################
    #
    # TimeValueMatrix:GetSequenceValuesAfterDiseaseStarts
    #
    #####################################################
    def GetSequenceValuesAfterDiseaseStarts(self, rowIDStr, fHigherIsHealthier, lastHealthyValue, valueErrorRange):
        fFoundRow = False

        # Look for the row with this ID.
        # <><> FIXME BUGBUG This is slow, and the linear search really should be replaced 
        # with a hash lookup using the ID as the key.
        for entry in self.timelineList:
            if (entry['ID'] == rowIDStr):
                fFoundRow = True
                break
        # End - for entry in self.timelineList:

        if (not fFoundRow):
            return None, None

        # Make a woring copy so we can edit it without affecting the original
        copiedEntry = copy.deepcopy(entry)

        # Simplify the list by combining values from the same day into a single entry
        self.CombineMultipleEntriesFromSameDay(copiedEntry, fHigherIsHealthier)
        if (len(copiedEntry['v']) <= 0):
            return None, None

        self.DiscardHealthyItemsFromBeginning(copiedEntry, fHigherIsHealthier, lastHealthyValue)
        if (len(copiedEntry['v']) <= 0):
            return None, None

        # We don't care about absolute times, so make all times start at day 0        
        self.MakeTimesRelativeToZero(copiedEntry)

        return copiedEntry['d'], copiedEntry['v']
    # End - GetSequenceValuesAfterDiseaseStarts





# End - class TimeValueMatrix







################################################################################
# 
################################################################################
def CopyTimeValueMatrix(srcTVMatrix):
    newTVMatrix = TimeValueMatrix()
    newTVMatrix.Copy(srcTVMatrix)
    return newTVMatrix
# End - CopyTimeValueMatrix





################################################################################
# 
################################################################################
def CreateTimeValueMatrixFromTDF(tvMatrixFilePathName, valueName):
    newTVMatrix = TimeValueMatrix()
    newTVMatrix.MakeFromTDF(tvMatrixFilePathName, valueName)
    return newTVMatrix
# End - CreateTimeValueMatrixFromTDF




################################################################################
# 
################################################################################
def MakeTimeValueMatrixFromSelectionsOfTDF(tvMatrixFilePathName, valueName, selectOp, maxValue, minValue):
    newTVMatrix = TimeValueMatrix()
    newTVMatrix.MakeFromTDFAndSelectRanges(tvMatrixFilePathName, valueName, selectOp, maxValue, minValue)
    return newTVMatrix
# End - MakeTimeValueMatrixFromSelectionsOfTDF





################################################################################
# 
################################################################################
def CreateDerivedTimeValueMatrix(srcTVMatrix, opName):
    newTVMatrix = TimeValueMatrix()
    newTVMatrix.MakeDerivedValueList(srcTVMatrix, opName)
    return newTVMatrix
# End - CreateDerivedTimeValueMatrix




################################################################################
# 
################################################################################
def ReadTimeValueMatrixFromFile(tvMatrixFilePathName):
    newTVMatrix = TimeValueMatrix()
    newTVMatrix.ReadFromFile(tvMatrixFilePathName)
    return newTVMatrix
# End - ReadTimeValueMatrixFromFile



#####################################################
#
#####################################################
def TimeValueMatrix_FixMatrixFile(oldFilePath, newFilePath):
    newTVMatrix = TimeValueMatrix()
    newTVMatrix.ImportAndFix(newFilePath, oldFilePath)
# End - TimeValueMatrix_FixMatrixFile



# <><> FIXME Delete this. Some testing/debugging junk.
#TimeValueMatrix_FixMatrixFile("/home/ddean/ActiveData/researchResults/TrendsInCKD/CKDTVMatrixFilteredTimelineLengthOver10.txt",
#                "/home/ddean/ActiveData/researchResults/TrendsInCKD/NewCKDTVMatrixFilteredTimelineLengthOver10.txt")
#ReadTimeValueMatrixFromFile("/home/ddean/ActiveData/researchResults/TrendsInCKD/CKDTVMatrixFilteredTimelineLengthOver10.txt")
