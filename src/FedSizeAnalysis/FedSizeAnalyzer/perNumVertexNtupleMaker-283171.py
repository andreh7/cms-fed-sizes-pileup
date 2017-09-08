
import os
scriptDir = os.path.join(
    os.environ['CMSSW_BASE'],
    "src/FedSizeAnalysis/FedSizeAnalyzer")

assert os.environ.has_key('RUN'), "enivonrment variable RUN not set"
run = int(os.environ['RUN'])

triggerConditions = ( 'HLT_*', )

# note that this is less than previous' years high pileup
# fills (but this run was with two bunch crossings only,
# so potentially less statistics and thus smaller tails ?
# Or should we check the instantaneous luminosity ?)
maxNumVertices = eval(open(os.path.join(scriptDir,
                                    "data",
                                    "max-num-vertices-%d.txt" % run)).read())


# fedids seen in this run
fedIDsSeen = eval("[ " + 
                  open(os.path.join(scriptDir,
                                    "data",
                                    "fedids-%d.txt" % run)).read() + 
                  "]")

lumiFile = "lumi-files/lumi-by-bx-and-ls-%s.csv" % os.environ['RUN']
