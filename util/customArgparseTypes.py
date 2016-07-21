"""A set of custom types to be used with the argparse module"""

import os
import sys
import argparse

def abs_existing_file(f):
    path = os.path.abspath(f)
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f+'\n    File must exist!')
    return path


