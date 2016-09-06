#!/usr/bin/env python3

"""
A script to locate the top 49 CO2 emitting cities within the global CO2
emissions dataset
"""

import argparse

import os
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
            default=os.path.join('data','CityCO2Emissions.csv'),
            help='The cities dataset.')
    
    parser.add_argument('-e','--emissions', type=cat.abs_existing_file,
            default=os.path.join('data','fix.nc'),
            help='The emissions dataset.')
    
    parser.add_argument('-y','--year', type=cat.emissions_year,
            default=2005,
            help='Year to plot for the emissions dataset.')

    parser.add_argument('-g','--grid', action='store_true',
            help='Show the emissions grid. Warning: this will clobber the global'+
                 ' map and is only useful for zooming in.')
    

    return parser.parse_args(args)


def main(args):
    # Setup the plot
    city_map = Basemap(projection='robin', lon_0=0)
    city_map.drawcoastlines()
    city_map.fillcontinents(color='0.75', lake_color='1')
    city_map.drawparallels(np.arange(-80.,81.,20.))
    city_map.drawmeridians(np.arange(-180.,181.,20.))
    city_map.drawmapboundary(fill_color='white')
    
    # Get emissions data
    emis = DataGrid(Dataset(args.emissions, 'r'))
    
    emis_dy = 2008-args.year
    start_month = -12*emis_dy
    stop_month = -12*(emis_dy-1)

    emis_year = emis.ff[start_month,:,:] 
    for tt in range(start_month, stop_month):
        emis_year += emis.ff[tt,:,:] 
    emis_year *= emis.area[:,:] * emis.dt.total_seconds() # g

    emis_year_ppm = (emis_year / MOLAR_MASS_C) / (MEAN_MASS_AIR / MOLAR_MASS_AIR) * 1.e6 
    emis_year_Gt = emis_year * 1.0e-15

    x_grid, y_grid = city_map(emis.lon_grid, emis.lat_grid)
    
    clevs = [0.0001] + np.linspace(0.0,0.085,18)
    cont = city_map.contourf(x_grid, y_grid, emis_year_Gt, clevs, cmap='Reds', zorder=100)

    
    # Get city data
    city_data = pandas.read_csv(args.cities)
    
    x, y = city_map(np.array(city_data['Longitude'].tolist()), 
                    np.array(city_data['Latitude'].tolist()) )
    
    city_map.scatter(x, y, 30, marker='o', edgecolors='m', facecolors='none', zorder=200)


    # Show the emissions grid
    if args.grid:
        city_map.scatter(x_grid, y_grid, 10, marker='+', color='b', zorder=150)

    # Finish plot
    plt.title('The top 49 $CO_2$ emitting cities in 2005 [Hoornweg, 2010], \n '+
            'located within the globally gridded $CO_2$ emissions (Gt; '+
            '>1e-4) during '+str(args.year))
    
    cbar = city_map.colorbar(cont, location='bottom', pad='5%')
    cbar.set_label('Gt $CO_2$')
    plt.show()


if __name__ == '__main__':
    main(parse_args())

