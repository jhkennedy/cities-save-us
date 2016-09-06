#!/usr/bin/env python3

"""
A script to verify cities emissions data
"""

import argparse

import scipy
import numpy as np

from datetime import datetime, timedelta
from netCDF4 import Dataset

from util import customArgparseTypes as cat

MOLAR_MASS_AIR = 28.966 # g/Mol
MEAN_MASS_AIR = 5.1480e21 # g
MOLAR_MASS_C = 12.01 # g/Mol
PPM_C_1752 = 276.39 # Mol/(Mol/1e6)

def parse_args(args=None):
    parser = argparse.ArgumentParser(description=__doc__,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   
    parser.add_argument('-e','--emissions', type=cat.abs_existing_file,
            default=os.path.join('data','fix.nc'),
            help='The emissions dataset.')
    
    return parser.parse_args(args)


class DataGrid:
    def __init__(self, data):
        self.lon = data.variables['Longitude']
        self.lat = data.variables['Latitude']
        self.area = data.variables['AREA']
        self.ff = data.variables['FF']
        self.t = data.variables['time_counter']
        
        self.lat_grid, self.lon_grid = scipy.meshgrid(self.lat[:], self.lon[:], indexing='ij')
        
        date_string = str.join(' ', self.t.getncattr('units').split(' ')[2:])
        self.t_0 = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

        self.dt = timedelta(days=365.0/12.0)

        em1751 = 0.0
        for tt in range(12):
            em1751 += np.sum( self.ff[tt,:,:] * self.area[:,:] ) * self.dt.total_seconds() # g
        
        self.gC_0 = em1751

        ppm_em1751 = (em1751 / MOLAR_MASS_C) / (MEAN_MASS_AIR / MOLAR_MASS_AIR) * 1.e6
                   # (g / g/Mol) / (g / g/Mol) * 1.e6
                   # (Mol) / (Mol) * 1.e6
                   # (Mol) / (Mol/1.e6)
                   # ppm
        self.ppm_0 = PPM_C_1752 - ppm_em1751
        

def main(args):
    emis = DataGrid(Dataset(args.emissions, 'r'))

    print('Initial Carbon (ppm):  '+str(emis.ppm_0))
    
    total_emissions = 0.0 # gC
    for tt in range(len(emis.t)):
        total_emissions += np.sum( emis.ff[tt,:,:] * emis.area[:,:] ) * emis.dt.total_seconds() # g
        
    print('Total emisions (gC):   '+str(total_emissions))

    ppm_emissions = (total_emissions / MOLAR_MASS_C) / (MEAN_MASS_AIR / MOLAR_MASS_AIR) * 1.e6 
                  # (g / g/Mol) / (g / g/Mol) * 1.e6
                  # (Mol) / (Mol) * 1.e6
                  # (Mol) / (Mol/1.e6)
                  # ppm

    print('Total emisions (+ppm): '+str(ppm_emissions))
    print('Final Carbon   (ppm):  '+str(emis.ppm_0 + ppm_emissions)) 


if __name__ == '__main__':
    main(parse_args())
