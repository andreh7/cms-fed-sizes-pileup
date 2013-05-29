import utils, os


#----------------------------------------------------------------------
# some global parameters
#----------------------------------------------------------------------



run = int(os.environ['RUN'])
dataset = "express"

hlt_description = "HLT_Physics"

# maximum number of vertices for the plots
# (check the output of the first (CMSSW) step
# what the maximum number of vertices found
# is)

max_num_vertices = 54

#----------------------------------------------------------------------
# quantities derived from the above parameters
#----------------------------------------------------------------------

input_data_dir = "../data/%s-%d" % (dataset,run)

output_data_dir = "data/%s-%d/%s"  % (dataset,run, hlt_description)

#----------------------------------------

import os

if not os.path.exists(output_data_dir):
    os.mkdir(output_data_dir)


plots_output_dir = "plots/%s-%d/%s"  % (dataset,run, hlt_description)
if not os.path.exists(plots_output_dir):
    os.makedirs(plots_output_dir)

#----------------------------------------------------------------------
# binning for the per-bunch crossing luminosity
#----------------------------------------------------------------------

lumiBinningXlow  = 8.3
lumiBinningXhigh = 9.3

lumiBinningBinWidth = 0.1

lumiBinningNbins = int((lumiBinningXhigh - lumiBinningXlow) / float(lumiBinningBinWidth) + 0.5)

# fitting range
linear_fit_min_per_bx_lumi = 8.3
linear_fit_max_per_bx_lumi = 9.3

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

poisson_fit_start, poisson_fit_end = 20.5, 40.5
# poisson_fit_start, poisson_fit_end = 17.5, 44.5

#--------------------
# parameters for the linear fit of event size
# vs. number of vertices

linear_fit_min_num_vertices = 22
linear_fit_max_num_vertices = 42

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
if False:
    # request by Christoph, 2011-10-12
    # take all tracker FEDs
    allSubsysToPlot = [ "size%03d" % fed for fed in utils.trackerFeds ]

if False:
    # tracker but size/rate per FRL, not FED

    import FEDtoFRLMappingData
    frlTuples = FEDtoFRLMappingData.makeFRLtuples(utils.trackerFeds)
    allSubsysToPlot = [ "+".join([ "size%03d" % x for x in thisFeds]) for thisFeds in frlTuples ]

    # from pprint import pprint
    # pprint(frlTuples)
    # print "----------------------------------------"
    # pprint(allSubsysToPlot)
    # print len(utils.normalFEDlist)
    # print len(allSubsysToPlot)
    # import sys; sys.exit(1)

#--------------------
if False:

    allSubsysToPlot = []

    for fedlist in (
        utils.pixelFeds,
        utils.ecalFeds,
        utils.cscFeds):

        allSubsysToPlot += [ "size%03d" % fed for fed in fedlist ]


    # allSubsysToPlot = [ "size003" ]

#--------------------

if False:
    # 2012-01-19
    # plot evolution per fedbuilder
    import FedBuilderData

    allSubsysToPlot = FedBuilderData.makeGroupExpressions(fedsToExclude =
       # these feds seem not to exist in this run
       [ 810,
         831,
         832,
         833,
         834,
         835,
         836,
         837,
         838,
         839,

         841,
         842,
         843,
         844,
         845,
         846,
         847,
         848,
         849,

         851,
         852,
         853,
         854,
         855,
         856,
         857,
         858,
         859,

         861,
         862,
         863,
         864,
         865,
         866,
         867,
         868,
         869,

         890,
         891,
         892,
         893,

         894,
         895,
         896,
         897,
         898,
         899,
         900,
         901,

         662, # EB-
         663, # EB+
         664, # EE+
         661, # EE-

         793, # RPC
         ]
                                                          )

#--------------------

if False:
    # list of ALL (existing) feds
    allSubsysToPlot = [ "size%03d" % fed for fed in utils.normalFEDlist ]         

    frlTuples = FEDtoFRLMappingData.makeFRLtuples(utils.normalFEDlist)

#--------------------

if True:
    # per FRL
    #
    # all FRLs (i.e. tracker FEDs paired but
    # rest per FED
    import FEDtoFRLMappingData
    frlTuples = FEDtoFRLMappingData.makeFRLtuples(utils.normalFEDlist)
    allSubsysToPlot = [ "+".join([ "size%03d" % x for x in thisFeds]) for thisFeds in frlTuples ]
#--------------------
