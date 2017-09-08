#!/usr/bin/env python

# given a plot output directory, produces a CSV file
# with the quantiles of the distributions per subsystem analyzed

import sys, os

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
if __name__ == "__main__":


    ARGV = sys.argv[1:]

    assert len(ARGV) == 1

    tasksFile = ARGV.pop(0)

    import pickle

    tasks = pickle.load(open(tasksFile))['tasks']

    plotDir = os.path.dirname(tasksFile)
    outputFname = os.path.join(plotDir, "distributions.csv")

    fout = open(outputFname, "w")

    #----------
    from FedSizePerVertexLinearFit import FedSizePerVertexLinearFit

    isFirst = True
    for task in tasks:
        if not isinstance(task, FedSizePerVertexLinearFit):
            continue

        task.writeQuantilesCSV(fout, isFirst)
        isFirst = False

    fout.close()
    print >> sys.stderr,"wrote report to", outputFname

