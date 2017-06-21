#!/usr/bin/env python

import sys, os

#----------------------------------------------------------------------

first_ls=78
last_ls=3484
ls_per_job=100

#----------------------------------------------------------------------

def runJob(startLS, lastLS, background):
    logFname = "log-$RUN-%04d-%04d.log" % (startLS, lastLS)

    cmd = "cmsRun fedsizeanalyzer_cfg.py " + str(startLS) + " " + str(lastLS) + \
        " hltphysics $RUN"

    cmd = "nice -n 10 " + cmd

    if background:
        cmd += " > " + logFname + " 2>&1 &"
    else:
        cmd += " 2>&1 | tee " + logFname

    print "running",cmd
    os.system(cmd)

#----------------------------------------------------------------------

ARGV = sys.argv[1:]

if len(ARGV) == 0:
  for startLS in range(first_ls, last_ls + 1, ls_per_job):

    lastLS=startLS + ls_per_job - 1

    runJob(startLS, lastLS, background = True)

elif len(ARGV) == 2:

  startLS = int(ARGV[0])
  lastLS = int(ARGV[1])

  runJob(startLS, lastLS, background = False)

else:
  print "unexpected number of command line arguments"
  sys.exit(1)
