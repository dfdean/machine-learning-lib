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
# TDF - Timeline Data Format - MEDICAL Vocabulary
#
################################################################################

TDF_DATA_TYPE_INT                   = 0
TDF_DATA_TYPE_FLOAT                 = 1
TDF_DATA_TYPE_BOOL                  = 2
TDF_DATA_TYPE_STRING_LIST           = 3
TDF_DATA_TYPE_UNKNOWN               = -1

ANY_EVENT_OR_VALUE = "ANY"


################################################################################
g_FunctionInfo = {'delta': {'resultDataType': TDF_DATA_TYPE_UNKNOWN},
    'rate': {'resultDataType': TDF_DATA_TYPE_FLOAT},
    'rate7': {'resultDataType': TDF_DATA_TYPE_FLOAT},
    'rate14': {'resultDataType': TDF_DATA_TYPE_FLOAT},
    'rate30': {'resultDataType': TDF_DATA_TYPE_FLOAT},
    'rate60': {'resultDataType': TDF_DATA_TYPE_FLOAT},
    'rate90': {'resultDataType': TDF_DATA_TYPE_FLOAT},
    'rate180': {'resultDataType': TDF_DATA_TYPE_FLOAT},
    'accel': {'resultDataType': TDF_DATA_TYPE_FLOAT},
    'faster7Than30': {'resultDataType': TDF_DATA_TYPE_BOOL},
    'runavg': {'resultDataType': TDF_DATA_TYPE_FLOAT},
    'bollup': {'resultDataType': TDF_DATA_TYPE_BOOL},
    'bolllow': {'resultDataType': TDF_DATA_TYPE_BOOL},
    'range': {'resultDataType': TDF_DATA_TYPE_UNKNOWN},
    'relrange': {'resultDataType': TDF_DATA_TYPE_UNKNOWN}
}  # g_FunctionInfo



################################################################################
g_LabValueInfo = {
    ##############################
    # CBC
    'Hgb': {'minVal': 2.0, 'maxVal': 17.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'HgbAlone': {'minVal': 2.0, 'maxVal': 17.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'HgbCBC': {'minVal': 2.0, 'maxVal': 17.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'HgbCBCDiff': {'minVal': 2.0, 'maxVal': 17.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'HgbABG': {'minVal': 2.0, 'maxVal': 17.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'HgbPathology': {'minVal': 2.0, 'maxVal': 17.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'WBC': {'minVal': 1.0, 'maxVal': 25.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'Plt': {'minVal': 30.0, 'maxVal': 500.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'AbsNeutrophils': {'minVal': 0.1, 'maxVal': 25.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'AbsLymphs': {'minVal': 0.1, 'maxVal': 25.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'MCV': {'minVal': 60.0, 'maxVal': 110.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # Basic Metabolic Function Panel (and Renal Function Panel)
    'Na': {'minVal': 115.0, 'maxVal': 155.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'K': {'minVal': 2.0, 'maxVal': 7.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'Cl': {'minVal': 80.0, 'maxVal': 120.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'CO2': {'minVal': 10.0, 'maxVal': 35.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'BUN': {'minVal': 5.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'Cr': {'minVal': 0.5, 'maxVal': 6.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'Glc': {'minVal': 50.0, 'maxVal': 300.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'Ca': {'minVal': 6.0, 'maxVal': 13.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'iCal': {'minVal': 1.0, 'maxVal': 6.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'Phos': {'minVal': 1.0, 'maxVal': 8.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'Mg': {'minVal': 1.0, 'maxVal': 3.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},

    ##############################
    # Hepatic Function Panel
    'ALT': {'minVal': 10.0, 'maxVal': 150.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'AST': {'minVal': 10.0, 'maxVal': 150.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'ALP': {'minVal': 30.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'Tbili': {'minVal': 0.5, 'maxVal': 20.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'TProt': {'minVal': 1.0, 'maxVal': 8.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'Alb': {'minVal': 1.0, 'maxVal': 5.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},

    ##############################
    # Random Urine
    'UProt': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UAlb': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UNa': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UUN': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UCr': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UCl': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UK': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'UCO2': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # 24hr Urine
    #'UCr24hr': {'minVal': 1.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    #'UProt24hr': {'minVal': 1.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    #'UNa24hr': {'minVal': 1.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    #'UCl24hr': {'minVal': 1.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    #'UK24hr': {'minVal': 1.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    #'UUN24hr': {'minVal': 1.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # Cardiac
    'LVEF': {'minVal': 1.0, 'maxVal': 80.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 1.0},
    'TropHS': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Trop': {'minVal': 0.1, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'NTBNP': {'minVal': 50.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'BNP': {'minVal': 50.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # PFT
    'FEV1_FVC': {'minVal': 0.1, 'maxVal': 1.5, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.01},
    'FEV1': {'minVal': 0.1, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 1.0},
    'DLCO': {'minVal': 1.0, 'maxVal': 20.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 1.0},

    ##############################
    # Misc
    'Lac': {'minVal': 0.1, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'PT': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'PTT': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'INR': {'minVal': 0.5, 'maxVal': 6.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'DDimer': {'minVal': 0.1, 'maxVal': 5.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Fibrinogen': {'minVal': 0, 'maxVal': 2000, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Haptoglobin': {'minVal': 0, 'maxVal': 2000, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'FreeHgb': {'minVal': 0, 'maxVal': 2000, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'LDH': {'minVal': 0, 'maxVal': 2000, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'A1c': {'minVal': 5.0, 'maxVal': 15.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'PTH': {'minVal': 1.0, 'maxVal': 8.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'CK': {'minVal': 1.0, 'maxVal': 2000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Procal': {'minVal': 0.01, 'maxVal': 2.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'CRP': {'minVal': 1.0, 'maxVal': 20.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Lipase': {'minVal': 1.0, 'maxVal': 50.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'CystatinC': {'minVal': 1.0, 'maxVal': 50.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'Transferrin': {'minVal': 1.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'TransferrinSat': {'minVal': 1.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Iron': {'minVal': 1.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'TIBC': {'minVal': 1.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "Iron;TransferrinSat;Transferrin"},
    'Ferritin': {'minVal': 10.0, 'maxVal': 400.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # ABG and VBG
    'PO2': {'minVal': 20.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'PCO2': {'minVal': 20.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'BGSpO2': {'minVal': 50.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # Drug levels
    'VancLvl': {'minVal': 0.1, 'maxVal': 60.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'TacLvl': {'minVal': 0.1, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'SiroLvl': {'minVal': 0.1, 'maxVal': 35.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'GentLvl': {'minVal': 0.1, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'TobLvl': {'minVal': 0.1, 'maxVal': 15.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'AmikLvl': {'minVal': 0.1, 'maxVal': 50.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'CycLvl': {'minVal': 10.0, 'maxVal': 350.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'MTXLvl': {'minVal': 0.5, 'maxVal': 26.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'EveroLvl': {'minVal': 0.1, 'maxVal': 15.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'DigLvl': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'VoriLvl': {'minVal': 0.1, 'maxVal': 12.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'GabapLvl': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'DaptoLvl': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'ValpLvl': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'LevLvl': {'minVal': 0.1, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},

    ##############################
    # Derived values
    'GFR': {'minVal': 5.0, 'maxVal': 60.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "WtKg;AgeInYrs;Cr;IsMale", 'ValueWordIncrement': 1.0},
    'UPCR': {'minVal': 0.1, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "UProt;UCr", 'ValueWordIncrement': 0.1},
    'UACR': {'minVal': 0.01, 'maxVal': 5.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "UAlb;UCr", 'ValueWordIncrement': 0.1},
    'FENa': {'minVal': 0.01, 'maxVal': 2.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "Cr;Na;UCr;UNa", 'ValueWordIncrement': 0.01},
    'FEUrea': {'minVal': 5.0, 'maxVal': 50.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "Cr;BUN;UCr;UUN", 'ValueWordIncrement': 0.01},
    'AdjustCa': {'minVal': 6.0, 'maxVal': 13.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "Ca;Alb"},
    'ProtGap': {'minVal': 1.0, 'maxVal': 7.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "TProt;Alb"},
    'AnionGap': {'minVal': 5.0, 'maxVal': 20.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "Na;Cl;CO2"},
    'UrineAnionGap': {'minVal': -10.0, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "UNa;UK;UCl"},
    'BUNCrRatio': {'minVal': 1.0, 'maxVal': 30.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "BUN;Cr"},
    'NeutLymphRatio': {'minVal': -10.0, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "AbsNeutrophils;AbsLymphs"},
    'MELD': {'minVal': 1.0, 'maxVal': 50.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "Cr;Na;Tbili;INR", 'ValueWordIncrement': 1.0},
    'BaselineCr': {'minVal': 0.3, 'maxVal': 8.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "Cr", 'ValueWordIncrement': 0.1},
    'BaselineGFR': {'minVal': 10.0, 'maxVal': 60.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "WtKg;AgeInYrs;BaselineCr;IsMale", 'ValueWordIncrement': 1.0},
    'InAKI': {'minVal': 0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "Cr;BaselineCr"},

    ##############################
    # Vitals
    'TF': {'minVal': 95.0, 'maxVal': 105.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'SBP': {'minVal': 50.0, 'maxVal': 180.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'DBP': {'minVal': 30.0, 'maxVal': 120.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'HR': {'minVal': 30.0, 'maxVal': 160.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'SPO2': {'minVal': 70.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'WtKg': {'minVal': 30.0, 'maxVal': 200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 1.0},
    'BMI': {'minVal': 15.0, 'maxVal': 50.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 1.0},

    ##############################
    # Med Doses We Monitor
    'VancDose': {'minVal': 500.0, 'maxVal': 4000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3, 'ValueWordIncrement': 1.0},
    'CoumDose': {'minVal': 0.5, 'maxVal': 9.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3, 'ValueWordIncrement': 0.1},
    'TacroDose': {'minVal': 1.0, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3, 'ValueWordIncrement': 0.1},
    'CycDose': {'minVal': 50.0, 'maxVal': 750.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3, 'ValueWordIncrement': 0.1},
    'MTXDose': {'minVal': 5.0, 'maxVal': 50.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3, 'ValueWordIncrement': 0.1},
    'TobraDose': {'minVal': 100.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3, 'ValueWordIncrement': 1.0},
    'VoriDose': {'minVal': 100.0, 'maxVal': 1200.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3, 'ValueWordIncrement': 1.0},
    'SiroDose': {'minVal': 10.0, 'maxVal': 30.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3, 'ValueWordIncrement': 1.0},
    'GentDose': {'minVal': 10.0, 'maxVal': 600.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3, 'ValueWordIncrement': 1.0},
    'AmikDose': {'minVal': 10.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3, 'ValueWordIncrement': 1.0},
    'EveroDose': {'minVal': 5.0, 'maxVal': 50.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3, 'ValueWordIncrement': 1.0},
    'DigDose': {'minVal': 10.0, 'maxVal': 600.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3, 'ValueWordIncrement': 1.0},
    'GabaDose': {'minVal': 10.0, 'maxVal': 1800.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3, 'ValueWordIncrement': 1.0},
    'DaptoDose': {'minVal': 50.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3, 'ValueWordIncrement': 1.0},
    'Dapto': {'minVal': 50.0, 'maxVal': 600.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3, 'ValueWordIncrement': 1.0},

    ##############################
    # Inhaler Drugs
    'AlbutDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3},
    'IpraDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3},
    'TiotropDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3},
    'UmeclDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3},
    'FluticDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3},
    'BudesInhDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3},
    'MometDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3},
    'FormotDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3},
    'SalmetDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3},
    'VilantDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': "", 'MaxDaysWithZero': 3},

    ##############################
    # Med Doses For CYP450 Interactions
    'RifampicinDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'RifampinDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'PhenytoinDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'CarbamazDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'AmioDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'FlucDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'KetoconDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'MiconDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'ItraconDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'MetronidDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'SulphaphenDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'RitonavirDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'ClarithroDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'ErythroDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'DiltDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'VerapamilDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'AmlodipineDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'GemfibroDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'CiprofloxDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'AtorvaDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'SimvaDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'RosuvaDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'PravaDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'LovastatinDose': {'minVal': 1.0, 'maxVal': 1000.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # Total CYP450 Interactions
    'CYP2C9Inducer': {'minVal': 0.0, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': True, 'VariableDependencies': "RifampicinDose", 'ValueWordIncrement': 0.1},
    'CYP2C9Inhibiter': {'minVal': 0.0, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': True, 'VariableDependencies': "AmioDose;FlucDose;SulphaphenDose;MiconDose", 'ValueWordIncrement': 0.1},
    'CYP3A4Inducer': {'minVal': 0.0, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': True, 'VariableDependencies': "RifampinDose;CarbamazDose;PhenytoinDose", 'ValueWordIncrement': 0.1},
    'CYP3A4Inhibitor': {'minVal': 0.0, 'maxVal': 10.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': True, 'VariableDependencies': "ClarithroDose;ErythroDose;KetoconDose;ItraconDose;VoriDose;AmioDose;DiltDose;VerapamilDose;FlucDose", 'ValueWordIncrement': 0.1},

    ##############################
    # Transfusions - Used for the Iatrogenic Anemia Paper
    #'TransRBC': {'minVal': 1.0, 'maxVal': 3.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "inval", 'Calculated': False, 'VariableDependencies': ""},
    #'TransPlts': {'minVal': 1.0, 'maxVal': 3.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "inval", 'Calculated': False, 'VariableDependencies': ""},
    #'TransFFP': {'minVal': 1.0, 'maxVal': 3.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "inval", 'Calculated': False, 'VariableDependencies': ""},
    #'TransCryo': {'minVal': 1.0, 'maxVal': 3.0, 'dataType': TDF_DATA_TYPE_FLOAT, 'ActionAfterEachTimePeriod': "inval", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # Patient Status
    'HospitalDay': {'minVal': 0.0, 'maxVal': 100.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "InHospital"},
    'InHospital': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'LengthOfStay': {'minVal': 0.0, 'maxVal': 90.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "InHospital;HospitalAdmitDate;HospitalAdmitDate"},
    'DaysSincePrev': {'minVal': 0.0, 'maxVal': 20.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "InHospital;HospitalAdmitDate;HospitalAdmitDate"},
    'MajorSurgeries': {'minVal': 1.0, 'maxVal': 3.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'GIProcedures': {'minVal': 1.0, 'maxVal': 3.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "zero", 'Calculated': False, 'VariableDependencies': ""},
    'HadDialysis': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MostRecentDialysisDate"},
    'HadSurgery': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "MostRecentMajorSurgeryDate"},
    'Procedure': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_STRING_LIST, 'ActionAfterEachTimePeriod': "none", 'Calculated': False, 'VariableDependencies': ""},
    'Surgery': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_STRING_LIST, 'ActionAfterEachTimePeriod': "none", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # Patient Characteristice
    'IsMale': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'AgeInYrs': {'minVal': 18.0, 'maxVal': 80.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': True, 'VariableDependencies': "", 'ValueWordIncrement': 0.1},
    'MedHxDiabetes': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},

    ##############################
    # Future Disease Stages by Boolean
    'Outcome': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'OutcomeImprove': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'OutcomeWorsen': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'OutcomeFutureEndStage': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'Future_Boolean_CKD5': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD5Date"},
    'Future_Boolean_CKD4': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD4Date"},
    'Future_Boolean_CKD3b': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD3bDate"},
    'Future_Boolean_CKD3a': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD3aDate"},

    'Future_CKD5_2YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD5Date"},
    'Future_CKD4_2YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD4Date"},
    'Future_CKD3b_2YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD3bDate"},
    'Future_CKD3a_2YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD3aDate"},

    'Future_CKD5_5YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD5Date"},
    'Future_CKD4_5YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD4Date"},
    'Future_CKD3b_5YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD3bDate"},
    'Future_CKD3a_5YRS': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD3aDate"},

    ##############################
    # Future Disease Stages by Number of Days
    'Future_Days_Until_Discharge': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "HospitalAdmitDate;NextFutureDischargeDate;InHospital"},
    'Future_Days_Until_CKD5': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD5Date"},
    'Future_Days_Until_CKD4': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD4Date"},
    'Future_Days_Until_CKD3b': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD3bDate"},
    'Future_Days_Until_CKD3a': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR;StartCKD3aDate"},
    'Future_Days_Until_AKI': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "Cr;InAKI;NextAKIDate"},
    'Future_Days_Until_AKIResolution': {'minVal': 0.0, 'maxVal': 3650, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "Cr;InAKI;NextCrAtBaselineDate"},

    ##############################
    # INTERNAL USE ONLY
    # These are only used when compiling timeline events.
    'StartCKD5Date': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR"},
    'StartCKD4Date': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR"},
    'StartCKD3bDate': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR"},
    'StartCKD3aDate': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "GFR"},

    'NextCrAtBaselineDate': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "Cr;BaselineCr"},

    'NextAKIDate': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "Cr;InAKI;BaselineCr"},
    'Flag_HospitalAdmission': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},
    'Flag_HospitalDischarge': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "remove", 'Calculated': False, 'VariableDependencies': ""},

    'HospitalAdmitDate': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "InHospital"},
    'NextFutureDischargeDate': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "HospitalAdmitDate;NextFutureDischargeDate;InHospital"},

    'MostRecentDialysisDate': {'minVal': (18.0 * 365), 'maxVal': (90.0 * 365), 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""},
    'MostRecentMajorSurgeryDate': {'minVal': (18.0 * 365), 'maxVal': (90.0 * 365), 'dataType': TDF_DATA_TYPE_INT, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': "InHospital"},

    'NewLabs': {'minVal': 0.0, 'maxVal': 1.0, 'dataType': TDF_DATA_TYPE_BOOL, 'ActionAfterEachTimePeriod': "", 'Calculated': False, 'VariableDependencies': ""}
}  # g_LabValueInfo







