#!/usr/bin/env python

# utilities to make plotting tasks for different ways of grouping FEDs

#----------
# initialize
#----------

fedAssociation = {}
import glob
for fname in glob.glob("hwdb/fedAssoc-*.py"):
    execfile(fname)


#----------------------------------------------------------------------

def makeFedGroups(run, fedsInRun, groupingName, groupNameFunc, postGroupingNameFunc = None):
    # generic function which groups fedbuilders by the given criterion
    #
    # groupNameFunc must (given a dict with fed information)
    # return the name of the group
    #
    # postGroupingNameFunc can be used to change the name of the groups
    # after the grouping is complete (used e.g. to name the FRL groups
    # based on the FEDids associated to it)
    
    import sys

    import runToFbset
    fbset = runToFbset.getFbsetFromRun(run)

    retval = []

    fedsInRun = set(fedsInRun)

    assert fedAssociation.has_key(fbset), "could not find data for fbset " + fbset

    # get assocation information of all FEDs
    allFedData = fedAssociation[fbset]

    # to keep track of which groups were added already
    groups = {}

    # group by fedbuilders
    for fedData in allFedData:

        fedId = fedData['fed']

        thisGroup = groupNameFunc(fedData)

        # list of output FEDs
        if groups.has_key(thisGroup):
            # existing group
            # append fed
            groups[thisGroup]['fedIds'].append(fedId)
        else:
            # create a new group entry
            # note that we keep filling its fedIds entry later on
            outputData = dict(label = thisGroup,
                              grouping = "by " + groupingName,
                              fedIds = [ fedId ]
                              )
            groups[thisGroup] = outputData
            retval.append(outputData)

    # end of loop over FEDs

    #----------
    # rename groups after grouping is complete
    #----------
    if postGroupingNameFunc != None:
        for outputData in retval:
            # update group name
            outputData['label'] = postGroupingNameFunc(outputData)

    #----------
    # remove FEDs not in the run and check which groups had no FED in the run
    # (do this only AFTER renaming the groups so we can print the new names)
    #----------
    retval2 = []
    for outputData in retval:    
        # remove FEDs not in run
        outputData['fedIds'] = [ fed for fed in outputData['fedIds'] if fed in fedsInRun ]

        if not outputData['fedIds']:
            print >> sys.stderr,"skipping", groupingName,outputData['label'],", no feds included in run"
        else:
            retval2.append(outputData)

    return retval2

#----------------------------------------------------------------------
def makeFRLgroups(run, fedsInRun):
    """ summing by FRL/FEROL, i.e. many tracker FEDs are in pairs, most others are single FEDs """
    
    import FEDtoFRLMappingData
    frlTuples = FEDtoFRLMappingData.makeFRLtuples(run, fedsInRun)

    allSubsysToPlot = []

    for thisFeds in frlTuples:
        # only keep those FEDs which were in the run
        thisFeds = [ x for x in thisFeds if x in fedsInRun ]

        if thisFeds:

            # get the subsystem name of the first 
            assert len(thisFeds) <= 4

            allSubsysToPlot.append(dict(
                    label = "+".join(str(x) for x in thisFeds),
                    grouping = "by FRL",
                    fedIds = thisFeds,
                    )
                    )

    return allSubsysToPlot

#----------------------------------------------------------------------

def makeSingleFEDgroups(run, fedsInRun):
    """ makes a list of groups consisting of a single FED only """
    
    allSubsysToPlot = []

    for fed in fedsInRun:

        allSubsysToPlot.append(dict(
                label = "fed %d" % fed,
                grouping = "by FED",
                fedIds = [ fed ],
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
                fedIds = thisFeds,
                     )
                )

    # end of loop over subdetectors
    return groups

#----------------------------------------------------------------------

def makeTTCpartitionGroups(fedsInRun):
    # returns a map for TTC partition name to list of FEDs
    # (restricted to those in fedsInRun)

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
                fedIds = thisFeds,
                      )
                )

    # end of loop over subdetectors
    return groups


#----------------------------------------------------------------------
def makeFEDbuilderGroups(run, fedsInRun):
    # returns groups of fedbuilders (based on fbset)

    import sys

    import runToFbset
    fbset = runToFbset.getFbsetFromRun(run)

    retval = []

    fedsInRun = set(fedsInRun)

    import FedBuilderData

    assert FedBuilderData.fedBuilderGroups.has_key(fbset), "could not find data for fbset " + fbset

    for line in FedBuilderData.fedBuilderGroups[fbset]:

        # exclude fedbuilders for which no single FED was in the run
        feds = [ fed for fed in line['feds'] if fed in fedsInRun ]
        if not feds:
            print >> sys.stderr,"skipping fedbuilder",line['name'],", no feds included in run"
            continue

        retval.append(dict(label = line['name'],
                           grouping = "by fedbuilder",
                           fedIds = feds
                           ))

    return retval

#----------------------------------------------------------------------

def makeAllFedsGroup(fedsInRun):
    """ returns a plotting group for plotting the sum of all FEDs in the run (total event size) """
    
    return [ dict(
            label = "total",
            grouping = None,
            fedIds = fedsInRun,
            )
             ]

#----------------------------------------------------------------------
