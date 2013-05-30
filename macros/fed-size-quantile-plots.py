from pprint import pprint
import ROOT
ROOT.gROOT.ProcessLine(".x ~/rootlogon.C")
ROOT.gROOT.ProcessLine("setTDRStyle();")
ROOT.gStyle.SetErrorX(0.5)

import utils

#----------------------------------------------------------------------
# parameters
#----------------------------------------------------------------------

# execfile("parameters.py")

import utils
parameters = utils.loadParameters()
#--------------------

# quantiles = [ 0.50, 0.95, 0.999, "mean" ]

# the quantiles to be plotted
quantile_histo_defs = [

    { "quantile": 0.50, "FillColor": ROOT.kGreen },

    { "quantile": 0.95, "FillColor": ROOT.kBlue },

    { "quantile": 0.999, "FillColor": ROOT.kRed }, 

    ]

draw_mean = False

subdet_range_arrow_ypos = 3000
subdet_range_label_ypos = 3200

subdet_range_arrow_size = 0.005

# for debugging or adjusting the plots: NOTE THAT THIS
# NOW GIVES A BIASED VIEW AS IT PROCESSES THE EVENTS
# GROUPED BY NUMBER OF RECONSTRUCTED VERTICES
# max_events_per_fed = 10000
# max_events_per_fed = 100000
max_events_per_fed = None  # take all events

#----------------------------------------------------------------------
isiterable = lambda obj: isinstance(obj, basestring) or getattr(obj, '__iter__', False)
#----------------------------------------------------------------------

class MainClass:

    #----------------------------------------

    def __init__(self, rootFile):
        # get all tuples for all number
        # of reconstructed vertices
        self.numVerticesToTuple = {}

        import re

        for keyName in [ x.GetName() for x in rootFile.Get("tupler").GetListOfKeys() ]:

            # print "KEY=",keyName

            obj = rootFile.Get("tupler/" + keyName)
            if not isinstance(obj, ROOT.TNtuple):
                continue

            mo = re.match("all_sizes_(\d+)vtx", keyName)

            if not mo:
                continue

            numVertices = int(mo.group(1))

            # there can be several 'versions'
            # for the same ntuple
            if not self.numVerticesToTuple.has_key(numVertices):
                self.numVerticesToTuple[numVertices] = obj

        #--------------------

        # we assume that all tuples have the same fedids
        # in them
        import utils
        self.fed_ids = utils.getFedIdsFromTuple(self.numVerticesToTuple.values()[0])
        # exclude the special DAQ fed 
        self.fed_ids = [ x for x in self.fed_ids if not x == 1023 ]

    
    #----------------------------------------

    def calculateQuantiles(self, quantile_histo_defs, labels, fedGroups, cutExpr = ""):
        """ calculates the quantiles for the given groups
        of feds.
          """

        assert(len(labels) == len(fedGroups))

        # create the calculated quantiles
        # (we histogram them later as
        # we might produce different ranges
        # of feds)

        # first index is the index of the quantile
        # second index is the fed number
        self.quantile_values = [ {} for i in range(len(quantile_histo_defs)) ]

        #--------------------
        # loop over all feds 
        #--------------------

        for label, fed_ids in zip(labels,fedGroups):

            if not isiterable(fed_ids):
                fed_ids = (fed_ids,)

                
            print "processing feds",label,fed_ids

            this_fed_sizes = []

            this_fed_max_events = max_events_per_fed

            if this_fed_max_events == None:
                # the TTree::Draw limit
                this_fed_max_events = 1000000000

            # exclude those feds which we have not found in
            # the ROOT tuple (in order to avoid error messages
            # from ROOT)
            fed_ids = [ x for x in fed_ids if x in self.fed_ids ]

            if fed_ids:

                # build plot expression
                plotExpr = "+".join([ "size%03d" % fed_id for fed_id in fed_ids ])
                # print "plotExpr=",plotExpr

                sum_num_selected_events = 0

                for numVertices,ntuple in self.numVerticesToTuple.iteritems():

                    # print numVertices,"vertices"

                    # do we have to do this for each iteration ?
                    ntuple.SetEstimate(ntuple.GetEntries())

                    ntuple.Draw(plotExpr, cutExpr, "goff", this_fed_max_events)

                    this_fed_sizes_buf = ntuple.GetV1()

                    num_selected_events = ntuple.GetSelectedRows()

                    sum_num_selected_events += num_selected_events

                    assert(num_selected_events >= 0)

                    # convert to a list
                    this_fed_sizes.extend([ this_fed_sizes_buf[i] for i in xrange(num_selected_events) ])

                    this_fed_max_events = this_fed_max_events - num_selected_events

                    if this_fed_max_events <= 0:
                        break

                # end of loop over all tuples/number of vertices

                print "num_selected_events=",sum_num_selected_events

                this_fed_sizes_sorted = sorted(this_fed_sizes)
            else:
                # no feds selected
                this_fed_sizes_sorted = []

            # calculate the quantiles
            for index, histo_def in enumerate(quantile_histo_defs):

                if this_fed_sizes_sorted:

                    quantile = histo_def['quantile']

                    # as all the feds have the same number of events,
                    # we actually need to calculate these positions
                    # only once...
                    # print "pos_in_array=",pos_in_array

                    # pos_in_array = int(round(quantile * len(this_fed_sizes)))
                    # if pos_in_array < 0:
                    #     pos_in_array = 0
                    # elif pos_in_array >= len(this_fed_sizes):
                    #     pos_in_array = len(this_fed_sizes)-1
                    # 
                    # value = this_fed_sizes_sorted[pos_in_array]

                    value = utils.getQuantile(this_fed_sizes_sorted, quantile)

                else:
                    # no values, set the quantile to zero
                    value = 0

                # print "quantile:",quantile,"pos_in_array",pos_in_array,"value",value

                self.quantile_values[index][label] = value

                # print "Setting",fed_id, value

            # calculate the average, max and min and fill this into the histogram

            # mean_size = sum(this_fed_sizes) / num_selected_events
            # 
            # max_size = max(this_fed_sizes)
            # min_size = min(this_fed_sizes)
            # 
            # # fill the graph
            # point_num = fed_id - min_fedid
            # graph.SetPoint(point_num, fed_id, mean_size)
            # graph.SetPointEYlow(point_num,mean_size - min_size)
            # graph.SetPointEYhigh(point_num,max_size - mean_size)


            # break
        
        


    #----------------------------------------
    def getQuantile(self, label, quantileIndex):

        return self.quantile_values[label][quantileIndex]

    #----------------------------------------


#----------------------------------------------------------------------

def makePlot(quantile_values, fed_ids, min_fedid = None, max_fedid = None, canvasName = None, addRangeArrows = True,
             maximumScaling = None,
             xtitle = None,
             ytitle = None,
             outputFnameSuffix = "",
             ):
    """ make a plot for the case where we look at individual FEDs """
    
    if min_fedid == None:
        min_fedid = min(fed_ids)

    if max_fedid == None:
        max_fedid = max(fed_ids)

    #------------------------------
    # create and fill histograms for the different quantiles
    # one histogram per quantile to plot, these
    # are then superimposed
    #------------------------------
    quantile_histos = []

    for index, quantile_histo_def in enumerate(quantile_histo_defs):

        histo = ROOT.TH1F("quantile_histo_%d" % index,
                          "%.1f%% quantile" % (quantile_histo_def['quantile'] * 100),
                          max_fedid - min_fedid + 1, min_fedid - 0.5, max_fedid + 0.5)

        quantile_histos.append(histo)
        gc_saver.append(histo)

        # fill the histogram

        for fed_id in fed_ids:

            if fed_id < min_fedid or fed_id > max_fedid:
                continue

            value = quantile_values[index][fed_id]

            bin_number = quantile_histos[index].FindBin(fed_id)

            histo.SetBinContent(bin_number, value)

        # end of loop over all feds
        
        #------------------------------
        # udpate the histogram maximum if needed
        #------------------------------
        if maximumScaling != None:
            histo.SetMaximum(histo.GetMaximum() * maximumScaling)

    # end of loop over histograms / quantiles 

    #------------------------------

    # draw the quantile histograms
    is_first = True

    hs = ROOT.THStack("hs","FED sizes")

    # make sure the quantiles are in sorted order:
    # when we plot them we need to draw the lowest
    # quantile numbers last
    quantile_ordered_indices = range(len(quantile_histos))
    quantile_ordered_indices.sort(lambda x,y: cmp(quantile_histo_defs[y]['quantile'],quantile_histo_defs[x]['quantile']))

    legendWidth = 0.1
    legendHeight = 0.1

    # legendX0 = 0.8
    legendY0 = 0.8

    legendX0 = 0.2

    # legend = ROOT.TLegend(0.8,0.8,0.9,0.9)
    legend = ROOT.TLegend(legendX0, legendY0, legendX0 + legendWidth, legendY0 + legendHeight)

    for index in quantile_ordered_indices:

        histo = quantile_histos[index]
        hs.Add(histo)

        legend.AddEntry(histo,histo.GetTitle(),"F")

        histo_def = quantile_histo_defs[index]

        # apply attributes
        for key in histo_def.keys():

            if key == 'quantile':
                continue

            # call things like SetFillColor etc.
            value = histo_def[key]

            getattr(histo,"Set" + key)(value)


    if canvasName != None:
        canv = ROOT.TCanvas(canvasName, canvasName, 1200, 600)
        gc_saver.append(canv)
    hs.Draw("nostack")    
    gc_saver.append(hs)
    legend.Draw()
    gc_saver.append(legend)

    #----------------------------------------
    # make arrows for subdetector fed ranges
    #----------------------------------------

    if addRangeArrows:

        import utils
        for fed_range in utils.getFedRanges(fed_ids,
                                            dict(splitHCAL = True)):

            det_name = fed_range['name']

            det_min_fed = fed_range['start']
            det_max_fed = fed_range['end']

            #--------------------
            # check whether this range actually overlaps
            # with something we were asked to plot
            if det_min_fed > max_fedid:
                continue

            if det_max_fed < min_fedid:
                continue
            #--------------------

            det_mid_fed = (det_max_fed + det_min_fed) / 2.0

            arrow = ROOT.TArrow(det_min_fed-0.5, subdet_range_arrow_ypos,
                                det_max_fed+0.5, subdet_range_arrow_ypos,
                                subdet_range_arrow_size,
                                "<>")
            arrow.SetLineWidth(4)

            arrow.Draw()

            gc_saver.append(arrow)

            # draw a label on the arrow

            fedsThisSubdet = [ x for x in fed_ids if x >= det_min_fed and x <= det_max_fed]
            # print "FEDS for",det_name,":",numFedsThisSubdet

            # check how many feds there are normally for this subdet
            import utils
            expectedFedsThisSubdet = [ x for x in utils.normalFEDlist if x >= det_min_fed and x <= det_max_fed]

            if len(fedsThisSubdet) != len(expectedFedsThisSubdet):
                arrowText = det_name + " (%d/%d)" % (len(fedsThisSubdet), len(expectedFedsThisSubdet))
            else:
                arrowText = det_name + " (%d)" % len(fedsThisSubdet)

            missingFedsThisSubdet = [ x for x in expectedFedsThisSubdet if not x in fedsThisSubdet ]

            if missingFedsThisSubdet:
                print len(missingFedsThisSubdet),"missing feds in",det_name,":",missingFedsThisSubdet

            label = ROOT.TText(det_mid_fed,subdet_range_label_ypos,arrowText)

            # how to center the text ?

            # 10*horizontal + vertical
            # 1 = bottom adjusted
            # 10 = left adjusted
            # 2, 20 = centered
            label.SetTextAlign(12)

            label.SetTextAngle(90)

            label.Draw()
            gc_saver.append(label)

        # loop over fed ranges
    # save the plot

    ROOT.gPad.SetGrid()

    if xtitle != None:
        hs.GetXaxis().SetTitle(xtitle)

    if ytitle != None:
        hs.GetYaxis().SetTitle(ytitle)


    #--------------------
    # add the run number to the plot
    #--------------------
    label = ROOT.TLatex(# 0.89,0.15,
                        0.89, 0.93,
                        "run %d" % parameters.run)
    label.SetNDC(True)
    label.SetTextSize(label.GetTextSize() * 0.5)

    # 10's are horizontal alignment
    # 01's are vertical alignment

    # label.SetTextAlign(31)    # bottom right
    label.SetTextAlign(33)    # top right
    label.Draw()
    gc_saver.append(label)

    #--------------------        


    ROOT.gPad.SaveAs(parameters.plots_output_dir + "/quantiles-%d-%d%s.png" % (min_fedid, max_fedid, outputFnameSuffix))

    return quantile_histos

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------

gc_saver = []

fname = parameters.output_data_dir + "/small-tuples.root"

print "opening ",fname
fin = ROOT.TFile.Open(fname)

mainClass = MainClass(fin)
print len(mainClass.fed_ids), "feds found"

#----------------------------------------
# standard plot
#----------------------------------------
if True:
    mainClass.calculateQuantiles(quantile_histo_defs, mainClass.fed_ids, mainClass.fed_ids)

    # minFed, maxFed = 0,820
    minFed, maxFed = 0,679

    makePlot(mainClass.quantile_values, mainClass.fed_ids, minFed,maxFed,"c1",
             xtitle = "FED number",
             ytitle = "Fragment size [bytes]"
             )

    makePlot(mainClass.quantile_values, mainClass.fed_ids, 680,820,"c2",
             xtitle = "FED number",
             ytitle = "Fragment size [bytes]"
             )

#----------------------------------------
# standard plot for any fed has a large size
#----------------------------------------
if False:
    # for HLT_Physics
    # sizeRequirement = "size_max >= 6000"

    # if hlt_description == "HLT_L1Tech_BSC_minBias_threshold1"
    sizeRequirement = "size_max >= 4000"

    mainClass.calculateQuantiles(quantile_histo_defs, mainClass.fed_ids, mainClass.fed_ids, cutExpr = sizeRequirement)

    # minFed, maxFed = 0,820
    minFed, maxFed = 0,679

    makePlot(mainClass.quantile_values, mainClass.fed_ids,minFed, maxFed ,"c1",
             xtitle = "FED number",
             ytitle = "Fragment size [bytes]",
             outputFnameSuffix = "-large-feds",
             )

    makePlot(mainClass.quantile_values, mainClass.fed_ids, 680,820,"c2",
             xtitle = "FED number",
             ytitle = "Fragment size [bytes]",
             outputFnameSuffix = "-large-feds",
             )



#----------------------------------------
# per fedbuilder plots
#----------------------------------------
if False:
    # build the groups of feds associated to fedbuilders

    sort_by_decreasing_median_size = True

    import FedBuilderData

    labels = range(len(FedBuilderData.fedBuilderGroups))

    mainClass.calculateQuantiles(quantile_histo_defs,
                                 labels,
                                 [ x['feds'] for x in FedBuilderData.fedBuilderGroups ]
                                 )

    #--------------------
    if sort_by_decreasing_median_size:
        # sort (and relabel) by decreasing value of median fedbuilder size
        sortedLabels = labels[:]

        medianIndex = [ i for i in range(len(quantile_histo_defs)) if quantile_histo_defs[i]['quantile'] == 0.5]

        assert(len(medianIndex) == 1)
        medianIndex = medianIndex[0]

        sortedLabels.sort(lambda y,x: cmp(mainClass.quantile_values[medianIndex][x],
                                          mainClass.quantile_values[medianIndex][y]))
        # reoder the quantile values
        new_quantile_values = []
        for qv in mainClass.quantile_values:
            tmp = [ qv[sortedLabels[i]] for i in range(len(qv)) ]
            new_quantile_values.append(tmp)

    else:
        # no sorting
        sortedLabels = labels[:]
        new_quantile_values = mainClass.quantile_values[:]

    #--------------------

    # note that we use labels here on purpose
    makePlot(new_quantile_values, labels,canvasName = "c1", addRangeArrows = False, maximumScaling = 1.5,
             xtitle = "fedbuilder #",
             ytitle = "sum of fragment sizes [bytes]",
             )

    # print how many subsystems are represented in each fedbuilder
    for xpos, label in enumerate(sortedLabels):

        fedGroup = FedBuilderData.fedBuilderGroups[label]['feds']
        fedGroup = [ x for x in fedGroup if x in mainClass.fed_ids ]

        #--------------------
        # label: number of feds of which subsystem
        if False:
            subsysCounts = {}
            for fed in fedGroup:
                subsys = utils.getSubsystemFromFed(fed)
                subsysCounts[subsys] = subsysCounts.get(subsys, 0) + 1

            subsystems = subsysCounts.keys()

            subsystems.sort(lambda y,x: cmp(subsysCounts[x], subsysCounts[y]))

            counts = [ subsysCounts[x] for x in subsystems ]

            text = ", ".join( [ "%d*%s" % (x,y) for x,y in zip(counts,subsystems) ])

        if True:
            text = "%s (%s)" % (FedBuilderData.fedBuilderGroups[label]['name'], FedBuilderData.fedBuilderGroups[label]['frlpc'])

        #--------------------

        print label,":", text

        ypos = 30000

        rootLabel = ROOT.TText(xpos,ypos,text)

        rootLabel.SetTextAlign(12)
        rootLabel.SetTextAngle(90)

        rootLabel.SetTextSize(rootLabel.GetTextSize() * 0.4)
        rootLabel.Draw()

        gc_saver.append(rootLabel)

    # loop over fedbuilders

    #--------------------
    # run data set and trigger path label
    #--------------------

    text = "run %d, %s, %s" % (run, dataset, hlt_description)

    rootLabel = ROOT.TText(0.2,0.9,text)
    rootLabel.SetNDC(1)

    rootLabel.Draw()

    gc_saver.append(rootLabel)

    ROOT.gPad.SaveAs(parameters.plots_output_dir + "/quantiles-0-68.png")
