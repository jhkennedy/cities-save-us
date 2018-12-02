#!/usr/bin/env python3

import os
import re
import argparse
import pandas as pd
import geopandas as gp

import data

from util import custom_argparse_types as cat


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

    return parser.parse_args(args)


def strip_all(string):
    return string.strip().replace(' ', '')


def split_camel_case(string):
    # From: https://stackoverflow.com/a/37697078
    return re.sub('(?!^)([A-Z][a-z]+)', r' \1', string)


def main(args):
    cmip = args.emissions.from_disk()
    print(cmip.name)

    cities = pd.read_csv(args.cities)
    towns = gp.read_file(args.town_areas)

    city_towns = set(cities.City[cities.Country == 'USA']).intersection(
            set(towns.City.apply(strip_all))
    )
    city_towns = [split_camel_case(s) for s in city_towns]

    for ct in city_towns:
        print(towns[towns.City == ct].City)


if __name__ == '__main__':
    main(parse_args())
