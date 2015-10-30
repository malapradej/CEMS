#!/bin/bash

# A script that will read in the output lut one angle set at a time and 
# deletes a files in a directory structure of the lut.
# run a bsub command line operation to send jobs to lotus.
# run using: ./lsf_delete.sh <lut_root_path> 
# with <arg>...


WRK_DIR=$1

cd $WRK_DIR

for dir in $(find $WRK_DIR -mindepth 3 -type d);
do
    echo $dir
    #jbnm="del_$dir"
    #bsub -q lotus -We 1 -eo "$WRK_DIR/log/err/$jbnm.err" -oo "$WRK_DIR/log/out/$jbnm.out" -J $jbnm "find $dir -type f -delete"  
done
