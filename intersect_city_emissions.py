#!/usr/bin/env python3

import os
import re
import argparse
import pandas as pd
import shapefile
import matplotlib.pyplot as plt

from shapely.geometry import shape
from cartopy import crs as ccrs
from cartopy.feature import ShapelyFeature
import cartopy.feature

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


def main(args):
    # cmip = args.emissions.from_disk()
    # print(cmip.name)

    cities = pd.read_csv(args.cities)
    towns = shapefile.Reader(args.town_areas)

    city_towns = set(cities.City[cities.Country == 'USA']).intersection(
            set([strip_all(r[3]) for r in towns.iterRecords()])
    )
    city_towns = [whitespace_camel_case(s) for s in city_towns]

    for ct in city_towns:
        geojson = city_shape_from_record(towns, ct)

        if ct.upper() == 'PHILADELPHIA'or ct.upper() == 'CHICAGO':
            # FIXME: But why??
            continue

        # setup plot
        fig, ax = plt.subplots(1, 1, subplot_kw={'projection': ccrs.Robinson()},
                               figsize=(8, 6))

        plt.title(ct)
        shp = ShapelyFeature(shape(geojson),  ccrs.PlateCarree(), edgecolor='black')
        ax.add_feature(shp)

        plt.show()


if __name__ == '__main__':
    main(parse_args())
