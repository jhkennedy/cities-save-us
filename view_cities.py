#!/usr/bin/env python3

"""
A script to view cities emissions data
"""
import os
import sys
import argparse

from util import customArgparseTypes as cat
from pprint import pprint

def parse_args(args=None):
    parser = argparse.ArgumentParser(description=__doc__,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   
    parser.add_argument('-e','--emmissions', type=cat.abs_existing_file,
            help='The emissions dataset.')
    
    results = parser.parse_args(args)
    
    return results


def main(args):
    pprint(args)

if __name__ == '__main__':
    args = parse_args()
    main(args)
