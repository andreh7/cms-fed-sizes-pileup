import utils

import sys
import pylab

#----------------------------------------------------------------------

def makeSubsystemEvolutionData(tasks):
    # extracts linear fits per vertex results and returns
    # a dict of 
    #   grouping description mapping to
    #   list of dicts with the fit results
    #
    # a value item can be passed to a GrandUnificationPlot instance
    
    retval = {}

    from FedSizePerVertexLinearFit import FedSizePerVertexLinearFit

    for task in tasks:
        if not isinstance(task, FedSizePerVertexLinearFit):
            continue

        if task.subsys == 'total':
            # also add this, it gives a nice overview of the overall 
            # event size and rate
            grouping = 'total'
        else:
            grouping = task.grouping

        # sizes in kB (note that 'total' is in MB)
        retval.setdefault(grouping, []).append({
                "subsystem":  task.subsys, 
                "offset":     task.meanFitResult['alpha'], 
                "slope":      task.meanFitResult['beta'], 
                "numFeds":    task.numFeds,
                })

    return retval


#----------------------------------------------------------------------

class GrandUnificationPlot:
    # produce a plot with e.g. per subsystem evolution to large number
    # of vertices

    #----------------------------------------

    def __init__(self, 
                 parameters, tasks, groupingName,
                 triggerRate = None,
                 xmax = 200,
                 printCSV = False,
                 keyFunc = None,
                 labelTextFunc = None,
                 subsystemsTitle = 'Subsystem'):
        
        """
           @param tasks:   is the list of tasks to extract information from.
                           By the time this task runs, these tasks must have calculated
                           the fit result.
                           
           @param groupingName: the name of the grouping (e.g. 'by subsystem') for which the plot
                           is made
        
           @param keyFunc: is the function determining the sorting of the lines.
                           If not given, entries are sorted by decreasing order of slope (and then offset).
                           Note that sorting always happens in reverse order.


           @param labelTextFunc is a function which takes three arguments subsystem, offset, slope
                           and must produce a string to be used for labeling of the plot.
                           If left None, a default function is used.
                       """

        self.parameters      = parameters
        self.triggerRate     = triggerRate
        self.xmax            = xmax
        self.printCSV        = printCSV
        self.keyFunc         = keyFunc
        self.labelTextFunc   = labelTextFunc
        self.subsystemsTitle = subsystemsTitle
        self.tasks           = tasks
        self.groupingName    = groupingName

        #--------------------
        # sort by slope first, then by offset
        # see e.g. http://stackoverflow.com/questions/1915376/is-pythons-sorted-function-guaranteed-to-be-stable/1971943#1971943

        if self.keyFunc == None:
            self.keyFunc = lambda x: (x['slope'], x['offset'])

        #--------------------
        # label text function
        #--------------------

        if self.labelTextFunc == None:
            if self.triggerRate != None:
                # per FED rate in MB/s
                self.labelTextFunc = lambda subsystem, offset, slope: "%s (%.2f + (%.2f/vertex)) MB/s" % (subsystem, offset, slope)
            else:
                # total size
                self.labelTextFunc = lambda subsystem, offset, slope: "%s (%.3f kB/vertex)" % (subsystem, slope)



    #----------------------------------------
    def produce(self):
        #--------------------
        # extract fit results
        #--------------------

        self.subsystemEvolutionData = makeSubsystemEvolutionData(self.tasks)
        self.subsystemEvolutionData = self.subsystemEvolutionData.get(self.groupingName, None)

        if self.subsystemEvolutionData == None:
            print >> sys.stderr,"WARNING: grouping '%s' not found in GrandUnificationPlot" % self.groupingName
            return

        #--------------------

        if self.triggerRate != None:
            # plot per FED rate instead of subsystem size

            for data in self.subsystemEvolutionData:
                if data['numFeds'] == None:
                    data['offset'] = None
                    data['slope'] = None
                    continue

                data['offset'] *= self.triggerRate / float(data['numFeds'])
                data['slope'] *= self.triggerRate / float(data['numFeds'])


    #----------------------------------------
    
    def plot(self, outputFilePrefix):
        # we need to keep the output files as a class member for generating the HTML report
        self.outputFiles = []

        if self.subsystemEvolutionData == None:
            return self.outputFiles

        if self.printCSV:
            csvLines = []
        else:
            csvLines = None

        import pylab

        # figure with the plot
        figPlot = pylab.figure()

        #--------------------
        # draw legend next to pad
        #--------------------

        # if True:
        # 
        #     pylab.figure(figsize = (8 + 8,6 + 13))
        # 
        #     # scale back to 8,6
        #     ax = pylab.gca()
        #     box = ax.get_position()
        # 
        #     #         before         new
        #     xfactor = 8 * 0.8  /   ( (8+8) * 0.8)
        #     yfactor = 6 * 0.8  /   ( (6+13) * 0.8)
        # 
        #     ax.set_position([box.x0, box.y0, box.width * xfactor, box.height * yfactor])
        # else:
        #     pylab.figure(figsize = (8,6))


        #--------------------

        #xvalues = pylab.linspace(1,self.xmax,self.xmax + 1)
        import numpy
        xvalues = numpy.arange(1,self.xmax + 1,1)


        plots = []

        logy = False

        self.subsystemEvolutionData.sort(key = self.keyFunc, reverse = True)
        #--------------------
        for data in self.subsystemEvolutionData:

            if self.triggerRate != None:
                floatFormat = "%8.2f"
                unit = "MB/s"
            else:
                floatFormat = "%8.3f"
                unit = "kByte"

            #--------------------
            if data['slope'] == None:
                # e.g. when giving a potentially compliated expression of combination of FEDs
                slopeString = "-"
            else:
                slopeString = floatFormat % data['slope']

            #--------------------

            if data['numFeds'] == None:
                fedsString = "??"
            else:
                fedsString = "%3d" % data['numFeds']

            #--------------------
            if data['offset'] == None:
                offsetString = "-"
            else:
                offsetString = floatFormat % data['offset']

            print ("subsystem %-20s: #FEDS=" + fedsString + " offset=" + offsetString + " " + unit + " slope=" + slopeString + " " + unit + "/vtx") % (
                data['subsystem'],
                )

            if csvLines != None:
                if len(csvLines) == 0:
                    # add header before first data line
                    csvLines.append(["subsystem","number of feds","subsys", "offset","slope"])

                # find out which subsystem this corresponds to
                # if it's a single fed
                import re

                mo = re.match('FED(\d+)$', data['subsystem'])
                if mo:
                    subsys = utils.getSubsystemFromFed(int(mo.group(1)))
                    if subsys == None:
                        subsys = "???"
                else:
                    subsys = ""


                csvLines.append([data['subsystem'],
                                 fedsString,
                                 subsys,
                                 offsetString,
                                 slopeString])

            #--------------------                

            if data['slope'] == None or data['slope'] < 0.001:
                continue

            func = lambda x: data['offset'] + data['slope'] * x

            yvalues = [ func(x) for x in xvalues]

            # produce the label
            labelText = self.labelTextFunc(data['subsystem'], data['offset'], data['slope'])

            if logy:
                plot, = pylab.semilogy(xvalues,yvalues, '-',
                                   linewidth = 3,
                                   label = labelText)
            else:
                plot, = pylab.plot(xvalues,yvalues, '-',
                                   linewidth = 3,
                                   label = labelText)
            plots.append(plot)

        # end of loop over subsystems/groups of FEDs

        #--------------------
        # print the data also in CSV format
        #--------------------

        if csvLines != None:
            if self.triggerRate == None:
                fname = self.parameters.plots_output_dir + "/" + outputFilePrefix + "subsystem-gut.csv"
            else:
                fname = self.parameters.plots_output_dir + "/" + outputFilePrefix + "subsystem-gut-fed-rate.csv"        

            fout = open(fname,"w")

            for line in csvLines:
                print >> fout, ",".join([ x.strip() for x in line])

            fout.close()
            self.outputFiles.append(dict(fname = fname))

        #--------------------


        pylab.grid()
        pylab.xlabel("number of vertices")

        if self.triggerRate == None:
            pylab.ylabel("%s event size [kB]" % self.subsystemsTitle)

            pylab.figure()

            # pylab.legend(loc='upper left', bbox_to_anchor=(1, 3.5))


            pylab.title('%s Event Size Grand Unification' % self.subsystemsTitle)
        else:
            pylab.ylabel("per FED data rate [MB/s] at " + str(self.triggerRate) + " kHz trigger rate")

            import matplotlib.font_manager
            fontProp = matplotlib.font_manager.FontProperties(size=8)

            # pylab.legend(loc='upper left', prop = fontProp)

            pylab.title('Per FED Data Rate Grand Unification')

        #--------------------
        # produce a legend on a separate figure
        #--------------------

        figLegend = pylab.figure(figsize=(7,19))
        pylab.figlegend(*figPlot.gca().get_legend_handles_labels(), loc = 'upper left')

        # switch back to plot figure
        pylab.figure(figPlot.number)

        #--------------------
        # add a patch highlighting the maximum
        # number of vertices used here
        import matplotlib.collections as collections
        ymin, ymax = pylab.gca().get_yaxis().get_view_interval()

        collection = collections.BrokenBarHCollection.span_where(
               xvalues,
            ymin=ymin, ymax=ymax,

            # make the area span the linear fit
            where=numpy.logical_and(xvalues >= self.parameters.linear_fit_min_num_vertices, xvalues <= self.parameters.linear_fit_max_num_vertices ),
            facecolor='green',
            alpha=0.5)

        pylab.gca().add_collection(collection)
        #--------------------

        if self.triggerRate == None:
            fname = self.parameters.plots_output_dir + "/" + outputFilePrefix + "subsystem-gut"
        else:
            fname = self.parameters.plots_output_dir + "/" + outputFilePrefix + "subsystem-gut-fed-rate"        

        for fig, name in (
            (figPlot, fname),
            (figLegend, fname + "-legend"),
            ):

            name = name + ".png"
            fig.savefig(name)
            print "wrote",name

            self.outputFiles.append(dict(fname = name))


        return self.outputFiles

    #----------------------------------------

    def __getstate__(self):

        # exclude non-pickleable objects such as functions

        retval = dict(self.__dict__)

        del retval['keyFunc']
        del retval['labelTextFunc']

        return retval

#----------------------------------------------------------------------
