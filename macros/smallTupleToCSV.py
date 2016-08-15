#!/usr/bin/env python

# tool to export the per event and FED sizes to a csv file
# (which then can e.g. be read from R)

import sys, re

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------

ARGV = sys.argv[1:]

assert len(ARGV) == 1, "must specify exactly one input file"

import ROOT

fin = ROOT.TFile(ARGV[0])
assert fin.IsOpen()

# find the number of vertices

theDir = fin.Get("tupler")
assert theDir != None


#----------
# get number of vertices
#----------

allNumVertices = []

for key in theDir.GetListOfKeys():

    key = key.GetName()

    mo = re.match("all_sizes_(\d+)vtx$", key)

    if not mo:
        continue

    allNumVertices.append(int(mo.group(1)))

if not allNumVertices:
    print >> sys.stderr,"no suitable input trees found"
    sys.exit(1)

#----------
# get list of FEDs
#----------

allFedNumbers = None

treeName = "all_sizes_%dvtx" % allNumVertices[0]
tree = theDir.Get(treeName)
assert tree != None, "could not find tree '%s'" % treeName

# TODO: there is no luminosity section number
branchNames = [ "bx" ]
outputNames = [ "num_vertices", "bx" ]

for branch in tree.GetListOfBranches():

    branchName = branch.GetName()

    mo = re.match("size(\d+)$", branchName)

    if mo:
        fedId = int(mo.group(1), 10)

        branchNames.append(branchName)
        outputNames.append("fed%04d" % fedId)

#----------
# set branch addresses
#----------
# see https://root.cern.ch/phpBB3/viewtopic.php?t=10962

structDef = [ "struct inputStruct {" ]

for branchName in branchNames:
    # all branches are Float_t
    structDef.append("Float_t " + branchName + ";")

structDef += [ "}" ]

ROOT.gROOT.ProcessLine("".join([ x + "\n" for x in structDef]))


#----------
# print header
#----------
print ",".join(outputNames)

#----------
# read the data from the ROOT file and write it out to CSV
#----------

for index, numVertices in enumerate(sorted(allNumVertices)):

    print >> sys.stderr, "processing tree %d/%d" % (index + 1, len(allNumVertices))

    tree = theDir.Get("all_sizes_%dvtx" % numVertices)
    assert tree != None

    # inputBuf = ROOT.inputStruct()
    # for branchName in branchNames:
    #     tree.SetBranchAddress(branchName, AddressOf(inputBuf, branchName))


    print >> sys.stderr,tree.GetEntries(),"entries"
    for i in range(tree.GetEntries()):

        tree.GetEntry(i)

        outputValues = [ numVertices ] + [ int(getattr(tree, branchName)) for branchName in branchNames ]

        print ",".join([ str(x) for x in outputValues ])
        



