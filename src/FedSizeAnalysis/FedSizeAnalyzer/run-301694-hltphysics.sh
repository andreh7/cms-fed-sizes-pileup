#!/bin/bash

FIRST_LS=36
LAST_LS=102
LS_PER_JOB=100

# need export to see it from subprocesses 
export RUN=301694

for startLS in $(seq $FIRST_LS $LS_PER_JOB $LAST_LS) ; do

  lastLS=$[$startLS + $LS_PER_JOB - 1]

  cmsRun fedsizeanalyzer_cfg.py $startLS $lastLS hltphysics $RUN > log-$RUN-hltphysics-$startLS-$lastLS.log 2>&1 &

done
