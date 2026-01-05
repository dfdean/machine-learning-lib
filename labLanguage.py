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
# LabLangFile
#
# This uses Word2Vec to make word vectors. There are alternatives, but none are great
# - Language models like BERT can make word embeddings, but this breaks up a word into 
# several parts (like stemming maybe?) and assigns a vector to each part. In the language
# of lab values, a single lab may not be easily decomposible
# - GloVe has fewer implementations, and although it may perform better than Word2Vec,
# does not seem to have supported packages for creating word embeddings from another domain
#
# I will use gensim, but even that is not simple. Gensim does not install with Python 3.13 on Fedora.
# I tried a bunch of things (cannot compile because OpenBLAS is installed but PkgConfig cannot find it)
# but none worked so I run it in a Python VirtualEnv with Python 3.10.
#
# *** To Select a Python virtual environment from the command line
#   source gensim_env/bin/activate
#
# *** To Select a Python virtual environment from the command line
#   Open the Command Palette (Ctrl+Shift+P).
#   Select the command, "Python Select Interpreter"
# See https://code.visualstudio.com/docs/python/environments
#
#
# References:
# - https://radimrehurek.com/gensim/models/word2vec.html
# - https://radimrehurek.com/gensim/auto_examples/tutorials/run_word2vec.html
#
# The word2vec papers:
# - https://arxiv.org/pdf/1301.3781
# - https://arxiv.org/abs/1310.4546
#
#
#
#
# - https://huggingface.co/docs/datasets/tutorial
# This creates a Hugging Face dataset for lab values.
# Hugging Face is an open source library now produced by the Hugging Face company 
# from NYC (https://en.wikipedia.org/wiki/Hugging_Face)
#
# - https://medium.com/@Roy.Wong/step-by-step-guide-how-to-use-bert-word-embeddings-in-python-ac7b621771d8
# This only shows how to tokenize and find embeddings of words using pre-trained embedding.
#
################################################################################
import os
import sys
import shutil
import math
import random
from os.path import isfile
import decimal  # For float-to-string workaround
from datetime import datetime
import uuid as UUID
import copy

# UUencoding
import base64

import statistics
from scipy import stats
from scipy.stats import spearmanr
import numpy as np

# Gensim
import gensim
from gensim.models import Word2Vec
from nltk.tokenize import sent_tokenize, word_tokenize
import zipfile as ZipFile

import warnings
warnings.filterwarnings(action='ignore')

import xml.dom
import xml.dom.minidom
from xml.dom.minidom import parseString
from xml.dom.minidom import getDOMImplementation

import xmlTools as dxml
import tdfFile as tdf
import dataShow as DataShow
import medHistogram as MedHistogram



#------------------------------------------------
# File Syntax
#
# This is an XML file with the following sections
#------------------------------------------------

LABLANG_FILE_DOC_ELEMENT_NAME                   = "LabLang"
LABLANG_FILE_HEAD_ELEMENT_NAME                  = "Head"
LABLANG_FILE_CBOW_ELEMENT_NAME                  = "CBOW"

LABLANG_FILE_HEADER_UUID_ELEMENT_NAME           = "UUID"
LABLANG_FILE_HEADER_DERIVEDFROM_ELEMENT_NAME    = "DerivedFrom"
LABLANG_FILE_HEADER_DESC_ELEMENT_NAME           = "Description"
LABLANG_FILE_HEADER_CREATED_ELEMENT_NAME        = "Created"
LABLANG_FILE_HEADER_PADDING_ELEMENT_NAME        = "Padding"

# These are used for parsing, so they are case-normalized.
LABLANG_FILE_LOWERCASE_HEAD_OPEN_ELEMENT        = "<head>"
LABLANG_FILE_LOWERCASE_HEAD_CLOSE_ELEMENT       = "</head>"
LABLANG_FILE_LOWERCASE_DOC_CLOSE_ELEMENT        = "</LabLangFile>"
LABLANG_FILE_LOWERCASE_CBOW_OPEN_ELEMENT        = "<cbow>"
LABLANG_FILE_LOWERCASE_CBOW_CLOSE_ELEMENT       = "</cbow>"

NEWLINE_STR = "\n"
VALUE1_VALUE2_SEPARATOR_CHAR = "~"

# The names of sections
LABLANG_FILE_SECTION_NONE_FILE_EMPTY        = -2
LABLANG_FILE_SECTION_NONE_FILE_COMPLETE     = -1
LABLANG_FILE_SECTION_HEADER                 = 0
LABLANG_FILE_SECTION_NONE                   = 1
LABLANG_FILE_SECTION_CBOW                   = 2

g_LabLangFileHeaderPaddingStr = "\"____________________________________________________________________________________________________\
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
# Special Vocabulary
#------------------------------------------------
LAB_VOCAB_1DAY      = "Pause1Day"
LAB_VOCAB_7DAYS     = "WeekPause7Day"
LAB_VOCAB_30DAYS    = "MonthPause30Day"
LAB_VOCAB_365DAYS   = "YearPause365Day"



# Used for the testing
ERROR_DISTANCES = [0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 2.0, 3.0]





################################################################################
#
# Class LabLangFile
#
################################################################################
class LabLangFile():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, filePathname):
        self.filePathName = filePathname
        self.CurrentSectionInFile = LABLANG_FILE_SECTION_NONE_FILE_EMPTY

        self.fileHeaderStr = ""
        self.fileUUID = str(UUID.uuid4())
        self.derivedFromFileUUID = ""
        self.createDateStr = ""
        self.descriptionStr = ""

        self.TrainingDataSentenceList = []

        self.trainingDataText = ""
        self.numTrainingChunks = 0

        self.CBOWModel = None

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

    def GetNumTrainingChunks(self):
        return self.numTrainingChunks




    #####################################################
    #
    # [LabLangFile::WriteHeader]
    #
    #####################################################
    def WriteHeader(self, fileH):
        fileH.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + NEWLINE_STR)
        fileH.write("<" + LABLANG_FILE_DOC_ELEMENT_NAME + " version=\"0.1\" xmlns=\"http://www.dawsondean.com/ns/LabLang/\">" + NEWLINE_STR)
        fileH.write(NEWLINE_STR)

        fileH.write("<" + LABLANG_FILE_HEAD_ELEMENT_NAME + ">" + NEWLINE_STR)

        fileH.write("    <" + LABLANG_FILE_HEADER_UUID_ELEMENT_NAME + ">" + self.fileUUID 
                    + "</" + LABLANG_FILE_HEADER_UUID_ELEMENT_NAME + ">" + NEWLINE_STR)

        if (self.derivedFromFileUUID != ""):
            fileH.write("    <" + LABLANG_FILE_HEADER_DERIVEDFROM_ELEMENT_NAME + ">" + self.derivedFromFileUUID 
                        + "</" + LABLANG_FILE_HEADER_DERIVEDFROM_ELEMENT_NAME + ">" + NEWLINE_STR)

        fileH.write("    <" + LABLANG_FILE_HEADER_DESC_ELEMENT_NAME + ">" + self.descriptionStr 
                    + "</" + LABLANG_FILE_HEADER_DESC_ELEMENT_NAME + ">" + NEWLINE_STR)    

        if (self.createDateStr != ""):
            fileH.write("    <" + LABLANG_FILE_HEADER_CREATED_ELEMENT_NAME + ">" + self.createDateStr 
                    + "</" + LABLANG_FILE_HEADER_CREATED_ELEMENT_NAME + ">" + NEWLINE_STR)
        else:
            fileH.write("    <" + LABLANG_FILE_HEADER_CREATED_ELEMENT_NAME + ">" + datetime.today().strftime('%b-%d-%Y') + " "
                    + datetime.today().strftime('%H:%M') + "</" + LABLANG_FILE_HEADER_CREATED_ELEMENT_NAME + ">" + NEWLINE_STR)

        fileH.write("    <" + LABLANG_FILE_HEADER_PADDING_ELEMENT_NAME + ">" + g_LabLangFileHeaderPaddingStr 
                    + "</" + LABLANG_FILE_HEADER_PADDING_ELEMENT_NAME + ">" + NEWLINE_STR)

        fileH.write("</" + LABLANG_FILE_HEAD_ELEMENT_NAME + ">" + NEWLINE_STR)    
    # End of WriteHeader





    #####################################################
    #
    # [LabLangFile::WriteFooter]
    #
    # This closes a file. It is NOT atomic, but close to it.
    # Once this procedure returns, the file may remain open but
    # the data on disk should record that the action completed.
    #####################################################
    def WriteFooter(self, fileH):
        fileH.write("</" + LABLANG_FILE_DOC_ELEMENT_NAME + ">" + NEWLINE_STR + NEWLINE_STR + NEWLINE_STR)
        fileH.flush()
        self.CurrentSectionInFile = LABLANG_FILE_SECTION_NONE_FILE_COMPLETE
    # End of WriteFooter




    #####################################################
    #
    # [LabLangFile::WriteStartSection]
    #
    # Start a new section of the file
    # It is NOT atomic, but close to it. Once this procedure 
    # returns, the file may remain open but the data on disk
    #should record that the action completed.
    #####################################################
    def WriteStartSection(self, fileH, sectionID):
        if (LABLANG_FILE_SECTION_CBOW == sectionID):
            fileH.write("<" + LABLANG_FILE_CBOW_ELEMENT_NAME + ">" + NEWLINE_STR)
            fileH.flush()
            self.CurrentSectionInFile = LABLANG_FILE_SECTION_CBOW
    # End of WriteStartSection




    #####################################################
    #
    # [LabLangFile::WriteStopSection]
    #
    # Close and Commit a new section of the file
    # It is NOT atomic, but close to it. Once this procedure 
    # returns, the file may remain open but the data on disk
    #should record that the action completed.
    #####################################################
    def WriteStopSection(self, fileH, sectionID):
        if (LABLANG_FILE_SECTION_CBOW == sectionID):
            fileH.write("<" + LABLANG_FILE_CBOW_ELEMENT_NAME + ">" + NEWLINE_STR)
            fileH.flush()
            self.CurrentSectionInFile = LABLANG_FILE_SECTION_NONE
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
            print("Error from opening Covar file. File=" + newFilePath)
            return
            
        # Write a new fixed header to the dest file
        self.WriteHeader(fileH)
        self.WriteStartSection(fileH, LABLANG_FILE_SECTION_CBOW)

        # Write the Gensim model to a separate file.    
        gensimPath = newFilePath + ".gensim"
        try:
            os.remove(gensimPath)
        except Exception as e:
            pass
        self.CBOWModel.save(gensimPath)

        # Read the serialized file and use it as the CBOW section        
        gensimContents = ""
        try:
            with open(gensimPath, 'rb') as gensimFileH:
                binaryData = gensimFileH.read()
        except Exception as e:
            print("Error from opening gensim file. File=" + gensimPath)
            return

        # Encode the bytes using uu.encode
        gensimContentsBytes = base64.b64encode(binaryData)
        gensimContents = gensimContentsBytes.decode("utf-8")

        try:
            os.remove(gensimPath)
        except Exception as e:
            pass

        # Write the contents to our file
        fileH.write(gensimContents)
        fileH.write("\n")

        self.WriteStopSection(fileH, LABLANG_FILE_SECTION_CBOW)
        self.WriteFooter(fileH)
        fileH.close()
    # End - WriteToFile





    #####################################################
    # [ReadFile]
    #####################################################
    def ReadFile(self):
        # Make sure the result file name exists.
        if (not os.path.isfile(self.filePathName)):
            fileH = open(self.filePathName, "a")
            self.WriteHeader(fileH)
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
        if (self.CurrentSectionInFile != LABLANG_FILE_SECTION_HEADER):
            return
        self.fileHeaderStr = startSectionLine

        ####################
        # Read the file header 
        self.ReadHeader(fileH)

        ####################
        # Read the next section start
        startLine = self.ReadFileSectionStart(fileH)
        if (self.CurrentSectionInFile == LABLANG_FILE_SECTION_CBOW):
            self.ReadCBOWSection(fileH)
            self.CurrentSectionInFile = LABLANG_FILE_SECTION_NONE

        fileH.close()
    # End - ReadFile






    #####################################################
    # [ReadHeader]
    #####################################################
    def ReadHeader(self, fileH):
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
            if (testStr == LABLANG_FILE_LOWERCASE_HEAD_CLOSE_ELEMENT):
                self.fileHeaderStr += currentLine
                self.CurrentSectionInFile = LABLANG_FILE_SECTION_NONE
                break
            elif (testStr == LABLANG_FILE_LOWERCASE_DOC_CLOSE_ELEMENT):
                self.CurrentSectionInFile = LABLANG_FILE_SECTION_NONE_FILE_COMPLETE
                break
            elif (testStr == LABLANG_FILE_LOWERCASE_CBOW_OPEN_ELEMENT):
                self.CurrentSectionInFile = LABLANG_FILE_SECTION_CBOW
                break
            else:
                self.fileHeaderStr += currentLine
        # End - while True


        headerXMLDOM = dxml.XMLTools_ParseStringToDOM(self.fileHeaderStr)
        if (headerXMLDOM is None):
            print("TDFFileReader::__init__. Error from parsing string:")

        headerNode = dxml.XMLTools_GetNamedElementInDocument(headerXMLDOM, "Head")
        if (headerNode is None):
            print("TDFReader.__init__. Head elements is missing: [" + self.fileHeaderStr + "]")
    # End - ReadHeader






    #####################################################
    # [ReadCBOWSection]
    #####################################################
    def ReadCBOWSection(self, fileH):
        cbowSerializedText = ""

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
            if (testStr == LABLANG_FILE_LOWERCASE_CBOW_CLOSE_ELEMENT):
                self.CurrentSectionInFile = LABLANG_FILE_SECTION_NONE
                break
            elif (testStr == LABLANG_FILE_LOWERCASE_DOC_CLOSE_ELEMENT):
                self.CurrentSectionInFile = LABLANG_FILE_SECTION_NONE_FILE_COMPLETE
                break
            elif (testStr == LABLANG_FILE_LOWERCASE_CBOW_OPEN_ELEMENT):
                self.CurrentSectionInFile = LABLANG_FILE_SECTION_CBOW
                break
            else:
                cbowSerializedText += currentLine
        # End - while True

        # Encode the bytes using uu.encode
        gensimContentsBytes = base64.b64decode(cbowSerializedText)

        # Write the Gensim model to a separate file.    
        gensimPath = self.filePathName + ".gensim"

        # Write the serialized file and use it as the CBOW section        
        try:
            os.remove(gensimPath)
        except Exception as e:
            pass
        try:
            with open(gensimPath, 'wb') as gensimFileH:
                gensimFileH.write(gensimContentsBytes)
        except Exception as e:
            print("Error from opening gensim file. File=" + gensimPath)
            return

        self.CBOWModel = gensim.models.Word2Vec.load(gensimPath)
        try:
            os.remove(gensimPath)
        except Exception as e:
            pass
    # End - ReadCBOWSection







    #####################################################
    # [ReadFileSectionStart]
    #####################################################
    def ReadFileSectionStart(self, fileH):
        startLine = ""

        ####################
        # Read to the next section start
        self.CurrentSectionInFile = LABLANG_FILE_SECTION_NONE
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
            if (testStr == LABLANG_FILE_LOWERCASE_HEAD_OPEN_ELEMENT):
                startLine = currentLine
                self.CurrentSectionInFile = LABLANG_FILE_SECTION_HEADER
                break
            elif (testStr == LABLANG_FILE_LOWERCASE_CBOW_OPEN_ELEMENT):
                startLine = currentLine
                self.CurrentSectionInFile = LABLANG_FILE_SECTION_CBOW
                break
        # End - Read the next section start

        return startLine
    # End - ReadFileSectionStart





    #####################################################
    # AddtrainingDataText
    #####################################################
    def AddtrainingDataText(self, newDataChunk):
        cleanedData = newDataChunk.replace("\n", " ")

        self.trainingDataText = self.trainingDataText + cleanedData
        self.numTrainingChunks += 1
    # End - AddtrainingDataText


    #####################################################
    # MakeWordEmbedding
    #####################################################
    def MakeWordEmbedding(self):
        self.CBOWModel = gensim.models.Word2Vec(self.trainingDataText, min_count=1, vector_size=100, window=5)
    # End - MakeWordEmbedding




    #####################################################
    #
    # [LabLangFile::CreateFromTDF]
    #
    #####################################################
    def CreateFromTDF(self, tdfFilePathName):
        currentTimelineID = 0

        self.TrainingDataSentenceList = []

        fCarryForwardPreviousDataValues = False
        varNameListStr = tdf.TDF_GetNamesForAllVariables()

        srcTDF = tdf.TDF_CreateTDFFileReaderEx(tdfFilePathName, varNameListStr, "", [], 
                                                tdf.TDF_TIME_GRANULARITY_DAYS, 
                                                fCarryForwardPreviousDataValues)
        if (srcTDF is None):
            print("CreateFromTDF Error opening src file: " + tdfFilePathName)
            return
 
        # Iterate over every timeline
        fFoundTimeline = srcTDF.GotoFirstTimeline()
        while (fFoundTimeline):
            currentTimelineID = srcTDF.GetCurrentTimelineID()
            if (currentTimelineID < 0):
                print("ERROR! Bad currentTimelineID: " + str(currentTimelineID))
                sys.exit(0)

            # Split all of the data entries up into individual entries, one for each day
            entryList = srcTDF.GetRawAllValuesPerDay()
            numEntries = len(entryList)
            if (numEntries <= 0):
                fFoundTimeline = srcTDF.GotoNextTimeline()
                continue


            # Examine each day
            prevDayNum = -1
            for currentEntry in entryList:
                newSentenceForCurrentDay = []

                # Start with some time delay tokens from the previous day
                currentDay = currentEntry['D']
                if (prevDayNum != -1):
                    deltaDays = currentDay - prevDayNum
                    while (deltaDays > 365):
                        newSentenceForCurrentDay.append(LAB_VOCAB_365DAYS)
                        deltaDays = deltaDays - 365
                    while (deltaDays > 365):
                        newSentenceForCurrentDay(LAB_VOCAB_30DAYS)
                        deltaDays = deltaDays - 30
                    while (deltaDays > 7):
                        newSentenceForCurrentDay(LAB_VOCAB_7DAYS)
                        deltaDays = deltaDays - 7
                    while (deltaDays > 1):
                        newSentenceForCurrentDay(LAB_VOCAB_1DAY)
                        deltaDays = deltaDays - 1
                # End - if (prevDayNum != -1):
                prevDayNum = currentDay

                # Examine each variable in the current day
                for _, (varName, varStr) in enumerate(latestValues.items()):
                    # Skip the day number, we already processed that above.
                    if (varName == 'D'):
                        continue

                    try:
                        valueFloat = float(varStr)
                    except Exception:
                        valueFloat = TDF_INVALID_VALUE
                    if ((valueFloat == TDF_INVALID_VALUE) or (valueFloat <= TDF_SMALLEST_VALID_VALUE)):
                        continue

                    varWord = self.MakeWordForLab(varName, valueFloat)
                    newSentenceForCurrentDay.append(varWord)
            # End - for currentEntry in entryList:

            self.TrainingDataSentenceList.append(newSentenceForCurrentDay)

            fFoundTimeline = srcTDF.GotoNextTimeline()
        # End - while (fFoundTimeline):

        srcTDF.Shutdown()


        # Method 1:
        # self.CBOWModel = gensim.models.Word2Vec(self.trainingDataText, min_count=1, vector_size=100, window=5)


        # Method 2:
        self.CBOWModel = gensim.models.Word2Vec(min_count=1)
        # prepare the model vocabulary
        self.CBOWModel.build_vocab(self.TrainingDataSentenceList)
        # To support linear learning-rate decay from (initial) alpha to min_alpha, and accurate 
        # progress-percentage logging, either total_examples (count of sentences) or total_words 
        # (count of raw words in sentences) MUST be provided. If sentences is the same corpus that 
        # was provided to build_vocab() earlier, you can simply use total_examples=self.corpus_count.
        #
        # To avoid common mistakes around the model’s ability to do multiple training passes itself, an explicit 
        # epochs argument MUST be provided. In the common and recommended case where train() is only called once, 
        # you can set epochs=self.epochs.
        self.CBOWModel.train(self.TrainingDataSentenceList, total_examples=model.corpus_count, epochs=model.epochs)  
    # End - CreateFromTDF







    #####################################################
    #
    # [LabLangFile::TestWithTDF]
    #
    #####################################################
    def TestWithTDF(self, tdfFilePathName, valueNameList, predictedName):
        numErrorRanges = len(ERROR_DISTANCES)
        scoreList = [0] * numErrorRanges
        numValidPredictions = 0
        numInvalidPredictions = 0


        # Make params to open the TDF reader
        fCarryForwardPreviousDataValues = False
        varNameListStr = ""
        for currentVarName in valueNameList:
            varNameListStr = varNameListStr + currentVarName + tdf.VARIABLE_LIST_SEPARATOR
        # End - for currentVarName in valueNameList:
        varNameListStr = varNameListStr[:-1]

        # Open the TDF reader
        srcTDF = tdf.TDF_CreateTDFFileReaderEx(tdfFilePathName, varNameListStr, predictedName, [], 
                                                tdf.TDF_TIME_GRANULARITY_DAYS, 
                                                fCarryForwardPreviousDataValues)
        if (srcTDF is None):
            print("TestWithTDF Error opening src file: " + tdfFilePathName)
            return
 
        # Iterate over every timeline
        fFoundTimeline = srcTDF.GotoFirstTimeline()
        while (fFoundTimeline):
            currentTimelineID = srcTDF.GetCurrentTimelineID()
            if (currentTimelineID < 0):
                print("ERROR! Bad currentTimelineID: " + str(currentTimelineID))
                sys.exit(0)

            numReturnedDataSets, inputArray, resultArray, dayNumArray = srcTDF.GetDataForCurrentTimeline([],
                                                                [],  # requirePropertyNameList,
                                                                [],  # requirePropertyValueList,
                                                                False,  # fAddMinibatchDimension
                                                                True,  # NeedTrueResultForEveryInput
                                                                None)  # Count missing instances
            if (numReturnedDataSets <= 0):
                fFoundTimeline = srcTDF.GotoNextTimeline()
                continue

            numSamples = inputArray.shape[0] - 1
            for sampleNum in range(numSamples):
                currentInputVec = inputArray[sampleNum]
                nextResult = resultArray[sampleNum + 1].item()

                predictedValue = self.GetSimilarLabValue(valueNameList, currentInputVec, predictedName)
                if (predictedValue == TDF_INVALID_VALUE):
                    numInvalidPredictions += 1
                else:
                    numValidPredictions += 1
                    deltaValue = abs(predictedValue - nextResult)
                    for rangeNum in range(numErrorRanges):
                        if (deltaValue <= ERROR_DISTANCES[rangeNum]):
                            scoreList[rangeNum] += 1
                            break
                    # End - for rangeNum in range(numErrorRanges):
                # End - if (predictedValue != TDF_INVALID_VALUE):
            # End - for sampleNum in range(numSamples):

            fFoundTimeline = srcTDF.GotoNextTimeline()
        # End - while (fFoundTimeline):

        srcTDF.Shutdown()
        return scoreList
    # End - TestWithTDF







    #####################################################
    #
    #####################################################
    def MakeWordForLab(self, labName, labValue):
        try:
            labValue = round(labValue, 1)
        except:
            pass

        numStr = str(labValue).replace(".", ".")
        return labName.lower() + "_" + numStr
    # End - LabLang_MakeWordForLab





    #####################################################
    #
    #####################################################
    def GetLabWordStem(self, labName):
        wordParts = labName.lower().split("_")
        return wordParts[0]
    # End - GetLabWordStem




    #####################################################
    #
    #####################################################
    def GetLabWordNumber(self, labName):
        wordParts = labName.lower().split("_")
        if (len(wordParts) < 2):
            return TDF_INVALID_VALUE

        numStr = wordParts[1]
        try:
            labValue = float(numStr)
            return labValue
        except:
            return TDF_INVALID_VALUE
    # End - GetLabWordNumber





    #####################################################
    #
    #####################################################
    def GetSimilarLabValue(self, labNameList, labValueList, targetLabName):
        targetLabName = targetLabName.lower()

        positiveWordList = []
        negativeWordList = []
        for currentName, currentValue in zip(labNameList, labValueList):
            labWord = self.MakeWordForLab(currentName, currentValue)
            positiveWordList.append(labWord)
        # End - for currentName, currentValue in zip(labNameList, labValueList):

        resultList = self.CBOWModel.most_similar(positiveWordList, negativeWordList, topn=20, restrict_vocab=None, indexer=None)

        for resultEntry in resultList:
            resultWord = resultEntry[0]
            resultScore = resultEntry[1]
            wordStem = self.GetLabWordStem(resultWord)
            if (wordStem == targetLabName):
                result = self.GetLabWordNumber(resultWord)
                return result
        # End - for resultEntry in resultList:

            return TDF_INVALID_VALUE
    # End - LabLang_MakeWordForLab


# End - class LabLangFile










#####################################################
#
#####################################################
def LabLang_CreateEmpty(filePath):
    try:
        os.remove(filePath) 
    except Exception:
        pass

    labLangFile = LabLangFile(filePath)
    return labLangFile
# End - LabLang_CreateEmpty




#####################################################
#
#####################################################
def LabLang_CreateFromTDFFile(tdfFilePathName):
    labLangFile = LabLangFile("")
    labLangFile.CreateFromTDF(tdfFilePathName)
    return labLangFile
# End - LabLang_CreateFromTDFFile




#####################################################
#
#####################################################
def LabLang_OpenExisting(filePath):
    labLangFile = LabLangFile(filePath)
    return labLangFile
# End - LabLang_OpenExisting





################################################################################
#
################################################################################



################################################################################
#
# [LabLang_LoadtrainingDataTextFromDirectories]
#
################################################################################
def LabLang_LoadtrainingDataTextFromDirectories(labLang, srcDir):
    if (labLang.GetNumTrainingChunks() >= 2):
        return

    for fileName in os.listdir(srcDir):
        srcFilePath = os.path.join(srcDir, fileName)

        #####################
        if os.path.isfile(srcFilePath):
            try:
                # Specify the encoding to skip the BOM \ufeff at the start of the file
                fileH = open(srcFilePath, 'r', encoding='utf-8-sig')
                contentsTextUnicode = fileH.read()
            except:
                continue
            fileH.close()

            # Convert the text from Unicode to ASCII. 
            try:
                contentsText = contentsTextUnicode.decode("utf-8", "ignore")
            except UnicodeDecodeError as err:
                print("Unicode Error from converting string. err=" + str(err))
                contentsText = contentsTextUnicode
            except Exception:
                print("Error from converting string")
                contentsText = contentsTextUnicode

            labLang.AddtrainingDataText(contentsText)

        #####################
        elif os.path.isdir(srcFilePath):
            LabLang_LoadtrainingDataTextFromDirectories(labLang, srcFilePath)
        # End - elif os.path.isdir(srcFilePath):

        if (labLang.GetNumTrainingChunks() >= 2):
            return
    # End - for fileName in os.listdir(srcDir):
# End - LabLang_LoadtrainingDataTextFromDirectories





labLang = LabLang_CreateEmpty("")
LabLang_LoadtrainingDataTextFromDirectories(labLang, "/home/ddean/ActiveData/mlData/Gutenberg/")
labLang.MakeWordEmbedding()

testFilePath = "/home/ddean/ActiveData/researchResults/labLang/saveState.txt"
labLang.WriteToFile(testFilePath)
newLabLang = LabLang_OpenExisting(testFilePath)

print("XXX Quit")
sys.exit(0)


# The trained word vectors are stored in a KeyedVectors instance, as model.wv:
#vector = model.wv['computer']  # get numpy vector of a word
#sims = model.wv.most_similar('computer', topn=10)  # get other similar words


# The reason for separating the trained vectors into KeyedVectors is that if you don’t need the full model 
# state any more (don’t need to continue training), its state can be discarded, keeping just the vectors and 
# their keys proper.
# This results in a much smaller and faster object that can be mmapped for lightning fast loading and sharing
# the vectors in RAM between processes:
#from gensim.models import KeyedVectors
#word_vectors = model.wv

# Store just the words + their trained embeddings.
#word_vectors.save("word2vec.wordvectors")

# Load back with memory-mapping = read-only, shared across processes.
#wv = KeyedVectors.load("word2vec.wordvectors", mmap='r')

# Get numpy vector of a word
#vector = wv['computer']  

#It is impossible to continue training the vectors loaded from the C format because the hidden weights, 
#vocabulary frequencies and the binary tree are missing. To continue training, you’ll need the full 
#Word2Vec object state, as stored by save(), not just the KeyedVectors


# [] Get word_freq (dict of (str, int)) – A mapping from a word in the vocabulary to its frequency count.


