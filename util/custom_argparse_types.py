"""A set of custom types to be used with the argparse module"""

import argparse
import os


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
