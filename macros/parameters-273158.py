import utils, os

import fedgroups

#----------------------------------------------------------------------
# some global parameters
#----------------------------------------------------------------------



run = int(os.environ['RUN'])
dataset = "hltphysics"

hlt_description = "HLT_Physics"

# maximum number of vertices for the plots
# (check the output of the first (CMSSW) step
# what the maximum number of vertices found
# is)

max_num_vertices = 42

#----------------------------------------------------------------------

# FEDids seen in CMSSW
fedsInRun = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 50, 51, 52, 53, 54, 55, 56, 57, 58, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 520, 522, 523, 524, 525, 528, 529, 530, 531, 532, 534, 535, 537, 539, 540, 541, 542, 545, 546, 547, 548, 549, 551, 553, 554, 555, 556, 557, 560, 561, 563, 564, 565, 566, 568, 570, 571, 572, 573, 574, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 714, 715, 716, 717, 724, 725, 726, 727, 728, 729, 730, 731, 735, 760, 770, 771, 772, 773, 774, 790, 791, 792, 831, 832, 833, 834, 835, 836, 837, 838, 839, 841, 842, 843, 844, 845, 846, 847, 848, 849, 851, 852, 853, 854, 855, 856, 857, 858, 859, 861, 862, 863, 864, 865, 866, 867, 868, 869, 1024, 1100, 1102, 1104, 1106, 1108, 1110, 1112, 1114, 1116, 1118, 1120, 1122, 1132, 1354, 1356, 1358, 1360, 1376, 1377, 1380, 1381, 1384, 1385, 1390, 1391, 1393, 1394, 1395, 1402, 1404]

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

poisson_fit_start, poisson_fit_end = 9.5, 20.5
# poisson_fit_start, poisson_fit_end = 4.5, 27.5
#poisson_fit_start, poisson_fit_end = 20.5, 40.5

#--------------------
# parameters for the linear fit of event size
# vs. number of vertices

# original range
linear_fit_min_num_vertices,linear_fit_max_num_vertices  = 5, 30

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

    allSubsysToPlot.extend(fedgroups.makeFEDbuilderGroups(fedsInRun = fedsInRun))

    # DEBUG
    # allSubsysToPlot = [ allSubsysToPlot[1] ]

#--------------------
# per FRL
#--------------------
if True:

    items = fedgroups.makeFRLgroups(fedsInRun)

    # DEBUG
    # items = [ items[0] ]

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

# allSubsysToPlot = [ allSubsysToPlot[0] ]

