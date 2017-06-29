
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

#----------------------------------------------------------------------

def makeFRLtuples(run, fedList):
    """ returns a list of lists with the given feds, either
    alone (all subsystems but the strip tracker) or paired
    if both FEDs of an FRL are given (i.e. if only one FED
    of an FRL with two FEDs is given as input, there will
    only be the given FED in the tuple).

    Useful to plot e.g. the per FRL rate instead of the per FED rate
    """

    import runToEqset
    # get eqset name
    eqset = runToEqset.getEqsetFromRun(run)

    return fedPairs[eqset]

#----------------------------------------------------------------------
