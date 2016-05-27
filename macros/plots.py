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
ROOT.gROOT.ProcessLine(".x ~/rootlogon.C")
ROOT.gROOT.ProcessLine("setTDRStyle();")
ROOT.gStyle.SetErrorX(0.5)

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

def weightedAverage(values, weights):
    """ calculates a weighted average.
        numpy seems not to be available for the CMSSW python installation,
    so we have to do it by hand..."""

    sum_value_times_weight = 0

    for val, weight in zip(values,weights):
        sum_value_times_weight += val * weight

    return sum_value_times_weight / sum(weights)

#----------------------------------------------------------------------
# number of primary vertices found
#----------------------------------------------------------------------

class NumVertices:
    """ DOES THIS MAKE SENSE HERE ? BECAUSE WE ALREADY ASSUME
    THAT WE KNOW THE MAXIMUM NUMBER OF VERTICES BEFOREHAND
    (VARIABLE max_num_vertices). """

    #----------------------------------------
    def __init__(self):

        self.histo_fname = parameters.output_data_dir + "/num_vertices.xml"

    #----------------------------------------
    def produce(self):

        draw_expr = "min(" + \
                    "num_vertices,%d" % parameters.max_num_vertices + \
                    ")>>histo_num_vertices(%d,-0.5,%.1f)" % (parameters.max_num_vertices + 1, parameters.max_num_vertices + 0.5)

                    # ")>>histo_num_vertices(8,-0.5,7.5)"

        small_tuple.tree.Draw(draw_expr)

        ROOT.histo_num_vertices.Sumw2()

        # save the histogram
        ROOT.histo_num_vertices.SaveAs(self.histo_fname)

    #----------------------------------------
        
    def plot(self):
        # load the histogram
        fin = ROOT.TFile.Open(self.histo_fname)

        global histo
        histo = fin.Get("histo_num_vertices")

        total_num_events = histo.GetEntries()

        #--------------------
        # fit the poissonian to the distribution starting at one

        numPoissonComponents = 1

        if numPoissonComponents == 1:
            func = ROOT.TF1("pois","[0]*TMath::Poisson(x,[1])",parameters.poisson_fit_start,parameters.poisson_fit_end)
            func.SetParName(0,"norm.")
            func.SetParName(1,"#mu")          
            func.SetParameter(0,1)
            func.SetParameter(1,0.5 * (parameters.poisson_fit_start + parameters.poisson_fit_end))
        elif numPoissonComponents == 2:
            # experimental: two Poissonians e.g. to capture multiple populations
            # originating from different triggers
            func = ROOT.TF1("pois","TMath::Abs([0])*TMath::Poisson(x,[1])+TMath::Abs([2])*TMath::Poisson(x,[3])",
                            parameters.poisson_fit_start,parameters.poisson_fit_end)

            func.SetParName(0,"sqrt(norm. 1)")
            func.SetParName(1,"#mu_{1}")
            func.SetParName(2,"sqrt(norm. 2)")
            func.SetParName(3,"#mu_{2}")

            func.SetParameter(0,1)
            func.SetParameter(1,10000)

            func.SetParameter(2,1)
            func.SetParameter(3,1)

            # note that we should use a reasonable estimate for the
            # upper limit due to the transformation ROOT internally
            # uses to map a finite range onto an unconstrained one...
            

        else:
            raise Exception("number Poisson components %d not yet supported" % numPoissonComponents)
            
        func.SetLineWidth(3)

        histo.SetMarkerStyle(20)
        histo.SetXTitle("Number of rec. primary vertices")
        histo.SetYTitle("Number of events")

        histo.Draw("Ep")

        if parameters.poissonFitYscalingFactor != None:
            histo.SetMaximum(parameters.poissonFitYscalingFactor * histo.GetMaximum())
            
        histo.Fit(func,"","",parameters.poisson_fit_start,parameters.poisson_fit_end)
        ROOT.gPad.Update()
        
        ROOT.gPad.SetLogy()
        ROOT.gPad.SetGrid()
        ROOT.gPad.Modified()

        stats = histo.FindObject("stats")
        stats.SetX1NDC(0.55)
        stats.SetY1NDC(0.73)
        stats.SetX2NDC(0.98)
        stats.SetY2NDC(0.99)
        ROOT.gPad.Modified()

        # calculate average number of vertices
        label = ROOT.TLatex(0.4,0.87,"num. events: %.0f" % total_num_events)
        label.SetNDC(1)
        label.Draw()

        #--------------------
        # get number of events per bin to calculate
        # the average number of vertices. 

        num_vertices_list = []
        num_events_list = []
        
        for i in range(1,histo.GetNbinsX()):
            num_vertices = histo.GetBinCenter(i)
            if num_vertices < 1:
                continue

            # print "num vertices: ",num_vertices, " events:",histo.GetBinContent(i)
            num_events_list.append(histo.GetBinContent(i))
            num_vertices_list.append(num_vertices)

        avg_num_vertices = weightedAverage(num_vertices_list, num_events_list)


        # print "average number of vertices:",self.avg_num_vertices

        label = ROOT.TLatex(0.2,0.2,"avg. # vertices: %.2f" % avg_num_vertices)
        label.SetNDC(1)
        label.Draw()

                                     
        ROOT.gPad.SaveAs(parameters.plots_output_dir + "/num-vertices-fitted.png")
        ROOT.gPad.SaveAs(parameters.plots_output_dir + "/num-vertices-fitted.C")
        fin.Close()

        #--------------------
        # write the average number of vertices also to a file
        # for later use in other tasks
        utils.writeStringToFile(parameters.plots_output_dir + "/avg-num-vertices.txt",str(avg_num_vertices) + "\n")

        #--------------------

        
        #--------------------
        fin = ROOT.TFile.Open(self.histo_fname)
        histo = fin.Get("histo_num_vertices")

        # draw the fraction
        histo.Scale(1/float(histo.GetEntries()))
        
        histo.SetMarkerStyle(20)
        histo.SetXTitle("number of rec. primary vertices")
        histo.SetYTitle("fraction of events")

        histo.Draw("Ep")
        
        ROOT.gPad.SetLogy()
        ROOT.gPad.SetGrid()

        label = ROOT.TLatex(0.4,0.87,"num. events: %.0f" % total_num_events)
        label.SetNDC(1)
        label.Draw()

        ROOT.gPad.SaveAs(parameters.plots_output_dir + "/num-vertices.png")

        fin.Close()
        ROOT.gROOT.cd()

        #--------------------
        # set output files
        #--------------------
        self.outputFiles = [
            dict(fname = parameters.plots_output_dir + "/num-vertices-fitted.png"),
            dict(fname = parameters.plots_output_dir + "/num-vertices.png"),
            dict(fname = parameters.plots_output_dir + "/avg-num-vertices.txt"),
        ]

#----------------------------------------------------------------------
# FED size distribution
#----------------------------------------------------------------------

class FedSizeDist:
    """ this uses the small tuple which only contains sum of all FED sizes
    per event, thus not very suitable to make per-subsystem plots.

    Should be merged though with the per-subdetector plotting.
    """
    histoMinimum = 1e-6

    scaleMaximum = 10

    #----------------------------------------
    def __init__(self):

        self.show_fraction = True

        # bin width in MB
        self.bin_width = ( parameters.fedsize_histo_xmax - parameters.fedsize_histo_xmin ) / float(parameters.fedsize_histo_nbins)

        print "bin_width=",self.bin_width

    #----------------------------------------
    def produce(self):

        # produce histograms of the fed size distributions

        for num_vertices in range(1,parameters.max_num_vertices + 1):

            histo_name = "fed_size_dist_" + str(num_vertices)

            plot_expr = "min(total_event_size/1e6,%f)>>%s(%d,%f,%f)" % \
                        (parameters.fedsize_histo_xmax * 0.999, 
                         histo_name,
                         parameters.fedsize_histo_nbins,
                         parameters.fedsize_histo_xmin, 
                         parameters.fedsize_histo_xmax
                         )

            cut_expr = "min(num_vertices,%d)" % (parameters.max_num_vertices) + " == %d" % num_vertices

            print "plot_expr=",plot_expr
            print "cut_expr=",cut_expr
            

            small_tuple.tree.Draw(plot_expr,cut_expr)

            # do we need errors and histogram normalization ?
            # ROOT.histo_num_vertices.Sumw2()

            # save the histogram
            # seems not to work
            # ROOT.gROOT.Get(histo_name).SaveAs("data/" + histo_name + ".xml")

            getattr(ROOT,histo_name).SaveAs(parameters.output_data_dir + "/" + histo_name + ".xml")

    #----------------------------------------
        
    def plot(self):

        global hs
        global legend

        hs = ROOT.THStack()
        legend = ROOT.TLegend(0.55,0.6,0.85,0.9)

        # define a color map
        colors = {
            1: 0
            }

        # create a color palette
        import array
        red = array.array('d',   [1,0.5])
        green = array.array('d', [0.5,0])
        blue = array.array('d',  [0.5,0])

        stops = array.array('d', [0,1])
        
        npoints = parameters.max_num_vertices

        first_color = ROOT.TColor.CreateGradientColorTable(len(stops), stops, red, green, blue, npoints)

        assert(first_color >= 0)

        #--------------------

        total_num_events = 0

        num_vertex_to_histo = {}

        for num_vertices in range(1,parameters.max_num_vertices + 1):

            histo_name = "fed_size_dist_" + str(num_vertices)

            fin = ROOT.TFile.Open(parameters.output_data_dir + "/" + histo_name + ".xml")
            
            histo = fin.Get(histo_name)

            num_vertex_to_histo[num_vertices] = histo

            # set color
            # histo.SetFillColor(ROOT.kOrange - num_vertices)
            histo.SetFillColor(first_color + num_vertices - 1)

            hs.Add(histo)

            if num_vertices == 1:
                title = "%d vertex" % num_vertices
            else:
                title = "%d vertices" % num_vertices
                
            legend.AddEntry(histo, title,"f")

            total_num_events += histo.GetEntries()

            fin.Close()
            ROOT.gROOT.cd()

        # this assumes that the entire sample is
        # cointained in the histograms together
        print "total_num_events=",total_num_events

        if self.show_fraction:
            for num_vertices in range(1,parameters.max_num_vertices + 1):            
                num_vertex_to_histo[num_vertices].Scale(1/float(total_num_events))

        if self.histoMinimum != None:
            hs.SetMinimum(self.histoMinimum)

        if self.scaleMaximum != None:
            hs.SetMaximum(hs.GetMaximum() * self.scaleMaximum)

        hs.Draw("nostack")

        hs.GetXaxis().SetTitle("Sum of FED sizes [MB]");

        if self.show_fraction:
            title = "fraction of events/%.2f MB" % self.bin_width
        else:
            title = "number of events/%.2f MB" % self.bin_width

        hs.GetYaxis().SetTitle(title);

        ROOT.gPad.SetLogy()
        ROOT.gPad.SetGrid()

        legend.Draw()

        ROOT.gPad.Modified()

        ROOT.gPad.SaveAs(parameters.plots_output_dir + "/fed-size-distributions-per-vertex.png")

        #--------------------
        # set output files
        #--------------------
        self.outputFiles = [
            dict(fname = parameters.plots_output_dir + "/fed-size-distributions-per-vertex.png"),
        ]

        
    #----------------------------------------

execfile("FedSizePerVertexLinearFit.py")

#----------------------------------------------------------------------
# number of events per lumi section
#----------------------------------------------------------------------
class NumEventsPerLumiSection:

    #----------------------------------------

    def __init__(self):
        pass

    #----------------------------------------

    def produce(self):
        # looks like it's fast to produce this plot,
        # no need to store an intermediate histogram for the moment
        pass

    #----------------------------------------
    def plot(self):

        #--------------------
        # determine the maximum luminosity section automatically
        small_tuple.tree.SetEstimate(small_tuple.tree.GetEntries())
        small_tuple.tree.Draw("lumisection","","goff")
        entries = small_tuple.tree.GetSelectedRows()

        v1 = small_tuple.tree.GetV1()
        lumisections = [ v1[index] for index in xrange(entries) ]

        max_lumi_section = int(max(lumisections) * 1.1)
        #--------------------

        # let root fill the histogram
        small_tuple.tree.Draw("lumisection>>htemp(%d,-0.5,%f)" %
                    (max_lumi_section, max_lumi_section - 0.5))

        ROOT.gPad.SetGrid()
        ROOT.gPad.SetLogy(0)

        ROOT.htemp.SetXTitle("Luminosity section")
        ROOT.htemp.SetYTitle("# events per luminosity section")


        
        ROOT.gPad.SaveAs(parameters.plots_output_dir + "/events-per-lumi-section.png")

        #--------------------
        # set output files
        #--------------------
        self.outputFiles = [
            dict(fname = parameters.plots_output_dir + "/events-per-lumi-section.png"),
            ]

    #----------------------------------------

#----------------------------------------------------------------------
# number of vertices as function of the lumi section
#----------------------------------------------------------------------
class NumVerticesPerLumiSection:

    #----------------------------------------

    def __init__(self):
        pass

    #----------------------------------------

    def produce(self):
        # looks like it's fast to produce this plot,
        # no need to store an intermediate histogram for the moment
        pass

    #----------------------------------------
    def plot(self):
        #--------------------
        # determine the maximum luminosity section automatically
        small_tuple.tree.SetEstimate(small_tuple.tree.GetEntries())
        small_tuple.tree.Draw("lumisection","","goff")
        entries = small_tuple.tree.GetSelectedRows()

        v1 = small_tuple.tree.GetV1()
        lumisections = [ v1[index] for index in xrange(entries) ]

        max_lumi_section = int(max(lumisections) * 1.1)
        #--------------------

        # let root fill the histogram
        # we call the histogram htemp2 to avoid problems
        # with the previous plotting step....
        small_tuple.tree.Draw("num_vertices:lumisection>>htemp2(%d,-0.5,%f)" % (max_lumi_section, max_lumi_section - 0.5),"",
                         "prof")

        ROOT.gPad.SetGrid()
        ROOT.gPad.SetLogy(0)

        ROOT.htemp2.SetXTitle("Luminosity section")
        ROOT.htemp2.SetYTitle("# vertices per event")
        
        ROOT.gPad.SaveAs(parameters.plots_output_dir + "/vertices-per-lumi-section.png")

        #--------------------
        # set output files
        #--------------------
        self.outputFiles = [
            dict(fname = parameters.plots_output_dir + "/vertices-per-lumi-section.png"),
            ]

    #----------------------------------------


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
    NumVertices(),
    FedSizeDist(),
    
    # global, not per subsystem
    # but for the moment still needs
    # the per vertex ntuples
    FedSizePerVertexLinearFit(),

    # per BX lumi is not available anymore
    # in the event in LHC Run II
    # FedSizePerBXlumiLinearFit(),
    
    NumEventsPerLumiSection(),
    NumVerticesPerLumiSection(),
    LuminosityEvolution(small_tuple),

    # this is not yet implemented (or not needed any more ?)
    # PerFedSize(),
    ]

#--------------------

if True:
    for line in parameters.allSubsysToPlot:

        # to keep backwards compatibility
        if isinstance(line,str):
            # old way
            subsys = line

            size_expr = subsys.lower()

            if not 'size' in size_expr:
                # assume it's a single subsystem
                size_expr = "size_" + size_expr

        else:
            # expect a dict
            subsys = line['label']
            size_expr = line['expr']
            

        yaxis_unit_label = "kB"
        yaxis_unit_size = 1e3


        if subsys == "total":
            yaxis_unit_label = "MB"
            yaxis_unit_size = 1e6


        thisTask = FedSizePerVertexLinearFit(size_expr = size_expr,
                                                   subsys_name = subsys,
                                                   yaxis_unit_label = yaxis_unit_label,
                                                   yaxis_unit_size = yaxis_unit_size,
                                                   legendBottomLeft = parameters.fedSizePerVertexLinearFitLegendPositions(parameters.run, subsys)
                                                   )

        thisTask.instanceName = subsys
        all_tasks.append(thisTask)
#----------------------------------------------------------------------

# FOR TESTING 
# all_tasks = [ FedSizePerVertexLinearFit(), ]
# all_tasks = [ FedSizePerBXlumiLinearFit.FedSizePerBXlumiLinearFit(), ]

# list of output files (needed to produce a zip file)
outputFiles = []

for task in all_tasks:

    print "#----------------------------------------"
    print "# producing",task.__class__.__name__,

    if hasattr(task,'instanceName'):
        print "(%s)" % task.instanceName

    print
    print "#----------------------------------------"
    task.produce()

    print "#----------------------------------------"
    print "# plotting",task.__class__.__name__,
    if hasattr(task,'instanceName'):
        print "(%s)" % task.instanceName
    print
    print "#----------------------------------------"
    task.plot()

    outputFiles.extend(task.outputFiles)

#----------------------------------------------------------------------
# collect information about the evolution of the fed sizes
# per subsystem
#----------------------------------------------------------------------

subsystemEvolutionData = []

for task in all_tasks:
    if not isinstance(task, FedSizePerVertexLinearFit):
        continue

    if task.subsys == 'total':
        continue

    # print sizes in kB (note that 'total' is in MB)
    # print "subsystem %-20s: #FEDS=%3d offset=%8.3f kByte slope=%8.3f kByte/vtx" % (task.subsys, task.numFeds, task.alpha, task.beta)
    subsystemEvolutionData.append({"subsystem":  task.subsys, "offset":   task.alpha, "slope":  task.beta, "numFeds": task.numFeds})

#----------------------------------------
# persistently store the subsystemEvolutionData
#----------------------------------------
if True:
    import cPickle as pickle
    fout = open(parameters.output_data_dir + "/subsystemEvolutionData.pkl","w")
    pickle.dump(subsystemEvolutionData, fout)
    fout.close()

#----------------------------------------
# load subsystemEvolutionData from pickled file
#----------------------------------------

if False:
    import cPickle as pickle
    fin = open(parameters.output_data_dir + "/subsystemEvolutionData.pkl")
    subsystemEvolutionData = pickle.load(fin)
    fin.close()


#----------------------------------------

# import pprint
# pprint.pprint(subsystemEvolutionData)

import GrandUnificationPlot


# standard 'Grand Unification Plot' for subsystem sizes
GrandUnificationPlot.makeGrandUnificationPlot(outputFiles, subsystemEvolutionData,
                                              printCSV = True,
                                              )


# special version for fedbuilders at 30 vertices
# GrandUnificationPlot.makeGrandUnificationPlot(outputFiles, subsystemEvolutionData, xmax = 50, printCSV = True,
#                          # sort according to size at given number of vertices
#                          keyFunc = lambda x: x['slope'] * 30 + x['offset'],
#                          subsystemsTitle = 'FEDBuilder',
# 
#                          labelTextFunc = lambda subsystem, offset, slope: "%s (%.2f kB/ev @ 30 vertices)" % (subsystem, offset + 30 * slope),
#                          )

# 'Grand Unification Plot' for per fed rate
# GrandUnificationPlot.makeGrandUnificationPlot(outputFiles, subsystemEvolutionData, triggerRate = 100, xmax = 50, printCSV = True)

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
import XLSutils

if XLSutils.xlsUtilExists():

    print >> sys.stderr,"creating spreadsheet..."

    # read the number of vertices
    avg_num_vertices = float(open(parameters.plots_output_dir + "/avg-num-vertices.txt").read())

    xlsFname = summaryOutputFilesDir + "/evolution-summary-%d.xlsx" % parameters.run

    # create a spread sheet with some formulas allowing
    # to test different scenarios
    XLSutils.makeXLS(
        # the underlying csv file
        parameters.plots_output_dir + "/subsystem-gut.csv", 

        # the output file
        xlsFname,
        
        avg_num_vertices
        )

    print >> sys.stderr,"created spreadsheet file",xlsFname

