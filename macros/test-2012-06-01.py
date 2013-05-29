#!/usr/bin/env python

import ROOT, re
gcSaver = []

#----------------------------------------------------------------------

fname = "data/zerobias-194912/HLT_Physics/small-tuples.root"

feds = [ 615 ]

#----------------------------------------------------------------------

fedToSizes = {}

#----------------------------------------------------------------------
def scaleRange(minval, maxval, scale = 1.1):

    halfDiff = (maxval - minval) * 0.5

    halfDiff *= scale

    mid = (maxval + minval) * 0.5

    return mid - halfDiff, mid + halfDiff

#----------------------------------------------------------------------

fin = ROOT.TFile(fname)



tupler = fin.Get("tupler")

for key in tupler.GetListOfKeys():

    name = key.GetName()

    mo = re.match("all_sizes_(\d+)vtx$",name)

    if not mo:
        continue

    tree = tupler.Get(name)

    for fed in feds:
        tree.Draw("size%03d" % fed,"","goff")
        numEvents = tree.GetSelectedRows()

        values = tree.GetV1()

        values = [ values[i] for i in range(numEvents) ]

        fedToSizes.setdefault(fed,[]).extend(values)

    # end of loop over feds

# plot the distributions

for fed in feds:
    values = fedToSizes[fed]
    
    minVal, maxVal = scaleRange(min(values), max(values))

    nbins = 50

    histo = ROOT.TH1F("histo_fed%03d" % fed, "fed%03d" % fed,
                      nbins, minVal, maxVal)
    gcSaver.append(histo)

    for value in values:
        histo.Fill(value)

    histo.Draw()

    # func = ROOT.TF1("func","exp([0]+[1]*x)",minVal, maxVal)
    # func.SetParameter(0,1)
    # func.SetParameter(1,-5)

    # histo.Fit(func,"","",2000,4000)

    func = ROOT.TF1("func","[1]/[0]*exp(-x/[0])",0, maxVal)

    binWidth = (maxVal - minVal)/float(nbins)

    # set mean
    func.SetParameter(0,2000)
    func.SetParName(0,"mean")
    func.SetParName(1,"normalization")

    func.SetParameter(1,len(values) * binWidth)
    histo.GetListOfFunctions().Add(func)

    histo.Draw("HF")

    ROOT.gPad.SetLogy()


