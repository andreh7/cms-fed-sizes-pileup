#!/usr/bin/env python

import os, sys, commands, re

# script to interactively run the first steps needed to
# setup the configuration files

#----------------------------------------------------------------------
# parameters
#----------------------------------------------------------------------

cacheFname = "initialize.cache.py"

#----------------------------------------------------------------------
def readString(prompt, defaultValue = None):
    print prompt,

    if defaultValue != None:
        print "(default=" + str(defaultValue) + ")",

    print "",

    value = sys.stdin.readline()

    value = value.split('\n')[0]
    if value == "":
        return defaultValue

    return value

#----------------------------------------------------------------------

def askYesNo(prompt, default = None):
    prompt += "(y/n"

    defaultString = None
    if default != None:
        prompt += ", default="
        if default:
            defaultString = "Y"
        else:
            defaultString = "N"

        prompt += defaultString
    prompt += ")"

    while True:
        value = readString(prompt, defaultString)

        if value != None:
            if value.upper() == 'Y':
                return True

            if value.upper() == 'N':
                return False

        print "please answer y or n"

    


#----------------------------------------------------------------------
def findInitialCMSSWrelease():
    """ used to find an initial CMSSW release
    to run dbsql """

    # assume that we have scram in the path
    lines = commands.getoutput("scram list -c CMSSW").splitlines()

    versionAndDir = []

    for line in lines:
        # example line:
        #
        # CMSSW           CMSSW_5_1_1               /afs/cern.ch/cms/slc5_amd64_gcc462/cms/cmssw/CMSSW_5_1_1

        dummy, version, dir = re.split('\s+',line.strip())

        # take the highest version with just plain numbers
        # (no integration builds, no patches, no prereleases)
        mo = re.match("CMSSW_(\d+)_(\d+)_(\d+)", version)
        if not mo:
            continue

        versionAndDir.append(
            [ (int(mo.group(1)),
               int(mo.group(2)),
               int(mo.group(3)),
               ),
            dir])


    # end of loop over all lines
    if not versionAndDir:
        print >> sys.stderr,"no suitable CMSSW version found for dbsql, exiting"
        sys.exit(1)

    # sort them
    versionAndDir.sort(lambda x,y: cmp(x[0],y[0]))

    # print >> sys.stderr, "using",versionAndDir[-1]
    return versionAndDir[-1][1]

#----------------------------------------------------------------------

def writeCache():
    fout = open(cacheFname,"w")

    for var in [ 'run',
                 'rawDataSet',
                 'recoDataSet',
                 'sampleName',
                 ]:

        value = globals().get(var,None)

        print >> fout,var,"=",

        if isinstance(value,str):
            # does not do escaping but not needed here
            print >> fout,'"' + value + '"'
        else:
            print >> fout,str(value)

    fout.close()

#----------------------------------------------------------------------

def selectDatasets():
    global cmsswDir 
    global run
    global rawDataSet, recoDataSet
    
    
    cmdParts = ["cd " + cmsswDir,
                " && ",
                "eval `scram runtime -sh`"
                " && ",
                "dbsql 'find dataset where run = " + str(run) + "'"
                ]

    cmd = " ".join(cmdParts)

    datasets = []

    print >> sys.stderr,"running dbsql..."
    output = commands.getoutput(cmd)

    for line in output.splitlines():
        # just take all lines which start with a '/'
        if not line.startswith('/'):
            continue

        # ignore some data tiers
        if line.endswith("/ALCARECO"):
            continue

        if line.endswith("/ALCAPROMPT"):
            continue

        if line.endswith("/DQM"):
            continue

        datasets.append(line)

    print
    print "found the following datasets:"
    for index, dataset in enumerate(datasets):
        print "%2d %s" % (index + 1, dataset)

    print

    try:
        index = datasets.index(globals().get('rawDataSet',None)) + 1
    except Exception:
        index = None
    
    index = int(readString("select raw dataset:", index))
    rawDataSet = datasets[index - 1]


    try:
        index = datasets.index(globals().get('recoDataSet',None)) + 1
    except Exception:
        index = None

    index = int(readString("select reco dataset:", index))
    recoDataSet = datasets[index - 1]

    return rawDataSet, recoDataSet

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------

global run

if os.path.exists(cacheFname):
    execfile(cacheFname)

run = int(readString("enter run number:", globals().get("run", None)))
writeCache()

global cmsswDir
cmsswDir = findInitialCMSSWrelease()

global rawDataSet, recoDataSet

rawDataSet, recoDataSet = selectDatasets()
writeCache()



#--------------------
# ask for sample description
#--------------------
global sampleName
sampleName = readString("enter a sample description name (e.g. minbias):",globals().get("sampleName",None))
writeCache()


#--------------------
# create the file list
#--------------------

print >> sys.stderr,"creating the file list"

fileListFname = "file_list_" + sampleName + "_" +str(run) + ".py"

runCommand = True

if os.path.exists(fileListFname):
    runCommand = askYesNo("file list '" + fileListFname + "' exists already, do you want to overwrite it ?")

if runCommand:

    cmdParts = [
        "./cms.print-raw-and-reco-files-vs-lumisection.py",
        "--run=" + str(run),
        rawDataSet,
        recoDataSet,
        "> " + fileListFname,
        ]

    cmd = " ".join(cmdParts)

    print >> sys.stderr,"querying dbs to produce the file list"
    res = os.system(cmd)

    if res != 0:
        print >> sys.stderr,"failed to run command",cmd
        sys.exit(1)

    assert(os.path.exists(fileListFname))
    print >> sys.stderr,"created file list " + fileListFname

#----------------------------------------
# copy fedsizeanalyzer-XXX.py from the highest run number
# found so far

# TODO: copy perNumVertexNtupleMaker-XXX.py from the highest run number
#       found so far

#----------------------------------------


print
print "setup for the environment:"
print

print "export RUN=" + str(run)
print "export RAWDATASET=" + rawDataSet
print "export RECODATASET=" + recoDataSet
print
print "castor directory: /castor/cern.ch/user/a/aholz/fed-size-analysis/" + str(run)
print

