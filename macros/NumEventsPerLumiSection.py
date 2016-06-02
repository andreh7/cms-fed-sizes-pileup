#!/usr/bin/env python

#----------------------------------------------------------------------
# number of events per lumi section
#----------------------------------------------------------------------
class NumEventsPerLumiSection:

    #----------------------------------------

    def __init__(self, parameters, small_tuple):
        self.parameters = parameters
        self.small_tuple = small_tuple

    #----------------------------------------

    def produce(self):
        # looks like it's fast to produce this plot,
        # no need to store an intermediate histogram for the moment
        pass

    #----------------------------------------
    def plot(self):

        import ROOT

        #--------------------
        # determine the maximum luminosity section automatically
        self.small_tuple.tree.SetEstimate(self.small_tuple.tree.GetEntries())
        self.small_tuple.tree.Draw("lumisection","","goff")
        entries = self.small_tuple.tree.GetSelectedRows()

        v1 = self.small_tuple.tree.GetV1()
        lumisections = [ v1[index] for index in xrange(entries) ]

        max_lumi_section = int(max(lumisections) * 1.1)
        #--------------------

        # let root fill the histogram
        self.small_tuple.tree.Draw("lumisection>>htemp(%d,-0.5,%f)" %
                    (max_lumi_section, max_lumi_section - 0.5))

        ROOT.gPad.SetGrid()
        ROOT.gPad.SetLogy(0)

        ROOT.htemp.SetXTitle("Luminosity section")
        ROOT.htemp.SetYTitle("# events per luminosity section")


        
        ROOT.gPad.SaveAs(self.parameters.plots_output_dir + "/events-per-lumi-section.png")

        #--------------------
        # set output files
        #--------------------
        self.outputFiles = [
            dict(fname = self.parameters.plots_output_dir + "/events-per-lumi-section.png"),
            ]

    #----------------------------------------

