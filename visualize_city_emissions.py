#!/usr/bin/env python3

"""
A script to locate the top 49 CO2 emitting cities within the global CO2
emissions dataset
"""

import os
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt

from cartopy import crs as ccrs
from cartopy import feature as cpf

import data

from util import custom_argparse_types as cat


def parse_args(args=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-c', '--cities', type=cat.abs_existing_file,
                        default=os.path.join('data', 'cities',  'CitiesandClimateChange.csv'),
                        help='The cities dataset.')

    parser.add_argument('-e', '--emissions', type=data.get_emissions_grid,
                        default='CMIP6',
                        help='The emissions dataset.')

    parser.add_argument('-t', '--title', action='store_true', default=False,
                        help='Include plot titles')

    parser.add_argument('-y', '--year',
                        default='2005',
                        help='Year to plot for the emissions dataset.')

    parser.add_argument('-g', '--grid', action='store_true',
                        help='Show the emissions grid. Warning: this will clobber the global'
                             ' map and is only useful for zooming in.')

    parser.add_argument('-s', '--save', action='store_true',
                        help='Save the figure as a 600dpi EPS figure instead of show.')

    return parser.parse_args(args)


def main(args):
    emis = args.emissions.from_disk()

    emis_year_gC = emis.series_emissions(args.year, n_months=12)
    emis_year_Mt = emis_year_gC * 1.0e-12

    # setup plot
    fig, ax = plt.subplots(1, 1, subplot_kw={'projection': ccrs.Robinson()},
                           figsize=(8, 6))

    pcm = ax.pcolormesh(emis.lon_corners, emis.lat_corners, np.ma.masked_less(emis_year_Mt, 0.1),
                        vmin=0.1, vmax=85.1, zorder=1, cmap='Reds', transform=ccrs.PlateCarree())

    ax.set_global()
    ax.add_feature(cpf.LAND, zorder=0, facecolor='lightgrey', edgecolor='black')
    ax.gridlines()

    # Get city data
    city_data = pd.read_csv(args.cities)

    x, y = np.array(city_data['Longitude'].tolist()), np.array(city_data['Latitude'].tolist())

    ax.scatter(x, y, 30, marker='o', edgecolors='m', facecolors='none', zorder=3,
               transform=ccrs.PlateCarree())

    # Show the emissions grid
    if args.grid:
        ax.scatter(emis.lon_grid, emis.lat_grid, 10, marker='+', color='b', zorder=2,
                   transform=ccrs.PlateCarree())

    # Finish plot
    if args.title:
        plt.title(f'The top 49 $CO_2$ emitting cities in 2005 [Hoornweg, 2010], \n'
                  f'located within the {emis.name} globally gridded $CO_2$ emissions'
                  f'(Mt; >1e-4) during {args.year}')

    cbar = fig.colorbar(pcm, orientation='horizontal', fraction=0.03, pad=0.05)
    cbar.set_label('Mt $CO_2$')
    plt.tight_layout()
    if args.save:
        plt.savefig(f'top_49_in_globe_{args.year}.pdf', dpi=600)
    else:
        plt.show()

    ax = city_data.plot.bar(x='City', y='Total GHG (MtCO2e)', color='C0', figsize=(8, 6))
    ax.legend(['Hoornweg, 2010 (Mt CO2)'])
    ax.set_ylabel('Mt CO2')

    if args.title:
        plt.title(f'The top 49 $CO_2$ emitting cities in 2005 [Hoornweg, 2010]')

    plt.tight_layout()
    if args.save:
        plt.savefig(f'top_49_barchart_{args.year}.pdf', dpi=600)
    else:
        plt.show()


if __name__ == '__main__':
    main(parse_args())
