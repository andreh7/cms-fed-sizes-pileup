#!/usr/bin/env python

# common utilities to plot quantile distributions
# of the fed size vs. e.g. the number of vertices
# or per bunch crossing luminosity bins

import array

#----------------------------------------------------------------------

def sigmaToArea(numSigmas):
    """ returns the area of a normal distribution between -numSigmas and +numSigmas """
    # see e.g. http://mathworld.wolfram.com/NormalDistribution.html for
    # the relation of the integral of the normal distribution and
    # the erf(..) function
    
    # and http://stackoverflow.com/questions/457408
    from scipy.special import erf
    import math
    
    return erf(numSigmas / math.sqrt(2))

    
#----------------------------------------------------------------------

# the quantiles to be plotted (see also fed-size-quantile-plots.py
# but these here are symmetric (because we work with graphs, not histograms)
# these should be ordered
import ROOT

standardQuantileHistoDefs = [
    # 0.1% - 99.9%
    # { "quantile": 0.001, "FillColor": ROOT.kRed }, 

    # 5-95% (5% larger, 5% less, note that this does NOT correspond to two sigma which would be approximately 2.5%-97.5% !)
    # { "quantile": 0.05, "FillColor": ROOT.kBlue },

    # +/- 3 sigma
    { "quantile": (1 - sigmaToArea(3)) / 2, "FillColor": ROOT.kRed },

    # +/- 3 sigma
    { "quantile": (1 - sigmaToArea(2)) / 2, "FillColor": ROOT.kBlue },

    # +/- 1 sigma
    { "quantile": (1 - sigmaToArea(1)) / 2, "FillColor": ROOT.kGreen },
    
    ]



#----------------------------------------------------------------------


def makeGraph(xpos, lowerValues, centerValues, upperValues, fillColor, x_error_size):
    """ makes a graph from the given lower and upper values """

    assert(len(xpos) == len(centerValues))
    assert(len(xpos) == len(lowerValues))
    assert(len(xpos) == len(upperValues))

    upper_error_sizes = [ x - y for x,y in zip(upperValues, centerValues)]
    lower_error_sizes = [ x - y for x,y in zip(centerValues,lowerValues) ]

    x_errors = array.array('d', [ x_error_size ] * len(xpos) )

    ROOT.gStyle.SetErrorX(x_error_size)
    gr = ROOT.TGraphAsymmErrors(len(xpos),
                                array.array('d',xpos),
                                array.array('d',centerValues),

                                x_errors,
                                x_errors,

                                array.array('d',lower_error_sizes),
                                array.array('d',upper_error_sizes),
                                )

    ROOT.gStyle.SetEndErrorSize(0)

    if fillColor != None:
        gr.SetFillColor(fillColor)

    return gr

#----------------------------------------------------------------------
# class plotter:
#
#  plotting functionality (once the quantiles were determined)
#  formerly in the class FedSizePerVertexLinearFit

class Plotter:

    #----------------------------------------
    
    def __init__(self,
                 xpos,   # the bin centers
                 min_values,
                 avg_values,  # average values
                 max_values,

                 legendXLeft,
                 legendYBottom,
                 legendWidth,
                 legendHeight,

                 minMaxBarColor,

                 plotMinMax,

                 quantile_histo_defs,

                 quantile_values_lower,

                 quantile_values_upper,

                 plotAvg,

                 ymaxScale,

                 xaxisTitle,

                 yaxisTitle,

                 subsys,

                 yaxis_unit_label,

                 numFeds,

                 xbinWidth,

                 averageNumVertices = None,

                 yaxis_unit_size = None,

                 linear_fit_extrapolation_min_num_vertices = None,

                 linear_fit_extrapolation_max_num_vertices = None,
                 ):

        self.xpos = xpos
        self.min_values = min_values
        self.avg_values = avg_values
        self.max_values = max_values

        self.legendXLeft   = legendXLeft
        self.legendYBottom = legendYBottom
        self.legendWidth   = legendWidth  
        self.legendHeight  = legendHeight

        self.minMaxBarColor = minMaxBarColor

        self.plotMinMax     = plotMinMax

        self.quantile_histo_defs = quantile_histo_defs

        self.quantile_values_lower = quantile_values_lower
        self.quantile_values_upper = quantile_values_upper

        self.plotAvg = plotAvg

        self.ymaxScale = ymaxScale

        self.xaxisTitle = xaxisTitle

        self.yaxisTitle = yaxisTitle

        self.subsys = subsys

        self.yaxis_unit_label = yaxis_unit_label

        self.numFeds = numFeds

        self.xbinWidth = xbinWidth

        self.averageNumVertices = averageNumVertices

        self.linear_fit_extrapolation_min_num_vertices = linear_fit_extrapolation_min_num_vertices

        self.linear_fit_extrapolation_max_num_vertices = linear_fit_extrapolation_max_num_vertices


        print "UUU ymaxScale=",ymaxScale

    #----------------------------------------

    def __makeAvgGraph(self):
        return makeGraph(
            self.xpos,
            self.avg_values, self.avg_values, self.avg_values,
            self.minMaxBarColor,
            self.xbinWidth / 2.0)
    #----------------------------------------

    def __makeMinMaxGraph(self):
        return makeGraph(
            self.xpos,
            self.min_values, self.avg_values, self.max_values,
            self.minMaxBarColor,
            self.xbinWidth / 2.0)

    #----------------------------------------

    def fitAverage(self,
                   linear_fit_min_value,
                   linear_fit_max_value,

                   # template for writing a text on the graph
                   # with the fit result
                   label_template,

                   ):
        """ perform a linear fit to the average values """
        import utils
        parameters = utils.loadParameters()

        global linear_fit_min_num_vertices, linear_fit_max_num_vertices

        # filter the values for the fit
        xpos_for_fit = []
        ypos_for_fit = []
        for x,y in zip(self.xpos, self.avg_values):
            if x >= linear_fit_min_value and \
               x <= linear_fit_max_value:
                xpos_for_fit.append(x)
                ypos_for_fit.append(y)

        # alpha, beta = linearFit(xpos, avg_values)
        self.alpha, self.beta = utils.linearFit(xpos_for_fit, ypos_for_fit)

        #--------------------

        print "subsys,alpha,beta=",self.subsys, self.alpha, self.beta

        self.fittedFunc = ROOT.TF1("linearfunc","[0]+x*[1]",
                                   linear_fit_min_value,
                                   linear_fit_max_value,
                                   )
        self.fittedFunc.SetParName(0,"const")
        self.fittedFunc.SetParName(1,"slope")
        self.fittedFunc.SetParameter(0,self.alpha)
        self.fittedFunc.SetParameter(1,self.beta)


        self.fitResultLabel = label_template % dict(
            offset = self.alpha,
            slope  = self.beta,
            unit   = self.yaxis_unit_label)
        

    #----------------------------------------
    def plot(self):
        """ produces the graph from the data supplied """

        if not globals().has_key('gc_saver'):
            globals()['gc_saver'] = []
        global gc_saver
        
        #--------------------
        # produce and draw the standard graphs
        #--------------------

        self.mg = ROOT.TMultiGraph(); gc_saver.append(self.mg)

        self.legend = ROOT.TLegend(self.legendXLeft, self.legendYBottom,
                                   self.legendXLeft + self.legendWidth, self.legendYBottom + self.legendHeight)

        self.avgGraph = self.__makeAvgGraph()
        self.minMaxGraph = self.__makeMinMaxGraph()

        if self.plotMinMax:
            self.mg.Add(self.minMaxGraph, "E2")
            self.legend.AddEntry(self.minMaxGraph, "Min/Max","F")

        #--------------------
        # produce and draw the quantile graphs
        #--------------------        
        
        for index, quantile_histo_def in enumerate(self.quantile_histo_defs):        
            gr = makeGraph(
                self.xpos,
                self.quantile_values_lower[index],
                self.avg_values, # should not matter what we use here
                self.quantile_values_upper[index],
                quantile_histo_def.get('FillColor',None),
                self.xbinWidth / 2.0,
                )

            self.mg.Add(gr,"E2")

            quantile_lower = 100 * quantile_histo_def['quantile']
            quantile_upper = 100 - quantile_lower
            quantile_area = quantile_upper - quantile_lower
            
            # self.legend.AddEntry(gr, "%.1f-%.1f%% (%.1f%%)" % (quantile_lower, quantile_upper, quantile_area), "F")
            self.legend.AddEntry(gr, "%.1f%%" % quantile_area, "F")

        #--------------------
        # plot the average graph (bullets) last
        #--------------------
        if self.plotAvg:

            self.mg.Add(self.avgGraph,"P")

            self.legend.AddEntry(self.avgGraph,"average","P")
        

        # draw an extrapolation line if requested
        # (draw before the fitted line so )

        if hasattr(self,'fittedFunc') and \
               self.linear_fit_extrapolation_min_num_vertices != None and \
               self.linear_fit_extrapolation_max_num_vertices != None:
            # just draw a line through the two endpoints
            xvalues = [ self.linear_fit_extrapolation_min_num_vertices, self.linear_fit_extrapolation_max_num_vertices]
            yvalues = [ self.fittedFunc.Eval(x) for x in xvalues ]

            gr = ROOT.TGraph(2, array.array('f',xvalues), array.array('f',yvalues)); gc_saver.append(gr)
            gr.SetLineWidth(3)
            gr.SetLineColor(ROOT.kRed)
            gr.SetLineStyle(ROOT.kDashed)
            
            self.mg.Add(gr,"L")


        #--------------------
        # draw all the graphs
        #--------------------

        ROOT.gPad.Clear()         # avoid drawing over the previous plot
        self.mg.Draw("A")

        if self.ymaxScale != None:

            # find out the global maximum
            overallMax = self.mg.GetHistogram().GetMaximum()

            overallMax *= self.ymaxScale

            print "VVV applying ymaxscale",self.ymaxScale,overallMax

            self.mg.SetMaximum(overallMax)
            self.mg.SetMinimum(0)

            ROOT.gPad.Modified()
                
        self.legend.SetFillColor(ROOT.kWhite)
        self.legend.Draw()

        #--------------------
        # produce the axis labels
        #--------------------

        ROOT.gPad.SetGrid()

        self.mg.GetXaxis().SetTitle(self.xaxisTitle)
        self.mg.GetYaxis().SetTitle(self.yaxisTitle)

        #--------------------
        # plot the linear fit to the average values
        #--------------------
        # global fittedFunc

        if hasattr(self,'fittedFunc'):

            self.fittedFunc.Draw("same")

            ROOT.gPad.SetLogy(0)

            self.fittedFunc.SetLineWidth(3)
            self.fittedFunc.SetLineColor(ROOT.kBlue)

            label = ROOT.TLatex(0.20,0.9,self.fitResultLabel)
            label.SetNDC(1)
            label.Draw()


            gc_saver.append(label)
            gc_saver.append(self.fittedFunc)

        #--------------------
        # add the run number to the plot
        #--------------------
        if True:

            import utils
            parameters = utils.loadParameters()

            label = ROOT.TLatex(0.89,0.15,"run %d" % parameters.run)
            label.SetNDC(True)
            label.SetTextSize(label.GetTextSize() * 0.5)
            label.SetTextAlign(31)
            label.Draw()
            gc_saver.append(label)

        #--------------------
        if self.numFeds != None:
            #--------------------
            # add a small label with number of FEDs
            label = ROOT.TLatex(0.9,0.96,"%d FEDS" % self.numFeds)
            label.SetNDC(True)
            label.SetTextSize(label.GetTextSize() * 0.5)
            label.SetTextAlign(31)
            label.Draw()
            gc_saver.append(label)

            #--------------------
            # add a second axis with the average
            # data rate per FED at a given trigger rate

            # example trigger rate in kHz
            triggerRate = 100


            ROOT.gPad.SetRightMargin(0.15)

            # how to go from total event size (in kByte) to
            # per FED data rate (in MByte/s) ?
            # just multiply by the trigger rate in kHz
            # and divide by the number of FEDs

            yaxisMin = self.mg.GetHistogram().GetMinimum()
            yaxisMax = self.mg.GetHistogram().GetMaximum()

            xaxisMax = self.mg.GetHistogram().GetXaxis().GetXmax()

            # print "XXX yaxisMin=",yaxisMin,"yaxisMax=",yaxisMax

            # name for conversion function
            funcName = "axisConversionFunc_%s" % self.subsys
            func = ROOT.TF1(funcName,"x",triggerRate * yaxisMin / float(self.numFeds), triggerRate * yaxisMax / float(self.numFeds))

            rightAxis = ROOT.TGaxis(xaxisMax, yaxisMin, xaxisMax, yaxisMax, funcName, 505, "L+")
            rightAxis.SetTitle("per FED rate [MB/s] @ %d kHz" % triggerRate)
            rightAxis.SetTitleOffset(rightAxis.GetTitleOffset() * 1.5)

            rightAxis.Draw()
            gc_saver.append(rightAxis)

            # remove original tick marks on right side (from tdrStyle)
            ROOT.gPad.SetTicky(0)
            

        #--------------------
        # arrow for average number of vertices
        # (and also other user specified)
        #--------------------

        linear_fit_arrows = getattr(parameters, "linear_fit_arrows", [ dict(vtx = "avg") ])

        if hasattr(self, 'fittedFunc'):
            # left end for horizontal arrows
            xmin, xmax = self.mg.GetXaxis().GetXmin(), self.mg.GetXaxis().GetXmax()
            xleft = xmin + 0.05 * (xmax - xmin)

            # lower end for vertical arrows
            ymin, ymax = self.mg.GetYaxis().GetXmin(), self.mg.GetYaxis().GetXmax()
            ymin = 0
            ybot  = ymin + 0.08 * (ymax - ymin)
            print "ymin,ymax=",ymin,ymax

            for line in linear_fit_arrows:

                xpos = line['vtx']

                if xpos == "avg":
                    if self.averageNumVertices == None:
                        # can't draw this
                        continue
                    xpos = self.averageNumVertices

                ypos = self.fittedFunc(xpos)

                #----------
                # vertical arrow
                #----------

                arrow = ROOT.TArrow(xpos, ypos,
                                    xpos, ybot)

                gc_saver.append(arrow)

                arrow.SetLineWidth(2)
                arrow.Draw()

                # add a label with the average number of vertices
                xlabel = ROOT.TLatex(xpos, ybot + (ypos - ybot) * 0.5,"  %.1f vtx" % xpos)
                xlabel.SetTextSize(xlabel.GetTextSize() * 0.5)
                gc_saver.append(xlabel)

                xlabel.Draw()

                #----------
                # horizontal arrow
                #----------

                print "PP",xpos,ypos,xleft

                arrow = ROOT.TArrow(xpos, ypos,
                                    xleft, ypos)

                gc_saver.append(arrow)

                arrow.SetLineWidth(2)
                arrow.Draw()

                # add a label with the average number of vertices

                if self.yaxis_unit_label.lower() == 'kb':
                    yval = ypos
                elif self.yaxis_unit_label.lower() == 'mb':
                    yval = ypos * 1000.0

                ylabel = ROOT.TLatex(xleft, ypos * 1.1,"  %.1f kByte" % yval)
                ylabel.SetTextSize(xlabel.GetTextSize() * 0.9)
                gc_saver.append(ylabel)

                ylabel.Draw()

            # end of loop over arrows

        # if has a fitted function
