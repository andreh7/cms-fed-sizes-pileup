# some utilities potentially useful across several scripts

#----------------------------------------------------------------------
# expected list of FEDs during normal data taking
#----------------------------------------------------------------------
#
# derived from a run missing three feds and comparing to
# the numbers on http://cmsonline.cern.ch/daqStatusSCX/aDAQmon/DAQstatusGre.jpg
#
# (note that http://cmsdaqweb.cms/local/daqview/cdaq/DAQ_ru_static.html seems
# to contain also FEDs which are reserved for some subsystems (e.g. CSCTF)
# but probably are not implemented...

normalFEDlist = [ ]

normalFEDlist += range( 0,39 + 1)     # Pixel
normalFEDlist += range(50, 489 + 1)   # Tracker
normalFEDlist.remove(103)             # seems not to be in http://cmsdaqweb.cms/local/daqview/cdaq/DAQ_ru_static.html
normalFEDlist.remove(388)             # seems not to be in http://cmsdaqweb.cms/local/daqview/cdaq/DAQ_ru_static.html

normalFEDlist += [520, 522, 523, 524, 525, 529, 530, 531,
                  532, 534, 535, 537, 539, 540, 541, 542,
                  545, 546, 547, 548, 549, 551, 553, 554,
                  555, 556, 557, 560, 561, 563, 564, 565,
                  566, 568, 570, 571, 572, 573, 574] # Preshower
normalFEDlist += range(601, 654 + 1)  # ECAL
normalFEDlist += [690, 691, 692]      # CASTOR
normalFEDlist += range(700, 731 + 1)  # HCAL
normalFEDlist += [735]                # LumiScalers
normalFEDlist += [745]                # GCT
normalFEDlist += range(750, 757 + 1)  # CSC
normalFEDlist += [760]                # CSCTF
normalFEDlist += [770, 771, 772, 773, 774] # DT
normalFEDlist += [780]                # DTTF
normalFEDlist += [790, 791, 792]      # RPC
normalFEDlist += [812, 813]           # GlobalTrigger


#----------------------------------------------------------------------

# see also above
trackerFeds = [] 
trackerFeds += range(50, 489 + 1)   # Tracker
trackerFeds.remove(103)             # seems not to be in http://cmsdaqweb.cms/local/daqview/cdaq/DAQ_ru_static.html
trackerFeds.remove(388)             # seems not to be in http://cmsdaqweb.cms/local/daqview/cdaq/DAQ_ru_static.html

#----------------------------------------
# see also above
pixelFeds = range( 0,39 + 1)     # Pixel

ecalFeds  = range(601, 654 + 1)   # ECAL

cscFeds   = range(750, 757 + 1)  # CSC

#----------------------------------------------------------------------

# garbage collection saver for ROOT
gcs = []

#----------------------------------------------------------------------
# some constants
#----------------------------------------------------------------------

MU_BARN = 1e-6
INV_MU_BARN = 1 / MU_BARN

NANO_BARN = 1e-9
INV_NANO_BARN = 1 / NANO_BARN

PICO_BARN = 1e-12
INV_PICO_BARN = 1 / PICO_BARN

# 1 cm^2 in barn
CM2 = 1e24

#----------------------------------------------------------------------

# map:
#   first key:  subdetector
#   second key: ttc partition
#   value:      list of FEDs

# eqset /daq2/eq_160519_01
subdetTTCpartFEDs = { 
  "CASTOR": {
    "CASTOR": [690, 691, 692, 693],
    "LTC_CASTOR": [820],
  }, # CASTOR

  "CSC": {
    "CSC+": [831, 832, 833, 834, 835, 836, 837, 838, 839, 841, 842, 843, 844, 845, 846, 847, 848, 849],
    "CSC-": [851, 852, 853, 854, 855, 856, 857, 858, 859, 861, 862, 863, 864, 865, 866, 867, 868, 869],
    "CSCTF": [-1, -1, 760, 890, 891, 892, 893, 894, 895, 896, 897, 898, 899, 900, 901],
    "LTC_CSC": [822],
  }, # CSC

  "CTPPS_TOT": {
    "TOTDET": [578, 579, 580, 581],
    "TOTTRG": [577],
  }, # CTPPS_TOT

  "DT": {
    "DT+": [773, 774],
    "DT-": [770, 771],
    "DT0": [772],
    "LTC_DT": [823],
    "TWINMUX": [1390, 1391, 1393, 1394, 1395],
  }, # DT

  "ECAL": {
    "EB+": [628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 663],
    "EB-": [610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 662],
    "EE+": [646, 647, 648, 649, 650, 651, 652, 653, 654, 664],
    "EE-": [601, 602, 603, 604, 605, 606, 607, 608, 609, 661],
    "LTC_ECAL": [819],
  }, # ECAL

  "ES": {
    "ES+": [548, 549, 551, 553, 554, 555, 556, 557, 560, 561, 563, 564, 565, 566, 568, 570, 571, 572, 573, 574],
    "ES-": [520, 522, 523, 524, 525, 528, 529, 530, 531, 532, 534, 535, 537, 539, 540, 541, 542, 545, 546, 547],
  }, # ES

  "HCAL": {
    "HBHEA": [700, 701, 702, 703, 704, 705, 1100, 1102, 1104],
    "HBHEB": [706, 707, 708, 709, 710, 711, 1106, 1108, 1110],
    "HBHEC": [712, 713, 714, 715, 716, 717, 1112, 1114, 1116],
    "HO": [724, 725, 726, 727, 728, 729, 730, 731],
    "LTC_HCAL": [817],
  }, # HCAL

  "HF": {
    "HF": [718, 719, 1118, 1120, 1122, 1132],
  }, # HF

  "PIXEL": {
    "BPIX": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
    "FPIX": [32, 33, 34, 35, 36, 37, 38, 39],
    "LTC_PIXEL": [824],
  }, # PIXEL

  "PIXEL_UP": {
    "PIXELPILOT": [40, 1240],
  }, # PIXEL_UP

  "RPC": {
    "LTC_RPC": [821],
    "RPC": [-1, -1, 790, 791, 792, 793],
  }, # RPC

  "SCAL": {
    "SCAL": [735],
  }, # SCAL

  "TCDS": {
    "CPM-PRI": [1024, 1025],
    "CPM-SEC": [1050, 1051],
    "GTPe": [814],
    "LPM1": [1038],
    "lpm1": [1026],
    "lpm11": [1036],
    "LPM11": [1048],
    "LPM12": [1049],
    "lpm12": [1037],
    "LPM_BRIL": [1032, 1044],
    "LPM_CSC": [1029, 1041],
    "LPM_DT": [1030, 1042],
    "LPM_ECAL_ES": [1034, 1046],
    "LPM_HCAL": [1033, 1045],
    "LPM_RPC": [1028, 1040],
    "LPM_SCAL_TOTEM": [1031, 1043],
    "LPM_TRACKER_PIXEL": [1027, 1039],
    "LPM_TRG": [1035, 1047],
  }, # TCDS

  "TRACKER": {
    "LTC_TRACKER": [818],
    "TEC+": [260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355],
    "TEC-": [164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259],
    "TIBTID": [50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163],
    "TOB": [356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489],
  }, # TRACKER

  "TRG": {
    "CALSTAGE1": [1352],
    "CALTRIGUP": [1360, 1362, 1364, 1366],
    "GCT": [745],
    "GT": [809, 813],
    "GTUP": [1404],
    "LTC_TRG": [816],
    "MUTFUP": [1376, 1377, 1380, 1381, 1384, 1385, 1386, 1392, 1402],
    "RCT": [1350, 1354, 1356, 1358],
  }, # TRG

}

#----------------------------------------------------------------------

def getSubsystemFromFed(fed):
    """ given a FED number, returns the subsystem it belongs to or None if not found"""

    # using the data from the hardware database
    for subsys, subsysData in subdetTTCpartFEDs.items():
        for ttcp, feds in subsysData.items():
            if fed in feds:
                return subsys
    # not found
    return None

#----------------------------------------------------------------------

def getFedRanges(all_feds, fedNameGroupOptions = {}):
    """given the list of all feds found in a dataset, returns a list of
     dicts with elements 'start', 'end' and 'name' corresponding
     to the first and last FED of the corresponding subdetector
     and the subdetector's name """

    retval = []

    previous_name = None

    this_range = None

    last_fed = None

    for fed in sorted(all_feds):

        this_name = getSubsystemFromFed(fed, *fedNameGroupOptions)

        if this_name != previous_name:
            # start a new range
            if this_range != None:
                this_range['end'] = last_fed
                retval.append(this_range)

            this_range = { "start": fed, "name": this_name }


        # prepare next iteration
        last_fed = fed
        previous_name = this_name

    if this_range != None:
        this_range['end'] = last_fed
        retval.append(this_range)

    return retval


#----------------------------------------------------------------------

def getFedIdsFromTuple(ntuple):
    """ given a 'per fed tuple', determines the FED ids contained
    in the dataset and returns the list of FED ids """

    branch_names = [ x.GetName() for x in ntuple.GetListOfBranches() ]

    import re

    fed_ids = [ ]

    for branch_name in branch_names:

        mo = re.match("size(\d+)$", branch_name)

        if mo:
            # note that we NEED NOT strip leading zeroes
            # ourselves (int seems NOT to interpret
            # these as octal numbers, just the
            # python interpreter does with int literals)

            number = mo.group(1)
            # print number, int(number)

            number = int(number)

            fed_ids.append(number)
    
    return fed_ids

#----------------------------------------------------------------------

def openSizePerFedNtuples(input_data_dir, max_num_vertices):
    """ returns a dict the ntuples
        per number of reconstructed vertices which contain
        one variable per fed and sums per subsystem.

        The dicts map from number of vertices to the root tuple.
        """

    import ROOT

    ntuple = {}
    # new: the tuples are now all in one file (produced by CMSSW)

    import os
    if not os.path.exists(input_data_dir + "/small-tuples.root"):
        raise Exception("file " + input_data_dir + "/small-tuples.root" + " does not exist")

    fin = ROOT.TFile.Open(input_data_dir + "/small-tuples.root"); gcs.append(fin)
    for nv in range(max_num_vertices+1):
        
        ntuple[nv] = fin.Get("tupler/all_sizes_%dvtx" % nv)

    return ntuple
#----------------------------------------------------------------------

def getNumFedsPerFedGroup(input_data_dir):
    """ returns a dict of subsystem / fed group name
        (as defined in PerNumVertexNtupleMaker.cc)
        to the number of FEDs seen in the first event
        (which should be constant within one run)
        """

    import ROOT
    import array

    ntuple = {}
    # new: the tuples are now all in one file (produced by CMSSW)

    import os
    if not os.path.exists(input_data_dir + "/small-tuples.root"):
        raise Exception("file " + input_data_dir + "/small-tuples.root" + " does not exist")

    olddir = ROOT.gDirectory
    fin = ROOT.TFile.Open(input_data_dir + "/small-tuples.root")

    tree = fin.Get("tupler/fedGroupSize")

    # setup buffers
    groupName = ROOT.TObjString()
    tree.SetBranchAddress("groupName", ROOT.AddressOf(groupName))

    groupSize = array.array('i',[ 0 ])
    tree.SetBranchAddress("groupSize", groupSize)

    retval = {}

    # read all entries
    for i in range(tree.GetEntries()):
        tree.GetEntry(i)

        # make a copy of groupName as for the next entry,
        # it's value will change (but the reference is the
        # same), givin a dict with only one entry
        # if we don't clone groupName
        retval[str(groupName)] = groupSize[0]

    # make sure we don't like open file descriptors
    olddir.cd()
    fin.Close()
    
    return retval



#----------------------------------------------------------------------

def getQuantile(sortedValues, quantile):
    """ takes care of underflow/overflow effects """

    if not sortedValues:
        # no value, no quantile
        return None

    pos_in_array = int(round(quantile * len(sortedValues)))
    if pos_in_array < 0:
        return sortedValues[0]
    elif pos_in_array >= len(sortedValues):
        return sortedValues[-1]
    else:
        return sortedValues[pos_in_array]

#----------------------------------------------------------------------

def linearFit(x,y):

    assert(len(x) == len(y))

    n = float(len(x))

    if n < 2:
        raise Exception("must have at least two points for a linear fit, found %d" % n)

    def sumProd(x,y):

        sum = 0

        for xx,yy in zip(x,y):
            sum += xx*yy

        return sum

    sum_x = sum(x)
    sum_y = sum(y)

    xmean = sum_x / n
    ymean = sum_y / n
    
    
    beta_hat = ( sumProd(x,y) - 1/n * sum_x * sum_y ) / \
               ( sumProd(x,x) - 1/n * sum_x * sum_x)

    alpha_hat = ymean - beta_hat * xmean

    return alpha_hat, beta_hat

#----------------------------------------------------------------------

def isIntString(x):
    try:
        int(x)
        return True
    except ValueError:
        return False

#----------------------------------------------------------------------    
    
def writeStringToFile(fname, text):
    fout = open(fname,"w")
    fout.write(text)
    fout.close()


#----------------------------------------------------------------------

def loadParameters():
    """
    @return a module object which contains the parameters. This can
    e.g. used as follows:

      parameters = loadParameters()
      print parameters.x

      See also http://stackoverflow.com/questions/6811902

    """
    import sys, imp, os

    ARGV = sys.argv[1:]

    if len(ARGV) >= 1:
        fname = ARGV[0]
    else:
        if not os.environ.has_key('RUN'):
            print >> sys.stderr,"no configuration file specified and the environment variable $RUN is not set, exiting"
            sys.exit(1)

        fname = "parameters-{RUN}.py".format(RUN=os.environ['RUN'])

    with open(fname, "U") as module_file:
        mod = imp.load_module(
            "parameters", module_file, fname, (".py","U", imp.PY_SOURCE))

    # return an object instead of a module (because the former can be pickled)
    from Parameters import Parameters
    retval = Parameters()

    for key in dir(mod):
        if key.startswith("__"):
             continue

        obj = getattr(mod, key)
        setattr(retval, key, obj)

    return retval


#----------------------------------------------------------------------


def getStandardSubsystemFEDnames():
    # these groups are defined in
    # FedSizeAnalysis/FedSizeAnalyzer/src/PerNumVertexNtupleMaker.cc 
    return [
        'CSCTF',
        'DTTF',
        'GCT',
        'LumiScalers', 
        'GlobalTrigger',
        'CSC',
        'DT',
        'CASTOR',
        # 'Pixel',
        
        'BPIX',
        'FPIX',

        "HF",

        
        'Preshower',
        'ECAL',
        'HCAL',
        'RPC',
        'Tracker',
        
        
        ]



#----------------------------------------------------------------------

# this should not need changing: the length
# of a luminosity section in seconds
seconds_per_lumi_section = 23.31


#----------------------------------------------------------------------


#----------------------------------------------------------------------

def newestFileDate(glob_pattern):
    import glob, os    

    newest_date = None

    for fname in glob.glob(glob_pattern):

        this_date = os.path.getmtime(fname)

        if this_date > newest_date:
            newest_date = this_date

    return newest_date

#----------------------------------------------------------------------

    
#----------------------------------------------------------------------

def getIndividualFedsFromSmallTupleFile():
    """ returns a list of individual fed numbers stored in the small tuple file"""
    
    getSmallTuple()

    
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
