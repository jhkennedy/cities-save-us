"""
Some useful utilities
"""

import numpy as np
import pandas as pd

#########################
# Some useful constants #
#########################
MOLAR_MASS_AIR = 28.966  # g/Mol
MEAN_MASS_AIR = 5.1480e21  # g
MOLAR_MASS_C = 12.01  # g/Mol
PPM_C_1752 = 276.39  # Mol/(Mol/1e6)


class EmissionsGrid(object):
    """
    Class to represent and work with gridded emissions data.
    """
    def __init__(self, lat=None, lon=None, area=None, ff_co2=None, start_date=None, end_date=None, n_months=None):
        """
        Initialize
        """
        if lat.shape and not lon.shape:
            raise ValueError('lat and lon must both be given.')
        self.lat = lat
        self.lon = lon
        self.lat_grid, self.lon_grid = np.meshgrid(self.lat[:], self.lon[:], indexing='ij')
        
        if area.shape != self.lat_grid.shape:
            raise ValueError('lat_grid and area must have the same shape;'
                             ' lat_gird.shape = {}'.format(self.lat_grid.shape))
        self.area = area
       
        self.months = self._month_series(start_date, end_date, n_months)
        
        if ff_co2.shape != (len(self.months), *self.lat_grid.shape):
            raise ValueError('ff_co2 must have this shape: {}'.format((len(self.months), *self.lat_grid.shape)))
        self.ff_co2 = ff_co2  # in gC/m^2/s

        self.co2 = self.ff_co2 * self.area * (self.months.days_in_month[:, None, None].values * 24 * 60 * 60)  # in gC

        self.ppm_0 = PPM_C_1752 - self.gC_to_ppm(self.series_emissions(start_date, '1752').sum())


    # noinspection PyPep8Naming
    @staticmethod
    def gC_to_ppm(emissions):
        """
        Convert gC to ppm
        """
        # (g / g/Mol) / (g / g/Mol) * 1.e6
        # (Mol) / (Mol) * 1.e6
        # ppm
        return (emissions / MOLAR_MASS_C) / (MEAN_MASS_AIR / MOLAR_MASS_AIR) * 1.e6 


    @staticmethod
    def _month_series(start_date=None, end_date=None, n_months=None):
        """
        Get a series of months from two of three: start_date, end_date, n_months.
        """
        if start_date and end_date:
            series = pd.date_range(start=start_date, end=end_date, freq='M')
        elif start_date and n_months:
            series = pd.date_range(start=start_date, periods=n_months, freq='M')
        elif end_date and n_months:
            series = pd.date_range(end=end_date, periods=n_months, freq='M')
        else:
            raise ValueError('Must specify at least two of: start_date, end_date, n_months.')

        return series

    
    def _month_slice(self, start_date=None, end_date=None, n_months=None):
        """
        Get the series indexes from a subseries specified by two of three: start_date, end_date, n_months.
        """
        start = pd.Timestamp(start_date, freq='M') + 0  # set to end of month 
        end = pd.Timestamp(end_date, freq='M') - 1    # set to previous month 

        if start_date and end_date:
            idx_start = self.months.get_loc(start) 
            idx_end = self.months.get_loc(end)+1
        elif start_date and n_months:
            idx_start = self.months.get_loc(start) 
            idx_end = idx_start + n_months
        elif end_date and n_months:
            idx_end = self.months.get_loc(end)+1 
            idx_start = idx_end - n_months
        else:
            raise ValueError('Must specify at least two of: start_date, end_date, n_months.')

        return slice(idx_start, idx_end)

    def series_emissions(self, start_date=None, end_date=None, n_months=None):
        """
        Find the total emissions at each grid location over a timeseries 
        """
        _slice = self._month_slice(start_date, end_date, n_months)
        
        return self.co2[_slice, :, :].sum(axis=0)
