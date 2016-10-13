#!/usr/bin/env python
import array, sys, os, pprint


#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
# read the parameters from a file

ARGV = sys.argv[1:]

if len(ARGV) > 1:
    print >> sys.stderr,"must specify at most one command line argument (a file with plotting parameters)"
    sys.exit(1)

# import parameters
# execfile(ARGV[0])
import utils
parameters = utils.loadParameters()

#----------------------------------------------------------------------
# ROOT setup
#----------------------------------------------------------------------
import ROOT

# speed up plotting by not talking to an X server
ROOT.gROOT.SetBatch(1)

ROOT.gROOT.ProcessLine(".x ~/rootlogon.C")
ROOT.gROOT.ProcessLine("setTDRStyle();")
ROOT.gStyle.SetErrorX(0.5)

#----------
# increase maximum number of operators (basically for plotting
# the sum of all FED sizes), see https://root.cern.ch/phpBB3/viewtopic.php?t=8218
# 
# this does not work unfortunately, this leafs to a segmentation violation...
# ROOT.v5.TFormula.SetMaxima(1100)
#----------


gc_saver = []

# single file
# fin = ROOT.TFile.Open("../data/myOutputFile.root")
# Events = fin.Get("Events")

# produce a chain
Events = ROOT.TChain("Events")
Events.Add(parameters.input_data_dir + "/*.root")

#----------------------------------------------------------------------
# global variables
#----------------------------------------------------------------------

num_events = None

# a simple tuple with the values used here
# calculated from the original CMSSW tree

from SmallTuple import SmallTuple
small_tuple = SmallTuple(parameters)

#----------------------------------------

def groupInts(integer_list):
    """ groups a list of integers into 'ranges',
     see http://stackoverflow.com/questions/3429510

     returns a list of tuples (min,max)

     """
    import itertools

    groups = (list(x) for it, x in itertools.groupby(integer_list,
                                                     lambda x,c=itertools.count(): next(c)-x))

    return [ (g[0], g[-1]) for g in groups ]

#----------------------------------------

def getNumEvents():

    if num_events == None:
        num_events = Events.GetEntries()

    return num_events

#----------------------------------------------------------------------

from NumVertices import NumVertices
from FedSizeDist import FedSizeDist
from FedSizePerVertexLinearFit import FedSizePerVertexLinearFit
from NumVerticesPerLumiSection import NumVerticesPerLumiSection
from NumEventsPerLumiSection import NumEventsPerLumiSection

#----------------------------------------------------------------------
# checking which lumisections appear in the file and
# print these (no plotting here)
#----------------------------------------------------------------------
class PrintLumiSectionsFound:

    def produce(self):
        # get the list of all lumisections
        lumi_sections = getAllLumiSections()

        # print "XX",len(lumi_sections)

        # now group them and print this

        ranges = groupInts(lumi_sections)

        print "lumisections found:", \
              ",".join([
                  "%d-%d" % (x[0],x[1]) if x[0] != x[1] else "%d" % x[0]
            for x in ranges ])
            


    #----------------------------------------
    def plot(self):
        pass


    #----------------------------------------

from LuminosityEvolution import LuminosityEvolution

#----------------------------------------------------------------------
class PerFedSize():
    pass


#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------

# fit the 


#----------------------------------------
# cross check: number of feds should be
#              the same throughout the run
#----------------------------------------


# Events.Draw("fedSizeData.getNumFeds()")
# for the run analyzed, this is always 635

#----------------------------------------
# Events.Draw("fedSizeData.getSumAllFedSizes()")

#----------------------------------------------------------------------
from FedSizePerBXlumiLinearFit import FedSizePerBXlumiLinearFit

all_tasks = [
    # PrintLumiSectionsFound(),
    NumVertices(parameters, small_tuple),
    # FedSizeDist(parameters, small_tuple),
    
    # global, not per subsystem
    # but for the moment still needs
    # the per vertex ntuples
    # FedSizePerVertexLinearFit(parameters),

    # per BX lumi is not available anymore
    # in the event in LHC Run II
    # FedSizePerBXlumiLinearFit(parameters),
    
    NumEventsPerLumiSection(parameters, small_tuple),
    NumVerticesPerLumiSection(parameters, small_tuple),
    LuminosityEvolution(parameters, small_tuple),

    # this is not yet implemented (or not needed any more ?)
    # PerFedSize(),
    ]

#--------------------

if True:

    #----------
    # read the input data once
    #----------
    inputTupleName = os.path.join(parameters.input_data_dir,"small-tuples.root")

    from FedSizeMatrix import FedSizeMatrix
    fedSizeMatrix = FedSizeMatrix()
    fedSizeMatrix.read(inputTupleName, parameters.max_num_vertices,
                       parameters.fedsInRun)

    for line in parameters.allSubsysToPlot:

        # expect a dict
        assert isinstance(line, dict)

        subsys = line['label']
        fedIds = line['fedIds']
        grouping = line.get('grouping', None)

        yaxis_unit_label = "kB"
        y_scale_factor = 1.

        if subsys == "total":
            yaxis_unit_label = "MB"
            y_scale_factor = 0.001


        thisTask = FedSizePerVertexLinearFit(parameters, 
                                             fedSizeMatrix, 
                                             fedIds = fedIds,
                                             subsys_name = subsys,
                                             grouping_name = grouping,
                                             yaxis_unit_label = yaxis_unit_label,
                                             y_scale_factor = y_scale_factor,
                                             legendBottomLeft = parameters.fedSizePerVertexLinearFitLegendPositions(parameters.run, subsys),
                                             )

        thisTask.instanceName = subsys
        all_tasks.append(thisTask)

#----------------------------------------------------------------------
# collect information about the evolution of the fed sizes
# per subsystem ('grand unification plot')
#----------------------------------------------------------------------
from GrandUnificationPlot import GrandUnificationPlot

for grouping in [
    "by subsystem",
    ]:
    all_tasks.append(GrandUnificationPlot(parameters, all_tasks, grouping,
                                          printCSV = True,
                                          )
                     )


# special version for fedbuilders size at 30 vertices
# GrandUnificationPlot.makeGrandUnificationPlot(outputFiles, subsystemEvolutionData, xmax = 50, printCSV = True,
#                          # sort according to size at given number of vertices
#                          keyFunc = lambda x: x['slope'] * 30 + x['offset'],
#                          subsystemsTitle = 'FEDBuilder',
# 
#                          labelTextFunc = lambda subsystem, offset, slope: "%s (%.2f kB/ev @ 30 vertices)" % (subsystem, offset + 30 * slope),
#                          )

# 'Grand Unification Plot' for per fed rate
# GrandUnificationPlot.makeGrandUnificationPlot(outputFiles, subsystemEvolutionData, triggerRate = 100, xmax = 50, printCSV = True)


#----------------------------------------------------------------------

# FOR TESTING 
# all_tasks = [ FedSizePerVertexLinearFit(parameters), ]
# all_tasks = [ FedSizePerBXlumiLinearFit(parameters), ]

# list of output files (needed to produce a zip file)
outputFiles = []

duplicateOutputFilesWarnings = []

for taskIndex, task in enumerate(all_tasks):

    print "#----------------------------------------"
    print "# producing",task.__class__.__name__,

    if hasattr(task,'instanceName'):
        print "(%s)" % task.instanceName,

    print
    print "#----------------------------------------"
    task.produce()

    print "#----------------------------------------"
    print "# plotting",task.__class__.__name__,
    if hasattr(task,'instanceName'):
        print "(%s)" % task.instanceName,
    print
    print "#----------------------------------------"
    task.plot(outputFilePrefix = "%04d-" % taskIndex)

    thisOutputFiles = task.outputFiles

    # check that we do not have duplicate output files
    for outputFile in thisOutputFiles:
        outputFile = outputFile['fname']

        if outputFile in outputFiles:
            duplicateOutputFilesWarnings.append("task %d (%s) produces duplicate output file %s"  %
                                                (taskIndex, task.__class__.__name__, outputFile))

        if not os.path.exists(outputFile):
            duplicateOutputFilesWarnings.append("task %d (%s) claims to produce file %s but it does not exist" % 
                                                (taskIndex, task.__class__.__name__, outputFile))

    outputFiles.extend(thisOutputFiles)

if duplicateOutputFilesWarnings:
    for line in duplicateOutputFilesWarnings:
        print >> sys.stderr,"WARNING:",line

#----------------------------------------

# print "output files"
# pprint.pprint(outputFiles)

import tempfile
summaryOutputFilesDir = tempfile.mkdtemp()

#----------------------------------------
# create a zip file with the generated plots/files
#----------------------------------------

import zipfile

zipfname = summaryOutputFilesDir + "/plots-%d.zip" % parameters.run
fout = zipfile.ZipFile(zipfname,"w")

for outputFile in outputFiles:
    fout.write(outputFile['fname'])

fout.close()

print >> sys.stderr,"wrote plots to " + zipfname
print >> sys.stderr,"plots output directory is",parameters.output_data_dir

#----------------------------------------
# creat a powerpoint file if the
# corresponding tool is found
#----------------------------------------
plotReportMakerJar = os.path.expanduser("~/bin/PlotReportMaker-1.0-SNAPSHOT-jar-with-dependencies.jar")

if os.path.exists(plotReportMakerJar):

    pptFname = summaryOutputFilesDir + "/plots-%d.ppt" % parameters.run

    #--------------------
    # create a configuration file, based
    # on the plots created
    #--------------------

    lines = [
        "config = ProjectData()",
        'config.reportOutputFileName = "%s"' % pptFname,
        'config.addToc = False',
        ]

    # add plots
    for outputFile in outputFiles:

        fname = outputFile['fname']

        if not fname.endswith(".png"):
            # do NOT include .C files etc.
            continue

        description = outputFile.get('description','no description available')
        lines.extend([
            "",
            "plot = PlotDescription()",
            'plot.shortName = "%s"' % fname,
            'plot.plotFileName = "%s"' % fname,
            'plot.description = "%s"' % description,
            'config.addPlot(plot)'
            ])

    # import pprint
    # pprint.pprint(lines)

    # write the generated configuration
    (fd, fname) = tempfile.mkstemp(suffix = ".py")
    fout = open(fname,"w")
    for line in lines:
        print >> fout,line

    fout.close()

    #--------------------

    # run the command
    cmd = " ".join([
        "java -jar",
        "-Dpython.cachedir=/tmp", # needed for Jython 2.2
        plotReportMakerJar,
        fout.name])

    res = os.system(cmd)

    if res != 0:
        raise Exception("failed to create powerpoint file " + pptFname)
    else:
        print >> sys.stderr,"created powerpoint file " + pptFname

#----------------------------------------
# save task data for later reporting
#----------------------------------------

tasksOutputFile = os.path.join(parameters.plots_output_dir, "allTasks.pkl")
print >> sys.stderr,"writing task data to",tasksOutputFile
fout = open(tasksOutputFile, "w")
import cPickle as pickle
pickle.dump(all_tasks, fout)
fout.close()


