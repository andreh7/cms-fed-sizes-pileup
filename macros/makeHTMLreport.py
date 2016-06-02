#!/usr/bin/env python

# given a plot output directory, produces a HTML report

import sys, os

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
ARGV = sys.argv[1:]

assert len(ARGV) == 1

tasksFile = ARGV.pop(0)

import pickle

all_tasks = pickle.load(open(tasksFile))

plotDir = os.path.dirname(tasksFile)

from HTMLReportMaker import HTMLReportMaker
outputFname = os.path.join(plotDir, "report.html")

reportMaker = HTMLReportMaker(all_tasks)

fout = open(outputFname, "w")
fout.write(reportMaker.make())
fout.close()

print >> sys.stderr,"wrote report to", outputFname

