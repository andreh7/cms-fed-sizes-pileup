#!/usr/bin/env python

import sys, os, commands, re, pprint

# unfortunately, I don't see a way of making dbsql NOT print a header,
# so we need some glue code here...

#----------------------------------------------------------------------

def makeRanges(values):

    assert(len(values) > 0)

    values = sorted(values)

    startValue = values[0]
    lastValue = values[0]

    retval = []

    for i in range(1, len(values)):
        if values[i] == lastValue + 1:
            lastValue += 1
            continue

        retval.append((startValue, lastValue))

        startValue = values[i]
        lastValue = values[i]


    retval.append((startValue, lastValue))

    return retval


#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
from optparse import OptionParser
parser = OptionParser("""

  usage: %prog [options] rawdataset1[,rawdataset1b,...] recodataset2[,recodataset2b,...]

  runs dbsql to get the logical files of the given dataset(s) and combines
  them by lumi sections 
  
"""
)

# parser.add_option("--prefix",
#                   dest="prefix",
#                   default="",
#                   type="str",
#                   help="prefix each file with the given string. Useful for e.g. producing command line options to be used with another program",
#                   metavar="PREFIX")

parser.add_option("--run",
                  dest="runs",
                  default=[],
                  type="int",
                  action="append",
                  help="restrict the query to the given run. Note that this option can be specified ",
                  metavar="RUN")

(options, ARGV) = parser.parse_args()

if len(ARGV) != 2:
    parser.print_help()
    sys.exit(1)


if len(options.runs) != 1:
    print >> sys.stderr, "currently, you must specify exactly one run. Other cases are currently"
    print >> sys.stderr, "not supported"
    sys.exit(1)

if options.runs:

    # some runs were specified
    run_spec = " and " + \
               "( " + \
               " or ".join([ "run = " + str(run) for run in options.runs]) + \
               " )"
else:
    # no runs were specified
    run_spec = ""


# print "run_spec=",run_spec

lumisection_to_file = []

all_lumi_sections_seen = set()

import operator
# allDataSets = reduce(operator.add,[ datasetSpec.split(',') for datasetSpec in ARGV: ])

for index,datasetSpec in enumerate(ARGV):

    # make sure we have at least one file
    # from each group 
    for dataset in datasetSpec.split(','):

        query = "find file, lumi where dataset = %s" % dataset + run_spec

        print >> sys.stderr, "query=",query
        lines = commands.getoutput("dbsql '" + query + "'").splitlines()

        lumisection_to_file.append({})

        thisDataSetLumiSections = set()

        for line in lines:

            # seems not to behave the same way as when run interactively...
            # if not line.startswith(" "):
            #     continue

            line = line.lstrip()

            # print "line=",line

            # assume all files start with /store..
            if not line.startswith("/store/"):
                continue

            fname, lumisection = re.split('\s+',line)
            lumisection = int(lumisection)
            thisDataSetLumiSections.add(lumisection)

            # file_to_lumisection.setdefault(file, set()).add(lumisection)

            # this potentially takes quite some memory but
            # should be affordable for the moment
            lumisection_to_file[index].setdefault(lumisection,[]).append(fname)

            # print >> sys.stderr,"index=",index,"fname=",fname

            all_lumi_sections_seen.add(lumisection)

            # print file, lumisection

        if thisDataSetLumiSections:
            print >> sys.stderr, "found",len(thisDataSetLumiSections),"lumi sections (%d..%d)" % (min(thisDataSetLumiSections),max(thisDataSetLumiSections))
        else:
            print >> sys.stderr, "found NO lumisections"

    # end loop over datasets

# end loop over dataset groups

#--------------------
# flatten the list of files
# for theList in lumisection_to_file:
#     for key in theList.keys():
#         theList[key] = ",".join(theList[key])


# pprint.pprint(lumisection_to_file)
# sys.exit(1)

#--------------------

# now combine datasets: make a list of lumisection to pairs/tuples of files

ls_to_files = {}

new_all_lumi_sections_seen = []
for ls in all_lumi_sections_seen:
    # do not take lumisections for which at least one of the datasets
    # does not have a file for this lumisection

    all_datasets_found = True

    the_files = []

    for di in range(len(ARGV)):
        if not lumisection_to_file[di].has_key(ls):
            all_datasets_found = False
            break

        the_files.append(lumisection_to_file[di][ls])

    if not all_datasets_found:
        continue

    ls_to_files[ls] = the_files 
    new_all_lumi_sections_seen.append(ls) 

all_lumi_sections_seen = new_all_lumi_sections_seen

# merge ranges of lumisections pointing the same pairs of files

# print >> sys.stderr, "ls_to_files=",ls_to_files
pprint.pprint(ls_to_files, stream = sys.stderr)

start_ls = None
previous_ls = None

previous_files = None

output_data = []

for ls in sorted(all_lumi_sections_seen):

    this_files = ls_to_files[ls]

    if this_files == previous_files:

        # we still have the same files for this lumi section
        # (as the previous one), check whether we just continue
        # a range or whether we start a new one

        if start_ls == None:
            # we're just starting a range
            start_ls = previous_ls
        else:
            # we're continuing a range. Don't do anything here
            pass

    else:
        # not continuing a range
        # check whether we should flush the previous one

        if start_ls != None:
            output_data.append({
                "start_ls":start_ls,
                "end_ls": previous_ls,
                "files": previous_files,
                })

        # we could be starting a new range here    
        start_ls = ls

    # prepare for next iteration
    previous_ls = ls
    previous_files = this_files

if start_ls != None:
    output_data.append({
        "start_ls":start_ls,
        "end_ls": previous_ls,
        "files": previous_files,
        })


print "# output of "
print "# " + " ".join(sys.argv)
print "#"
print "# lumi sections:",", ".join("%d-%d" % x for x in makeRanges(all_lumi_sections_seen))
print "#"
print "files_list =",
pprint.pprint(output_data)
