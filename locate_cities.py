#!/usr/bin/env python3

"""
A script to locate the top 49 CO2 emitting cities within the global CO2
emissions dataset
"""

import argparse

import pandas
import numpy as np
import matplotlib.pyplot as plt

from mpl_toolkits.basemap import Basemap
from netCDF4 import Dataset

from util import customArgparseTypes as cat
from verify_data import DataGrid
from verify_data import MOLAR_MASS_AIR, MEAN_MASS_AIR, MOLAR_MASS_C, PPM_C_1752 

def parse_args(args=None):
    parser = argparse.ArgumentParser(description=__doc__,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   
    parser.add_argument('-c','--cities', type=cat.abs_existing_file,
            help='The the cities dataset.')
    
    parser.add_argument('-e','--emmissions', type=cat.abs_existing_file,
            help='The emissions dataset.')
    
    parser.add_argument('-y','--year', type=cat.emissions_year,
            default=2005,
            help='Year to plot for the emissions dataset.')

    return parser.parse_args(args)


def main(args):
    emis = DataGrid(Dataset(args.emmissions, 'r'))
    
    emis_dy = 2008-args.year
    start_month = -12*emis_dy
    stop_month = -12*(emis_dy-1)

    emis_year = emis.ff[start_month,:,:] 
    for tt in range(start_month, stop_month):
        emis_year += emis.ff[tt,:,:] 
    emis_year *= emis.area[:,:] * emis.dt.total_seconds()

    city_map = Basemap(projection='robin', lon_0=0)
    
    city_data = pandas.read_csv(args.cities)

    city_map = Basemap(projection='robin', lon_0=0)

    city_map.drawcoastlines()
    city_map.fillcontinents(color='0.75', lake_color='1')
    city_map.drawparallels(np.arange(-80.,81.,20.))
    city_map.drawmeridians(np.arange(-180.,181.,20.))
    city_map.drawmapboundary(fill_color='white')
    
    x_grid, y_grid = city_map(emis.lon_grid, emis.lat_grid)
    
    emis_year_ppm = (emis_year / MOLAR_MASS_C) / (MEAN_MASS_AIR / MOLAR_MASS_AIR) * 1.e6 
    
    clevs = [0.001, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035]
    city_map.contourf(x_grid, y_grid, emis_year_ppm, clevs, cmap='Reds', zorder=100)
    #plt.title('$CO_2$ (ATM ppm; >0.001) emissions in 2007')
   
    
    x, y = city_map(np.array(city_data['Longitude'].tolist()), 
                    np.array(city_data['Latitude'].tolist()) )
    
    city_map.scatter(x, y, 30, marker='o', edgecolors='m', facecolors='none', zorder=200)

    plt.title('The top 49 $CO_2$ emitting cities in 2005 [Hoornweg, 2010], \n '+
            'located within the globally gridded $CO_2$ emissions (ATM ppm; '+
            '>0.001) for '+str(args.year))
    plt.show()


if __name__ == '__main__':
    main(parse_args())

