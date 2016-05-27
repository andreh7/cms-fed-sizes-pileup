#!/usr/bin/env python

import utils
import os

class SmallTuple:
    """ keeps information obtained from the small tuple file """
    
    #----------------------------------------

    def __init__(self, parameters):
        
        # open the file and keep a pointer to the tree

        # the file name of the file
        # containing the cached data
        fname = parameters.input_data_dir + "/small-tuples.root"

        # try to find it on disk 

        biggest_time = None

        # also check whether this is newer than all
        # of the original ntuples
        if os.path.exists(fname) and \
           os.path.getmtime(fname) >= utils.newestFileDate(parameters.input_data_dir + "/*.root"):

            self.__loadSmallTuple(fname)
        else:
            raise Exception("small tuple " + fname + " is out of date (files in " + parameters.input_data_dir + " seem newer) or not existing, need to rerun cmsRun")

    #----------------------------------------

    def __loadSmallTuple(self, fname):

        import ROOT

        # keep a reference to the input file
        self.fin = ROOT.TFile.Open(fname)

        assert self.fin.IsOpen(), "failed to open small tuple file " + fname

        smallTupleName = "tupler/small_tuple"

        small_tuple = self.fin.Get(smallTupleName)

        assert small_tuple != None, "could not get " + smallTupleName + " in file " + fname

        # maybe this magically prevents crashes ?
        ROOT.gROOT.cd()

        self.tree = small_tuple

    #----------------------------------------

    def getAllLumiSections(self):
        """ returns a list of all luminosity sections found """

        self.tree.SetEstimate(self.tree.GetEntries())
        self.tree.Draw("lumisection","","goff")

        num_entries = self.tree.GetSelectedRows()
        data = self.tree.GetV1()

        lumi_sections = set([ data[i] for i in xrange(num_entries) ])

        return lumi_sections

    #----------------------------------------
