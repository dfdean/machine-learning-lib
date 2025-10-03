#!/usr/bin/python3
################################################################################
# 
# Copyright (c) 2024 Dawson Dean
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
#
################################################################################
import sys
import copy
from datetime import datetime


IGNORE_BOUND = "Ignore"
LESS_THAN = "LT"
GREATER_THAN = "GT"
GREATER_THAN_EQUAL = "GTE"
INVALID_VALUE = -31415927



################################################################################
#
# class CHTMLFileTemplate
#
# This a a template of an HTML page. It is used to build a new web page with 
# a basic content and then some sections replaced with custom text
################################################################################
BODY_TEXT_VAR_NAME = "<!-- BODY -->"
TABLE_TEXT_VAR_NAME = "<!-- TABLE -->"
JAVASCRIPT_DICT_TEXT_VAR_NAME = "<!-- JSCRIPTDICT -->"
LOG_TEXT_VAR_NAME = "<!-- LOG -->"
class CHTMLFileTemplate(object):
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self):
        self.m_Body = ""
        self.m_TableStr = ""
        self.m_HTMLTableStrList = []
        self.m_JScriptDictEntryList = []
        self.m_LogStrList = []
    # End -  __init__


    #####################################################
    # [CHTMLFileTemplate::
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return
    # End of destructor


    #####################################################
    # [CHTMLFileTemplate::SetBodyStr]
    #####################################################
    def SetBodyStr(self, textStr):
        self.m_Body += textStr


    #####################################################
    # [CHTMLFileTemplate::SetTableStr]
    #####################################################
    def SetTableStr(self, textStr):
        self.m_TableStr = textStr
    # End - SetTableStr


    #####################################################
    # [CHTMLFileTemplate::AddHTMLTableRowToDoc]
    #####################################################
    def AddHTMLTableRowToDoc(self, textStrList):
        rowStr = "<tr>"

        for textStr in textStrList:
            if (textStr.startswith("<td")):
                rowStr = rowStr + " " + str(textStr)
            else:
                rowStr = rowStr + " <td>" + str(textStr) + "</td>"
        # End - for textStr in textStrList:

        rowStr = rowStr + "</tr>\n"
        self.m_HTMLTableStrList.append(rowStr)
    # End - AddHTMLTableRowToDoc



    #####################################################
    # [CHTMLFileTemplate::MakeColoredTableCellStr]
    #####################################################
    def MakeColoredTableCellStr(self, val, greenBoundType, boundValueForGreen, redBoundType, boundValueForRed):
        return self.MakeColoredTableCellStrEx(val, val, greenBoundType, boundValueForGreen, redBoundType, boundValueForRed)



    #####################################################
    # [CHTMLFileTemplate::MakeColoredTableCellStrEx]
    #####################################################
    def MakeColoredTableCellStrEx(self, val, criteriaVal, greenBoundType, boundValueForGreen, redBoundType, boundValueForRed):
        cellStr = ""
        if (greenBoundType != IGNORE_BOUND):
            if ((greenBoundType == LESS_THAN) and (criteriaVal < boundValueForGreen)):
                cellStr = "<td style=\"color:green;\">"
            elif ((greenBoundType == GREATER_THAN) and (criteriaVal > boundValueForGreen)):
                cellStr = "<td style=\"color:green;\">"
            elif ((greenBoundType == GREATER_THAN_EQUAL) and (criteriaVal >= boundValueForGreen)):
                cellStr = "<td style=\"color:green;\">"

        if ((cellStr == "") and (redBoundType != IGNORE_BOUND)):
            if ((redBoundType == LESS_THAN) and (criteriaVal < boundValueForRed)):
                cellStr = "<td style=\"color:red;\">"
            elif ((redBoundType == GREATER_THAN) and (criteriaVal > boundValueForRed)):
                cellStr = "<td style=\"color:red;\">"

        if (cellStr == ""):
           cellStr = "<td>"

        return cellStr + str(val) + "</td>"
    # End - MakeColoredTableCellStrEx




    #####################################################
    # [CHTMLFileTemplate::AddJavascriptTableRow]
    #####################################################
    def AddJavascriptTableRow(self, valueList):
        rowStr = " { "
        for valueInfo in valueList:
            nameStr = valueInfo["Name"]
            valueObject = valueInfo["Value"]
            rowStr = rowStr + " \"" + nameStr + "\" : " + str(valueObject) + ", "
        # End - for valueInfo in valueList:

        # Remove the last ","
        rowStr = rowStr[:-1]

        rowStr = rowStr + "},\n"
        self.m_JScriptDictEntryList.append(rowStr)
    # End - AddJavascriptTableRow




    #####################################################
    # [CHTMLFileTemplate::AddLogStr]
    #####################################################
    def AddLogStr(self, textStr):
        self.m_LogStrList.append(textStr)




    #####################################################
    # [CHTMLFileTemplate::ExpandTemplate]
    #####################################################
    def ExpandTemplate(self, templateFilePathName):
        templateStr = ""
        with open(templateFilePathName, 'r') as fileH:
            templateStr = fileH.read()

        templateStr = templateStr.replace(BODY_TEXT_VAR_NAME, self.m_Body)

        # Make a string with the HTML Table contents
        tableStr = self.m_TableStr
        for currentStr in self.m_HTMLTableStrList:
            tableStr = tableStr + currentStr + "\n"
        templateStr = templateStr.replace(TABLE_TEXT_VAR_NAME, tableStr)

        # Make a string with the Javascript array contents
        dictDeclarationStr = ""
        tableStr = ""
        for currentStr in self.m_JScriptDictEntryList:
            dictDeclarationStr = dictDeclarationStr + currentStr + "\n"
        templateStr = templateStr.replace(JAVASCRIPT_DICT_TEXT_VAR_NAME, dictDeclarationStr)

        # Make a string with the logging contents
        logStr = ""
        for currentStr in self.m_LogStrList:
            logStr = logStr + currentStr + "\n<br>"
        if (logStr != ""):
            logStr = "Log:\n<br>" + logStr
        templateStr = templateStr.replace(LOG_TEXT_VAR_NAME, logStr)

        return templateStr
    # End - ExpandTemplate



    #####################################################
    # [CHTMLFileTemplate::MakeFileFromTemplate]
    #####################################################
    def MakeFileFromTemplate(self, templateFilePathName, outputFilePathName):
        templateStr = self.ExpandTemplate(templateFilePathName)

        # Write the expanded file
        with open(outputFilePathName, "w+") as fileH:
            fileH.write(templateStr)
    # End - MakeFileFromTemplate

# End - CHTMLFileTemplate






################################################################################
################################################################################
def MakeTemplate():
    return CHTMLFileTemplate()
# End - MakeTemplate



