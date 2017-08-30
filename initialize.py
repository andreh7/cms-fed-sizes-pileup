#!/usr/bin/env python

# initializes the setup for a new run and dataset

import sys, os


#----------------------------------------------------------------------
class FileListMaker:
    def __init__(self, options, prevTasks):
        sys.path.append(os.path.join(os.environ["CMSSW_BASE"], "src/FedSizeAnalysis/FedSizeAnalyzer"))
        self.options = options

        self.outputFname = os.path.join(os.environ["CMSSW_BASE"],
                                        "src/FedSizeAnalysis/FedSizeAnalyzer",
                                        "file_list_" + options.dstitle + "_" + str(options.run) + ".py")

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
    def __init__(self, options, prevTasks):
        self.origJsonFile = options.jsonFile
        self.name = 'copy_json'

        parts = os.path.splitext(os.path.basename(self.origJsonFile))

        self.outputFname = os.path.join(os.environ["CMSSW_BASE"],
                                        "src/FedSizeAnalysis/FedSizeAnalyzer",
                                        parts[0] + "-" + str(options.run) + parts[1])

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

    def __init__(self, options, prevTasks):
        self.name = 'step1_config_file'

        self.jsonFile = None

        # get the name of the local json file
        for task in prevTasks:
            if isinstance(task, JsonFileCopy):
                self.jsonFile = task.outputFname

        assert self.jsonFile is not None

        workdir = os.path.join(os.environ["CMSSW_BASE"],
                                       "src/FedSizeAnalysis/FedSizeAnalyzer")

        self.outputFname = os.path.join(workdir, 
                                       "fedsizeanalyzer-" + str(options.run) + ".py")

        self.templateFile = os.path.join(workdir, 
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

tasks = []
for clazz in [
    FileListMaker,
    JsonFileCopy,
    Step1ConfigFile,
    ]:
    tasks.append(clazz(options, tasks))

for task in tasks:
    if not task.needsRunning():
        print >> sys.stderr, "skipping",task.name
        continue
    
    print >> sys.stderr, "running",task.name
    task.doRun()




