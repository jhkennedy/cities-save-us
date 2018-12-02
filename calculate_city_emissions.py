#!/usr/bin/env python3

"""
A script to determine the CO2 emissions at the grid points nearest the top 49
emitting cities (coordinates). 
"""

import argparse
import os

import numpy as np
import pandas as pd
from scipy import spatial
from scipy.interpolate import RegularGridInterpolator

import data
from util import custom_argparse_types as cat


def parse_args(args=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-c', '--cities', type=cat.abs_existing_file,
                        default=os.path.join('data', 'cities', 'CitiesandClimateChange.csv'),
                        help='The cities dataset.')

    parser.add_argument('-e', '--emissions', type=data.get_emissions_grid,
                        default='CMIP6',
                        help='The emissions dataset.')

    parser.add_argument('-y', '--year',
                        default='2005',
                        help='Year to plot for the emissions dataset.')

    parser.add_argument('-n', '--nearest', type=cat.unsigned_int,
                        help='Sum the emissions for this many cells which are '
                             'nearest neighbors to a city.')

    return parser.parse_args(args)


def main(args):
    emis = args.emissions.from_disk()

    emis_year_gC = emis.series_emissions(args.year, n_months=12)
    emis_year_Mt = emis_year_gC.values * 1.0e-12

    city_data = pd.read_csv(args.cities)

    if not args.nearest:
        emis_grid_nn = RegularGridInterpolator([emis.emissions.lat.values,
                                                emis.emissions.lon.values],
                                               emis_year_Mt, method='nearest')

        city_data['NN Emissions (MtCO2e)'] = emis_grid_nn(city_data[['Latitude', 'Longitude']])
        number_of_cells = 1
    else:
        emis.ll = np.ndarray((len(emis.lat_grid.ravel()), 2))
        emis.ll[:, 0] = emis.lat_grid.ravel()
        emis.ll[:, 1] = emis.lon_grid.ravel()

        emis.tree = spatial.cKDTree(emis.ll)
        city_q_distance, city_q_idxs = emis.tree.query(city_data[['Latitude', 'Longitude']],
                                                       k=args.nearest)

        city_q_emissions = np.zeros(city_data[['Latitude']].shape)
        for ii in range(len(city_data[['Latitude']])):
            city_q_emissions[ii] = np.sum(emis_year_Mt.ravel()[city_q_idxs[ii, :]])

        city_data['NN Emissions (MtCO2e)'] = city_q_emissions
        number_of_cells = args.nearest

    city_data['NN Em. - City (MtCO2e)'] = city_data.iloc[:, 7] - city_data.iloc[:, 5]
    city_data['% Error'] = (city_data.iloc[:, 7]
                            - city_data.iloc[:, 5]) / city_data.iloc[:, 5] * 100.

    print('\nTotal emissions from the to 50 cities:')
    city_emis = city_data['Total GHG (MtCO2e)'].sum()
    nn_emis = city_data['NN Emissions (MtCO2e)'].sum()
    print('    As reported in [Hoornweg, 2010]:               {}'.format(city_emis))
    print('    As calculated using {:2d} '
          'nearest neighbor cells: {:.3f}'.format(number_of_cells, nn_emis))

    global_emis = emis_year_Mt.sum()
    print('\nTotal global emissions from {} (Mt):            {:.3f}'.format(emis.name, global_emis))

    print('\n% global emissions cities account for:')
    print('    ' + 'Using [Hoornweg, 2010]:'
                   '             {:.3f}'.format(city_emis / global_emis * 100))
    print('    ' + 'Using {:2d} nearest neighbor cells:'
                   '    {:.3f}'.format(number_of_cells, nn_emis / global_emis * 100))

    print('')


if __name__ == '__main__':
    main(parse_args())
