#!/usr/bin/env python

# utilities to make plotting tasks for different ways of grouping FEDs

#----------------------------------------------------------------------
def makeFRLgroups(fedsInRun):
    """ summing by FRL/FEROL, i.e. many tracker FEDs are in pairs, most others are single FEDs """
    
    import FEDtoFRLMappingData
    frlTuples = FEDtoFRLMappingData.makeFRLtuples(fedsInRun)

    allSubsysToPlot = []

    for thisFeds in frlTuples:
        # only keep those FEDs which were in the run
        thisFeds = [ x for x in thisFeds if x in fedsInRun ]

        if thisFeds:

            # get the subsystem name of the first 

            allSubsysToPlot.append(dict(
                    label = "+".join(str(x) for x in thisFeds),
                    grouping = "by FRL",
                    expr = "+".join([ "size%03d" % x for x in thisFeds]),
                    numFeds = len(set(thisFeds)),
                                   )
                    )

    return allSubsysToPlot

#----------------------------------------------------------------------

def makeSubSystemGroups(fedsInRun):
    import utils, operator

    groups = []

    for subdet in sorted(utils.subdetTTCpartFEDs.keys()):
        # put all FEDs of all ttcpartitions in this subdetector into one group
        
        thisFeds = reduce(operator.__add__, utils.subdetTTCpartFEDs[subdet].values())

        # make sure we don't count any FED more than once
        thisFeds = sorted(set(thisFeds))

        # filter only FEDs in this run
        thisFeds = [ x for x in thisFeds if x in fedsInRun ]

        if not thisFeds:
            continue

        groups.append(dict(
                label = subdet,
                grouping = "by subsystem",
                expr = "+".join([ "size%03d" % x for x in thisFeds]),
                numFeds = len(set(thisFeds)),
                     )
                )

    # end of loop over subdetectors
    return groups

#----------------------------------------------------------------------

def makeTTCpartitionGroups(fedsInRun):

    import utils, operator

    groups = []

    for subdet in sorted(utils.subdetTTCpartFEDs.keys()):
        # put all FEDs of all ttcpartitions in this subdetector into one group
        
        for ttcpart in sorted(utils.subdetTTCpartFEDs[subdet].keys()):

            thisFeds = utils.subdetTTCpartFEDs[subdet][ttcpart]

            # make sure we don't count any FED more than once
            thisFeds = sorted(set(thisFeds))
            
            # filter only FEDs in this run
            thisFeds = [ x for x in thisFeds if x in fedsInRun ]

            if not thisFeds:
                continue

            groups.append(dict(
                    label = ttcpart,
                grouping = "by TTC partition",
                expr = "+".join([ "size%03d" % x for x in thisFeds]),
                numFeds = len(set(thisFeds)),
                      )
                )

    # end of loop over subdetectors
    return groups


#----------------------------------------------------------------------
def makeFEDbuilderGroups(fedsInRun):

    import sys

    retval = []

    fedsInRun = set(fedsInRun)

    import FedBuilderData
    for line in FedBuilderData.fedBuilderGroups:

        # exclude fedbuilders for which no single FED was in the run
        feds = [ fed for fed in line['feds'] if fed in fedsInRun ]
        if not feds:
            print >> sys.stderr,"skipping fedbuilder",line['name'],", no feds included in run"
            continue

        retval.append(dict(label = line['name'],
                           grouping = "by fedbuilder",
                           expr = "+".join(["size%03d" % fed for fed in feds ]),
                           numFeds = len(set(feds)),
                           ))

    return retval

#----------------------------------------------------------------------

def makeAllFedsGroup(fedsInRun):
    """ returns a plotting group for plotting the sum of all FEDs in the run (total event size) """
    
    # use the sum expression instead of a dedicated variable (for simplicity)
    # 
    # in order to avoid the following ROOT error message:
    # 
    #  Error in <TTreeFormula::Compile>:  Too many operators !
    # the main program should call TFormular::SetMaxima(..)
    # (see https://root.cern.ch/phpBB3/viewtopic.php?t=8218 )
    # 
    # can't get this to work however (still getting a segmentation violation)
    # using the 'size_total' variable instead
    return [ dict(
            label = "total",
            grouping = None,
            # expr = "+".join([ "size%03d" % x for x in fedsInRun]),
            expr = "size_total",
            numFeds = len(set(fedsInRun)),
            )
             ]

#----------------------------------------------------------------------
