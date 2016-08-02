#!/usr/bin/env python

import sys, os, commands, re, pprint

# tool to make a list of files for the given raw and reco datasets
# using dascli
#
# compared to what was done in Run1, we do NOT group by lumisection
# anymore here (seems to need more queries with DAS than it did with DBS)


#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
from optparse import OptionParser
parser = OptionParser("""

  usage: %prog [options] rawdataset recodataset

  runs dascli to get the logical files of the given RAW and RECO datasets
  
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
# check presence of dascli
#----------

if os.system("which dascli >/dev/null 2>&1") != 0:
    print >> sys.stderr,"can't find 'dascli' command, exiting"
    sys.exit(1)

#----------------------------------------

import operator

# maps from 'raw'/'reco' to list of files in this dataset (and run)
output_data = {}

assert len(ARGV) == 2
for dstier, dataset in (
    ('raw', ARGV[0]),
    ('reco', ARGV[1])):

    query = "file dataset=%s" % dataset + " " + run_spec

    cmd = "dascli --limit 0 --query '" + query + "'"
    print >> sys.stderr, "executing",cmd
    lines = commands.getoutput(cmd).splitlines()

    output_data[dstier] = lines

# end loop over datasets

print "# output of "
print "# " + " ".join(sys.argv)
print "#"
print "files_list =",
pprint.pprint(output_data)
