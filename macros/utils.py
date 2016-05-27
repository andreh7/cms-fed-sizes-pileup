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

# from http://cmsdoc.cern.ch/cms/TRIDAS/horizontal/RUWG/DAQ_IF_guide/DAQ_IF_guide.html
def getSubsystemFromFed(fed,
                        splitHCAL = False,
                        splitPixel = True,
                        ):
    """ given a FED number, returns the subsystem it belongs to """


    # Pixel
    if splitPixel:
        if fed >= 0	        and fed <= 31	: return "BPIX"
        if fed >= 32        and fed <= 39	: return "FPIX"
    else:
        if fed >= 0	        and fed <= 39	: return "Pixel"

    if fed >= 50	and fed <= 489	: return "Tracker"
    if fed >= 520	and fed <= 575	: return "Preshower"
    if fed >= 600	and fed <= 670	: return "ECAL"
    if fed >= 690	and fed <= 693	: return "CASTOR"

    # HCAL
    if splitHCAL:
        if fed >= 700	and fed <= 717	: return "HBHE"
        if fed >= 718	and fed <= 723	: return "HF"
        if fed >= 724	and fed <= 731	: return "HO"
    else:
        if fed >= 700	and fed <= 731	: return "HCAL"


    if fed >= 735	and fed <= 735	: return "LumiScalers"
    if fed >= 745	and fed <= 749	: return "GCT"
    if fed >= 750	and fed <= 757	: return "CSC"
    if fed >= 760	and fed <= 760	: return "CSCTF"
    if fed >= 770	and fed <= 779	: return "DT"
    if fed >= 780	and fed <= 780	: return "DTTF"
    if fed >= 790	and fed <= 795	: return "RPC"
    if fed >= 812	and fed <= 813	: return "GlobalTrigger"
    if fed >= 814	and fed <= 814	: return "GlobalTrigger"
    if fed >= 815	and fed <= 824	: return "LTC"
    if fed >= 830	and fed <= 887	: return "CSC"
    if fed >= 890	and fed <= 901	: return "CSCTF"
    if fed >= 1023	and fed <= 1023	: return "DAQ"

    return "???"

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

    return mod


parameters = loadParameters()

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


def loadSmallTuple(fname):

    global small_tuple

    import ROOT
    fin = ROOT.TFile.Open(fname); gcs.append(fin)

    assert fin.IsOpen(), "failed to open small tuple file " + fname

    smallTupleName = "tupler/small_tuple"

    small_tuple = fin.Get(smallTupleName)

    assert small_tuple != None, "could not get " + smallTupleName + " in file " + fname

    # maybe this magically prevents crashes ?
    ROOT.gROOT.cd()

    return small_tuple

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

def getSmallTuple():

    import os
    global small_tuple

    # the file name of the file
    # containing the cached data
    fname = parameters.input_data_dir + "/small-tuples.root"

    if globals().has_key('small_tuple') and small_tuple != None:
        return small_tuple

    # try to find it on disk 

    biggest_time = None

    # also check whether this is newer than all
    # of the original ntuples
    if os.path.exists(fname) and \
       os.path.getmtime(fname) >= newestFileDate(parameters.input_data_dir + "/*.root"):

        small_tuple = loadSmallTuple(fname)
        return small_tuple

    raise Exception("small tuple " + fname + " is out of date (files in " + parameters.input_data_dir + " seem newer) or not existing, need to rerun cmsRun")


    ## # not on disk or not recent enough, we must
    ## # produce it
    ## 
    ## print >> sys.stderr,"getting the original data from the large number of files"
    ## 
    ## Events.SetEstimate(Events.GetEntries())
    ## Events.Draw(":".join( [
    ##     "fedSizeData.getNumPrimaryVertices()", # V1
    ##     "fedSizeData.getSumAllFedSizes()",     # V2
    ##     "EventAuxiliary.luminosityBlock()",    # V3
    ##     "EventAuxiliary.event()",              # V4
    ##     ]),
    ##             "", # cut
    ##             "goff"
    ##             )
    ## 
    ## small_tuple = ROOT.TNtuple("small_tuple","small_tuple",":".join([
    ##     "num_vertices",
    ##     "total_event_size",
    ##     "lumisection",
    ##     "event"]))
    ## 
    ## entries = Events.GetSelectedRows()
    ## 
    ## vector = [ Events.GetV1(), Events.GetV2(), Events.GetV3(), Events.GetV4() ]
    ## 
    ## for index in xrange(entries):
    ##     small_tuple.Fill(vector[0][index],
    ##                 vector[1][index],
    ##                 vector[2][index])
    ## 
    ## fout = ROOT.TFile.Open(fname,"RECREATE")
    ## fout.cd()
    ## small_tuple.Write()
    ## ROOT.gROOT.cd()
    ## fout.Close()
    ## 
    ## print >> sys.stderr,"wrote cached file"
    ## 
    ## # try loading the file again in order to avoid
    ## # crashes
    ## return loadSmallTuple(fname)

#----------------------------------------------------------------------
def getAllLumiSections():
    """ returns a list of all luminosity sections found """

    small_tuple = getSmallTuple()
    small_tuple.SetEstimate(small_tuple.GetEntries())
    small_tuple.Draw("lumisection","","goff")

    num_entries = small_tuple.GetSelectedRows()
    data = small_tuple.GetV1()

    lumi_sections = set([ data[i] for i in xrange(num_entries) ])

    return lumi_sections

    
#----------------------------------------------------------------------
