#!/usr/bin/env python

import utils

#----------------------------------------------------------------------
# number of primary vertices found
#----------------------------------------------------------------------

class NumVertices:
    """ DOES THIS MAKE SENSE HERE ? BECAUSE WE ALREADY ASSUME
    THAT WE KNOW THE MAXIMUM NUMBER OF VERTICES BEFOREHAND
    (VARIABLE max_num_vertices). """

    #----------------------------------------
    def __init__(self, parameters, small_tuple):

        self.parameters = parameters
        self.small_tuple = small_tuple
        self.histo_fname = self.parameters.output_data_dir + "/num_vertices.xml"

    #----------------------------------------
    
    # to exclude parameters from being pickled
    # def __getstate__(self):
    #     state = dict(self.__dict__)
    #     del state['parameters']
    #         return state

    #----------------------------------------
    def produce(self):

        import ROOT

        draw_expr = "min(" + \
                    "num_vertices,%d" % self.parameters.max_num_vertices + \
                    ")>>histo_num_vertices(%d,-0.5,%.1f)" % (self.parameters.max_num_vertices + 1, self.parameters.max_num_vertices + 0.5)

                    # ")>>histo_num_vertices(8,-0.5,7.5)"

        self.small_tuple.tree.Draw(draw_expr,
                                   self.small_tuple.makeFullCut()
                                   )

        ROOT.histo_num_vertices.Sumw2()

        # save the histogram
        ROOT.histo_num_vertices.SaveAs(self.histo_fname)

    #----------------------------------------
        
    def plot(self, outputFilePrefix):
        import ROOT

        # load the histogram
        fin = ROOT.TFile.Open(self.histo_fname)

        global histo
        histo = fin.Get("histo_num_vertices")

        total_num_events = histo.GetEntries()

        #--------------------
        # fit the poissonian to the distribution starting at one

        numPoissonComponents = 1

        if numPoissonComponents == 1:
            func = ROOT.TF1("pois","[0]*TMath::Poisson(x,[1])",self.parameters.poisson_fit_start,self.parameters.poisson_fit_end)
            func.SetParName(0,"norm.")
            func.SetParName(1,"#mu")          
            func.SetParameter(0,1)
            func.SetParameter(1,0.5 * (self.parameters.poisson_fit_start + self.parameters.poisson_fit_end))
        elif numPoissonComponents == 2:
            # experimental: two Poissonians e.g. to capture multiple populations
            # originating from different triggers
            func = ROOT.TF1("pois","TMath::Abs([0])*TMath::Poisson(x,[1])+TMath::Abs([2])*TMath::Poisson(x,[3])",
                            self.parameters.poisson_fit_start,self.parameters.poisson_fit_end)

            func.SetParName(0,"sqrt(norm. 1)")
            func.SetParName(1,"#mu_{1}")
            func.SetParName(2,"sqrt(norm. 2)")
            func.SetParName(3,"#mu_{2}")

            func.SetParameter(0,1)
            func.SetParameter(1,10000)

            func.SetParameter(2,1)
            func.SetParameter(3,1)

            # note that we should use a reasonable estimate for the
            # upper limit due to the transformation ROOT internally
            # uses to map a finite range onto an unconstrained one...
            

        else:
            raise Exception("number Poisson components %d not yet supported" % numPoissonComponents)
            
        func.SetLineWidth(3)

        histo.SetMarkerStyle(20)
        histo.SetXTitle("Number of rec. primary vertices")
        histo.SetYTitle("Number of events")

        histo.Draw("Ep")

        if self.parameters.poissonFitYscalingFactor != None:
            histo.SetMaximum(self.parameters.poissonFitYscalingFactor * histo.GetMaximum())
            
        histo.Fit(func,"","",self.parameters.poisson_fit_start,self.parameters.poisson_fit_end)
        ROOT.gPad.Update()
        
        ROOT.gPad.SetLogy()
        ROOT.gPad.SetGrid()
        ROOT.gPad.Modified()

        stats = histo.FindObject("stats")
        stats.SetX1NDC(0.55)
        stats.SetY1NDC(0.73)
        stats.SetX2NDC(0.98)
        stats.SetY2NDC(0.99)
        ROOT.gPad.Modified()

        # calculate average number of vertices
        label = ROOT.TLatex(0.4,0.87,"num. events: %.0f" % total_num_events)
        label.SetNDC(1)
        label.Draw()

        #--------------------
        # get number of events per bin to calculate
        # the average number of vertices. 

        num_vertices_list = []
        num_events_list = []
        
        for i in range(1,histo.GetNbinsX()):
            num_vertices = histo.GetBinCenter(i)
            if num_vertices < 1:
                continue

            # print "num vertices: ",num_vertices, " events:",histo.GetBinContent(i)
            num_events_list.append(histo.GetBinContent(i))
            num_vertices_list.append(num_vertices)

        # keep this in the object such that we also can use it 
        # when using the pickled task objects
        self.avg_num_vertices = utils.weightedAverage(num_vertices_list, num_events_list)


        # print "average number of vertices:",self.avg_num_vertices

        label = ROOT.TLatex(0.2,0.2,"avg. # vertices: %.2f" % self.avg_num_vertices)
        label.SetNDC(1)
        label.Draw()

                                     
        ROOT.gPad.SaveAs(self.parameters.plots_output_dir + "/" + outputFilePrefix + "num-vertices-fitted.png")
        ROOT.gPad.SaveAs(self.parameters.plots_output_dir + "/" + outputFilePrefix + "num-vertices-fitted.C")
        fin.Close()

        #--------------------
        # write the average number of vertices also to a file
        # for later use in other tasks
        # do NOT use the output file prefix here because we need to read it from other modules
        utils.writeStringToFile(self.parameters.plots_output_dir + "/" + "avg-num-vertices.txt",str(self.avg_num_vertices) + "\n")

        #--------------------

        
        #--------------------
        fin = ROOT.TFile.Open(self.histo_fname)
        histo = fin.Get("histo_num_vertices")

        # draw the fraction
        histo.Scale(1/float(histo.GetEntries()))
        
        histo.SetMarkerStyle(20)
        histo.SetXTitle("number of rec. primary vertices")
        histo.SetYTitle("fraction of events")

        histo.Draw("Ep")
        
        ROOT.gPad.SetLogy()
        ROOT.gPad.SetGrid()

        label = ROOT.TLatex(0.4,0.87,"num. events: %.0f" % total_num_events)
        label.SetNDC(1)
        label.Draw()

        ROOT.gPad.SaveAs(self.parameters.plots_output_dir + "/" + outputFilePrefix + "num-vertices.png")

        fin.Close()
        ROOT.gROOT.cd()

        #--------------------
        # set output files
        #--------------------
        self.outputFiles = [
            dict(fname = self.parameters.plots_output_dir + "/" + outputFilePrefix + "num-vertices-fitted.png"),
            dict(fname = self.parameters.plots_output_dir + "/" + outputFilePrefix + "num-vertices.png"),
            dict(fname = self.parameters.plots_output_dir + "/" + "avg-num-vertices.txt"),
        ]
