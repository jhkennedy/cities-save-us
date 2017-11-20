#!/usr/bin/env python3

"""
A script to locate the top 49 CO2 emitting cities within the global CO2
emissions dataset
"""


import os
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from mpl_toolkits.basemap import Basemap

import data

from util import customArgparseTypes as cat


def parse_args(args=None):
    parser = argparse.ArgumentParser(description=__doc__,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   
    parser.add_argument('-c','--cities', type=cat.abs_existing_file,
            default=os.path.join('data','CityCO2Emissions.csv'),
            help='The cities dataset.')
    
    parser.add_argument('-e','--emissions', type=cat.emissions_file,
            default=os.path.join('data','CMIP5_gridcar_CO2_emissions_fossil_fuel_Andres_1751-2007_monthly_SC_mask11.nc'),
            help='The emissions dataset.')
    
    parser.add_argument('-y','--year',
            default='2005',
            help='Year to plot for the emissions dataset.')

    parser.add_argument('-g','--grid', action='store_true',
            help='Show the emissions grid. Warning: this will clobber the global'+
                 ' map and is only useful for zooming in.')
    

    return parser.parse_args(args)


def main(args):
    # Get emissions data
    if 'cmip5' in args.emissions.lower():
        emis = data.CMIP5EmissionsGrid.fromFile(args.emissions)
        model = 'CMIP5'
    else:
        raise ValueError('Unknown emissions dataset.')
   
    # Setup the plot
    city_map = Basemap(projection='robin', lon_0=0)
    city_map.drawcoastlines()
    city_map.fillcontinents(color='0.75', lake_color='1')
    city_map.drawparallels(np.arange(-80.,81.,20.))
    city_map.drawmeridians(np.arange(-180.,181.,20.))
    city_map.drawmapboundary(fill_color='white')
    
    emis_year_gC = emis.series_emissions(args.year, n_months=12)
    emis_year_Mt = emis_year_gC * 1.0e-12

    x_grid, y_grid = city_map(emis.lon_grid, emis.lat_grid)
    
    clevs = [0.1] + np.linspace(0.0,85,18)
    cont = city_map.contourf(x_grid, y_grid, emis_year_Mt, clevs, cmap='Reds', zorder=100)

    
    # Get city data
    city_data = pd.read_csv(args.cities)
    
    x, y = city_map(np.array(city_data['Longitude'].tolist()), 
                    np.array(city_data['Latitude'].tolist()) )
    
    city_map.scatter(x, y, 30, marker='o', edgecolors='m', facecolors='none', zorder=200)


    # Show the emissions grid
    if args.grid:
        city_map.scatter(x_grid, y_grid, 10, marker='+', color='b', zorder=150)

    # Finish plot
    title = ' '.join(['The top 49 $CO_2$ emitting cities in 2005 [Hoornweg, 2010], \n',
                       'located within the {} globally gridded $CO_2$ emissions',
                       '(Mt; >1e-4) during {}'])
    plt.title(title.format(model, args.year))
    
    cbar = city_map.colorbar(cont, location='bottom', pad='5%')
    cbar.set_label('Mt $CO_2$')
    plt.show()


if __name__ == '__main__':
    main(parse_args())
