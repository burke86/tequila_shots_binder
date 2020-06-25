import numpy as np
import sys, os
import warnings
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import lightkurve as lk
from lightkurve import MPLSTYLE

from astropy import units as u
from astropy.table import unique
from astropy.table import QTable
from astropy.coordinates import SkyCoord
from astropy.wcs.utils import pixel_to_skycoord
import astropy.io.fits as fits

plt.style.use(MPLSTYLE)

def load(coord, diffim=False,
         out_dir=os.path.join(os.path.expanduser('~'),'tequila_shots/output')):
    """
    Load tequila_shots output file for previous pipeline run.
    WARNING: This code is not fully validated!
    Args:
        coord (SkyCoord): Astropy SkyCoord of target
            (REQUIRED)
        diffim (bool): Load difference imaging?
            (default is False)
        out_dir (str): Work directory path
            (default is '~/tequila_shots/output')
    Returns:
        out_dict: Output dictionary
            Use `out_dict.keys()` to get keywords.
    """

    # Get coordinate name
    coord_name = 'J{0}{1}'.format(coord.ra.to_string(unit=u.hourangle, sep='', precision=2, pad=True),
                                  coord.dec.to_string(sep='', precision=2, alwayssign=True, pad=True))

    # Get the directory of the target
    coord_dir = os.path.join(out_dir, coord_name)
    
    if not os.path.exists(coord_dir):
        print('Coord directory does not exist!')
        return None
        
    print('Files in object directory %s:' % coord_dir)
    f_list = os.listdir(coord_dir)
    
    if len(f_list) == 0:
        print('Coord directory is empty!')
        return None
    
    [print(f) for f in f_list]
    #TODO/WARNING: sort by sector!!
    print('WARNING: Sectors may be jumbled!!')
    
    f_list = [os.path.join(coord_dir,f) for f in f_list]
    
    # Plot image and get TPFs
    out_dict = {}
    out_dict['lc_target'] = [] # Target light curve array of all sectors
    out_dict['lc_target_bkg'] = [] # background light curve array 
    out_dict['lc_star'] = [] # Star light curve array of all sectors
    out_dict['aper_target_list'] = [] # List of target apertures files for each sector
    out_dict['aper_star_list'] = [] # List of star apertures files for each sector
    out_dict['ref_flux_list'] = [] # List of target pixel files for each sector
    out_dict['tpf_list'] = [] # List of target pixel files for each sector
    out_dict['tpf_diff_list'] = [] # List of difference target pixel files for each sector
    out_dict['coord_dir'] = coord_dir # Target output directory
    out_dict['wcs_ref'] = [] # Reference WCS
    
    # Populate dict
    for f in f_list:
        if '_panel_' in f:
            img = mpimg.imread(f)
            imgplot = plt.imshow(img)
            plt.gca().axis('off')
            plt.tight_layout()
            plt.show()
        elif 'ref_flux_' in f:
            out_dict['ref_flux_list'].append(fits.open(f)[0].data)
        elif 'lc_target_bkg_' in f:
            out_dict['lc_target_bkg'].append(lk.lightcurvefile.LightCurveFile(f))
        elif 'lc_target_' in f:
            out_dict['lc_target'].append(lk.lightcurvefile.LightCurveFile(f))
        elif 'lc_star_' in f:
            out_dict['lc_star'].append(lk.lightcurvefile.LightCurveFile(f))
        # Load TPFs
        if diffim:
            if 'tpf_diff_' in f:
                tpf = lk.TessTargetPixelFile(f)
                out_dict['tpf_list'].append(tpf)
                if out_dict['wcs_ref'] == []:
                    out_dict['wcs_ref'] = tpf.wcs
            elif 'tpfdiff_' in f:
                tpf = lk.TessTargetPixelFile(f)
                out_dict['tpf_diff_list'].append(tpf)
        else:
            if 'tpf_' in f:
                tpf = lk.TessTargetPixelFile(f)
                out_dict['tpf_list'].append(tpf)
                if out_dict['wcs_ref'] == []:
                    out_dict['wcs_ref'] = tpf.wcs
    
    print('Done loading.')
    
    return out_dict
