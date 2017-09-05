#!/usr/bin/env python

import os, sys

class FedSizeMatrix:
    # class to hold the individual fed sizes accessible by fed id and 
    # number of vertices or pileup in memory
    # 
    # replaces openSizePerFedNtuples(..) in utils.py ?

    def __init__(self):

        # 13 TeV total cross section (in microbarn) recommended by Lumi experts
        # to get pileup
        self.totalXsect = 80000.
        # orbit frequency (from Lumi expert)
        self.orbitFreq = 11245.6

        # conversion factor to multiply the per bx instantaneous
        # luminosities (in Hz per microbarn) with to get
        # the (average) number of interactions per bunch crossing
        # (pileup)
        self.lumiToPuFactor = self.totalXsect / self.orbitFreq

    #----------------------------------------
    
    def read(self, fname, maxNumVertices, allFedIds, cut = ""):

        # reads data from a small tuples file where we have one ntuple
        # per number of vertices

        if not os.path.exists(fname):
            raise Exception("file " + fname + " does not exist")

        # first index is number of vertices
        # second index is fedid
        # value is a numpy array of fragment sizes in the run
        # 
        # this allows to easily add several fedids to form groups
        # for a fixed number of vertices

        self.data = {}

        import ROOT

        import numpy as np

        fin = ROOT.TFile.Open(fname)

        for nv in range(maxNumVertices+1):
            ntuple = fin.Get("tupler/all_sizes_%dvtx" % nv)

            if ntuple == None:
                continue

            # index is fedid
            thisVtxData = {}
            self.data[nv] = thisVtxData

            # number of events with this number of reconstructed vertices

            nevents = ntuple.GetEntries()
            ntuple.SetEstimate(nevents)

            nentries = None

            print >> sys.stderr,"reading",nv,"vertices"

            for fedId in allFedIds:
                ntuple.Draw("size%03d" % fedId, cut, "goff")
                
                # note that we may have less than nevents rows
                # selected due to the cut
                
                if nentries == None:
                    nentries = ntuple.GetSelectedRows()
                else:
                    assert nentries == ntuple.GetSelectedRows()

                data = ntuple.GetV1()

                vec = np.zeros(nentries, dtype = 'int32')

                for i in range(nentries):
                    vec[i] = data[i]

                thisVtxData[fedId] = vec
            # end of loop over fedIds

        # end of loop over number of vertices

        fin.Close()
        ROOT.gROOT.cd()

    #----------------------------------------

    def getFedSums(self, numVertices, fedIds):
        # @return a vector with the sum of the fragment sizes
        #         of the given fedIds for each event
        #         for the events with numVertices vertices

        retval = None
        
        for fedId in fedIds:
            if retval == None:
                retval = self.data[numVertices][fedId]
            else:
                # note: do NOT use +=
                retval = retval + self.data[numVertices][fedId]
    
        return retval

    #----------------------------------------

    def setFixedFedSize(self, fedId, size):
        # sets the size of the given fed to the given size
        # for all number of vertices and all events
        #
        # this can be used to fix certain FEDs whose
        # size is much larger in the RAW data files
        # than it is online
        for numVertices, tmp in self.data.items():
            tmp[fedId][:] = size

    #----------------------------------------

#----------------------------------------------------------------------

# test 
if __name__ == '__main__':
    
    fedIds = eval(open("../src/FedSizeAnalysis/FedSizeAnalyzer/data/fedids-282092.txt").read())

    maxNumVertices = eval(open("../src/FedSizeAnalysis/FedSizeAnalyzer/data/max-num-vertices-282092.txt").read())

    matrix = FedSizeMatrix()


    import time
    start = time.time()
    matrix.read("../data/hltphysics-282092/small-tuples.root", maxNumVertices,fedIds)

    print "read data in %.1f" % ((time.time() - start) / 60.0),"minutes"
