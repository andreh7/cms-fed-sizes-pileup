#!/usr/bin/env python

# tool to plot the per bunch crossing luminosity
# (to get an idea how to select the binning by eye)

import sys, os

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
ARGV = sys.argv[1:]

assert(len(ARGV) == 1)

fname = ARGV[0]

import ROOT
fin = ROOT.TFile.Open(fname)

fin.Get("tupler/small_tuple").Draw("per_bx_lumi")

