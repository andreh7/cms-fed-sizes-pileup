#!/usr/bin/env python


runToFbset = {
    273158 : "fb_all_withuTCA_consolidated3_no1240_TOTEM",

    275832 : "fb_all_withuTCA_with_CTPPS_TOT",

    273301 : "fb_all_withuTCA_consolidated3_no1240_TOTEM",

    276870 : "fb_all",

    282092 : "fb_all_with1240_withCASTOR",

    283171 : "/daq2/eq_160913_01/fb_all_with1240_withCASTOR_w582_583",

    296702 : "/daq2/eq_170531/fb_all",
    }

def getFbsetFromRun(run):
    
    if not runToFbset.has_key(run):
        raise Exception("don't know fbset for run " + str(run))

    return runToFbset[run]
