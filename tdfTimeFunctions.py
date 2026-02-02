#####################################################################################
# 
# Copyright (c) 2022-2026 Dawson Dean
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
# Time-Based Derived Values - Make derived values from existing values across time
#
# Each of these is a state-ful object that takes a time ordered sequence of input
# values and outputs a computed value.
# It ASSUMES inputs are passed in in increasing time order, so pass in the values 
# at time t-1 before time t.
#
# The functions are identified by Case-INsensitive names:
#
# "delta" - Returns a float, the delta between current and most recent previous value
# It also allows you to specify how long a timespan to use for the rate:
#       delta - the current value and the most recent previous value
#       delta3 - the current value and a previous value from 3 days before
#       delta7 - the current value and a previous value from 7 days before
#       delta14 - the current value and a previous value from 14 days before
#       delta30 - the current value and a previous value from 30 days before
#       delta60 - the current value and a previous value from 60 days before
#       delta90 - the current value and a previous value from 90 days before
#       delta180 - the current value and a previous value from 180 days before
#
# "rate" - Returns a float, the rate over time between current and most recent previous value. 
# This is "delta" divided by the number of days between the two values.
# It also allows you to specify how long a timespan to use for the rate:
#       rate - the current value and the most recent previous value
#       rate3 - the current value and a previous value from 3 days before
#       rate7 - the current value and a previous value from 7 days before
#       rate14 - the current value and a previous value from 14 days before
#       rate30 - the current value and a previous value from 30 days before
#       rate60 - the current value and a previous value from 60 days before
#       rate90 - the current value and a previous value from 90 days before
#       rate180 - the current value and a previous value from 180 days before
#
# "accel" - Returns a float, the accelleration over time across the current and 2 most recent 
# previous values. This is "rate" divided by the number of days between the two values.
# It also allows you to specify how long a timespan to use for the accelleration:
#       accel - the current value and the most recent previous value
#       accel3 - the current value and a previous value from 3 days before
#       accel7 - the current value and a previous value from 7 days before
#       accel14 - the current value and a previous value from 14 days before
#       accel30 - the current value and a previous value from 30 days before
#       accel60 - the current value and a previous value from 60 days before
#       accel90 - the current value and a previous value from 90 days before
#       accel180 - the current value and a previous value from 180 days before
#
# "percentchange" - Returns a float, the relative change between current and most recent 
# previous value. This is ((newVal - oldValue) / oldValue)
# It also allows you to specify how long a timespan to use for the rate:
#       percentchange - the current value and the most recent previous value
#       percentchange7 - the current value and a previous value from 7 days before
#       percentchange14 - the current value and a previous value from 14 days before
#       percentchange30 - the current value and a previous value from 30 days before
#       percentchange60 - the current value and a previous value from 60 days before
#       percentchange90 - the current value and a previous value from 90 days before
#       percentchange180 - the current value and a previous value from 180 days before
#
# "isstable" - Returns a boolean that describes whether all values in the last time
# period have been within a range of 0.3
# It also allows you to specify how long a timespan to use
#       isstable - the current value and the most recent previous value
#       isstable7 - the current value and all previous values from the past 7 days
#       isstable14 - the current value and all previous values from the past 14 days
#       isstable30 - the current value and all previous values from the past 30 days
#       isstable60 - the current value and all previous values from the past 60 days
#       isstable90 - the current value and all previous values from the past 90 days
#       isstable180 - the current value and all previous values from the past 180 days
#
# "runavg" - Returns a float, the running average of all recent values within the past N days
#   By default N is 60    
#
# "bollup" - Returns a bool, whether the current value is >= the upper Bollinger band.
#   Bollinger band computed with all values in past N days. By default N is 60    
#
# "bolllow" - Returns a bool, whether the current value is <= the lower Bollinger band.
#   Bollinger band computed with all values in past N days. By default N is 60    
#
# "range" - Returns a float, the range between min and max recent values within the past N days
# It also allows you to specify how long a timespan to use
#       range - the current value and all previous values from the past 3 days
#       range7 - the current value and all previous values from the past 7 days
#       range14 - the current value and all previous values from the past 14 days
#       range30 - the current value and all previous values from the past 30 days
#       range60 - the current value and all previous values from the past 60 days
#       range90 - the current value and all previous values from the past 90 days
#       range180 - the current value and all previous values from the past 180 days
#
# "relrange" - Returns a float, the relative range between min and max recent values within the past N days
# This is similar to "percentchange", except it uses the min and max values of the time period, rather
# than the earliest and latest values. This is ((maxVal - minValue) / minValue)
# It also allows you to specify how long a timespan to use for the rate:
#       relrange - the current value and all previous values from the past 3 days
#       relrange7 - the current value and all previous values from the past 7 days
#       relrange14 - the current value and all previous values from the past 14 days
#       relrange30 - the current value and all previous values from the past 30 days
#       relrange60 - the current value and all previous values from the past 60 days
#       relrange90 - the current value and all previous values from the past 90 days
#       relrange180 - the current value and all previous values from the past 180 days
#
# "faster30than90" - Returns a Bool, the rate of change over the past 30 days is faster than
# that over the past 90 days.

################################################################################

from collections import deque
import statistics

import tdfFile as tdf


################################################################################
# This is used for computing Baselines
################################################################################
class CTimeSeries():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, timeGranularity, maxHistoryInTime):
        self.TimeGranularity = timeGranularity
        self.ValueQueue = deque()

        self.maxHistoryInTime = maxHistoryInTime
        self.maxHistoryInItems = 100
        self.lowestValue = tdf.TDF_INVALID_VALUE

        self.MostRecentValue = tdf.TDF_INVALID_VALUE
        self.MostRecentTime = -1

        self.OldestTime = -1
    # End -  __init__



    #####################################################
    #
    # [CTimeSeries::
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return
    # End of destructor



    #####################################################
    #
    # [CTimeSeries::AddNewValue]
    #
    #####################################################
    def AddNewValue(self, value, timeInDays, timeHours, timeMin, timeSecs):
        fNeedToFindLowestValue = False

        if (self.TimeGranularity == tdf.TDF_TIME_GRANULARITY_DAYS):
            timeCode = timeInDays
        else:                
            timeCode = tdf.TDF_ConvertTimeToSeconds(timeInDays, timeSecs)

        newQueueEntry = {'v': value, 't': timeCode}
        self.ValueQueue.append(newQueueEntry)
        self.MostRecentValue = round(float(value), 2)
        self.MostRecentTime = timeCode

        if ((self.lowestValue == tdf.TDF_INVALID_VALUE) or (value < self.lowestValue)):
            self.lowestValue = value

        if ((self.OldestDay == -1) and (self.OldestHour == -1) and (self.OldestMin == -1) and (self.OldestSec == -1)):
            self.OldestTime = timeCode
        else:
            # Trim the queue
            deltaTime = timeCode - self.OldestTime
            while ((deltaTime > self.maxHistoryInTime)
                    or (len(self.ValueQueue) > self.maxHistoryInItems)):
                removedValue = self.ValueQueue[0]
                self.ValueQueue.popleft()

                # If we removed the smallest value, then we need to search through
                # the list for a new smallest value
                if (round(removedValue['v'], 2) == round(self.lowestValue, 2)):
                    fNeedToFindLowestValue = True

                oldestValue = self.ValueQueue[0]
                self.OldestTime = oldestValue['t']

                deltaTime = timeInDays - self.OldestDay
            # End - while (deltaTime > self.maxHistoryInTime) or (len(self.ValueQueue) > self.maxHistoryInItems)):


            if (fNeedToFindLowestValue):
                # iterate over the deque's elements
                self.lowestValue = -1
                for elem in self.ValueQueue:
                    currentVal = round(elem['v'], 2)
                    if ((self.lowestValue == -1) or (currentVal < self.lowestValue)):
                        self.lowestValue = currentVal
                # End - for elem in self.ValueQueue:
            # End - if (fNeedToFindLowestValue):
        # else               
    # End of AddNewValue



    #####################################################
    #
    # [CTimeSeries::GetLowestValue]
    #
    #####################################################
    def GetLowestValue(self):
        if (self.MostRecentValue == -1):
            return None

        return self.lowestValue
    # End of GetLowestValue



    #####################################################
    #
    # [CTimeSeries::ValueHasIncreased]
    #
    #####################################################
    def ValueHasIncreased(self, deltaValue):
        if (self.MostRecentValue == -1):
            return False

        if (self.MostRecentValue >= round((self.lowestValue + deltaValue), 2)):
            return True

        return False
    # End of ValueHasIncreased

# End - class CTimeSeries








################################################################################
#
#
################################################################################
class CTimeFunctionBaseClass():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, timeGranularity, numDays):
        self.TimeGranularity = timeGranularity
        self.MaxTimeInQueue = numDays
        self.ValueQueue = deque()
    # End -  __init__


    #####################################################
    #
    # [CTimeFunctionBaseClass::PruneOldValues]
    #
    #####################################################
    def PruneOldValues(self, newTimeCode):
        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((newTimeCode - self.ValueQueue[0]['t']) >= self.MaxTimeInQueue):
                self.ValueQueue.popleft()
            else:
                break
        # End - while (True):
    # End of PruneOldValues

# End - class CTimeFunctionBaseClass









################################################################################
#
# This is a generiv series 
################################################################################
class CGenericTimeValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, timeGranularity):
        self.TimeGranularity = timeGranularity
        self.PrevValue = None
        self.CurrentValue = None

        self.Reset()
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.CurrentValue = None
        self.PrevValue = None
    # End -  Reset


    #####################################################
    #
    # [CGenericTimeValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, timeInDays, timeSeconds):
        if (self.TimeGranularity == tdf.TDF_TIME_GRANULARITY_DAYS):
            timeCode = timeInDays
        else:                
            timeCode = tdf.TDF_ConvertTimeToSeconds(timeInDays, timeSeconds)

        newValInfo = {'v': value, 't': timeCode}
        self.PrevValue = self.CurrentValue
        self.CurrentValue = newValInfo
        if (self.PrevValue is None):
            return tdf.TDF_INVALID_VALUE

        deltaValue = value - self.PrevValue['v']
        deltaTime = timeCode - self.PrevValue['t']
        if (deltaTime <= 0):
            return tdf.TDF_INVALID_VALUE

        rate = float(deltaValue / deltaTime)
        return rate
    # End of ComputeNewValue

# End - class CGenericTimeValue









################################################################################
#
#
################################################################################
class CAccelerationValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, timeGranularity, numDays):
        self.TimeGranularity = timeGranularity
        self.MaxTimeInQueue = numDays
        self.Reset()
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
    # End -  Reset


    #####################################################
    #
    # [CAccelerationValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, timeInDays, timeSeconds):
        if (self.TimeGranularity == tdf.TDF_TIME_GRANULARITY_DAYS):
            timeCode = timeInDays
        else:                
            timeCode = tdf.TDF_ConvertTimeToSeconds(timeInDays, timeSeconds)

        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((timeCode - self.ValueQueue[0]['t']) >= self.MaxTimeInQueue):
                self.ValueQueue.popleft()
            else:
                break
        # End - while (True):

        # Compute the current rate. This will then be used to later
        # compute the accelleration.
        deltaValue = -1
        deltaTime = -1
        for entry in self.ValueQueue:
            currentDeltaValue = abs(value - entry['v'])

            if ((deltaValue == -1) or (currentDeltaValue > deltaValue)):
                deltaValue = currentDeltaValue
                deltaTime = timeCode - entry['t']
        # End - for elem in self.ValueQueue:

        # <> Use the full time span, even though the range may be in a subset
        newRate = 0.0
        if (len(self.ValueQueue) >= 1):
            deltaTime = timeCode - self.ValueQueue[0]['t']
            if (deltaTime > 0):
                newRate = abs(float(deltaValue / deltaTime))
        # End - if (len(self.ValueQueue) >= 1):
        
        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 't': timeCode, 'r': newRate})

        # A list with only 2 items cannot have an accelleration.
        if (len(self.ValueQueue) <= 2):
            return tdf.TDF_INVALID_VALUE    

        # Get the oldest and newest rates.
        # We are NOT looking for the min and max rates, but rather the rates at the
        # beginning and end of the sliding window. We are using increasing sizes in
        # the sliding window to moderate the effect of a big change in rate.
        deltaTime = timeCode - self.ValueQueue[0]['t']
        deltaRate = newRate - self.ValueQueue[0]['r'] 

        if (deltaTime <= 0):
            return tdf.TDF_INVALID_VALUE

        acceleration = abs(float(deltaRate / deltaTime))
        return acceleration
    # End of ComputeNewValue

# End - class CAccelerationValue





################################################################################
#
#
################################################################################
class CDeltaValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, timeGranularity, numDays, varName):
        self.TimeGranularity = timeGranularity
        self.MaxTimeInQueue = numDays
        self.Reset()
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return

    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
    # End -  Reset


    #####################################################
    #
    # [CDeltaValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, timeInDays, timeSeconds):
        if (self.TimeGranularity == tdf.TDF_TIME_GRANULARITY_DAYS):
            timeCode = timeInDays
        else:                
            timeCode = tdf.TDF_ConvertTimeToSeconds(timeInDays, timeSeconds)

        # Pop any values that are older than we need.
        while (len(self.ValueQueue) > 0):
            if ((timeCode - self.ValueQueue[0]['t']) >= self.MaxTimeInQueue):
                self.ValueQueue.popleft()
            else:
                break
        # End - while (len(self.ValueQueue) > 2):

        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 't': timeCode})
           
        # A list with only 1 items cannot have a delta
        if (len(self.ValueQueue) <= 1):
            return tdf.TDF_INVALID_VALUE    

        # Normally, this is an old entry, but it may also be the entry
        # we just added if the queue is just starting up.
        oldestEntry = self.ValueQueue[0]

        if ((timeCode - oldestEntry['t']) < 1):
            return tdf.TDF_INVALID_VALUE

        deltaValue = float(value - oldestEntry['v'])
        return deltaValue
    # End of ComputeNewValue

# End - class CDeltaValue






################################################################################
#
#
################################################################################
class CSum():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, timeGranularity, numDays, varName):
        self.TimeGranularity = timeGranularity
        self.ValueQueue = deque()
        self.TotalValue = 0
        self.MaxTimeInQueue = numDays
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
        self.TotalValue = 0
    # End -  Reset


    #####################################################
    #
    # [CRunningAvgValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, timeInDays, timeSeconds):
        if (self.TimeGranularity == tdf.TDF_TIME_GRANULARITY_DAYS):
            timeCode = timeInDays
        else:                
            timeCode = tdf.TDF_ConvertTimeToSeconds(timeInDays, timeSeconds)

        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((timeCode - self.ValueQueue[0]['t']) >= self.MaxTimeInQueue):
                self.TotalValue = self.TotalValue - self.ValueQueue[0]['v']
                self.ValueQueue.popleft()
            else:
                break
        # End - while (True):

        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 't': timeCode})
        self.TotalValue += value

        if (len(self.ValueQueue) > 0):
            sumVal = float(self.TotalValue)
        else:
            sumVal = tdf.TDF_INVALID_VALUE

        return sumVal
    # End of ComputeNewValue

# End - class CSum







################################################################################
#
#
################################################################################
class CRunningAvgValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, timeGranularity, numDays):
        self.TimeGranularity = timeGranularity
        self.MaxTimeInQueue = numDays
        self.Reset()
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
        self.TotalValue = 0
    # End -  Reset


    #####################################################
    #
    # [CRunningAvgValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, timeInDays, timeSeconds):
        if (self.TimeGranularity == tdf.TDF_TIME_GRANULARITY_DAYS):
            timeCode = timeInDays
        else:                
            timeCode = tdf.TDF_ConvertTimeToSeconds(timeInDays, timeSeconds)

        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((timeCode - self.ValueQueue[0]['t']) >= self.MaxTimeInQueue):
                self.TotalValue = self.TotalValue - self.ValueQueue[0]['v']
                self.ValueQueue.popleft()
            else:
                break
        # End - while (True):

        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 't': timeCode})
        self.TotalValue += value

        if (len(self.ValueQueue) > 0):
            avgValue = float(self.TotalValue / len(self.ValueQueue))
        else:
            avgValue = tdf.TDF_INVALID_VALUE

        return avgValue
    # End of ComputeNewValue

# End - class CRunningAvgValue








################################################################################
#
#
################################################################################
class CRateValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, timeGranularity, numDays):
        self.TimeGranularity = timeGranularity
        self.MaxTimeInQueue = numDays
        self.Reset()
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
    # End -  Reset


    #####################################################
    #
    # [CRateValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, timeInDays, timeSeconds):
        if (self.TimeGranularity == tdf.TDF_TIME_GRANULARITY_DAYS):
            timeCode = timeInDays
        else:                
            timeCode = tdf.TDF_ConvertTimeToSeconds(timeInDays, timeSeconds)

        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((timeCode - self.ValueQueue[0]['t']) >= self.MaxTimeInQueue):
                self.ValueQueue.popleft()
            else:
                break
        # End - while (True):

        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 't': timeCode})

        # A list with only 1 item cannot have a range.
        if (len(self.ValueQueue) <= 1):
            return tdf.TDF_INVALID_VALUE    

        deltaValue = -1
        deltaTime = -1
        for entry in self.ValueQueue:
            currentDeltaValue = abs(value - entry['v'])
            if ((deltaValue == -1) or (currentDeltaValue > deltaValue)):
                deltaValue = currentDeltaValue
                deltaTime = timeCode - entry['t']
        # End - for elem in self.ValueQueue:

        # <> Use the full time span, even though the range may be in a subset
        deltaTime = timeCode - self.ValueQueue[0]['t']

        if (deltaTime <= 0):
            return tdf.TDF_INVALID_VALUE

        rate = float(deltaValue / deltaTime)
        return rate
    # End of ComputeNewValue

# End - class CRateValue









################################################################################
#
#
################################################################################
class CRateCrossValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, timeGranularity, shortNumDays, longNumDays, varName):
        self.TimeGranularity = timeGranularity
        self.shortRate = CRateValue(shortNumDays)
        self.longRate = CRateValue(longNumDays)

        self.fDetectFasterRate = True
        self.fFuzzinessMargin = 1.1

        self.Reset()
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.shortRate.Reset()
        self.longRate.Reset()
    # End -  Reset


    #####################################################
    #
    # [CRateCrossValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, timeInDays, timeSeconds):
        shortRateVal = self.shortRate.ComputeNewValue(value, timeInDays, timeSeconds)
        longRateVal = self.longRate.ComputeNewValue(value, timeInDays, timeSeconds)
        if ((shortRateVal == tdf.TDF_INVALID_VALUE) or (longRateVal == tdf.TDF_INVALID_VALUE)):
            return tdf.TDF_INVALID_VALUE

        if ((self.fDetectFasterRate) and (shortRateVal >= (self.fFuzzinessMargin * longRateVal))):
            return 1

        return 0
    # End of ComputeNewValue

# End - class CRateCrossValue






################################################################################
#
#
################################################################################
class CBollingerValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, timeGranularity, fUpperBollinger, numDays):
        self.TimeGranularity = timeGranularity
        self.fUpperBollinger = fUpperBollinger
        self.MaxTimeInQueue = numDays

        self.Reset()
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
        self.TotalValue = 0
    # End -  Reset


    #####################################################
    #
    # [CBollingerValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, timeInDays, timeSeconds):
        if (self.TimeGranularity == tdf.TDF_TIME_GRANULARITY_DAYS):
            timeCode = timeInDays
        else:                
            timeCode = tdf.TDF_ConvertTimeToSeconds(timeInDays, timeSeconds)

        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((timeCode - self.ValueQueue[0]['t']) >= self.MaxTimeInQueue):
                self.TotalValue = self.TotalValue - self.ValueQueue[0]['v']
                self.ValueQueue.popleft()
            else:
                break
        # End - while (True):

        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 't': timeCode})
        self.TotalValue += value

        numValues = len(self.ValueQueue)
        if (numValues < 2):
            return tdf.TDF_INVALID_VALUE
        avgValue = float(self.TotalValue / numValues)

        # Get the total of deviations, or the difference between each value and the mean
        listOfValues = [entry['v'] for entry in self.ValueQueue]
        listStdDev = statistics.stdev(listOfValues)
        if (self.fUpperBollinger):
            bandVal = avgValue + listStdDev
            result = (value >= bandVal)
        else:
            bandVal = avgValue - listStdDev
            result = (value <= bandVal)

        return result
    # End of ComputeNewValue

# End - class CBollingerValue








################################################################################
#
#
################################################################################
class CRangeValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, timeGranularity, fAbsolute, numDays):
        self.TimeGranularity = timeGranularity
        self.ValueQueue = deque()
        self.MaxValue = tdf.TDF_INVALID_VALUE
        self.MinValue = tdf.TDF_INVALID_VALUE

        self.fAbsolute = fAbsolute
        self.MaxTimeInQueue = numDays
    # End - __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
        self.MaxValue = tdf.TDF_INVALID_VALUE
        self.MinValue = tdf.TDF_INVALID_VALUE
    # End -  Reset


    #####################################################
    #
    # [CRangeValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, timeInDays, timeSeconds):
        if (self.TimeGranularity == tdf.TDF_TIME_GRANULARITY_DAYS):
            timeCode = timeInDays
        else:                
            timeCode = tdf.TDF_ConvertTimeToSeconds(timeInDays, timeSeconds)

        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((timeCode - self.ValueQueue[0]['t']) >= self.MaxTimeInQueue):
                if ((self.MinValue == self.ValueQueue[0]['v']) or (self.MaxValue == self.ValueQueue[0]['v'])):
                    self.MaxValue = tdf.TDF_INVALID_VALUE
                    self.MinValue = tdf.TDF_INVALID_VALUE

                self.ValueQueue.popleft()
            else:
                break
        # End - while (True):

        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 't': timeCode})

        if ((self.MaxValue == tdf.TDF_INVALID_VALUE) or (self.MinValue == tdf.TDF_INVALID_VALUE)):
            self.MinValue = tdf.TDF_INVALID_VALUE
            self.MaxValue = tdf.TDF_INVALID_VALUE

            for entry in self.ValueQueue:
                if ((self.MinValue == tdf.TDF_INVALID_VALUE) or (entry['v'] <= self.MinValue)):
                    self.MinValue = entry['v']
                if ((self.MaxValue == tdf.TDF_INVALID_VALUE) or (entry['v'] >= self.MaxValue)):
                    self.MaxValue = entry['v']
            # End - for entry in self.ValueQueue:
        # End - if (fRecomputeMinMax):
        else:  # if (not fRecomputeMinMax):
            if ((self.MinValue == tdf.TDF_INVALID_VALUE) or (value <= self.MinValue)):
                self.MinValue = value
            if ((self.MaxValue == tdf.TDF_INVALID_VALUE) or (value >= self.MaxValue)):
                self.MaxValue = value
        # End - if (not fRecomputeMinMax):

        if ((self.MinValue == tdf.TDF_INVALID_VALUE) 
                or (self.MaxValue == tdf.TDF_INVALID_VALUE)
                or (len(self.ValueQueue) <= 1)):
            return tdf.TDF_INVALID_VALUE

        if (self.fAbsolute):
            result = float(self.MaxValue - self.MinValue)
        elif (self.MinValue != 0):
            result = float(self.MaxValue - self.MinValue)
            result = float(result / self.MinValue)
        else:
            result = 0

        return result
    # End of ComputeNewValue

# End - class CRangeValue




################################################################################
#
#
################################################################################
class CPercentChangeValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, timeGranularity, numDays):
        self.TimeGranularity = timeGranularity
        self.MaxTimeInQueue = numDays
        self.Reset()
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
        self.lowestValue = tdf.TDF_INVALID_VALUE
    # End -  Reset


    #####################################################
    #
    # [CPercentChangeValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, timeInDays, timeSeconds):
        if (self.TimeGranularity == tdf.TDF_TIME_GRANULARITY_DAYS):
            timeCode = timeInDays
        else:                
            timeCode = tdf.TDF_ConvertTimeToSeconds(timeInDays, timeSeconds)

        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((timeCode - self.ValueQueue[0]['t']) >= self.MaxTimeInQueue):
                if (self.lowestValue == self.ValueQueue[0]['v']):
                    self.lowestValue = tdf.TDF_INVALID_VALUE

                self.ValueQueue.popleft()
            else:
                break
        # End - while (True):

        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 't': timeCode})

        # Find the lowest value in the queue.
        # This may not be the oldest, we may have initially decreased then risen again.
        if (self.lowestValue == tdf.TDF_INVALID_VALUE):
            for elem in self.ValueQueue:
                if ((self.lowestValue == tdf.TDF_INVALID_VALUE) or (elem['v'] < self.lowestValue)):
                    self.lowestValue = elem['v']
            # End - for elem in self.ValueQueue:
        # End - if (self.lowestValue == tdf.TDF_INVALID_VALUE):

        if ((self.lowestValue == tdf.TDF_INVALID_VALUE) or (len(self.ValueQueue) < 2)):
            return tdf.TDF_INVALID_VALUE

        if (self.lowestValue == 0):
            result = 0
        else:
            result = float((value - self.lowestValue) / self.lowestValue)

        return result
    # End of ComputeNewValue

# End - class CPercentChangeValue









################################################################################
#
#
################################################################################
class CThresholdValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, timeGranularity, fAbove, thresholdVal, numDays):
        self.TimeGranularity = timeGranularity
        self.fAbove = fAbove
        self.thresholdVal = thresholdVal
        self.MaxTimeInQueue = numDays
        self.Reset()
    # End - __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
        self.MaxValue = tdf.TDF_INVALID_VALUE
        self.MinValue = tdf.TDF_INVALID_VALUE
    # End -  Reset


    #####################################################
    #
    # [CThresholdValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, timeInDays, timeSeconds):
        if (self.TimeGranularity == tdf.TDF_TIME_GRANULARITY_DAYS):
            timeCode = timeInDays
        else:                
            timeCode = tdf.TDF_ConvertTimeToSeconds(timeInDays, timeSeconds)

        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((timeCode - self.ValueQueue[0]['t']) >= self.MaxTimeInQueue):
                if ((self.MinValue == self.ValueQueue[0]['v']) or (self.MaxValue == self.ValueQueue[0]['v'])):
                    self.MaxValue = tdf.TDF_INVALID_VALUE
                    self.MinValue = tdf.TDF_INVALID_VALUE

                self.ValueQueue.popleft()
            else:
                break
        # End - while (True):

        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 't': timeCode})

        if ((self.MaxValue == tdf.TDF_INVALID_VALUE) or (self.MinValue == tdf.TDF_INVALID_VALUE)):
            self.MinValue = tdf.TDF_INVALID_VALUE
            self.MaxValue = tdf.TDF_INVALID_VALUE

            for entry in self.ValueQueue:
                if ((self.MinValue == tdf.TDF_INVALID_VALUE) or (entry['v'] <= self.MinValue)):
                    self.MinValue = entry['v']
                if ((self.MaxValue == tdf.TDF_INVALID_VALUE) or (entry['v'] >= self.MaxValue)):
                    self.MaxValue = entry['v']
            # End - for entry in self.ValueQueue:
        # End - if (fRecomputeMinMax):
        else:  # if (not fRecomputeMinMax):
            if ((self.MinValue == tdf.TDF_INVALID_VALUE) or (value <= self.MinValue)):
                self.MinValue = value
            if ((self.MaxValue == tdf.TDF_INVALID_VALUE) or (value >= self.MaxValue)):
                self.MaxValue = value
        # End - if (not fRecomputeMinMax):


        if ((not self.fAbove) and (self.thresholdVal > 0) and (self.MaxValue <= self.thresholdVal)):
            return 1

        if ((self.fAbove) and (self.thresholdVal > 0) and (self.MinValue >= self.thresholdVal)):
            return 1

        return 0
    # End of ComputeNewValue

# End - class CThresholdValue










################################################################################
#
#
################################################################################
class CVolatilityValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, timeGranularity, numDays):
        self.TimeGranularity = timeGranularity
        self.MaxTimeInQueue = numDays
        self.Reset()
    # End - __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
    # End -  Reset


    #####################################################
    #
    # [CVolatilityValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, timeInDays, timeSeconds):
        if (self.TimeGranularity == tdf.TDF_TIME_GRANULARITY_DAYS):
            timeCode = timeInDays
        else:                
            timeCode = tdf.TDF_ConvertTimeToSeconds(timeInDays, timeSeconds)

        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((timeCode - self.ValueQueue[0]['t']) >= self.MaxTimeInQueue):
                #if ((self.MinValue == self.ValueQueue[0]['v']) or (self.MaxValue == self.ValueQueue[0]['v'])):
                self.ValueQueue.popleft()
            else:
                break
        # End - while (True):

        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        self.ValueQueue.append({'v': value, 't': timeCode})

        totalChange = 0
        prevValue = tdf.TDF_INVALID_VALUE
        for entry in self.ValueQueue:
            currentValue = entry['v']
            if (prevValue != tdf.TDF_INVALID_VALUE):
                totalChange += abs(currentValue - prevValue)

            prevValue = currentValue
        # End - for entry in self.ValueQueue:

        numChanges = len(self.ValueQueue) - 1
        if (numChanges <= 0):
            return tdf.TDF_INVALID_VALUE

        return (totalChange / numChanges)
    # End of ComputeNewValue

# End - class CVolatilityValue










################################################################################
#
#
################################################################################
class CRSIValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, timeGranularity, numDays):
        self.TimeGranularity = timeGranularity
        self.MaxTimeInQueue = numDays

        self.percentChangeList = [0.0] * numDays
        self.percentGainList = [0.0] * numDays
        self.percentLossList = [0.0] * numDays

        self.Reset()
    # End - __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.ValueQueue = deque()
    # End -  Reset


    #####################################################
    #
    # [CRSIValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, timeInDays, timeSeconds):
        if (self.TimeGranularity == tdf.TDF_TIME_GRANULARITY_DAYS):
            timeCode = timeInDays
        else:                
            timeCode = tdf.TDF_ConvertTimeToSeconds(timeInDays, timeSeconds)

        # Prune old items that are now more than N days before the new item.
        # This will leave only items with the past N days in the list.
        while (len(self.ValueQueue) > 0):
            if ((timeCode - self.ValueQueue[0]['t']) >= self.MaxTimeInQueue):
                #if ((self.MinValue == self.ValueQueue[0]['v']) or (self.MaxValue == self.ValueQueue[0]['v'])):
                self.ValueQueue.popleft()
            else:
                break
        # End - while (True):

        numValues = len(self.ValueQueue)
        fAddNewValue = True
        if ((self.TimeGranularity == tdf.TDF_TIME_GRANULARITY_DAYS) 
                and (numValues > 0) 
                and (timeInDays == self.ValueQueue[numValues - 1]['t'])):
            self.ValueQueue[numValues - 1]['v'] = value
            fAddNewValue = False

        # Items are added to the list as LIFO, so oldest item is index [0] and
        # new items are added to the right
        # We visit items in increasing time order, so the list is always appended with
        # newer items on the right.
        if (fAddNewValue):
            self.ValueQueue.append({'v': value, 't': timeCode})

        # Make a list of gains and losses
        numValueChanges = numValues - 1
        oldVal = self.ValueQueue[0]['v']
        for index in range(1, numValues):
            newVal = self.ValueQueue[index]['v']
            if (oldVal != 0):
                deltaVal = newVal - oldVal
                percentChange = float(deltaVal / oldVal) * 100.0
                self.percentChangeList[index - 1] = percentChange
            oldVal = newVal
        # End - for index in range(numValues):

        for index in range(numValueChanges):
            percentChange = self.percentChangeList[index]
            if (percentChange > 0):
                self.percentGainList[index] = percentChange
                self.percentLossList[index] = 0
            else:
                self.percentGainList[index] = 0
                self.percentLossList[index] = -percentChange
        # End - for index in range(numValueChanges):

        if (numValueChanges > 0):
            avgPercentGain = sum(self.percentGainList) / numValueChanges
            avgPercentLoss = sum(self.percentLossList) / numValueChanges
        else:
            avgPercentGain = 0
            avgPercentLoss = 0

        if (avgPercentLoss == 0):
            relativeStrength = 0.0
        else:
            relativeStrength = avgPercentGain / avgPercentLoss
        relativeStrengthIndex = 100.0 - (100.0 / (1.0 + relativeStrength))

        return relativeStrengthIndex
    # End of ComputeNewValue

# End - class CRSIValue







################################################################################
#
#
################################################################################
class CIsStableValue():
    #####################################################
    # Constructor - This method is part of any class
    #####################################################
    def __init__(self, timeGranularity, numDays, varName, threshold):
        self.TimeGranularity = timeGranularity
        self.RangeVar = CRangeValue(True, numDays)
        self.threshold = threshold

        self.Reset()
    # End -  __init__


    #####################################################
    # Destructor - This method is part of any class
    #####################################################
    def __del__(self):
        return


    #####################################################
    #####################################################
    def Reset(self):
        self.RangeVar.Reset()
    # End -  Reset


    #####################################################
    #
    # [CIsStableValue::ComputeNewValue]
    #
    #####################################################
    def ComputeNewValue(self, value, timeInDays, timeSeconds):
        valRange = self.RangeVar.ComputeNewValue(value, timeInDays, timeSeconds)
        if (valRange == tdf.TDF_INVALID_VALUE):
            return tdf.TDF_INVALID_VALUE

        if (valRange > self.threshold):
            return 0

        return 1
    # End of ComputeNewValue

# End - class CIsStableValue










#####################################################################################
#
#####################################################################################
def CreateTimeValueFunction(functionNameStr, timeGranularity, varName):
    functionNameStr = functionNameStr.lower()
    ###############################################
    if (functionNameStr == "generic"):
        return CGenericTimeValue(timeGranularity)

    ###############################################
    elif (functionNameStr == "delta"):
        return CDeltaValue(timeGranularity, 1, varName)
    elif (functionNameStr == "delta3"):
        return CDeltaValue(timeGranularity, 3, varName)
    elif (functionNameStr == "delta7"):
        return CDeltaValue(timeGranularity, 7, varName)
    elif (functionNameStr == "delta14"):
        return CDeltaValue(timeGranularity, 14, varName)
    elif (functionNameStr == "delta30"):
        return CDeltaValue(timeGranularity, 30, varName)
    elif (functionNameStr == "delta60"):
        return CDeltaValue(timeGranularity, 60, varName)
    elif (functionNameStr == "delta90"):
        return CDeltaValue(timeGranularity, 90, varName)
    elif (functionNameStr == "delta180"):
        return CDeltaValue(timeGranularity, 180, varName)

    ###############################################
    elif (functionNameStr == "sum"):
        return CSum(timeGranularity, 1, varName)
    elif (functionNameStr == "sum3"):
        return CSum(timeGranularity, 3, varName)
    elif (functionNameStr == "sum7"):
        return CSum(timeGranularity, 7, varName)
    elif (functionNameStr == "sum14"):
        return CSum(timeGranularity, 14, varName)
    elif (functionNameStr == "sum30"):
        return CSum(timeGranularity, 30, varName)
    elif (functionNameStr == "sum60"):
        return CSum(timeGranularity, 60, varName)
    elif (functionNameStr == "sum90"):
        return CSum(timeGranularity, 90, varName)
    elif (functionNameStr == "sum180"):
        return CSum(timeGranularity, 180, varName)

    ###############################################
    elif (functionNameStr == "rate"):
        return CRateValue(timeGranularity, 1)
    elif (functionNameStr == "rate3"):
        return CRateValue(timeGranularity, 3)
    elif (functionNameStr == "rate7"):
        return CRateValue(timeGranularity, 7)
    elif (functionNameStr == "rate14"):
        return CRateValue(timeGranularity, 14)
    elif (functionNameStr == "rate30"):
        return CRateValue(timeGranularity, 30)
    elif (functionNameStr == "rate60"):
        return CRateValue(timeGranularity, 60)
    elif (functionNameStr == "rate90"):
        return CRateValue(timeGranularity, 90)
    elif (functionNameStr == "rate180"):
        return CRateValue(timeGranularity, 180)

    ###############################################
    elif (functionNameStr == "accel"):
        return CAccelerationValue(timeGranularity, 2)
    elif (functionNameStr == "accel3"):
        return CAccelerationValue(timeGranularity, 3)
    elif (functionNameStr == "accel7"):
        return CAccelerationValue(timeGranularity, 7)
    elif (functionNameStr == "accel14"):
        return CAccelerationValue(timeGranularity, 14)
    elif (functionNameStr == "accel30"):
        return CAccelerationValue(timeGranularity, 30)
    elif (functionNameStr == "accel60"):
        return CAccelerationValue(timeGranularity, 60)
    elif (functionNameStr == "accel90"):
        return CAccelerationValue(timeGranularity, 90)
    elif (functionNameStr == "accel180"):
        return CAccelerationValue(timeGranularity, 180)

    ###############################################
    elif (functionNameStr == "range"):
        return CRangeValue(timeGranularity, True, 1)
    elif (functionNameStr == "range3"):
        return CRangeValue(timeGranularity, True, 3)
    elif (functionNameStr == "range7"):
        return CRangeValue(timeGranularity, True, 7)
    elif (functionNameStr == "range14"):
        return CRangeValue(timeGranularity, True, 14)
    elif (functionNameStr == "range30"):
        return CRangeValue(timeGranularity, True, 30)
    elif (functionNameStr == "range60"):
        return CRangeValue(timeGranularity, True, 60)
    elif (functionNameStr == "range90"):
        return CRangeValue(timeGranularity, True, 90)
    elif (functionNameStr == "range180"):
        return CRangeValue(timeGranularity, True, 180)

    ###############################################
    elif (functionNameStr == "relrange"):
        return CRangeValue(timeGranularity, False, 1)
    elif (functionNameStr == "relrange3"):
        return CRangeValue(timeGranularity, False, 3)
    elif (functionNameStr == "relrange7"):
        return CRangeValue(timeGranularity, False, 7)
    elif (functionNameStr == "relrange14"):
        return CRangeValue(timeGranularity, False, 14)
    elif (functionNameStr == "relrange30"):
        return CRangeValue(timeGranularity, False, 30)
    elif (functionNameStr == "relrange60"):
        return CRangeValue(timeGranularity, False, 60)
    elif (functionNameStr == "relrange90"):
        return CRangeValue(timeGranularity, False, 90)
    elif (functionNameStr == "relrange180"):
        return CRangeValue(timeGranularity, False, 180)

    ###############################################
    elif (functionNameStr == "percentchange"):
        return CPercentChangeValue(timeGranularity, 2)
    elif (functionNameStr == "percentchange3"):
        return CPercentChangeValue(timeGranularity, 3)
    elif (functionNameStr == "percentchange7"):
        return CPercentChangeValue(timeGranularity, 7)
    elif (functionNameStr == "percentchange14"):
        return CPercentChangeValue(timeGranularity, 14)
    elif (functionNameStr == "percentchange30"):
        return CPercentChangeValue(timeGranularity, 30)
    elif (functionNameStr == "percentchange60"):
        return CPercentChangeValue(timeGranularity, 60)
    elif (functionNameStr == "percentchange90"):
        return CPercentChangeValue(timeGranularity, 90)
    elif (functionNameStr == "percentchange180"):
        return CPercentChangeValue(timeGranularity, 180)

    ###############################################
    elif (functionNameStr == "isstable"):
        return CIsStableValue(timeGranularity, 3, varName, 0.3)
    elif (functionNameStr == "isstable7"):
        return CIsStableValue(timeGranularity, 7, varName, 0.3)
    elif (functionNameStr == "isstable14"):
        return CIsStableValue(timeGranularity, 14, varName, 0.3)
    elif (functionNameStr == "isstable30"):
        return CIsStableValue(timeGranularity, 30, varName, 0.3)
    elif (functionNameStr == "isstable60"):
        return CIsStableValue(timeGranularity, 60, varName, 0.3)
    elif (functionNameStr == "isstable90"):
        return CIsStableValue(timeGranularity, 90, varName, 0.3)
    elif (functionNameStr == "isstable180"):
        return CIsStableValue(timeGranularity, 180, varName, 0.3)

    ###############################################
    elif (functionNameStr in ("runavg", "runnavg")):
        return CRunningAvgValue(timeGranularity, 60)
    elif (functionNameStr in ("runavg3", "runnavg3")):
        return CRunningAvgValue(timeGranularity, 3)
    elif (functionNameStr in ("runavg7", "runnavg7")):
        return CRunningAvgValue(timeGranularity, 7)
    elif (functionNameStr in ("runavg14", "runnavg14")):
        return CRunningAvgValue(timeGranularity, 14)
    elif (functionNameStr == "runavg30"):
        return CRunningAvgValue(timeGranularity, 30)
    elif (functionNameStr == "runavg60"):
        return CRunningAvgValue(timeGranularity, 60)
    elif (functionNameStr == "runavg90"):
        return CRunningAvgValue(timeGranularity, 90)
    elif (functionNameStr == "runavg180"):
        return CRunningAvgValue(timeGranularity, 180)

    ###############################################
    elif (functionNameStr == "below45"):
        return CThresholdValue(timeGranularity, False, 45, 60)
    elif (functionNameStr == "below45_3"):
        return CThresholdValue(timeGranularity, False, 45, 3)
    elif (functionNameStr == "below45_7"):
        return CThresholdValue(timeGranularity, False, 45, 7)
    elif (functionNameStr == "below45_14"):
        return CThresholdValue(timeGranularity, False, 45, 14)
    elif (functionNameStr == "below45_30"):
        return CThresholdValue(timeGranularity, False, 45, 30)
    elif (functionNameStr == "below45_60"):
        return CThresholdValue(timeGranularity, False, 45, 60)
    elif (functionNameStr == "below45_90"):
        return CThresholdValue(timeGranularity, False, 45, 90)
    elif (functionNameStr == "below45_180"):
        return CThresholdValue(timeGranularity, False, 45, 180)

    ###############################################
    elif (functionNameStr == "above45"):
        return CThresholdValue(timeGranularity, True, 45, 60)
    elif (functionNameStr == "above45_3"):
        return CThresholdValue(timeGranularity, True, 45, 3)
    elif (functionNameStr == "above45_7"):
        return CThresholdValue(timeGranularity, True, 45, 7)
    elif (functionNameStr == "above45_14"):
        return CThresholdValue(timeGranularity, True, 45, 14)
    elif (functionNameStr == "above45_30"):
        return CThresholdValue(timeGranularity, True, 45, 30)
    elif (functionNameStr == "above45_60"):
        return CThresholdValue(timeGranularity, True, 45, 60)
    elif (functionNameStr == "above45_90"):
        return CThresholdValue(timeGranularity, True, 45, 90)
    elif (functionNameStr == "above45_180"):
        return CThresholdValue(timeGranularity, True, 45, 180)

    ###############################################
    elif (functionNameStr == "vol"):
        return CVolatilityValue(timeGranularity, 60)
    elif (functionNameStr == "vol3"):
        return CVolatilityValue(timeGranularity, 3)
    elif (functionNameStr == "vol7"):
        return CVolatilityValue(timeGranularity, 7)
    elif (functionNameStr == "vol14"):
        return CVolatilityValue(timeGranularity, 14)
    elif (functionNameStr == "vol30"):
        return CVolatilityValue(timeGranularity, 30)
    elif (functionNameStr == "vol60"):
        return CVolatilityValue(timeGranularity, 60)
    elif (functionNameStr == "vol90"):
        return CVolatilityValue(timeGranularity, 90)
    elif (functionNameStr == "vol180"):
        return CVolatilityValue(timeGranularity, 180)

    ###############################################
    elif (functionNameStr == "rsi"):
        return CRSIValue(timeGranularity, 60)
    elif (functionNameStr == "rsi3"):
        return CRSIValue(timeGranularity, 3)
    elif (functionNameStr == "rsi7"):
        return CRSIValue(timeGranularity, 7)
    elif (functionNameStr == "rsi14"):
        return CRSIValue(timeGranularity, 14)
    elif (functionNameStr == "rsi30"):
        return CRSIValue(timeGranularity, 30)
    elif (functionNameStr == "rsi60"):
        return CRSIValue(timeGranularity, 60)
    elif (functionNameStr == "rsi90"):
        return CRSIValue(timeGranularity, 90)
    elif (functionNameStr == "rsi180"):
        return CRSIValue(timeGranularity, 180)

    ###############################################
    elif (functionNameStr == "bollup"):
        return CBollingerValue(timeGranularity, True, 60)

    ###############################################
    elif (functionNameStr == "bolllow"):
        return CBollingerValue(timeGranularity, False, 60)

    ###############################################
    elif (functionNameStr == "faster30than90"):
        return CRateCrossValue(timeGranularity, 30, 90, varName)

    ###############################################
    else:
        print("CreateTimeValueFunction. Unrecognized func: " + functionNameStr)
        return None
# End - CreateTimeValueFunction



