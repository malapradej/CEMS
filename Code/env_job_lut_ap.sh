#!/bin/bash
# a subscript of lsf_lut_ap.sh that makes sure the virtual env is activated per 
# process run.
COD_DIR=/home/users/malapradej/DASF/Code

. ~/venv/bin/activate
python2.7 $COD_DIR/Emulator_LUT_ap_1cpu.py "$@"
