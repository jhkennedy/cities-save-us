#!/usr/bin/env python3

"""
A script to determine the CO2 emissions at the grid points nearest the top 49
emitting cities (coordinates). 
"""

import argparse

import os
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

    emis_grid_nn = RegularGridInterpolator([emis.lat, emis.lon],
            emis_year_Mt, method='nearest')
   
    soi.append('Em. dataset (MtCO2e)')
    city_data[soi[-1]] = emis_grid_nn(city_data[['Latitude','Longitude']])
    
    soi.append('Total - Em. (MtCO2e)')
    city_data[soi[-1]] = city_data[soi[1]] - city_data[soi[3]]

    print(city_data[ [soi[i] for i in [1,3,4]] ].describe())
    print('-'*80)
    print(city_data[ [soi[i] for i in [1,3,4]] ])
    

if __name__ == '__main__':
    main(parse_args())

