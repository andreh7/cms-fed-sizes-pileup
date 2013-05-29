from pprint import pprint
import ROOT
ROOT.gROOT.ProcessLine(".x ~/rootlogon.C")
ROOT.gROOT.ProcessLine("setTDRStyle();")
ROOT.gStyle.SetErrorX(0.5)

from utils import *

import utils

#----------------------------------------------------------------------
# parameters
#----------------------------------------------------------------------

execfile("parameters.py")



#----------------------------------------------------------------------

#----------------------------------------------------------------------
# FED size distribution
#----------------------------------------------------------------------

fedsize_histo_xmin = 0.0e6
fedsize_histo_xmax = 0.9e6
fedsize_histo_nbins = 18

# is different from the same class in plots.py: plots the individual FED
# sizes, not sums of fed sizes in the given subdetector
class FedSizeDist:

    #----------------------------------------
    def __init__(self, fed_ids, subdet_name, subdet_title, legend_spec = None):

        self.unit_name = "10^{3} Bytes"
        self.unit_size = 1000

        # bin width in plotting units
        # self.bin_width = ( fedsize_histo_xmax - fedsize_histo_xmin ) / float(fedsize_histo_nbins)
        # self.bin_width /= float(self.unit_size)

        # print "bin_width=",self.bin_width

        self.fed_ids = fed_ids[:]
        self.subdet_name = subdet_name
        self.subdet_title = subdet_title

        if legend_spec == None:
            legend_spec = { "x1": 0.55, "y1": 0.6,
                                 "x2": 0.85, "y2": 0.9 }

        self.legend_spec = legend_spec

    #----------------------------------------
    def produce(self):

        import sys

        # for determining the binning (as we have several plots
        # to superimpose, we determine the binning better ourselves...)
        min_value =   sys.float_info.max
        max_value = - sys.float_info.max

        import tempfile
        workdir = tempfile.mkdtemp()

        # produce histograms of the fed size distributions
        for num_vertices in range(max_num_vertices + 1):

            ntuple[num_vertices].SetEstimate(ntuple[num_vertices].GetEntries())

            # produce a small ntuple to benefit from the auto-binning
            # feature of ROOT
            for fed in self.fed_ids:

                plot_expr = "size%03d/%f"% (fed, self.unit_size)

                # print "plot_expr=",plot_expr

                ntuple[num_vertices].Draw(plot_expr,"","goff")

                this_fed_sizes = ntuple[num_vertices].GetV1()

                num_selected_events = ntuple[num_vertices].GetSelectedRows()

                assert(num_selected_events > 0)

                # convert to a list
                this_fed_sizes = [ this_fed_sizes[i] for i in xrange(num_selected_events) ]

                # can't keep everything (i.e. for all number of vertices at the same time)
                # memory (not for tracker)
                # tracker has 440 FEDs, times ~ 1.9 Mio events = 836 Mio values -> 3.6 GBytes of memory...

                # update minimum and maximum

                if this_fed_sizes:
                    min_value = min(min_value,min(this_fed_sizes))
                    max_value = max(max_value,max(this_fed_sizes))

            # end loop over feds

        # end loop over number of vertices

        #--------------------
        # determine the binning
        #--------------------
        min_max_half_diff = 0.5 * (max_value - min_value)
        min_max_mid       = 0.5 * (max_value + min_value)

        # allow for some margin
        histo_xmin = min_max_mid - 1.1 * min_max_half_diff
        histo_xmax = min_max_mid + 1.1 * min_max_half_diff

        #--------------------

        print "histo_xmin,xmax=",histo_xmin, histo_xmax

        histo_nbins = 30

        # reopen the ntuple files to fill the histograms
        # note that we do this only here to havel a consistent
        # binning across ALL number of vertices

        # for checking the total number of entries per subdet
        total_num_entries = 0

        for num_vertices in range(max_num_vertices + 1):

            # open the ntuple file
            histo_name = "fed_size_dist_" + str(num_vertices) + "_" + self.subdet_name

            # draw the contents of the small ntuple (to benefit from the auto-binning mechanism)

            # loop over all fedids

            isFirst = True

            for fed in self.fed_ids:
                plot_expr = "(size%03d/%f)>>" % (fed, self.unit_size)

                if isFirst:
                    isFirst = False
                    plot_expr += histo_name +  "(%d,%f,%f)" % (histo_nbins, histo_xmin, histo_xmax)
                else:
                    # append to existing histogram
                    plot_expr += "+" + histo_name

                # print "plot_expr=",plot_expr

                ntuple[num_vertices].Draw(plot_expr)

            getattr(ROOT,histo_name).SaveAs(output_data_dir + "/" + histo_name + ".xml")

            total_num_entries += getattr(ROOT,histo_name).GetEntries()

            ROOT.gROOT.cd()
            # fin.Close()
        # end loop over number of vertices

        print "total number of entries for " + self.subdet_title + ":", total_num_entries," which is %.1f per FED" % (total_num_entries / float(len(self.fed_ids)))

    #----------------------------------------
        
    def plot(self):

        global hs
        global legend

        hs = ROOT.THStack()
        legend = ROOT.TLegend(self.legend_spec['x1'], self.legend_spec['y1'],
                              self.legend_spec['x2'], self.legend_spec['y2']
                              )

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
        
        npoints = max_num_vertices + 1

        first_color = ROOT.TColor.CreateGradientColorTable(len(stops), stops, red, green, blue, npoints)

        assert(first_color >= 0)

        #--------------------

        total_num_events = 0

        num_vertex_to_histo = {}

        for num_vertices in range(max_num_vertices + 1):

            histo_name = "fed_size_dist_" + str(num_vertices) + "_" + self.subdet_name
            
            fin = ROOT.TFile.Open(output_data_dir + "/" + histo_name + ".xml")
            
            histo = fin.Get(histo_name)

            num_vertex_to_histo[num_vertices] = histo

            # set color
            # histo.SetFillColor(ROOT.kOrange - num_vertices)
            histo.SetFillColor(first_color + num_vertices)

            hs.Add(histo)

            if num_vertices == 1:
                title = "%d vertex" % num_vertices
            else:
                title = "%d vertices" % num_vertices
                
            legend.AddEntry(histo, title,"f")

            total_num_events += histo.GetEntries()

            fin.Close()
            ROOT.gROOT.cd()

            # end loop over number of vertices

        # this assumes that the entire sample is
        # cointained in the histograms together
        print "total_num_events=",total_num_events

        hs.Draw("nostack")

        hs.GetXaxis().SetTitle("FED sizes for " + self.subdet_title + " [" + self.unit_name + "]");

        # if self.show_fraction:
        #     title = "fraction of events/%.2f MB" % self.bin_width
        # else:

        # title = "number of FED and Events/%.2f MB" % self.bin_width
        title = "number of FED and Events"

        hs.GetYaxis().SetTitle(title);

        ROOT.gPad.SetLogy()
        ROOT.gPad.SetGrid()

        legend.Draw()

        ROOT.gPad.Modified()

        ROOT.gPad.SaveAs(plots_output_dir + "/fed-size-distributions-per-vertex-" + self.subdet_name + ".png")
        
    #----------------------------------------



#----------------------------------------------------------------------
gc_saver = []

# open all input ntuples
# map from number of vertices to input file
ntuple = utils.openSizePerFedNtuples()

fed_ids = getFedIdsFromTuple(ntuple[0])

# fed_ranges = getFedRanges(fed_ids)

fed_ranges = [
    # triggers & scalers:
    {'end': 760, 'name': 'CSCTF', 'start': 760},
    {'end': 780, 'name': 'DTTF', 'start': 780},
    {'end': 745, 'name': 'GCT', 'start': 745},
    {'end': 735, 'name': 'Lumi_Scalers', 'start': 735},
    {'end': 813, 'name': 'GlobalTrigger', 'start': 812},
    
    
    
    {'end': 757, 'name': 'CSC', 'start': 750},
    {'end': 779, 'name': 'DT', 'start': 770},
    {'end': 692, 'name': 'CASTOR', 'start': 690},
    
    
    {'end': 39,  'name': 'Pixel', 'start': 0},
    
    {'end': 574, 'name': 'Preshower', 'start': 520},
    {'end': 654, 'name': 'ECAL', 'start': 601},
    {'end': 731, 'name': 'HCAL', 'start': 700},
    
    {'end': 792, 'name': 'RPC', 'start': 790},
    
    
    {'end': 489, 'name': 'Tracker', 'start': 50},

    # {'end': 1023, 'name': 'DAQ', 'start': 1023},
    ]

#--------------------
# custom legend positions
legend_specs = {
    "CASTOR" :        { "x1": 0.2,  "y1": 0.6, "x2": 0.5, "y2": 0.9 },
    "GlobalTrigger" : { "x1": 0.35, "y1": 0.6, "x2": 0.65, "y2": 0.9 },

    "Lumi_Scalers" :  { "x1": 0.2,  "y1": 0.6, "x2": 0.5, "y2": 0.9 },
    }
#--------------------

for fed_range in fed_ranges:

    print "doing",fed_range['name']
    
    this_range_fedids = [ x for x in fed_ids if x >= fed_range['start'] and x <= fed_range['end'] ]

    name = fed_range['name']
    
    task = FedSizeDist(this_range_fedids, name.lower(), name,
                       legend_spec = legend_specs.get(name,None) )

    task.produce()
    task.plot()


