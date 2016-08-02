#!/usr/bin/env python


runToFbset = {
    273158 : "fb_all_withuTCA_consolidated3_no1240_TOTEM",

    275832 : "fb_all_withuTCA_with_CTPPS_TOT",

    273301 : "fb_all_withuTCA_consolidated3_no1240_TOTEM",

    }

def getFbsetFromRun(run):
    
    if not runToFbset.has_key(run):
        raise Exception("don't know fbset for run " + str(run))

    return runToFbset[run]
