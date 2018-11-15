#!/usr/bin/env python3

"""
A probe the historical CO2 emissions data.
"""

import argparse

import data

def parse_args(args=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-e', '--emissions', type=data.get_emissions_grid,
                        default='CMIP6',
                        help='The emissions dataset.')

    return parser.parse_args(args)


def main(args):
    try:
        emis = args.emissions.from_disk()
    except:
        raise ValueError('Unknown emissions dataset.')

    print('\nInitial Carbon (ppm):       {:.3f} on {}'.format(emis.ppm_0, (emis.months[0] - 1).strftime('%Y-%m-%d')))

    T_em = emis.series_emissions(emis.months[0], '2007-12-31').sum()
    # print('\nTotal cumulonive emisions (gC):   {:.3e} at {}'.format(T_em, emis.months[-1]))

    ppm_em = emis.gC_to_ppm(T_em).values
    print('Total cum. emisions (+ppm): {:.3f} on {}'.format(ppm_em, '2007-12-31'))
    print('Final Carbon   (ppm):       {:.3f} on {}'.format(emis.ppm_0 + ppm_em, '2007-12-31'))

    print('\nNote: Final carbon is based solely on emissions data and does not include '
          'any of the other carbon sources/sinks in the Earth system.\n')


if __name__ == '__main__':
    main(parse_args())
