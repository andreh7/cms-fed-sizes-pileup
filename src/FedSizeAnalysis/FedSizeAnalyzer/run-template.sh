#!/bin/bash

FIRST_LS={firstLs}
LAST_LS={lastLs}
LS_PER_JOB=100

# need export to see it from subprocesses 
export RUN={run}

for startLS in $(seq $FIRST_LS $LS_PER_JOB $LAST_LS) ; do

  lastLS=$[$startLS + $LS_PER_JOB - 1]

  cmsRun fedsizeanalyzer_cfg.py $startLS $lastLS {dstitle} $RUN > log-$RUN-{dstitle}-$startLS-$lastLS.log 2>&1 &

done
