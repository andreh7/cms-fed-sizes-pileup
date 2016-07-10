#!/bin/bash

FIRST_LS=1
LAST_LS=1279
LS_PER_JOB=200

for startLS in $(seq $FIRST_LS $LS_PER_JOB $LAST_LS) ; do

  lastLS=$[$startLS + $LS_PER_JOB - 1]

  cmsRun fedsizeanalyzer_cfg.py $startLS $lastLS hltphysics $RUN > log-$RUN-$startLS-$lastLS.log 2>&1 &

done