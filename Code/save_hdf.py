#!/usr/bin/env python

"""A script that simply saves the *.npz emulators into an hdf5 file according
to the convention of JGD. 
./save_hdf.py <path_to_emulators>
"""

import h5py
import sys
import os
import re
import glob
import numpy as np
import pdb

if len(sys.argv)==1:
    raise IOError, 'No path argument was provided.'

path = sys.argv[1]
if not(os.path.exists(path)):
    raise IOError, 'Path %s does not exits.' %path

fn_hdf = os.path.join(path, 'libradtran_emulators.h5')
if os.path.exists(fn_hdf):
    os.remove(fn_hdf)
    print 'file %s existed so writing over it.' % fn_hdf

f5 = h5py.File(fn_hdf, 'w')

file_names = glob.glob(os.path.join(path, '*.npz'))

for fn in file_names:
    print 'converting %s.' % fn
    pckl = np.load(fn)
    basis_functions = pckl['basis_functions']
    hyperparams = pckl['hyperparams']
    thresh = pckl['thresh']
    y_train = pckl['y']
    X_train = pckl['X']
    n_pcs = pckl['n_pcs']
    group = re.search('libradtran_(.+?)[.]npz' , fn).group(1)
    
    if group in f5.keys():
        raise ValueError, 'Emulator already exists!'
    f5.create_group('/%s' % group)
    f5.create_dataset ( "/%s/X_train" % group, data=X_train )
    f5.create_dataset ( "/%s/y_train" % group, data=y_train )
    f5.create_dataset ( "/%s/hyperparams" % group, data=hyperparams )
    f5.create_dataset ( "/%s/basis_functions" % group, data=basis_functions )
    f5.create_dataset ( "/%s/thresh" % group, data=thresh )
    f5.create_dataset ( "/%s/n_pcs" % group, data=n_pcs )
     
f5.close()
print 'done!'

