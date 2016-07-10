#!/usr/bin/env python


runToEqset = {
    273158 : "eq_160404",
    }

def getEqsetFromRun(run):
    
    if not runToEqset.has_key(run):
        raise Exception("don't know eqset for run " + str(run))

    return runToEqset[run]
