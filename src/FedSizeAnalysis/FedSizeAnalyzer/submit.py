#!/usr/bin/env python

import os, sys

# ~/cmsutils/cms.submit-cfg-to-lsf.py fedsizeanalyzer_cfg.py \


#----------------------------------------------------------------------
# parameters
#----------------------------------------------------------------------
ls_per_job = 20
queue = "1nh"

# this is currentyl just used for file names
dataset = "jet"

# this is also currently used for file names only
run = 146644

# this must be set to the name the cmsRun job produces
# (i.e. this does not set which output file is produced
# by the cmsRun job. If this is not set to the correct
# name, the job output files will NOT be copied
# to the castor output directory)
outputFname = "out.root"

# the destination directory in castor
destDir = "/castor/cern.ch/user/a/aholz/2010-09-30-fed-size-analysis"

printOnly = False
cfg_file = "fedsizeanalyzer_cfg.py"

# if empty, selects all jobs
# selected_jobs = [ 61, 64, 75, 91]
selected_jobs = [  ]

#----------------------------------------------------------------------

file_list_name = "file_list_%s_%d.py" % (dataset, run)

if not os.path.exists(file_list_name):
    print >> sys.stderr, "file list file " + file_list_name + " not found"
    sys.exit(1)
    
execfile(file_list_name)

min_ls = min([ x['start_ls'] for x in files_list])
max_ls = max([ x['end_ls'] for x in files_list])

print min_ls, max_ls

start_ls = min_ls

job_number = 1

while start_ls < max_ls:

    end_ls = min(start_ls + ls_per_job - 1, max_ls)

    # submit the job

    if not selected_jobs or job_number in selected_jobs:

        cmd_parts = [ "bsub",
                      "-q " + queue,
                      "-J " + str(job_number) + "_" + dataset
                      ]

        script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

        output_prefix, output_suffix = outputFname.rsplit('.',1)

        dest_output_file = destDir + "/" + dataset + "_" + str(run) + "_" + ("%d." % job_number) + output_suffix
        dest_output_log = destDir + "/" + dataset + "_" + str(run) + "_" + ("%d." % job_number) + "log"

        cmd = " ".join(cmd_parts)

        if printOnly:
            pipe = sys.stdout
        else:
            pipe = os.popen(cmd, "w")

        original_dir = os.getcwd()

        print >> pipe, "#!/bin/sh"
        print >> pipe
        print >> pipe
        print >> pipe, "cd " + original_dir
        print >> pipe, "eval `scramv1 runtime -sh`"
        print >> pipe, "cd -"
        print >> pipe
        print >> pipe
        print >> pipe, "# run cmsRun"
        print >> pipe, "cmsRun",os.path.abspath(cfg_file),start_ls,end_ls,dataset,run," 2>&1 | tee %d.log"  % job_number

        print >> pipe
        print >> pipe, "# copy the produced output file to castor"
        print >> pipe, "rfcp " + outputFname + " " + dest_output_file
        print >> pipe, "rfcp " + "%d.log" % job_number + " " + dest_output_log

        if not printOnly:
            pipe.close()
            print "submitted job",job_number," for lumisections",start_ls,"..",end_ls
        else:
            print "----------------------------------------"


    # prepare next iteration
    start_ls = end_ls + 1
    job_number += 1

