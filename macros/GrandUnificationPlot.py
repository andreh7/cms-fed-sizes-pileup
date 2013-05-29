import utils
parameters = utils.loadParameters()

import pylab

#----------------------------------------------------------------------
def makeGrandUnificationPlot(outputFiles, subsystemEvolutionData,
                             triggerRate = None,
                             xmax = 200,
                             printCSV = False,
                             keyFunc = None,
                             labelTextFunc = None,
                             subsystemsTitle = 'Subsystem'):

    """@param keyFunc: is the function determining the sorting of the lines.
                       If not given, entries are sorted by decreasing order of slope (and then offset).
                       Note that sorting always happens in reverse order.


       @param labelTextFunc is a function which takes three arguments subsystem, offset, slope
                          and must produce a string to be used for labeling of the plot.
                          If left None, a default function is used.
                       
                       """
    
    if triggerRate != None:
        # plot per FED rate instead of subsystem size
        subsystemEvolutionData = list(subsystemEvolutionData) # make a copy

        for data in subsystemEvolutionData:
            if data['numFeds'] == None:
                data['offset'] = None
                data['slope'] = None
                continue

            data['offset'] *= triggerRate / float(data['numFeds'])
            data['slope'] *= triggerRate / float(data['numFeds'])

    if printCSV:
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

    #xvalues = pylab.linspace(1,xmax,xmax + 1)
    import numpy
    xvalues = numpy.arange(1,xmax + 1,1)


    plots = []

    logy = False
    
    #--------------------
    # sort by slope first, then by offset
    # see e.g. http://stackoverflow.com/questions/1915376/is-pythons-sorted-function-guaranteed-to-be-stable/1971943#1971943

    if keyFunc == None:
        keyFunc = lambda x: (x['slope'], x['offset'])
    
    subsystemEvolutionData.sort(key = keyFunc, reverse = True)
    #--------------------
    # label text function
    #--------------------

    if labelTextFunc == None:
        if triggerRate != None:
            # per FED rate in MB/s
            labelTextFunc = lambda subsystem, offset, slope: "%s (%.2f + (%.2f/vertex)) MB/s" % (subsystem, offset, slope)
        else:
            # total size
            labelTextFunc = lambda subsystem, offset, slope: "%s (%.3f kB/vertex)" % (subsystem, slope)

    #--------------------
    for data in subsystemEvolutionData:

        if triggerRate != None:
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
        labelText = labelTextFunc(data['subsystem'], data['offset'], data['slope'])

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
        if triggerRate == None:
            fname = parameters.plots_output_dir + "/subsystem-gut.csv"
        else:
            fname = parameters.plots_output_dir + "/subsystem-gut-fed-rate.csv"        

        fout = open(fname,"w")

        for line in csvLines:
            print >> fout, ",".join([ x.strip() for x in line])

        fout.close()
        outputFiles.append(dict(fname = fname))

    #--------------------


    pylab.grid()
    pylab.xlabel("number of vertices")

    if triggerRate == None:
        pylab.ylabel("%s event size [kB]" % subsystemsTitle)

        pylab.figure()

        # pylab.legend(loc='upper left', bbox_to_anchor=(1, 3.5))


        pylab.title('%s Event Size Grand Unification' % subsystemsTitle)
    else:
        pylab.ylabel("per FED data rate [MB/s] at " + str(triggerRate) + " kHz trigger rate")

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
        where=numpy.logical_and(xvalues >= parameters.linear_fit_min_num_vertices, xvalues <= parameters.linear_fit_max_num_vertices ),
        facecolor='green',
        alpha=0.5)

    pylab.gca().add_collection(collection)
    #--------------------

    if triggerRate == None:
        fname = parameters.plots_output_dir + "/subsystem-gut"
    else:
        fname = parameters.plots_output_dir + "/subsystem-gut-fed-rate"        

    for fig, name in (
        (figPlot, fname),
        (figLegend, fname + "-legend"),
        ):

        name = name + ".png"
        fig.savefig(name)
        print "wrote",name

        outputFiles.append(dict(fname = name))

#----------------------------------------------------------------------
