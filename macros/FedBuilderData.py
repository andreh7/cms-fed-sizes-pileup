#!/usr/bin/env python

import glob, re

# first key: dpset name
# value: list of fedbuilder dicts
fedBuilderGroups = {}

for fname in glob.glob("hwdb/fbset-*.py"):
    execfile(fname)

#----------------------------------------------------------------------
# utility functions
#----------------------------------------------------------------------

def fedbuilderFromFed(run, fed):

    # find the fedbuilder the given fed belongs to
    for line in fedBuilderGroups:
        if fed in line['feds']:
            return line['name']

    # not found
    return None

#----------------------------------------------------------------------
