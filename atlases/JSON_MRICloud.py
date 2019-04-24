# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
from os.path import isfile, join
from pathlib import Path
import numpy as np
from nibabel.testing import data_path
import nibabel as nib
import json
import pdb
import glob
from nilearn import plotting as nip
from nilearn import image
import pandas as pd

mypath = str(Path().absolute())
labelpath = join(mypath,'MRI_Cloud_Atlases')
dirs = [x[0] for x in os.walk(labelpath)]
dirs = [i for i in dirs if 'git' not in i]
dirs = [i for i in dirs if 'ipynb' not in i]
dirs = [i for i in dirs if '01' in i]
files = []
for d in dirs:
    patient = d.split('/')
    patient = patient[len(patient)-1]
    file = patient+'_FullLabels.nii'
    patFile = os.path.join(d,file)
    files.append(patFile)
    
def main():
    for f in files:
        print(f)
        outfile = f.replace('.nii','.json')
        parcel_im = nib.load(f)
        #get_centers(parcel_im,outfile)
        parcel_centers = get_centers(parcel_im,outfile)
        
        with open(outfile) as js:
            js_contents = json.load(js)
            for (k, v) in js_contents.items():
                try:
                    js_contents[k]["center"] = parcel_centers[int(k)]
                except KeyError:
                    js_contents[k]["center"] = None
                    with open(outfile, 'w') as jso:
                        json.dump(js_contents, jso, indent=4)
    return parcel_centers

def get_centers(brain, outfile):
    """
    Get coordinate centers given a nifti image loaded with nibabel
    
    Returns a dictionary of label: coordinate as an [x, y, z] array
    """
    dat = brain.get_data()
    dat = np.squeeze(dat)
    labs = np.unique(dat)
    labs = labs[labs != 0]
    print('here')
    fd_dat = np.stack([np.asarray(dat == lab).astype('float64') for lab in labs], axis=3)
    print('here2')
    parcels = nib.Nifti1Image(dataobj=fd_dat, header=brain.header, affine=brain.affine)
    regions_imgs = image.iter_img(parcels)
    # compute the centers of mass for each ROI
    coords_connectome = [nip.find_xyz_cut_coords(img) for img in regions_imgs]

    
    return dict(zip(labs, coords_connectome))

main()

