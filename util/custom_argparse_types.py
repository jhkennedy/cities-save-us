"""A set of custom types to be used with the argparse module"""

import argparse
import os


def emissions_file(f):
    MSG = 'NOTE: you may need to combine the emsissions datasets first! See the data directory.'
    N = len(MSG)
    try:
        path = abs_existing_file(f)
    except argparse.ArgumentTypeError as E:
        print('{}\n{}\n{}'.format('=' * N, MSG, '=' * N))
        raise E

    return path


def abs_existing_file(f):
    path = os.path.abspath(f)
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f + '\n    File must exist!')
    return path


def unsigned_int(x):
    """
    Small helper function so argparse will understand unsigned integers.
    """
    x = int(x)
    if x < 1:
        raise argparse.ArgumentTypeError("This argument is an unsigned int type! "
                                         "Should be an integer greater than zero.")
    return x
