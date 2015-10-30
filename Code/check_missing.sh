#!/bin/bash

# a script that checks which files in the emulator of diagnostics are missing.

path=$1
lrt_bgn=libradtran
lrt_end=.npz

for sza in 10 20 30 40 50 60 70 80 90; do
    for vza in 00 10 20 30 40 50 60 70 80; do
        for raa in 000 015 030 045 060 075 090 105 120 135 150 165 180; do
            FILE=${path}${lrt_bgn}_atm_path_${sza}_${vza}_${raa}${lrt_end}
            #echo $FILE
            if [ ! -f "$FILE" ]
            then
                echo $FILE
            fi
        done
    done
done
