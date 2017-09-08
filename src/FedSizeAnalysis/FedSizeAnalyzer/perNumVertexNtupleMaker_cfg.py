import FWCore.ParameterSet.Config as cms
import os, sys, pprint, glob

#----------------------------------------------------------------------
# default parameters
# note: override these in a per run configuration file
# perNumVertexNtupleMaker-<run>.py
#----------------------------------------------------------------------

if not os.environ.has_key('RUN'):
    print >> sys.stderr,"environment variable RUN must be set"
    sys.exit(1)

if not os.environ.has_key('DATASET'):
    print >> sys.stderr,"environment variable DATASET must be set"
    sys.exit(1)


inputFiles = glob.glob("root-files/run-" + os.environ['RUN'] + "/" +
                       "-".join([ "out",
                                  os.environ['RUN'],
                                  os.environ['DATASET'],
                                  "*",
                                  "*",
                                  ]) + ".root")

assert inputFiles,"no input files found for run " + os.environ['RUN']

inputFiles = [ 'file:' + fname for fname in inputFiles ]

outputFile = os.path.expandvars("$CMSSW_BASE/../small-tuples/$DATASET-$RUN/small-tuples.root")

# create output file if not yet existing
if not os.path.exists(os.path.dirname(outputFile)):
    os.makedirs(os.path.dirname(outputFile))


#--------------------
# select events by HLT path
#
# set to None if no selection required
#--------------------

#triggerConditions = ( 'HLT_L1Tech_BSC_minBias_threshold1_v*', )
# triggerConditions = None


#--------------------

# set to non-None if you want to keep the filtered CMSSW events
cmsswOutputFname = '/tmp/ah/events.root'

#----------------------------------------------------------------------
# load per-run configuration
execfile("perNumVertexNtupleMaker-%s.py" % os.environ['RUN'])
#----------------------------------------------------------------------


process = cms.Process("FEDSIZENTUPLER")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )


process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(inputFiles),
)

#----------------------------------------------------------------------
# select events based on HLT trigger
#----------------------------------------------------------------------

import HLTrigger.HLTfilters.triggerResultsFilter_cfi as hlt

if triggerConditions != None:
    process.hltSelection = hlt.triggerResultsFilter.clone(
             hltResults = cms.InputTag( "TriggerResults","","HLT"),
            # triggerConditions = ( 'HLT_Physics_v*', ),
            triggerConditions = triggerConditions,
            l1tResults = '',
            throw = False
            )

#----------------------------------------------------------------------
# TFileService
# see https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideTFileService
#----------------------------------------------------------------------

process.TFileService = cms.Service("TFileService", 
      fileName = cms.string(outputFile),
      closeFileFast = cms.untracked.bool(True)
  )

#----------------------------------------------------------------------
# that's our little custom code


process.tupler = cms.EDAnalyzer('PerNumVertexNtupleMaker',

                                maxNumVertices = cms.untracked.uint32(maxNumVertices),
                                src = cms.untracked.InputTag('fedSizeData'),

                                fedIDs = cms.untracked.vuint32(*fedIDsSeen),

                                lumiFile = cms.untracked.string(lumiFile),
                                )

#----------------------------------------------------------------------
if cmsswOutputFname != None:
    process.out = cms.OutputModule("PoolOutputModule",
        # running interactively                           
        # fileName = cms.untracked.string('/tmp/myOutputFile.root'),

        # fileName = cms.untracked.string('out-%04d-%04d.root' % (min_ls, max_ls)),
        fileName = cms.untracked.string(cmsswOutputFname),                           

        # dropMetaDataForDroppedData = cms.untracked.bool(True),
        outputCommands = cms.untracked.vstring([
                                       # 'drop *',
                                       # 'keep FedSizeAnalysisData_*_*_*',
                                       # 'keep *_TriggerResults_*_*',
                                       'keep *',
                                       ]),

        # select only certain events
        SelectEvents = cms.untracked.PSet(
          SelectEvents = cms.vstring('mainPath')
        ),


    )

process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))


#----------------------------------------------------------------------

pathParts = []

if hasattr(process,'hltSelection'):
    pathParts.append(process.hltSelection)    # restrict the output ntuples to certain HLT paths    

pathParts.append(process.tupler)  # run our own code
# build a path, connecting all ingredients with a '*' 
import operator 
process.mainPath = cms.Path(reduce(operator.mul, pathParts))

if cmsswOutputFname != None:
    process.e = cms.EndPath(process.out)

#----------------------------------------------------------------------
# produce fewer 'begin processing...' messages
#----------------------------------------------------------------------
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

