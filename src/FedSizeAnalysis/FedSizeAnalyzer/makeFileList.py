#!/usr/bin/env python

import sys, os, commands, re, pprint

# tool to make a list of files for the given raw and reco datasets
# using das_client
#
# compared to what was done in Run1, we do NOT group by lumisection
# anymore here (seems to need more queries with DAS than it did with DBS)


#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
from optparse import OptionParser
parser = OptionParser("""

  usage: %prog [options] rawdataset[,rawdataset2...] recodataset[,recodataset2...]

  runs das_client to get the logical files of the given RAW and RECO datasets
  
"""
)

parser.add_option("--run",
                  dest="run",
                  default=None,
                  type="int",
                  help="restrict the query to the given run",
                  metavar="RUN")

(options, ARGV) = parser.parse_args()

if len(ARGV) != 2:
    parser.print_help()
    sys.exit(1)

if options.run:

    # a run was specified
    run_spec = "run=" + str(options.run)
else:
    # no runs were specified
    run_spec = ""

#----------------------------------------

#----------
# check presence of das_client
#----------

if os.system("which das_client >/dev/null 2>&1") != 0:
    print >> sys.stderr,"can't find 'das_client' command, exiting"
    sys.exit(1)

#----------------------------------------

import operator

# maps from 'raw'/'reco' to list of files in this dataset (and run)
output_data = {}

assert len(ARGV) == 2
for dstier, datasetSpec in (
    ('raw', ARGV[0]),
    ('reco', ARGV[1])):

    for dataset in datasetSpec.split(','):

        query = "file dataset=%s" % dataset + " " + run_spec

        cmd = "das_client --limit 0 --query '" + query + "'"
        print >> sys.stderr, "executing",cmd

        status = 1

        for retry in range(3):
            status, lines = commands.getstatusoutput(cmd)
            lines = lines.splitlines()
            if status == 0:
                break

            # sometimes we get a good result when just retrying
            # (different backend server ?)
            time.sleep(10)
            print >> sys.stderr,"retrying"

        if status != 0:
            print >> sys.stderr,"failed to run das_client multiple times"
            sys.exit(1)

        output_data.setdefault(dstier,[]).extend(lines)

# end loop over datasets

print "# output of "
print "# " + " ".join(sys.argv)
print "#"
print "files_list =",
pprint.pprint(output_data)
