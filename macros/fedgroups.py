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

    return makeFedGroups(run, fedsInRun, "FRL", lambda fedData: fedData['frl'],
                         lambda outputData: "+".join([str(x) for x in sorted(outputData['fedIds'])])
                         )

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

def makeSubSystemGroups(run, fedsInRun):

    return makeFedGroups(run, fedsInRun, "subsystem", lambda fedData: fedData['subsystem'])

#----------------------------------------------------------------------

def makeTTCpartitionGroups(run, fedsInRun):
    # returns a map for TTC partition name to list of FEDs
    # (restricted to those in fedsInRun)

    return makeFedGroups(run, fedsInRun, "TTC partition", lambda fedData: fedData['ttcPartition'])

#----------------------------------------------------------------------

def makeFEDbuilderGroups(run, fedsInRun):
    # returns groups of fedbuilders (based on fbset)

    return makeFedGroups(run, fedsInRun, "fedbuilder", lambda fedData: fedData['fedbuilder'])

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
