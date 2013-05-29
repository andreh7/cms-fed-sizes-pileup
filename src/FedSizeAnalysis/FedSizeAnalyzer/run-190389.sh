#!/bin/bash

eval `scram runtime -sh`
export RUN=190389

# before promptreco was available
# export RECODATASET=/ExpressPhysics/Commissioning12-Express-v1/FEVT
# export RAWDATASET=/ExpressPhysics/Commissioning12-Express-v1/FEVT

# there seem also to be other 
# streams like
#
#  /FEDMonitor/Commissioning12-v1/RAW
#  /L1Accept/Commissioning12-v1/RAW
# 
# but at the time of writing, there were
# no RECO datasets available 

export RAWDATASET="/MinimumBias/Commissioning12-v1/RAW"
export RECODATASET="/MinimumBias/Commissioning12-PromptReco-v1/RECO"

./cms.print-raw-and-reco-files-vs-lumisection.py --run=$RUN $RAWDATASET $RECODATASET > file_list_minbias_$RUN.py
cmsRun fedsizeanalyzer_cfg.py 1 99999 minbias $RUN
