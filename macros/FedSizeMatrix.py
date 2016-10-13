#!/usr/bin/env python

import os, sys

class FedSizeMatrix:
    # class to hold the individual fed sizes accessible by fed id and 
    # number of vertices in memory
    # 
    # replaces openSizePerFedNtuples(..) in utils.py ?

    #----------------------------------------
    
    def read(self, fname, maxNumVertices, allFedIds):

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

            print >> sys.stderr,"reading",nv,"vertices"

            for fedId in allFedIds:
                ntuple.Draw("size%03d" % fedId,"","goff")
                
                # this should actually be equal to nevents
                # nentries = ntuple.GetSelectedRows()
                data = ntuple.GetV1()

                vec = np.zeros(nevents, dtype = 'int32')

                for i in range(nevents):
                    vec[i] = data[i]

                thisVtxData[fedId] = vec
            # end of loop over fedIds

        # end of loop over number of vertices

        ROOT.gROOT.cd()

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
