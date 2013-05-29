#----------------------------------------------------------------------
# some global parameters
#----------------------------------------------------------------------

run = 166161
dataset = "minbias"

hlt_description = "HLT_Physics"

# maximum number of vertices for the plots
# (easiest determined by hand as it can take
# long time to find events with the maximum
# number of vertices)

max_num_vertices = 19

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

lumiBinningNbins = 18
lumiBinningXlow  = 0
lumiBinningXhigh = 1.8

# fitting range
linear_fit_min_per_bx_lumi = 0.4
linear_fit_max_per_bx_lumi = 1.7


perLumiSize_relYmax = 1.8

#----------------------------------------------------------------------

# custom positions of the legend for different plots
# of the event size distribution as function of the
# number of reconstructed vertices
#
# could use collections.defaultdict(dict) here
# but would have to be nested
#
def fedSizePerVertexLinearFitLegendPositions(run, subsys_name):

    if run == 179827 and subsys_name == "total":
        return (0.61, 0.15)

    if subsys_name == "CSC":
        if (run, dataset, hlt_description) == (160957, 'minbias', 'HLT_Physics'):
            return (0.64, 0.67)

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
        if (run, dataset, hlt_description) == (160957, 'minbias', 'HLT_Physics'):
            return (0.69, 0.15)
        
        return (0.18, 0.66)

    if subsys_name == "ECAL":
        if (run, dataset, hlt_description) == (160957, 'minbias', 'HLT_Physics'):
            return (0.64, 0.16)

        return (0.62, 0.16)

    if subsys_name == "HCAL" and (run, dataset, hlt_description) == (160957, 'minbias', 'HLT_L1Tech_BSC_minBias_threshold1'):
        return (0.74, 0.64)

    if subsys_name == "total":
        return (0.61, 0.15)



    # default values
    return (0.6, 0.65)
#----------------------------------------------------------------------

poissonFitYscalingFactor = None

if dataset == "minbias":
    poisson_fit_start = 0.5
    poisson_fit_end = max_num_vertices   + 0.5

    if hlt_description == "HLT_Physics" and run == 160957:
        poisson_fit_start = 2.5
        poisson_fit_end = 5.5

elif dataset == "express":
    poisson_fit_start = 7
    poisson_fit_end = max_num_vertices   + 0.5    

    poissonFitYscalingFactor = 100

elif dataset == "jet":
    poisson_fit_start = 1.5
    poisson_fit_end = max_num_vertices -1  + 0.5

elif run == 179827:
    poisson_fit_start = 0.5
    poisson_fit_end = max_num_vertices   + 0.5


#--------------------
# parameters for the linear fit of event size
# vs. number of vertices

linear_fit_min_num_vertices = 0
linear_fit_max_num_vertices = 17


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

#--------------------

# this should not need changing: the length
# of a luminosity section in seconds
seconds_per_lumi_section = 23.31

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
                "size413+size368",
                "size413",
                "size368",
         
                # 2) FED 53 is currently the FED with the largest data volume and which is NOT paired.
                "size053",

                # The same as above but "typical" (i.e. NOT worst case) cases:
                # 3) pair 295 and 263
                "size295+size263",
                "size295",
                "size263",

                # 4) single 151
                "size151",

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
import utils

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
