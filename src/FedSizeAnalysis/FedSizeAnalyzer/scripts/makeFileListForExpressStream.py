#!/usr/bin/env python

import sys, commands

#
# creates a file list for an express stream castor directory
#

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
ARGV = sys.argv[1:]
assert(len(ARGV) == 1)

dirname = ARGV[0]

storePrefix = "/castor/cern.ch/cms"

if not dirname.startswith(storePrefix + "/store/"):
    print >> sys.stderr,"the given directory must start with",storePrefix + "/store/"
    sys.exit(1)

dirname = dirname[len(storePrefix):]

# list all files in this directory
cmd = "nsls " + storePrefix + dirname
status,output = commands.getstatusoutput(cmd)
if status != 0:
    print >> sys.stderr,"failed to run " + cmd
    sys.exit(1)


files = [ dirname + "/" + x for x in output.splitlines() ]

# print files


#
# note that the start and end lumisection are used for testing for
# overlap with the overall given range of lumi sections (in ../fedsizeanalyzer_cfg.py)
#
# as we have seen an example of files appearing in the express stream but
# not appearing in DBS, we just set the start and end lumi section
# such that the files should always be included

output_data = []

for fname in files:
    output_data.append(dict(
        start_ls = 0,
        end_ls = 99999,
        files = [
            # the first file in the list is the RAW file, the second is the RECO file
            # in this case (FEVT event content) they're both the same...
            fname,
            fname
            ]
        )
       )
    
print "# output of"
print "# " + " ".join(sys.argv[1:])
print "files_list =",

import pprint
pprint.pprint(output_data)
