#!/usr/bin/env python
"""
Creating emulators for libradtran
------------------------------------

This script creates a number of GP emulators derived from 
a number of training libradtran runs. The results are also
validated with a small(ish) set of additional independent
libradtran runs. 

The main assumptions on this script are that the training and
validation pairs exist on their own directories, and that the
different angular configurations are stored as subfolders with
the following naming scheme:

    /SZA/VZA/RAA/*.p
    
An example program run might be

    ./create_emulator.py --sza 10 --vza 0 --raa 0
    
which in UCL's computers, will look for files in 
``/data/selene/ucfajlg/libradtran_emu/lhd350_train_full/`` for 
the training set and ``/data/selene/ucfajlg/libradtran_emu/lhd200_valid_full2/``
for the validation set.

The outputs will appear in 
``/data/selene/ucfajlg/libradtran_emu/lhd200_valid_full/diagnostics`` (where
plots and text versions of the plots will be stored, filenames contain angles
and what not) and in 
``/data/selene/ucfajlg/libradtran_emu/lhd350_train_full/emulators``, where the 
emulator ``.npz`` configuration files will be stored.

A number of default parameter choices have been made for the emulators, these
include the use of 99% of the variance, and nothing else (I think...)

"""

__author__ = "J Gomez-Dans (NCEO & UCL)"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "J Gomez-Dans"
__email__ = "j.gomez-dans@ucl.ac.uk"

import argparse
import json
import glob
import cPickle
import os

import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt

import numpy as np

import gp_emulator

import pdb

thresh = 0.99

def plot_config ():
    """Update the MPL configuration"""
    config_json='''{
            "lines.linewidth": 2.0,
            "axes.edgecolor": "#bcbcbc",
            "patch.linewidth": 0.5,
            "legend.fancybox": true,
            "axes.color_cycle": [
                "#FC8D62",
                "#66C2A5",
                "#8DA0CB",
                "#E78AC3",
                "#A6D854",
                "#FFD92F",
                "#E5C494",
                "#B3B3B3"
            ],
            "axes.facecolor": "#eeeeee",
            "axes.labelsize": "large",
            "axes.grid": false,
            "patch.edgecolor": "#eeeeee",
            "axes.titlesize": "x-large",
            "svg.embed_char_paths": "path",
            "xtick.direction" : "out",
            "ytick.direction" : "out",
            "xtick.color": "#262626",
            "ytick.color": "#262626",
            "axes.edgecolor": "#262626",
            "axes.labelcolor": "#262626",
            "axes.labelsize": 12,
            "font.size": 12,
            "legend.fontsize": 12,
            "xtick.labelsize": 12,
            "ytick.labelsize": 12
            
    }
    '''
    s = json.loads ( config_json )
    plt.rcParams.update(s)
    plt.rcParams["axes.formatter.limits"] = [-4,4]
    

def pretty_axes( ax ):
    """This function takes an axis object ``ax``, and makes it purrty.
    Namely, it removes top and left axis & puts the ticks at the
    bottom and the left"""

    ax.spines["top"].set_visible(False)  
    ax.spines["bottom"].set_visible(True)  
    ax.spines["right"].set_visible(False)              
    ax.spines["left"].set_visible(True)  

    ax.get_xaxis().tick_bottom()  
    ax.get_yaxis().tick_left()  
    loc = plt.MaxNLocator( 6 )
    ax.yaxis.set_major_locator( loc )
    

    ax.tick_params(axis="both", which="both", bottom="off", top="off",  
            labelbottom="on", left="off", right="off", labelleft="on")  


def do_emulator ( sza, vza, raa, train_dir, validation_dir, plot_yn='n'):

    plot_config()
    files = glob.glob(os.path.join ( train_dir, "%d/%d/%d/*.p" % 
                                    (  sza, vza, raa)) )
    
    train_size = len ( files )
    
    params = np.zeros(( train_size, 6 ))
    #wvc, aot, alt, press, a, p
    spectra = np.zeros (( 1, train_size, 5201 ))
    #toa refl
    for i,fich in enumerate( files ):
        xd = cPickle.load ( open(fich, 'r') )
        params[i,:] = [xd['WVC'], xd['AOT'], xd['alt'], xd['press'], xd['a'], xd['p']]
        spectra[0, i, :] = xd['toa_refl']
    files = glob.glob(os.path.join ( validation_dir, "%d/%d/%d/*.p" % 
                                    (  sza, vza, raa)) )
    if len ( files ) == 0:
        raise IOError, "Are you sure this directory exists? (%s)" % \
            (os.path.join ( validation_dir, "%d/%d/%d/" % (  sza, vza, raa)))

    validation_size = len ( files )
    vparams = np.zeros(( validation_size, 6 ))
    #wvc, aot, alt, press
    vspectra = np.zeros (( 1, validation_size, 5201 ))
    # dlb_trans, atm_path, sph_albedo
    for i,fich in enumerate( files ):
        xd = cPickle.load ( open(fich, 'r') )
        vparams[i,:] = [xd['WVC'], xd['AOT'], xd['alt'], xd['press'], xd['a'], xd['p']]
        vspectra[0, i, :] = xd['toa_refl']

    m1 = spectra[0,:,:].mean(axis=0)
    M = [m1]

    gp1 = gp_emulator.MultivariateEmulator ( X= spectra[0,:,:], y=params, 
                                            thresh=thresh, n_tries=10 )

    # Save emulators
    if not os.path.exists ( os.path.join ( train_dir, "emulators" ) ):
        os.mkdir ( os.path.join ( train_dir, "emulators" ) )
    gp1.dump_emulator ( os.path.join ( train_dir, "emulators", 
                        "libradtran_toa_refl_%02d_%02d_%03d.npz" % 
                         (sza, vza, raa) ), 'toa_refl', sza, vza, raa )
    
    vrmse1 = [ ( vspectra[0, i, :] - gp1.predict ( vparams[i,:])[0]) 
              for i in xrange(validation_size)]

    V = [ vrmse1 ]

    if not os.path.exists ( os.path.join ( validation_dir, "diagnostics" ) ):
        os.mkdir ( os.path.join ( validation_dir, "diagnostics" ) )

    if plot_yn.lower() == 'y': 
        fig, axs = plt.subplots ( nrows=1, ncols=2, figsize=(10,5) ,sharex=True )
        
        labels = ["TOA Reflectance"]
        
        axs[1].plot(xd['lam'], np.array(V[0]).std(axis=0), '-', lw=2, label='std of rmse' )
        axs[1].plot(xd['lam'], M[0], '--', lw=2, label='mean training spectra' )

        axs[0].set_ylabel(labels[0])
        pretty_axes(axs[1])
        [ axs[0].plot ( xd['lam'], vspectra[0,j,:], "-k", alpha=0.5, lw=1, rasterized=True, label='validation spectra' ) \
            for j in np.arange(0, validation_size,20)]
        pretty_axes(axs[0])
        
        axs[0].set_xlabel("Wavelength [nm]")
        axs[1].set_xlabel("Wavelength [nm]")
        fig.suptitle("%d training samples, %.1f%% variance kept.\n Validation on %d samples" % ( train_size, thresh*100., validation_size) +
            "\nSZA: %02d VZA: %02d RAA: %03d" % ( sza, vza, raa ) )
        axs[1].set_title("RMSE validation error")
        axs[0].set_title ("Validation plot")
        plt.legend(loc='best')   
        plt.subplots_adjust(top=.8)
        #plt.tight_layout()
        piccy_fname = os.path.join ( os.path.join ( validation_dir, "diagnostics", 
                            "validation_plot_%02d_%02d_%03d.pdf" % (  sza, vza, raa)) )
        plt.savefig(piccy_fname, dpi=150, bbox_inches="tight")
        #plt.savefig(piccy_fname.replace("pdf", "png"), dpi=150, bbox_inches="tight")

    diagnostics_fname = os.path.join ( os.path.join ( validation_dir, "diagnostics", 
                        "diagnostics_%02d_%02d_%03d.txt" % (  sza, vza, raa)) )

    vrmse1 = np.array ( vrmse1 )
    rmse = "".join ( [ "%15.5g" % f for f in vrmse1.mean(axis=0) ] )
    rmse += "".join ( [ "%15.5g" % f for f in vrmse1.std(axis=0) ] )
    # Maybe we need to g
    with open ( diagnostics_fname, 'w') as fp:
        fp.write ("%02d %02d %03d %s" % ( sza, vza, raa, rmse ) )
    

if __name__ == "__main__":

    parser = argparse.ArgumentParser ( description=__doc__ )
    parser.add_argument ( "--sza", help="Solar zenith angle in degrees", type=int )
    parser.add_argument ( "--vza", help="View zenith angle in degrees", type=int )
    parser.add_argument ( "--raa", help="Relative azimuth angle in degrees", type=int )
    parser.add_argument ( "--train", "-t", help="Training data dir", 
            type=str, default="/work/scratch/malapradej/DASF/Data/LUT_ap/lhd250_train_ap1/" )
    parser.add_argument ( "--validate", "-v", help="Validation data dir", 
            type=str, default="/work/scratch/malapradej/DASF/Data/LUT_ap/lhd300_valid_ap1/" )
    parser.add_argument ( "--plot", "-p", help="Plot validation figures (y/n)", 
            type=str, default="n" )
 
    args = parser.parse_args ()
    do_emulator ( args.sza, args.vza, args.raa, args.train, args.validate, args.plot )
