import utils, os


#----------------------------------------------------------------------
# some global parameters
#----------------------------------------------------------------------



# run = 176201
# run = 178208 # high pileup fill
# # dataset = "jet"
# dataset = "express"

run = 179827
dataset = "zerobias"

hlt_description = "HLT_ZeroBias"

# maximum number of vertices for the plots
# (check the output of the first (CMSSW) step
# what the maximum number of vertices found
# is)

max_num_vertices = 61

#----------------------------------------------------------------------
# quantities derived from the above parameters
#----------------------------------------------------------------------

input_data_dir = "../data/%s-%d" % (dataset,run)

if not os.path.exists(input_data_dir):
    # use the EOS dir
    input_data_dir = os.path.expanduser("~aholz/eos/cms/store/user/aholz/castor/fed-size-analysis/%s-%d" % (dataset,run))


output_data_dir = "data/%s-%d/%s"  % (dataset,run, hlt_description)

    

#----------------------------------------

import os

if not os.path.exists(output_data_dir):
    os.makedirs(output_data_dir)


plots_output_dir = "plots/%s-%d/%s"  % (dataset,run, hlt_description)
if not os.path.exists(plots_output_dir):
    os.makedirs(plots_output_dir)

#----------------------------------------------------------------------
# binning for the per-bunch crossing luminosity
#----------------------------------------------------------------------

lumiBinningNbins = 12
lumiBinningXlow  = 5.4
lumiBinningXhigh = 6.6

# fitting range
linear_fit_min_per_bx_lumi = 5.4
linear_fit_max_per_bx_lumi = 6.6

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
poissonFitYscalingFactor = 10

poisson_fit_start = 7.5
poisson_fit_end = max_num_vertices   + 0.5

#--------------------
# parameters for the linear fit of event size
# vs. number of vertices

# where to fit
linear_fit_min_num_vertices = 10
linear_fit_max_num_vertices = 40

# where to draw the extrapolation
linear_fit_extrapolation_min_num_vertices = 10
linear_fit_extrapolation_max_num_vertices = 130

# additional arrow positions at other number of vertices
linear_fit_arrows = [ dict(vtx = "avg"), # the standard vertex
                      # dict(vtx = 140 * 0.7), # LHC Phase II
                      dict(vtx = (2 - 0.262561079388) / 0.0151176047105), # line which goes through 2 MByte

                       

                      ]

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

    allSubsysToPlot = []

    import FEDtoFRLMappingData

    fedsProcessed = set()

    for fed in utils.trackerFeds:

        # avoid plotting a pair of
        # FEDs twice
        if fed in fedsProcessed:
            continue

        fedsProcessed.add(fed)

        peerFED =  FEDtoFRLMappingData.fedToPeerFedMapping.get(fed,None)

        # make sure that the peer FED normally is part of data taking
        if peerFED != None and not peerFED in utils.trackerFeds:
            peerFED = None

        if peerFED == None:
            # this FED has no peer
            allSubsysToPlot.append("size%03d" % fed)
        else:
            fedsProcessed.add(peerFED)

            # this FED shares an FRL with another FED
            thisFeds = sorted([fed, peerFED])
            allSubsysToPlot.append("+".join([ "size%03d" % x for x in thisFeds]))

    # end of loop of all tracker feds

#--------------------
if False:
    
    # do the plots for each Pixel FED
    allSubsysToPlot = [ "size%03d" % fed for fed in utils.pixelFeds ]


#--------------------

if True:
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
