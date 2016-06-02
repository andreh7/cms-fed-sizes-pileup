#!/usr/bin/env python

import utils

gcs = []

#----------------------------------------------------------------------
# make a plot of delivered lumi vs. lumi section
#----------------------------------------------------------------------
class LuminosityEvolution:

    #----------------------------------------
    def __init__(self, parameters, smallTuple):

        # use /cm^2 units instead of
        # inv nb/lumisection
        self.use_cm = True

        self.parameters = parameters
        self.smallTuple = smallTuple

    #----------------------------------------

    def produce(self):
        pass

    #----------------------------------------
    def plot(self):

        # list of output files
        self.outputFiles = [ ]

        # get the processed lumi sections from the data tuples
        all_lumi_sections = self.smallTuple.getAllLumiSections()

        fname = "lumi-by-ls-%d.csv" % self.parameters.run

        import os
        if not os.path.exists(fname):
            print "could not find file '%s'," % fname
            print "you should run"
            print"     lumiCalc.py -r %d -o lumi-by-ls-%d.csv --nowarning lumibyls" % (self.parameters.run, self.parameters.run)
            print "Skipping luminosity evolution plot. Press return."
            sys.stdin.readline()
            return
        
        import csv
        csv_reader = csv.reader(open(fname))

        if False:
            # LHC RUN I lumiCalc.py
            line = csv_reader.next()
            assert(line == ['run', 'ls', 'delivered', 'recorded'])
            posLS = 1
            posDelivered = 2
            posRecorded = 3
        if True:
            # LHC RUN II brilcalc
            line = csv_reader.next()
            line = csv_reader.next()
            print "line=",line
            assert(line == ['#run:fill', 'ls', 'time' , 'beamstatus' , 'E(GeV)', 'delivered(/ub)', 'recorded(/ub)', 'avgpu', 'source'])
            posLS = 1
            posDelivered = 5
            posRecorded = 6


        import ROOT
        lumi_tuple = ROOT.TNtuple("lumi_tuple","lumi_tuple",":".join([
            "lumisection",
            "delivered",
            "recorded",
            ]))

        total_rec_lumi = 0
        total_del_lumi = 0

        for line in csv_reader:
            if line[0].startswith('#'):
                continue

            if False:
                # LHC Run I
                lumisection = int(line[posLS])
            if True:
                # LHC Run II
                lumisection, lumisection2 = [ int(x) for x in line[posLS].split(':')]
                assert lumisection == lumisection2 or lumisection2 == 0

            # restrict the plot only to the lumisections
            # found in the root files
            if not lumisection in all_lumi_sections:
                continue
            
            delivered_lumi = float(line[posDelivered]) * utils.INV_MU_BARN
            recorded_lumi = float(line[posRecorded]) * utils.INV_MU_BARN

            lumi_tuple.Fill(lumisection,
                            delivered_lumi / utils.INV_NANO_BARN,
                            recorded_lumi / utils.INV_NANO_BARN,
                            )


            total_rec_lumi += recorded_lumi
            total_del_lumi += delivered_lumi

        for name, total in (
            ('delivered', total_del_lumi),
            ('recorded', total_rec_lumi),
            ):

            self.canvas = ROOT.TCanvas()

            ROOT.gPad.SetLogy(0)

            if self.use_cm:
                quantity = ("%s *" %name) +  str(utils.INV_NANO_BARN * utils.CM2 / utils.seconds_per_lumi_section)
            else:
                quantity = "%s" % name

            # note that TNTuple::Draw(..) seems to create a 2D histogram (not a 1D one)
            # so we can't simply change the y scale by setting SetMaximum(..)
            #
            # first draw the tuple to get the x and y ranges
            lumi_tuple.Draw(quantity + ":lumisection","","goff")

            htemp = lumi_tuple.GetHistogram()

            # create an empty histogram just for the scale
            # 
            # set the y range mostly for the delivered luminosity plot (the recorded
            # typically has dips going to zero because of resyncs)

            dummy = ROOT.TH2F("dummy","",
                              1, htemp.GetXaxis().GetXmin(), htemp.GetXaxis().GetXmax(), # xaxis
                              1,                          0, htemp.GetYaxis().GetXmax() * 1.1  # yaxis
                              )
            gcs.append(dummy)
            dummy.Draw()

            # draw the tuple again
            lumi_tuple.Draw(quantity + ":lumisection","","same")
                              
            dummy.SetXTitle("luminosity section number")

            if self.use_cm:
                dummy.SetYTitle("%s luminosity [cm^{-2}s^{-1}]" % name)
            else:
                dummy.SetYTitle("%s luminosity per LS [nb^{-1}]" % name)

            #--------------------

            ROOT.gPad.SetGrid()

            #--------------------
            # figure out an appropriate unit for the luminosity
            lumiForPrinting = total / utils.INV_PICO_BARN
            if lumiForPrinting < 1:
                # use inverse nanobarns instead
                lumiForPrinting = "%.1f nb^{-1}" % (lumiForPrinting * 1000)
            else:
                # use inverse picobarns
                lumiForPrinting = "%.1f pb^{-1}" % lumiForPrinting

            self.label = ROOT.TLatex(0.25,0.25,"integrated luminosity: " + lumiForPrinting)

            #--------------------

            self.label.SetNDC(1)
            self.label.Draw()
            ROOT.gPad.Modified()
            # ROOT.gPad.Update()

            ROOT.gPad.SaveAs(self.parameters.plots_output_dir + "/lumi-evolution-%s.png" % name)
            self.outputFiles.append(
                dict(fname = self.parameters.plots_output_dir + "/lumi-evolution-%s.png" % name)
                )

            print "total %s lumi =" % name,total / utils.INV_PICO_BARN,"/pb"



    #----------------------------------------
        
