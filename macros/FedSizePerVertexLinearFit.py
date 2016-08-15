#----------------------------------------------------------------------
# FED size distribution: minimum, maximum, average and fit to average
#----------------------------------------------------------------------

import os

import utils
import FedSizePerXUtils

import ROOT

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
                 size_expr = "size_total", subsys_name = None,
                 grouping_name = None,
                 yaxis_unit_label = "MB", y_scale_factor = 0.001,
                 legendBottomLeft = None,
                 numFeds = None,
                 ):
        """ @param size_expr is the expression to plot, typically
            something like size_<subsys> but can also be an expression
            summing individual FEDs
            
        """

        self.parameters = parameters


        self.ymaxScale = getattr(self.parameters,'size_evolution_rel_yscale',1.2)
        self.ymaxScale = None


        # assert(size_expr.startswith("size_"))
        self.size_expr = size_expr

        #--------------------

        if subsys_name == None or 'size' in subsys_name:
            import re

            # build an automatic name
            # by replacing 'size_' either
            # by 'FED' if a number follows
            # or by the empty string if
            # a non-number (subsystem name)
            # follows

            tmp = str(self.size_expr)
            subsys_name = ""

            while tmp:
                # the matching of the overall will be
                # the first group,
                # the inner expression will be the second group
                mo = re.search("(size([0-9]+|_[0-9a-zA-Z]+))",tmp)

                if not mo:
                    # no match, just add the rest
                    subsys_name += tmp
                    tmp = ""
                    break

                # add everything before the matching
                subsys_name += tmp[:mo.start(1)]

                # keep only things after the match for
                # the next iteration
                tmp = tmp[mo.end(1):]

                groupName = mo.group(2)
                if groupName.startswith('_'):
                    groupName = groupName[1:]

                if utils.isIntString(groupName):
                    # seems to be a FED
                    subsys_name += "FED%s" % groupName
                else:
                    # seems to be a subsystem
                    subsys_name += groupName

            # while there is something left of the plot expression to convert

        #--------------------

        self.subsys = subsys_name
        self.grouping = grouping_name

        self.numFeds = numFeds

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
    def produce(self):

        # produce histograms of the fed size distributions

        ntuple = utils.openSizePerFedNtuples(self.parameters.input_data_dir, self.parameters.max_num_vertices)

        # maps from number of vertices to list of sum of fragment sizes
        self.fragmentSizes = {}

        for num_vertices in range(self.parameters.size_evolution_min_num_vertices,
                                  self.parameters.size_evolution_max_num_vertices + 1):

            # make sure this subsystem is known
            tupleVariables = [ x.GetName() for x in ntuple[num_vertices].GetListOfLeaves() ]
            ## if not self.size_variable in  tupleVariables:
            ##     raise Exception("no variable %s found in the per fed size tuple (is this a well known subsystem ?)" % self.size_variable)

            # get all the values in the ntuple
            ntuple[num_vertices].SetEstimate(ntuple[num_vertices].GetEntries())
            ntuple[num_vertices].Draw(self.size_expr,"","goff")

            # and write them out to a text file
            nentries = ntuple[num_vertices].GetSelectedRows()
            data = ntuple[num_vertices].GetV1()

            #----------
            # keep event sizes data
            #----------            
            self.fragmentSizes[num_vertices] = [ data[i] for i in range(nentries) ]

        # close the input file again (otherwise we'll run out of
        # file descriptors when running for all FEDs)
        ROOT.gROOT.cd()
        ntuple.values()[0].GetDirectory().GetFile().Close()
            
    #----------------------------------------

    def plot(self, outputFilePrefix):

        #----------
        if os.path.exists(self.parameters.plots_output_dir + "/avg-num-vertices.txt"):
            avg_num_vertices = float(open(self.parameters.plots_output_dir + "/avg-num-vertices.txt").read())
        else:
            avg_num_vertices = None

        #----------
        import array

        self.xpos = []
        self.min_values = []
        self.max_values = []
        self.avg_values = []

        # first index is the number of the quantile
        # second index is the index corresponding to the number of vertices
        self.quantile_values_lower = {}
        self.quantile_values_upper = {}

        # we should support the case where there were no events
        # for a given number of vertices

        for num_vertices in range(self.parameters.size_evolution_min_num_vertices,
                                  self.parameters.size_evolution_max_num_vertices + 1):

            # reading them back:
            event_sizes = self.fragmentSizes[num_vertices]
            
            event_sizes.sort()
            if event_sizes:
                # there were events with this number of reconstructed vertices

                # convert to kBytes
                event_sizes = [ x / 1000.0 for x in event_sizes ]

                self.min_values.append(min(event_sizes))
                self.max_values.append(max(event_sizes))

                self.avg_values.append(sum(event_sizes) / float(len(event_sizes)))

                # only append the current number of vertices
                # if there were actually some events
                self.xpos.append(num_vertices)

                #--------------------
                # calculate quantiles
                #--------------------

                for index, quantile_histo_def in enumerate(self.quantile_histo_defs):

                    # calculate the quantile
                    quantile = quantile_histo_def['quantile']
                    assert(quantile <= 0.5)

                    self.quantile_values_lower.setdefault(index,[]).append(utils.getQuantile(event_sizes, quantile))
                    self.quantile_values_upper.setdefault(index,[]).append(utils.getQuantile(event_sizes, 1.0 - quantile))

        #--------------------
        # use the helper class to actually per form the fit
        #--------------------
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

            xaxisTitle = "Number of rec. primary vertices",

            yaxisTitle = "Sum of FED sizes %s [%s]" % (self.subsys, self.yaxis_unit_label),

            subsys = self.subsys,

            yaxis_unit_label = self.yaxis_unit_label,
            
            numFeds = self.numFeds,

            xbinWidth = 0.8,

            averageNumVertices = avg_num_vertices,

            y_scale_factor = self.y_scale_factor,

            # for drawing the extrapolation
            linear_fit_extrapolation_min_num_vertices = getattr(self.parameters, 'linear_fit_extrapolation_min_num_vertices', None),
            linear_fit_extrapolation_max_num_vertices = getattr(self.parameters, 'linear_fit_extrapolation_max_num_vertices', None),

            )

        # perform lienar fit but only if the fitting range was specified
        if self.parameters.linear_fit_min_num_vertices != None and \
                self.parameters.linear_fit_max_num_vertices != None:

            plotter.fitAverage(linear_fit_min_value = self.parameters.linear_fit_min_num_vertices - 0.5,
                               linear_fit_max_value = self.parameters.linear_fit_max_num_vertices + 0.5,
                               label_template = "size = (%(offset).3f + nvtx * %(slope).3f) %(unit)s",
                               )

            self.alpha = plotter.alpha
            self.beta = plotter.beta

        else:
            self.alpha = None
            self.beta = None

        plotter.plot()

        #--------------------

        ROOT.gPad.SaveAs(self.parameters.plots_output_dir + "/" + outputFilePrefix + "average-sizes-vs-vertex-" + self.subsys + ".png")
        ROOT.gPad.SaveAs(self.parameters.plots_output_dir + "/" + outputFilePrefix + "average-sizes-vs-vertex-" + self.subsys + ".C")
        
        #--------------------
        # set output files
        #--------------------
        self.outputFiles = [
            dict(fname = self.parameters.plots_output_dir + "/" + outputFilePrefix + "average-sizes-vs-vertex-" + self.subsys + ".png"),
            dict(fname = self.parameters.plots_output_dir + "/" + outputFilePrefix + "average-sizes-vs-vertex-" + self.subsys + ".C"),
            ]

        # free memory
        del self.fragmentSizes
    
    #----------------------------------------
