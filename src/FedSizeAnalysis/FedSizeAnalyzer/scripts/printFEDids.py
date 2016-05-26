#!/usr/bin/env python

# print the FEDids in the first event found
# 
# run this on an output file of fedsizeanalyzer_cfg.py
#
# runs just on the first event because a run contains a fixed
# set of FEDs in CMS

import sys, os

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------

ARGV = sys.argv[1:]

assert len(ARGV) == 1

inputFname = ARGV.pop(0)

#----------
from DataFormats.FWLite import Events, Handle

events = Events(inputFname)
handle  = Handle ('FedSizeAnalysisData')

label = ("fedSizeData", )

for event in events:
    event.getByLabel (label, handle)

    dataObj = handle.product()
    
    fedids = list(dataObj.getFedIds())
    fedids.sort()

    print ", ".join(str(x) for x in fedids)

    # just run on the first event
    break


