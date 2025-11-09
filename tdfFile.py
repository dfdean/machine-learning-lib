#####################################################################################
# 
# Copyright (c) 2020-2025 Dawson Dean
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
# TDF - Timeline Data Format
#
# The file is xml file format that is designed to store time-series of data for medical 
# applications. All Elements have close tags, and comments are standard XML comments.
#
# To read a TDF file, we typically iterate at several levels:
#   For each partition in the file
#       For each timeline in the partition
#           For each data entry in the current timeline
#
# You do not have to iterate over partitions, so you can instead just iterate over
#   all timelines in the file. However, this allows you to have different worker processes
#   for a single file, and so avoid Python memory growth. That is important, because on very
#   large files, Python's heap can grow to consume all virtual memory and crash the process.
#
##########################################
#
# XML Syntax
# ------------
#  <TDF>
#  Parent Element: None (document root)
#  Child Elements: Head, TimelineList
#  Text Contents: None
#  Attributes: None
#
#  <Head>
#  Parent Element: TDF
#  Child Elements: Description, Created, DataSource, Events, DataValues
#  Text Contents: None
#  Attributes: None
#
#  <Vocab>
#  Parent Element: Head
#  Child Elements: None
#  Text Contents: One of the element vocabularies. Current supported values are:
#           Medicine
#  Attributes: None
#
#  <Description>
#  Parent Element: Head
#  Child Elements: None
#  Text Contents: A human readable string that describes this data.
#  Attributes: None
#
#  <DataType>
#  Parent Element: Head
#  Child Elements: None
#  Text Contents: A human readable string that describes what this data is. For medical data, this includes "TL", "Derived"
#  Attributes: None
#
#  <DataSource>
#  Parent Element: Head
#  Child Elements: None
#  Text Contents: A human readable string that describes where this data was extracted from
#  Attributes: None
#
#  <Created>
#  Parent Element: Head
#  Child Elements: None
#  Text Contents: Contains the time and data that the file was generated
#  Attributes: None
#
#  <Keywords>
#  Parent Element: Head
#  Child Elements: None
#  Text Contents: Contains a comma-separated list of Keywords
#  Attributes: None
#
#  <Events>
#  Parent Element: Head
#  Child Elements: None
#  Text Contents: Contains a comma-separated list of events
#  Attributes: None
#
#  <DataValues>
#  Parent Element: Head
#  Child Elements: None
#  Text Contents: Contains a comma-separated list of events
#  Attributes: None
#
#  <TimelineList>
#  Parent Element: TDF
#  Child Elements: A list of <TL> elements
#  Text Contents: None
#  Attributes: None
#
#
#  <TL id=nnn gender=male race=c>
#  Parent Element: TimelineList
#  Child Elements:
#     This contains all data and events for a single timeline. This related
#     data is stored as nested elements below the TL element.
#  Text Contents: None
#  Attributes: 
#       id = nnn
#           A unique id within this file. It is de-identified, so it is not
#           related to any actual MRN.
#
#       gender = "aaa" where aaa is one of:
#           M - Male
#           F - Female
#
#       race = "aaa" where aaa is one of:
#           ? - Unknown
#           W - white, caucasian
#           Af - African, African American
#           L - Latin, Hispanic
#           A - Asian
#           I - Asian Indian
#           AI - American Indian, Alaskan
#           ME - Middle Eastern
#
#
#  <E C=className V=value T=ttt V=aaa/bbb/ccc D=detail />
#  Parent Element: TL
#  Child Elements: None
#  Text Contents:
#     This element describes one or more events that happened at a time.
#     The events are a comma-separated list of words in the text of the element.
#  Attributes:
#      T="ttt" is the timestamp for when the event happened
#      C = className where className is described in TDFMedicineValues
#      V = value   where value is described in TDFMedicineValues
#      P = Priority. This is only used for RadImg
#      D - Detail 
#
#  <D C=className T=ttt>  name=value;name=value;...;name=value  </D>
#  Parent Element: Patient
#  Child Elements: None
#  Text Contents:
#   This element contains all data that is sampled at a single time.
#   An example is a Basic Metabolic Panel, which has 7 lab values, and all are
#   drawn from the same blood sample at the same time.    
#   The data values are stored as a text string of name=value pairs.
#             Na=131,K=3.7
#  Attributes:
#      T="ttt" is the timestamp for when the event happened
#
#      C = className  where className is one of:
#           L - Labs
#           V - Vitals
#           D - Diagnoses
#
#       V - A series of name value pairs, in the form:
#           name1=val1;name2=val2;name3=val3
#           The values are numbers except in a few specific cases below.
#
#  <M T=xxxx diag=value>
#  This is a medication.
#  Attributes:
#      T="ttt" is the timestamp for when the event happened
#      C = medType, which is one of the following:
#         IRx - This is an inpatient prescription. The date is when it was ordered, so it starts after this date.
#         HRx - This is a home prescription. The date is when it was ordered, so it starts after this date.
#         Rec - This is an inpatient med-rec, which is when it was reconciled. The date is the time of the med-rec, so the med was given up tp this date.
#         Mar - This is an inpatient administration, recorded in the MAR.
#         Blood - This is a transfusion
#      ST="ttt" this is a stop time. This is usually unreliable. Some hospitals set an arbitrary
#         stop time, like 1 year from start, to indicate a med that continues until it is explicitly discontinued.
#
#   The body of the element is a list of medications.
#           med1,med2,med3,......,medn
#   Where each med is a tuple string:
#       drugName:dose:doseRoute:dosesPerDay
#       Dose is a floating point number, like 12.5 or 50    
#           The units of the dose string are implied by the med, but are usually mg.
#       The dose route is:
#           i - IV
#           o - oral
#           t - topical
#       The dosesPerDay is an integer. It is assumed doses are spread out evenly over the day, so 
#       for example, 2 doses per day would imply Q12h.
#
#
#  <Text T=ttt C=nnn>  some-text   </Text>
#  Parent Element: TL
#  Child Elements: None
#  Text Contents:
#     This is a free text note or report 
#  Attributes:
#      T="ttt" is the timestamp for when the procedure was reported.
#      C="nnn" where nnn is one of:
#           Note
#
#
##########################################
#
# TimeStamps are a formatted string that is the time code. Each TimeStamp has the
# format:   
#          dd:hh:mm
# or:
#          dd:hh:mm:ss
# or:
#          dd:hh:mm:ss:ms
#
# where:
#   dd is the number of days. 
#       The number may be positive or negative depending on whether the timecode
#       is before or after the indexEvent of the timeline.
#   hh is the number of hours. 
#   mm is the number of minutes. 
#   ss is the number of seconds. This is optional and not used for medical data.
#   ms is the number of milliseconds. This is optional and not used for medical data.
#
# All numbers are 2 or more digits. They are padded with a leading 0 if the 
# number is < 10.
#
# Days are the day in your lifetime, so 365 is the 1st birthday, 3650 is the tenth birthday and
# 36500 is the 100th birthday. This representation has several advantages:
# 1. It is deidentified. It has no relation to the calendar date
# 2. It is easy to compute time intervals, like whether 2 dates are within 30 days of each other.
# 3. The same timestamp tells you when something happened in relation to all other events, and also
#   exactly how old the patient is at each event.
#
##########################################
#
# The Reader API allows clients to iterate over timelines and read values
# for a timeline. A client may specify criteria that restricts data to specific sections.
# Some example criteria for medical data include:
#     - Values while a patient is in the hospital only
#     - Everything between admission and discharge to the hospital
#     - All events between a surgery and discharge. This looks at post-operative complications.
#     - All events between dialysis and 1 day later. This looks at post-dialysis complications.
#
################################################################################
import os
import sys
import math
import re
import copy
from datetime import datetime
import numpy as np
import uuid as UUID

# Normally we have to set the search path to load these.
# But, this .py file is always in the same directories as these imported modules.
import xmlTools as dxml
import tdfTimeFunctions as timefunc

# Import g_LabValueInfo
from tdfMedicineValues import g_LabValueInfo
from tdfMedicineValues import g_FunctionInfo

# Category Variables
# We really need a public include file with just these values.
TDF_DATA_TYPE_INT                   = 0
TDF_DATA_TYPE_FLOAT                 = 1
TDF_DATA_TYPE_BOOL                  = 2
TDF_DATA_TYPE_STRING_LIST           = 3
TDF_DATA_TYPE_UNKNOWN               = -1

TDF_TIME_GRANULARITY_DAYS       = 0
TDF_TIME_GRANULARITY_SECONDS    = 1

# WARNING! These are also defined in tdfMedicineValues.py
# We really need a public include file with just these values.
# Until then, any change here must be duplicated in tdfMedicineValues.py
ANY_EVENT_OR_VALUE = "ANY"

# This is 0-based, so January is 0
g_DaysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

NEWLINE_STR = "\n"

# These separate variables in a list, or rows of variables in a sequence.
VARIABLE_LIST_SEPARATOR             = ";"
VARIABLE_ROW_SEPARATOR              = "/"

# These are the parts of a single variable name.
# A variable name can include an offset and functions
# Some examples:   a   a[3]    a.f()
VARIABLE_FUNCTION_PARAM_SEPARATOR   = ","
VARIABLE_START_OFFSET_MARKER        = "["
VARIABLE_STOP_OFFSET_MARKER         = "]"
VARIABLE_OFFSET_RANGE_MARKER        = ":"
VARIABLE_START_PARAM_ARGS_MARKER    = "("
VARIABLE_STOP_PARAM_ARGS_MARKER     = ")"
VARIABLE_FUNCTION_MARKER            = "."
VARIABLE_RANGE_LAST_MATCH_MARKER    = "@"

VARIABLE_RANGE_SIMPLE               = -1
VARIABLE_RANGE_LAST_MATCH           = 1

# BE CARFFUL - Only use 8 digits. If we do more digits, then values that
# start the same as TDF_INVALID_VALUE can become different if they are cast between 
# float and double or other conversions.
TDF_INVALID_VALUE = -314159

# This allows testing for TDF_INVALID_VALUE that is resilient to rounding errors and
# conversions between int and float. Use if (x > TDF_SMALLEST_VALID_VALUE):
# If this were C, I would use #define IS_VALID_VALUE(x) (x > TDF_SMALLEST_VALID_VALUE)
# Note, however, that times/dates (day number) and indexes are always positive, so they
# may compare to 0 to test validity.
TDF_SMALLEST_VALID_VALUE = -1000

g_TDF_Log_Buffer = ""

MIN_CR_RISE_FOR_AKI = 0.3

g_TDFHeaderPaddingStr = """____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________\
____________________________________________________________________________________________________"""


TIMELINE_OPEN_ELEMENT_PREFIX_CASE_INDEPENDANT = "<tl"
TIMELINE_CLOSE_ELEMENT_CASE_INDEPENDANT = "</tl>"




################################################################################
#
# [TDF_Log]
#
################################################################################
def TDF_Log(message):
    global g_TDF_Log_Buffer
    g_TDF_Log_Buffer += "TDF: " + message + "\n"
    print(message)
# End - TDF_Log



################################################################################
# 
# [TDF_MakeTimeStamp]
#
# This creates a formatted string that is the time code. Each timecode has the
# format:
#          dd:secInDay
# or:
#          dd:hh:mm
# or:
#          dd:hh:mm:ss
# or:
#          dd:hh:mm:ss:ms
#
# where:
#   dd is the number of days. 
#       The number may be positive or negative depending on whether the timecode
#       is before or after the indexEvent of the timeline.
#   secInDay is the number of seconds in a day
#   hh is the number of hours. 
#   mm is the number of minutes. 
#   ss is the number of seconds. This is optional and not used for medical data.
#   ms is the number of milliseconds. This is optional and not used for medical data.
#
# All numbers are 2 or more digits. They are padded with a leading 0 if the 
# number is < 10.
# There are 86400 seconds in a day
################################################################################
def TDF_MakeTimeStamp(daysInt, hoursInt, minutesInt, secondsInt):
    #print("  daysStr = " + str(daysInt))
    #print("  hoursStr = " + str(hoursInt))
    #print("  minutesStr = " + str(minutesInt))
    #print("  secondsStr = " + str(secondsInt))

    # New format: DaysInLife:SecondsInDay
    secondsInDay = int(secondsInt) + int(minutesInt * 60) + int(hoursInt * 60 * 60)
    result = str(daysInt) + ":" + str(secondsInDay)

    # Old format: dd:hh:mm:ss:ms
    #result = "{0:0>2d}:{1:0>2d}:{2:0>2d}:{2:0>2d}".format(daysInt, hoursInt, minutesInt, secondsInt)
    return result
# End - TDF_MakeTimeStamp


################################################################################
################################################################################
def TDF_MakeTimeStampSimple(daysInt, secondsInDay):
    result = str(daysInt) + ":" + str(secondsInDay)
    return result
# End - TDF_MakeTimeStampSimple




################################################################################
# 
# [TDF_ConvertTimeStampToIntSeconds]
#
# This parses a formatted string that is a time code and converts it to the
# number of seconds. Each timecode has the format:   nn:nn:nn:nn
# where:
#
#   nn is the number of days
#   nn is the number of hours
#   nn is the number of minutes 
#   nn is the number of seconds 
#
# All numbers are 2 or more digits. They are padded with a leading 0 if the 
# number is < 10.
#  
################################################################################
def TDF_ConvertTimeStampToIntSeconds(timeStampStr):
    words = timeStampStr.split(':')

    # Add days in seconds
    result = (int(words[0]) * 24 * 60 * 60)
    # Add seconds in a day
    if (len(words) == 2):
        result = result + int(words[1])
    else:
        # Add hours in hours
        result += (int(words[1]) * 60 * 60)

        # Add minutes in seconds
        result += (int(words[2]) * 60)

        # Add seconds if they are present - these are optional
        if (len(words) >= 4):
            result = result + int(words[3])
    
    return result
# End - TDF_ConvertTimeStampToIntSeconds




################################################################################
# 
# [TDF_ConvertTimeToSeconds]
#
################################################################################
def TDF_ConvertTimeToSeconds(days, hours, minutes, seconds):
    # Add days in seconds
    result = (days * 24 * 60 * 60)

    # Add hours in seconds
    result += (hours * 60 * 60)

    # Add minutes in seconds
    result += (minutes * 60)

    # Add seconds if they are present - these are optional
    if (seconds > 0):
        result += seconds

    return result
# End - TDF_ConvertTimeToSeconds






################################################################################
# 
# [TDF_ParseTimeStamp]
#
# This parses a formatted string that is a time code and converts it to separate 
# integers
################################################################################
def TDF_ParseTimeStamp(timeCode):
    if (timeCode == ""):
        TDF_Log("Error. TDF_ParseTimeStamp invalid str: " + timeCode)
        return 0, 0, 0, 0

    # This is days, hours, min
    words = timeCode.split(':')
    if (len(words) >= 4):
        return int(words[0]), int(words[1]), int(words[2]), int(words[3])
    elif (len(words) >= 3):
        return int(words[0]), int(words[1]), int(words[2]), 0
    elif (len(words) == 2):
        secInDay = int(words[1])
        minInDay = int(secInDay / 60)
        secInDay = secInDay - (minInDay * 60)
        hoursInDay = int(minInDay / 60)
        minInDay = minInDay - (hoursInDay * 60)
        return int(words[0]), hoursInDay, minInDay, secInDay
    elif (len(words) == 1):
        return int(words[0]), 0, 0, 0
    else:
        return 0, 0, 0, 0
# End - TDF_ParseTimeStamp




################################################################################
# 
# [TDF_ParseTimeStampIntoDaysSecs]
#
# This parses a formatted string that is a time code and converts it to separate 
# integers
################################################################################
def TDF_ParseTimeStampIntoDaysSecs(timeCode):
    if (timeCode == ""):
        TDF_Log("Error. TDF_ParseTimeStampIntoDaysSecs invalid str: " + timeCode)
        return 0, 0

    # This is days, hours, min
    words = timeCode.split(':')
    if (len(words) >= 4):
        seconds = int(words[3])
        minutes = int(words[2])
        hours = int(words[1])
        minInDay = minutes + int(60 * hours)
        secInDay = seconds + int(60 * minInDay)
        return int(words[0]), secInDay
    elif (len(words) >= 3):
        minutes = int(words[2])
        hours = int(words[1])
        minInDay = minutes + int(60 * hours)
        secInDay = int(60 * minInDay)
        return int(words[0]), secInDay
    elif (len(words) == 2):
        return int(words[0]), int(words[1])
    elif (len(words) == 1):
        return int(words[0]), 0
    else:
        return 0, 0
# End - TDF_ParseTimeStampIntoDaysSecs









################################################################################
#
# This is used only for writing a TDF File. Typically, it is used when importing 
# data from some other format into TDF.
#
################################################################################
class TDFFileWriter():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self):
        self.outputFileH = None
    # End -  __init__


    #####################################################
    # [TDFFileWriter::
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #
    # [TDFFileWriter::SaveAndClose]
    #
    # Called to explicitly release resources
    #####################################################
    def SaveAndClose(self):
        self.outputFileH.flush()
        self.outputFileH.close()
    # End of SaveAndClose



    #####################################################
    #
    # [TDFFileWriter::__SetFileOutputFileHandle__
    # 
    #####################################################
    def __SetFileOutputFileHandle__(self, fileH):
        self.outputFileH = fileH
    # End -  __SetFileOutputFileHandle__



    #####################################################
    #
    # [TDFFileWriter::WriteHeader]
    #
    #####################################################
    def WriteHeader(self, comment, dataSourceStr, keywordStr):
        self.outputFileH.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + NEWLINE_STR)
        self.outputFileH.write("<TDF version=\"0.1\" xmlns=\"http://www.dawsondean.com/ns/TDF/\">" + NEWLINE_STR)
        self.outputFileH.write(NEWLINE_STR)
        self.outputFileH.write("<Head>" + NEWLINE_STR)
        self.outputFileH.write("    <Vocabulary>Medicine</Vocabulary>" + NEWLINE_STR)
        self.outputFileH.write("    <VocabularyDefinition></VocabularyDefinition>" + NEWLINE_STR)
        self.outputFileH.write("    <UUID>" + str(UUID.uuid4()) + "</UUID>" + NEWLINE_STR)
        self.outputFileH.write("    <DerivedFrom></DerivedFrom>" + NEWLINE_STR)
        self.outputFileH.write("    <Description>" + comment + "</Description>" + NEWLINE_STR)    
        self.outputFileH.write("    <DataSource>" + dataSourceStr + "</DataSource>" + NEWLINE_STR)
        self.outputFileH.write("    <Created>" + datetime.today().strftime('%b-%d-%Y') + " "
                + datetime.today().strftime('%H:%M') + "</Created>" + NEWLINE_STR)
        self.outputFileH.write("    <Properties>" + keywordStr + "</Properties>" + NEWLINE_STR)
        self.outputFileH.write("    <Padding>" + g_TDFHeaderPaddingStr + "</Padding>" + NEWLINE_STR)

        self.outputFileH.write("</Head>" + NEWLINE_STR)    
        self.outputFileH.write(NEWLINE_STR)
        self.outputFileH.write("<TimelineList>" + NEWLINE_STR)    
    # End of WriteHeader




    #####################################################
    #
    # [TDFFileWriter::WriteFooter]
    #
    #####################################################
    def WriteFooter(self):
        self.outputFileH.write(NEWLINE_STR + "</TimelineList>" + NEWLINE_STR)    
        self.outputFileH.write(NEWLINE_STR + "</TDF>" + NEWLINE_STR)
        self.outputFileH.write(NEWLINE_STR + NEWLINE_STR)
    # End of WriteFooter




    #####################################################
    #
    # [TDFFileWriter::WriteXMLNode]
    #
    #####################################################
    def WriteXMLNode(self, xmlNode):
        bytesStr = xmlNode.toprettyxml(indent=' ', newl='', encoding="utf-8")
        textStr = bytesStr.decode("utf-8", "strict")  

        self.outputFileH.write(NEWLINE_STR + NEWLINE_STR)
        self.outputFileH.write(textStr)
    # End of WriteXMLNode




    ################################################################################
    # 
    # [TDFFileWriter::StartTimelineNode]
    #
    ################################################################################
    def StartTimelineNode(self, timelineID, gender, extraStr):
        textStr = NEWLINE_STR + NEWLINE_STR + "<TL"
        textStr = textStr + " id=\"" + str(timelineID) + "\""

        if ((gender is not None) and (gender != "")):
            textStr = textStr + " gender=\"" + gender + "\""

        if ((extraStr is not None) and (extraStr != "")):
            textStr = textStr + extraStr

        textStr = textStr + ">" + NEWLINE_STR

        self.outputFileH.write(textStr)
    # End - StartTimelineNode




    ################################################################################
    # 
    # [TDFFileWriter::FinishTimelineNode]
    #
    ################################################################################
    def FinishTimelineNode(self):
        self.outputFileH.write("</TL>" + NEWLINE_STR)
    # End - FinishTimelineNode




    ################################################################################
    # 
    # [TDFFileWriter::WriteDataNode]
    #
    ################################################################################
    def WriteDataNode(self, classStr, timeStampStr, optionStr, valueStr):
        xmlStr = "    <D C=\"" + classStr + "\" T=\"" + timeStampStr + "\""

        if ((optionStr is not None) and (optionStr != "")):
            optionStr = optionStr.replace(" ", "")
            xmlStr = xmlStr + " O=\"" + optionStr + "\""

        valueStr = valueStr.replace('=>', '')
        valueStr = valueStr.replace('=<', '')
        valueStr = valueStr.replace('>=', '')
        valueStr = valueStr.replace('<=', '')
        valueStr = valueStr.replace('>', '')
        valueStr = valueStr.replace('<', '')
        valueStr = valueStr.replace('+', '')
        valueStr = valueStr.replace('-', '')
        valueStr = valueStr.replace(' ', '')

        xmlStr = xmlStr + ">" + valueStr + "</D>" + NEWLINE_STR
        self.outputFileH.write(xmlStr)
    # End - WriteDataNode



    ################################################################################
    # 
    # [TDFFileWriter::WriteEventNode]
    #
    ################################################################################
    def WriteEventNode(self, eventType, timeStampStr, calendarTimeStr, stopTimeStr, valueStr, detailStr):
        xmlStr = "    <E C=\"" + eventType + "\" T=\"" + timeStampStr + "\""

        if ((calendarTimeStr is not None) and (calendarTimeStr != "")):
            # Remove characters that would create an invalid XML file.
            calendarTimeStr = calendarTimeStr.replace('>', '') 
            calendarTimeStr = calendarTimeStr.replace('<', '') 
            calendarTimeStr = calendarTimeStr.replace('=>', '')
            xmlStr = xmlStr + " CT=\"" + calendarTimeStr + "\""

        if ((stopTimeStr is not None) and (stopTimeStr != "")):
            xmlStr = xmlStr + "ST=\"" + timeStampStr + "\""

        if ((valueStr is not None) and (valueStr != "")):
            # Remove characters that would create an invalid XML file.
            valueStr = valueStr.replace('=>', '')
            valueStr = valueStr.replace('=<', '')
            valueStr = valueStr.replace('>=', '')
            valueStr = valueStr.replace('<=', '')
            valueStr = valueStr.replace('>', '')
            valueStr = valueStr.replace('<', '')
            valueStr = valueStr.replace("+", '')
            valueStr = valueStr.replace("-", '')
            valueStr = valueStr.replace(" ", '')
            xmlStr = xmlStr + " V=\"" + valueStr + "\""

        if ((detailStr is not None) and (detailStr != "")):
            # Remove characters that would create an invalid XML file.
            detailStr = detailStr.replace('=>', '')
            detailStr = detailStr.replace('=<', '')
            detailStr = detailStr.replace('>=', '')
            detailStr = detailStr.replace('<=', '')
            detailStr = detailStr.replace('>', '')
            detailStr = detailStr.replace('<', '')
            detailStr = detailStr.replace('+', '')
            detailStr = detailStr.replace('-', '')
            detailStr = detailStr.replace(' ', '')
            xmlStr = xmlStr + " D=\"" + detailStr + "\""

        xmlStr = xmlStr + " />" + NEWLINE_STR

        self.outputFileH.write(xmlStr)
    # End - WriteEventNode




    ################################################################################
    # 
    # [TDFFileWriter::WriteTextNode]
    #
    ################################################################################
    def WriteTextNode(self, textType, extraAttributeName, extraAttributeValue, textStr):
        # Remove characters that would create an invalid XML file.
        textStr = textStr.replace('>', '') 
        textStr = textStr.replace('<', '') 
        textStr = textStr.replace("=<", "")
        textStr = textStr.replace("=", "")
        textStr = textStr.replace("=>", "")

        xmlStr = "    <Text C=\"" + textType + "\""
        if ((extraAttributeName != "") and (extraAttributeValue != "")):
            xmlStr = xmlStr + " " + extraAttributeName + "=\"" + extraAttributeValue + "\""
        xmlStr = xmlStr + ">"

        xmlStr = xmlStr + textStr + "</Text>" + NEWLINE_STR

        self.outputFileH.write(xmlStr)
    # End - WriteTextNode




    ################################################################################
    # 
    # [TDFFileWriter::AppendNameValuePairToStr]
    #
    ################################################################################
    def AppendNameValuePairToStr(self, totalStr, name, valueStr):
        if ((name is None) or (valueStr is None)):
            print("Error. AppendNameValuePairToStr discarding NONE name or value str")
            return totalStr

        #name = name.lstrip()
        #valueStr = valueStr.lstrip()
        # Remove characters that would create an invalid XML file.
        valueStr = valueStr.replace('=>', '')
        valueStr = valueStr.replace('=<', '')
        valueStr = valueStr.replace('>=', '')
        valueStr = valueStr.replace('<=', '')
        valueStr = valueStr.replace('>', '')
        valueStr = valueStr.replace('<', '')

        if ((name == "") or (valueStr == "")):
            print("Error. AppendNameValuePairToStr discarding empty name str. name=" + name + ", valueStr=" + valueStr )
            return totalStr    

        try:
            # Lint gets upset that I do not use this, but I am only doing it to check the conversion works.
            dummyFloatVal = float(valueStr)
        except Exception:
            print("Error. AppendNameValuePairToStr discarding non-numeric valueStr: " + str(valueStr))
            return totalStr    

        totalStr = totalStr + name + "=" + valueStr + ","
        return totalStr
    # End - AppendNameValuePairToStr

# End - class TDFFileWriter





################################################################################
# 
# [TDFFileWriter_AppendMedInfoToStr]
#
# This builds up a comma-separated list of values, each has the form:
#       medName:dose:route:doseRoute:dosesPerDayStr
# Optionally
#       medName:dose:route:doseRoute:dosesPerDayStr-StopDay
#
# Dose is a string of a float (like 12.5)
# The dose Units is implied by the drug. For example, most PO meds are mg, 
# while insulin is Units, creams are applications, inhaleds are puffs, etc.
#
# doseRoute is "i", "o", 't', ...
# The route matters, for example, Lasix IV is approx 2x lasix PO.
################################################################################
def TDFFileWriter_AppendMedInfoToStr(totalStr, drugName, doseStr, doseRoute, dosesPerDayStr, stopDayStr):
    if ((drugName is None) or (drugName == "") or (totalStr is None)):
        print("Error. TDFFileWriter_AppendMedInfoToStr discarding NONE name or value str")
        return totalStr

    try:
        # Lint gets upset that I do not use this, but I am only doing it to check the conversion works.
        dummyFloatVal = float(doseStr)
    except Exception:
        print("Error. TDFFileWriter_AppendMedInfoToStr discarding non-numeric doseStr: " + str(doseStr))
        return totalStr

    if (doseRoute == ""):
        doseRoute = "o"
    if (dosesPerDayStr == ""):
        dosesPerDayStr = "0"


    if (dosesPerDayStr != ""):
        try:
            # Lint gets upset that I do not use this, but I am only doing it to check the conversion works.
            dummyDosesPerDayInt = float(dosesPerDayStr)
        except Exception:
            print("Error. TDFFileWriter_AppendMedInfoToStr discarding non-numeric dosesPerDayStr: " + str(dosesPerDayStr))
            return totalStr
    # End - if (dosesPerDayStr != ""):
    if (dosesPerDayStr == ""):
        dosesPerDayStr = "1"

    if (stopDayStr != ""):
        totalStr = totalStr + drugName + ":" + doseStr + ":" + doseRoute + ":" + dosesPerDayStr + "-" + stopDayStr + ","
    else:
        totalStr = totalStr + drugName + ":" + doseStr + ":" + doseRoute + ":" + dosesPerDayStr + ","

    return totalStr
# End - TDFFileWriter_AppendMedInfoToStr





################################################################################
# 
# [TDFFileWriter_AppendProcInfoToStr]
#
# This builds up a comma-separated list of values, each has the form:
#       procSubType:cptCode
#
# procType is a string: Proc or Surg
# procSubType is a string: EGD, ERCP, Colonoscopy, or Major/Endo
# 
################################################################################
def TDFFileWriter_AppendProcInfoToStr(totalStr, procSubType, cptCode):
    if ((procSubType is None) or (procSubType == "") or (totalStr is None)):
        print("Error. TDFFileWriter_AppendProcInfoToStr discarding NONE name or value str")
        return totalStr

    totalStr = totalStr + procSubType + ":" + cptCode + ","
    return totalStr
# End - TDFFileWriter_AppendProcInfoToStr






################################################################################
#
# This is used to read a TDF file. It is read-only, and is designed to be called
# by a Neural Net or similar program.
################################################################################
class TDFFileReader():
    #####################################################
    #
    # [TDFFileReader::__init__]
    #
    #####################################################
    def __init__(self, tdfFilePathName, inputNameListStr, resultValueName, 
                    requirePropertyNameList, timeGranularity, fCarryForwardPreviousDataValues):
        super().__init__()

        # Save the parameters
        self.tdfFilePathName = tdfFilePathName
        self.fileHandle = None

        # Initialize some parsing control options to their default values.
        # These may be overridden later.
        self.fCarryForwardPreviousDataValues = fCarryForwardPreviousDataValues
        self.ConvertResultsToBools = False
        self.TimeGranularity = timeGranularity

        #######################
        # Initialize Parsing Variables
        # This is also done when we start parsing each time.
        # But a lot of the static code checkers want all member variables initialized in the constructor.
        # And that seems to be a good practice.
        self.CurrentTimelineID = TDF_INVALID_VALUE
        self.CurrentIsMale = 1
        self.CurrentWtInKg = TDF_INVALID_VALUE
        self.currentTimelineNode = None
        self.currentTimelineXMLDOM = None

        self.CompiledTimeline = []

        self.latestTimelineEntryDataList = {}
        self.latestTimeLineEntry = None

        self.StartCKD5Date = TDF_INVALID_VALUE
        self.StartCKD4Date = TDF_INVALID_VALUE
        self.StartCKD3bDate = TDF_INVALID_VALUE
        self.StartCKD3aDate = TDF_INVALID_VALUE
        self.NextFutureDischargeDate = TDF_INVALID_VALUE

        self.OutcomeImprove = TDF_INVALID_VALUE
        self.OutcomeWorsen = TDF_INVALID_VALUE
        self.OutcomeFutureEndStage = TDF_INVALID_VALUE

        self.FutureBaselineCr = TDF_INVALID_VALUE
        self.baselineCrSeries = None
        self.varIndexThatMustBeNonZero = -1
        self.maxZeroDays = -1
        self.DaysSincePrevResultIndex = -1

        ###################
        self.ParseVariableList(inputNameListStr, resultValueName, requirePropertyNameList)

        ###################
        # Open the file.
        # Opening in binary mode is important. I do seek's to arbitrary positions
        # and that is only allowed when a file is opened in binary.
        try:
            self.fileHandle = open(self.tdfFilePathName, 'rb') 
        except Exception:
            TDF_Log("Error from opening TDF file. File=" + self.tdfFilePathName)
            return
        self.lineNum = 0

        ####################
        # Read the file header as a series of text lines and create a single
        # large text string for just the header. Stop at the body, which may
        # be quite large, and may not fit in in memory all at once.
        self.fileHeaderStr = ""        
        while True: 
            # Get next line from file 
            try:
                binaryLine = self.fileHandle.readline() 
            except UnicodeDecodeError as err:
                print("Unicode Error from reading Lab file. lineNum=" + str(self.lineNum) + ", err=" + str(err))
                continue
            except Exception:
                print("Error from reading Lab file. lineNum=" + str(self.lineNum))
                continue
            self.lineNum += 1

            # Convert the text from Unicode to ASCII. 
            try:
                currentLine = binaryLine.decode("ascii", "ignore")
            except UnicodeDecodeError as err:
                print("Unicode Error from converting string. lineNum=" + str(self.lineNum) + ", err=" + str(err))
                continue
            except Exception:
                print("Error from converting string. lineNum=" + str(self.lineNum))
                continue

            # Quit if we hit the end of the file.
            if (currentLine == ""):
                break
            self.fileHeaderStr += currentLine

            # Remove whitespace, including the trailing newline.
            currentLine = currentLine.rstrip().lstrip().lower()
            if (currentLine == "</head>"):
                break
        # End - Read the file header

        # Add a closing element to make the header string into a complete XML string, 
        # and then we can parse it into XML
        self.fileHeaderStr += "</TDF>"
        #print("__init__. Header str=" + self.fileHeaderStr)
        self.headerXMLDOM = dxml.XMLTools_ParseStringToDOM(self.fileHeaderStr)
        if (self.headerXMLDOM is None):
            TDF_Log("TDFFileReader::__init__. Error from parsing string:")

        self.headerNode = dxml.XMLTools_GetNamedElementInDocument(self.headerXMLDOM, "Head")
        if (self.headerNode is None):
            print("TDFReader.__init__. Head elements is missing: [" + self.fileHeaderStr + "]")
            return

        # Initalize the iterator to start at the beginning.
        self.currentTimelineNodeStr = ""
        self.LastTimeLineIndex = TDF_INVALID_VALUE
    # End -  __init__



    #####################################################
    #
    # [TDFFileReader::__del__]
    #
    # Destructor. This method is part of any class
    #####################################################
    def __del__(self):
        self.Shutdown()
    # End of destructor



    #####################################################
    #
    # [TDFFileReader::Shutdown]
    #
    # Called to explicitly release resources
    #####################################################
    def Shutdown(self):
        if (self.fileHandle is not None):
            try:
                self.fileHandle.close()
            except Exception:
                pass
        self.fileHandle = None
    # End of Shutdown


    #####################################################
    # [TDFFileReader::SetConvertResultsToBools]
    #####################################################
    def SetConvertResultsToBools(self, fConvertResultsToBools):
        self.ConvertResultsToBools = fConvertResultsToBools


    #####################################################
    # [TDFFileReader::SetCarryForwardPreviousDataValues]
    #####################################################
    def SetCarryForwardPreviousDataValues(self, fEnabled):
        self.fCarryForwardPreviousDataValues = fEnabled


    #####################################################
    # [TDFFileReader::SetTimeGranularity]
    #####################################################
    def SetTimeGranularity(self, fValue):
        self.TimeGranularity = fValue


    #####################################################
    #
    # [TDFFileReader::ParseVariableList]
    #
    #####################################################
    def ParseVariableList(self, inputNameListStr, resultValueName, requirePropertyNameList):
        self.DaysSincePrevResultIndex = -1

        # Get information about the requested variables. Each variable may be a simple value, 
        # like "Cr", or a value at an offset, like "Cr[-1]" or a function like Cr.rate
        # Note, one name may appear several times in the list, but have different functions
        # or offsets.
        self.allValueVarNameList = inputNameListStr.split(VARIABLE_LIST_SEPARATOR)

        # Before we expand the list, count how many vars we return to teh client.
        self.numInputValues = len(self.allValueVarNameList)

        # Get information about the result. However, this is optional
        if ((resultValueName is not None) and (resultValueName != "")):
            self.resultLabInfo, self.resultValueName, self.resultValueOffsetStartRange, self.resultValueOffsetStopRange, self.resultValueOffsetRangeOption, _ = TDF_ParseOneVariableName(resultValueName)
            if (self.resultLabInfo is None):
                TDF_Log("ERROR TDFFileReader::ParseVariableList Undefined resultValueName: " + resultValueName)
                sys.exit(0)
            self.resultDataType = self.resultLabInfo['dataType']
        else:
            self.resultValueName = ""
            self.resultLabInfo = None
            self.resultValueOffsetStartRange = 0
            self.resultValueOffsetStopRange = 0
            self.resultValueOffsetRangeOption = VARIABLE_RANGE_SIMPLE
            self.resultDataType = TDF_DATA_TYPE_INT

        # Add any other variables we will use. This will include params for start/stop and criteria
        # The list starts with the valiables used for inputs. So, the contents of the total array
        # will look like this:
        # ------------------------------------------------------
        # | Inputs | Outputs | Filtering Values | Dependencies |
        # ------------------------------------------------------
        if (self.resultValueName != ""):
            self.allValueVarNameList.append(self.resultValueName)
        if (requirePropertyNameList is not None):
            for _, nameStr in enumerate(requirePropertyNameList):
                self.allValueVarNameList.append(nameStr)

        # Parse the initial list of variables needed.
        # This may not be all; once we closely look at the variables, we may
        # realize we need more variables to compute derived values.
        numVarsInFullNameList = len(self.allValueVarNameList)
        self.allValuesLabInfoList = [None] * numVarsInFullNameList
        self.AllValuesOffsetStartRange = [0] * numVarsInFullNameList
        self.AllValuesOffsetStopRange = [0] * numVarsInFullNameList
        self.AllValuesOffsetRangeOption = [0] * numVarsInFullNameList
        self.allValuesFunctionNameList = [""] * numVarsInFullNameList
        self.allValuesFunctionObjectList = [None] * numVarsInFullNameList
        # Each iteration parses a single variable.
        for valueIndex, valueName in enumerate(self.allValueVarNameList):
            labInfo, valueName, valueStartOffsetRange, valueStopOffsetRange, valueRangeOption, functionName = TDF_ParseOneVariableName(valueName)

            self.allValueVarNameList[valueIndex] = valueName
            self.allValuesLabInfoList[valueIndex] = labInfo
            self.AllValuesOffsetStartRange[valueIndex] = valueStartOffsetRange
            self.AllValuesOffsetStopRange[valueIndex] = valueStopOffsetRange
            self.AllValuesOffsetRangeOption[valueIndex] = valueRangeOption
            self.allValuesFunctionNameList[valueIndex] = functionName

            if (valueName == "DaysSincePrev"):
                self.DaysSincePrevResultIndex = valueIndex
            # End - if (valueName == "DaysSincePrev"):
        # End - for valueIndex, valueName in enumerate(inputValueNameList):

        # Use the variable name stem (found by parsing the full variable names) 
        # and look these up in the dictionary to pull in all dependencies.
        # This will also look up dependency variables in the dictionary.
        #
        # I use an old-fashioned C-style loop here because I am iterating through the
        # array as I am also growing the array. So, the stop index may be different for each 
        # loop iteration.
        index = 0
        while (True):
            if (index >= len(self.allValueVarNameList)):
                break

            valueName = self.allValueVarNameList[index]
            labInfo = self.allValuesLabInfoList[index]
            # If some dependency variables were added to the list on a previous iteration, then 
            # we may need to  parse them now.
            if (labInfo is None):
                TDF_Log("\n\n\nERROR!! TDFFileReader::ParseVariableList Did not have a parsed variable for [" + valueName + "]")
                print("self.allValueVarNameList = " + str(self.allValueVarNameList))
                raise ValueError('A very specific bad thing happened.')
            # End - if (labInfo == None)

            if (self.allValuesFunctionNameList[index] != ""):
                self.allValuesFunctionObjectList[index] = timefunc.CreateTimeValueFunction(
                                                                        self.TimeGranularity,
                                                                        self.allValuesFunctionNameList[index],
                                                                        self.allValueVarNameList[index])
                if (self.allValuesFunctionObjectList[index] is None):
                    print("\n\n\nERROR!! TDFFileReader::ParseVariableList Undefined function: " 
                            + self.allValuesFunctionNameList[index])
                    sys.exit(0)
            # End - if (self.allValuesFunctionNameList[index] != ""):

            # Now, grow the list of input variables by pulling in any dependencies.
            # The user may request a derived variable, which means we have to also collect any 
            # dependencies that are used to derive that variable.
            variableNameListStr = labInfo['VariableDependencies']
            if (variableNameListStr != ""):
                variableNameList = variableNameListStr.split(";")
                if (variableNameList is not None):
                    for _, nameStr in enumerate(variableNameList):
                        labInfo, valueName, valueStartOffsetRange, valueStopOffsetRange, valueRangeOption, functionName = TDF_ParseOneVariableName(nameStr)

                        # This is a bit subtle.
                        # The names in the list will be pulled in whenever they are available.
                        # It does not matter if the original variable name specified an offset like Cr[-3]
                        # So, for example, even if Cr is in the list as part of Cr[-3], a new Cr dependency
                        # does NOT need to be added. The original Cr, even with the offset, will cause the
                        # code that compiles a timeline to store every instance of a Cr in the file.
                        # So, avoid unnecessary duplicate names.
                        #
                        # HOWEVER! input variables specified by the user may include functions. We need
                        # a different function state, so if we have 2 input variables that are different
                        # functions applied to the same value (like "Cr.rate" and Cr.accel") then we need
                        # separate entries, with duplicated base variable.
                        if ((valueName != "") and (valueName not in self.allValueVarNameList)):
                            self.allValueVarNameList.append(valueName)
                            self.allValuesLabInfoList.append(labInfo)
                            self.AllValuesOffsetStartRange.append(valueStartOffsetRange)
                            self.AllValuesOffsetStopRange.append(valueStopOffsetRange)
                            self.AllValuesOffsetRangeOption.append(valueRangeOption)
                            self.allValuesFunctionNameList.append(functionName)
                            self.allValuesFunctionObjectList.append(None)
                    # End - for _, nameStr in enumerate(variableNameList):
                # End - if (variableNameList is not None):
            # End - if (variableNameListStr != ""):

            index += 1
        # End - while (True):


        # Some values (like meds) can be 0 for a few days at most when we return a series of data,
        # but not for extended periods of time.
        self.varIndexThatMustBeNonZero = -1
        self.maxZeroDays = -1
        for labInfoIndex, labInfo in enumerate(self.allValuesLabInfoList):
            try:
                if ('MaxDaysWithZero' in labInfo):
                    self.maxZeroDays = labInfo['MaxDaysWithZero']
                    self.varIndexThatMustBeNonZero = labInfoIndex
                    break
            except Exception:
                pass
        # End - for labInfoIndex, labInfo in enumerate(self.allValuesLabInfoList):
    # End -  ParseVariableList



    #####################################################
    #
    # [TDFFileReader::GetRawXMLStrForHeader]
    #
    # This is used by the TDF writer class when making
    # a derived TDF file from an original source.
    #####################################################
    def GetRawXMLStrForHeader(self):
        resultStr = self.fileHeaderStr

        # Remove the </TDF> we added to make it parseable.
        resultStr = resultStr[:-6]
        # Add the TimelineList element.
        resultStr = resultStr + "<TimelineList>"

        return resultStr
    # End of GetRawXMLStrForHeader



    #####################################################
    #
    # [TDFFileReader::GetRawXMLStrForFooter]
    #
    # This is used by the TDF writer class when making
    # a derived TDF file from an original source.
    #####################################################
    def GetRawXMLStrForFooter(self):
        footerStr = "\n\n</TimelineList>\n</TDF>\n\n"
        return footerStr
    # End of GetRawXMLStrForFooter



    #####################################################
    #
    # [TDFFileReader::GetRawXMLStrForFirstTimeline]
    #
    # Returns a string for the XML of the first Timeline.
    # This is used by the TDF writer class when making
    # a derived TDF file from an original source.
    #####################################################
    def GetRawXMLStrForFirstTimeline(self):
        fFoundTimeline, _, _, _ = self.GotoFirstTimelineEx(True)
        if (not fFoundTimeline):
            return ""

        return self.currentTimelineNodeStr
    # End - GetRawXMLStrForFirstTimeline(self)



    #####################################################
    #
    # [TDFFileReader::GetRawXMLStrForNextTimeline]
    #
    # Returns a string for the XML of the next Timeline.
    # This is used by the TDF writer class when making
    # a derived TDF file from an original source.
    #####################################################
    def GetRawXMLStrForNextTimeline(self):
        fFoundTimeline, fEOF, _, _ = self.ReadNextTimelineXMLStrImpl(TDF_INVALID_VALUE)
        if ((not fFoundTimeline) or (fEOF)):
            return None

        # We parse so the reader will also be able to examine properties in the timeline.
        # This lets us split a large file by properties
        fFoundTimeline = self.ParseCurrentTimelineImpl()
        if ((not fFoundTimeline) or (fEOF)):
            return None

        return self.currentTimelineNodeStr
    # End - GetRawXMLStrForNextTimeline(self)




    #####################################################
    #
    # [TDFFileReader::GetRawValues]
    #
    # This returns one list of values, and is used when we 
    # preflight.
    #####################################################
    def GetRawValues(self, valueName, fUniqueValues, fOnlyOneValuePerTimeEntry):
        prevValue = TDF_INVALID_VALUE
        prevTimeCode = -1
        valueList = []

        # Get information about the requested variables. This splits
        # complicated name values like "eGFR[-30]" into a name and an 
        # offset, like "eGFR" and "-30"
        labInfo, nameStem, _, _, _, functionName = TDF_ParseOneVariableName(valueName)
        if (labInfo is None):
            TDF_Log("!Error! Cannot parse variable: " + valueName)
            return valueList

        # This loop will iterate over each step in the timeline.
        for timeLineIndex in range(self.LastTimeLineIndex + 1):
            timelineEntry = self.CompiledTimeline[timeLineIndex]
            currentTimeCode = timelineEntry['TimeCode']
            if ((fOnlyOneValuePerTimeEntry) and (prevTimeCode == currentTimeCode)):
                continue

            latestValues = timelineEntry['data']
            if (nameStem not in latestValues):
                continue

            value = latestValues[nameStem]
            try:
                valueFloat = float(value)
            except Exception:
                valueFloat = TDF_INVALID_VALUE
            if ((valueFloat == TDF_INVALID_VALUE) or (valueFloat <= TDF_SMALLEST_VALID_VALUE)):
                continue

            if ((fUniqueValues) and (prevValue != TDF_INVALID_VALUE) and (prevValue == valueFloat)):
                continue

            newDict = {"Time": currentTimeCode, "Val": valueFloat, "Day": timelineEntry['Day'], "Sec": timelineEntry['Sec']}
            valueList.append(newDict)
            prevTimeCode = currentTimeCode
            prevValue = valueFloat
        # End - for timeLineIndex in range(self.LastTimeLineIndex + 1)

        return valueList
    # End - GetRawValues()





    #####################################################
    #
    # [TDFFileReader::GetRawAllValuesPerDay]
    #
    #####################################################
    def GetRawAllValuesPerDay(self):
        listOfAllDaysValues = []
        fOnlyOneValuePerTimeEntry = True

        # This loop will iterate over each step in the timeline.
        prevDayNum = -1
        prevDayDict = None
        for timeLineIndex in range(self.LastTimeLineIndex + 1):
            timelineEntry = self.CompiledTimeline[timeLineIndex]
            currentTimeCode = timelineEntry['TimeCode']
            currentDay, secs = TDF_ParseTimeStampIntoDaysSecs(currentTimeCode)
            latestValues = timelineEntry['data']

            if ((fOnlyOneValuePerTimeEntry) and (prevDayNum == currentDay) and (prevValueDict is not None)):
                currentDayDict = prevDayDict
            else:
                # Start a new day
                currentDayDict = {'D': currentDay}

                # Record this for next time
                prevDayNum = currentDay
                prevDayDict = currentDayDict
            # End of starting a new day

            # Now, add each value
            for _, (varName, varStr) in enumerate(latestValues.items()):
                try:
                    valueFloat = float(varStr)
                except Exception:
                    valueFloat = TDF_INVALID_VALUE
                if ((valueFloat == TDF_INVALID_VALUE) or (valueFloat <= TDF_SMALLEST_VALID_VALUE)):
                    continue

                currentDayDict[varName] = valueFloat
            # End - for _, (varName, varFloat) in enumerate(latestValues.items()):
        # End - for timeLineIndex in range(self.LastTimeLineIndex + 1)

        return listOfAllDaysValues
    # End - GetRawAllValuesPerDay






    #####################################################
    # [TDFFileReader::GetXMLNodeForCurrentTimeline]
    #####################################################
    def GetXMLNodeForCurrentTimeline(self):
        return self.currentTimelineNode


    #####################################################
    # [TDFFileReader::GetNumInputValues]
    #####################################################
    def GetNumInputValues(self):
        return self.numInputValues


    #####################################################
    # [TDFFileReader::GetAllValueVarNameList]
    #####################################################
    def GetAllValueVarNameList(self):
        return self.allValueVarNameList


    #####################################################
    # [TDFFileReader::GetFileUUIDStr]
    #####################################################
    def GetFileUUIDStr(self):
        xmlStr = dxml.XMLTools_GetChildNodeTextAsStr(self.headerNode, "UUID", "")
        return xmlStr
    # End of GetFileUUIDStr


    #####################################################
    # [TDFFileReader::GetCurrentTimelineID]
    #####################################################
    def GetCurrentTimelineID(self):
        return self.CurrentTimelineID



    #####################################################
    #
    # [TDFFileReader::GotoFirstTimeline]
    #
    # Returns a single boolean fFoundTimeline
    #   This is True iff the procedure found a valid timeline entry.
    #   This is False if it hit the end of the file
    #####################################################
    def GotoFirstTimeline(self):
        fFoundTimeline, _, _, _ = self.GotoFirstTimelineEx(False)
        return fFoundTimeline
    # End - GotoFirstTimeline




    #####################################################
    #
    # [TDFFileReader::GotoFirstTimelineEx]
    #
    # This returns more information than GotoFirstTimeline
    #
    # Returns a single boolean fFoundTimeline
    #   This is True iff the procedure found a valid timeline entry.
    #   This is False if it hit the end of the file
    #####################################################
    def GotoFirstTimelineEx(self, fOnlyFindTimelineBoundaries):
        self.fileHandle.seek(0, 0)

        # Advance in the file to the start of the timeline list
        while True: 
            # Get next line from file 
            try:
                binaryLine = self.fileHandle.readline() 
            except UnicodeDecodeError as err:
                print("Unicode Error from reading Lab file. lineNum=" + str(self.lineNum) + ", err=" + str(err))
                continue
            except Exception:
                print("Error from reading Lab file. lineNum=" + str(self.lineNum))
                continue
            self.lineNum += 1

            # Convert the text from Unicode to ASCII. 
            try:
                currentLine = binaryLine.decode("ascii", "ignore")
            except UnicodeDecodeError as err:
                print("Unicode Error from converting string. lineNum=" + str(self.lineNum) + ", err=" + str(err))
                continue
            except Exception:
                print("Error from converting string. lineNum=" + str(self.lineNum))
                continue

            # If we hit the end of the file, then we did not find a next timeline.
            if (currentLine == ""):
                return False, False, TDF_INVALID_VALUE, TDF_INVALID_VALUE

            # Remove whitespace, including the trailing newline.
            currentLine = currentLine.rstrip()
            currentLine = currentLine.lstrip()
            #TDF_Log("GotoFirstTimelineEx. currentLine=" + currentLine)
            if (currentLine == "<TimelineList>"):
                break
        # End - Advance to the first timeline

        # Now, go to the first timeline
        fFoundTimeline, fEOF, startTimelinePosInFile, stopTimelinePosInFile = self.GotoNextTimelineEx(fOnlyFindTimelineBoundaries)

        return fFoundTimeline, fEOF, startTimelinePosInFile, stopTimelinePosInFile
    # End - GotoFirstTimelineEx




    #####################################################
    #
    # [TDFFileReader::GotoNextTimeline]
    #
    # Returns a single boolean fFoundTimeline
    #   This is True iff the procedure found a valid timeline entry.
    #   This is False if it hit the end of the file
    #####################################################
    def GotoNextTimeline(self):
        fFoundTimeline, _, _, _ = self.GotoNextTimelineEx(False)
        return fFoundTimeline
    # End - GotoNextTimeline(self)




    #####################################################
    #
    # [TDFFileReader::GotoNextTimelineEx]
    # This returns more information than GotoNextTimeline
    #####################################################
    def GotoNextTimelineEx(self, fOnlyFindTimelineBoundaries):
        fFoundTimeline, fEOF, startTimelinePosInFile, stopTimelinePosInFile = self.ReadNextTimelineXMLStrImpl(TDF_INVALID_VALUE)
        if ((not fFoundTimeline) or (fEOF)):
            return False, False, 0, 0

        if (not fOnlyFindTimelineBoundaries):
            fFoundTimeline = self.ParseCurrentTimelineImpl()

        return fFoundTimeline, fEOF, startTimelinePosInFile, stopTimelinePosInFile
    # End - GotoNextTimelineEx(self)





    #####################################################
    #
    # [TDFFileReader::ReadTimelineAtKnownPosition]
    #
    #####################################################
    def ReadTimelineAtKnownPosition(self, startTimelinePosInFile, stopTimelinePosInFile):
        timelineLength = stopTimelinePosInFile - startTimelinePosInFile
        self.currentTimelineNodeStr = ""

        try:
            self.fileHandle.seek(startTimelinePosInFile, 0)
            dataBytes = self.fileHandle.read(timelineLength)
        except Exception:
            return False

        # Convert the text from Unicode to ASCII. 
        try:
            myStr = dataBytes.decode("ascii", "ignore")
        except UnicodeDecodeError:
            return False
        except Exception:
            return False

        self.currentTimelineNodeStr = myStr
        fFoundTimeline = self.ParseCurrentTimelineImpl()
        if (not fFoundTimeline):
            print("ReadTimelineAtKnownPosition. Error! Read data = [" + myStr + "] fFoundTimeline = " + str(fFoundTimeline))
            print("\n\nReadTimelineAtKnownPosition. BAIL\n\n")
            sys.exit(0)

        return fFoundTimeline
    # End - ReadTimelineAtKnownPosition




    #####################################################
    #
    # [TDFFileReader::GotoFirstTimelineInPartition]
    #
    # This returns two values: fFoundTimeline, fEOF
    #   fFoundTimeline - True if we read a complete timeline
    #   fEOF - True if we hit the end of the file
    #
    # This will find the next timeline that starts within the
    # current partition. The selected timeline may extend beyond
    # the end of the partition, which is OK. 
    #####################################################
    def GotoFirstTimelineInPartition(self, startTimelinePosInFile, stopTimelinePosInFile, 
                                startPartition, stopPartition, fOnlyFindTimelineBoundaries):
        fFoundTimeline = False
        fEOF = False

        # If we already know the position of the timeline, then just read
        # it. We don't need to find it.
        if ((startTimelinePosInFile > 0) and (stopTimelinePosInFile > 0)):
            fFoundTimeline = self.ReadTimelineAtKnownPosition(startTimelinePosInFile, stopTimelinePosInFile)
            return fFoundTimeline, fEOF, startTimelinePosInFile, stopTimelinePosInFile

        # Otherwise, we are looking for the timeline in the file.
        # If this is the beginning of the file, then skip over the header.
        if (startPartition == 0):
            fFoundTimeline, fEOF, startTimelinePosInFile, stopTimelinePosInFile = self.GotoFirstTimelineEx(fOnlyFindTimelineBoundaries)
            if (not fFoundTimeline):
                fEOF = True
            return fFoundTimeline, fEOF, startTimelinePosInFile, stopTimelinePosInFile

        # Otherwise, jump to the partition starting position. 
        # Note, the partition boundaries are arbitrary byte positions, so
        # this may jump to the middle of a line of text. That is OK, since
        # we will still advance until we see a valid start of a timeline element.
        self.fileHandle.seek(startPartition, 0)

        # Now, go to the first timeline
        fFoundTimeline, fEOF, startTimelinePosInFile, stopTimelinePosInFile = self.GotoNextTimelineInPartition(TDF_INVALID_VALUE, 
                                                                                TDF_INVALID_VALUE,
                                                                                stopPartition,
                                                                                fOnlyFindTimelineBoundaries)

        return fFoundTimeline, fEOF, startTimelinePosInFile, stopTimelinePosInFile
    # End - GotoFirstTimelineInPartition






    #####################################################
    #
    # [TDFFileReader::GotoNextTimelineInPartition]
    #
    # This returns two values: fFoundTimeline, fEOF
    #   fFoundTimeline - True if we read a complete timeline
    #   fEOF - True if we hit the end of the file
    #
    # This will find the next timeline that starts within the
    # current partition. The selected timeline may extend beyond
    # the end of the partition, which is OK. 
    #####################################################
    def GotoNextTimelineInPartition(self, startTimelinePosInFile, stopTimelinePosInFile, 
                                    stopPartition, fOnlyFindTimelineBoundaries):
        # If we already know the position of the timeline, then just read
        # it. We don't need to find it.
        if ((startTimelinePosInFile > 0) and (stopTimelinePosInFile > 0)):
            fEOF = False
            fFoundTimeline = self.ReadTimelineAtKnownPosition(startTimelinePosInFile, stopTimelinePosInFile)
            return fFoundTimeline, fEOF, startTimelinePosInFile, stopTimelinePosInFile

        fFoundTimeline, fEOF, startTimelinePosInFile, stopTimelinePosInFile = self.ReadNextTimelineXMLStrImpl(stopPartition)
        if ((not fFoundTimeline) or (fEOF)):
            return fFoundTimeline, fEOF, startTimelinePosInFile, stopTimelinePosInFile

        if (not fOnlyFindTimelineBoundaries):
            fFoundTimeline = self.ParseCurrentTimelineImpl()

        return fFoundTimeline, fEOF, startTimelinePosInFile, stopTimelinePosInFile
    # End - GotoNextTimelineInPartition(self)





    #####################################################
    #
    # [TDFFileReader::ReadNextTimelineXMLStrImpl]
    #
    # This returns four values:
    #   fFoundTimeline - True if we read a complete timeline
    #   fEOF - True if we hit the end of the file
    #   startTimelinePosInFile - Where valid timeline data actually started
    #   stopTimelinePosInFile - Where valid timeline data actually stopped
    #
    # It is OK to start a timeline before the end of the partition and 
    # then read it past the end. So, we may read a timeline that 
    # stretches past the end of the partition. But, it is NOT OK
    # to start a timeline after the end of the partition.
    #####################################################
    def ReadNextTimelineXMLStrImpl(self, stopPartition):
        fFoundTimeline = False
        fEOF = False
        startTimelinePosInFile = TDF_INVALID_VALUE
        stopTimelinePosInFile = TDF_INVALID_VALUE

        ####################
        # Read the next timeline node as a text string
        # 1. This ASSUMES we are about to read the <TL> opening tag for the next timeline.
        #     We start just before the first timeline when opening a file.
        #     We stop just before the next timeline when we read one timeline.
        self.currentTimelineNodeStr = ""
        fStartedTimelineSection = False
        while True: 
            currentLinePositon = self.fileHandle.tell()
            # Check if we have run past the end of the partition
            # It is OK to start a timeline before the end of the partition and then read it past the end
            # if possible (we read a little extra data at the end to allow for this).
            # But, it is NOT OK to start a timeline after the end of the partition.
            if ((0 < stopPartition <= currentLinePositon) and (not fStartedTimelineSection)):
                break

            # Get next line from file 
            try:
                binaryLine = self.fileHandle.readline() 
            except UnicodeDecodeError as err:
                print("Unicode Error from reading TDF file. lineNum=" + str(self.lineNum) + ", err=" + str(err))
                continue
            except Exception:
                print("Error from reading Lab file. lineNum=" + str(self.lineNum))
                continue
            self.lineNum += 1

            # Convert the text from Unicode to ASCII. 
            try:
                currentLine = binaryLine.decode("ascii", "ignore")
            except UnicodeDecodeError as err:
                print("Unicode Error from converting string. lineNum=" + str(self.lineNum) + ", err=" + str(err))
                continue
            except Exception:
                print("Error from converting string. lineNum=" + str(self.lineNum))
                continue

            # If we hit the end of the file, then we did not find a next timeline.
            if (currentLine == ""):
                fEOF = True
                break

            # Before we decide to save the line, remove whitespace for comparisons.
            # Gotcha 1: Do this to a temp copy, but save the original line with the whitespace
            # Gotcha 2: Do this before we decide we are in the timeline. Don't save text before the timeline starts.
            #print("ReadNextTimelineXMLStrImpl. currentLine=" + currentLine)
            lineTokenText = currentLine.lstrip().rstrip().lower()

            # Now, check if this is the start of a timeline element
            # Notice the timeline element may contain attributes, so don't compare 
            # with "<TL>"
            if ((not fStartedTimelineSection) and (lineTokenText.startswith(TIMELINE_OPEN_ELEMENT_PREFIX_CASE_INDEPENDANT))):
                fStartedTimelineSection = True
                startTimelinePosInFile = currentLinePositon

            if (fStartedTimelineSection):
                # OldBugFix: currentLine = currentLine.replace("=<", "")
                self.currentTimelineNodeStr += currentLine
            # End - if (fStartedTimelineSection):

            # Stop when we have read the entire timeline.
            # Do not do this if we just hit an end. We may hit the end of one timeline that
            # started on a previous buffer before getting to the first timeline in the current buffer.
            if ((lineTokenText.startswith(TIMELINE_CLOSE_ELEMENT_CASE_INDEPENDANT)) and (fStartedTimelineSection)):
                # If we found both the start and end of a timeline, then we founf thew whole timeline.
                fFoundTimeline = True
                stopTimelinePosInFile = self.fileHandle.tell()
                break
        # End - Read the file header

        return fFoundTimeline, fEOF, startTimelinePosInFile, stopTimelinePosInFile
    # End - ReadNextTimelineXMLStrImpl(self)





    #####################################################
    #
    # [TDFFileReader::FindAllTimelinesInPartition]
    #
    # This returns two values: fFoundTimeline, fEOF
    #   fFoundTimeline - True if we read a complete timeline
    #   fEOF - True if we hit the end of the file
    #####################################################
    def FindAllTimelinesInPartition(self, startPartition, stopPartition):
        #TDF_Log("FindAllTimelinesInPartition. startPartition=" + str(startPartition) + 
        #            ", stopPartition=" + str(stopPartition))
        fEOF = False
        fFoundOpenElement = False
        currentOpenElementPosition = TDF_INVALID_VALUE
        currentCloseElementPosition = TDF_INVALID_VALUE
        openElement = re.compile('<TL', re.IGNORECASE)
        closeElement = re.compile('</TL>', re.IGNORECASE)
        resultTimelinePositionLists = []

        # Jump to the partition starting position. 
        # Note, the partition boundaries are arbitrary byte positions, so
        # this may jump to the middle of a line of text. That is OK, since
        # we will still advance until we see a valid start of a timeline element.
        self.fileHandle.seek(startPartition, 0)

        # Advance in the file to the start of each timeline
        while True: 
            currentLinePositonInFile = self.fileHandle.tell()
            # Check if we have run past the end of the partition
            # It is OK to start a timeline before the end of the partition and then read it past the end.
            # But, it is NOT OK to start a timeline after the end of the partition.
            if ((not fFoundOpenElement) and (0 < stopPartition <= currentLinePositonInFile)):
                break

            # Get next line from file 
            try:
                binaryLine = self.fileHandle.readline() 
            except UnicodeDecodeError as err:
                print("Unicode Error from reading Lab file. lineNum=" + str(self.lineNum))
                print("err=" + str(err))
                continue
            except Exception:
                print("Error from reading Lab file. lineNum=" + str(self.lineNum))
                continue
            self.lineNum += 1

            # Convert the text from Unicode to ASCII. 
            try:
                currentLine = binaryLine.decode("ascii", "ignore")
            except UnicodeDecodeError as err:
                print("Unicode Error from converting string. lineNum=" + str(self.lineNum))
                print("err=" + str(err))
                continue
            except Exception:
                print("Error from converting string. lineNum=" + str(self.lineNum))
                continue

            # If we hit the end of the file, then we did not find a next timeline.
            if (currentLine == ""):
                fEOF = True
                break

            # Scan through a string, looking for any location where this RE matches.
            # If we haven't found an open element, then we are looking for one
            # If we found an open element, then we are looking for the next close.
            if (fFoundOpenElement):
                matchResult = closeElement.match(currentLine)
            else:  # if (not fFoundOpenElement)
                matchResult = openElement.match(currentLine)

            if matchResult:
                if (fFoundOpenElement):
                    # If we previously found an open and just now found a close, then we have
                    # the entire element
                    fFoundOpenElement = False
                    currentCloseElementPosition = currentLinePositonInFile + len(currentLine)
                    newDict = {"start": currentOpenElementPosition, "stop": currentCloseElementPosition}
                    resultTimelinePositionLists.append(newDict)
                else:  # (not fFoundOpenElement)
                    # If we had not previously found an open and just now found an open, then we are
                    # ready to search for the close
                    fFoundOpenElement = True
                    currentOpenElementPosition = currentLinePositonInFile
            # End - if matchResult

        # End - Advance in the file to the start of each timeline

        return resultTimelinePositionLists, fEOF
    # End - FindAllTimelinesInPartition






    #####################################################
    #
    # [TDFFileReader::ParseCurrentTimelineImpl]
    #
    # Returns True/False. 
    #   It returns True if it found a valid timeline entry.
    #####################################################
    def ParseCurrentTimelineImpl(self):
        # Parse the text string into am XML DOM
        self.currentTimelineXMLDOM = dxml.XMLTools_ParseStringToDOM(self.currentTimelineNodeStr)
        if (self.currentTimelineXMLDOM is None):
            TDF_Log("ParseCurrentTimelineImpl. Error from parsing string:")
            return False

        self.currentTimelineNode = dxml.XMLTools_GetNamedElementInDocument(self.currentTimelineXMLDOM, "TL")
        if (self.currentTimelineNode is None):
            TDF_Log("ParseCurrentTimelineImpl. timeline element is missing: [" + self.currentTimelineNodeStr + "]")
            return False

        # Get some properties from the timeline. These apply to all data entries within this timeline.
        genderStr = self.currentTimelineNode.getAttribute("gender")
        if (genderStr == "M"):
            self.CurrentIsMale = 1
        else:
            self.CurrentIsMale = 0

        self.CurrentWtInKg = TDF_INVALID_VALUE
        wtInKgStr = self.currentTimelineNode.getAttribute("wt")
        if ((wtInKgStr) and (wtInKgStr != "")):
            self.CurrentWtInKg = float(wtInKgStr)

        self.CurrentTimelineID = TDF_INVALID_VALUE
        idStr = self.currentTimelineNode.getAttribute("id")
        if ((idStr) and (idStr != "")):
            self.CurrentTimelineID = int(idStr)

        # Generate a timeline of actual and derived data values.
        # This covers the entire timeline.
        self.CompileTimelineImpl()

        return True
    # End - ParseCurrentTimelineImpl(self)




    #####################################################
    #
    # [TDFFileReader::CompileTimelineImpl]
    #
    # This ASSUMES ParseVariableList() has already run (it's called in the constructor).
    # As a result, these are ALL valid: 
    #       self.allValueVarNameList, self.AllValuesOffsetStartRange, self.allValuesFunctionNameList
    #
    # I have debated whether latestTimelineEntryDataList should be a dict or an array.
    # I like the idea of an array, than can just map to the list
    # of requested values once we need to return values. This probably can be performance
    # tuned, and I am influenced by the idea that Google's AKI neural net seems to do that.
    #
    # However, there are a lot of internal values, like DayofDischarge that need to be
    # collected and maintained and are never returned to the client. The number of these
    # may change over time. A dict is more efficient at this, and uses Python's internal
    # implementation, rather than writing something like an enumerator loop to find all 
    # cases of a variable in the list. Moverover, a dict handles the problem of duplicate
    # entries.
    #####################################################
    def CompileTimelineImpl(self):
        self.CompiledTimeline = []

        # At any given time, self.latestTimelineEntryDataList has the most recent
        # value for each lab.
        self.latestTimelineEntryDataList = {}
        self.latestTimeLineEntry = None
        latestTimeLineEntryTimeCode = TDF_INVALID_VALUE

        # Initialize the latestTimelineEntryDataList with the values.
        for _, nameStr in enumerate(self.allValueVarNameList):
            self.latestTimelineEntryDataList[nameStr] = TDF_INVALID_VALUE

        # Initialize the latest labs with a few special values that don't change.
        if ("IsMale" in self.allValueVarNameList):
            self.latestTimelineEntryDataList['IsMale'] = int(self.CurrentIsMale)
        if ("WtKg" in self.allValueVarNameList):
            self.latestTimelineEntryDataList['WtKg'] = int(self.CurrentWtInKg)

        # Initially, all outcomes are false for this timeline. 
        # This will change as we move forward through the timeline.
        if ("InHospital" in self.allValueVarNameList):
            self.latestTimelineEntryDataList['InHospital'] = 0
        if ("MajorSurgeries" in self.allValueVarNameList):
            self.latestTimelineEntryDataList['MajorSurgeries'] = 0
        if ("GIProcedures" in self.allValueVarNameList):
            self.latestTimelineEntryDataList['GIProcedures'] = 0


        # Now we have a basic initialized accumulator, save a copy of it.
        # Each new data point will start with either a copy of the previous data
        # point (to carry old values forward) or else a copy of this initialized
        # accumulator. 
        savedInitialDataList = copy.deepcopy(self.latestTimelineEntryDataList)

        # These are the times that milestones are reached. These are computed on the
        # forward pass, and then saved into the timeline on the reverse pass
        self.StartCKD5Date = TDF_INVALID_VALUE
        self.StartCKD4Date = TDF_INVALID_VALUE
        self.StartCKD3bDate = TDF_INVALID_VALUE
        self.StartCKD3aDate = TDF_INVALID_VALUE
        self.NextFutureDischargeDate = TDF_INVALID_VALUE

        self.FutureBaselineCr = TDF_INVALID_VALUE
        self.baselineCrSeries = None
        if ("baselineCr" in self.allValueVarNameList):
            self.baselineCrSeries = timefunc.CTimeSeries(TDF_TIME_GRANULARITY_DAYS, 7)

        # Get outcome results.
        # These are often global values that apply to the entire timeline.
        # They may be defined after the TDF file is created, because they may
        # apply to an edited form of the TDF file. So they cannot be stored 
        # in the timeline. Instead, we insert them in the timeline when a TDF
        # is opened for reading.
        self.OutcomeImprove = TDF_INVALID_VALUE
        attrStr = self.currentTimelineNode.getAttribute("OutcomeImprove")
        if (attrStr is not None):
            attrStr = attrStr.lower()
            if ((genderStr == "true") or (genderStr == "t") or (genderStr == "1")):
                self.OutcomeImprove = 1
            else:
                self.OutcomeImprove = 0

        self.OutcomeWorsen = TDF_INVALID_VALUE
        attrStr = self.currentTimelineNode.getAttribute("OutcomeWorsen")
        if (attrStr is not None):
            attrStr = attrStr.lower()
            if ((genderStr == "true") or (genderStr == "t") or (genderStr == "1")):
                self.OutcomeWorsen = 1
            else:
                self.OutcomeWorsen = 0
        self.OutcomeFutureEndStage = TDF_INVALID_VALUE
        attrStr = self.currentTimelineNode.getAttribute("OutcomeFutureEndStage")
        if (attrStr is not None):
            attrStr = attrStr.lower()
            if ((genderStr == "true") or (genderStr == "t") or (genderStr == "1")):
                self.OutcomeFutureEndStage = 1
            else:
                self.OutcomeFutureEndStage = 0

        # <> BUGBUG FIXME
        # These are used in the forward pass to fix a bug in TDF files.
        # Some XML nodes may have out of order dates.
        # Probably from an admit order, which is dated earlier than the first labs of the admission.
        prevDateDays = TDF_INVALID_VALUE
        prevDateHours = TDF_INVALID_VALUE
        prevDateMinutes = TDF_INVALID_VALUE
        prevDateSeconds = TDF_INVALID_VALUE
        #<> End

        ######################################
        # FORWARD PASS
        # Keep a running list of the latest values for all lab values. This includes
        # all lab values.
        currentNode = dxml.XMLTools_GetFirstChildNode(self.currentTimelineNode)
        while (currentNode):
            nodeType = dxml.XMLTools_GetElementName(currentNode).lower()

            #print("Forward Pass. NodeType: " + nodeType)
            # We ignore any nodes other than Data and Events and Outcomes
            if (nodeType not in ('e', 'd')):
                # Go to the next XML node in the TDF
                currentNode = dxml.XMLTools_GetAnyPeerNode(currentNode)
                continue

            # Get the timestamp for this XML node.
            timeStampStr = currentNode.getAttribute("T")
            if ((timeStampStr is not None) and (timeStampStr != "")):
                labDateDays, labDateHours, labDateMins, labDateSecs = TDF_ParseTimeStamp(timeStampStr)
                prevDateDays = labDateDays
                prevDateHours = labDateHours
                prevDateMinutes = labDateMins
                prevDateSeconds = labDateSecs
            else:
                # Just copy the old timestamp forward.
                labDateDays = prevDateDays
                labDateHours = prevDateHours
                labDateMins = prevDateMinutes
                labDateSecs = prevDateSeconds

            # Now calculate the time code. The actual value depends on the granularity of
            # the timeline. It can be in seconds or days or something else.
            if (self.TimeGranularity == TDF_TIME_GRANULARITY_DAYS):
                currentTimeCode = labDateDays
            else:                
                currentTimeCode = TDF_ConvertTimeToSeconds(labDateDays, labDateHours, labDateMins, labDateSecs)

            dataClass = ""
            if (nodeType == "d"):
                dataClass = currentNode.getAttribute("C").lower()


            # Find where we store the data from this XML node in the runtime timeline.
            # There may be separate XML nodes for labs, vitals and events that all map to the same
            # timeline entry. Collapse all data data from the same time to a single timeline entry.
            reuseLatestData = False
            if (latestTimeLineEntryTimeCode == currentTimeCode):
                reuseLatestData = True
            # Diagnosis dates are sloppy. However, do not overuse too much
            # because that allows a later diagnosis to overwrite the date of a much
            # earlier data point.
            elif ((nodeType == "d") and (dataClass == "d") and (latestTimeLineEntryTimeCode == currentTimeCode)):
                reuseLatestData = True


            # Get the timeline entry for this time, create a new timeline entry if necessary.
            if ((reuseLatestData) and (self.latestTimeLineEntry is not None)):
                #print("Reuse existing timeline entry")
                timelineEntry = self.latestTimeLineEntry
            else:
                # Otherwise, we are starting a new timeline entry.
                # Make a new time slot. 
                timelineEntry = {'TimeCode': currentTimeCode, 'Day': labDateDays, 'Sec': labDateSecs + (labDateMins * 60) + (labDateHours * 3600)}

                # This is a bit dangerous/weird:
                # It is nice to make the dayNum and SecInDay available without having to rederive it
                # when a client gets timeline data.
                # But, don't spend the extra space storing this if secs=0 always and dayNum is just the timestamp.
                # However, this means the values in each entry will be different depending on the time granularity.
                #if (self.TimeGranularity != TDF_TIME_GRANULARITY_DAYS):
                    #timelineEntry['Day'] = labDateDays
                    #timelineEntry['Sec'] = labDateSecs + (labDateMins * 60) + (labDateHours * 3600)

                # Note: This may make a new timeline entry before we have confirmed that there is new data.
                # It ensures that we will include days for meds only without labs
                # That may be a bit verbose but will not lead to incorrect data.
                self.CompiledTimeline.append(timelineEntry)
                self.latestTimeLineEntry = timelineEntry
                latestTimeLineEntryTimeCode = currentTimeCode
    
                # Each timeline node needs a private copy of the latest labs.
                # Make a copy of the most recent labs, so we inherit any labs up to this point.
                # This node may overwrite any of the labs that change.
                if (self.fCarryForwardPreviousDataValues):
                    newDataList = copy.deepcopy(self.latestTimelineEntryDataList)
                else:
                    newDataList = copy.deepcopy(savedInitialDataList)

                # Some values, like drug doses, are never carried forward, and instead
                # must be re-ordered daily. This is the only way they stop after being cancelled.
                # Additionally, some values, like procedures, are never carried forward.
                for valueName, varDictInfo in zip(self.allValueVarNameList, self.allValuesLabInfoList):
                    if (varDictInfo['ActionAfterEachTimePeriod'] == ""):
                        # Test for "" explicitly because it is by far the most common, and we quickly
                        # do nothing and skip all of the other tests.
                        pass
                    elif (varDictInfo['ActionAfterEachTimePeriod'] == "inval"):
                        newDataList[valueName] = TDF_INVALID_VALUE
                    elif (varDictInfo['ActionAfterEachTimePeriod'] == "zero"):
                        newDataList[valueName] = 0
                    elif (varDictInfo['ActionAfterEachTimePeriod'] == "none"):
                        newDataList[valueName] = None
                    elif ((varDictInfo['ActionAfterEachTimePeriod'] == "remove") and (valueName in newDataList)):
                        del newDataList[valueName]
                # End - for varName, varDictInfo in zip(self.allValueVarNameList, self.allValuesLabInfoList):

                self.latestTimeLineEntry['data'] = newDataList
                self.latestTimeLineEntry['eventNodeList'] = []
                self.latestTimelineEntryDataList = newDataList
                #print("newDataList=" + str(newDataList))
            # End - if ((not reuseLatestData) or (self.latestTimeLineEntry is None)):

            # Read the contents of this XML node into the runtime timeline data structures.
            # Events
            if (nodeType == "e"):
                timelineEntry['eventNodeList'].append(currentNode)
                self.ProcessEventNodeForwardImpl(currentNode, labDateDays)
            # Data
            elif (nodeType == "d"):
                self.ProcessDataNodeForwardImpl(currentNode, labDateDays)

            ###################################
            # Compute a few SPECIAL calculated values
            # This allows them to be used for future predictions, like future values of GFR is needed to compute 
            # Days_Until_CKD4. This means a few special values (like MELD and GFR) need to be done in the forward
            # pass, so they can later be used to calculate days until values in the backward pass.
            if (self.allValuesLabInfoList is not None):
                for labInfoIndex, labInfo in enumerate(self.allValuesLabInfoList):
                    if ((labInfo is not None) and (labInfo['Calculated'])):
                        labName = self.allValueVarNameList[labInfoIndex]
                        self.CalculateDerivedValuesFORWARDPass(labName, labDateDays, self.latestTimelineEntryDataList)
                # End - for labInfoIndex, labInfo in enumerate(self.allValuesLabInfoList):
            # End - if (self.allValuesLabInfoList is not None):

            # Go to the next XML node in the TDF
            currentNode = dxml.XMLTools_GetAnyPeerNode(currentNode)
        # End - while (currentNode):

        self.LastTimeLineIndex = len(self.CompiledTimeline) - 1        


        ######################################
        # Do a SECOND forward pass.
        # This loop will iterate over each step in the timeline.
        # We do this as a SEPARATE loop, becuase it uses the final values for each day.
        # The first forward pass may write several labs for the same day. For example,
        # when there is a bad lab and we do a re-check lab.
        # Alternatively, the time granularity may map high freq events to low freq records
        # and so several values may overwrite each other.
        # Do this when we have settled on a final value for each time slot.
        for timeLineIndex in range(self.LastTimeLineIndex + 1):
            timelineEntry = self.CompiledTimeline[timeLineIndex]
            self.RecordTimeMilestonesOnForwardPass(timelineEntry['data'], timelineEntry['TimeCode'])
        # End - for timeLineIndex in range(self.LastTimeLineIndex + 1):

        ######################################
        # REVERSE PASS
        # Keep a running list of the next occurrence of each event.
        timeLineIndex = self.LastTimeLineIndex
        while (timeLineIndex >= 0):
            timelineEntry = self.CompiledTimeline[timeLineIndex]
            currentTimeCode = timelineEntry['TimeCode']
            # Get a reference to the data collected up to this point in FORWARD order.
            # This was compiled in the previous loop, which did the forward pass.
            reversePassTimeLineData = timelineEntry['data']

            # Now, update the events at this node using data pulled from the future 
            # in REVERSE order.
            for eventNode in timelineEntry['eventNodeList']:
                self.ProcessEventNodeInReverseImpl(reversePassTimeLineData, eventNode, labDateDays)

            # Remove any references so the data can eventually be garbage collected when we are
            # done with the XML but still using the timeline.
            timelineEntry['eventNodeList'] = []

            ###################################
            # Compute "SPECIAL" calculated values
            # Some calculated values need to be done using future knowledge,
            # not just past knowledge.
            self.CalculateAllDerivedValuesREVERSEPass(reversePassTimeLineData, currentTimeCode)

            timeLineIndex = timeLineIndex - 1
        # End - for timeLineIndex in range(self.LastTimeLineIndex + 1):
    # End - CompileTimelineImpl(self)





    ################################################################################
    #
    # [TDFFileReader::ProcessDataNodeForwardImpl]
    #
    # This processes any DATA node as we move forward in the the timeline. 
    # It updates self.latestTimelineEntryDataList, possibly overwriting earlier outcomes.
    ################################################################################
    def ProcessDataNodeForwardImpl(self, dataNode, labDateDays):
        dataClass = dataNode.getAttribute("C")

        ###################################
        # Labs and Vitals
        # Copy labs and vitals into the accumulator
        if (dataClass in ("L", "V")):
            labTextStr = str(dxml.XMLTools_GetTextContents(dataNode))
            assignmentList = labTextStr.split(',')
            for assignment in assignmentList:
                assignmentParts = assignment.split('=')
                if (len(assignmentParts) < 2):
                    continue
                labName = assignmentParts[0]
                labvalueStr = assignmentParts[1]

                # Look up the lab. Optimistically, try the lab name as is, it is usually a valid name
                try:
                    labInfo = g_LabValueInfo[labName]
                    foundValidLab = True
                except Exception:
                    foundValidLab = False

                # Do not save any values that are not used. There are many defined variables, and
                # a single hospital database may have many different values. We only care about some.
                # Don't spend the time or memory saving everything.
                if ((foundValidLab) and (labName not in self.allValueVarNameList)):
                    foundValidLab = False

                # Some labs are *only* computed. This lets us ensure they are correctly calculated
                # using a known algorithm and done in a consistent manner. So, ignore any of these
                # values that may also appear in the TDF. For example, many medical records try to 
                # "help" by proving a value for GFR that is computed with MDRD or Cockrauft-Galt.
                if (labName == "GFR"):
                    foundValidLab = False

                # Try to parse the value.
                if (foundValidLab):
                    try:
                        labValueFloat = float(labvalueStr)
                    except Exception:
                        # Replace invalid characters.
                        labvalueStr = labvalueStr.replace('>', '') 
                        labvalueStr = labvalueStr.replace('<', '') 
                        try:
                            labValueFloat = float(labvalueStr)
                        except Exception:
                            foundValidLab = False

                    labMinVal = float(labInfo['minVal'])
                    labMaxVal = float(labInfo['maxVal'])
                # End - if ((labName != "") and (labValue != "")):

                # Rule out ridiculous values. Often, vitals will be entered incorrectly or
                # similar things. This won't catch all invalid entries, but will catch some.
                if ((foundValidLab) and ((labValueFloat < TDF_SMALLEST_VALID_VALUE) or (labValueFloat >= (3 * labMaxVal)))):
                    foundValidLab = False

                # Now, clip the value to the min and max for this variable and then save it.
                if (foundValidLab):
                    if (labValueFloat < float(labMinVal)):
                        labValueFloat = float(labMinVal)
                    if (labValueFloat > float(labMaxVal)):
                        labValueFloat = float(labMaxVal)
                    self.latestTimelineEntryDataList[labName] = labValueFloat
                # End - if (foundValidLab)
            # End - for assignment in assignmentList
        # End - if ((dataClass == "L") or (dataClass == "V")):


        # Some values come from the timestamp, not the contents, of the data element.
        if ("AgeInYrs" in self.allValueVarNameList):
            self.latestTimelineEntryDataList["AgeInYrs"] = int(labDateDays / 365)


        # Store outcome results.
        # These are often global values that apply to the entire timeline.
        # They may be defined after the TDF file is created, because they may
        # apply to an edited form of the TDF file. So they cannot be stored 
        # in the timeline. Instead, we insert them in the timeline when a TDF
        # is opened for reading.
        if ("OutcomeImprove" in self.allValueVarNameList):
            self.latestTimelineEntryDataList["OutcomeImprove"] = self.OutcomeImprove
        if ("OutcomeWorsen" in self.allValueVarNameList):
            self.latestTimelineEntryDataList["OutcomeWorsen"] = self.OutcomeWorsen
        if ("OutcomeFutureEndStage" in self.allValueVarNameList):
            self.latestTimelineEntryDataList["OutcomeFutureEndStage"] = self.OutcomeFutureEndStage
    # End - ProcessDataNodeForwardImpl




    ################################################################################
    #
    # [TDFFileReader::CalculateDerivedValuesFORWARDPass]
    #
    # This is called when we build the timeline. Some values like GFR and MELD 
    # are needed for the reverse pass.
    #
    # It CANNOT use values from the future, like days_until_CKD5. Those are computed
    # on the reverse pass which comes later.
    ################################################################################
    def CalculateDerivedValuesFORWARDPass(self, varName, currentDayNum, varValueDict):
        ##############################################
        if (varName == "GFR"):
            try:
                currrentCr = varValueDict['Cr']
            except Exception:
                currrentCr = TDF_INVALID_VALUE
            try:
                patientAge = varValueDict['AgeInYrs']
            except Exception:
                patientAge = TDF_INVALID_VALUE
            try:
                fIsMale = varValueDict['IsMale']
            except Exception:
                fIsMale = TDF_INVALID_VALUE

            eGFR = self.CalculateGFR(currrentCr, patientAge, fIsMale)
            if (eGFR > TDF_SMALLEST_VALID_VALUE):
                eGFR = round(eGFR)
                varValueDict[varName] = eGFR
        # End - if (varName = "GFR"):

        ##############################################
        elif (varName == "MELD"):
            try:
                serumCr = varValueDict['Cr']
                serumNa = varValueDict['Na']
                tBili = varValueDict['Tbili']
                inr = varValueDict['INR']
            except Exception:
                serumCr = TDF_INVALID_VALUE
                serumNa = TDF_INVALID_VALUE
                tBili = TDF_INVALID_VALUE
                inr = TDF_INVALID_VALUE

            if ((serumCr > TDF_SMALLEST_VALID_VALUE) and (tBili > TDF_SMALLEST_VALID_VALUE) 
                    and (serumNa > TDF_SMALLEST_VALID_VALUE) and (inr > TDF_SMALLEST_VALID_VALUE)):
                # Clip bili, INR and Cr to specific ranges. The formula is not
                # validated for vals outside those ranges.
                inr = max(inr, 1.0)
                tBili = max(tBili, 1.0)
                serumCr = max(serumCr, 1.0)
                serumCr = min(serumCr, 4.0)
                serumNa = max(serumNa, 125)
                serumNa = min(serumNa, 137)

                # If the base is not passed as a second parameter, then math.log() returns natural log.
                lnCr = math.log(float(serumCr))
                lntBili = math.log(float(tBili))
                lnINR = math.log(float(inr))

                # Be careful, some formula will rearrange the parens, so add 6.43 rather than 10*0.643, but it is the same.
                meldScore = 10 * ((0.957 * lnCr) + (0.378 * lntBili) + (1.12 * lnINR) + 0.643)
                if (meldScore > 11.0):
                    # MELD = MELD(i) + 1.32*(137-Na) – [0.033*MELD(i)*(137-Na)]
                    meldScore = meldScore + (1.32 * (137 - serumNa)) - (0.033 * meldScore * (137 - serumNa))

                result = round(meldScore)
                varValueDict[varName] = result

        ##############################################
        elif (varName in ("CYP2C9Inducer", "CYP2C9Inhibiter", "CYP3A4Inducer", "CYP3A4Inhibitor")):
            result = 0
            inputList = g_LabValueInfo[varName]['VariableDependencies']
            for drugName in inputList:
                try:
                    drugDose = varValueDict[drugName]
                    if (drugDose > 0):
                        result += 1
                except Exception:
                    pass
            # End - for drugName in inputList:
            varValueDict[varName] = result

        ##############################################
        # Compute the baseline Cr
        # ------------------------
        # The baseline Cr is tricky and requires past and future knowledge.
        # Consider a pt with Cr 1.0, then goes to an AKI with peak Cr 2.9 then
        # recovers to a new baseline Cr of 1.4.
        #
        # Baseline is the lowest value of the past 7 days, but also cannot be higher 
        # than the lowest future value.
        # We will calculate it here based on past history, but may revise the value on the
        # forward pass using future information.
        if (varName == "BaselineCr"):
            # Try to extend the running history of recent Cr values
            try:
                currrentCr = varValueDict['Cr']
            except Exception:
                currrentCr = TDF_INVALID_VALUE
            if (currrentCr > TDF_SMALLEST_VALID_VALUE):
                self.baselineCrSeries.AddNewValue(currrentCr, currentDayNum, 0, 0, 0)

            # Now, update the value
            varValueDict[varName] = self.baselineCrSeries.GetLowestValue()
        # End - if (varName == "BaselineCr")

        ##############################################
        elif (varName == "BUNCrRatio"):
            try:
                serumBUN = varValueDict['BUN']
            except Exception:
                serumBUN = TDF_INVALID_VALUE
            try:
                currrentCr = varValueDict['Cr']
            except Exception:
                currrentCr = TDF_INVALID_VALUE
            if ((serumBUN > TDF_SMALLEST_VALID_VALUE) and (currrentCr > TDF_SMALLEST_VALID_VALUE)):
                result = float(serumBUN) / float(currrentCr)
                result = round(result)
                varValueDict[varName] = result

        ##############################################
        elif (varName == "TIBC"):
            try:
                serumTransferrin = varValueDict['Transferrin']
            except Exception:
                serumTransferrin = TDF_INVALID_VALUE
            try:
                serumFeSat = varValueDict['TransferrinSat']
            except Exception:
                serumFeSat = TDF_INVALID_VALUE
            try:
                serumIron = varValueDict['Iron']
            except Exception:
                serumIron = TDF_INVALID_VALUE

            # FeSat = (Fe / TIBC) * 100 
            # or TIBC = (Fe / FeSat) * 100
            if ((serumIron > TDF_SMALLEST_VALID_VALUE) and (serumFeSat > TDF_SMALLEST_VALID_VALUE)):
                result = float(serumIron) / float(serumFeSat)
                result = round(result) * 100
                varValueDict[varName] = result
            # Transferrin (mg/dL) = 0.8 x TIBC (µg of iron/dL) – 43
            elif ((serumTransferrin > TDF_SMALLEST_VALID_VALUE)):
                result = (float(serumTransferrin) + 43) / 0.8
                varValueDict[varName] = round(result) * 100

        ##############################################
        elif (varName == "NeutLymphRatio"):
            try:
                AbsNeutrophils = varValueDict['AbsNeutrophils']
            except Exception:
                AbsNeutrophils = TDF_INVALID_VALUE
            try:
                AbsLymphs = varValueDict['AbsLymphs']
            except Exception:
                AbsLymphs = TDF_INVALID_VALUE
            if ((AbsNeutrophils > TDF_SMALLEST_VALID_VALUE) and (AbsLymphs > TDF_SMALLEST_VALID_VALUE)):
                result = float(AbsNeutrophils) / float(AbsLymphs)
                varValueDict[varName] = round(result)

        ##############################################
        elif (varName == "AnionGap"):
            try:
                serumNa = varValueDict['Na']
                serumCl = varValueDict['Cl']
                serumCO2 = varValueDict['CO2']
            except Exception:
                serumNa = TDF_INVALID_VALUE
                serumCl = TDF_INVALID_VALUE
                serumCO2 = TDF_INVALID_VALUE
            if ((serumNa > TDF_SMALLEST_VALID_VALUE) 
                    and (serumCl > TDF_SMALLEST_VALID_VALUE)
                    and (serumCO2 > TDF_SMALLEST_VALID_VALUE)):
                varValueDict[varName] = serumNa - (serumCl + serumCO2)

        ##############################################
        elif (varName == "ProtGap"):
            try:
                serumTProt = varValueDict['TProt']
                serumAlb = varValueDict['Alb']
            except Exception:
                serumTProt = TDF_INVALID_VALUE
                serumAlb = TDF_INVALID_VALUE
            if ((serumTProt > TDF_SMALLEST_VALID_VALUE) and (serumAlb > TDF_SMALLEST_VALID_VALUE)):
                varValueDict[varName] = serumTProt - serumAlb

        ##############################################
        elif (varName == "UrineAnionGap"):
            try:
                urineNa = varValueDict['UNa']
                urineK = varValueDict['UK']
                urineCl = varValueDict['UCl']
            except Exception:
                urineNa = TDF_INVALID_VALUE
                urineK = TDF_INVALID_VALUE
                urineCl = TDF_INVALID_VALUE
            if ((urineNa > TDF_SMALLEST_VALID_VALUE) 
                    and (urineK > TDF_SMALLEST_VALID_VALUE)
                    and (urineCl > TDF_SMALLEST_VALID_VALUE)):
                varValueDict[varName] = (urineNa + urineK) - urineCl

        ##############################################
        elif (varName == "UACR"):
            try:
                result = varValueDict['UACR']
            except Exception:
                result = TDF_INVALID_VALUE

            if (result < TDF_SMALLEST_VALID_VALUE):
                try:
                    urineAlb = varValueDict['UAlb']
                    urineCr = varValueDict['UCr']
                except Exception:
                    urineAlb = TDF_INVALID_VALUE
                    urineCr = TDF_INVALID_VALUE
                if ((urineAlb > TDF_SMALLEST_VALID_VALUE) and (urineCr > TDF_SMALLEST_VALID_VALUE)):
                    result = float(urineAlb) / float(urineCr)

            if (result > TDF_SMALLEST_VALID_VALUE):
                varValueDict[varName] = result

        ##############################################
        elif (varName == "UPCR"):
            try:
                result = varValueDict['UPCR']
            except Exception:
                result = TDF_INVALID_VALUE

            if (result < TDF_SMALLEST_VALID_VALUE):
                try:
                    urineProt = varValueDict['UProt']
                    urineCr = varValueDict['UCr']
                except Exception:
                    urineProt = TDF_INVALID_VALUE
                    urineCr = TDF_INVALID_VALUE
                if ((urineProt > TDF_SMALLEST_VALID_VALUE) and (urineCr > TDF_SMALLEST_VALID_VALUE)):
                    result = float(urineProt) / float(urineCr)

            if (result > TDF_SMALLEST_VALID_VALUE):
                varValueDict[varName] = result

        ##############################################
        elif (varName == "FENa"):
            try:
                serumCr = varValueDict['Cr']
                serumNa = varValueDict['Na']
                urineCr = varValueDict['UCr']
                urineNa = varValueDict['UNa']
            except Exception:
                serumCr = TDF_INVALID_VALUE
                serumNa = TDF_INVALID_VALUE
                urineCr = TDF_INVALID_VALUE
                urineNa = TDF_INVALID_VALUE

            if ((serumCr > TDF_SMALLEST_VALID_VALUE) 
                    and (serumNa > TDF_SMALLEST_VALID_VALUE) 
                    and (urineCr > TDF_SMALLEST_VALID_VALUE) 
                    and (urineNa > TDF_SMALLEST_VALID_VALUE)):
                result = 100.0 * float(serumCr * urineNa) / float(serumNa * urineCr)
                varValueDict[varName] = result

        ##############################################
        elif (varName == "FEUrea"):
            try:
                serumCr = varValueDict['Cr']
                serumBUN = varValueDict['BUN']
                urineCr = varValueDict['UCr']
                urineUUN = varValueDict['UUN']
            except Exception:
                serumCr = TDF_INVALID_VALUE
                serumBUN = TDF_INVALID_VALUE
                urineCr = TDF_INVALID_VALUE
                urineUUN = TDF_INVALID_VALUE

            if ((serumCr > TDF_SMALLEST_VALID_VALUE) 
                    and (serumBUN > TDF_SMALLEST_VALID_VALUE) 
                    and (urineCr > TDF_SMALLEST_VALID_VALUE)
                    and (urineUUN > TDF_SMALLEST_VALID_VALUE)):
                result = 100.0 * float(serumCr * urineUUN) / float(serumBUN * urineCr)
                varValueDict[varName] = result

        ##############################################
        elif (varName == "AdjustCa"):
            try:
                tCal = varValueDict['Ca']
                alb = varValueDict['Alb']
            except Exception:
                tCal = TDF_INVALID_VALUE
                alb = TDF_INVALID_VALUE

            if ((tCal > TDF_SMALLEST_VALID_VALUE) and (alb > TDF_SMALLEST_VALID_VALUE)):
                varValueDict[varName] = float(tCal) + (0.8 * (4.0 - float(alb)))
            else:
                try:
                    tCal = varValueDict['Ca']
                except Exception:
                    tCal = TDF_INVALID_VALUE
                if (tCal > TDF_SMALLEST_VALID_VALUE):
                    varValueDict[varName] = tCal

        ##############################################
        elif (varName == "KappaLambdaRatio"):
            try:
                kappaVal = varValueDict['FLCKappa']
                lambdaVal = varValueDict['FLCLambda']
            except Exception:
                kappaVal = TDF_INVALID_VALUE
                lambdaVal = TDF_INVALID_VALUE

            if ((kappaVal > TDF_SMALLEST_VALID_VALUE) and (lambdaVal > TDF_SMALLEST_VALID_VALUE)):
                result = float(kappaVal) / float(lambdaVal)
                varValueDict[varName] = result

        ##############################################
        elif (varName == "HospitalDay"):
            try:
                if (varValueDict['HospitalAdmitDate'] > TDF_SMALLEST_VALID_VALUE):
                    varValueDict['HospitalDay'] = (currentDayNum - varValueDict['HospitalAdmitDate']) + 1
            except Exception:
                pass
    # End - CalculateDerivedValuesFORWARDPass





    ################################################################################
    #
    # [TDFFileReader::CalculateGFR]
    #
    # This can use several formula. In all cases, SCr (standardized serum creatinine) = mg/dL
    # However, I ONLY use CKD EPI. It is pretty good, and I use the same consistent estimate,
    # and it does not rely on values like Cystatin C which are not reliably measured.
    #
    # CKD EPI (2021)
    #   eGFR = 142 x min(SCr/κ, 1)^α x max(SCr/κ, 1)^-1.209 x 0.9938^Age x 1.012 [if female] 
    #   Where:
    #      kappa = 0.7 (females) or 0.9 (males)
    #      alpha = -0.241 (females) or -0.302 (males)
    # See: https://www.kidney.org/content/ckd-epi-creatinine-equation-2021
    #
    ################################################################################
    def CalculateGFR(self, currrentCr, patientAge, fIsMale):
        eGFR = TDF_INVALID_VALUE

        #######################
        # CKD EPI
        # eGFR = 141 x min(SCr/κ, 1)^α x max(SCr /κ, 1)^-1.209 x 0.993Age x 1.012 [if female]
        #   Where:
        #      SCr (standardized serum creatinine) = mg/dL
        #      kappa = 0.7 (females) or 0.9 (males)
        #      alpha = -0.241 (females) or -0.302 (males)
        # See: https://www.kidney.org/content/ckd-epi-creatinine-equation-2009
        if ((currrentCr > TDF_SMALLEST_VALID_VALUE) and (patientAge > TDF_SMALLEST_VALID_VALUE)):
            if (fIsMale > 0):
                kappa = 0.9
                alpha = -0.302
            else:
                kappa = 0.7
                alpha = -0.241

            creatKappaRatio = float(currrentCr) / kappa

            eGFR = 142.0
            if (creatKappaRatio < 1):
                eGFR = eGFR * math.pow(creatKappaRatio, alpha)

            if (creatKappaRatio > 1):
                eGFR = eGFR * math.pow(creatKappaRatio, -1.209)

            eGFR = eGFR * math.pow(0.9938, patientAge)
            if (fIsMale <= 0):
                eGFR = eGFR * 1.012

        return eGFR
    # End - TDFFileReader::CalculateGFR()





    ################################################################################
    #
    # [TDFFileReader::ProcessEventNodeForwardImpl]
    #
    # This processes any EVENT node as we move forward in the the timeline. 
    # It updates self.latestTimelineEntryDataList, possibly overwriting earlier outcomes.
    ################################################################################
    def ProcessEventNodeForwardImpl(self, eventNode, eventDateDays):
        eventClass = eventNode.getAttribute("C")
        eventValue = eventNode.getAttribute("V")

        ############################################
        if (eventClass == "Admit"):
            if ('InHospital' in self.allValueVarNameList):
                self.latestTimelineEntryDataList['InHospital'] = 1
            if ('HospitalAdmitDate' in self.allValueVarNameList):
                self.latestTimelineEntryDataList['HospitalAdmitDate'] = eventDateDays
            # Flag_HospitalAdmission is *always* added
            self.latestTimelineEntryDataList['Flag_HospitalAdmission'] = 1

        ############################################
        elif (eventClass == "Discharge"):
            if ('InHospital' in self.allValueVarNameList):
                self.latestTimelineEntryDataList['InHospital'] = 0
            if ('HospitalAdmitDate' in self.allValueVarNameList):
                self.latestTimelineEntryDataList['HospitalAdmitDate'] = TDF_INVALID_VALUE
            # Flag_HospitalDischarge is *always* added
            self.latestTimelineEntryDataList['Flag_HospitalDischarge'] = 1

        ############################################
        elif (eventClass == "Proc"):
            if (("GIProcedures" in self.allValueVarNameList) and (("EGD:" in eventValue) or ("Colonoscopy:" in eventValue))):
                self.latestTimelineEntryDataList['GIProcedures'] = 1
            if ('Procedure' in self.allValueVarNameList):
                self.latestTimelineEntryDataList['Procedure'] = eventValue
            if ((eventValue == "Dialysis") and ('MostRecentDialysisDate' in self.allValueVarNameList)):
                self.latestTimelineEntryDataList['MostRecentDialysisDate'] = eventDateDays

        ############################################
        elif (eventClass == "Surg"):
            if ('MajorSurgeries' in self.allValueVarNameList):
                self.latestTimelineEntryDataList['MajorSurgeries'] += 1
            if ('Surgery' in self.allValueVarNameList):
                self.latestTimelineEntryDataList['Surgery'] = eventValue
            if (('MostRecentMajorSurgeryDate' in self.allValueVarNameList) and (eventValue.startswith("Major"))):
                self.latestTimelineEntryDataList['MostRecentMajorSurgeryDate'] = eventDateDays

        ############################################
        # Transfusions
        elif (eventClass == "Blood"):
            doseStr = eventNode.getAttribute("D")
            eventValParts = eventValue.split(":")
            eventValue = eventValParts[0].lower()
            if (eventValue == "rbc"):
                doseValue = "TransRBC"
            elif (eventValue == "plts"):
                doseValue = "TransPlts"
            elif (eventValue == "ffp"):
                doseValue = "TransFFP"
            elif (eventValue == "cryo"):
                doseValue = "TransCryo"
            else:
                doseValue = ""
    
            if (doseValue in self.allValueVarNameList):
                self.latestTimelineEntryDataList[doseValue] = 1

        ############################################
        # Inpatient medications
        elif (eventClass == "IMed"):
            drugInfoList = eventValue.split(",")
            # Several drugs may be given at the same time.
            # Process each one in turn.
            for drugInfo in drugInfoList:
                # The string drugInfo has at least four format:
                #   medName + ":" + doseStr + ":" + doseRoute + ":" + dosesPerDayInt + ","
                # However, some may not be included in all drug doses.
                medNameAndDoseParts = drugInfo.split(":")
                medName = medNameAndDoseParts[0]
                # Check if this is one of the meds we care about. We are only interested
                # in a few, like meds whose drug levels we predict.
                if (medName in self.allValueVarNameList):
                    numNameParts = len(medNameAndDoseParts)

                    # Extract the parts of the med. Note that not all parts will be
                    # specified for each drug dose.
                    if (numNameParts >= 4):
                        dosesPerDayFloat = float(medNameAndDoseParts[3])
                        dosesPerDayInt = int(dosesPerDayFloat)
                        doseRoute = medNameAndDoseParts[2]
                        doseStr = medNameAndDoseParts[1]
                    else:
                        dosesPerDayInt = 1
                        if (numNameParts >= 3):
                            doseRoute = medNameAndDoseParts[2]
                            doseStr = medNameAndDoseParts[1]
                        else:
                            doseRoute = "i"
                            if (numNameParts >= 2):
                                doseStr = medNameAndDoseParts[1]
                            else:
                                doseStr = "1"
                            # End - (numNameParts < 3)
                        # End - (numNameParts < 4)
                    # End - (numNameParts < 5)

                    # Be careful. Some meds are things like "Pharmacist to dose" and do not have a dose number.
                    if (doseStr in ("0", "")):
                        doseStr = "1"
                    doseFloat = float(doseStr)

                    # BUG! <> FIXME
                    # Some meds are ordered incorrectly, so they have total dose # num split doses.
                    # For example somebody may order 3750 Vanc TID when they mean 1250 TID for a total of 3750.
                    # Try to detect this and work around it.
                    labInfo = g_LabValueInfo[medName]
                    halfMaxVal = float(labInfo['maxVal']) / 2.0
                    if (doseFloat > halfMaxVal):
                        dosesPerDayInt = 1

                    # Ignore oral Vanc
                    if (("VancDose" == medName) and ("o" == doseRoute)):
                        pass
                    # Ignore doses that do not make sense
                    elif (("VancDose" == medName) and (doseFloat < 100)):
                        pass
                    else:
                        # Add this to the daily total. Some meds may be given daily, or Q12h or Q8h.
                        # We use the total daily dose for each day. 
                        # It was initialized to 0 when we started each new day

                        # BUG! <> FIXME
                        # Some data records the meds that are ordered, not given. So, if you order something
                        # and then cancel it and re-order it with a new time or priority or stat, then those will
                        # both show up. That is incorrect, since the initial replaced orders may never be given.
                        # So, we *replace* the old value, not add to it. 
                        #
                        # If we take data from a MAR and only record the given doses, then this needs to be changed to:
                        #       self.latestTimelineEntryDataList[medName] += (doseFloat * dosesPerDayInt)
                        self.latestTimelineEntryDataList[medName] = (doseFloat * dosesPerDayInt)
                # End - if (medName in self.allValueVarNameList):
            # End - for drugInfo in drugInfoList
        # End - elif (eventClass == "Med"):
    # End - ProcessEventNodeForwardImpl






    ################################################################################
    #
    # [TDFFileReader::RecordTimeMilestonesOnForwardPass]
    #
    # This is done on the FORWARD pass
    ################################################################################
    def RecordTimeMilestonesOnForwardPass(self, timeLineData, currentDayNum):
        # In an AKI, the eGFR (I know, it's not validated for AKI...) may change up and down.
        # So, we say you start a particular stage of CKD if the current eGFR meets a criteria
        # now and will not fail to meet that criteria again in the future.
        # For example, you are CKD4 if you meet CKD4 now and will never be CKD3b in the future.
        # As a result, on the forward pass, if you do meet CKD3b now, then cancel any previous
        # timestamps for CKD4, since they were obviously premature (likely an AKI that resolved).
        # 
        # Additionally, we set any missing previous CKD dates for previous stages of CKD.
        # For example, if a declining patient is CKD3a then CKD3b then CKD4, but the first we see
        if ("GFR" in timeLineData):
            currentGFR = timeLineData["GFR"]

            # Beware the boundary cases. From KDIGO:
            #   CKD3a is GFR 45-59
            #   CKD3a is GFR 30-44
            #   CKD3a is GFR 15-29
            #   CKD is GFR <15
            if (currentGFR < TDF_SMALLEST_VALID_VALUE):
                pass
            elif (currentGFR < 15):
                if (self.StartCKD5Date < 0):
                    self.StartCKD5Date = currentDayNum
            elif (15 <= currentGFR < 30):
                if (self.StartCKD4Date < 0):
                    self.StartCKD4Date = currentDayNum
                self.StartCKD5Date = TDF_INVALID_VALUE
            elif (30 <= currentGFR < 45):
                if (self.StartCKD3bDate < 0):
                    self.StartCKD3bDate = currentDayNum
                self.StartCKD4Date = TDF_INVALID_VALUE
                self.StartCKD5Date = TDF_INVALID_VALUE
            elif (45 <= currentGFR < 60):
                if (self.StartCKD3aDate < 0):
                    self.StartCKD3aDate = currentDayNum
                self.StartCKD3bDate = TDF_INVALID_VALUE
                self.StartCKD4Date = TDF_INVALID_VALUE
                self.StartCKD5Date = TDF_INVALID_VALUE
            elif (currentGFR >= 60):
                self.StartCKD3aDate = TDF_INVALID_VALUE
                self.StartCKD3bDate = TDF_INVALID_VALUE
                self.StartCKD4Date = TDF_INVALID_VALUE
                self.StartCKD5Date = TDF_INVALID_VALUE
    # End - RecordTimeMilestonesOnForwardPass






    ################################################################################
    #
    # [TDFFileReader::CalculateAllDerivedValuesREVERSEPass]
    #
    # This processes any DATA node as we move REVERSE in the the timeline. 
    # It also propagates values backward in time. This lets nodes record the time until 
    # some future event
    #
    # This runs after the forward and since it is in reverse everything from the future is
    # already known. As a result, it can calculate values based on both current data 
    # and future events. For example, on the forward pass, we computed the date when some 
    # milestones are first met. Now, on the reverse pass, update each timeline point with 
    # data about the future. So, every value will know when a future milestone will be met.
    ################################################################################
    def CalculateAllDerivedValuesREVERSEPass(self, reversePassTimeLineData, currentDayNum):
        #print("CalculateAllDerivedValuesREVERSEPass")
        currentCr = TDF_INVALID_VALUE
        inAKI = 0

        ##########################################
        # Update the baseline Cr
        # ------------------------
        # The baseline Cr is tricky and requires past and future knowledge.
        # Consider a pt with Cr 1.0, then goes to an AKI with peak Cr 2.9 then
        # recovers to a new baseline Cr of 1.4.
        #
        # Baseline is the lowest value of the past 7 days, but also cannot be higher 
        # than the lowest future value.
        #
        # If a future Cr (one we previously saw in the reverse direction) is
        # LESS than the current Cr, then the current Cr reflects an AKI, not baseline.
        # In this case, just copy the future baseline back to this point.
        # Otherwise, update the Cr.
        if (("BaselineCr" in self.allValueVarNameList) 
                or ("BaselineGFR" in self.allValueVarNameList)):
            # These were calculated earlier, on the FORWARD pass, using a TimeSeries
            # which was a running list of the most recent 7 days of recent values
            try:
                baselineCr = reversePassTimeLineData['BaselineCr']
            except Exception:
                baselineCr = TDF_INVALID_VALUE

            # Extend the lowest Cr from the future by adding information from present.
            # The future lowest Cr is the lowest value of all Cr from now into the future.
            try:
                currentCr = reversePassTimeLineData['Cr']
            except Exception:
                currentCr = TDF_INVALID_VALUE

            if ((currentCr > TDF_SMALLEST_VALID_VALUE)
                    and ((self.FutureBaselineCr < TDF_SMALLEST_VALID_VALUE) 
                        or (currentCr < self.FutureBaselineCr))):
                self.FutureBaselineCr = currentCr
            # End - if (currentCr > TDF_SMALLEST_VALID_VALUE):

            # The current baseline cannot be worse than what it will be.
            if ((self.FutureBaselineCr > TDF_SMALLEST_VALID_VALUE) 
                    and (self.FutureBaselineCr < baselineCr)):
                reversePassTimeLineData["BaselineCr"] = self.FutureBaselineCr

            # The baseline GFR is derived from the baseline Creatinine
            try:
                patientAge = reversePassTimeLineData['AgeInYrs']
            except Exception:
                patientAge = TDF_INVALID_VALUE
            try:
                fIsMale = reversePassTimeLineData['IsMale']
            except Exception:
                fIsMale = TDF_INVALID_VALUE

            eGFR = self.CalculateGFR(baselineCr, patientAge, fIsMale)
            if (eGFR > TDF_SMALLEST_VALID_VALUE):
                reversePassTimeLineData["BaselineGFR"] = round(eGFR)
        # End - if (varName = "BaselineGFR"):


        ##########################################
        # Now we know the baselines, we can decide whether we are in an AKI.
        # If we are not at baseline Cr, then we are in AKI
        if ("InAKI" in self.allValueVarNameList):
            inAKI = 0
            deltaCr = TDF_INVALID_VALUE
            try:
                currentCr = reversePassTimeLineData['currentCr']
            except Exception:
                currentCr = TDF_INVALID_VALUE
            try:
                baselineCr = reversePassTimeLineData['BaselineCr']
            except Exception:
                baselineCr = TDF_INVALID_VALUE

            if ((currentCr > TDF_SMALLEST_VALID_VALUE) and (baselineCr > TDF_SMALLEST_VALID_VALUE)):
                deltaCr = currentCr - baselineCr
                # Like KDIGO, I use 0.3 as the threshold, but only for basic Cr
                # The threshold should depend on the CKD. A variation of 0.3
                # when the baseline GFR is 20 and Cr is 2.5, is probably not a real AKI.
                # Still, this is what the guidelines say.
                if ((baselineCr <= 1.5) and (deltaCr >= 0.3)):
                    inAKI = 1
                if (deltaCr >= (1.5 * baselineCr)):
                    inAKI = 1
            # End - if ((currentCr > TDF_SMALLEST_VALID_VALUE) and (baselineCr > TDF_SMALLEST_VALID_VALUE)):

            reversePassTimeLineData["InAKI"] = inAKI
            # Computing the dates of the next AKI or AKI recovery is different than CKD.
            # CKD stage monotonically increases, but AKI's may come and go. As a result,
            # We must store these in the timeline itself, not in member variables.
            if (inAKI):
                reversePassTimeLineData["NextAKIDate"] = currentDayNum
            else:
                reversePassTimeLineData["NextCrAtBaselineDate"] = currentDayNum
        # End - if ("InAKI" in self.allValueVarNameList):


        ##########################################
        # Computing the dates of the next AKI or AKI recovery is different than CKD.
        # CKD stage monotonically increases, but AKI's may come and go. As a result,
        # we only use the AKI from the timeline.
        if ("Future_Days_Until_AKI" in self.allValueVarNameList):
            try:
                dateOfNextAKI = reversePassTimeLineData['NextAKIDate']
            except Exception:
                dateOfNextAKI = TDF_INVALID_VALUE
            deltaDays = dateOfNextAKI - currentDayNum
            if ((dateOfNextAKI > 0) and (deltaDays > 0)):
                reversePassTimeLineData["Future_Days_Until_AKI"] = deltaDays
            else:
                reversePassTimeLineData["Future_Days_Until_AKI"] = TDF_INVALID_VALUE

        if ("Future_Days_Until_AKIResolution" in self.allValueVarNameList):
            try:
                dateOfNextAKIResolution = reversePassTimeLineData['NextCrAtBaselineDate']
            except Exception:
                dateOfNextAKIResolution = TDF_INVALID_VALUE

            deltaDays = dateOfNextAKIResolution - currentDayNum
            if ((dateOfNextAKIResolution > 0) and (deltaDays > 0)):
                reversePassTimeLineData["Future_Days_Until_AKIResolution"] = deltaDays
            else:
                reversePassTimeLineData["Future_Days_Until_AKIResolution"] = TDF_INVALID_VALUE

        ##########################################
        # These dates were calculated on the forward pass, but they get propagated backward
        # once we do the reverse pass. They are only valid once we have seen the entire timeline.
        if ("StartCKD5Date" in self.allValueVarNameList):
            reversePassTimeLineData["StartCKD5Date"] = self.StartCKD5Date
        if ("StartCKD4Date" in self.allValueVarNameList):
            reversePassTimeLineData["StartCKD4Date"] = self.StartCKD4Date
        if ("StartCKD3bDate" in self.allValueVarNameList):
            reversePassTimeLineData["StartCKD3bDate"] = self.StartCKD3bDate
        if ("StartCKD3aDate" in self.allValueVarNameList):
            reversePassTimeLineData["StartCKD3aDate"] = self.StartCKD3aDate

        ##############################################
        # CKD 5
        if ("Future_Boolean_CKD5" in self.allValueVarNameList):
            result = 1 if (self.StartCKD5Date > 0) else 0
            reversePassTimeLineData["Future_Boolean_CKD5"] = result

        if ("Future_Days_Until_CKD5" in self.allValueVarNameList):
            if ((self.StartCKD5Date > 0) and (currentDayNum <= self.StartCKD5Date)):
                reversePassTimeLineData["Future_Days_Until_CKD5"] = self.StartCKD5Date - currentDayNum
            else:
                reversePassTimeLineData["Future_Days_Until_CKD5"] = TDF_INVALID_VALUE

        if ("Future_CKD5_2YRS" in self.allValueVarNameList):
            eventWillHappen = False
            if (self.StartCKD5Date > 0):
                daysUntilEvent = self.StartCKD5Date - currentDayNum
                if (daysUntilEvent < 730):
                    eventWillHappen = True
            reversePassTimeLineData["Future_CKD5_2YRS"] = eventWillHappen

        if ("Future_CKD5_5YRS" in self.allValueVarNameList):
            eventWillHappen = False
            if (self.StartCKD5Date > 0):
                daysUntilEvent = self.StartCKD5Date - currentDayNum
                if (daysUntilEvent < 1825):
                    eventWillHappen = True
            reversePassTimeLineData["Future_CKD5_5YRS"] = eventWillHappen

        ##############################################
        # CKD 4
        if ("Future_Boolean_CKD4" in self.allValueVarNameList):
            result = 1 if (self.StartCKD4Date > 0) else 0
            reversePassTimeLineData["Future_Boolean_CKD4"] = result

        if ("Future_Days_Until_CKD4" in self.allValueVarNameList):
            if ((self.StartCKD4Date > 0) and (currentDayNum <= self.StartCKD4Date)):
                daysUntilEvent = self.StartCKD4Date - currentDayNum
            else:
                daysUntilEvent = TDF_INVALID_VALUE
            reversePassTimeLineData["Future_Days_Until_CKD4"] = daysUntilEvent

        if ("Future_CKD4_2YRS" in self.allValueVarNameList):
            eventWillHappen = False
            if (self.StartCKD4Date > 0):
                daysUntilEvent = self.StartCKD4Date - currentDayNum
                if (daysUntilEvent < 730):
                    eventWillHappen = True
            reversePassTimeLineData["Future_CKD4_2YRS"] = eventWillHappen

        if ("Future_CKD4_5YRS" in self.allValueVarNameList):
            eventWillHappen = False
            if (self.StartCKD4Date > 0):
                daysUntilEvent = self.StartCKD4Date - currentDayNum
                if (daysUntilEvent < 1825):
                    eventWillHappen = True
            reversePassTimeLineData["Future_CKD4_5YRS"] = eventWillHappen

        ##############################################
        # CKD 3b
        if ("Future_Boolean_CKD3b" in self.allValueVarNameList):
            result = 1 if (self.StartCKD3bDate > 0) else 0
            reversePassTimeLineData["Future_Boolean_CKD3b"] = result

        if ("Future_Days_Until_CKD3b" in self.allValueVarNameList):
            if ((self.StartCKD3bDate > 0) and (currentDayNum <= self.StartCKD3bDate)):
                daysUntilEvent = self.StartCKD3bDate - currentDayNum
            else:
                daysUntilEvent = TDF_INVALID_VALUE
            reversePassTimeLineData["Future_Days_Until_CKD3b"] = daysUntilEvent

        if ("Future_CKD3b_2YRS" in self.allValueVarNameList):
            eventWillHappen = False
            if (self.StartCKD3bDate > 0):
                daysUntilEvent = self.StartCKD3bDate - currentDayNum
                if (daysUntilEvent < 730):
                    eventWillHappen = True
            reversePassTimeLineData["Future_CKD3b_2YRS"] = eventWillHappen

        if ("Future_CKD3b_5YRS" in self.allValueVarNameList):
            eventWillHappen = False
            if (self.StartCKD3bDate > 0):
                daysUntilEvent = self.StartCKD3bDate - currentDayNum
                if (daysUntilEvent < 1825):
                    eventWillHappen = True
            reversePassTimeLineData["Future_CKD3b_5YRS"] = eventWillHappen

        ##############################################
        # CKD 3a
        if ("Future_Boolean_CKD3a" in self.allValueVarNameList):
            result = 1 if (self.StartCKD3aDate > 0) else 0
            reversePassTimeLineData["Future_Boolean_CKD3a"] = result

        if ("Future_Days_Until_CKD3a" in self.allValueVarNameList):
            if ((self.StartCKD3aDate > 0) and (currentDayNum <= self.StartCKD3aDate)):
                daysUntilEvent = self.StartCKD3aDate - currentDayNum
            else:
                daysUntilEvent = TDF_INVALID_VALUE
            reversePassTimeLineData["Future_Days_Until_CKD3a"] = daysUntilEvent

        if ("Future_CKD3a_2YRS" in self.allValueVarNameList):
            eventWillHappen = False
            if (self.StartCKD3aDate > 0):
                daysUntilEvent = self.StartCKD3aDate - currentDayNum
                if (daysUntilEvent < 730):
                    eventWillHappen = True
            reversePassTimeLineData["Future_CKD3a_2YRS"] = eventWillHappen

        if ("Future_CKD3a_5YRS" in self.allValueVarNameList):
            eventWillHappen = False
            if (self.StartCKD3aDate > 0):
                daysUntilEvent = self.StartCKD3aDate - currentDayNum
                if (daysUntilEvent < 1825):
                    eventWillHappen = True
            reversePassTimeLineData["Future_CKD3a_5YRS"] = eventWillHappen

        ##############################################
        # Length of Stay
        if ("LengthOfStay" in self.allValueVarNameList):
            try:
                CurrentAdmitDay = reversePassTimeLineData['HospitalAdmitDate']
            except Exception:
                CurrentAdmitDay = TDF_INVALID_VALUE

            if ((CurrentAdmitDay > 0) and (self.NextFutureDischargeDate > 0)):
                reversePassTimeLineData['LengthOfStay'] = self.NextFutureDischargeDate - CurrentAdmitDay
            else:
                reversePassTimeLineData['LengthOfStay'] = TDF_INVALID_VALUE

        ##############################################
        # Discharge
        # If we know the next discharge date, then we can compute how soon that will happen.
        if ("Future_Days_Until_Discharge" in self.allValueVarNameList):
            reversePassTimeLineData["Future_Days_Until_Discharge"] = TDF_INVALID_VALUE
            if (('InHospital' in reversePassTimeLineData) 
                    and (reversePassTimeLineData['InHospital'] > 0) 
                    and (self.NextFutureDischargeDate > 0)):
                daysUntilEvent = max(self.NextFutureDischargeDate - currentDayNum, 0)
                reversePassTimeLineData["Future_Days_Until_Discharge"] = daysUntilEvent
        # End - if (self.NextFutureDischargeDate > 0):

        if ("Future_Category_Discharge" in self.allValueVarNameList):
            reversePassTimeLineData["Future_Category_Discharge"] = TDF_INVALID_VALUE
            if (('InHospital' in reversePassTimeLineData) 
                    and (reversePassTimeLineData['InHospital'] > 0) 
                    and (self.NextFutureDischargeDate > 0)):
                reversePassTimeLineData["Future_Category_Discharge"] = self.ComputeOutcomeCategory(currentDayNum, 
                                                                                    self.NextFutureDischargeDate)
        # End - if (self.NextFutureDischargeDate > 0):
    # End - CalculateAllDerivedValuesREVERSEPass





    ################################################################################
    #
    # [TDFFileReader::ProcessEventNodeInReverseImpl]
    #
    # This processes any EVENT node as we move REVERSE in the the timeline. 
    # It also propagates values backward in time. This lets nodes record the time until 
    # some future event. 
    ################################################################################
    def ProcessEventNodeInReverseImpl(self, reversePassTimeLineData, eventNode, eventDateDays):
        eventClass = eventNode.getAttribute("C")

        #####################
        if (eventClass == "Admit"):
            self.NextFutureDischargeDate = TDF_INVALID_VALUE
        #####################
        elif (eventClass == "Discharge"):
            self.NextFutureDischargeDate = eventDateDays
    # End - ProcessEventNodeInReverseImpl




    #####################################################
    #
    # [TDFFileReader::GetNamedValueFromTimeline]
    #
    # The Offsets are in whatever time unit the timeline uuses.
    # This may be days (for labs) or seconds (for vitals).
    # self.TimeGranularity  will be one of:
    #       TDF_TIME_GRANULARITY_DAYS
    #       TDF_TIME_GRANULARITY_SECONDS
    #
    # BUGUG FIXME <> If this is called with several different offsets, 
    # like -1, then -3, then -5, it may return the *same* past timepoint
    # for all of them because it is closest to all offsets.
    #####################################################
    def GetNamedValueFromTimeline(self, valueName, 
                                startOffsetRange, endOffsetRange, rangeOption, 
                                functionObject, 
                                timeLineIndex, prevUsedTimeCode):
        result = TDF_INVALID_VALUE
        fFoundIt = False
        matchingRangeDay = -1

        timelineEntry = self.CompiledTimeline[timeLineIndex]
        currentTimeCode = timelineEntry['TimeCode']
       
        ############################
        # This is the simple case, we want a value from the current position in the timeline.
        # This is likely most common, so special-case this with a fast path.
        # Also, if this uses a function, then we also need the latest value
        #
        # This ASSUMES there is only a SINGLE entry for each timestamp.
        # If there were several entries per timecode, then we would have to find *all* entries
        # for the target range.
        if ((startOffsetRange == endOffsetRange == 0) or (functionObject is not None)):
            latestValues = timelineEntry['data']
            if (valueName not in latestValues):
                return False, TDF_INVALID_VALUE, -1

            result = latestValues[valueName]
            if (result < TDF_SMALLEST_VALID_VALUE):
                return False, TDF_INVALID_VALUE, -1

            # If there is no function, then we are done.
            if (functionObject is None):
                return True, result, currentTimeCode
            else:
                timeCodeInDays = int(currentTimeCode / (60 * 60 * 24))
                timeCodeInHrs = int(currentTimeCode / (60 * 60)) - (timeCodeInDays * 24)
                timeCodeInMin = int(currentTimeCode / 60) - ((timeCodeInDays * 24 * 60) + (timeCodeInHrs * 60))
                timeCodeInSecs = currentTimeCode - ((timeCodeInDays * 60 * 60 * 24) + (timeCodeInHrs * 60 * 60) + (timeCodeInMin * 60))
                result = functionObject.ComputeNewValue(result, timeCodeInDays, timeCodeInHrs, timeCodeInMin, timeCodeInSecs)

                # Do not panic, this is not a bug or a real error.
                # This normally just means the function may just not have enough historical
                # data to give a meaningful result.
                if (result < TDF_SMALLEST_VALID_VALUE):
                    return False, TDF_INVALID_VALUE, -1

                return True, result, currentTimeCode
            # End - if (functionObject is not None):
        # End - if ((startOffsetRange == endOffsetRange == 0) or (functionObject is not None))

        # Okay, we cannot do the easy way, so now the hard part.
        # We look for the value in a different day or a range of different days.
        referenceTimeCode = currentTimeCode
        if (rangeOption == VARIABLE_RANGE_LAST_MATCH):
            referenceTimeCode = prevUsedTimeCode
        firstTimeCodeInRange = referenceTimeCode + startOffsetRange
        lastTimeCodeInRange = referenceTimeCode + endOffsetRange

        # Decide if we are searching forward or reverse.
        # This compares absolute days, so it is independant of whether the 
        # search is before or after the current day.
        fSearchForward = True
        if (firstTimeCodeInRange > lastTimeCodeInRange):
            fSearchForward = False

        # Now, move to the start of the range.
        # This can be before or after the current time position, and is independant
        # of whether we search forward or backward. All combinations of direction 
        # and future/past are possible. So, for example, you can search FORWARD
        # from offset -5 to offset -2, or BACKWARD from +4 to +1.
        #
        # WARNING! This ASSUMES there is only a SINGLE entry for each day.
        # If there were several entries per day, then we would have to find either the
        # first or last day in the range depending on whether we are searching in forward
        # or reverse direction.
        if ((fSearchForward) and (firstTimeCodeInRange >= currentTimeCode)):
            currentTimeLineIndex = timeLineIndex
            while (currentTimeLineIndex < self.LastTimeLineIndex):
                timelineEntry = self.CompiledTimeline[currentTimeLineIndex]
                if (timelineEntry['TimeCode'] >= firstTimeCodeInRange):
                    break
                currentTimeLineIndex = currentTimeLineIndex + 1
            # End - while (currentTimeLineIndex >= 0):
        elif ((fSearchForward) and (firstTimeCodeInRange <= currentTimeCode)):
            currentTimeLineIndex = timeLineIndex
            testIndex = timeLineIndex
            while (testIndex >= 0):
                timelineEntry = self.CompiledTimeline[testIndex]
                if (timelineEntry['TimeCode'] < firstTimeCodeInRange):
                    break
                currentTimeLineIndex = testIndex
                testIndex = testIndex - 1
            # End - while (currentTimeLineIndex >= 0):
        elif ((not fSearchForward) and (firstTimeCodeInRange > currentTimeCode)):
            currentTimeLineIndex = timeLineIndex
            testIndex = timeLineIndex
            while (testIndex < self.LastTimeLineIndex):
                timelineEntry = self.CompiledTimeline[testIndex]
                if (timelineEntry['TimeCode'] > firstTimeCodeInRange):
                    break
                currentTimeLineIndex = testIndex
                testIndex = testIndex + 1
            # End - while (currentTimeLineIndex >= 0):
        elif ((not fSearchForward) and (firstTimeCodeInRange < currentTimeCode)):
            currentTimeLineIndex = timeLineIndex
            while (currentTimeLineIndex >= 0):
                timelineEntry = self.CompiledTimeline[currentTimeLineIndex]
                if (timelineEntry['TimeCode'] <= firstTimeCodeInRange):
                    break
                currentTimeLineIndex = currentTimeLineIndex - 1

        ############################
        # Search backward
        if (not fSearchForward):
            # Move the index through the timeline until we find and examine 
            # all entries in the range of dates
            while (currentTimeLineIndex >= 0):
                timelineEntry = self.CompiledTimeline[currentTimeLineIndex]
                currentTimeCode = timelineEntry['TimeCode']

                # We are moving backward, so once we are less than the end of the range, quit.
                if (currentTimeCode < lastTimeCodeInRange):
                    break

                labValueDict = timelineEntry['data']
                if (valueName in labValueDict):
                    result = labValueDict[valueName]                        
                    if (TDF_INVALID_VALUE != result):
                        fFoundIt = True
                        matchingRangeDay = currentTimeCode
                        break
                # End - if (valueName in labValueDict):

                currentTimeLineIndex = currentTimeLineIndex - 1
            # End - while ((currentTimeLineIndex >= 0) and ...
        # End - if (firstTimeCodeInRange > lastTimeCodeInRange):
        ############################
        # Otherwise, search forward.
        else:  # (fSearchForward)
            while (currentTimeLineIndex <= self.LastTimeLineIndex):
                timelineEntry = self.CompiledTimeline[currentTimeLineIndex]
                currentTimeCode = timelineEntry['TimeCode']

                # We are moving forward, so once we are past than the end of the range, quit.
                if (currentTimeCode > lastTimeCodeInRange):
                    break

                labValueDict = timelineEntry['data']
                if (valueName in labValueDict):
                    result = labValueDict[valueName]
                    if (TDF_INVALID_VALUE != result):
                        fFoundIt = True
                        matchingRangeDay = currentTimeCode
                        break
                # End - if (valueName in labValueDict):

                currentTimeLineIndex += 1
            # End - while ((currentTimeLineIndex <= self.LastTimeLineIndex) and ...
        # End - if (firstTimeCodeInRange <= lastTimeCodeInRange):

        return fFoundIt, result, matchingRangeDay
    # End - GetNamedValueFromTimeline





    #####################################################
    #
    # [TDFFileReader::CheckIfCurrentTimeMeetsCriteria]
    #
    #####################################################
    def CheckIfCurrentTimeMeetsCriteria(self, 
                                        propertyRelationList, 
                                        propertyNameList, 
                                        propertyValueList, 
                                        timelineEntry):
        latestValues = timelineEntry['data']

        numProperties = len(propertyNameList)                                                
        for propNum in range(numProperties):
            valueName = propertyNameList[propNum]
            if (valueName not in latestValues):
                return False

            actualVal = latestValues[valueName]
            if ((actualVal == TDF_INVALID_VALUE) or (actualVal <= TDF_SMALLEST_VALID_VALUE)):
                return False

            targetVal = float(propertyValueList[propNum])
            relationName = propertyRelationList[propNum]

            try:
                labInfo = g_LabValueInfo[valueName]
            except Exception:
                print("Error! CheckIfCurrentTimeMeetsCriteria found undefined lab name: " + valueName)
                return False
            dataTypeName = labInfo['dataType']

            ###############
            if (relationName == ".EQ."):
                if ((dataTypeName == TDF_DATA_TYPE_FLOAT) and (float(actualVal) != float(targetVal))):
                    return False
                elif ((dataTypeName in (TDF_DATA_TYPE_INT, TDF_DATA_TYPE_BOOL)) and (int(actualVal) != int(targetVal))):
                    return False
            ###############
            elif (relationName == ".NEQ."):
                if ((dataTypeName == TDF_DATA_TYPE_FLOAT) and (float(actualVal) == float(targetVal))):
                    return False
                elif ((dataTypeName in (TDF_DATA_TYPE_INT, TDF_DATA_TYPE_BOOL)) and (int(actualVal) == int(targetVal))):
                    return False
            ###############
            elif (relationName == ".LT."):
                if ((dataTypeName == TDF_DATA_TYPE_FLOAT) and (float(actualVal) >= float(targetVal))):
                    return False
                elif ((dataTypeName in (TDF_DATA_TYPE_INT, TDF_DATA_TYPE_BOOL)) and (int(actualVal) >= int(targetVal))):
                    return False
            ###############
            elif (relationName == ".LTE."):
                if ((dataTypeName == TDF_DATA_TYPE_FLOAT) and (float(actualVal) > float(targetVal))):
                    return False
                elif ((dataTypeName in (TDF_DATA_TYPE_INT, TDF_DATA_TYPE_BOOL)) and (int(actualVal) > int(targetVal))):
                    return False
            ###############
            elif (relationName == ".GT."):
                if ((dataTypeName == TDF_DATA_TYPE_FLOAT) and (float(actualVal) <= float(targetVal))):
                    return False
                elif ((dataTypeName in (TDF_DATA_TYPE_INT, TDF_DATA_TYPE_BOOL)) and (int(actualVal) <= int(targetVal))):
                    return False
            ###############
            elif (relationName == ".GTE."):
                if ((dataTypeName == TDF_DATA_TYPE_FLOAT) and (float(actualVal) < float(targetVal))):
                    return False
                elif ((dataTypeName in (TDF_DATA_TYPE_INT, TDF_DATA_TYPE_BOOL)) and (int(actualVal) < int(targetVal))):
                    return False
            ###############
            else:
                return False
        # End - for propNum in range(numProperties):

        return True
    # End - CheckIfCurrentTimeMeetsCriteria





    #####################################################
    #
    # [TDFFileReader::GetDataForCurrentTimeline]
    #
    # This returns several Numpy Arrays:
    #   - The first is an NxM array of data values
    #           Each column is 1 timestep, and each array is one input variable.
    #
    #   - The second is an Nx1 array of results
    #           It is the result at each time step
    #
    #   - The third is an Nx1 array of timecodes for each result
    #
    #####################################################
    def GetDataForCurrentTimeline(self, 
                                requirePropertyRelationList,
                                requirePropertyNameList,
                                requirePropertyValueList,
                                fAddMinibatchDimension,
                                fNeedTrueResultForEveryInput,
                                numMissingInstances):
        numRequireProperties = len(requirePropertyNameList)
        matchingRangeDay = -1

        # Find where we will look for the data
        firstTimelineIndex = 0
        lastTimelineIndex = self.LastTimeLineIndex

        # Count the max possible number of complete data nodes.
        # We may return less than this, but this lets us allocate result storage.
        maxNumCompleteLabSets = (lastTimelineIndex - firstTimelineIndex) + 1
        if (maxNumCompleteLabSets <= 0):
            return 0, None, None, None

        # Make a vector big enough to hold all possible labs.
        # We will likely not need all of this space, but there is enough
        # room for the most extreme case.
        if (fAddMinibatchDimension):
            inputArray = np.zeros((maxNumCompleteLabSets, 1, self.numInputValues))
            if (self.ConvertResultsToBools):
                resultArray = np.zeros((maxNumCompleteLabSets, 1, 1), dtype=int)
            else:
                resultArray = np.zeros((maxNumCompleteLabSets, 1, 1))
        else:
            inputArray = np.zeros((maxNumCompleteLabSets, self.numInputValues))
            if (self.ConvertResultsToBools):
                resultArray = np.zeros((maxNumCompleteLabSets, 1), dtype=int)
            else:
                resultArray = np.zeros((maxNumCompleteLabSets, 1))
        timeCodeArray = np.zeros((maxNumCompleteLabSets))


        # Initialize all time function objects
        # Things like velocity and acceleration start at an initial state for each different timeline
        for _, functionObject in enumerate(self.allValuesFunctionObjectList):
            if (functionObject is not None):
                functionObject.Reset()

        # This loop will iterate over each step in the timeline.
        # Note, we may have to step over several entries to find all of the data values for one interval.
        lastNonZeroEntryIndex = -1
        timeLineIndex = firstTimelineIndex
        numReturnedDataSets = 0
        prevReturnedTimeCode = -1
        while (timeLineIndex <= lastTimelineIndex):
            timelineEntry = self.CompiledTimeline[timeLineIndex]

            # Check if there are additional requirements for a timeline entry.
            # Do this BEFORE we actually try to read the properties. It may save us the work
            # of getting properties only to throw them away. On the other hand, we may check
            # whether some timeline points are useful even if they do not containt he desired data.
            if (numRequireProperties > 0):
                fOKToUseTimepoint = self.CheckIfCurrentTimeMeetsCriteria(requirePropertyRelationList,
                                                        requirePropertyNameList,
                                                        requirePropertyValueList,
                                                        timelineEntry)
                # We may skip some entries that do not meet some criteria. For example, we may want to see
                # all values of X when y >= 12. Skip this entry if it does not meet the criteria.
                if (not fOKToUseTimepoint):
                    timeLineIndex += 1
                    continue
            # End - if (numRequireProperties > 0):

            # Find the labs we are looking for.
            # There are often lots of labs, but this only return labs that are relevant.
            foundAllInputs = True
            matchingRangeDay = -1
            currentTimeCode = timelineEntry['TimeCode']
            for valueIndex in range(self.numInputValues):
                # Get information about the lab.
                try:
                    valueName = self.allValueVarNameList[valueIndex]
                except Exception:
                    foundAllInputs = False
                    break

                # Get the lab value itself.
                if (valueIndex == self.DaysSincePrevResultIndex):
                    fFoundIt = True
                    matchingRangeDay = timelineEntry['TimeCode']
                    if (prevReturnedTimeCode < 0):
                        result = 30
                    else:
                        result = currentTimeCode - prevReturnedTimeCode
                # End - if (valueIndex == self.DaysSincePrevResultIndex):
                else:
                    foundIt, result, matchingRangeDay = self.GetNamedValueFromTimeline(valueName, 
                                                                self.AllValuesOffsetStartRange[valueIndex],
                                                                self.AllValuesOffsetStopRange[valueIndex],
                                                                self.AllValuesOffsetRangeOption[valueIndex],
                                                                self.allValuesFunctionObjectList[valueIndex],
                                                                timeLineIndex, matchingRangeDay)

                # Some values, like meds, may be zero, and are still considered for short stretches. For example, you
                # can skip a day or two, but not long periods of time.
                fIgnoreRunOfZeroValues = False
                if ((foundIt) and (self.varIndexThatMustBeNonZero == valueIndex) and (self.maxZeroDays > 0)):
                    if (result == 0):
                        if ((lastNonZeroEntryIndex < 0) 
                                or ((timelineEntry['TimeCode'] - lastNonZeroEntryIndex) > self.maxZeroDays)):
                            foundIt = False
                            fIgnoreRunOfZeroValues = True
                        # End - if ((lastNonZeroEntryIndex < 0) or ....
                    # End - if (result == 0):
                    else:
                        lastNonZeroEntryIndex = timelineEntry['TimeCode']
                # End - if ((foundIt) and (varIndexThatMustBeNonZero = valueIndex)):

                if (not foundIt):
                    # Note, foundIt may still be False even for values that default to 0, like drug levels, 
                    # if we cannot find any day with any values in the specified range. 
                    # This is not a bug. Do not freak out. 
                    foundAllInputs = False
                    if (numMissingInstances is not None):
                        numMissingInstances[valueIndex] += 1
                        result = TDF_INVALID_VALUE
                    else:
                        break
                # End - if (not foundIt):

                try:
                    if (fAddMinibatchDimension):
                        inputArray[numReturnedDataSets][0][valueIndex] = result
                    else:
                        inputArray[numReturnedDataSets][valueIndex] = result
                except Exception:
                    print("GetDataForCurrentTimeline. EXCEPTION when writing one value")
                    print("     valueName=" + valueName)
                    print("     fAddMinibatchDimension=" + str(fAddMinibatchDimension))
                    print("     numReturnedDataSets=" + str(numReturnedDataSets) + ", valueIndex=" + str(valueIndex))
                    print("     maxNumCompleteLabSets=" + str(maxNumCompleteLabSets) + ", self.numInputValues=" + str(self.numInputValues))
                    print("GetDataForCurrentTimeline. inputArray.shape=" + str(inputArray.shape))
                    sys.exit(0)
            # End - for valueIndex, valueName in enumerate(self.allValueVarNameList):

            # If we did not find all of the Input values here, move on and try the next timeline position.
            if (not foundAllInputs):
                timeLineIndex += 1
                continue

            # Now, try to get the result for this time step.
            # Note, this is NOT normalized. That is a category ID, or exact value like INR, 
            # so we want the actual numeric value, not a normalized version.            
            foundResult, result, matchingRangeDay = self.GetNamedValueFromTimeline(self.resultValueName, 
                                                                self.resultValueOffsetStartRange, 
                                                                self.resultValueOffsetStopRange, 
                                                                self.resultValueOffsetRangeOption,
                                                                None, timeLineIndex, matchingRangeDay)

            # Sometimes, it is OK if there is not be a result for every intermediate step, only
            # the last step. In that case, just mark the result as IN            
            if ((not foundResult) and (not fNeedTrueResultForEveryInput)):
                result = TDF_INVALID_VALUE
                foundResult = True
            # End - if ((not foundResult) and (not fNeedTrueResultForEveryInput)):

            # If we found all values, then assemble the next vector of results.
            if (foundResult):
                if (fAddMinibatchDimension):
                    resultArray[numReturnedDataSets][0][0] = result
                else:
                    resultArray[numReturnedDataSets][0] = result
                timeCodeArray[numReturnedDataSets] = timelineEntry['TimeCode']
            else:
                timeLineIndex += 1
                continue

            # If every value leads to a separate result, then strip out duplicates.
            # Otherwise, if we can have intermetiate values without a valid result, then even if they are
            # identical, it is still useful, because it tells the system that another time period passed.
            #if ((fNeedTrueResultForEveryInput) and (numReturnedDataSets > 0)):
            if (numReturnedDataSets > 0):
                if (fAddMinibatchDimension):
                    compareVector = inputArray[numReturnedDataSets][0][:] != inputArray[numReturnedDataSets - 1][0][:]
                else:
                    compareVector = inputArray[numReturnedDataSets][:] != inputArray[numReturnedDataSets - 1][:]
                foundUniqueInputVector = any(compareVector)
                # If the inputs are identical, we may still want to include this item if the outputs are identical
                if (not foundUniqueInputVector):
                    if (fAddMinibatchDimension):
                        foundUniqueInputVector = result != resultArray[numReturnedDataSets - 1][0][0]
                    else:
                        foundUniqueInputVector = result != resultArray[numReturnedDataSets - 1][0]
                # End - if (not foundUniqueInputVector):

                if (not foundUniqueInputVector):
                    timeLineIndex += 1
                    continue
            # End - if ((fNeedTrueResultForEveryInput) and (numReturnedDataSets > 0)):

            # If we found all values, then assemble the next vector of results.
            numReturnedDataSets += 1
            prevReturnedTimeCode = currentTimeCode
            if (numReturnedDataSets >= maxNumCompleteLabSets):
                break
            timeLineIndex += 1
        # End - while (timeLineIndex <= lastTimelineIndex)

        if (numReturnedDataSets <= 0):
            return 0, None, None, None
        # End - if (numReturnedDataSets <= 0):

        if (numReturnedDataSets > maxNumCompleteLabSets):
            TDF_Log("ERROR! numReturnedDataSets != numCompleteLabSets")
            numReturnedDataSets = maxNumCompleteLabSets

        # The client expects that the returned arrays will be the exact size, so
        # we have to return a full array, without any unused rows. Trim off rows we
        # did not use.
        if (fAddMinibatchDimension):
            inputArray = inputArray[:numReturnedDataSets, :1, :self.numInputValues]
            resultArray = resultArray[:numReturnedDataSets, :1, :1]
        else:
            inputArray = inputArray[:numReturnedDataSets, :self.numInputValues]
            resultArray = resultArray[:numReturnedDataSets, :1]
        timeCodeArray = timeCodeArray[:numReturnedDataSets]

        return numReturnedDataSets, inputArray, resultArray, timeCodeArray
    # End - GetDataForCurrentTimeline()







    #####################################################
    #
    # [TDFFileReader::GetSyncedPairOfValueListsForCurrentTimeline]
    #
    # This returns two lists of values, and is used when we compute 
    # correlations
    #####################################################
    def GetSyncedPairOfValueListsForCurrentTimeline(self, 
                                            nameStem1, 
                                            valueOffset1, 
                                            functionObject1, 
                                            nameStem2, 
                                            valueOffset2, 
                                            functionObject2,
                                            requirePropertyNameList,
                                            requirePropertyRelationList,
                                            requirePropertyValueList):
        numRequireProperties = len(requirePropertyNameList)
        timeCodeWithSavedValues = TDF_INVALID_VALUE
        value1FromCurrentTimeCode = TDF_INVALID_VALUE
        value2FromCurrentTimeCode = TDF_INVALID_VALUE
        valueList1 = []
        valueList2 = []
        matchingRangeDay = -1

        # Initialize the time function objects
        # Things like velocity and acceleration start at an initial state for each different timeline
        if (functionObject1 is not None):
            functionObject1.Reset()
        if (functionObject2 is not None):
            functionObject2.Reset()

        # This loop will iterate over each step in the timeline.
        for timeLineIndex in range(self.LastTimeLineIndex + 1):
            timelineEntry = self.CompiledTimeline[timeLineIndex]
            currentTimeCode = timelineEntry['TimeCode']

            # If we are starting a new time, then check the time we just finished.
            # If it has both values, then save them to the result list.
            if (timeCodeWithSavedValues != currentTimeCode):
                if ((value1FromCurrentTimeCode != TDF_INVALID_VALUE) and (value2FromCurrentTimeCode != TDF_INVALID_VALUE)):
                    numSavedValues = len(valueList1)
                    if ((numSavedValues == 0) 
                            or (valueList1[numSavedValues - 1] != value1FromCurrentTimeCode) 
                            or (valueList2[numSavedValues - 1] != value2FromCurrentTimeCode)):
                        valueList1.append(value1FromCurrentTimeCode)
                        valueList2.append(value2FromCurrentTimeCode)
                # End - if ((value1FromCurrentTimeCode != TDF_INVALID_VALUE) and (value2FromCurrentTimeCode != TDF_INVALID_VALUE)):

                value1FromCurrentTimeCode = TDF_INVALID_VALUE
                value2FromCurrentTimeCode = TDF_INVALID_VALUE
                timeCodeWithSavedValues = currentTimeCode
            # End - if (dayNumWithSavedValues != currentTimeCode)

            # Check if this is a timeline entry we care about.
            if (numRequireProperties > 0):
                fMeetsCriteria = self.CheckIfCurrentTimeMeetsCriteria(requirePropertyRelationList,
                                                                    requirePropertyNameList,
                                                                    requirePropertyValueList,
                                                                    timelineEntry)
                if not fMeetsCriteria:
                    continue
            # End - if (numRequireProperties > 0):

            # Find the values we are looking for.
            # If we want to correlate things like a daily med and a lab from morning labs, they
            # may appear at different times on the same day.
            foundNewValue1, value1, matchingRangeDay = self.GetNamedValueFromTimeline(nameStem1, 
                                                                    valueOffset1, valueOffset1, -1,
                                                                    functionObject1,
                                                                    timeLineIndex, matchingRangeDay)
            foundNewValue2, value2, matchingRangeDay = self.GetNamedValueFromTimeline(nameStem2, 
                                                                    valueOffset2, valueOffset2, -1,
                                                                    functionObject2,
                                                                    timeLineIndex, matchingRangeDay)

            # Save valid values.
            # BE CAREFUL! Some values, like drug doses, may be 0 on days the med is not given.
            # In other words, 0 should be treated like TDF_INVALID_VALUE and ignored.
            if (foundNewValue1 and (value1 not in (TDF_INVALID_VALUE, 0))):
                value1FromCurrentTimeCode = value1
            if (foundNewValue2 and (value2 not in (TDF_INVALID_VALUE, 0))):
                value2FromCurrentTimeCode = value2
        # End - for timeLineIndex in range(self.LastTimeLineIndex + 1)

        # If the last day has both values, then save them to the result list.
        if ((value1FromCurrentTimeCode != TDF_INVALID_VALUE) and (value2FromCurrentTimeCode != TDF_INVALID_VALUE)):
            numSavedValues = len(valueList1)
            if ((numSavedValues == 0) 
                    or (valueList1[numSavedValues - 1] != value1FromCurrentTimeCode) 
                    or (valueList2[numSavedValues - 1] != value2FromCurrentTimeCode)):
                valueList1.append(value1FromCurrentTimeCode)
                valueList2.append(value2FromCurrentTimeCode)
        # End - if ((value1FromCurrentTimeCode != TDF_INVALID_VALUE) and (value2FromCurrentTimeCode != TDF_INVALID_VALUE)):

        return valueList1, valueList2
    # End - GetSyncedPairOfValueListsForCurrentTimeline()





    ################################################################################
    #
    # [GetMaxDaysWithZeroValue]
    #
    ################################################################################
    def GetMaxDaysWithZeroValue(self):
        maxDays = 1024 * 1024
        for _, labInfo in enumerate(self.allValuesLabInfoList):
            if ((labInfo is not None) and ('MaxDaysWithZero' in labInfo)):
                currentMaxDays = labInfo['MaxDaysWithZero']
                if ((currentMaxDays > 0) and (currentMaxDays < maxDays)):
                    maxDays = currentMaxDays
        # End - for _, varName in enumerate(self.allValueVarNameList):

        return maxDays
    # End - GetMaxDaysWithZeroValue

# End - class TDFFileReader








################################################################################
# A public procedure.
################################################################################
def TDF_GetVariableType(fullValueName):
    # Get information about the lab.
    labInfo, _, _, _, _, functionName = TDF_ParseOneVariableName(fullValueName)
    if (labInfo is None):
        #print("Error! TDF_GetVariableType found undefined lab name: " + fullValueName)
        return TDF_DATA_TYPE_UNKNOWN

    # If the functionName is not NULL, then use that to determine the type
    if ((functionName is not None) and (functionName in g_FunctionInfo)):
        functionInfo = g_FunctionInfo[functionName]
        funcReturnType = functionInfo['resultDataType']
        # Some functions are always the same type as the variable
        if (funcReturnType != TDF_DATA_TYPE_UNKNOWN):
            return funcReturnType
    # End - if ((functionName is not None) and (functionName in g_FunctionInfo)):

    return labInfo['dataType']
# End - TDF_GetVariableType




################################################################################
# A public procedure.
################################################################################
def TDF_GetMinMaxValuesForVariable(fullValueName):
    # Get information about the lab.
    labInfo, _, _, _, _, _ = TDF_ParseOneVariableName(fullValueName)
    if (labInfo is None):
        print("Error! TDF_GetMinMaxValuesForVariable found undefined lab name: " + fullValueName)
        return TDF_INVALID_VALUE, TDF_INVALID_VALUE

    labMinVal = float(labInfo['minVal'])
    labMaxVal = float(labInfo['maxVal'])
    return labMinVal, labMaxVal
# End - TDF_GetMinMaxValuesForVariable




################################################################################
# A public procedure.
################################################################################
def TDF_GetNumClassesForVariable(fullValueName):
    # Get information about the lab.
    labInfo, _, _, _, _, _ = TDF_ParseOneVariableName(fullValueName)
    if (labInfo is None):
        print("Error! TDF_GetNumClassesForVariable found undefined lab name: " + fullValueName)
        return 1

    # A boolean is treated like a 2-class category variable.
    if (labInfo['dataType'] == TDF_DATA_TYPE_BOOL):
        numVals = 2
    else:
        numVals = 1

    return numVals
# End - TDF_GetNumClassesForVariable




#####################################################
#
# [TDFFileReader::TDF_ParseOneVariableName]
#
#####################################################
def TDF_ParseOneVariableName(valueName):
    labInfo = None
    valueOffsetStartRange = 0
    valueOffsetStopRange = 0
    valueOffsetRangeOption = VARIABLE_RANGE_SIMPLE
    functionName = ""
    
    # The variable names come from a user config file, so may have whitespace.
    valueName = valueName.replace(" ", "")

    # Any variable may have a function. For example: Cr.rate
    # Check if there is a function marker to see if we need to 
    # parse this.
    if (VARIABLE_FUNCTION_MARKER in valueName):
        nameParts = valueName.split(VARIABLE_FUNCTION_MARKER, 1)
        valueName = nameParts[0]
        functionName = nameParts[1]
    # End - if (VARIABLE_START_PARAM_ARGS_MARKER in varName):

    # A single name may have one of several forms:
    #   "foo"
    #   "foo[offset]" where offset is an integer, and may be positive (5) or negative (-2)
    #   "foo[start:stop]" where start and stop are both offsets
    #   "foo[@ offset]"
    #   "foo[@ start:stop]"
    #
    # Future options:
    #   "foo[largest start:stop]"
    #   "foo[smallest start:stop]"
    #   "foo[avg start:stop]"
    #   "foo[first start:stop]"
    #   "foo[last start:stop]"
    #
    # Split the names into name stems and optional offsets
    valueOffsetStr = ""
    if (VARIABLE_START_OFFSET_MARKER in valueName):
        nameParts = valueName.split(VARIABLE_START_OFFSET_MARKER, 1)
        valueName = nameParts[0]
        valueOffsetStr = nameParts[1]
        valueOffsetStr = valueOffsetStr.split(VARIABLE_STOP_OFFSET_MARKER, 1)[0]

        # Parse any range options.
        if (valueOffsetStr.startswith(VARIABLE_RANGE_LAST_MATCH_MARKER)):
            valueOffsetRangeOption = VARIABLE_RANGE_LAST_MATCH
            valueOffsetStr = valueOffsetStr[1:]

        # Check if this is a simple offset like "[1]" or a range like "[1:8]"
        if (VARIABLE_OFFSET_RANGE_MARKER in valueOffsetStr):
            nameParts = valueOffsetStr.split(VARIABLE_OFFSET_RANGE_MARKER, 1)
            if (nameParts[0].lstrip().rstrip() == ""):
                valueOffsetStartRange = 0
            else:
                valueOffsetStartRange = int(nameParts[0])
            if (nameParts[1].lstrip().rstrip() == ""):
                valueOffsetStopRange = 0
            else:
                valueOffsetStopRange = int(nameParts[1])
        else:
            valueOffsetStartRange = int(valueOffsetStr)
            valueOffsetStopRange = valueOffsetStartRange
    # End - if (VARIABLE_START_OFFSET_MARKER in valueName):

    if ((valueName != "") and (valueName in g_LabValueInfo)):
        labInfo = g_LabValueInfo[valueName]

    return labInfo, valueName, valueOffsetStartRange, valueOffsetStopRange, valueOffsetRangeOption, functionName
# End - TDF_ParseOneVariableName





################################################################################
#
# [CreateFilePartitionList]
#
# A public procedure to create a dictionary of partitions in a file.
# This is used by mlEngine to break up a file into chunks
################################################################################
def CreateFilePartitionList(tdfFilePathName, partitionSizeInBytes):
    #print("CreateFilePartitionList. tdfFilePathName = " + tdfFilePathName)
    partitionList = []

    try:
        fileInfo = os.stat(tdfFilePathName)
        fileLength = fileInfo.st_size
    except Exception:
        return partitionList

    partitionStartPos = 0
    while (partitionStartPos < fileLength):
        partitionStopPos = min(partitionStartPos + partitionSizeInBytes, fileLength)
        newDict = {'start': partitionStartPos, 'stop': partitionStopPos, 'ptListStr': ""}
        partitionList.append(newDict)

        partitionStartPos = partitionStopPos
    # End - while (partitionStartPos < fileLength):

    return partitionList
# End - CreateFilePartitionList




################################################################################
# A public procedure.
################################################################################
def TDF_GetNamesForAllVariables():
    listStr = ""
    for _, (varName, _) in enumerate(g_LabValueInfo.items()):
        listStr = listStr + varName + VARIABLE_LIST_SEPARATOR

    # Remove the last separator
    listStr = listStr[:-1]
    return listStr
# End - TDF_GetNamesForAllVariables






################################################################################
#
# [TDFFileReader::RemoveDataOutsideTimeBounds]
#
################################################################################
def RemoveDataOutsideTimeBound(timelineNode, firstDayNum, lastDayNum):
    numDaysKept = 0

    parentNode = timelineNode
    currentNode = dxml.XMLTools_GetFirstChildNode(timelineNode)
    while (currentNode):
        nodeType = dxml.XMLTools_GetElementName(currentNode).lower()

        # We ignore any nodes other than Data and Events
        if (nodeType not in ('e', 'd')):
            # Go to the next XML node in the TDF
            currentNode = dxml.XMLTools_GetAnyPeerNode(currentNode)
            continue
        # Get the timestamp for this XML node.
        labDateDays = -1
        timeStampStr = currentNode.getAttribute("T")
        if ((timeStampStr is not None) and (timeStampStr != "")):
            labDateDays, labDateHours, labDateMins, labDateSecs = TDF_ParseTimeStamp(timeStampStr)

        nextPeer = dxml.XMLTools_GetAnyPeerNode(currentNode)
        if (labDateDays >= 0):
            if ((labDateDays < firstDayNum) or (labDateDays > lastDayNum)):
                parentNode.removeChild(currentNode)
            else:
                numDaysKept += 1

        # Go to the next XML node in the TDF
        currentNode = nextPeer
    # End - while (currentNode):

    return numDaysKept
# End - RemoveDataOutsideTimeBound




#####################################################
# [TDFFileReader::GetTimelineAttribute]
#####################################################
def GetTimelineAttribute(timelineNode, attrName):
    return timelineNode.getAttribute(attrName)




#####################################################
# [TDFFileReader::SetTimelineAttribute]
#####################################################
def SetTimelineAttribute(timelineNode, attrName, attrValue):
    timelineNode.setAttribute(attrName, attrValue)




################################################################################
# A public procedure to create the DataLoader
################################################################################
def TDF_CreateTDFFileReader(tdfFilePathName, inputNameListStr, resultValueName, 
                            requirePropertyNameList):
    fCarryForwardPreviousDataValues = True

    reader = TDFFileReader(tdfFilePathName, inputNameListStr, resultValueName, 
                            requirePropertyNameList, TDF_TIME_GRANULARITY_DAYS,
                            fCarryForwardPreviousDataValues)
    return reader
# End - TDF_CreateTDFFileReader




################################################################################
# A public procedure to create the DataLoader
################################################################################
def TDF_CreateTDFFileReaderEx(tdfFilePathName, inputNameListStr, resultValueName, 
                            requirePropertyNameList, timeGranularity, fCarryForwardPreviousDataValues):
    reader = TDFFileReader(tdfFilePathName, inputNameListStr, resultValueName, 
                            requirePropertyNameList, timeGranularity, fCarryForwardPreviousDataValues)
    return reader
# End - TDF_CreateTDFFileReaderEx




################################################################################
# 
################################################################################
def TDF_CreateNewFileWriter(fileH):
    writer = TDFFileWriter()
    writer.__SetFileOutputFileHandle__(fileH)

    return writer
# End - TDF_CreateNewFileWriter




