#!/usr/bin/env python

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
    def __init__(self, parameters, small_tuple):

        self.parameters = parameters
        self.small_tuple = small_tuple

        self.show_fraction = True

        # bin width in MB
        self.bin_width = ( self.parameters.fedsize_histo_xmax - self.parameters.fedsize_histo_xmin ) / float(self.parameters.fedsize_histo_nbins)

        print "bin_width=",self.bin_width

    #----------------------------------------
    def produce(self):

        # produce histograms of the fed size distributions

        for num_vertices in range(1,self.parameters.max_num_vertices + 1):

            histo_name = "fed_size_dist_" + str(num_vertices)

            plot_expr = "min(total_event_size/1e6,%f)>>%s(%d,%f,%f)" % \
                        (self.parameters.fedsize_histo_xmax * 0.999, 
                         histo_name,
                         self.parameters.fedsize_histo_nbins,
                         self.parameters.fedsize_histo_xmin, 
                         self.parameters.fedsize_histo_xmax
                         )

            cut_expr = "min(num_vertices,%d)" % (self.parameters.max_num_vertices) + " == %d" % num_vertices

            print "plot_expr=",plot_expr
            print "cut_expr=",cut_expr
            

            self.small_tuple.tree.Draw(plot_expr,cut_expr)

            import ROOT

            # do we need errors and histogram normalization ?
            # ROOT.histo_num_vertices.Sumw2()

            # save the histogram
            # seems not to work
            # ROOT.gROOT.Get(histo_name).SaveAs("data/" + histo_name + ".xml")

            getattr(ROOT,histo_name).SaveAs(self.parameters.output_data_dir + "/" + histo_name + ".xml")

    #----------------------------------------
        
    def plot(self):

        global hs
        global legend
        import ROOT

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
        
        npoints = self.parameters.max_num_vertices

        first_color = ROOT.TColor.CreateGradientColorTable(len(stops), stops, red, green, blue, npoints)

        assert(first_color >= 0)

        #--------------------

        total_num_events = 0

        num_vertex_to_histo = {}

        for num_vertices in range(1,self.parameters.max_num_vertices + 1):

            histo_name = "fed_size_dist_" + str(num_vertices)

            fin = ROOT.TFile.Open(self.parameters.output_data_dir + "/" + histo_name + ".xml")
            
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
            for num_vertices in range(1,self.parameters.max_num_vertices + 1):            
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

        ROOT.gPad.SaveAs(self.parameters.plots_output_dir + "/fed-size-distributions-per-vertex.png")

        #--------------------
        # set output files
        #--------------------
        self.outputFiles = [
            dict(fname = self.parameters.plots_output_dir + "/fed-size-distributions-per-vertex.png"),
        ]

        
    #----------------------------------------
