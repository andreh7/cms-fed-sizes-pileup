import FWCore.ParameterSet.Config as cms
import os, sys, pprint


#----------------------------------------------------------------------
# parameters
#----------------------------------------------------------------------

if not os.environ.has_key('RUN'):
    print >> sys.stderr,"environment variable RUN not set, aborting"
    sys.exit(1)

run = int(os.environ['RUN'])


#----------------------------------------------------------------------
# load per-run configuration
execfile("fedsizeanalyzer-%s.py" % os.environ['RUN'])

#----------------------------------------------------------------------
if keepL1MenuInformation:

    for item in ('L1GtTriggerMenuLite_*_*_*',
                 'L1GlobalTriggerReadoutRecord_*_*_*'):
        if not item in keepProducts:
            keepProducts.append(item)

#----------------------------------------------------------------------
script_dir = os.environ['CMSSW_BASE'] + "/src" + "/FedSizeAnalysis/FedSizeAnalyzer"

# print "script_dir=",script_dir
# print "locals=",locals().keys()

def getInputFiles(min_ls, max_ls):
    global files_list

    """ returns a pair of lists of raw, reco files for the given luminosity section range """

    # do it this way because the script might be
    # copied to a temporary directory...


    # files_list = locals()['files_list']

    raw_files = set()
    reco_files = set()

    for entry in files_list:
        # check whether the luminosity section range of these files
        # have an overlap with the specified range

        if max_ls < entry['start_ls']:
            continue

        if min_ls > entry['end_ls']:
            continue

        # the first file in the list is the RAW file, the second is the RECO file

        # before 2011-12-14
        # raw_files.add(entry['files'][0])
        # reco_files.add(entry['files'][1])

        # from 2011-12-14 on: multiple files possible
        # for RECO and RAW thus entry['files'][X] is a list,
        # not a string any more
        raw_files = raw_files.union(entry['files'][0])
        reco_files = reco_files.union(entry['files'][1])

    return list(raw_files), list(reco_files)

#----------------------------------------------------------------------

if os.path.basename(sys.argv[0]) == 'cmsRun':
    ARGV = sys.argv[1:]
else:
    ARGV = sys.argv[:]

min_ls = int(ARGV[1])
max_ls = int(ARGV[2])

dataset = ARGV[3]
run = int(ARGV[4])

print "min_ls=",min_ls
print "max_ls=",max_ls
print "dataset=",dataset
print "run=",run

# read the list of files vs. lumisection
execfile(script_dir + "/file_list_%s_%s.py" % (dataset, run))

raw_files, reco_files = getInputFiles(min_ls, max_ls)

print len(reco_files),"reco files"
pprint.pprint(reco_files)

print len(raw_files),"raw files"
pprint.pprint(raw_files)

#----------------------------------------------------------------------
process = cms.Process("FEDSIZEANALYSIS")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(maxEvents) )


process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(reco_files),
                            
    secondaryFileNames = cms.untracked.vstring(raw_files),

)

#----------------------------------------------------------------------
# reject random trigger events (there was a problem with run 146644)
#----------------------------------------------------------------------

import HLTrigger.HLTfilters.triggerResultsFilter_cfi as hlt

if run != 198588:
    process.rejectHltRandom = hlt.triggerResultsFilter.clone(
             hltResults = cms.InputTag( "TriggerResults","","HLT"),
            triggerConditions = ( 'NOT HLT_Random_v*', ),
            l1tResults = '',
            throw = False
            )
else:
    process.rejectHltRandom = cms.EDFilter("HLTBool",
                                           result = cms.bool( True )
                                           )


#----------------------------------------------------------------------
# that's our little custom code
process.fedSizeData = cms.EDProducer('FedSizeAnalyzer',
                                     )

if os.environ['RUN'] >= 190000:
    # for 2012 (e.g. for runs >= 190000)
    #  FEDRawDataCollection                  "rawDataCollector"          ""                "LHC"     
    process.fedSizeData.rawDataSource = cms.InputTag("rawDataCollector")
else:
    # for 2011 (and before ?)
    process.fedSizeData.rawDataSource = cms.InputTag("source"),

if locals().has_key('useRECO'):
    process.fedSizeData.useRECO = cms.untracked.bool(useRECO)


#----------------------------------------------------------------------
process.out = cms.OutputModule("PoolOutputModule",
    # running interactively                           
    # fileName = cms.untracked.string('/tmp/myOutputFile.root'),

    fileName = cms.untracked.string('out-%04d-%04d.root' % (min_ls, max_ls)),
                               
    # dropMetaDataForDroppedData = cms.untracked.bool(True),
    outputCommands = cms.untracked.vstring([
                                   'drop *',
                                   'keep FedSizeAnalysisData_*_*_*',
                                   'keep *_TriggerResults_*_*',

                                   # for keeping the original vertex collection
                                   'keep *_offlinePrimaryVertices_*_*',

                                   # for per-bunch crossing luminosity information
                                   # see https://hypernews.cern.ch/HyperNews/CMS/get/luminosity/104/1.html
                                   'keep edmMergeableCounter_*_*_*',
                                   'keep LumiSummary_lumiProducer_*_*',
                                   'keep LumiDetails_lumiProducer_*_*',

                                   ]),

    # select only certain events
    SelectEvents = cms.untracked.PSet(
      SelectEvents = cms.vstring('mainPath')
    ),
                               

)

# additional, user-specified products to keep
process.out.outputCommands.extend([ "keep " + x for x in keepProducts ])



process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))


#----------------------------------------------------------------------
# produce L1GtTriggerMenuLite objects
# see also http://cmslxr.fnal.gov/lxr/source/EventFilter/L1GlobalTriggerRawToDigi/test/L1GtTriggerMenuLite_cfg.py 
#----------------------------------------------------------------------

# to be concatenated with * later on
mainPathComponents = []

#----------
# for per-bunch crossing luminosity information
# see https://hypernews.cern.ch/HyperNews/CMS/get/luminosity/104/1.html
process.load("RecoLuminosity.LumiProducer.lumiProducer_cff")
mainPathComponents.append(process.lumiProducer)
#----------

mainPathComponents.append(process.rejectHltRandom)     # veto random trigger events
mainPathComponents.append(process.fedSizeData)         # run our own code

import operator

process.mainPath = cms.Path(
    # apply '*' between the elements of mainPathComponents
    reduce(operator.mul, mainPathComponents)
    )

process.e = cms.EndPath(process.out)

#----------------------------------------------------------------------
# produce fewer 'begin processing...' messages
#----------------------------------------------------------------------
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

#----------------------------------------------------------------------
# good luminosity section selection
#----------------------------------------------------------------------

process.source.lumisToProcess = cms.untracked.VLuminosityBlockRange()

#----------------------------------------
# read the given good lumi section (JSON)
# file 
#----------------------------------------

required_run = int(os.environ['RUN'])

if good_lumi_section_json_file != None:

    json_data = eval( open(good_lumi_section_json_file).read() )

    lumi_sections_from_json = []

    for run,lumisections in sorted(json_data.iteritems()):
        run = int(run)
        if run != required_run:
            continue

        for ls in lumisections:
            lumi_sections_from_json.append([ls[0], ls[1]])

    if len(lumi_sections_from_json) == 0:
        raise Exception("no luminosity sections found to process for run %d" % required_run)

    del run

    #----------------------------------------


    # filter these lumi sections
    selected_ls_ranges = []

    for ls_range in lumi_sections_from_json:
        if ls_range[0] > max_ls:
            continue
        if ls_range[1] < min_ls:
            continue

        # there is some overlap

        selected_ls_ranges.append([
            max(min_ls, ls_range[0]),
            min(max_ls, ls_range[1])
            ])

    print "selected_ls_ranges=",
    pprint.pprint(selected_ls_ranges)

    if selected_ls_ranges:
        process.source.lumisToProcess.extend([ "%d:%d-%d:%d" % (required_run, ls_range[0], required_run, ls_range[1]) for ls_range in selected_ls_ranges ])
    else:
        # avoid putting something empty here because this means 'take all'
        process.source.lumisToProcess.append('0:0-0:0')
    # process.source.lumisToProcess.append('146644:2377-146644:2473')
else:
    print "no json file given, running on everything"
