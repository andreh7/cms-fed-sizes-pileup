#!/usr/bin/env python

#
# script for finding which FEDs are paired into
# one FRL
# 
# reads a spreadsheet taken from
# https://twiki.cern.ch/twiki/bin/view/CMS/DAQ-CI-subdet-DAQ-Mapping

#----------------------------------------------------------------------

def isInt(x):
    try:
        int(x)
        return True
    except ValueError:
        return False

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------

# note: this is not available on lxplus (but it is on Ubuntu)
import xlrd

workbook = xlrd.open_workbook("FED_FRL_map_v51.xls")
sheet = workbook.sheet_by_index(0)


# assume fixed column positions
colFEDsourceID = 12

# in which slot (of the compact PCI crate)
# the FRL is
colFRLslot = 1

# crate in which the FRL is
colFRLCrateName = 0

colSubsysName = 5

#--------------------

crateSlotToFed = {}

for row in range(sheet.nrows):

    # check whether this row is not a header or empty row

    # make sure there is a subsystem name:
    #  - is not empty
    #  - does not have spaces (except at the beginning and end)
    #  - does not contain digits


    subsysName = sheet.cell_value(row,colSubsysName)

    if not isinstance(subsysName, str) and not isinstance(subsysName, unicode):
        continue

    subsysName = subsysName.strip()

    if subsysName == '':
        continue

    if ' ' in subsysName:
        continue

    # print subsysName

    frlCrate = sheet.cell_value(row, colFRLCrateName)
    frlSlot = int(float(sheet.cell_value(row, colFRLslot)) + 0.5)

    fed = int(float(sheet.cell_value(row, colFEDsourceID)) + 0.5)
    
    # print frlCrate, frlSlot
    key = (frlCrate, frlSlot, subsysName)

    crateSlotToFed.setdefault(key,[]).append(fed)


# import pprint
# pprint.pprint(crateSlotToFed)
# 
#
# convert to a map of FED to peer FED

pairMapping = {}

for fedlist in crateSlotToFed.values():
    if len(fedlist) < 2:
        continue

    # the data format assumes that there is at most
    # one peer FED
    assert(len(fedlist) == 2)

    assert(not pairMapping.has_key(fedlist[0]))
    assert(not pairMapping.has_key(fedlist[1]))

    pairMapping[fedlist[0]] = fedlist[1]
    pairMapping[fedlist[1]] = fedlist[0]

import pprint
pprint.pprint(pairMapping)


    
    
    
    

