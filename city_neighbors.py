#!/usr/bin/env python3

"""
A script to determine the CO2 emissions at the grid points nearest the top 49
emitting cities (coordinates). 
"""

import argparse

import os
import scipy
import pandas
import numpy as np

from netCDF4 import Dataset
from scipy.interpolate import RegularGridInterpolator

from util import customArgparseTypes as cat
from verify_data import DataGrid
from verify_data import MOLAR_MASS_AIR, MEAN_MASS_AIR, MOLAR_MASS_C, PPM_C_1752 


def parse_args(args=None):
    parser = argparse.ArgumentParser(description=__doc__,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   
    parser.add_argument('-c','--cities', type=cat.abs_existing_file,
            default=os.path.join('data','CityCO2Emissions.csv'),
            help='The cities dataset.')
    
    parser.add_argument('-e','--emissions', type=cat.abs_existing_file,
            default=os.path.join('data','fix.nc'),
            help='The emissions dataset.')
    
    parser.add_argument('-y','--year', type=cat.emissions_year,
            default=2005,
            help='Year to plot for the emissions dataset.')
    
    parser.add_argument('-n','--nearest', type=cat.unsigned_int,
            help='Use all this many nearest neighbors.')
    

    return parser.parse_args(args)

def main(args):
    emis = DataGrid(Dataset(args.emissions, 'r'))

    emis_dy = 2008-args.year
    start_month = -12*emis_dy
    stop_month = -12*(emis_dy-1)

    emis_year = emis.ff[start_month,:,:] 
    for tt in range(start_month, stop_month):
        emis_year += emis.ff[tt,:,:] 
    emis_year *= emis.area[:,:] * emis.dt.total_seconds() # g

    emis_year_ppm = (emis_year / MOLAR_MASS_C) / (MEAN_MASS_AIR / MOLAR_MASS_AIR) * 1.e6 
    emis_year_Mt = emis_year * 1.0e-12


    city_data = pandas.read_csv(args.cities)
    soi = ['Population (Millions)','Total GHG (MtCO2e)','Total GHG (tCO2e/cap)']

    
    if not args.nearest:
        emis_grid_nn = RegularGridInterpolator([emis.lat, emis.lon],
                emis_year_Mt, method='nearest')
       
        soi.append('Em. dataset (MtCO2e)')
        city_data[soi[-1]] = emis_grid_nn(city_data[['Latitude','Longitude']])
        
    else:
        emis.ll = np.ndarray( (len(emis.lat_grid.ravel()), 2) )
        emis.ll[:,0] = emis.lat_grid.ravel()
        emis.ll[:,1] = emis.lon_grid.ravel()

        emis.tree = scipy.spatial.cKDTree(emis.ll)
        
        city_qd, city_qi = emis.tree.query(city_data[['Latitude','Longitude']], k=args.nearest)
        
        city_qe = np.zeros(city_data[['Latitude']].shape)
        for ii in range(len(city_data[['Latitude']])):
            city_qe[ii] = np.sum(emis_year_Mt.ravel()[city_qi[ii,:]])

        soi.append('Em. dataset (MtCO2e)')
        city_data[soi[-1]] = city_qe


    soi.append('Total - Em. (MtCO2e)')
    city_data[soi[-1]] = city_data[soi[1]] - city_data[soi[3]]

    soi.append('% Diff (Total vs Em.)')
    city_data[soi[-1]] = (city_data[soi[3]] - city_data[soi[1]]) / city_data[soi[1]] * 100.


    print(city_data[ [soi[ii] for ii in [1,3,4,5]] ])
    print('-'*80)
    print(city_data[ [soi[ii] for ii in [1,3,4,5]] ].describe())
    print('-'*80)

    print('Total emissions from the cities (Mt):\n')
    city_emis = np.array( [np.sum(city_data[soi[ii]]) for ii in [1,3,4]] )
    for ii, item in enumerate([1,3,4]):
        print(soi[item]+':   '+str(city_emis[ii]))
    
    print('\nTotal global emissions (Mt):\n')
    emis.globe = np.sum(emis_year_Mt, axis=None)
    print(emis.globe)

    print('\n% global emissions cities account for:\n')
    for ii, item in enumerate([1,3,4]):
        print(soi[item]+':   '+str(city_emis[ii]/emis.globe*100.))
    


if __name__ == '__main__':
    main(parse_args())

