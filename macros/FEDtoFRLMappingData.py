
# for each FED which shares an FRL with another FED,
# this maps to the peer FED. If a FED does not appear
# in this dict, it does not share an FRL with another FED
#
# note that this dict contains the mapping in both directions
# (i.e. if A maps to B, B also maps to A)
#

import glob, re

# maps from eqset name to list of feds which are on the same FRL
fedPairs = {}

for fname in glob.glob("hwdb/fedpairs-*.py"):
    execfile(fname)

# first index is run,
# second index is fed
# value is peer fed
fedToPeerFedMapping = { }

# fill the pair mapping
for eqset in fedPairs.keys():

    fedToPeerFedMapping[eqset] = {}

    for line in fedPairs[eqset]:
        if len(line) == 1:
            continue

        assert len(line) == 2
        fedToPeerFedMapping[eqset][line[0]] = line[1]
        fedToPeerFedMapping[eqset][line[1]] = line[0]

del line

#----------------------------------------------------------------------

def makeFRLtuples(run, fedList):
    """ returns a list of tuples with the given feds, either
    alone (all subsystems but the strip tracker) or paired
    if both FEDs of an FRL are given (i.e. if only one FED
    of an FRL with two FEDs is given as input, there will
    only be the given FED in the tuple).

    Useful to plot e.g. the per FRL rate instead of the per FED rate
    """

    import runToEqset
    # get eqset name
    eqset = runToEqset.getEqsetFromRun(run)

    retval = []
    fedsProcessed = set()

    import utils

    for fed in fedList:

        # avoid plotting a pair of
        # FEDs twice
        if fed in fedsProcessed:
            continue

        fedsProcessed.add(fed)

        peerFED =  fedToPeerFedMapping[eqset].get(fed,None)

        # make sure that the peer FED normally is part of data taking
        if peerFED != None and not peerFED in utils.trackerFeds:
            peerFED = None

        if peerFED == None:
            # this FED has no peer
            retval.append((fed,))
        else:
            fedsProcessed.add(peerFED)

            # this FED shares an FRL with another FED
            thisFeds = sorted([fed, peerFED])
            retval.append(tuple(thisFeds))

    # end of loop of all given feds
    return retval
    

    

#----------------------------------------------------------------------
