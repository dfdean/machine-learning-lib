##################################################################################
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
# This is designed to be independant of the specific Machine Learning library, so
# it should work equally well with PyTorch or TensorFlow or other libraries. 
# It does assume numpy, but that is common to Python
#
#####################################################################################
#
# Top Level Elements
# ===============================
#   <JobControl>
#       JobName - A string that identifies the job to a human
#       JobSpecVersion - Currently 1.0
#       Status - IDLE, TRAIN, TEST
#       AllowGPU - True/False, defaults to True
#       Debug - True/False, defaults to False
#       LogFilePathName - A pathname where the log file for this execution is stored.
#           This file is created/emptied when the job starts.
#       StressTest - True/False, defaults to False
#   </JobControl>
#
#   <Data>
#       DataFormat 
#           TDF
#       StoreType
#           File
#       TrainData - A file pathname
#       TestData - A file pathname
#       TimeGranularity
#   </Data>
#
#   <Input>
#        <Type>xxxxx</Type>
#       <Test>xxxxx</Test>
#   </Input>
#
#   <Output>
#       <Type>xxxxx</Type>
#       <Value>xxxxx</Value>
#       <When>xxxxx</When>
#   </Output>
#
#   <Network>
#       NetworkType
#           SimpleNet | DeepNet | LSTM
#
#       LogisticOutput
#       OutputThreshold
#           A number between 0 and 1 which determines whether the prediction is true.
#           This is only used for Logistic networks
#
#       InputSequence
#       InputSequenceMinSize
#       InputSequenceMaxSize
#           This defaults to 1 for a function that takes a single value and outputs a result.
#    
#       MaxSequenceDurationInDays
#           How far apart a sequence duration can be spread
#
#       StateSize
#           An integer, 0-N, which is the size of a RNN state vector.
#           If not specified, then this is 0
#           If this is 0, then this is a simple deep neural network. It is
#               an RNN iff this value is present and greater than 0
#
#       <InputLayer>
#           layerOutputSize
#           NonLinear - 
#               LogSoftmax | ReLU | Sigmoid
#           InputValues - A comma-separated list of variables, like "Age,Cr,SBP". 
#               See the TDFTools.py documentation for a list of defined names.
#               The value name appeats in a <D> element. 
#               For example, Hgb would extract data from the following <D> element:
#                   <D C="L" T="100:10:30">Hgb=7.0,</D>
#               Each value may be followed by an offset in brackets
#               Examples: Cr[-1]   INR[next]
#               The number in brackets is the number of days from the current point in the timeline.
#               The offset "next" means the next occurrence.    
#               The special value "Dose" is always followed by a "/" and then the name of a medication.
#               For example Dose/Coumadin is the dose of Coumadin given.
#               Doses may also have offsets. For example Dose/Coumadin[-1] is the dose of Coumadin given 1 day before.
#
#       <HiddenLayer>
#           layerOutputSize
#           NonLinear - 
#               LogSoftmax | ReLU | Sigmoid
#
#       <OutputLayer>
#           layerOutputSize
#           NonLinear - 
#               LogSoftmax | ReLU | Sigmoid
#           ResultValue - A variable name. See the TDFTools.py documentation.
#           Different variables have different interpretations as result values.
#           These include:
#               Number - A numeric value, which may be a dose or a lab value
#               FutureEventClass - A number 0-11. See the TDFTools.py documentation.
#               Binary - A number 0-1
#               FutureEventClass or BinaryDiagnosis will count the number of exact matches; the 
#                   predicted class must exactly match the actual value.
#               Number will count buckets:
#               Exact (to 1 decimal place)
#               Within 2%
#               Within 5%
#               Within 10%
#               Within 25%
#   </Network>
#
#   <Training>
#       LossFunction
#           NLLLoss | BCELoss
#
#       Optimizer
#           SGD
#
#       LearningRate
#       BatchSize
#       NumEpochs
#   </Training>
#
#   <Results>
#       <PreflightResults>
#           <NumSequences>N (int)</NumSequences>
#           <NumItemsPerClass>N (int)</NumItemsPerClass>
#           <InputMins>a,b,c,d,...</InputMins>
#           <InputMaxs>a,b,c,d,...</InputMaxs>
#           <InputRanges>a,b,c,d,...</InputMaxs>
#
#           <ResultMin>xxxxx</ResultMin>
#           <ResultMax>xxxxx</ResultMax>
#           <ResultMean>xxxxx</ResultMean>
#
#           <ResultClassWeightList>
#               <NumResultClasses> Number of classes (int) </NumResultClasses>
#               <ResultClassWeight>
#                   <ResultClassID> class ID (int) </ResultClassID>
#                   <ClassWeight> class ID (float) </ClassWeight>
#               </ResultClassWeight>
#               .....
#           </ResultClassWeightList>
#       </PreflightResults>
#
#       <TrainingResults>
#           NumSequencesTrainedPerEpoch
#           NumTimelinesTrainedPerEpoch
#           NumTimelinesSkippedPerEpoch
#           TrainAvgLossPerEpoch
#          TrainNumItemsPerClass
#       </TrainingResults>
#
#       <TestingResults>
#           <AllTests>
#               NumSequencesTested
#               TestNumItemsPerClass
#               TestNumPredictionsPerClass
#               TestNumCorrectPerClass
#               NumCorrectPredictions
#               TotalAbsError
#               TotalNumPredictions
#               PredictionValueList
#               TrueResultValueList
#               Used for int and float results:
#                  NumPredictionsWithin2Percent
#                   NumPredictionsWithin5Percent
#                   NumPredictionsWithin10Percent
#                   NumPredictionsWithin20Percent
#                   NumPredictionsWithin50Percent
#                   NumPredictionsWithin100Percent
#               Used for class results.
#                   NumPredictionsWithin1Class
#               Used for binary results.
#                   NumPredictionsTruePositive
#                   NumPredictionsTrueNegative
#                   NumPredictionsFalsePositive
#                   NumPredictionsFalseNegative
#           </AllTests>
#
#           <TestSubGroup0>
#               Same as AllTests
#           </TestSubGroup0>
#
#       </TestingResults>
#
#   </Results>
#
#   <Runtime>
#   The runtime state for the Job training/testing sequence. It is describes the execution
#   of a job, not the job results.
#       JobFilePathName
#
#       StartRequestTimeStr
#       StopRequestTimeStr
#
#       CurrentEpochNum
#       TotalTrainingLossInCurrentEpoch
#
#       BufferedLogLines
#
#       OS  
#       CPU
#       GPU
#   </Runtime>
#
# <SavedModelState>
#   <PyTorchOptimizerState>
#   <NeuralNetMatrixList>
#   This is part of SavedModelStateXMLNode, and it is used for neural nets (deep and logistics)
#   The runtime weight matrices and bias vectors for a network.
#   This allows a network to suspend and then later resume its state, possibly in a 
#   different process or a different server.
#       <Weight>
#       <Bias>
#
#####################################################################################
import os
import sys
import re
import io
from datetime import datetime
import platform
import random
import uuid as UUID

import hashlib  # For Hashing an array
import json

from xml.dom.minidom import getDOMImplementation

import numpy

from sklearn.metrics import f1_score
from sklearn.metrics import auc
from sklearn.metrics import roc_auc_score
from sklearn.metrics import precision_recall_curve

# Normally we have to set the search path to load these.
# But, this .py file is always in the same directories as these imported modules.
import xmlTools as dxml
import tdfFile as tdf

NEWLINE_STR = "\n"
ML_JOB_NUM_NUMERIC_VALUE_BUCKETS            = 20




########################################
# XML Elements

# <MLJob>
ROOT_ELEMENT_NAME = "MLJob"
# Attributes
FORMAT_VERSION_ATTRIBUTE    = "JobVersion"
DEFAULT_JOB_FORMAT_VERSION  = 1
JOB_UUID_ELEMENT_NAME = "UUID"

# <JobControl>
JOB_CONTROL_ELEMENT_NAME = "JobControl"
JOB_CONTROL_NAME_ELEMENT_NAME = "Name"
JOB_CONTROL_DESCRIPTION_ELEMENT_NAME = "Description"
JOB_CONTROL_VARIATION_ELEMENT_NAME = "Variation"
JOB_CONTROL_STATUS_ELEMENT_NAME = "Status"
JOB_CONTROL_ERROR_CODE_ELEMENT_NAME = "ErrCode"
JOB_CONTROL_RESULT_MSG_ELEMENT_NAME = "ErrMsg"
JOB_CONTROL_RESULT_MSG_OK = "OK"
JOB_CONTROL_RUN_OPTIONS_ELEMENT_NAME = "RunOptions"
JOB_CONTROL_RUN_OPTION_SEPARATOR_STR = ","
JOB_CONTROL_DEBUG_ELEMENT_NAME = "Debug"
JOB_CONTROL_ALLOW_GPU_ELEMENT_NAME = "AllowGPU"
JOB_CONTROL_LOG_FILE_PATHNAME_ELEMENT_NAME = "LogFilePathname"

# <Network>
NETWORK_ELEMENT_NAME = "Network"
NETWORK_TYPE_ELEMENT_NAME = "NetworkType"
NETWORK_STATE_SIZE_ELEMENT_NAME = "RecurrentStateSize"
NETWORK_OUTPUT_THRESHOLD_ELEMENT_NAME = "MapOutputToBoolThreshold"
NETWORK_SEQUENCE_ELEMENT_NAME = "InputSequence"
NETWORK_SEQUENCE_SIZE_ELEMENT_NAME = "InputSequenceSize"
NETWORK_SEQUENCE_MAX_DURATION_DAYS_ELEMENT_NAME = "MaxSequenceDurationInDays"

# <Input>
NETWORK_INPUT_ELEMENT_NAME = "Input"
NETWORK_INPUT_VALUES_ELEMENT_NAME = "InputValues"
NETWORK_INPUT_CRITERIA_TEST_ELEMENT_NAME = "UsefulInput"
# Input and Output test relationship names
g_NameToRelationIDDict = {
            "in": tdf.VALUE_RELATION_IN_RANGE_ID,
            "gt": tdf.VALUE_RELATION_GREATER_THAN_ID,
            "gte": tdf.VALUE_RELATION_GREATER_THAN_EQUAL_ID,
            "lt": tdf.VALUE_RELATION_LESS_THAN_ID,
            "lte": tdf.VALUE_RELATION_LESS_THAN_EQUAL_ID, 
            "eq": tdf.VALUE_RELATION_EQUAL_ID }
VALUE_RELATION_IN_RANGE = "in"
VALUE_RELATION_RANGE_SEPARATOR = ":"

# <Output>
NETWORK_OUTPUT_ELEMENT_NAME = "Output"
NETWORK_OUTPUT_SOURCE_ELEMENT_NAME = "Source"
NETWORK_OUTPUT_VALUE_ELEMENT_NAME = "Value"
NETWORK_OUTPUT_WHEN_ELEMENT_NAME = "When"
# Output Sources. A test result can either be a logistic (a float between 0.0 and 1.0) or else a 2-category enum.
NETWORK_OUTPUT_SOURCE_VALUE = "value"
NETWORK_OUTPUT_SOURCE_TEST_LOGISTIC = "testlogistic"
NETWORK_OUTPUT_SOURCE_TEST_CATEGORY = "testcategory"
NETWORK_OUTPUT_SOURCE_VALUE_ID = 1
NETWORK_OUTPUT_SOURCE_TEST_LOGISTIC_ID = 2
NETWORK_OUTPUT_SOURCE_TEST_CATEGORY_ID = 3
g_NameToSourceIDDict = {
            NETWORK_OUTPUT_SOURCE_VALUE: NETWORK_OUTPUT_SOURCE_VALUE_ID,
            NETWORK_OUTPUT_SOURCE_TEST_LOGISTIC: NETWORK_OUTPUT_SOURCE_TEST_LOGISTIC_ID,
            NETWORK_OUTPUT_SOURCE_TEST_CATEGORY: NETWORK_OUTPUT_SOURCE_TEST_CATEGORY_ID }
# Output When. This says when the output value is to be drawn from
g_NameToWhenIDDict = {
            "atday": tdf.VALUE_WHEN_AT_DAY_ID,
            "afterday": tdf.VALUE_WHEN_AFTER_DAY_ID,
            "atseqenceend": tdf.VALUE_WHEN_AT_SEQUENCE_END_ID,
            "aftersequenceend": tdf.VALUE_WHEN_AFTER_SEQUENCE_END_ID,
            "ever": tdf.VALUE_WHEN_EVER_ID }

# <Data>
DATA_ELEMENT_NAME = "Data"
DATA_TIME_GRANULARITY_ELEMENT_NAME = "TimeGranularity"

# <Training>
TRAINING_ELEMENT_NAME = "Training"
TRAINING_OPTION_BATCHSIZE = "BatchSize"
TRAINING_OPTION_LEARNING_RATE = "LearningRate"
TRAINING_OPTION_NUM_EPOCHS = "NumEpochs"
TRAINING_OPTION_RESULT_PRIORITY_POLICY_ELEMENT_NAME = "PriorityPolicy"
TRAINING_OPTION_LOSS_FUNCTION_ELEMENT_NAME = "LossFunction"
TRAINING_MAX_NUM_SKIPPED_RESULT_CLASSES = "MaxSkippedResultClasses"
TRAINING_MAX_SKIPPED_DAYS_IN_SAME_SEQUENCE = "MaxSkippedDaysInSameSequence"

# <Training><ValueInfo>
TRAINING_PRIORITY_VALUE_INFO = "ValueInfo"
TRAINING_PRIORITY_VALUE_NAME = "ValueName"
TRAINING_PRIORITY_SRC_FILE = "SrcFile"
TRAINING_PRIORITY_CREATION_DATE = "DateCollected"
TRAINING_PRIORITY_MIN_VALUE = "MinValue"
TRAINING_PRIORITY_MAX_VALUE = "MaxValue"
TRAINING_PRIORITY_MEAN_VALUE = "MeanValue"
TRAINING_PRIORITY_NUM_CLASSES = "NumPriorities"
TRAINING_PRIORITY_CLASS_PRIORITIES = "ClassPriorities"

# <Runtime>
RUNTIME_ELEMENT_NAME = "Runtime"
RUNTIME_LOG_NODE_ELEMENT_NAME = "Log"
RUNTIME_HASH_DICT_ELEMENT_NAME = "HashDict"
RUNTIME_FILE_PATHNAME_ELEMENT_NAME = "JobFilePathname"
RUNTIME_START_ELEMENT_NAME = "StartRequestTimeStr"
RUNTIME_STOP_ELEMENT_NAME = "StopRequestTimeStr"
RUNTIME_CURRENT_EPOCH_ELEMENT_NAME = "CurrentEpochNum"
RUNTIME_NONCE_ELEMENT_NAME = "Nonce"
RUNTIME_OS_ELEMENT_NAME = "OS"
RUNTIME_CPU_ELEMENT_NAME = "CPU"
RUNTIME_GPU_ELEMENT_NAME = "GPU"
RUNTIME_TOTAL_TRAINING_LOSS_CURRENT_EPOCH_ELEMENT_NAME = "TotalTrainingLossInCurrentEpoch"
RUNTIME_NUM_TRAINING_LOSS_VALUES_CURRENT_EPOCH_ELEMENT_NAME = "NumTrainLossValuesCurrentEpoch"

# <Results>
RESULTS_ELEMENT_NAME = "Results"
RESULTS_PREFLIGHT_ELEMENT_NAME = "PreflightResults"
RESULTS_TRAINING_ELEMENT_NAME = "TrainingResults"
RESULTS_TESTING_ELEMENT_NAME = "TestingResults"

# <Results><PreflightResults>
RESULTS_PREFLIGHT_NUM_ITEMS_ELEMENT_NAME = "NumSequences"
RESULTS_PREFLIGHT_NUM_ITEMS_PER_CLASS_ELEMENT_NAME = "NumItemsPerClass"
RESULTS_PREFLIGHT_INPUT_MINS_ELEMENT_NAME = "InputMins"
RESULTS_PREFLIGHT_INPUT_MAXS_ELEMENT_NAME = "InputMaxs"
RESULTS_PREFLIGHT_INPUT_RANGES_ELEMENT_NAME = "InputRanges"
RESULTS_PREFLIGHT_OUTPUT_MIN_ELEMENT_NAME = "ResultMin"
RESULTS_PREFLIGHT_OUTPUT_MAX_ELEMENT_NAME = "ResultMax"
RESULTS_PREFLIGHT_OUTPUT_MEAN_ELEMENT_NAME = "ResultMean"
RESULTS_PREFLIGHT_OUTPUT_STDDEV_ELEMENT_NAME = "ResultStdDev"
RESULTS_PREFLIGHT_OUTPUT_TOTAL_ELEMENT_NAME = "ResultTotalSum"
RESULTS_PREFLIGHT_OUTPUT_COUNT_ELEMENT_NAME = "ResultCount"
RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_WEIGHT_LIST = "ResultClassWeightList"
RESULTS_PREFLIGHT_TRAINING_PRIORITY_NUM_RESULT_CLASSES = "NumResultClasses"
RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_WEIGHT = "ResultClassWeight"
RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_ID = "ResultClassID"
RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_WEIGHT_VALUE = "ClassWeight"
RESULTS_PREFLIGHT_NUM_MISSING_VALUES_LIST_ELEMENT_NAME = "NumMissingValuesList"
RESULTS_PREFLIGHT_ESTIMATED_MIN_VALUE_ELEMENT_NAME = "EstimatedMinValue"
RESULTS_PREFLIGHT_NUM_RESULT_PRIORITIES_ELEMENT_NAME = "NumResultBuckets"
RESULTS_PREFLIGHT_RESULT_BUCKET_SIZE_ELEMENT_NAME = "ResultBucketSize"
RESULTS_PREFLIGHT_RESULT_NUM_ITEMS_PER_BUCKET_ELEMENT_NAME = "NumResultsForEachBucket"

# <Results><TestingResults>
RESULTS_TEST_ALL_TESTS_GROUP_XML_ELEMENT_NAME = "AllTests"
RESULTS_TEST_TEST_SUBGROUP_XML_ELEMENT_NAME = "TestSubGroup"
RESULTS_TEST_NUM_GROUPS_ELEMENT_NAME = "NumSubgroups"
RESULTS_TEST_GROUP_MEANING_XML_ELEMENT_NAME = "SubgroupMeaning"
DEFAULT_TEST_GROUP_MEANING = "SeqLength"
DEFAULT_NUM_TEST_SUBGROUPS = 10
RESULTS_TEST_NUM_ITEMS_ELEMENT_NAME = "NumSequences"
RESULTS_TEST_NUM_ITEMS_PER_CLASS_ELEMENT_NAME = "NumItemsPerClass"
RESULTS_TEST_NUM_PREDICTIONS_PER_CLASS_ELEMENT_NAME = "NumPredictionsPerClass"
RESULTS_TEST_NUM_CORRECT_PER_CLASS_ELEMENT_NAME  = "NumCorrectPerClass"
RESULTS_TEST_NUM_CORRECT_PER_CLASS_ELEMENT_NAME  = "NumCorrectPerClass"
RESULTS_TEST_ROCAUC_ELEMENT_NAME = "ROCAUC"
RESULTS_TEST_AUPRC_ELEMENT_NAME = "AUPRC"
RESULTS_TEST_F1Score_ELEMENT_NAME = "F1Score"
RESULTS_TEST_NUM_LOGISTIC_OUTPUTS_ELEMENT_NAME = "LogisticOutputs"
RESULTS_TEST_TOTAL_ABS_ERROR_ELEMENT_NAME = "TotalAbsError"
RESULTS_TEST_TOTAL_NUM_PREDICTIONS_ELEMENT_NAME = "TotalNumPredictions"
RESULTS_TEST_ALL_PREDICTIONS_ELEMENT_NAME = "PredictionValueList"
RESULTS_TEST_ALL_TRUE_RESULTS_ELEMENT_NAME = "TrueResultValueList"

# <Results><TrainingResults>
RESULTS_TRAIN_SEQUENCES_TRAINED_PER_EPOCH_ELEMENT_NAME = "NumSequencesTrainedPerEpoch"
RESULTS_TRAIN_TIMELINES_TRAINED_PER_EPOCH_ELEMENT_NAME = "NumTimelinesTrainedPerEpoch"
RESULTS_TRAIN_TIMELINES_SKIPPED_PER_EPOCH_ELEMENT_NAME = "NumTimelinesSkippedPerEpoch"
RESULTS_TRAIN_DATA_POINTS_TRAINED_PER_EPOCH_ELEMENT_NAME = "NumDataPointsTrainedPerEpoch"
RESULTS_TRAIN_AVG_LOSS_PER_EPOCH_ELEMENT_NAME = "TrainAvgLossPerEpoch"
RESULTS_TRAIN_NUM_ITEMS_PER_CLASS_ELEMENT_NAME = "TrainNumItemsPerClass"

# <SavedModelState>
SAVED_MODEL_STATE_ELEMENT_NAME      = "SavedModelState"
RUNTIME_OPTIMIZER_STATE             = "PyTorchOptimizerState"

# <NeuralNetMatrixList>
NETWORK_MATRIX_LIST_NAME = "NeuralNetMatrixList"
NETWORK_MATRIX_WEIGHT_MATRIX_NAME = "Weight"
NETWORK_MATRIX_BIAS_VECTOR_NAME = "Bias"

VALUE_FILTER_LIST_SEPARATOR = ".AND."

MLJOB_MATRIX_FORMAT_ATTRIBUTE_NAME = "format"
MLJOB_MATRIX_FORMAT_SIMPLE = "simple"

# These are the values found in the <JobControl/Status> element
MLJOB_STATUS_IDLE         = "IDLE"
MLJOB_STATUS_PREFLIGHT    = "PREFLIGHT"
MLJOB_STATUS_TRAINING     = "TRAIN"
MLJOB_STATUS_TESTING      = "TEST"
MLJOB_STATUS_DONE         = "DONE"

# These are specific to Job files. They must be translated into other error codes
# in higher level modules. That's not pretty, but it makes Job a standalone module.
# It also is essentially the same as translating an exception from a low level module
# into another exception from a higher level module
JOB_E_NO_ERROR              = 0
JOB_E_UNKNOWN_ERROR         = 1
JOB_E_UNHANDLED_EXCEPTION   = 2
JOB_E_CANNOT_OPEN_FILE      = 100
JOB_E_INVALID_FILE          = 110

# These are used to read and write vectors and matrices to strings.
VALUE_SEPARATOR_CHAR        = ","
ROW_SEPARATOR_CHAR          = "/"

MLJOB_NAMEVAL_SEPARATOR_CHAR    = ";"
MLJOB_ITEM_SEPARATOR_CHAR   = ","

DEBUG_EVENT_TIMELINE_EPOCH          = "Epoch"
DEBUG_EVENT_TIMELINE_CHUNK          = "Chunk"
DEBUG_EVENT_TIMELINE_LOSS           = "Loss"
DEBUG_EVENT_OUTPUT_AVG              = "Out.avg"
DEBUG_EVENT_NONLINEAR_OUTPUT_AVG    = "NLOut.avg"

CALCULATE_TRAINING_WEIGHTS_DURING_PREFLIGHT = False





################################################################################
#
# class MLJobTestResults
#
# This class records all results for tests in a single group, where a group
# may be one set of assumptions or one type of result or something else.
# It lets us track the results of different preconditions, like subgroup analysis.
#
# Note that this is for testing only, not training.
################################################################################
class MLJobTestResults():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self):
        self.ResultXMLNode = None

        # These are inherited from the parent, not stored with each results bucket
        self.ResultValueType = tdf.TDF_DATA_TYPE_UNKNOWN
        self.ResultMinValue = 0
        self.ResultMaxValue = 0
        self.NumResultClasses = 0
        self.BucketSize = 0
        self.IsLogisticNetwork = False
        self.OutputThreshold = 0

        self.NumSamplesTested = 0
        self.TestResults = {}

        self.AllPredictions = []
        self.AllTrueResults = []
        self.TotalAbsoluteError = 0
        self.NumPredictions = 0

        self.TestNumItemsPerClass = []
        self.TestNumPredictionsPerClass = []
        self.TestNumCorrectPerClass = []

        self.LogisticResultsTrueValueList = []
        self.LogisticResultsPredictedProbabilityList = []
        self.ROCAUC = -1
        self.AUPRC = -1
        self.F1Score = -1
    # End -  __init__


    #####################################################
    #
    # [MLJobResults::InitResultsXML]
    #
    #####################################################
    def InitResultsXML(self, testResultXMLNode, xmlNodeName):
        self.ResultXMLNode = dxml.XMLTools_GetOrCreateChildNode(testResultXMLNode, 
                                                                xmlNodeName)
    # End of InitResultsXML



    #####################################################
    #
    # [MLJobResults::SetGlobalResultInfo]
    #
    # This is done at the start of testing, and records properties 
    # of the output value
    #####################################################
    def SetGlobalResultInfo(self, resultValueType, numResultClasses, resultMinValue, resultMaxValue, bucketSize, isLogisticNetwork, outputThreshold):
        self.ResultValueType = resultValueType
        self.NumResultClasses = numResultClasses

        self.ResultMinValue = resultMinValue
        self.ResultMaxValue = resultMaxValue
        self.BucketSize = bucketSize

        self.IsLogisticNetwork = isLogisticNetwork
        self.OutputThreshold = outputThreshold
    # End of SetGlobalResultInfo



    #####################################################
    #
    # [MLJobTestResults::StartTesting
    # 
    #####################################################
    def StartTesting(self):
        self.NumSamplesTested = 0
        self.TestResults = {"NumCorrectPredictions": 0}
        if (self.ResultValueType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
            self.TestResults["NumPredictionsWithin2Percent"] = 0
            self.TestResults["NumPredictionsWithin5Percent"] = 0
            self.TestResults["NumPredictionsWithin10Percent"] = 0
            self.TestResults["NumPredictionsWithin20Percent"] = 0
            self.TestResults["NumPredictionsWithin50Percent"] = 0
            self.TestResults["NumPredictionsWithin100Percent"] = 0
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_BOOL):
            self.TestResults["NumPredictionsTruePositive"] = 0
            self.TestResults["NumPredictionsTrueNegative"] = 0
            self.TestResults["NumPredictionsFalsePositive"] = 0
            self.TestResults["NumPredictionsFalseNegative"] = 0

        self.TestNumItemsPerClass = [0] * self.NumResultClasses
        self.TestNumPredictionsPerClass = [0] * self.NumResultClasses
        self.TestNumCorrectPerClass = [0] * self.NumResultClasses
    # End - StartTesting




    #####################################################
    #
    # [MLJobTestResults::RecordTestingResult
    # 
    #####################################################
    def RecordTestingResult(self, actualValue, predictedValue):
        self.NumSamplesTested += 1

        #########################
        if (self.ResultValueType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
            difference = abs(float(actualValue - predictedValue))

            # Record the guess itself
            self.AllPredictions.append(round(predictedValue, 2))
            self.AllTrueResults.append(round(actualValue, 2))
            self.TotalAbsoluteError += difference
            self.NumPredictions += 1

            # Record how accurate our guess is
            if (difference == 0):
                self.TestResults["NumCorrectPredictions"] += 1
            if (difference <= (actualValue * 0.02)):
                self.TestResults["NumPredictionsWithin2Percent"] += 1
            elif (difference <= (actualValue * 0.05)):
                self.TestResults["NumPredictionsWithin5Percent"] += 1
            elif (difference <= (actualValue * 0.1)):
                self.TestResults["NumPredictionsWithin10Percent"] += 1
            elif (difference <= (actualValue * 0.2)):
                self.TestResults["NumPredictionsWithin20Percent"] += 1
            elif (difference <= (actualValue * 0.5)):
                self.TestResults["NumPredictionsWithin50Percent"] += 1
            elif (difference <= (actualValue * 1.0)):
                self.TestResults["NumPredictionsWithin100Percent"] += 1

            # Record the actual value. This makes a histogram which shows the
            # distribution of actual values
            offset = max(actualValue - self.ResultMinValue, 0)
            actualBucketNum = int(offset / self.BucketSize)
            actualBucketNum = min(actualBucketNum, (ML_JOB_NUM_NUMERIC_VALUE_BUCKETS - 1))
            if (actualBucketNum >= len(self.TestNumItemsPerClass)):
                print("\n\nERROR!. bug")
                print("     actualBucketNum = " + str(actualBucketNum))
                print("     self.TestNumItemsPerClass = " + str(self.TestNumItemsPerClass))
                print("     len(self.TestNumItemsPerClass) = " + str(len(self.TestNumItemsPerClass)))
                print("     self.NumResultClasses = " + str(self.NumResultClasses))
                print("     self.ResultValueType = " + str(self.ResultValueType))
                print("     self.BucketSize = " + str(self.BucketSize))
                print("     self.ResultMinValue = " + str(self.ResultMinValue))
                raise Exception()

            self.TestNumItemsPerClass[actualBucketNum] += 1

            # Record the prediction value. This makes a histogram which shows the
            # distribution of predictions
            # Check for extremes, since the prediction may be very huge or very small.
            if (predictedValue >= self.ResultMaxValue):
                predictedBucketNum = ML_JOB_NUM_NUMERIC_VALUE_BUCKETS - 1
            elif (predictedValue < self.ResultMinValue):
                predictedBucketNum = 0
            else:
                try:
                    offset = max(predictedValue - self.ResultMinValue, 0)
                    predictedBucketNum = int(offset / self.BucketSize)
                    if (predictedBucketNum >= ML_JOB_NUM_NUMERIC_VALUE_BUCKETS):
                        predictedBucketNum = ML_JOB_NUM_NUMERIC_VALUE_BUCKETS - 1
                except Exception:
                    predictedBucketNum = 0
            # End - else
            self.TestNumPredictionsPerClass[predictedBucketNum] += 1
            if (predictedBucketNum == actualBucketNum):
                self.TestNumCorrectPerClass[actualBucketNum] += 1
        # End - if (self.ResultValueType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT))

        #########################
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_BOOL):
            # If this is a Logistic, then convert the resulting probability into a 0 or 1
            if ((self.IsLogisticNetwork) and (self.OutputThreshold > 0)):
                predictedFloat = float(predictedValue)
                self.LogisticResultsTrueValueList.append(actualValue)
                self.LogisticResultsPredictedProbabilityList.append(predictedFloat)

                # Now, convert the probability to a normal boolean result like 
                # we would have for any bool.
                if (predictedFloat >= self.OutputThreshold):
                    predictedValue = 1
                else:
                    predictedValue = 0
            # End - if ((self.IsLogisticNetwork) and (self.OutputThreshold > 0)):

            actualValueInt = int(actualValue)
            predictedValueInt = int(predictedValue)

            self.TestNumItemsPerClass[actualValueInt] += 1
            self.TestNumPredictionsPerClass[predictedValueInt] += 1
            if (actualValueInt == predictedValueInt):
                self.TestResults["NumCorrectPredictions"] += 1
                if (predictedValueInt > 0):
                    self.TestResults["NumPredictionsTruePositive"] += 1
                else:
                    self.TestResults["NumPredictionsTrueNegative"] += 1
                self.TestNumCorrectPerClass[int(actualValueInt)] += 1
            else:  # if (actualValueInt != predictedValueInt):
                if (predictedValueInt > 0):
                    self.TestResults["NumPredictionsFalsePositive"] += 1
                else:
                    self.TestResults["NumPredictionsFalseNegative"] += 1
        # End - elif (self.ResultValueType == tdf.TDF_DATA_TYPE_BOOL):
    # End -  RecordTestingResult




    #####################################################
    #
    # [MLJobTestResults::StopTesting]
    #
    #####################################################
    def StopTesting(self):
        # Normally this is done when we finish testing.
        if (self.IsLogisticNetwork):
            # Get the Receiver Operator Curve AUC
            self.ROCAUC = roc_auc_score(self.LogisticResultsTrueValueList, 
                                        self.LogisticResultsPredictedProbabilityList)

            # Get the Precision-Recall curve and AUPRC
            PrecisionResults, RecallResults, _ = precision_recall_curve(self.LogisticResultsTrueValueList, 
                                            self.LogisticResultsPredictedProbabilityList)
            self.AUPRC = auc(RecallResults, PrecisionResults)

            # Get the F1 score
            numSamples = len(self.LogisticResultsPredictedProbabilityList)
            predictedValueList = [0] * numSamples
            for index in range(numSamples):
                currentProbability = self.LogisticResultsPredictedProbabilityList[index]
                if (currentProbability >= self.OutputThreshold):
                    predictedValueList[index] = 1
            self.F1Score = f1_score(self.LogisticResultsTrueValueList, predictedValueList)
        # End - if (self.IsLogisticNetwork):
    # End of StopTesting



    #####################################################
    #
    # [MLJobTestResults::ReadTestResultsFromXML
    #
    #####################################################
    def ReadTestResultsFromXML(self):
        # Every simple value (like <aa>5</aa>) is a named value in the result dict.
        self.TestResults = {}
        currentXMLNode = dxml.XMLTools_GetFirstChildNode(self.ResultXMLNode)
        while (currentXMLNode is not None):
            if (dxml.XMLTools_IsLeafNode(currentXMLNode)):
                nameStr = dxml.XMLTools_GetElementName(currentXMLNode)
                valueStr = dxml.XMLTools_GetTextContents(currentXMLNode)
                try:
                    self.TestResults[nameStr] = int(valueStr)
                except Exception:
                    self.TestResults[nameStr] = valueStr
            # End - if (dxml.XMLTools_IsLeafNode(currentXMLNode)):

            currentXMLNode = dxml.XMLTools_GetAnyPeerNode(currentXMLNode)
        # End - while (currentXMLNode is not None):


        self.NumSamplesTested = dxml.XMLTools_GetChildNodeTextAsInt(self.ResultXMLNode, 
                                                    RESULTS_TEST_NUM_ITEMS_ELEMENT_NAME, 0)
        self.ROCAUC = dxml.XMLTools_GetChildNodeTextAsFloat(self.ResultXMLNode, 
                                                    RESULTS_TEST_ROCAUC_ELEMENT_NAME, 0.0)
        self.AUPRC = dxml.XMLTools_GetChildNodeTextAsInt(self.ResultXMLNode, 
                                                    RESULTS_TEST_AUPRC_ELEMENT_NAME, 0)
        self.F1Score = dxml.XMLTools_GetChildNodeTextAsInt(self.ResultXMLNode, 
                                                    RESULTS_TEST_F1Score_ELEMENT_NAME, 0)


        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.ResultXMLNode, 
                                                    RESULTS_TEST_NUM_ITEMS_PER_CLASS_ELEMENT_NAME, "")
        self.TestNumItemsPerClass = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.ResultXMLNode, 
                                                    RESULTS_TEST_NUM_PREDICTIONS_PER_CLASS_ELEMENT_NAME, "")
        self.TestNumPredictionsPerClass = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.ResultXMLNode, 
                                                    RESULTS_TEST_NUM_CORRECT_PER_CLASS_ELEMENT_NAME, "")
        self.TestNumCorrectPerClass = MLJob_ConvertStringTo1DVector(resultStr)



        self.TotalAbsoluteError = dxml.XMLTools_GetChildNodeTextAsFloat(self.ResultXMLNode, 
                                                    RESULTS_TEST_TOTAL_ABS_ERROR_ELEMENT_NAME, 0.0)
        self.NumPredictions = dxml.XMLTools_GetChildNodeTextAsInt(self.ResultXMLNode, 
                                                    RESULTS_TEST_TOTAL_NUM_PREDICTIONS_ELEMENT_NAME, 0)
        self.AllPredictions = []
        self.AllTrueResults = []

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.ResultXMLNode, RESULTS_TEST_ALL_PREDICTIONS_ELEMENT_NAME, "")
        if ((resultStr is not None) and (resultStr != "")):
            resultArray = resultStr.split(MLJOB_ITEM_SEPARATOR_CHAR)
            for valueStr in resultArray:
                try:
                    self.AllPredictions.append(float(valueStr))
                except Exception:
                    print("ReadTestResultsFromXML. EXCEPTION (RESULTS_TEST_ALL_PREDICTIONS_ELEMENT_NAME). Cannot convert valueStr: " + str(valueStr) + ", resultArray=" + str(resultArray))
                    continue
            # End - for valueStr in resultArray:
        # End - if ((resultStr not None) and (resultStr != "")):


        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.ResultXMLNode, RESULTS_TEST_ALL_TRUE_RESULTS_ELEMENT_NAME, "")
        if ((resultStr is not None) and (resultStr != "")):
            resultArray = resultStr.split(MLJOB_ITEM_SEPARATOR_CHAR)
            for valueStr in resultArray:
                try:
                    self.AllTrueResults.append(float(valueStr))
                except Exception:
                    print("ReadTestResultsFromXML. EXCEPTION (RESULTS_TEST_ALL_TRUE_RESULTS_ELEMENT_NAME). Cannot convert valueStr: " + str(valueStr) + ", resultArray=" + str(resultArray))
                    continue
            # End - for valueStr in resultArray:
        # End - if ((resultStr not None) and (resultStr != "")):

        if (len(self.AllPredictions) != len(self.AllTrueResults)):
            print("ReadTestResultsFromXML. RESULTS_TEST_ALL_TRUE_RESULTS_ELEMENT_NAME gives a different number of results")
            self.AllPredictions = []
            self.AllTrueResults = []


        self.LogisticResultsTrueValueList = []
        self.LogisticResultsPredictedProbabilityList = []
        if (self.IsLogisticNetwork):
            resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.ResultXMLNode, RESULTS_TEST_NUM_LOGISTIC_OUTPUTS_ELEMENT_NAME, "")
            if ((resultStr is not None) and (resultStr != "")):
                resultArray = resultStr.split(MLJOB_NAMEVAL_SEPARATOR_CHAR)
                for truthProbabilityPair in resultArray:
                    valuePair = truthProbabilityPair.split("=")
                    if (len(valuePair) == 2):
                        try:
                            trueValue = round(float(valuePair[0]))
                            probability = float(valuePair[1])
                        except Exception:
                            print("ReadTestResultsFromXML. EXCEPTION in reading Logistic results")
                            continue

                        #if (probability > 0): 
                        #print("Read Logistic Input. probability=" + str(probability) + ", trueValue=" + str(trueValue))

                        self.LogisticResultsTrueValueList.append(trueValue)
                        self.LogisticResultsPredictedProbabilityList.append(probability)
                # End - for truthProbabilityPair in resultArray:
            # End - if ((resultStr not None) and (resultStr != "")):

            self.ROCAUC = -1
            if ((len(self.LogisticResultsTrueValueList) > 0) and (len(self.LogisticResultsPredictedProbabilityList) > 0)):
                self.ROCAUC = roc_auc_score(self.LogisticResultsTrueValueList, 
                                            self.LogisticResultsPredictedProbabilityList)
        # End - if (self.IsLogisticNetwork):
    # End - ReadTestResultsFromXML





    #####################################################
    #
    # [MLJobTestResults::WriteTestResultsToXML
    #
    #####################################################
    def WriteTestResultsToXML(self):
        for index, (valName, value) in enumerate(self.TestResults.items()):
            dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, valName, str(value))

        dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_TEST_NUM_ITEMS_ELEMENT_NAME, 
                                                        str(self.NumSamplesTested))
        dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_TEST_ROCAUC_ELEMENT_NAME, str(self.ROCAUC))
        dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_TEST_AUPRC_ELEMENT_NAME, str(self.AUPRC))
        dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_TEST_F1Score_ELEMENT_NAME, str(self.F1Score))

        resultStr = MLJob_Convert1DVectorToString(self.TestNumItemsPerClass)
        dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_TEST_NUM_ITEMS_PER_CLASS_ELEMENT_NAME, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.TestNumPredictionsPerClass)
        dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_TEST_NUM_PREDICTIONS_PER_CLASS_ELEMENT_NAME, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.TestNumCorrectPerClass)
        dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_TEST_NUM_CORRECT_PER_CLASS_ELEMENT_NAME, resultStr)

        dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_TEST_TOTAL_ABS_ERROR_ELEMENT_NAME, str(self.TotalAbsoluteError))
        dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_TEST_TOTAL_NUM_PREDICTIONS_ELEMENT_NAME, str(self.NumPredictions))
        resultStr = ""
        for valueFloat in self.AllPredictions:
            if (resultStr != ""):
                resultStr += MLJOB_ITEM_SEPARATOR_CHAR
            resultStr += str(valueFloat)
        # End - for valueFloat in self.AllPredictions:
        dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_TEST_ALL_PREDICTIONS_ELEMENT_NAME, resultStr)

        resultStr = ""
        for valueFloat in self.AllTrueResults:
            if (resultStr != ""):
                resultStr += MLJOB_ITEM_SEPARATOR_CHAR
            resultStr += str(valueFloat)
        # End - for valueFloat in self.AllTrueResults:
        dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_TEST_ALL_TRUE_RESULTS_ELEMENT_NAME, resultStr)


        # This saves the values for Logistic function outputs
        # These are used to compute AUROC and AUPRC
        if (self.IsLogisticNetwork):
            logisticOutputsStr = ""
            listLength = len(self.LogisticResultsTrueValueList)
            for index in range(listLength):
                trueValue = self.LogisticResultsTrueValueList[index]
                probability = self.LogisticResultsPredictedProbabilityList[index]
                logisticOutputsStr = logisticOutputsStr + str(trueValue) + "=" + str(probability) + MLJOB_NAMEVAL_SEPARATOR_CHAR
            if (logisticOutputsStr != ""):
                logisticOutputsStr = logisticOutputsStr[:-1]
                dxml.XMLTools_AddChildNodeWithText(self.ResultXMLNode, RESULTS_TEST_NUM_LOGISTIC_OUTPUTS_ELEMENT_NAME, logisticOutputsStr)
        # End - if (self.IsLogisticNetwork):
    # End - WriteTestResultsToXML


# End - class MLJobTestResults
################################################################################






################################################################################
################################################################################
class MLJob():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self):
        self.JobFilePathName = ""
        self.FormatVersion = DEFAULT_JOB_FORMAT_VERSION
        self.fileUUID = ""

        # These are the sections of the JOB spec
        self.JobXMLDOM = None
        self.RootXMLNode = None
        self.UUIDXMLNode = None
        self.JobControlXMLNode = None
        self.DataXMLNode = None

        self.NetworkXMLNode = None
        self.NetworkOutputXMLNode = None
        self.NetworkInputXMLNode = None

        self.TrainingXMLNode = None
        self.RuntimeXMLNode = None
        self.ResultsXMLNode = None
        self.ResultsPreflightXMLNode = None
        self.ResultsTrainingXMLNode = None
        self.ResultsTestingXMLNode = None

        # Describe the network
        self.NetworkType = ""
        self.AllowGPU = False
        self.OutputThreshold = -1
        self.IsLogisticNetwork = False
        self.NumResultClasses = 0
        self.numInputVars = -1
        self.ResultValueType = tdf.TDF_DATA_TYPE_UNKNOWN

        # Runtime state
        self.Debug = False
        self.StartRequestTimeStr = ""
        self.StopRequestTimeStr = ""

        # Training State
        self.CurrentEpochNum = 0
        self.TrainingPriorities = [-1] * 1
        self.NumSamplesTrainedPerEpoch = 0
        self.NumTimelinesTrainedPerEpoch = 0
        self.NumTimelinesSkippedPerEpoch = 0
        self.NumDataPointsTrainedPerEpoch = 0
        self.TrainNumItemsPerClass = []
        self.TotalTrainingLossInCurrentEpoch = 0.0
        self.NumTrainLossValuesCurrentEpoch = 0
        self.AvgLossPerEpochList = []
        self.TrainingResultMinValue = -1
        self.TrainingResultMaxValue = -1
        self.TrainingNumResultPriorities = 0
        self.TrainingResultBucketSize = 1
        self.TrainingResultClassPriorities = []
        self.TotalTrainingLossInCurrentEpoch = 0.0
        self.NumTrainLossValuesCurrentEpoch = 0

        # Preflight state
        self.PreflightResultClassWeights = []
        self.NumResultsInPreflight = 0
        self.PreflightNumItemsPerClass = []
        self.PreflightInputMins = []
        self.PreflightInputMaxs = []
        self.PreflightInputRanges = []
        self.ResultValMinValue = 0
        self.ResultValMaxValue = 0
        self.ResultValBucketSize = 0
        self.PreflightResultMin = 0
        self.PreflightResultMax = 0
        self.PreflightResultMean = 0
        self.PreflightResultStdDev = 0
        self.PreflightResultTotal = 0
        self.PreflightResultCount = 0
        self.PreflightEstimatedMinResultValueForPriority = 0
        self.PreflightNumResultPriorities = 20
        self.PreflightResultBucketSize = 0
        self.PreflightNumResultsInEachBucket = []
        self.PreflightResultClassPriorities = []

        # Test State
        self.AllTestResults = MLJobTestResults()
        self.NumResultsSubgroups = DEFAULT_NUM_TEST_SUBGROUPS
        self.SubgroupMeaning = DEFAULT_TEST_GROUP_MEANING
        self.TestResultsSubgroupList = []
        for index in range(self.NumResultsSubgroups):
            self.TestResultsSubgroupList.append(MLJobTestResults())

        # Debugging State
        self.LogFilePathname = ""
        self.BufferedLogLines = ""
        self.HashDict = {}
        self.RuntimeNonce = 0
        self.SavedModelStateXMLNode = None
        self.NeuralNetMatrixListXMLNode = None
    # End -  __init__




    #####################################################
    #
    # [MLJob::InitNewJobImpl]
    #
    #####################################################
    def InitNewJobImpl(self):
        impl = getDOMImplementation()

        # This creates the document and the root node.
        self.JobXMLDOM = impl.createDocument(None, ROOT_ELEMENT_NAME, None)
        self.RootXMLNode = dxml.XMLTools_GetNamedElementInDocument(self.JobXMLDOM, ROOT_ELEMENT_NAME)
        self.FormatVersion = DEFAULT_JOB_FORMAT_VERSION
        dxml.XMLTools_SetAttribute(self.RootXMLNode, FORMAT_VERSION_ATTRIBUTE, str(self.FormatVersion))
        self.UUIDXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, JOB_UUID_ELEMENT_NAME)
        dxml.XMLTools_RemoveAllChildNodes(self.UUIDXMLNode)
        self.fileUUID = str(UUID.uuid4())
        textNode = self.JobXMLDOM.createTextNode(self.fileUUID)
        self.UUIDXMLNode.appendChild(textNode)

        # JobControl and its children
        self.JobControlXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, JOB_CONTROL_ELEMENT_NAME)
        self.SetJobControlStr(JOB_CONTROL_STATUS_ELEMENT_NAME, MLJOB_STATUS_IDLE)
        self.SetJobControlStr(JOB_CONTROL_RESULT_MSG_ELEMENT_NAME, "")
        self.SetJobControlStr(JOB_CONTROL_ERROR_CODE_ELEMENT_NAME, str(JOB_E_NO_ERROR))
        self.SetJobControlStr(JOB_CONTROL_RUN_OPTIONS_ELEMENT_NAME, "")

        # The Data Node
        self.DataXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, DATA_ELEMENT_NAME)

        # The Network Node and its children
        self.NetworkXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, NETWORK_ELEMENT_NAME)
        self.NetworkInputXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, NETWORK_INPUT_ELEMENT_NAME)
        self.NetworkOutputXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, NETWORK_OUTPUT_ELEMENT_NAME)

        self.TrainingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, TRAINING_ELEMENT_NAME)
        self.RuntimeXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, RUNTIME_ELEMENT_NAME)
        self.ResultsXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, RESULTS_ELEMENT_NAME)
        self.ResultsPreflightXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, 
                                                        RESULTS_PREFLIGHT_ELEMENT_NAME)
        self.ResultsTrainingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, 
                                                        RESULTS_TRAINING_ELEMENT_NAME)
        self.ResultsTestingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, 
                                                        RESULTS_TESTING_ELEMENT_NAME)
        self.AllTestResults.InitResultsXML(self.ResultsTestingXMLNode, 
                                                        RESULTS_TEST_ALL_TESTS_GROUP_XML_ELEMENT_NAME)
        for index in range(self.NumResultsSubgroups):
            testGroupName = RESULTS_TEST_TEST_SUBGROUP_XML_ELEMENT_NAME + str(index)
            self.TestResultsSubgroupList[index].InitResultsXML(self.ResultsTestingXMLNode, testGroupName)

        # The saved state
        self.SavedModelStateXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, 
                                                        SAVED_MODEL_STATE_ELEMENT_NAME)
        self.NeuralNetMatrixListXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.SavedModelStateXMLNode, 
                                                        NETWORK_MATRIX_LIST_NAME)

        self.HashDict = {}
        self.RuntimeNonce = 0

        self.InitResultInfo()
    # End of InitNewJobImpl





    #####################################################
    #
    # [MLJob::ReadJobFromFile]
    #
    # Returns: Error code
    #
    # We have to be able to read/write jobs as strings, to pass them
    # between processes. As a result, this just reads an entire file 
    # as a string and then calls the parsing procedures for strings.
    # Job files are pretty small (a few hundred K at most) so this it
    # should always fit into memory.
    #####################################################
    def ReadJobFromFile(self, jobFilePathName):
        fUseASCII = True
        err = JOB_E_NO_ERROR

        if (fUseASCII):
            try:
                fileH = open(jobFilePathName, "r")
                contentsText = fileH.read()
                fileH.close()
            except Exception:
                return JOB_E_CANNOT_OPEN_FILE
        else:
            try:
                fileH = io.open(jobFilePathName, mode="r", encoding="utf-8")
                contentsText = fileH.read()
                fileH.close()
            except Exception:
                return JOB_E_CANNOT_OPEN_FILE
        # End - if (fUseASCII):

        err = self.ReadJobFromString(contentsText)

        # Update the file name. If we renamed a file when it was closed,
        # we need to save this new file name.
        self.JobFilePathName = jobFilePathName

        return err
    # End of ReadJobFromFile





    #####################################################
    #
    # [MLJob::SaveAs]
    #
    # Insert the runtime node and results node
    #####################################################
    def SaveAs(self, jobFilePathName):
        # Update the file name. If we renamed a file when it was closed,
        # we need to save this new file name.
        self.JobFilePathName = jobFilePathName

        contentsText = self.WriteJobToString()

        fileH = open(jobFilePathName, "w")
        fileH.write(contentsText)
        fileH.close()
    # End of SaveAs



    #####################################################
    #
    # [MLJob::SaveJobWithoutRuntime]
    #
    #####################################################
    def SaveJobWithoutRuntime(self, jobFilePathName):
        # Update the file name. If we renamed a file when it was closed,
        # we need to save this new file name.
        self.JobFilePathName = jobFilePathName

        # Do not call self.WriteJobToString();
        # That will insert the runtime node and results node, which
        # can be confusing for an input job.

        # Remove any previous formatting text so we can format
        # Otherwise, indentation or newlines accumulate each time
        # the XML is serialized/deserialized, so for a large job the whitespace
        # grows to dwarf the actual content.        
        dxml.XMLTools_RemoveAllWhitespace(self.RootXMLNode)

        contentsText = self.JobXMLDOM.toprettyxml(indent="    ", newl="\n", encoding=None)

        fileH = open(jobFilePathName, "w")
        fileH.write(contentsText)
        fileH.close()
    # End of SaveJobWithoutRuntime




    #####################################################
    #
    # [MLJob::LogMsg]
    #
    # This is a public procedure.
    #####################################################
    def LogMsg(self, messageStr):
        if (self.LogFilePathname == ""):
            return

        #now = datetime.now()
        #timeStr = now.strftime("%Y-%m-%d %H:%M:%S")
        #completeLogLine = timeStr + " " + messageStr + NEWLINE_STR
        completeLogLine = messageStr + NEWLINE_STR

        try:
            fileH = open(self.LogFilePathname, "a+")
            fileH.write(completeLogLine) 
            fileH.flush()
            fileH.close()
        except Exception:
            pass

        # The old, now unused, way to log.
        #self.BufferedLogLines = self.BufferedLogLines + completeLogLine
        
        #print(messageStr)
    # End of LogMsg





    #####################################################
    #
    # [MLJob::ReadJobFromString]
    #
    # Return JOB_E_NO_ERROR or an error
    #####################################################
    def ReadJobFromString(self, jobString):
        #print("MLJob::ReadJobFromString. jobString=" + jobString)

        if (jobString == ""):
            return JOB_E_INVALID_FILE

        # Parse the text string into am XML DOM
        self.JobXMLDOM = dxml.XMLTools_ParseStringToDOM(jobString)
        if (self.JobXMLDOM is None):
            return JOB_E_INVALID_FILE

        self.RootXMLNode = dxml.XMLTools_GetNamedElementInDocument(self.JobXMLDOM, ROOT_ELEMENT_NAME)
        if (self.RootXMLNode is None):
            return JOB_E_INVALID_FILE

        self.FormatVersion = DEFAULT_JOB_FORMAT_VERSION
        attrStr = dxml.XMLTools_GetAttribute(self.RootXMLNode, FORMAT_VERSION_ATTRIBUTE)
        if ((attrStr is not None) and (attrStr != "")):
            self.FormatVersion = int(attrStr)
        self.UUIDXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, JOB_UUID_ELEMENT_NAME)
        self.fileUUID = dxml.XMLTools_GetTextContents(self.UUIDXMLNode)

        # Get the elements for the top-level sections
        self.JobControlXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, JOB_CONTROL_ELEMENT_NAME)
        self.DataXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, DATA_ELEMENT_NAME)

        # The Network Node and its children
        self.NetworkXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, NETWORK_ELEMENT_NAME)
        self.NetworkInputXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, NETWORK_INPUT_ELEMENT_NAME)
        self.NetworkOutputXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, NETWORK_OUTPUT_ELEMENT_NAME)

        self.TrainingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, TRAINING_ELEMENT_NAME)
        self.ResultsXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, RESULTS_ELEMENT_NAME)
        self.ResultsPreflightXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, 
                                                RESULTS_PREFLIGHT_ELEMENT_NAME)
        self.ResultsTrainingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, 
                                                RESULTS_TRAINING_ELEMENT_NAME)
        self.ResultsTestingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, 
                                                RESULTS_TESTING_ELEMENT_NAME)
        self.AllTestResults.InitResultsXML(self.ResultsTestingXMLNode, 
                                                RESULTS_TEST_ALL_TESTS_GROUP_XML_ELEMENT_NAME)
        for index in range(self.NumResultsSubgroups):
            testGroupName = RESULTS_TEST_TEST_SUBGROUP_XML_ELEMENT_NAME + str(index)
            self.TestResultsSubgroupList[index].InitResultsXML(self.ResultsTestingXMLNode, testGroupName)

        self.RuntimeXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, RUNTIME_ELEMENT_NAME)
        self.SavedModelStateXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, 
                                                        SAVED_MODEL_STATE_ELEMENT_NAME)
        self.NeuralNetMatrixListXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.SavedModelStateXMLNode, 
                                                        NETWORK_MATRIX_LIST_NAME)
        self.NetworkType = self.GetNetworkType().lower()

        self.OutputThreshold = -1
        # The default is any probability over 50% is True. This is a coin-toss.
        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.NetworkXMLNode, 
                                                NETWORK_OUTPUT_THRESHOLD_ELEMENT_NAME, "0.5")
        if ((resultStr is not None) and (resultStr != "")):
            try:
                self.OutputThreshold = float(resultStr)
            except Exception:
                self.OutputThreshold = -1

        self.Debug = dxml.XMLTools_GetChildNodeTextAsBool(self.JobControlXMLNode, JOB_CONTROL_DEBUG_ELEMENT_NAME, False)
        self.AllowGPU = dxml.XMLTools_GetChildNodeTextAsBool(self.JobControlXMLNode, JOB_CONTROL_ALLOW_GPU_ELEMENT_NAME, True)
        xmlNode = dxml.XMLTools_GetChildNode(self.JobControlXMLNode, JOB_CONTROL_LOG_FILE_PATHNAME_ELEMENT_NAME)
        if (xmlNode is not None):
            self.LogFilePathname = dxml.XMLTools_GetTextContents(xmlNode).lstrip().rstrip()

        self.ReadTrainingConfigFromXML(self.TrainingXMLNode)

        # Read any runtime if it is present. No error if it is missing.
        #
        # This is used when 
        # 1. Sending jobs between a dispatcher process and a child worker process
        #    In this case, it is not normally stored in a file. 
        #
        # 2. Using a pre-trained neural network to make a prediction on some new data.
        #
        # 3. To "suspend" runtime state and resume it at a later date.
        #    This is not supported now and would raise some tricky synchronization issues.
        self.ReadRuntimeFromXML(self.RuntimeXMLNode)

        # Figure out the result value type and properties. These are used at 
        # runtime, but all infer directly from the name of the output variable so
        # we do not write these to the file.
        self.InitResultInfo()

        # Read the results for both testing and training
        # This will overwrite any values that were intiialized.
        # But, initializing first means anything not stored in the XML file will still be initialized
        self.ReadPreflightResultsFromXML(self.ResultsPreflightXMLNode)
        self.ReadTrainResultsFromXML(self.ResultsTrainingXMLNode)
        self.ReadTestResultsFromXML(self.ResultsTestingXMLNode)

        return JOB_E_NO_ERROR
    # End of ReadJobFromString




    #####################################################
    #
    # [MLJob::WriteJobToString]
    #
    #####################################################
    def WriteJobToString(self):
        # Write the current runtime to a temporary node that is just used for 
        # holding an incomplete request that is currently executing
        # This is used when sending jobs between a dispatcher process and a
        # child worker process, and is not normally stored in a file. It could
        # be saved to a file if we ever want to "suspend" runtime state and
        # resume it at a later date, but that is not supported now and would
        # raise some tricky synchronization issues.
        self.RuntimeXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, RUNTIME_ELEMENT_NAME)
        self.WriteRuntimeToXML(self.RuntimeXMLNode)

        self.WritePreflightResultsToXML(self.ResultsPreflightXMLNode)
        self.WriteTrainResultsToXML(self.ResultsTrainingXMLNode)
        self.WriteTestResultsToXML(self.ResultsTestingXMLNode)

        # Remove any previous formatting text so we can format
        # Otherwise indentation or newlines accumulate each time
        # the XML is serialized/deserialized, so for a large job the whitespace
        # grows to dwarf the actual content.        
        dxml.XMLTools_RemoveAllWhitespace(self.RootXMLNode)

        resultStr = self.JobXMLDOM.toprettyxml(indent="    ", newl="\n", encoding=None)
        return resultStr
    # End of WriteJobToString




    #####################################################
    #
    # [MLJob::ReadTrainingConfigFromXML]
    #
    # There are two similar but importantly different procedures:
    #
    # 1. ReadTrainingConfigFromXML - Read the training configuration from 
    #   the Training section. This is read, but never written, because it
    #   is static configuration that is in the file, not results from execution.
    #
    # 2. ReadTrainResultsFromXML - Read the results of training, from the
    #   results section.
    #####################################################
    def ReadTrainingConfigFromXML(self, parentXMLNode):
        valueInfoNode = dxml.XMLTools_GetChildNode(parentXMLNode, TRAINING_PRIORITY_VALUE_INFO)

        self.TrainingResultMinValue = dxml.XMLTools_GetChildNodeTextAsFloat(valueInfoNode, 
                                                            TRAINING_PRIORITY_MIN_VALUE, -1.0)
        self.TrainingResultMaxValue = dxml.XMLTools_GetChildNodeTextAsFloat(valueInfoNode, 
                                                            TRAINING_PRIORITY_MAX_VALUE, -1.0)
        self.TrainingNumResultPriorities = dxml.XMLTools_GetChildNodeTextAsInt(valueInfoNode, 
                                                            TRAINING_PRIORITY_NUM_CLASSES, -1)

        valueRange = self.TrainingResultMaxValue - self.TrainingResultMinValue
        self.TrainingResultBucketSize = (valueRange / self.TrainingNumResultPriorities)

        listStr = dxml.XMLTools_GetChildNodeTextAsStr(valueInfoNode, TRAINING_PRIORITY_CLASS_PRIORITIES, "")
        if (listStr != ""):
            priorityStrList = listStr.split(",")
            self.TrainingResultClassPriorities = [int(i) for i in priorityStrList]
        else:
            self.TrainingResultClassPriorities = []
    # End - ReadTrainingConfigFromXML




    #####################################################
    #
    # [MLJob::ReadRuntimeFromXML]
    #
    #####################################################
    def ReadRuntimeFromXML(self, parentXMLNode):
        ###################
        # Basics
        # These are all optional. No error if any are missing.
        # Save the current file pathname in the XML so it can be restored when we pass a job back and 
        # forth in memory between processes.
        self.JobFilePathName = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                            RUNTIME_FILE_PATHNAME_ELEMENT_NAME, "")
        self.StartRequestTimeStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                            RUNTIME_START_ELEMENT_NAME, "")
        self.StopRequestTimeStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                            RUNTIME_STOP_ELEMENT_NAME, "")
        self.CurrentEpochNum = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, 
                                                            RUNTIME_CURRENT_EPOCH_ELEMENT_NAME, -1)
        self.RuntimeNonce = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, RUNTIME_NONCE_ELEMENT_NAME, 0)


        self.TotalTrainingLossInCurrentEpoch = dxml.XMLTools_GetChildNodeTextAsFloat(parentXMLNode, 
                                                            RUNTIME_TOTAL_TRAINING_LOSS_CURRENT_EPOCH_ELEMENT_NAME, -1.0)
        self.NumTrainLossValuesCurrentEpoch = dxml.XMLTools_GetChildNodeTextAsFloat(parentXMLNode, 
                                                            RUNTIME_NUM_TRAINING_LOSS_VALUES_CURRENT_EPOCH_ELEMENT_NAME, -1.0)

        ###################
        self.BufferedLogLines = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, RUNTIME_LOG_NODE_ELEMENT_NAME, "")

        ###################
        # Read the latest Hash table
        hashStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, RUNTIME_HASH_DICT_ELEMENT_NAME, "")
        if ((hashStr is not None) and (hashStr != "")):
            self.HashDict = json.loads(hashStr)
    # End - ReadRuntimeFromXML





    #####################################################
    #
    # [MLJob::WriteRuntimeToXML]
    #
    #####################################################
    def WriteRuntimeToXML(self, parentXMLNode):
        dxml.XMLTools_RemoveAllChildNodes(parentXMLNode)

        ###################
        # Basics
        # Save the current file pathname in the XML so it can be restored when we pass a job back and 
        # forth in memory between processes.
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RUNTIME_FILE_PATHNAME_ELEMENT_NAME, str(self.JobFilePathName))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RUNTIME_START_ELEMENT_NAME, str(self.StartRequestTimeStr))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RUNTIME_STOP_ELEMENT_NAME, str(self.StopRequestTimeStr))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RUNTIME_CURRENT_EPOCH_ELEMENT_NAME, str(self.CurrentEpochNum))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RUNTIME_NONCE_ELEMENT_NAME, str(self.RuntimeNonce))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RUNTIME_OS_ELEMENT_NAME, str(platform.platform()))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RUNTIME_CPU_ELEMENT_NAME, str(platform.processor()))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RUNTIME_GPU_ELEMENT_NAME, "None")

        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RUNTIME_TOTAL_TRAINING_LOSS_CURRENT_EPOCH_ELEMENT_NAME, 
                                            str(self.TotalTrainingLossInCurrentEpoch))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RUNTIME_NUM_TRAINING_LOSS_VALUES_CURRENT_EPOCH_ELEMENT_NAME, 
                                            str(self.NumTrainLossValuesCurrentEpoch))

        ###################
        # If there is a log string, then add it to the end of the Result node.
        if (self.BufferedLogLines != ""):
            logXMLNode = dxml.XMLTools_GetChildNode(parentXMLNode, RUNTIME_LOG_NODE_ELEMENT_NAME)
            if (logXMLNode is None):
                logXMLNode = self.JobXMLDOM.createElement(RUNTIME_LOG_NODE_ELEMENT_NAME)
                parentXMLNode.appendChild(logXMLNode)
            dxml.XMLTools_SetTextContents(logXMLNode, self.BufferedLogLines)
        # End - if (self.BufferedLogLines != "")

        ###################
        # Save the list of Matrix hash values
        hashStr = json.dumps(self.HashDict)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, RUNTIME_HASH_DICT_ELEMENT_NAME, hashStr)
    # End -  WriteRuntimeToXML



    #####################################################
    #
    # [MLJob::ReadPreflightResultsFromXML
    # 
    #####################################################
    def ReadPreflightResultsFromXML(self, parentXMLNode):
        self.NumResultsInPreflight = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_NUM_ITEMS_ELEMENT_NAME, 0)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_NUM_ITEMS_PER_CLASS_ELEMENT_NAME, "")
        self.PreflightNumItemsPerClass = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_INPUT_MINS_ELEMENT_NAME, "")
        self.PreflightInputMins = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_INPUT_MAXS_ELEMENT_NAME, "")
        self.PreflightInputMaxs = MLJob_ConvertStringTo1DVector(resultStr)

        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_INPUT_RANGES_ELEMENT_NAME, "")
        self.PreflightInputRanges = MLJob_ConvertStringTo1DVector(resultStr)


        self.PreflightResultMin = dxml.XMLTools_GetChildNodeTextAsFloat(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_OUTPUT_MIN_ELEMENT_NAME, 0.0)
        self.PreflightResultMax = dxml.XMLTools_GetChildNodeTextAsFloat(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_OUTPUT_MAX_ELEMENT_NAME, 0.0)
        self.PreflightResultMean = dxml.XMLTools_GetChildNodeTextAsFloat(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_OUTPUT_MEAN_ELEMENT_NAME, 0.0)
        self.PreflightResultStdDev = dxml.XMLTools_GetChildNodeTextAsFloat(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_OUTPUT_STDDEV_ELEMENT_NAME, 0.0)
        self.PreflightResultTotal = dxml.XMLTools_GetChildNodeTextAsFloat(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_OUTPUT_TOTAL_ELEMENT_NAME, 0.0)
        self.PreflightResultCount = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_OUTPUT_COUNT_ELEMENT_NAME, 0)


        ################################
        # Find the existing list of class weights
        classWeightsListXMLNode = dxml.XMLTools_GetChildNode(self.ResultsPreflightXMLNode, 
                                                RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_WEIGHT_LIST)
        if (classWeightsListXMLNode is not None):
            self.NumResultClasses = dxml.XMLTools_GetChildNodeTextAsInt(classWeightsListXMLNode, 
                                                RESULTS_PREFLIGHT_TRAINING_PRIORITY_NUM_RESULT_CLASSES, 
                                                self.NumResultClasses)

            # Make a new runtime object for each resultClass element
            self.PreflightResultClassWeights = [0] * self.NumResultClasses

            # Read each resultClass
            resultClassXMLNode = dxml.XMLTools_GetChildNode(classWeightsListXMLNode, 
                                                            RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_WEIGHT)
            while (resultClassXMLNode is not None):
                resultClassID = dxml.XMLTools_GetChildNodeTextAsInt(resultClassXMLNode, 
                                                        RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_ID, -1)
                classWeight = dxml.XMLTools_GetChildNodeTextAsFloat(resultClassXMLNode, 
                                                        RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_WEIGHT_VALUE,
                                                        -1.0)
                if ((resultClassID >= 0) and (classWeight >= 0)):
                    self.PreflightResultClassWeights[resultClassID] = classWeight

                resultClassXMLNode = dxml.XMLTools_GetPeerNode(resultClassXMLNode, 
                                                        RESULTS_PREFLIGHT_TRAINING_PRIORITY_RESULT_CLASS_WEIGHT)
            # End - while (resultClassXMLNode is not None):
        else:   # if (classWeightsListXMLNode is not None):
            self.PreflightResultClassWeights = []


        #############################
        # Read  the derived training weights
        self.PreflightEstimatedMinResultValueForPriority = dxml.XMLTools_GetChildNodeTextAsFloat(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_ESTIMATED_MIN_VALUE_ELEMENT_NAME, 0.0)
        self.PreflightNumResultPriorities = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_NUM_RESULT_PRIORITIES_ELEMENT_NAME, 0)
        self.PreflightResultMinPreflightResultBucketSize = dxml.XMLTools_GetChildNodeTextAsFloat(parentXMLNode, 
                                                        RESULTS_PREFLIGHT_RESULT_BUCKET_SIZE_ELEMENT_NAME, 0.0)
        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.ResultsPreflightXMLNode,
                                                RESULTS_PREFLIGHT_RESULT_NUM_ITEMS_PER_BUCKET_ELEMENT_NAME, "")
        if (resultStr is not None):
            self.PreflightNumResultsInEachBucket = []
            resultArray = resultStr.split(",")
            for numStr in resultArray:
                try:
                    countInt = int(numStr)
                    self.PreflightNumResultsInEachBucket.append(countInt)
                except Exception:
                    continue
            # End - for numStr in resultArray:
        # End - if (resultStr is not None):


        ################################
        # Read the list of missing value counts
        self.PreflightNumMissingInputsList = []
        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.ResultsPreflightXMLNode,
                                            RESULTS_PREFLIGHT_NUM_MISSING_VALUES_LIST_ELEMENT_NAME, "")
        if (resultStr is not None):
            resultArray = resultStr.split(",")
            for numStr in resultArray:
                try:
                    countInt = int(numStr)
                    self.PreflightNumMissingInputsList.append(countInt)
                except Exception:
                    continue
            # End - for numStr in resultArray:
        # End - if (resultStr is not None):

        self.FinishPreflight()
    # End - ReadPreflightResultsFromXML






    #####################################################
    #
    # [MLJob::WritePreflightResultsToXML
    # 
    #####################################################
    def WritePreflightResultsToXML(self, parentXMLNode):
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_NUM_ITEMS_ELEMENT_NAME, str(self.NumResultsInPreflight))

        resultStr = MLJob_Convert1DVectorToString(self.PreflightNumItemsPerClass)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_NUM_ITEMS_PER_CLASS_ELEMENT_NAME, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.PreflightInputMins)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_INPUT_MINS_ELEMENT_NAME, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.PreflightInputMaxs)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_INPUT_MAXS_ELEMENT_NAME, resultStr)

        resultStr = MLJob_Convert1DVectorToString(self.PreflightInputRanges)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_INPUT_RANGES_ELEMENT_NAME, resultStr)

        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_OUTPUT_MIN_ELEMENT_NAME, str(self.PreflightResultMin))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_OUTPUT_MAX_ELEMENT_NAME, str(self.PreflightResultMax))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_OUTPUT_MEAN_ELEMENT_NAME, str(self.PreflightResultMean))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_OUTPUT_STDDEV_ELEMENT_NAME, str(self.PreflightResultStdDev))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_OUTPUT_TOTAL_ELEMENT_NAME, str(self.PreflightResultTotal))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_OUTPUT_COUNT_ELEMENT_NAME, str(self.PreflightResultCount))


        #############################
        # Write the derived training weights
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_ESTIMATED_MIN_VALUE_ELEMENT_NAME, 
                                    str(self.PreflightEstimatedMinResultValueForPriority))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_NUM_RESULT_PRIORITIES_ELEMENT_NAME, 
                                    str(self.PreflightNumResultPriorities))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                    RESULTS_PREFLIGHT_RESULT_BUCKET_SIZE_ELEMENT_NAME, 
                                    str(self.PreflightResultBucketSize))
        resultStr = ""
        for currentNum in self.PreflightNumResultsInEachBucket:
            resultStr = resultStr + str(currentNum) + ","
        # End - for num in self.PreflightNumMissingInputsList:
        if (resultStr != ""):
            resultStr = resultStr[:-1]
        dxml.XMLTools_AddChildNodeWithText(self.ResultsPreflightXMLNode, 
                                           RESULTS_PREFLIGHT_RESULT_NUM_ITEMS_PER_BUCKET_ELEMENT_NAME, 
                                           resultStr)

        ################################
        # Write the list of missing value counts
        resultStr = ""
        for currentNum in self.PreflightNumMissingInputsList:
            resultStr = resultStr + str(currentNum) + ","
        # End - for num in self.PreflightNumMissingInputsList:
        if (resultStr != ""):
            resultStr = resultStr[:-1]
        dxml.XMLTools_AddChildNodeWithText(self.ResultsPreflightXMLNode, 
                                           RESULTS_PREFLIGHT_NUM_MISSING_VALUES_LIST_ELEMENT_NAME, 
                                           resultStr)

    # End - WritePreflightResultsToXML





    #####################################################
    #
    # [MLJob::ReadTrainResultsFromXML
    # 
    #####################################################
    def ReadTrainResultsFromXML(self, parentXMLNode):
        ###################
        self.NumSamplesTrainedPerEpoch = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, 
                                             RESULTS_TRAIN_SEQUENCES_TRAINED_PER_EPOCH_ELEMENT_NAME, 0)
        self.NumTimelinesTrainedPerEpoch = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, 
                                             RESULTS_TRAIN_TIMELINES_TRAINED_PER_EPOCH_ELEMENT_NAME, 0)
        self.NumTimelinesSkippedPerEpoch = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, 
                                             RESULTS_TRAIN_TIMELINES_SKIPPED_PER_EPOCH_ELEMENT_NAME, 0)
        self.NumDataPointsTrainedPerEpoch = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, 
                                             RESULTS_TRAIN_DATA_POINTS_TRAINED_PER_EPOCH_ELEMENT_NAME, 0)

        ###################
        self.AvgLossPerEpochList = []
        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                            RESULTS_TRAIN_AVG_LOSS_PER_EPOCH_ELEMENT_NAME, "")
        resultArray = resultStr.split(",")
        for avgLossStr in resultArray:
            try:
                avgLossFloat = float(avgLossStr)
                avgLossFloat = round(avgLossFloat, 4)
                self.AvgLossPerEpochList.append(avgLossFloat)
            except Exception:
                continue

        #################
        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                            RESULTS_TRAIN_NUM_ITEMS_PER_CLASS_ELEMENT_NAME, "")
        self.TrainNumItemsPerClass = MLJob_ConvertStringTo1DVector(resultStr)
    # End - ReadTrainResultsFromXML




    #####################################################
    #
    # [MLJob::WriteTrainResultsToXML
    # 
    #####################################################
    def WriteTrainResultsToXML(self, parentXMLNode):
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                            RESULTS_TRAIN_SEQUENCES_TRAINED_PER_EPOCH_ELEMENT_NAME, 
                                            str(self.NumSamplesTrainedPerEpoch))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                            RESULTS_TRAIN_TIMELINES_TRAINED_PER_EPOCH_ELEMENT_NAME, 
                                            str(self.NumTimelinesTrainedPerEpoch))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                            RESULTS_TRAIN_TIMELINES_SKIPPED_PER_EPOCH_ELEMENT_NAME, 
                                            str(self.NumTimelinesSkippedPerEpoch))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                            RESULTS_TRAIN_DATA_POINTS_TRAINED_PER_EPOCH_ELEMENT_NAME, 
                                            str(self.NumDataPointsTrainedPerEpoch))

        ###################
        resultStr = ""
        for avgLoss in self.AvgLossPerEpochList:
            avgLoss = round(avgLoss, 4)
            resultStr = resultStr + str(avgLoss) + ","
        # Remove the last comma
        if (len(resultStr) > 0):
            resultStr = resultStr[:-1]
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                        RESULTS_TRAIN_AVG_LOSS_PER_EPOCH_ELEMENT_NAME,
                                        resultStr)

        ###################
        resultStr = MLJob_Convert1DVectorToString(self.TrainNumItemsPerClass)
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                                        RESULTS_TRAIN_NUM_ITEMS_PER_CLASS_ELEMENT_NAME, 
                                        resultStr)
    # End - WriteTrainResultsToXML




    #####################################################
    #
    # [MLJob::ReadTestResultsFromXML
    # 
    #####################################################
    def ReadTestResultsFromXML(self, parentXMLNode):
        self.NumResultsSubgroups = dxml.XMLTools_GetChildNodeTextAsInt(parentXMLNode, 
                                                    RESULTS_TEST_NUM_GROUPS_ELEMENT_NAME, 
                                                    DEFAULT_NUM_TEST_SUBGROUPS)
        self.SubgroupMeaning = dxml.XMLTools_GetChildNodeTextAsStr(parentXMLNode, 
                                                    RESULTS_TEST_GROUP_MEANING_XML_ELEMENT_NAME,
                                                    DEFAULT_TEST_GROUP_MEANING)

        self.AllTestResults.ReadTestResultsFromXML()
        for index in range(self.NumResultsSubgroups):
            self.TestResultsSubgroupList[index].ReadTestResultsFromXML()
    # End - ReadTestResultsFromXML




    #####################################################
    #
    # [MLJob::WriteTestResultsToXML
    # 
    #####################################################
    def WriteTestResultsToXML(self, parentXMLNode):
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                            RESULTS_TEST_NUM_GROUPS_ELEMENT_NAME, 
                            str(self.NumResultsSubgroups))
        dxml.XMLTools_AddChildNodeWithText(parentXMLNode, 
                            RESULTS_TEST_GROUP_MEANING_XML_ELEMENT_NAME,
                            self.SubgroupMeaning)

        self.AllTestResults.WriteTestResultsToXML()
        for index in range(self.NumResultsSubgroups):
            self.TestResultsSubgroupList[index].WriteTestResultsToXML()
    # End - WriteTestResultsToXML





    #####################################################
    #
    # [MLJob::StartJobExecution]
    #
    # This is a public procedure.
    #####################################################
    def StartJobExecution(self):
        # Discard Previous results
        dxml.XMLTools_RemoveAllChildNodes(self.ResultsXMLNode)
        self.ResultsPreflightXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode,
                                                    RESULTS_PREFLIGHT_ELEMENT_NAME)
        self.ResultsTrainingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, 
                                                    RESULTS_TRAINING_ELEMENT_NAME)
        self.ResultsTestingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, 
                                                    RESULTS_TESTING_ELEMENT_NAME)
        self.AllTestResults.InitResultsXML(self.ResultsTestingXMLNode, 
                                                    RESULTS_TEST_ALL_TESTS_GROUP_XML_ELEMENT_NAME)
        for index in range(self.NumResultsSubgroups):
            testGroupName = RESULTS_TEST_TEST_SUBGROUP_XML_ELEMENT_NAME + str(index)
            self.TestResultsSubgroupList[index].InitResultsXML(self.ResultsTestingXMLNode, testGroupName)

        self.SetJobControlStr(JOB_CONTROL_STATUS_ELEMENT_NAME, MLJOB_STATUS_IDLE)
        self.SetJobControlStr(JOB_CONTROL_RESULT_MSG_ELEMENT_NAME, "")
        self.SetJobControlStr(JOB_CONTROL_ERROR_CODE_ELEMENT_NAME, str(JOB_E_NO_ERROR))

        now = datetime.now()
        self.StartRequestTimeStr = now.strftime("%Y-%m-%d %H:%M:%S")

        # Reset the log file if there is one.
        if (self.LogFilePathname != ""):
            try:
                os.remove(self.LogFilePathname) 
            except Exception:
                pass
            try:
                fileH = open(self.LogFilePathname, "w+")
                fileH.flush()
                fileH.close()
            except Exception:
                pass
        # End - if (self.LogFilePathname != ""):
    # End of StartJobExecution






    #####################################################
    #
    # [MLJob::FinishJobExecution]
    #
    # This is a public procedure.
    #####################################################
    def FinishJobExecution(self, errCode, errorMsg):
        # Each request has a single test. When we finish the test, we have
        # finished the entire reqeust.
        self.SetJobControlStr(JOB_CONTROL_STATUS_ELEMENT_NAME, MLJOB_STATUS_DONE)
        self.SetJobControlStr(JOB_CONTROL_ERROR_CODE_ELEMENT_NAME, str(errCode))
        if (errCode == JOB_E_NO_ERROR):
            self.SetJobControlStr(JOB_CONTROL_RESULT_MSG_ELEMENT_NAME, 
                                    JOB_CONTROL_RESULT_MSG_OK)
        else:
            self.SetJobControlStr(JOB_CONTROL_RESULT_MSG_ELEMENT_NAME, errorMsg)

        # Discard all of the hash values. Those are only used for debugging.
        xmlNode = dxml.XMLTools_GetChildNode(self.RuntimeXMLNode, RUNTIME_HASH_DICT_ELEMENT_NAME)
        if (xmlNode is not None):
            dxml.XMLTools_RemoveAllChildNodes(xmlNode)
        self.HashDict = {}

        now = datetime.now()
        self.StopRequestTimeStr = now.strftime("%Y-%m-%d %H:%M:%S")

        # Remove earlier results. We will write the final results when we save the job to XML
        dxml.XMLTools_RemoveAllChildNodes(self.ResultsXMLNode)
        self.ResultsPreflightXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, 
                                                            RESULTS_PREFLIGHT_ELEMENT_NAME)
        self.ResultsTrainingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, 
                                                            RESULTS_TRAINING_ELEMENT_NAME)
        self.ResultsTestingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, 
                                                            RESULTS_TESTING_ELEMENT_NAME)
        self.AllTestResults.InitResultsXML(self.ResultsTestingXMLNode, 
                                                            RESULTS_TEST_ALL_TESTS_GROUP_XML_ELEMENT_NAME)
        for index in range(self.NumResultsSubgroups):
            testGroupName = RESULTS_TEST_TEST_SUBGROUP_XML_ELEMENT_NAME + str(index)
            self.TestResultsSubgroupList[index].InitResultsXML(self.ResultsTestingXMLNode, testGroupName)

        self.AllTestResults.StopTesting()
        for index in range(self.NumResultsSubgroups):
            testGroupName = RESULTS_TEST_TEST_SUBGROUP_XML_ELEMENT_NAME + str(index)
            self.TestResultsSubgroupList[index].StopTesting()
    # End of FinishJobExecution




    #####################################################
    #
    # [MLJob::InitResultInfo
    # 
    # This is a private procedure, which takes the reuslt var
    # and computes its type, and more values used to collect result statistics.
    # This is done anytime we restore a job from memory, and also
    # when we start pre-flight or training.
    #####################################################
    def InitResultInfo(self):
        self.ResultValueType = self.GetNetworkOutputType()
        if (self.ResultValueType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
            self.NumResultClasses = ML_JOB_NUM_NUMERIC_VALUE_BUCKETS
            resultValName = self.GetNetworkOutputVarName()
            self.ResultValMinValue, self.ResultValMaxValue = tdf.TDF_GetMinMaxValuesForVariable(resultValName)
            valRange = float(self.ResultValMaxValue - self.ResultValMinValue)
            self.ResultValBucketSize = float(valRange) / float(ML_JOB_NUM_NUMERIC_VALUE_BUCKETS)
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_BOOL):
            self.NumResultClasses = 2
            self.ResultValMinValue = 0
            self.ResultValMaxValue = 1
            self.ResultValBucketSize = 1
        else:
            self.NumResultClasses = 1
            self.ResultValMinValue = 0
            self.ResultValMaxValue = 0
            self.ResultValBucketSize = 1

        inputVarNameListStr = self.GetNetworkInputVarNames()
        inputVarArray = inputVarNameListStr.split(MLJOB_NAMEVAL_SEPARATOR_CHAR)
        self.numInputVars = len(inputVarArray)

        self.AllTestResults.SetGlobalResultInfo(self.ResultValueType, 
                                    self.NumResultClasses, 
                                    self.ResultValMinValue, 
                                    self.ResultValMaxValue, 
                                    self.ResultValBucketSize, 
                                    self.IsLogisticNetwork, 
                                    self.OutputThreshold)

        for index in range(self.NumResultsSubgroups):
            self.TestResultsSubgroupList[index].SetGlobalResultInfo(self.ResultValueType, 
                                    self.NumResultClasses, 
                                    self.ResultValMinValue, 
                                    self.ResultValMaxValue, 
                                    self.ResultValBucketSize, 
                                    self.IsLogisticNetwork, 
                                    self.OutputThreshold)
    # End - InitResultInfo




    #####################################################
    #
    # [MLJob::StartPreflight]
    # 
    # This is a public procedure.
    #####################################################
    def StartPreflight(self):
        # Figure out the result value type and properties. These are used at 
        # runtime, but all infer directly from the name of the output variable so
        # we do not write these to the file.
        self.InitResultInfo()

        self.PreflightNumMissingInputsList = [0] * self.numInputVars

        self.PreflightNumItemsPerClass = numpy.zeros(self.NumResultClasses)
        self.PreflightInputMins = numpy.full((self.numInputVars), 1000000)
        self.PreflightInputMaxs = numpy.full((self.numInputVars), -1)
        self.PreflightInputRanges = numpy.full((self.numInputVars), 0)

        self.PreflightResultMin = 1000000
        self.PreflightResultMax = 0
        self.PreflightResultTotal = 0
        self.PreflightResultCount = 0

        # These are just guesses. We will not know the real min until we complete preflight.
        # However, these guesses will let us make an estimate at training priority.
        if (tdf.TDF_DATA_TYPE_BOOL == self.ResultValueType):
            self.PreflightEstimatedMinResultValueForPriority = 0
            self.PreflightNumResultPriorities = 2
            self.PreflightResultBucketSize = 1
        else:
            resultValueName = self.GetNetworkOutputVarName()
            minVal, maxVal = tdf.TDF_GetMinMaxValuesForVariable(resultValueName)
            valueRange = maxVal - minVal
            self.PreflightEstimatedMinResultValueForPriority = minVal
            self.PreflightNumResultPriorities = 20
            self.PreflightResultBucketSize = float(valueRange / self.PreflightNumResultPriorities)
        # Common
        self.PreflightNumResultsInEachBucket = [0] * self.PreflightNumResultPriorities

        self.SetJobControlStr(JOB_CONTROL_STATUS_ELEMENT_NAME, MLJOB_STATUS_PREFLIGHT)
    # End - StartPreflight




    #####################################################
    #
    # [MLJob::PreflightData
    # 
    # This is a public procedure.
    #####################################################
    def PreflightData(self, inputVec, resultVal):
        for valNum in range(self.numInputVars):
            currentValue = inputVec[valNum]
            if (currentValue < self.PreflightInputMins[valNum]):
                self.PreflightInputMins[valNum] = currentValue
            if (currentValue > self.PreflightInputMaxs[valNum]):
                self.PreflightInputMaxs[valNum] = currentValue
        # End - for valNum in range(self.numInputVars)

        # Be careful, results may sometimes be invalid if we are processing a
        # sequence. There may not be a result for every intermediate step, only
        # the last step.
        if ((resultVal != tdf.TDF_INVALID_VALUE) and (resultVal > tdf.TDF_SMALLEST_VALID_VALUE)):
            if (resultVal < self.PreflightResultMin):
                self.PreflightResultMin = resultVal
            if (resultVal > self.PreflightResultMax):
                self.PreflightResultMax = resultVal
            self.PreflightResultTotal += resultVal
            self.PreflightResultCount += 1

            offset = max(resultVal - self.PreflightEstimatedMinResultValueForPriority, 0)
            bucketNum = int(offset / self.PreflightResultBucketSize)
            if (bucketNum >= self.PreflightNumResultPriorities):
                bucketNum = self.PreflightNumResultPriorities - 1
            self.PreflightNumResultsInEachBucket[bucketNum] += 1
        # End - if (resultVal != tdf.TDF_INVALID_VALUE):
    # End - PreflightData



    #####################################################
    #
    # [MLJob::FinishPreflight
    # 
    #####################################################
    def FinishPreflight(self):
        if (len(self.PreflightInputRanges) == 0):
            return

        for inputNum in range(self.numInputVars):
            self.PreflightInputRanges[inputNum] = self.PreflightInputMaxs[inputNum] - self.PreflightInputMins[inputNum]
        # End - for inputNum in range(self.numInputVars):

        # Only do this if we did not restore the value and there are useful inputs
        if ((self.PreflightResultMean == 0) and (self.PreflightResultCount > 0)):
            self.PreflightResultMean = float(self.PreflightResultTotal) / float(self.PreflightResultCount)
            self.PreflightResultStdDev = 0
    # End - FinishPreflight


    #####################################################
    # [MLJob::GetPreflightResults]
    #####################################################
    def GetPreflightResults(self):
        return self.numInputVars, self.PreflightInputMins, self.PreflightInputRanges
    # End - GetPreflightResults

    #####################################################
    # [MLJob::GetNumTrainingPriorities]
    #####################################################
    def GetNumTrainingPriorities(self):
        return self.TrainingNumResultPriorities

    #####################################################
    # [MLJob::GetPreflightNumMissingInputs]
    #####################################################
    def GetPreflightNumMissingInputs(self):
        return self.PreflightNumMissingInputsList

    #####################################################
    # [MLJob::SetPreflightNumMissingInputs]
    #####################################################
    def SetPreflightNumMissingInputs(self, newList):
        self.PreflightNumMissingInputsList = newList



    #####################################################
    #
    # [MLJob::GetTrainingPriority]
    # 
    #####################################################
    def GetTrainingPriority(self, resultVal):
        #####################
        if (self.ResultValueType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
            offset = max((resultVal - self.TrainingResultMinValue), 0.0)
            if (self.TrainingResultBucketSize > 0):
                resultBucket = int(offset / self.TrainingResultBucketSize)
            else:
                resultBucket = 0
            resultBucket = min(resultBucket, self.TrainingNumResultPriorities - 1)

            return self.TrainingResultClassPriorities[resultBucket]
        #####################
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_BOOL):
            return 0
        else:
            return 0
    # End - GetTrainingPriority




    #####################################################
    #
    # [MLJob::StartTraining
    # 
    # This is a public procedure.
    #####################################################
    def StartTraining(self):
        random.seed()

        # Figure out the result value type and properties. These are used at 
        # runtime, but all infer directly from the name of the output variable so
        # we do not write these to the file.
        self.InitResultInfo()

        self.CurrentEpochNum = 0
        self.NumSamplesTrainedPerEpoch = 0
        self.NumTimelinesTrainedPerEpoch = 0
        self.NumTimelinesSkippedPerEpoch = 0
        self.NumDataPointsTrainedPerEpoch = 0

        self.TotalTrainingLossInCurrentEpoch = 0.0
        self.NumTrainLossValuesCurrentEpoch = 0
        self.AvgLossPerEpochList = []

        self.TrainNumItemsPerClass = [0] * self.NumResultClasses

        self.SetJobControlStr(JOB_CONTROL_STATUS_ELEMENT_NAME, MLJOB_STATUS_TRAINING)
    # End - StartTraining




    #####################################################
    #
    # [MLJob::StartTrainingEpoch
    # 
    # This is a public procedure.
    #####################################################
    def StartTrainingEpoch(self):
        # Reset the counters for the new epoch
        self.TotalTrainingLossInCurrentEpoch = 0.0
        self.NumTrainLossValuesCurrentEpoch = 0
    # End - StartTrainingEpoch



    #####################################################
    #
    # [MLJob::RecordTrainingLoss
    # 
    # This is a public procedure.
    #####################################################
    def RecordTrainingLoss(self, loss):
        # Be careful, the loss may be positive or negative
        self.TotalTrainingLossInCurrentEpoch += abs(loss)
        self.NumTrainLossValuesCurrentEpoch += 1
    # End -  RecordTrainingLoss



    #####################################################
    #
    # [MLJob::RecordTrainingSample
    # 
    # This is a public procedure.
    #
    # The standard deviation is the square root of the average of the squared deviations from the mean, 
    # i.e., std = sqrt(mean(x)) , where x = abs(a - a. mean())**2 . 
    # The average squared deviation is typically calculated as x. sum() / N , where N = len(x) .
    #####################################################
    def RecordTrainingSample(self, inputVec, actualValue):
        # We only record the stats on the first epoch.
        if (self.CurrentEpochNum > 0):
            return
        if (actualValue == tdf.TDF_INVALID_VALUE):
            return
        self.NumSamplesTrainedPerEpoch += 1

        #####################
        if (self.ResultValueType in (tdf.TDF_DATA_TYPE_INT, tdf.TDF_DATA_TYPE_FLOAT)):
            offset = max(actualValue - self.ResultValMinValue, 0)
            bucketNum = int(offset / self.ResultValBucketSize)
            if (bucketNum >= ML_JOB_NUM_NUMERIC_VALUE_BUCKETS):
                bucketNum = ML_JOB_NUM_NUMERIC_VALUE_BUCKETS - 1
            self.TrainNumItemsPerClass[bucketNum] += 1
        #####################
        elif (self.ResultValueType == tdf.TDF_DATA_TYPE_BOOL):
            intActualValue = max(int(actualValue), 0)
            intActualValue = min(int(actualValue), 1)
            self.TrainNumItemsPerClass[intActualValue] += 1
    # End -  RecordTrainingSample





    #####################################################
    #
    # [MLJob::FinishTrainingEpoch]
    # 
    # This is a public procedure.
    #####################################################
    def FinishTrainingEpoch(self):
        if (self.NumTrainLossValuesCurrentEpoch > 0):
            avgLoss = float(self.TotalTrainingLossInCurrentEpoch / float(self.NumTrainLossValuesCurrentEpoch))
        else:
            avgLoss = 0.0

        self.AvgLossPerEpochList.append(avgLoss)
        self.CurrentEpochNum += 1
    # End -  FinishTrainingEpoch




    #####################################################
    #
    # [MLJob::StartTesting]
    # 
    # This is a public procedure.
    #####################################################
    def StartTesting(self):
        # Figure out the result value type and properties. These are used at 
        # runtime, but all infer directly from the name of the output variable so
        # we do not write these to the file.
        self.InitResultInfo()

        self.AllTestResults.StartTesting()
        for index in range(self.NumResultsSubgroups):
            self.TestResultsSubgroupList[index].StartTesting()

        self.SetJobControlStr(JOB_CONTROL_STATUS_ELEMENT_NAME, MLJOB_STATUS_TESTING)
    # End - StartTesting




    #####################################################
    #
    # [MLJob::RecordTestingResult]
    # 
    # This is a for the job object. It calls the RecordTestingResult
    # procedure for the approprate results bucket
    #####################################################
    def RecordTestingResult(self, actualValue, predictedValue, subGroupNum):
        # Every result will go into the totals bucket
        self.AllTestResults.RecordTestingResult(actualValue, predictedValue)

        # If there is a subgroup, then we *also* add it to the results for that subgroup
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            self.TestResultsSubgroupList[subGroupNum].RecordTestingResult(actualValue, predictedValue)
    # End -  RecordTestingResult




    #####################################################
    #
    # [MLJob::GetNamedStateAsStr
    # 
    # This is used by the different models to restore their 
    # runtime state
    #####################################################
    def GetNamedStateAsStr(self, name, defaultVal):
        stateXMLNode = dxml.XMLTools_GetChildNode(self.SavedModelStateXMLNode, name)
        if (stateXMLNode is None):
            return defaultVal

        stateStr = dxml.XMLTools_GetTextContents(stateXMLNode)
        if (stateStr is None):
            return defaultVal

        stateStr = stateStr.lstrip().rstrip()
        return stateStr
    # End - GetNamedStateAsStr




    #####################################################
    #
    # [MLJob::SetNamedStateAsStr
    # 
    # This is used by the different models to restore their 
    # runtime state
    #####################################################
    def SetNamedStateAsStr(self, name, stateStr):
        stateXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.SavedModelStateXMLNode, name)
        if (stateXMLNode is None):
            return

        dxml.XMLTools_SetTextContents(stateXMLNode, stateStr)
    # End - SetNamedStateAsStr



    #####################################################
    #
    # [MLJob::GetLinearUnitMatrices
    # 
    # Returns:
    #   FoundIt (True/False)
    #   weightMatrix
    #   biasMatrix
    #####################################################
    def GetLinearUnitMatrices(self, name):
        linearUnitNode = dxml.XMLTools_GetChildNode(self.NeuralNetMatrixListXMLNode, name)
        if (linearUnitNode is None):
            return False, None, None

        weightXMLNode = dxml.XMLTools_GetChildNode(linearUnitNode, NETWORK_MATRIX_WEIGHT_MATRIX_NAME)
        biasXMLNode = dxml.XMLTools_GetChildNode(linearUnitNode, NETWORK_MATRIX_BIAS_VECTOR_NAME)
        if ((weightXMLNode is None) or (biasXMLNode is None)):
            return False, None, None

        weightStr = dxml.XMLTools_GetTextContents(weightXMLNode).lstrip().rstrip()
        biasStr = dxml.XMLTools_GetTextContents(biasXMLNode).lstrip().rstrip()

        weightMatrix = self.MLJob_ConvertStringTo2DMatrix(weightStr)
        biasMatrix = MLJob_ConvertStringTo1DVector(biasStr)

        return True, weightMatrix, biasMatrix
    # End - GetLinearUnitMatrices


     

    #####################################################
    #
    # [MLJob::SetLinearUnitMatrices
    # 
    #####################################################
    def SetLinearUnitMatrices(self, name, weightMatrix, biasMatrix):
        linearUnitNode = dxml.XMLTools_GetOrCreateChildNode(self.NeuralNetMatrixListXMLNode, name)
        if (linearUnitNode is None):
            return
        weightXMLNode = dxml.XMLTools_GetOrCreateChildNode(linearUnitNode, NETWORK_MATRIX_WEIGHT_MATRIX_NAME)
        biasXMLNode = dxml.XMLTools_GetOrCreateChildNode(linearUnitNode, NETWORK_MATRIX_BIAS_VECTOR_NAME)
        if ((weightXMLNode is None) or (biasXMLNode is None)):
            return

        weightStr = self.MLJob_Convert2DMatrixToString(weightMatrix)
        biasStr = MLJob_Convert1DVectorToString(biasMatrix)

        dxml.XMLTools_SetTextContents(biasXMLNode, biasStr)
        dxml.XMLTools_SetTextContents(weightXMLNode, weightStr)
    # End - SetLinearUnitMatrices




    ################################################################################
    #
    # [MLJob_Convert2DMatrixToString]
    #
    # inputArray is a numpy array.
    ################################################################################
    def MLJob_Convert2DMatrixToString(self, inputArray):
        numRows = len(inputArray)
        if (numRows <= 0):
            numCols = 0
        else:
            numCols = len(inputArray[0])

        resultString = "NumD=2;D=" + str(numRows) + VALUE_SEPARATOR_CHAR + str(numCols) + ";T=float;" + ROW_SEPARATOR_CHAR
        for rowNum in range(numRows):
            row = inputArray[rowNum]
            for numVal in row:
                resultString = resultString + str(numVal) + VALUE_SEPARATOR_CHAR
            resultString = resultString[:-1]
            resultString = resultString + ROW_SEPARATOR_CHAR

        return resultString
    # End - MLJob_Convert2DMatrixToString



    ################################################################################
    #
    # [MLJob_ConvertStringTo2DMatrix]
    #
    ################################################################################
    def MLJob_ConvertStringTo2DMatrix(self, matrixStr):
        # Read the dimension property
        sectionList = matrixStr.split(MLJOB_NAMEVAL_SEPARATOR_CHAR)
        dimensionStr = ""
        for propertyStr in sectionList:
            propertyParts = propertyStr.split("=")
            if (len(propertyParts) < 2):
                continue

            propName = propertyParts[0]
            propValue = propertyParts[1]
            if (propName == "D"):
                dimensionStr = propValue
        # End - for propertyStr in sectionList:

        # Parse the dimension property.
        numRows = 0
        numCols = 0
        if (dimensionStr != ""):
            dimensionList = dimensionStr.split(VALUE_SEPARATOR_CHAR)
            if (len(dimensionList) == 2):
                numRows = int(dimensionList[0])
                numCols = int(dimensionList[1])
            else:
                print("\n\nERROR! MLJob_ConvertStringTo2DMatrix. Invalid dimension for a matrixStr. dimensionStr=[" + dimensionStr + "]")
                sys.exit(0)
        # End - if (dimensionStr != ""):

        # Make an empty matrix which will be filled below.
        newMatrix = numpy.empty([numRows, numCols])

        # Read each 1-D vector and put it in the next position inside the result matrix
        matrixAllRowsStr = sectionList[len(sectionList) - 1]
        matrixRowStrList = matrixAllRowsStr.split(ROW_SEPARATOR_CHAR)
        rowNum = 0    
        for singleRowStr in matrixRowStrList:
            if (singleRowStr != ""):
                # Place a vector into the current spot of the result matrix
                valueList = singleRowStr.split(VALUE_SEPARATOR_CHAR)
                colNum = 0
                for value in valueList:
                    if (colNum >= numCols):
                        print("\n\nERROR! MLJob_ConvertStringTo2DMatrix. Overran a matrix. dimensionStr=[" + dimensionStr + "]")
                        sys.exit(0)
                    newMatrix[rowNum][colNum] = float(value)
                    colNum += 1
                # End - for value in valueList:

                # We should have filled it completely, and will stop at the end of the matrix
                if (colNum != numCols):
                    print("\n\nERROR! MLJob_ConvertStringTo2DMatrix. Underfilled a row in the matrix. dimensionStr=[" + dimensionStr + "]")
                    sys.exit(0)

                # Advance the position where we will next fill the result matrix
                rowNum += 1
            # End - if (singleRowStr != ""):
        # End - for singleRowStr in matrixRowStrList:

        # We should have filled it completely, and will stop at the end of the matrix
        if (rowNum != numRows):
            print("\n\nERROR! MLJob_ConvertStringTo2DMatrix. Underfilled the entire matrix. dimensionStr=[" + dimensionStr + "]")
            sys.exit(0)

        return newMatrix
    # End - MLJob_ConvertStringTo2DMatrix




    #####################################################
    #
    #   ACCESSOR METHODS
    #
    # A lot of the use of Job objects is to store hypervariables
    # to control execution, and also to store the results of 
    # execution for later analysis. These methods are used for both.
    #####################################################

    #####################################################
    #
    # [MLJob::GetNetworkType]
    #
    #####################################################
    def GetNetworkType(self):
        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.NetworkXMLNode, NETWORK_TYPE_ELEMENT_NAME, "")
        if (resultStr is None):
            return ""
        return resultStr
    # End of GetNetworkType
            

    #####################################################
    # [MLJob::GetJobDescription]
    #####################################################
    def GetJobDescription(self):
        return self.GetJobControlStr(JOB_CONTROL_DESCRIPTION_ELEMENT_NAME, "")


    #####################################################
    # [MLJob::GetJobVariation]
    #####################################################
    def GetJobVariation(self):
        return self.GetJobControlStr(JOB_CONTROL_VARIATION_ELEMENT_NAME, "")


    #####################################################
    # [MLJob::GetJobStatus]
    #####################################################
    def GetJobStatus(self):
        jobStatus = self.GetJobControlStr(JOB_CONTROL_STATUS_ELEMENT_NAME, MLJOB_STATUS_IDLE)
        jobErrStr = self.GetJobControlStr(JOB_CONTROL_ERROR_CODE_ELEMENT_NAME, str(JOB_E_NO_ERROR))
        errorMsg = self.GetJobControlStr(JOB_CONTROL_RESULT_MSG_ELEMENT_NAME, "")
        try:
            errCode = int(jobErrStr)
        except Exception:
            errCode = JOB_E_UNKNOWN_ERROR

        return jobStatus, errCode, errorMsg
    # End - GetJobStatus


    #####################################################
    # [MLJob::GetTimeGranularity]
    #####################################################
    def GetTimeGranularity(self, defaultVal):
        return dxml.XMLTools_GetChildNodeTextAsBool(self.DataXMLNode, DATA_TIME_GRANULARITY_ELEMENT_NAME, defaultVal)
    # End - GetTimeGranularity


    #####################################################
    # [MLJob::GetTrainingParamStr]
    #####################################################
    def GetTrainingParamStr(self, valName, defaultVal):
        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.TrainingXMLNode, valName, defaultVal)
        if ((resultStr is None) or (resultStr == "")):
            return defaultVal
        return resultStr

    #####################################################
    # [MLJob::GetTrainingParamInt]
    #####################################################
    def GetTrainingParamInt(self, valName, defaultVal):
        return dxml.XMLTools_GetChildNodeTextAsInt(self.TrainingXMLNode, valName, defaultVal)

    #####################################################
    # [MLJob::GetNetworkLayerSpec]
    #####################################################
    def GetNetworkLayerSpec(self, name):
        return dxml.XMLTools_GetChildNode(self.NetworkXMLNode, name)

    #####################################################
    # [MLJob::OKToUseGPU]
    #####################################################
    def OKToUseGPU(self):
        return self.AllowGPU

    #####################################################
    # [MLJob::GetDebug]
    #####################################################
    def GetDebug(self):
        return self.Debug

    #####################################################
    # [MLJob::GetIsLogisticNetwork]
    #####################################################
    def GetIsLogisticNetwork(self):
        return self.IsLogisticNetwork

    #####################################################
    # [MLJob::GetEpochNum]
    #####################################################
    def GetEpochNum(self):
        return self.CurrentEpochNum

    #####################################################
    # [MLJob::GetNumResultClasses]
    #####################################################
    def GetNumResultClasses(self):
        return self.NumResultClasses

    #####################################################
    # [MLJob::GetNumSequencesTrainedPerEpoch
    #####################################################
    def GetNumSequencesTrainedPerEpoch(self):
        return self.NumSamplesTrainedPerEpoch

    #####################################################
    # [MLJob::GetNumTimelinesSkippedPerEpoch
    #####################################################
    def GetNumTimelinesSkippedPerEpoch(self):
        return self.NumTimelinesSkippedPerEpoch

    #####################################################
    # [MLJob::SetNumTimelinesSkippedPerEpoch
    #####################################################
    def SetNumTimelinesSkippedPerEpoch(self, num):
        self.NumTimelinesSkippedPerEpoch = num

    #####################################################
    # [MLJob::GetNumTimelinesTrainedPerEpoch
    #####################################################
    def GetNumTimelinesTrainedPerEpoch(self):
        return self.NumTimelinesTrainedPerEpoch

    #####################################################
    # [MLJob::SetNumTimelinesTrainedPerEpoch
    #####################################################
    def SetNumTimelinesTrainedPerEpoch(self, num):
        self.NumTimelinesTrainedPerEpoch = num

    #####################################################
    # [MLJob::GetNumDataPointsPerEpoch
    #####################################################
    def GetNumDataPointsPerEpoch(self):
        return self.NumDataPointsTrainedPerEpoch

    #####################################################
    # [MLJob::SetNumDataPointsPerEpoch
    #####################################################
    def SetNumDataPointsPerEpoch(self, num):
        self.NumDataPointsTrainedPerEpoch = num

    #####################################################
    # [MLJob::GetNumSequencesTested
    #####################################################
    def GetNumSequencesTested(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[subGroupNum].NumSamplesTested
        else:
            return self.AllTestResults.NumSamplesTested

    #####################################################
    # [MLJob::SetDebug]
    #####################################################
    def SetDebug(self, fDebug):
        self.Debug = fDebug
        if (fDebug):
            textStr = "true"
        else:
            textStr = "false"
        dxml.XMLTools_AddChildNodeWithText(self.JobControlXMLNode, JOB_CONTROL_DEBUG_ELEMENT_NAME, textStr)
    # End - SetDebug

    #####################################################
    # [MLJob::GetMeanAbsoluteError
    #####################################################
    def GetMeanAbsoluteError(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            if (self.TestResultsSubgroupList[subGroupNum].NumPredictions <= 0):
                return 0
            return (self.TestResultsSubgroupList[subGroupNum].TotalAbsoluteError / self.TestResultsSubgroupList[subGroupNum].NumPredictions)
        else:
            if (self.AllTestResults.NumPredictions <= 0):
                return 0
            return (self.AllTestResults.TotalAbsoluteError / self.AllTestResults.NumPredictions)
    # End - GetMeanAbsoluteError

    #####################################################
    # [MLJob::GetPredictedAndTrueTestResults
    #####################################################
    def GetPredictedAndTrueTestResults(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[subGroupNum].AllPredictions, self.TestResultsSubgroupList[subGroupNum].AllTrueResults
        else:
            return self.AllTestResults.AllPredictions, self.AllTestResults.AllTrueResults
    # End - GetPredictedAndTrueTestResults


    #####################################################
    # [MLJob::GetAvgLossPerEpochList
    #####################################################
    def GetAvgLossPerEpochList(self):
        return self.AvgLossPerEpochList

    #####################################################
    # [MLJob::GetResultValMinValue
    #####################################################
    def GetResultValMinValue(self):
        return self.ResultValMinValue

    #####################################################
    # [MLJob::GetResultValBucketSize
    #####################################################
    def GetResultValBucketSize(self):
        return self.ResultValBucketSize

    #####################################################
    # [MLJob::GetTrainNumItemsPerClass
    #####################################################
    def GetTrainNumItemsPerClass(self):
        return self.TrainNumItemsPerClass

    #####################################################
    # [MLJob::GetTestResults
    #####################################################
    def GetTestResults(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[subGroupNum].TestResults
        else:
            return self.AllTestResults.TestResults

    #####################################################
    # [MLJob::GetTestNumItemsPerClass
    #####################################################
    def GetTestNumItemsPerClass(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[subGroupNum].TestNumItemsPerClass
        else:
            return self.AllTestResults.TestNumItemsPerClass

    #####################################################
    # [MLJob::GetROCAUC
    #####################################################
    def GetROCAUC(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[subGroupNum].ROCAUC
        else:
            return self.AllTestResults.ROCAUC

    #####################################################
    # [MLJob::GetAUPRC
    #####################################################
    def GetAUPRC(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[subGroupNum].AUPRC
        else:
            return self.AllTestResults.AUPRC

    #####################################################
    # [MLJob::GetF1Score
    #####################################################
    def GetF1Score(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[subGroupNum].F1Score
        else:
            return self.AllTestResults.F1Score

    #####################################################
    # [MLJob::GetTestNumCorrectPerClass
    #####################################################
    def GetTestNumCorrectPerClass(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[subGroupNum].TestNumCorrectPerClass
        else:
            return self.AllTestResults.TestNumCorrectPerClass

    #####################################################
    # [MLJob::GetTestNumPredictionsPerClass
    #####################################################
    def GetTestNumPredictionsPerClass(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[subGroupNum].TestNumPredictionsPerClass
        else:
            return self.AllTestResults.TestNumPredictionsPerClass

    #####################################################
    # [MLJob::GetStartRequestTimeStr]
    #####################################################
    def GetStartRequestTimeStr(self):
        return self.StartRequestTimeStr

    #####################################################
    # [MLJob::GetStopRequestTimeStr]
    #####################################################
    def GetStopRequestTimeStr(self):
        return self.StopRequestTimeStr

    #####################################################
    # [MLJob::GetLogisticResultsTrueValueList]
    #####################################################
    def GetLogisticResultsTrueValueList(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[subGroupNum].LogisticResultsTrueValueList
        else:
            return self.AllTestResults.LogisticResultsTrueValueList

    #####################################################
    # [MLJob::GetLogisticResultsPredictedProbabilityList]
    #####################################################
    def GetLogisticResultsPredictedProbabilityList(self, subGroupNum):
        if ((subGroupNum >= 0) and (subGroupNum < self.NumResultsSubgroups)):
            return self.TestResultsSubgroupList[subGroupNum].LogisticResultsPredictedProbabilityList
        else:
            return self.AllTestResults.LogisticResultsPredictedProbabilityList


    #####################################################
    #
    # [MLJob::GetNetworkStateSize]
    #
    #####################################################
    def GetNetworkStateSize(self):
        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.NetworkXMLNode, NETWORK_STATE_SIZE_ELEMENT_NAME, "")
        if ((resultStr is None) or (resultStr == "")):
            return 0

        try:
            resultInt = int(resultStr)
        except Exception:
            resultInt = 0

        return resultInt
    # End of GetNetworkStateSize



    #####################################################
    #
    # [MLJob::GetJobControlStr]
    #
    # Returns one parameter to the <JobControl> node.
    # This is a public procedure.
    #####################################################
    def GetJobControlStr(self, valName, defaultVal):
        xmlNode = dxml.XMLTools_GetChildNode(self.JobControlXMLNode, valName)
        if (xmlNode is None):
            return defaultVal

        resultStr = dxml.XMLTools_GetTextContents(xmlNode)
        resultStr = resultStr.lstrip()
        if ((resultStr is None) or (resultStr == "")):
            return defaultVal

        return resultStr
    # End of GetJobControlStr


    #####################################################
    #
    # [MLJob::SetJobControlStr]
    #
    # Updates one parameter to the <JobControl> node.
    # This is a public procedure.
    #####################################################
    def SetJobControlStr(self, valName, valueStr):
        xmlNode = dxml.XMLTools_GetChildNode(self.JobControlXMLNode, valName)
        if (xmlNode is None):
            xmlNode = self.JobXMLDOM.createElement(valName)
            self.JobControlXMLNode.appendChild(xmlNode)

        dxml.XMLTools_RemoveAllChildNodes(xmlNode)
        textNode = self.JobXMLDOM.createTextNode(valueStr)
        xmlNode.appendChild(textNode)
    # End of SetJobControlStr


    #####################################################
    #
    # [MLJob::GetDataParam]
    #
    # Returns one parameter to the <Data> node.
    # This is a public procedure.
    #####################################################
    def GetDataParam(self, valName, defaultVal):
        xmlNode = dxml.XMLTools_GetChildNode(self.DataXMLNode, valName)
        if (xmlNode is None):
            return defaultVal

        resultStr = dxml.XMLTools_GetTextContents(xmlNode)
        resultStr = resultStr.lstrip().rstrip()
        if ((resultStr is None) or (resultStr == "")):
            return defaultVal

        return resultStr
    # End of GetDataParam



    #####################################################
    #
    # [MLJob::GetNetworkInputVarNames]
    #
    #####################################################
    def GetNetworkInputVarNames(self):
        resultStr = dxml.XMLTools_GetChildNodeTextAsStr(self.NetworkInputXMLNode, NETWORK_INPUT_VALUES_ELEMENT_NAME, "")
        if (resultStr is None):
            return ""

        # Allow whitespace to be sprinkled around the file. Later the parsing code
        # assumes no unnecessary whitespace is present, but don't be that strict with the file format.
        return resultStr.replace(' ', '')
    # End of GetNetworkInputVarNames



    #####################################################
    #
    # [MLJob::GetInputCriteriaVarList]
    #
    #####################################################
    def GetInputCriteriaVarList(self):
        criteriaStr = dxml.XMLTools_GetChildNodeTextAsStr(self.NetworkInputXMLNode, NETWORK_INPUT_CRITERIA_TEST_ELEMENT_NAME, "")
        if (criteriaStr == ""):
            return []

        partsList = criteriaStr.split(" ")
        if (len(partsList) < 3):
            return []

        varName = partsList[0].lstrip().rstrip()
        return [ varName ]
    # End of GetInputCriteriaVarList




    #####################################################
    #
    # [MLJob::GetInputCriteriaInfo]
    #
    # This returns:
    #   fFoundIt, varName, relationID, value1, value2
    #####################################################
    def GetInputCriteriaInfo(self):
        fValid = False
        varName = ""
        relation = ""
        value1 = tdf.TDF_INVALID_VALUE
        value2 = tdf.TDF_INVALID_VALUE

        criteriaStr = dxml.XMLTools_GetChildNodeTextAsStr(self.NetworkInputXMLNode, NETWORK_INPUT_CRITERIA_TEST_ELEMENT_NAME, "")
        if (criteriaStr == ""):
            return False, "", "", tdf.TDF_INVALID_VALUE, tdf.TDF_INVALID_VALUE

        partsList = criteriaStr.split(" ")
        if (len(partsList) < 3):
            return False, "", "", tdf.TDF_INVALID_VALUE, tdf.TDF_INVALID_VALUE

        varName = partsList[0].lstrip().rstrip()
        relationStr = partsList[1].lstrip().rstrip().lower()
        valueStr = partsList[2].lstrip().rstrip()
        ##########################################
        # Conditions may be "foo GT x" or else "foo in x:y". This affects how we parse
        # the value.
        if (relationStr == VALUE_RELATION_IN_RANGE):
            if (":" not in valueStr):
                return False, "", "", tdf.TDF_INVALID_VALUE, tdf.TDF_INVALID_VALUE

            valPartsList = valueStr.split(":")
            if (len(valPartsList) < 2):
                return False, "", "", tdf.TDF_INVALID_VALUE, tdf.TDF_INVALID_VALUE

            try:
                value1 = float(valPartsList[0])
            except Exception:
                return False, "", "", tdf.TDF_INVALID_VALUE, tdf.TDF_INVALID_VALUE

            try:
                value2 = float(valPartsList[1])
            except Exception:
                return False, "", "", tdf.TDF_INVALID_VALUE, tdf.TDF_INVALID_VALUE
        ##########################################
        else:
            try:
                value1 = float(valueStr)
            except Exception:
                return False, "", "", tdf.TDF_INVALID_VALUE, tdf.TDF_INVALID_VALUE

        if (relationStr not in g_NameToRelationIDDict):
            return False, "", "", tdf.TDF_INVALID_VALUE, tdf.TDF_INVALID_VALUE

        relationID = g_NameToRelationIDDict[relationStr]
        return True, varName, relationID, value1, value2
    # End of GetInputCriteriaInfo






    #####################################################
    #
    # [MLJob::GetNetworkOutputType]
    #
    #####################################################
    def GetNetworkOutputType(self):
        # Don't compute this twice. Reuse previous values
        if (tdf.TDF_DATA_TYPE_UNKNOWN != self.ResultValueType):
            return self.ResultValueType

        outputSourceStr = dxml.XMLTools_GetChildNodeTextAsStr(self.NetworkOutputXMLNode, NETWORK_OUTPUT_SOURCE_ELEMENT_NAME, NETWORK_OUTPUT_SOURCE_VALUE)
        outputSourceStr = outputSourceStr.lower()
        if (outputSourceStr == NETWORK_OUTPUT_SOURCE_TEST_LOGISTIC):
            self.IsLogisticNetwork = True
            self.ResultValueType = tdf.TDF_DATA_TYPE_BOOL
            return tdf.TDF_DATA_TYPE_BOOL
        elif (outputSourceStr == NETWORK_OUTPUT_SOURCE_TEST_CATEGORY):
            self.IsLogisticNetwork = False
            self.ResultValueType = tdf.TDF_DATA_TYPE_BOOL
            return tdf.TDF_DATA_TYPE_BOOL
        elif (outputSourceStr != NETWORK_OUTPUT_SOURCE_VALUE):
            return tdf.TDF_DATA_TYPE_FLOAT

        varName = dxml.XMLTools_GetChildNodeTextAsStr(self.NetworkOutputXMLNode, NETWORK_OUTPUT_VALUE_ELEMENT_NAME, "")
        if (varName == ""):
            return tdf.TDF_DATA_TYPE_FLOAT

        return tdf.TDF_GetVariableType(varName)
    # End of GetNetworkOutputType




    #####################################################
    #
    # [MLJob::GetNetworkOutputVarName]
    #
    #####################################################
    def GetNetworkOutputVarName(self):
        outputSource = dxml.XMLTools_GetChildNodeTextAsStr(self.NetworkOutputXMLNode, NETWORK_OUTPUT_SOURCE_ELEMENT_NAME, NETWORK_OUTPUT_SOURCE_VALUE)
        outputValueStr = dxml.XMLTools_GetChildNodeTextAsStr(self.NetworkOutputXMLNode, NETWORK_OUTPUT_VALUE_ELEMENT_NAME, "")
        if (outputValueStr == ""):
            return ""

        outputSource = outputSource.lower()
        if (outputSource == NETWORK_OUTPUT_SOURCE_VALUE):
            return outputValueStr
        elif (outputSource in [NETWORK_OUTPUT_SOURCE_TEST_LOGISTIC, NETWORK_OUTPUT_SOURCE_TEST_CATEGORY]):
            partsList = outputValueStr.split(" ")
            if (len(partsList) < 3):
                return ""
            return partsList[0].lstrip().rstrip()

        return ""
    # End of GetNetworkOutputVarName





    #####################################################
    #
    # [MLJob::GetNetworkOutputInfo]
    #
    # This returns:
    #   fFoundIt, outputSourceID, varName, relationID, value1, value2, whenTimeID
    #####################################################
    def GetNetworkOutputInfo(self):
        fValid = False
        outputSourceStr = None
        outputSourceID = -1
        varName = None
        relationStr = None
        relationID = -1
        value1 = -1
        value2 = -1
        whenTimeID = -1

        outputSourceStr = dxml.XMLTools_GetChildNodeTextAsStr(self.NetworkOutputXMLNode, NETWORK_OUTPUT_SOURCE_ELEMENT_NAME, NETWORK_OUTPUT_SOURCE_VALUE)
        outputSourceStr = outputSourceStr.lower()
        if (outputSourceStr not in g_NameToSourceIDDict):
            return False, outputSourceID, varName, relationID, value1, value2, whenTimeID
        outputSourceID = g_NameToSourceIDDict[outputSourceStr]

        outputValueStr = dxml.XMLTools_GetChildNodeTextAsStr(self.NetworkOutputXMLNode, NETWORK_OUTPUT_VALUE_ELEMENT_NAME, "")
        if (outputValueStr == ""):
            return False, outputSourceID, varName, relationID, value1, value2, whenTimeID

        whenTimeStr = dxml.XMLTools_GetChildNodeTextAsStr(self.NetworkOutputXMLNode, NETWORK_OUTPUT_WHEN_ELEMENT_NAME, "")
        if (whenTimeStr not in g_NameToWhenIDDict):
            return False, outputSourceID, varName, relationID, value1, value2, whenTimeID
        whenTimeID = g_NameToWhenIDDict[whenTimeStr]

        #############################
        if (outputSourceID == NETWORK_OUTPUT_SOURCE_VALUE_ID):
            varName = outputValueStr
            return True, outputSourceID, varName, relationID, value1, value2, whenTimeID

        #############################
        if (outputSourceID in [NETWORK_OUTPUT_SOURCE_TEST_LOGISTIC_ID, NETWORK_OUTPUT_SOURCE_TEST_CATEGORY_ID]):
            partsList = outputValueStr.split(" ")
            if (len(partsList) < 3):
                return False, outputSourceID, varName, relationID, value1, value2, whenTimeID

            # Case-normalize the relation for comparisons, but leave the variable name case-sensitive.
            varName = partsList[0].lstrip().rstrip()
            relationStr = partsList[1].lstrip().rstrip().lower()
            valueStr = partsList[2].lstrip().rstrip()

            if (relationStr not in g_NameToRelationIDDict):
                return False, outputSourceID, varName, relationID, value1, value2, whenTimeID
            relationID = g_NameToRelationIDDict[relationStr]

            # Conditions may be "foo GT x" or else "foo in x:y". 
            # This affects how we parse the value.
            if (relationID == tdf.VALUE_RELATION_IN_RANGE_ID):
                if (":" not in valueStr):
                    return False, outputSourceID, varName, relationID, value1, value2, whenTimeID

                valPartsList = valueStr.split(":")
                if (len(valPartsList) < 2):
                    return False, outputSourceID, varName, relationID, value1, value2, whenTimeID

                try:
                    value1 = float(valPartsList[0])
                except Exception:
                    return False, outputSourceID, varName, relationID, value1, value2, whenTimeID

                try:
                    value2 = float(valPartsList[1])
                except Exception:
                    return False, outputSourceID, varName, relationID, value1, value2, whenTimeID
            # End - if (relation.lower() == VALUE_RELATION_IN_RANGE):
            else:
                try:
                    value1 = float(valueStr)
                except Exception:
                    return False, outputSourceID, varName, relationID, value1, value2, whenTimeID

            return True, outputSourceID, varName, relationID, value1, value2, whenTimeID
        # End - if (outputSourceID in [NETWORK_OUTPUT_SOURCE_TEST_LOGISTIC_ID, NETWORK_OUTPUT_SOURCE_TEST_CATEGORY_ID])


        return False, outputSourceID, varName, relationID, value1, value2, whenTimeID
    # End of GetNetworkOutputInfo






    #####################################################
    #
    # [MLJob::SetDataParam]
    #
    # Set one parameter to the <Data> node.
    # This is a public procedure.
    #####################################################
    def SetDataParam(self, valName, newVal):
        xmlNode = dxml.XMLTools_GetChildNode(self.DataXMLNode, valName)
        if (xmlNode is None):
            return JOB_E_UNKNOWN_ERROR

        dxml.XMLTools_SetTextContents(xmlNode, newVal)
        return JOB_E_NO_ERROR
    # End of SetDataParam






    #####################################################
    #
    # [MLJob::ParseConditionExpression]
    #
    # This is a public procedure.
    #####################################################
    def ParseConditionExpression(self, propertyListStr):
        numProperties = 0
        propertyRelationList = []
        propertyNameList = []
        propertyValueList = []

        if (propertyListStr != ""):
            propList = propertyListStr.split(VALUE_FILTER_LIST_SEPARATOR)
            for propNamePair in propList:
                #print("propNamePair=" + propNamePair)
                namePairParts = re.split("(.LT.|.LTE.|.EQ.|.NEQ.|.GTE.|.GT.)", propNamePair)
                if (len(namePairParts) == 3):
                    partStr = namePairParts[0]
                    partStr = partStr.replace(' ', '')
                    #print("propNamePair. Name=" + str(partStr))
                    propertyNameList.append(partStr)

                    partStr = namePairParts[1]
                    partStr = partStr.replace(' ', '')
                    # Tokens like ".GT. are case insensitive
                    partStr = partStr.upper()
                    #print("propNamePair. op=" + str(partStr))
                    propertyRelationList.append(partStr)

                    partStr = namePairParts[2]
                    partStr = partStr.replace(' ', '')
                    #print("propNamePair. value=" + str(partStr))
                    propertyValueList.append(partStr)

                    numProperties += 1
            # End - for propNamePair in propList:
        # End - if (requirePropertiesStr != ""):

        return numProperties, propertyRelationList, propertyNameList, propertyValueList
    # End - ParseConditionExpression


    ################################################################################
    #
    # [GetNonce]
    #
    ################################################################################
    def GetNonce(self):
        return self.RuntimeNonce
    # End - GetNonce


    ################################################################################
    #
    # [IncrementNonce]
    #
    ################################################################################
    def IncrementNonce(self):
        self.RuntimeNonce += 1
    # End - IncrementNonce


    ################################################################################
    #
    # [ChecksumExists]
    #
    ################################################################################
    def ChecksumExists(self, hashName):
        if (hashName in self.HashDict):
            return True
        return False
    # End - ChecksumExists


    ################################################################################
    #
    # [SetArrayChecksum]
    #
    # inputArray is a numpy array, and may be 1, 2, or 3 dimensional.
    ################################################################################
    def SetArrayChecksum(self, inputArray, hashName):
        if (numpy.isnan(inputArray).any()):
            print("ERROR!:\nSetArrayChecksum passed an Invalid Array")
            print("SetArrayChecksum. hashName = " + str(hashName))
            print("SetArrayChecksum. inputArray = " + str(inputArray))
            print("Exiting process...")
            raise Exception()

        hashVal = self.ComputeArrayChecksum(inputArray)
        #print("SetArrayChecksum. Save hash " + hashName + " = " + hashVal)
        self.HashDict[hashName] = hashVal
    # End - SetArrayChecksum



    ################################################################################
    #
    # [CompareArrayChecksum]
    #
    # inputArray is a numpy array, and may be 1, 2, or 3 dimensional.
    ################################################################################
    def CompareArrayChecksum(self, inputArray, hashName):
        newHashVal = self.ComputeArrayChecksum(inputArray)
        if (hashName not in self.HashDict):
            print("CompareArrayChecksum. hashName not in self.HashDict hashName = " + str(hashName))
            return False

        isEqual = (newHashVal == self.HashDict[hashName])
        return isEqual
    # End - CompareArrayChecksum




    ################################################################################
    #
    # [ComputeArrayChecksum]
    #
    # inputArray is a numpy array, and may be 1, 2, or 3 dimensional.
    ################################################################################
    def ComputeArrayChecksum(self, inputArray):
        if (numpy.isnan(inputArray).any()):
            print("ERROR!:\nComputeArrayChecksum passed an Invalid Array")
            print("ComputeArrayChecksum. inputArray = " + str(inputArray))
            print("Exiting process...")
            raise Exception()

        rawByteArray = inputArray.tobytes('C')
        newHashVal = hashlib.sha256(rawByteArray).hexdigest()
        return newHashVal
    # End - ComputeArrayChecksum



    ################################################################################
    #
    # [GetArrayChecksum]
    #
    ################################################################################
    def GetSavedArrayChecksum(self, hashName):
        if (hashName not in self.HashDict):
            return "NOT IN DICTIONARY"
        return self.HashDict[hashName]
    # End - GetSavedArrayChecksum


    #####################################################
    #
    # [MLJob::ResetRunStatus]
    #
    #####################################################
    def ResetRunStatus(self):
        # Discard Previous results
        dxml.XMLTools_RemoveAllChildNodes(self.ResultsXMLNode)
        self.ResultsPreflightXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, 
                                                                    RESULTS_PREFLIGHT_ELEMENT_NAME)
        self.ResultsTrainingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, 
                                                                    RESULTS_TRAINING_ELEMENT_NAME)
        self.ResultsTestingXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.ResultsXMLNode, 
                                                            RESULTS_TESTING_ELEMENT_NAME)
        self.AllTestResults.InitResultsXML(self.ResultsTestingXMLNode, 
                                                            RESULTS_TEST_ALL_TESTS_GROUP_XML_ELEMENT_NAME)
        for index in range(self.NumResultsSubgroups):
            testGroupName = RESULTS_TEST_TEST_SUBGROUP_XML_ELEMENT_NAME + str(index)
            self.TestResultsSubgroupList[index].InitResultsXML(self.ResultsTestingXMLNode, testGroupName)

        # Each request has a single test. When we finish the test, we have
        # finished the entire reqeust.
        self.SetJobControlStr(JOB_CONTROL_STATUS_ELEMENT_NAME, MLJOB_STATUS_IDLE)
        self.SetJobControlStr(JOB_CONTROL_RESULT_MSG_ELEMENT_NAME, "")
        self.SetJobControlStr(JOB_CONTROL_ERROR_CODE_ELEMENT_NAME, str(JOB_E_NO_ERROR))

        # Remove the Runtime state
        dxml.XMLTools_RemoveAllChildNodes(self.RuntimeXMLNode)

        # Discard previous results
        dxml.XMLTools_RemoveAllChildNodes(self.ResultsXMLNode)

        # Discard previous saved matrices
        dxml.XMLTools_RemoveAllChildNodes(self.SavedModelStateXMLNode)
        self.SavedModelStateXMLNode = dxml.XMLTools_GetOrCreateChildNode(self.RootXMLNode, 
                                                        SAVED_MODEL_STATE_ELEMENT_NAME)

        # Reset the log file if there is one.
        if (self.LogFilePathname != ""):
            try:
                os.remove(self.LogFilePathname) 
            except Exception:
                pass
        # End - if (self.LogFilePathname != ""):
    # End of ResetRunStatus


# End - class MLJob
################################################################################



################################################################################
#
# [MLJob_ConvertStringTo1DVector]
#
# This is used in both mlJob and also the MLJobTestResults subclass.
# So, it needs to be external to both classes.
################################################################################
def MLJob_ConvertStringTo1DVector(vectorStr):
    sectionList = vectorStr.split(";")
    matrixAllRowsStr = sectionList[len(sectionList) - 1]

    dimensionStr = ""
    for propertyStr in sectionList:
        propertyParts = propertyStr.split("=")
        if (len(propertyParts) < 2):
            continue

        propName = propertyParts[0]
        propValue = propertyParts[1]
        if (propName == "D"):
            dimensionStr = propValue
    # End - for propertyStr in sectionList:

    numCols = 0
    if (dimensionStr != ""):
        dimensionList = dimensionStr.split(VALUE_SEPARATOR_CHAR)
        if (len(dimensionList) > 0):
            numCols = int(dimensionList[0])

    newVector = numpy.empty([numCols])

    matrixValueStrList = matrixAllRowsStr.split(ROW_SEPARATOR_CHAR)
    for singleRowStr in matrixValueStrList:
        if (singleRowStr != ""):
            valueList = singleRowStr.split(VALUE_SEPARATOR_CHAR)
            colNum = 0
            for value in valueList:
                newVector[colNum] = float(value)
                colNum += 1
    # End - for singleRowStr in matrixValueStrList:

    return newVector
# End - MLJob_ConvertStringTo1DVector



################################################################################
#
# [MLJob_Convert1DVectorToString]
#
# This is used in both mlJob and also the MLJobTestResults subclass.
# So, it needs to be external to both classes.
################################################################################
def MLJob_Convert1DVectorToString(inputArray):
    dimension = len(inputArray)

    resultString = "NumD=1;D=" + str(dimension) + ";T=float;" + ROW_SEPARATOR_CHAR

    for numVal in inputArray:
        resultString = resultString + str(numVal) + VALUE_SEPARATOR_CHAR
    resultString = resultString[:-1]
    resultString = resultString + ROW_SEPARATOR_CHAR

    return resultString
# End - MLJob_Convert1DVectorToString





################################################################################
# 
# This is a public procedure.
################################################################################
def MLJob_CreateNewMLJob():
    job = MLJob()
    job.InitNewJobImpl()

    return job
# End - MLJob_CreateNewMLJob




################################################################################
# 
# This is a public procedure.
################################################################################
def MLJob_CreateMLJobFromString(jobStr):
    job = MLJob()
    err = job.ReadJobFromString(jobStr)
    if (err != JOB_E_NO_ERROR):
        job = None

    return job
# End - MLJob_CreateMLJobFromString




################################################################################
# 
# This is a public procedure.
#
# Returns:    err, job
################################################################################
def MLJob_ReadExistingMLJob(jobFilePathName):
    job = MLJob()
    err = job.ReadJobFromFile(jobFilePathName)
    if (err != JOB_E_NO_ERROR):
        #print("MLJob_ReadExistingMLJob. err = " + str(err))
        return err, None

    return JOB_E_NO_ERROR, job
# End - MLJob_ReadExistingMLJob







