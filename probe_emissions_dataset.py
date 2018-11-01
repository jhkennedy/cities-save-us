#!/usr/bin/env python3

"""
A probe the historical CO2 emissions data.
"""

import argparse
import os

import data
from util import custom_argparse_types as cat


def parse_args(args=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-e', '--emissions', type=cat.emissions_file,
                        default=os.path.join('data',  'CMIP5', 'CMIP5_gridcar_CO2_emissions_fossil_fuel_'
                                                              'Andres_1751-2007_monthly_SC_mask11.nc'),
                        help='The emissions dataset.')

    return parser.parse_args(args)


def main(args):
    if 'cmip5' in args.emissions.lower():
        emis = data.CMIP5EmissionsGrid.from_file(args.emissions)
    else:
        raise ValueError('Unknown emissions dataset.')

    print('\nInitial Carbon (ppm):       {:.3f} on {}'.format(emis.ppm_0, (emis.months[0] - 1).strftime('%Y-%m-%d')))

    T_em = emis.series_emissions(emis.months[0], emis.months[-1]).sum()
    # print('\nTotal cumulonive emisions (gC):   {:.3e} at {}'.format(T_em, emis.months[-1]))

    ppm_em = emis.gC_to_ppm(T_em)
    print('Total cum. emisions (+ppm): {:.3f} on {}'.format(ppm_em, emis.months[-1].strftime('%Y-%m-%d')))
    print('Final Carbon   (ppm):       {:.3f} on {}'.format(emis.ppm_0 + ppm_em, emis.months[-1].strftime('%Y-%m-%d')))

    print('\nNote: Final carbon is based soley on emissions data and does not include '
          'any of the other carbon sources/sinks in the Earth system.\n')


if __name__ == '__main__':
    main(parse_args())
