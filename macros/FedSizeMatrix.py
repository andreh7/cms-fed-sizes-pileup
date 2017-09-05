#!/usr/bin/env python

import os, sys
import numpy as np

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

        # similar to self.data but vs. pileup instead of number
        # of vertices:
        # 
        # first index is number of pileup events (rounded)
        # second index is fedid
        # value is a numpy array of fragment sizes in the run
        #   (while filling the data structure, value is a list to append to)
        self.dataPerPu = {}

        import ROOT

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
            
            #----------
            # get the per BX luminosities (assuming the order
            # of the entries is the same as in the following per FEDid
            # scans)
            #----------
            
            ntuple.Draw("per_bx_lumi", cut, "goff")

            nentries = ntuple.GetSelectedRows()
            data = ntuple.GetV1()
            
            thisPuValues = np.zeros(nentries, dtype = 'float32')
            for i in range(nentries):
                thisPuValues[i] = data[i]

            # convert from luminosity to number 
            # of pileup events and round to nearest integer
            thisPuValues = (thisPuValues * self.lumiToPuFactor + 0.5).astype('int32')

            #----------

            for fedId in allFedIds:
                ntuple.Draw("size%03d" % fedId, cut, "goff")
                
                # note that we may have less than nevents rows
                # selected due to the cut
                assert nentries == ntuple.GetSelectedRows()

                data = ntuple.GetV1()

                vec = np.zeros(nentries, dtype = 'int32')

                for i in range(nentries):
                    vec[i] = data[i]

                    # also distribute to per PU data
                    pu = thisPuValues[i]
                    self.dataPerPu.setdefault(pu, {}).setdefault(fedId,[]).append(data[i])

                thisVtxData[fedId] = vec
            # end of loop over fedIds

        # end of loop over number of vertices

        # convert per PU data from list to numpy arrays
        for tmp in self.dataPerPu.values():
            for fedId, fedSizes in tmp.items():
                tmp[fedId] = np.array(fedSizes, dtype = 'int32')


        fin.Close()
        ROOT.gROOT.cd()

    #----------------------------------------

    def getFedSums(self, xvalue, fedIds, usePu):
        # @return a vector with the sum of the fragment sizes
        #         of the given fedIds for each event
        #         for the events with xvalue vertices or 
        #         xvalue average interactions per BX
        #
        # @param usePu if True interprets xvalue as average number of
        #         interactions per BX (pileup) (must be an integer),
        #         if usePu is False, interprets xvalue as 
        #         number of reconstructed vertices

        retval = None
        
        if usePu:
            thisData = self.dataPerPu
        else:
            thisData = self.data

        if not thisData.has_key(xvalue):
            # no data for this xvalue, happens when we choose the
            # plotting range to wide (e.g. for usePu = True)
            return np.array([])

        thisData = thisData[xvalue]


        for fedId in fedIds:
            if retval == None:
                retval = thisData[fedId]
            else:
                # note: do NOT use +=
                retval = retval + thisData[fedId]
    
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

        for tmp in self.dataPerPu.values():
            tmp[fedID][:] = size

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
