#!/usr/bin/env python3

import os
import re
import argparse
import warnings
import numpy as np
import pandas as pd
import shapefile
import cartopy.feature
import matplotlib.pyplot as plt

from scipy.spatial import cKDTree
from shapely.geometry import shape
from shapely.geometry import MultiPoint
from cartopy import crs as ccrs

import data

from util import custom_argparse_types as cat

warnings.filterwarnings('ignore')


def parse_args(args=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-c', '--cities', type=cat.abs_existing_file,
                        default=os.path.join('data', 'cities', 'CitiesandClimateChange.csv'),
                        help='The cities dataset.')

    parser.add_argument('-t', '--town-areas', type=cat.abs_existing_file,
                        default=os.path.join('data', 'cities', 'USA', 'city_town_areas.shp'),
                        help='The shape of towns in the USA.')

    parser.add_argument('-e', '--emissions', type=data.get_emissions_grid,
                        default='CMIP6',
                        help='The emissions dataset.')

    parser.add_argument('-y', '--year',
                        default='2005',
                        help='Year to plot for the emissions dataset.')

    parser.add_argument('-n', '--nearest', type=cat.unsigned_int, default=3,
                        help='Sum the emissions for this many cells which are '
                             'nearest neighbors to a city.')

    parser.add_argument('--no-title', action='store_false',
                        help='Do not include titles on the plots.')

    parser.add_argument('-s', '--save', action='store_true',
                        help='Save the figure as a 600dpi EPS figure instead of show.')

    return parser.parse_args(args)


def strip_all(string: str) -> str:
    """
    Removes all white space around and in a string.

    :param string: A string to strip
    :return: A stripped string

    >>> strip_all('New York')
    'NewYork'
    """
    return string.strip().replace(' ', '')


def whitespace_camel_case(string: str) -> str:
    """
    Add white space between words indicated by CamelCase typing.

    :param string: A CamelCase string to add white space to
    :return: A white spaced string

    >>> whitespace_camel_case('NewYork')
    'New York'
    """
    # From: https://stackoverflow.com/a/37697078
    return re.sub('(?!^)([A-Z][a-z]+)', r' \1', string)


def city_shape_from_record(reader: shapefile.Reader, city: str) -> dict:
    """
    Get a geoJSON for a city from a shapefile

    :param reader: A shapefile reader
    :param city: The name of a city in the shapefile
    :return: A geoJSON of the city shape
    """
    for i, r in enumerate(reader.iterRecords()):
        if r[3] == city:
            return reader.shape(i).__geo_interface__
    raise KeyError(f'{city} does not exist in the shapefile')


def nn_corner_hulls(elem_nns: np.ndarray, x_corners: np.ndarray, y_corners: np.ndarray) -> list:
    """
        Get a set of convex hulls around the corners of the NN grid cells, where
        the corners are defined like:

        (X[i+1, j], Y[i+1, j])          (X[i+1, j+1], Y[i+1, j+1])
                              +--------+
                              | C[i,j] |
                              +--------+
            (X[i, j], Y[i, j])          (X[i, j+1], Y[i, j+1]),

        :param elem_nns: An list of a list of NN index locations (C[idx])
        :param x_corners: A meshgrid of the x coordinate values (X)
        :param y_corners: A meshgrid of the y coordinate values (Y)
        :return a list of shapely convex hull polygons
        """
    grid_shape = np.array(x_corners.shape) - 1
    hull_shapes = []
    for elem in elem_nns:
        all_corners = []
        for nn in elem:
            ii, jj = np.unravel_index(nn, grid_shape)
            # clockwise from lower-left
            all_corners.extend([(x_corners[ii, jj], y_corners[ii, jj]),
                                (x_corners[ii+1, jj], y_corners[ii + 1, jj]),
                                (x_corners[ii+1, jj+1], y_corners[ii + 1, jj + 1]),
                                (x_corners[ii, jj+1], y_corners[ii, jj + 1]),
                                ])

        hull_shapes.append(MultiPoint(all_corners).convex_hull)

    return hull_shapes


def main(args):
    emis = args.emissions.from_disk()

    emis_year_gC = emis.series_emissions(args.year, n_months=12)
    emis_year_Mt = emis_year_gC.values * 1.0e-12

    city_data = pd.read_csv(args.cities)

    emis.ll = np.ndarray((len(emis.lat_grid.ravel()), 2))
    emis.ll[:, 0] = emis.lat_grid.ravel()
    emis.ll[:, 1] = emis.lon_grid.ravel()

    emis.tree = cKDTree(emis.ll)
    city_q_distance, city_q_idxs = emis.tree.query(city_data[['Latitude', 'Longitude']],
                                                   k=args.nearest)

    city_q_emissions = np.zeros(city_data[['Latitude']].shape)
    for ii in range(len(city_data[['Latitude']])):
        city_q_emissions[ii] = np.sum(emis_year_Mt.ravel()[city_q_idxs[ii, :]])

    city_nn_outlines = nn_corner_hulls(city_q_idxs, emis.lon_corners, emis.lat_corners)

    city_data['NN Emissions (MtCO2e)'] = city_q_emissions * data.MOLAR_MASS_CO2 / data.MOLAR_MASS_C

    city_data['NN Em. - City (MtCO2e)'] = city_data['NN Emissions (MtCO2e)'] \
        - city_data['Total GHG (MtCO2e)']
    city_data['% Error'] = - city_data['NN Em. - City (MtCO2e)'] \
        / city_data['Total GHG (MtCO2e)'] * 100.

    towns = shapefile.Reader(args.town_areas)

    city_towns = set(city_data.City[city_data.Country == 'USA']).intersection(
        set([strip_all(r[3]) for r in towns.iterRecords()])
    )
    city_towns = [whitespace_camel_case(s) for s in city_towns]

    for ct in city_towns:
        geojson = city_shape_from_record(towns, ct)

        if ct.upper() == 'PHILADELPHIA' or ct.upper() == 'CHICAGO':
            # FIXME: But why??
            continue

        # setup plot
        fig, ax = plt.subplots(1, 1, subplot_kw={'projection': ccrs.Robinson()},
                               figsize=(8, 6))

        ax.add_feature(cartopy.feature.LAND, zorder=1, facecolor='none', edgecolor='darkgrey')

        pcm = ax.pcolormesh(emis.lon_corners, emis.lat_corners, np.ma.masked_less(emis_year_Mt, 0.1),
                            vmin=0.1, vmax=85.1, zorder=0, cmap='Reds', transform=ccrs.PlateCarree())

        shp = cartopy.feature.ShapelyFeature(shape(geojson), ccrs.PlateCarree(), edgecolor='tab:blue',
                                             facecolor='None', zorder=2)
        ax.add_feature(shp)

        outline_idx = city_data.loc[city_data.City == strip_all(ct)].index.values[0]
        oln = cartopy.feature.ShapelyFeature([city_nn_outlines[outline_idx].exterior],
                                             ccrs.PlateCarree(), edgecolor='tab:purple',
                                             facecolor='None', zorder=3)
        ax.add_feature(oln)

        ax.scatter(city_data['Longitude'], city_data['Latitude'], 30, marker='o',
                   edgecolors='m', facecolors='none', zorder=4, transform=ccrs.PlateCarree())

        cbar = fig.colorbar(pcm, orientation='horizontal', fraction=0.03, pad=0.05)
        cbar.set_label('Mt $CO_2$')

        clat = city_data.loc[city_data.City == strip_all(ct)].Latitude.values[0]
        clon = city_data.loc[city_data.City == strip_all(ct)].Longitude.values[0]
        ax.set_extent([clon-1.5, clon+1.5, clat-1.5, clat+1.5], crs=ccrs.PlateCarree())

        if args.no_title:
            plt.title(ct)

        plt.tight_layout()
        if args.save:
            plt.savefig(f'{strip_all(ct)}_{args.year}.eps', dpi=600)
        else:
            plt.show()

    ax = city_data.plot.bar(x='City', y=['Total GHG (MtCO2e)', 'NN Emissions (MtCO2e)'], figsize=(16, 6))
    ax.legend(['Hoornweg, 2010 (Mt CO2)', f'{emis.name} NN (Mt CO2)'])
    ax.set_ylabel('Mt CO2')

    if args.no_title:
        plt.title(f'City emissions in 2005 [Hoornweg, 2010] (Mt) compared to \n'
                  f'the {emis.name} emission calculated from {args.nearest} '
                  f'nearest neighbor cells for {args.year}.')

    plt.tight_layout()
    if args.save:
        plt.savefig(f'top_49_barchart_v_nn_{args.year}.eps', dpi=600)
    else:
        plt.show()


if __name__ == '__main__':
    main(parse_args())
