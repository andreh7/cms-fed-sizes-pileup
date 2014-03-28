#!/bin/bash

#----------------------------------------------------------------------

function setcmssw
{
    vers=$(echo ${1} | sed 's/\./_/g' )

    builtin cd  $(scramv1 list -c CMSSW CMSSW_${vers} | head -1 | awk '{print $3}' )

    eval `scramv1 runtime -sh` && \
    builtin cd -
}

#----------------------------------------------------------------------


if [ -z "$RUN" ]; then
  echo "environment variable \$RUN must be set to the run number under investigation"
  return
fi

#--------------------
# find the CMSSW version used for (RECO) for this run
#--------------------

if [ $RUN = 198588 ] || [ $RUN = 198609 ]; then
  CMSSW_VERSION=5_3_2_patch2 
elif [ $RUN = 179827 ] ; then

  export SCRAM_ARCH=slc5_amd64_gcc451
  CMSSW_VERSION=4_4_0_patch3

else
  echo "don't know which CMSSW version to use for run $RUN"
  return
fi 




echo "using CMSSW $CMSSW_VERSION for run $RUN"
setcmssw $CMSSW_VERSION
