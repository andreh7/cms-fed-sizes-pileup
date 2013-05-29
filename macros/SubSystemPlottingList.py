#!/usr/bin/env python

# a file sourced by plots.py to determine the
# list of FED groups to be plotted / generate a
# table for
#
# this was separated into its own file to
# allow better tracking with a version control
# system

allSubsysToPlot = [

                # these groups are defined in
                # FedSizeAnalysis/FedSizeAnalyzer/src/PerNumVertexNtupleMaker.cc 

                'CSCTF',
                'DTTF',
                'GCT',
                'LumiScalers', 
                'GlobalTrigger',
                'CSC',
                'DT',
                'CASTOR',
                'Pixel',

                # special request on 2011-07-06
                'BPIX',
                'FPIX',

                # special request on 2011-09-27
                "HF",

                #--------------------
                # requests 2011-10-04 by Christoph
                # for tracker FEDs
                # specify sums of individual FEDS

                # 1) The FEDs 413 and 368 form currently a pair and are thought to be the pair with the largest data volume.
                "size413+size368",
                "size413",
                "size368",
         
                # 2) FED 53 is currently the FED with the largest data volume and which is NOT paired.
                "size053",

                # The same as above but "typical" (i.e. NOT worst case) cases:
                # 3) pair 295 and 263
                "size295+size263",
                "size295",
                "size263",

                # 4) single 151
                "size151",

                #--------------------
                # testing for the above
                #--------------------
                # "size413+size368",
                # "size413",
                # "size368",
                #--------------------
                
                'Preshower',
                'ECAL',
                'HCAL',
                'RPC',
                'Tracker',

                "total",
                ]

#--------------------
import utils

if False:
    # request by Christoph, 2011-10-12
    # take all tracker FEDs
    allSubsysToPlot = [ "size%03d" % fed for fed in utils.trackerFeds ]

if True:
    # tracker but size/rate per FRL, not FED

    allSubsysToPlot = []

    import FEDtoFRLMappingData

    fedsProcessed = set()

    for fed in utils.trackerFeds:

        # avoid plotting a pair of
        # FEDs twice
        if fed in fedsProcessed:
            continue

        fedsProcessed.add(fed)

        peerFED =  FEDtoFRLMappingData.fedToPeerFedMapping.get(fed,None)

        # make sure that the peer FED normally is part of data taking
        if peerFED != None and not peerFED in utils.trackerFeds:
            peerFED = None

        if peerFED == None:
            # this FED has no peer
            allSubsysToPlot.append("size%03d" % fed)
        else:
            fedsProcessed.add(peerFED)

            # this FED shares an FRL with another FED
            thisFeds = sorted([fed, peerFED])
            allSubsysToPlot.append("+".join([ "size%03d" % x for x in thisFeds]))

    # end of loop of all tracker feds

#--------------------
if False:
    
    # do the plots for each Pixel FED
    allSubsysToPlot = [ "size%03d" % fed for fed in utils.pixelFeds ]

#--------------------
# generate plots/table for ALL FEDs

