"""A set of custom types to be used with the argparse module"""

import os
import sys
import argparse

def abs_existing_file(f):
    path = os.path.abspath(f)
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f+'\n    File must exist!')
    return path


def emissions_year(y):
    y = int(y)
    if y < 1751 and y > 2007:
        raise argparse.ArgumentTypeError(str(y)+' is not a valid year!\n Year'+
                ' must be (1751 <= year <= 2007).')
    return(y)


def unsigned_int(x):
    """
    Small helper function so argparse will understand unsigned integers.
    """
    x = int(x)
    if x < 1:
        raise argparse.ArgumentTypeError("This argument is an unsigned int type! Should be an integer greater than zero.")
    return x

