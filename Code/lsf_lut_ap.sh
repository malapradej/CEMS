#!/bin/bash

# A script that will read in the input lut and loop over every entry and 
# run a bsub command line operation to send jobs to lotus.
# run using: ./lsf_lut_ap.sh <lut_file.dat>
# with <arg>...

. ~/venv/bin/activate

WRK_DIR=/work/scratch/malapradej/DASF/Data/LUT_ap/lhd250_train_ap2
COD_DIR=/home/users/malapradej/DASF/Code

JOB_CWD=$WRK_DIR

mkdir -p $WRK_DIR

cd $WRK_DIR
mkdir -p log
mkdir -p log/err
mkdir -p log/out

while IFS= read -r line
do
    [[ $line = \#* ]] && continue # skips all # lines
    jbnm=${line// /_}
    bsub -q lotus -We 3 -eo "$WRK_DIR/log/err/$jbnm.err" -oo "$WRK_DIR/log/out/$jbnm.out" -J $jbnm "$COD_DIR/env_job_lut_ap.sh $line"
done <$1
