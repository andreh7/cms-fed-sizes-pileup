#!/usr/bin/env python

# initializes the setup for a new run and dataset

import sys, os

#----------------------------------------------------------------------

def getLocalJsonFname(tasks):
    # finds the name of the json file created on the local file system
    # from the previous tasks

    # get the name of the local json file
    for task in tasks:
        if isinstance(task, JsonFileCopy):
            return task.outputFname
    
    # not found
    return None

#----------------------------------------------------------------------
class FileListMaker:
    def __init__(self, options, prevTasks, runDir):
        sys.path.append(runDir)
        self.options = options

        self.outputFname = os.path.join(runDir, "file_list_" + options.dstitle + "_" + str(options.run) + ".py")

        self.name = 'make_file_list'
    #----------------------------------------

    def needsRunning(self):
        return not os.path.exists(self.outputFname)
    #----------------------------------------

    def doRun(self):
        import makeFileList
        makeFileList.ensureDasClientExists()

        output_data = makeFileList.findFiles(options.rawDataSet, options.recoDataSet, options.run)
        makeFileList.printData(output_data, self.outputFname)

        print >> sys.stderr,"wrote",self.outputFname

#----------------------------------------------------------------------

class JsonFileCopy:
    def __init__(self, options, prevTasks, runDir):
        self.origJsonFile = options.jsonFile
        self.name = 'copy_json'

        parts = os.path.splitext(os.path.basename(self.origJsonFile))

        self.outputFname = os.path.join(runDir, parts[0] + "-" + str(options.run) + parts[1])

    #----------------------------------------

    def needsRunning(self):
        return not os.path.exists(self.outputFname)
    #----------------------------------------

    def doRun(self):

        status = os.system("scp -p lxplus.cern.ch:" + self.origJsonFile + " " + self.outputFname)
        assert(status == 0)

        print >> sys.stderr,"wrote",self.outputFname


#----------------------------------------------------------------------

class Step1ConfigFile:
    # creates a config file for step1 from the template

    def __init__(self, options, prevTasks, runDir):
        self.name = 'step1_config_file'

        self.jsonFile = getLocalJsonFname(prevTasks)
        assert self.jsonFile is not None

        self.outputFname = os.path.join(runDir, 
                                       "fedsizeanalyzer-" + str(options.run) + ".py")

        self.templateFile = os.path.join(runDir, 
                                         "fedsizeanalyzer-template.py")


    #----------------------------------------

    def needsRunning(self):
        return not os.path.exists(self.outputFname)

    #----------------------------------------

    def doRun(self):
        text = open(self.templateFile).read()

        output = text.format(text, JSONFILE=os.path.basename(self.jsonFile))

        fout = open(self.outputFname, "w")
        fout.write(output)
        fout.close()

        print >> sys.stderr,"wrote",self.outputFname

#----------------------------------------------------------------------

class MakeRunScript:

    def __init__(self, options, prevTasks, runDir):
        self.name = 'step1_config_file'

        self.dstitle = options.dstitle
        self.run = options.run

        jsonFile = getLocalJsonFname(tasks)
        assert jsonFile is not None

        # get the lumi section range for our run
        # (for the moment we only care about the minimum and maximum)

        import json
        lumiSecs = json.load(open(jsonFile))

        # get the good lumi sections for the run in question
        lumiSecs = lumiSecs[str(options.run)]
        
        # lumiSecs is now a list of (min,max) pairs
        self.firstLs = min( x[0] for x in lumiSecs)
        self.lastLs  = max( x[1] for x in lumiSecs)

        self.outputFname = os.path.join(runDir, 
                                       "run-" + str(options.run) + "-" + self.dstitle + ".sh")

        self.templateFile = os.path.join(runDir, 
                                         "run-template.sh")

    #----------------------------------------

    def needsRunning(self):
        return not os.path.exists(self.outputFname)

    #----------------------------------------

    def doRun(self):
        text = open(self.templateFile).read()

        output = text.format(text, 
                             firstLs = self.firstLs,
                             lastLs = self.lastLs,
                             dstitle = self.dstitle,
                             run = self.run,
                             )

        fout = open(self.outputFname, "w")
        fout.write(output)
        fout.close()

        os.chmod(self.outputFname, 0755)

        print >> sys.stderr,"wrote",self.outputFname
    

#----------------------------------------------------------------------
# main 
#----------------------------------------------------------------------

assert os.environ.has_key('CMSSW_BASE'), "CMSSW_BASE environment variable not set, did you run cmsenv ?"

from argparse import ArgumentParser, RawTextHelpFormatter

parser = ArgumentParser(
    description =
     """
     performs setup operations for a new run
    """,
    formatter_class=RawTextHelpFormatter,
)
parser.add_argument("--run",
                    type = int,
                    help = "run to analyze",
                    required = True,
                    )

parser.add_argument("--raw",
                    dest = "rawDataSet",
                    type = str,
                    help = "comma separated list of RAW datasets",
                    required = True,
                    )

parser.add_argument("--reco",
                    dest = "recoDataSet",
                    type = str,
                    help = "comma separated list of RECO/AOD/MINIAOD datasets",
                    required = True,
                    )

parser.add_argument("--dstitle",
                    type = str,
                    help = "short name (selected by user) for the dataset to distinguish e.g. multiple analyses on same run",
                    required = True,
                    )

parser.add_argument("--json",
                    type = str,
                    dest = "jsonFile",
                    help = "original json file on lxplus for lumi section validation",
                    required = True,
                    )

options = parser.parse_args()
#----------------------------------------

options.rawDataSet  = options.rawDataSet.split(',')
options.recoDataSet = options.recoDataSet.split(',')

runDir = os.path.join(os.environ["CMSSW_BASE"], "src/FedSizeAnalysis/FedSizeAnalyzer")

tasks = []
for clazz in [
    FileListMaker,
    JsonFileCopy,
    Step1ConfigFile,
    MakeRunScript,
    ]:
    tasks.append(clazz(options, tasks, runDir))

for task in tasks:
    if not task.needsRunning():
        print >> sys.stderr, "skipping",task.name
        continue
    
    print >> sys.stderr, "running",task.name
    task.doRun()




