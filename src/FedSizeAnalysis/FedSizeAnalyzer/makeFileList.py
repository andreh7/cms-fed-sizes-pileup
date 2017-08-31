#!/usr/bin/env python

import sys, os, commands, re, pprint, time

# tool to make a list of files for the given raw and reco datasets
# using das_client
#
# compared to what was done in Run1, we do NOT group by lumisection
# anymore here (seems to need more queries with DAS than it did with DBS)

#----------------------------------------------------------------------

def findFiles(rawDataSet, recoDataSet, run, logStream = sys.stderr):
    # @param rawDataSet and recoDataSet are lists of dataset names
    # @param run can be None

    if run:
        # a run was specified
        run_spec = "run=" + str(run)
    else:
        # no runs were specified
        run_spec = ""

    #----------

    # maps from 'raw'/'reco' to list of files in this dataset (and run)
    output_data = {}

    for dstier, datasetList in (
        ('raw', rawDataSet),
        ('reco', recoDataSet)):

        for dataset in datasetList:

            query = "file dataset=%s" % dataset + " " + run_spec

            cmd = "das_client --limit 0 --query '" + query + "'"
            if logStream != None:
                print >> logStream, "executing",cmd

            status = 1

            for retry in range(3):
                status, lines = commands.getstatusoutput(cmd)
                lines = lines.splitlines()
                if status == 0:
                    break

                # sometimes we get a good result when just retrying
                # (different backend server ?)
                time.sleep(10)
                if logStream != None:
                    print >> logStream,"retrying"

            if status != 0:
                print >> sys.stderr,"failed to run das_client multiple times"
                sys.exit(1)

            output_data.setdefault(dstier,[]).extend(lines)

    # end loop over datasets
    return output_data

#----------------------------------------------------------------------

def ensureDasClientExists():
    if os.system("which das_client >/dev/null 2>&1") != 0:
        print >> sys.stderr,"can't find 'das_client' command, exiting"
        sys.exit(1)

#----------------------------------------------------------------------

def printData(output_data, outputFname = None):
    
    if outputFname == None:
        out = sys.stdout
    else:
        out = open(outputFname, "w")

    print >> out, "# output of "
    print >> out, "# " + " ".join(sys.argv)
    print >> out, "#"
    print >> out, "files_list =",
    pprint.pprint(output_data, stream = out)

    if outputFname != None:
        out.close()

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
if __name__ == '__main__':

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

    #----------------------------------------

    #----------
    # check presence of das_client
    #----------

    ensureDasClientExists()

    #----------------------------------------

    assert len(ARGV) == 2
    rawDataSet, recoDataSet = [ item.split(',') for item in ARGV ]
    output_data = findFiles(options.run, rawDataSet, recoDataset)

    printData(output_data)
