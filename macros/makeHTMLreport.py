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

reportData = pickle.load(open(tasksFile))
all_tasks = reportData['tasks']

run     = reportData['globalParams']['run']
dataset = reportData['globalParams']['dataset']
xvar    = reportData['globalParams']['xvar']


plotDir = os.path.dirname(tasksFile)

from HTMLReportMaker import HTMLReportMaker
outputFname = os.path.join(plotDir, "report-%d-%s.html" % (run, dataset))

reportMaker = HTMLReportMaker(all_tasks, run, dataset, xvar)

fout = open(outputFname, "w")
fout.write(reportMaker.make())
fout.close()

print >> sys.stderr,"wrote report to", outputFname

#----------
# also write out the spreadsheet (for convenience)
#----------
spreadsheetOutputFname = os.path.join(plotDir, "evolution-%d-%s.xlsx" % (run, dataset))
reportMaker.spreadSheetCreator.writeToFile(spreadsheetOutputFname)
print >> sys.stderr,"wrote spreadsheet to",spreadsheetOutputFname
