#!/usr/bin/env python

# given a plot output directory, produces python code
# with the evolution data

import sys, os


#----------------------------------------------------------------------

def writePythonData(fout, task):

    print >> fout,"dict(",

    print >> fout, 'grouping="%s",' % task.grouping,
    print >> fout, 'group="%s",' % task.subsys,
    print >> fout, 'numFeds=%d,' % task.numFeds,
    print >> fout, 'coeffs=[ %s ],' % ", ".join(str(x) for x in task.meanFitResult['coeffs']),
    print >> fout, 'fedIds=[ %s ],' % ", ".join(str(x) for x in task.fedIds),

    print >> fout,"),"



#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
if __name__ == "__main__":


    ARGV = sys.argv[1:]

    assert len(ARGV) == 1

    tasksFile = ARGV.pop(0)

    import pickle

    reportData = pickle.load(open(tasksFile))
    tasks   = reportData['tasks']
    run     = reportData['globalParams']['run']
    dataset = reportData['globalParams']['dataset']
    xvar    = reportData['globalParams']['xvar']

    plotDir = os.path.dirname(tasksFile)
    outputFname = os.path.join(plotDir, "fitData_%s_%d_vs_%s.py" % (dataset, run, xvar))
    fout = open(outputFname, "w")

    from makeEvolutionSpreadSheet import SpreadsheetCreator, getAverageNumVerticesFromTasks

    print >> fout, "fedSizeData = dict("
    print >> fout, "avgNumVertices =", getAverageNumVerticesFromTasks(tasks),","

    print >> fout
    print >> fout, "#"
    print >> fout, "# coefficients: constant term first, linear term next etc."
    print >> fout, "#"
    print >> fout, "evolutionData = [",
    
    #----------
    from FedSizePerVertexLinearFit import FedSizePerVertexLinearFit

    isFirst = True
    for task in tasks:
        if not isinstance(task, FedSizePerVertexLinearFit):
            continue

        writePythonData(fout, task)
        

        # task.writeQuantilesCSV(fout, isFirst)
        isFirst = False

    print >> fout,"],"
    print >> fout,")"

    fout.close()
    print >> sys.stderr,"wrote report to", outputFname

