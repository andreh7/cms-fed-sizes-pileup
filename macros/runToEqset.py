#!/usr/bin/env python


runToEqset = {
    273158 : "eq_160404",

    275832 : "eq_160519_01",

    273301 : "eq_160404",

    276870 : "eq_160708",

    282092 : "eq_160913_01",

    283171 : "eq_160913_01",

    }

def getEqsetFromRun(run):
    
    if not runToEqset.has_key(run):
        raise Exception("don't know eqset for run " + str(run))

    return runToEqset[run]
