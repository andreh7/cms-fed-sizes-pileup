#!/usr/bin/env python

import ROOT
import sys
from DataFormats.FWLite import Events, Handle

import glob, array, pprint


import utils
#----------------------------------------------------------------------
execfile("parameters.py")

max_num_events = None        # take all events
# max_num_events = 1000

#----------------------------------------------------------------------
files = glob.glob(input_data_dir + "/*.root")

if len(files) == 0:
    print >> sys.stderr,"no ROOT files found in directory " + input_data_dir
    sys.exit(1)

events = Events (files)
handle  = Handle ("FedSizeAnalysisData")

i = 0

fedids = None



# make one output file per number of vertices

# maps from number of vertices to output file
fout = {}

# maps from number of vertices to output tuple
output_tuple = {}

for num_vertices in range(max_num_vertices+1):
    fout[num_vertices] = ROOT.TFile(output_data_dir + "/all-sizes-%dvtx.root" % num_vertices, "RECREATE")

import time

total_num_events = events.size()

start_time = time.time()

max_num_vertices_seen = 0

# loop over events
for event in events:
        
    event.getByLabel (("fedSizeData"), handle)
    # get the product
    fedsizedata = handle.product()

    num_vertices = fedsizedata.getNumPrimaryVertices()

    max_num_vertices_seen = max(num_vertices, max_num_vertices_seen)

    if fedids == None:
        # get the list of FEDs in this run from the first event
        fedids = fedsizedata.getFedIds()

        # convert to a python list
        fedids = [ x for x in fedids ]

        # create the output ntuple
        # fout[num_vertices].cd()

        varnames = ['num_vertices'] + [ "size%03d" % fed for fed in fedids ]

        #--------------------
        # add per subdetector sums
        #--------------------
        fed_ranges = utils.getFedRanges(fedids)

        for item in fed_ranges:
            item['name'] = item['name'].lower()
            varnames.append("size_" + item['name'])

        # pprint.pprint(fed_ranges)


        #--------------------
        # add total size of event
        # (sum of all FEDs)
        #--------------------

        varnames.append("size_total")

        #--------------------
        # create one tuple per output file
        #--------------------
        for nv in range(max_num_vertices+1):        
            # does this actually work to declare the same
            # output tuple in different files at the same time ???

            fout[nv].cd()
            output_tuple[nv] = ROOT.TNtuple("all_sizes","all_sizes",
                                        ":".join(varnames))
        #--------------------

    #--------------------

    # get the sizes of all FEDs in the current event
    sizes = [ fedsizedata.getFedSize(fed) for fed in fedids ]

    values = [ num_vertices ] + \
             sizes

    assert(len(sizes) == len(fedids))
    all_fed_sizes_sum = sum(sizes)

    #--------------------
    # calculate per-subsystem fed sums
    #--------------------

    # fed_to_size = dict(zip(fedids, sizes))

    # there are more efficient ways of doing this
    # (rather than looping several times
    # over the list of all FEDs)
    # but this should work

    for item in fed_ranges:

        min_fedid = item['start']
        max_fedid = item['end']

        this_subdet_sum = sum([ the_size for the_size, the_fedid in zip(sizes,fedids)
                                if the_fedid >= min_fedid and the_fedid <= max_fedid ])

        values.append(this_subdet_sum)

    #--------------------
    # calculate the total size
    #--------------------

    values.append(all_fed_sizes_sum)

    #--------------------
    # fill the output tuple
    # apply(output_tuple.Fill, map(float, sizes))

    # note that we can check that the order of
    # filling was correct by checking fed 1023
    # which should always have a size of 112 

    assert(len(values) == len(varnames))

    fout[min(num_vertices, max_num_vertices)].cd()  # just to be safe...
    output_tuple[min(num_vertices, max_num_vertices)].Fill(array.array('f',values))

    #--------------------
    # print a status report
    #--------------------
    if i > 0 and i % 10000 == 0:
        # print i,"size=",fedsizedata.getFedSize(1023)

        now = time.time()

        delta_t = now - start_time

        time_per_event = delta_t / float(i)

        remaining_events = total_num_events - i

        print "processed %d events (out of %d), estimated remaining time: %.1f minutes" % (
            i,
            total_num_events,
            remaining_events * time_per_event / 60.0)

    # prepare next iteration
    i += 1

    if max_num_events != None and i >= max_num_events:
        break
    

for nv in range(max_num_vertices+1):
    fout[nv].cd()
    output_tuple[nv].Write()
    fout[nv].Close()

print "tuples were written to",output_data_dir
print "maximum number of vertices seen is",max_num_vertices_seen,
if max_num_vertices_seen > max_num_vertices:
    print "WHICH IS LARGER THAN max_num_vertices (%d), SHOULD BE UPDATED IN parameters.py" % max_num_vertices,

print 
