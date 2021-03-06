#----------------------------------------------------------------------
# FED size distribution: minimum, maximum, average and fit to average
#----------------------------------------------------------------------

import os

import utils
import FedSizePerXUtils

import ROOT
import numpy as np

#----------------------------------------------------------------------

class FedSizePerVertexLinearFit:

    #----------------------------------------
    # parameters
    #----------------------------------------

    # the quantiles to be plotted (see also fed-size-quantile-plots.py
    # but these here are symmetric (because we work with graphs, not histograms)
    # these should be ordered
    quantile_histo_defs = FedSizePerXUtils.standardQuantileHistoDefs[:]

    # minMaxBarColor = ROOT.kRed
    minMaxBarColor = ROOT.kRed - 8

    plotMinMax = True
    plotAvg = True

    # default parameters for legend
    legendWidth = 0.25
    legendHeight = 0.2

    legendXLeft = 0.6
    legendYBottom = 0.65

    #----------------------------------------

    def __init__(self, 
                 parameters,
                 fedSizeMatrix,
                 fedIds, subsys_name = None,
                 grouping_name = None,
                 yaxis_unit_label = "MB", y_scale_factor = 0.001,
                 legendBottomLeft = None,
                 xvar = 'vtx',
                 ):
        """ @param size_expr is the expression to plot, typically
            something like size_<subsys> but can also be an expression
            summing individual FEDs

            @param xvar can be vtx or pu: for vtx, the sizes are
            plotted against the number of reconstructed primary
            vertices, for pu against the (average) number of pileup
            for the given instantaneous luminosity of this
            bunch crossing and lumi section
        """

        self.parameters = parameters
        self.fedSizeMatrix = fedSizeMatrix
        self.fedIds = fedIds

        self.ymaxScale = getattr(self.parameters,'size_evolution_rel_yscale',1.2)
        self.ymaxScale = None

        assert xvar in ('vtx', 'pu')
        self.xvar = xvar

        #--------------------

        assert subsys_name != None

        self.subsys = subsys_name
        self.grouping = grouping_name

        self.numFeds = len(self.fedIds)

        self.yaxis_unit_label = yaxis_unit_label
        self.y_scale_factor = y_scale_factor

        if legendBottomLeft != None:
            self.legendXLeft = legendBottomLeft[0]
            self.legendYBottom = legendBottomLeft[1]
        # else:
        #     # copy static default values
        #     self.legendXLeft = legendXLeft
        #     self.legendYBottom = legendYBottom

    #----------------------------------------

    def getXvarRange(self):
        # @return minVal, maxVal

        if self.xvar == 'vtx':
            return self.parameters.size_evolution_min_num_vertices, self.parameters.size_evolution_max_num_vertices
        elif self.xvar == 'pu':
            return self.parameters.size_evolution_min_pu, self.parameters.size_evolution_max_pu
        else:
            raise Exception("internal error")

    #----------------------------------------
    def getLinearFitRange(self):
        # returns min,max of range for linear fit. Note that
        # one or both values can be None
        
        if self.xvar == 'vtx':
            return self.parameters.linear_fit_min_num_vertices, self.parameters.linear_fit_max_num_vertices
        elif self.xvar == 'pu':
            return getattr(self.parameters,'linear_fit_min_pu', None), getattr(self.parameters, 'linear_fit_max_pu', None)
        else:
            raise Exception("internal error")

    #----------------------------------------

    def produce(self):

        # produce vectors of the fed sizes as function of number of vertices
        # maps from number of vertices or average pileup to list of sum of fragment sizes
        self.fragmentSizes = {}

        minVal, maxVal = self.getXvarRange()

        # loop over number of vertices or pileup
        for xvalue in range(minVal, maxVal + 1):

            #----------
            # keep event sizes data
            #----------            
            self.fragmentSizes[xvalue] = self.fedSizeMatrix.getFedSums(xvalue, self.fedIds, self.xvar == 'pu')

        # we don't need the pointer to the matrix anymore, avoid that it
        # is pickled with this object into the output file...
        del self.fedSizeMatrix

    #----------------------------------------

    def plot(self, outputFilePrefix):

        #----------

        # get average number of vertices if we plot the sizes
        # vs. number of vertices
        # TODO: should get this from one of the previous tasks
        avg_xvalue = None

        if self.xvar == 'vtx':
            if os.path.exists(self.parameters.plots_output_dir + "/avg-num-vertices.txt"):
                avg_xvalue = float(open(self.parameters.plots_output_dir + "/avg-num-vertices.txt").read())

        #----------
        import array

        self.xpos = []
        self.min_values = []
        self.max_values = []
        self.avg_values = []
        self.median_values = []

        # first index is the number of the quantile
        # second index is the index corresponding to the number of vertices
        self.quantile_values_lower = {}
        self.quantile_values_upper = {}

        # we should support the case where there were no events
        # for a given number of vertices

        minVal, maxVal = self.getXvarRange()

        # loop over number of vertices or pileup
        for xvalue in range(minVal, maxVal + 1):

            # reading them back:
            event_sizes = self.fragmentSizes[xvalue]
            
            event_sizes.sort()
            if event_sizes != None and len(event_sizes) > 0:
                # event_sizes is a numpy array
                # there were events with this number of reconstructed vertices

                # convert to kBytes
                event_sizes = event_sizes / 1000.0 

                self.min_values.append(min(event_sizes))
                self.max_values.append(max(event_sizes))

                self.avg_values.append(sum(event_sizes) / float(len(event_sizes)))
                self.median_values.append(np.median(event_sizes))

                # only append the current number of vertices
                # if there were actually some events
                self.xpos.append(xvalue)

                #--------------------
                # calculate quantiles
                #--------------------

                for index, quantile_histo_def in enumerate(self.quantile_histo_defs):

                    # calculate the quantile
                    quantile = quantile_histo_def['quantile']
                    assert(quantile <= 0.5)
                    
                    # first index is quantile type, second index is number of vertices
                    self.quantile_values_lower.setdefault(index,[]).append(utils.getQuantile(event_sizes, quantile))
                    self.quantile_values_upper.setdefault(index,[]).append(utils.getQuantile(event_sizes, 1.0 - quantile))

        #--------------------
        # use the helper class to actually perform the fit
        #--------------------


        if self.xvar == 'vtx':
            extrapolationXmin = getattr(self.parameters, 'linear_fit_extrapolation_min_num_vertices', None),
            extrapolationXmax = getattr(self.parameters, 'linear_fit_extrapolation_max_num_vertices', None)

            xaxisTitle = "Number of rec. primary vertices"

        elif self.xvar == 'pu':
            extrapolationXmin = getattr(self.parameters, 'linear_fit_extrapolation_min_pu', None),
            extrapolationXmax = getattr(self.parameters, 'linear_fit_extrapolation_max_pu', None)

            xaxisTitle = "avg. interactions per BX"
        else:
            raise Exception("internal error")

        

        plotter = FedSizePerXUtils.Plotter(
            self.parameters,
            xpos = self.xpos,
            min_values = self.min_values,
            avg_values = self.avg_values,
            max_values = self.max_values,

            legendXLeft   = self.legendXLeft,
            legendYBottom = self.legendYBottom,
            legendWidth   = self.legendWidth,
            legendHeight  = self.legendHeight,  

            minMaxBarColor = self.minMaxBarColor,

            plotMinMax     = self.plotMinMax,

            quantile_histo_defs = self.quantile_histo_defs,

            quantile_values_lower = self.quantile_values_lower,

            quantile_values_upper = self.quantile_values_upper,
            
            plotAvg = self.plotAvg,

            ymaxScale = self.ymaxScale,

            xaxisTitle = xaxisTitle,

            yaxisTitle = "Sum of FED sizes %s [%s]" % (self.subsys, self.yaxis_unit_label),

            subsys = self.subsys,

            yaxis_unit_label = self.yaxis_unit_label,
            
            numFeds = self.numFeds,

            xbinWidth = 0.8,

            averageNumVertices = avg_xvalue,

            y_scale_factor = self.y_scale_factor,

            # for drawing the extrapolation
            linear_fit_extrapolation_min_num_vertices = extrapolationXmin,
            linear_fit_extrapolation_max_num_vertices = extrapolationXmax,

            )

        # perform linear fit but only if the fitting range was specified

        self.meanFitResult = {}
        self.uncertFitResult = {}

        linearFitXmin, linearFitXmax = self.getLinearFitRange()

        if  not linearFitXmin is None and not linearFitXmax is None:

            plotter.fitAverage(linear_fit_min_value = linearFitXmin - 0.5,
                               linear_fit_max_value = linearFitXmax + 0.5,
                               degree = self.parameters.fitFunctionDegree,
                               label_func = self.labelFunc,
                               )

            self.meanFitResult = dict(coeffs = plotter.meanFitResult['coeffs'])
            self.uncertFitResult = dict(coeffs = plotter.uncertFitResult['coeffs'])
        else:
            self.meanFitResult = dict(coeffs = None)
            self.uncertFitResult = dict(coeffs = None)

        plotter.plot()

        #--------------------

        if self.xvar == 'vtx':
            xvarName = "vertex"
        elif self.xvar == 'pu':
            xvarName = 'pu'
        else:
            raise Exception("internal error")

        outputFname = self.parameters.plots_output_dir + "/" + outputFilePrefix + "average-sizes-vs-" + xvarName + "-" + self.subsys + ".png"
        ROOT.gPad.SaveAs(outputFname)
        
        #--------------------
        # set output files
        #--------------------
        self.outputFiles = [
            dict(fname = outputFname),
            ]

        # free memory and avoid pickling this object
        del self.fragmentSizes
    
    #----------------------------------------

    def writeQuantilesCSV(self, os, writeHeader = False):
        # writes quantiles per number of vertex to a CSV format file

        if writeHeader:
            header = [ "subsys", 
                       "num vertices",
                       "mean",
                       ]

            for quantileDef in self.quantile_histo_defs:
                header.append("minus " + quantileDef['title'])

            header.append("median")

            for quantileDef in reversed(self.quantile_histo_defs):
                header.append("plus " + quantileDef['title'])

            print >> os, ",".join(header)

        #----------
        assert len(self.avg_values) == len(self.xpos)

        for index, xvalue in enumerate(self.xpos):

            parts = [ self.subsys, xvalue ]

            # add mean
            parts.append(self.avg_values[index])

            for quantileIndex in range(len(self.quantile_values_lower)):
                parts.append(self.quantile_values_lower[quantileIndex][index])

            # add median
            parts.append(self.median_values[index])

            for quantileIndex in reversed(range(len(self.quantile_values_lower))):
                parts.append(self.quantile_values_upper[quantileIndex][index])
        
            print >> os, ",".join([ str(x) for x in parts ])

    #----------------------------------------

    def labelFunc(self, coeffs, unit):
        # function returning a label given the fitted coefficients
        #
        # older version: "size = (%(offset).3f + nvtx * %(slope).3f) %(unit)s"

        assert len(coeffs) >= 1

        if self.xvar == 'vtx':
            varname = 'nvtx'
        elif self.xvar == 'pu':
            varname = 'pu'
        else:
            raise Exception("internal error")

        if len(coeffs) == 1:
            retval = "%.3f" % coeffs[0]
        elif len(coeffs) == 2:
            retval = "%.3f + %s * %.3f" % (coeffs[0], varname, coeffs[1])
        else:
            retval = "%.3f + %s * %.3f + O(%s^2)" % (coeffs[0], varname, coeffs[1], varname)

        # note the additional s for plural of the unit
        return "size = (%s) %ss" % (retval, unit)

    #----------------------------------------

