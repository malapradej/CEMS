#!/bin/bash

# A script that will read in the output lut one angle set at a time and 
# run the emulator training.
# run a bsub command line operation to send jobs to lotus.
# run using: ./lsf_emu.sh <training_path> <validation_path>
# with <arg>...

. ~/venv/bin/activate


TR_DIR=$1
VL_DIR=$2
COD_DIR=/home/users/malapradej/DASF/Code

WRK_DIR=$TR_DIR

cd $TR_DIR

## uncomment if the amount of files and directories are small.
## use alternative to speed up traversing directories.

#for dir in $(find $TR_DIR -mindepth 3 -type d -print);

for sza in 10 20 30 40 50 60 70 80; do
for vza in 0 10 20 30 40 50 60 70 80; do
for raa in 0 15 30 45 60 75 90 105 120 135 150 165 180; do
#do
#    IFS='/' read -ra Path <<< "$dir"
#    sza=${Path[${#Path[@]}-3]}
#    vza=${Path[${#Path[@]}-2]}
#    raa=${Path[${#Path[@]}-1]}
    jbnm="gp_emu_$sza_$vza_$raa"
    bsub -q lotus -We 10 -W 2:00 -eo "$WRK_DIR/log/err/$jbnm.err" -oo "$WRK_DIR/log/out/$jbnm.out" -J $jbnm "$COD_DIR/env_job_emu.sh $sza $vza $raa $TR_DIR $VL_DIR"  
done
done
done
