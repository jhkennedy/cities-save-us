#!/usr/bin/env python3

"""
A script to locate the top 49 CO2 emitting cities
"""

import numpy
import pandas
import argparse

import matplotlib.pyplot as plt

from mpl_toolkits.basemap import Basemap

from util import customArgparseTypes as cat

def parse_args(args=None):
    parser = argparse.ArgumentParser(description=__doc__,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   
    parser.add_argument('-c','--cities', type=cat.abs_existing_file,
            help='The the cities dataset.')
    
    return parser.parse_args(args)


def main(args):
    city_data = pandas.read_csv(args.cities)

    city_map = Basemap(projection='robin', lon_0=0)

    city_map.drawcoastlines()
    city_map.fillcontinents(color='0.75', lake_color='1')
    city_map.drawparallels(numpy.arange(-80.,81.,20.))
    city_map.drawmeridians(numpy.arange(-180.,181.,20.))
    city_map.drawmapboundary(fill_color='white')
    
    x, y = city_map(numpy.array(city_data['Longitude'].tolist()), 
                    numpy.array(city_data['Latitude'].tolist()) )
    
    city_map.scatter(x, y, 30, marker='o', color='m', zorder=100)

    plt.title('The top 49 $CO_2$ emitting cities in 2005 [Hoornweg, 2010]')
    plt.show()




if __name__ == '__main__':
    main(parse_args())

