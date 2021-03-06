#!/usr/bin/env python

import sys, os
scriptDir = os.path.dirname(sys.argv[0])

sys.path.insert(0,os.path.join(scriptDir, "../../.."))
import initialize

import psutil
numPhysicalCores = psutil.cpu_count(logical=False)


#----------------------------------------------------------------------

import threading

class Runner(threading.Thread):

    def __init__(self, jobIndex, totNumJobs, run, dstitle, startLs, lastLs):
        threading.Thread.__init__(self)
        self.jobIndex = jobIndex
        self.totNumJobs = totNumJobs
        self.runNumber = run
        self.dstitle = dstitle
        self.startLs = startLs
        self.lastLs = lastLs

        rundir = scriptDir

        cmdParts = [
            "cd " + rundir,
            " && ",
            # need export to see it from subprocesses 
            "export RUN=%d" % run,
            ";",
            "cmsRun",
            "fedsizeanalyzer_cfg.py",
            self.startLs,
            self.lastLs,
            dstitle,
            run,
            "> out-%d-%s-%04d-%04d.log 2>&1" % (run, dstitle, startLs, lastLs)
            ]

        self.cmd = " ".join([ str(x) for x in cmdParts])
        self.status = None


    def run(self):
        global threadLimiter
        threadLimiter.acquire()
        try:
            print >> sys.stderr,"starting %d/%d" % (self.jobIndex + 1, self.totNumJobs),"run",self.runNumber,"ds",self.dstitle,"ls %d..%d" % (self.startLs, self.lastLs)
            self.status = os.system(self.cmd)
            print >> sys.stderr,"finished %d/%d" % (self.jobIndex + 1, self.totNumJobs),"run",self.runNumber,"ds",self.dstitle,"ls %d..%d" % (self.startLs, self.lastLs),"status=",self.status

        finally:
            threadLimiter.release()        


#----------------------------------------------------------------------
# main 
#----------------------------------------------------------------------

initialize.ensureCmsEnv()

from argparse import ArgumentParser, RawTextHelpFormatter

parser = ArgumentParser(
    description =
     """
      run cmsRun jobs

    """,
    formatter_class=RawTextHelpFormatter,
)
parser.add_argument("--run",
                    type = int,
                    help = "run to analyze",
                    required = True,
                    )

parser.add_argument("--dstitle",
                    type = str,
                    help = "short name (selected by user) for the dataset to distinguish e.g. multiple analyses on same run",
                    required = True,
                    )

parser.add_argument("--json",
                    type = str,
                    help = "path of json file with good lumi sections",
                    required = True,
                    )


parser.add_argument("--num-parallel",
                    type = int,
                    dest = "maxNumThreads",
                    help = "maximum number of cmsRun executables to run at the same time (default: number of physical cores, %d on this machine)" % numPhysicalCores,
                    default = numPhysicalCores,
                    )

parser.add_argument("--skip",
                    type = str,
                    dest = "skipStartLs",
                    help = "comma separated list of start lumi sections for jobs to be skipped",
                    default = None,
                    )

parser.add_argument("--njobs",
                    type = int,
                    help = "number of jobs to split this task into",
                    default = 10,
                    )

options = parser.parse_args()

#----------------------------------------

runDir = os.path.join(os.environ["CMSSW_BASE"], "src/FedSizeAnalysis/FedSizeAnalyzer")


# get lumi sections for this run we should run over
# and distribute them over the jobs
lumiSections = initialize.getLumiSectionsForRun(options.json, options.run)

lumiSections.sort()

# round down
lsPerJob = len(lumiSections) / options.njobs

# determine how many jobs get one lumi section more
lsPerJobRemainder = len(lumiSections) % options.njobs

tasks = []
print "maxNumThreads=",options.maxNumThreads
threadLimiter = threading.BoundedSemaphore(options.maxNumThreads)


for i in range(options.njobs):
    if i < lsPerJobRemainder:
        thisNumLs = lsPerJob + 1
    else:
        thisNumLs = lsPerJob

    thisLumiSections = lumiSections[:thisNumLs]

    # create the job object
    tasks.append(Runner(i, 
                        options.njobs,
                        options.run,
                        options.dstitle,
                        min(thisLumiSections),
                        max(thisLumiSections)))

    lumiSections = lumiSections[thisNumLs:]

assert len(lumiSections) == 0
assert len(tasks) == options.njobs

# skip selected jobs
if options.skipStartLs:
    options.skipStartLs = set([ int(x) for x in options.skipStartLs.split(',') ])

    # insist that all specified jobs to skip are there
    for startLs in options.skipStartLs:
        indices = [ index for index,task in enumerate(tasks) if task.startLs == startLs ]
        assert len(indices) <= 1
        if len(indices) < 1:
            print >> sys.stderr,"could not find any task starting with ls",startLs,"to skip, exiting"
            sys.exit(1)
        
        del tasks[indices[0]]

print >> sys.stderr, "have",len(tasks),"active tasks"

# start all tasks
for task in tasks:
    task.start()

# wait for all tasks to complete
for task in tasks:
    task.join()

