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

assert len(ARGV) >= 1

if len(ARGV) > 1:
    print >> sys.stderr,"warning: more than one command line argument given, only looking at first file with at least one event"


for inputFname in ARGV:

    #----------
    from DataFormats.FWLite import Events, Handle

    events = Events(inputFname)
    handle  = Handle ('FedSizeAnalysisData')

    label = ("fedSizeData", )

    eventFound = False
    for event in events:
        event.getByLabel (label, handle)

        dataObj = handle.product()

        fedids = list(dataObj.getFedIds())
        fedids.sort()

        print ", ".join(str(x) for x in fedids)

        # just run on the first event
        eventFound = True
        break

    if not eventFound:
        print >> sys.stderr,"WARNING: no events found in",inputFname
    else:
        break

