import utils, os

import fedgroups

dataDir = os.path.join(
    os.environ['CMSSW_BASE'],
    "src/FedSizeAnalysis/FedSizeAnalyzer/data"
    )

assert os.environ.has_key('RUN'), "enivonrment variable RUN not set"
run = int(os.environ['RUN'])

# maximum number of vertices for the plots
# (check the output of the first (CMSSW) step
# what the maximum number of vertices found
# is)
max_num_vertices = eval(open(os.path.join(dataDir,
                                        "max-num-vertices-%d.txt" % run)).read())


# fedids seen in this run
fedsInRun = eval("[ " + 
                 open(os.path.join(dataDir,
                                   "fedids-%d.txt" % run)).read() + 
                  "]")


#----------------------------------------------------------------------
# some global parameters
#----------------------------------------------------------------------

dataset = "hltphysics"

hlt_description = "HLT_Physics"

#----------------------------------------------------------------------

#----------------------------------------------------------------------
# quantities derived from the above parameters
#----------------------------------------------------------------------

input_data_dir = "../data/%s-%d" % (dataset,run)

output_data_dir = "data/%s-%d/%s"  % (dataset,run, hlt_description)

#----------------------------------------

import os

assert os.path.exists(input_data_dir), "input directory " + input_data_dir + " does not exist"

if not os.path.exists(output_data_dir):
    os.makedirs(output_data_dir)


plots_output_dir = "plots/%s-%d/%s"  % (dataset,run, hlt_description)
if not os.path.exists(plots_output_dir):
    os.makedirs(plots_output_dir)

#----------------------------------------------------------------------
# binning for the per-bunch crossing luminosity
#----------------------------------------------------------------------

lumiBinningXlow  = 11.2
lumiBinningXhigh = 13.2

lumiBinningBinWidth = 0.1

lumiBinningNbins = int((lumiBinningXhigh - lumiBinningXlow) / float(lumiBinningBinWidth) + 0.5)

# fitting range
linear_fit_min_per_bx_lumi = 20
linear_fit_max_per_bx_lumi = 30

perLumiSize_relYmax = 1.6

#----------------------------------------------------------------------

# custom positions of the legend for different plots
# of the event size distribution as function of the
# number of reconstructed vertices
#
# could use collections.defaultdict(dict) here
# but would have to be nested
#
def fedSizePerVertexLinearFitLegendPositions(run, subsys_name):

    if subsys_name == "DTTF":
        return (0.6, 0.65)

    if subsys_name == "CSC":
        return (0.6, 0.65)

    if subsys_name == "RPC":
        return (0.6, 0.65)

    if subsys_name == "HCAL":
        return (0.6, 0.65)

    # default values
    return (0.6, 0.15)

    if subsys_name == "total":
        return (0.61, 0.15)

    if subsys_name == "CSCTF":
        return (0.6, 0.24)

    if subsys_name == "GCT":
        return (0.6, 0.24)

    if subsys_name == "LumiScalers":
        return (0.6, 0.24)

    if subsys_name == "GlobalTrigger":
        return (0.6, 0.24)

    if subsys_name == "CASTOR":
        return (0.63, 0.24)

    if subsys_name == "Preshower":
        return (0.18, 0.66)

    if subsys_name == "ECAL":
        return (0.62, 0.16)

    if subsys_name == "total":
        return (0.61, 0.15)

#----------------------------------------------------------------------

# set to None if no scaling requested
poissonFitYscalingFactor = 100

poisson_fit_start, poisson_fit_end = 11.5, 17.5
# poisson_fit_start, poisson_fit_end = 4.5, 27.5
#poisson_fit_start, poisson_fit_end = 20.5, 40.5

#--------------------
# parameters for the linear fit of event size
# vs. number of vertices

# original range
# linear_fit_min_num_vertices,linear_fit_max_num_vertices  = 20, 35
linear_fit_min_num_vertices,linear_fit_max_num_vertices  = 35, 45

# range used later on to check for slope change
# linear_fit_min_num_vertices,linear_fit_max_num_vertices  = 32, 42
#----------

# parameters for the corresponding plot
size_evolution_min_num_vertices = 0
size_evolution_max_num_vertices = max_num_vertices

size_evolution_rel_yscale = 1.6

#--------------------
# binning parameters for distributions of fed sizes
# fedsize_histo_xmin = 0.4
# fedsize_histo_xmax = 1.2
# fedsize_histo_nbins = 16

fedsize_histo_xmin = 0.2
fedsize_histo_xmax = 0.9
fedsize_histo_nbins = 14

#----------------------------------------------------------------------
allSubsysToPlot = [

                # these groups are defined in
                # FedSizeAnalysis/FedSizeAnalyzer/src/PerNumVertexNtupleMaker.cc 

                'CSCTF',
                'DTTF',
                'GCT',
                'LumiScalers', 
                'GlobalTrigger',
                'CSC',
                'DT',
                'CASTOR',
                'Pixel',

                # special request on 2011-07-06
                'BPIX',
                'FPIX',

                # special request on 2011-09-27
                "HF",

                #--------------------
                # requests 2011-10-04 by Christoph
                # for tracker FEDs
                # specify sums of individual FEDS

                # 1) The FEDs 413 and 368 form currently a pair and are thought to be the pair with the largest data volume.
                # "size413+size368",
                # "size413",
                # "size368",
         
                # 2) FED 53 is currently the FED with the largest data volume and which is NOT paired.
                # "size053",

                # The same as above but "typical" (i.e. NOT worst case) cases:
                # 3) pair 295 and 263
                # "size295+size263",
                # "size295",
                # "size263",

                # 4) single 151
                # "size151",

                #--------------------
                # testing for the above
                #--------------------
                # "size413+size368",
                # "size413",
                # "size368",
                #--------------------
                
                'Preshower',
                'ECAL',
                'HCAL',
                'RPC',
                'Tracker',

                "total",
                ]

#--------------------

allSubsysToPlot = []

#--------------------
# total size
#--------------------
if True:
    allSubsysToPlot.extend(fedgroups.makeAllFedsGroup(fedsInRun = fedsInRun))

#--------------------
# per fedbuilder
#--------------------
if True:

    import FedBuilderData

    allSubsysToPlot.extend(fedgroups.makeFEDbuilderGroups(run, fedsInRun = fedsInRun))

    # DEBUG
    # allSubsysToPlot = [ allSubsysToPlot[1] ]

#--------------------
# per FRL
#--------------------
if True:

    items = fedgroups.makeFRLgroups(run, fedsInRun)

    # DEBUG
    # items = [ items[0] ]

    allSubsysToPlot.extend(items)

#--------------------
# per FED
#--------------------
if True:

    items = fedgroups.makeSingleFEDgroups(run, fedsInRun)
    allSubsysToPlot.extend(items)

#--------------------
# per subsystem
#--------------------
if True:
    items = fedgroups.makeSubSystemGroups(fedsInRun)

    # DEBUG
    # items = [ items[0] ]

    allSubsysToPlot.extend(items)    
#--------------------
# per TTC partition
#--------------------
if True:
    items = fedgroups.makeTTCpartitionGroups(fedsInRun)

    # DEBUG
    # items = [ items[0] ]

    allSubsysToPlot.extend(items)    


