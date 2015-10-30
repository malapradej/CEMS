#!/bin/bash
# a subscript of lsf_emu.sh that makes sure the virtual env is activated per 
# process run.

COD_DIR=/home/users/malapradej/DASF/Code

cd $COD_DIR

. ~/venv/bin/activate

python2.7 $COD_DIR/create_emulator_ap.py --sza "$1" --vza "$2" --raa "$3" --train "$4" --validate "$5" --plot n
