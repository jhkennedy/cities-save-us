"""
Classes for working with these datasets
"""

import os
import numpy as np
import xarray as xr
import pandas as pd

#########################
# Some useful constants #
#########################
HERE = os.path.dirname(__file__)
MOLAR_MASS_AIR = 28.966  # g/Mol
MEAN_MASS_AIR = 5.1480e21  # g
MOLAR_MASS_C = 12.01  # g/Mol
MOLAR_MASS_CO2 = 44.01  # g/Mol
PPM_C_1752 = 276.39  # Mol/(Mol/1e6)


def get_emissions_grid(dataset: str):
    dataset = dataset.upper()
    if dataset == 'CMIP5':
        return CMIP5EmissionsGrid
    if dataset == 'CMIP6':
        return CMIP6EmissionsGrid
    else:
        raise ValueError(f'{dataset} is not a valid emissions dataset.')


class EmissionsGrid(object):
    """
    Class to represent and work with gridded emissions data.
    """

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


class CMIP6EmissionsGrid(EmissionsGrid):
    """
    The CMIP6 emissions dataset
    """
    def __init__(self, em_data, months=None, glob=None):
        self.name = 'CMIP6'
        self.glob = glob
        self.emissions = em_data

        self.lat_grid, self.lon_grid = np.meshgrid(em_data.lat.values, em_data.lon.values,
                                                   indexing='ij')

        timestamp = np.datetime_as_string(em_data.time[0].values, unit='D')
        if months is None:
            self.months = pd.date_range(start=timestamp, periods=len(em_data.time), freq='M')
        else:
            self.months = months

        self.co2 = self.emissions.sum('sector').CO2_em_anthro
        self.co2 = self.co2 * self.emissions.area * (
            self.months.days_in_month[:, None, None].values * 24 * 60 * 60) \
            * 1000. / MOLAR_MASS_CO2 * MOLAR_MASS_C  # in gC

        self.ppm_0 = PPM_C_1752 - self.gC_to_ppm(
                    self.series_emissions(timestamp, '1752').sum()).values

    @classmethod
    def from_disk(cls, glob=None, chunks=(('time', 12),), **kwargs):
        if glob is None:
            glob = os.path.join(HERE, 'CMIP6', 'CO2-*.nc')

        em_data = xr.open_mfdataset(glob, chunks=dict(chunks), **kwargs)

        area = xr.open_dataset(os.path.join(HERE, 'CMIP6', 'CEDS_gridcell_area_05.nc'))
        em_data['area'] = area['gridcell area']

        cmip6 = cls(em_data, glob=glob)
        return cmip6

    # noinspection PyTypeChecker
    @staticmethod
    def month_slice(start_date=None, end_date=None, n_months=None):
        """
        Get the series indexes from a sub-series specified by two of three:
        start_date, end_date, n_months.
        """
        start = pd.Timestamp(start_date, freq='M') - 1  # set to end of prev month
        end = pd.Timestamp(end_date, freq='M') + 0  # set to end of month

        if start_date and end_date:
            _slice = slice(start, end)
        elif start_date and n_months:
            _slice = slice(start, start + 12)
        elif end_date and n_months:
            _slice = slice(end-12, end)
        else:
            raise ValueError('Must specify at least two of: start_date, end_date, n_months.')

        return _slice

    def series_emissions(self, start_date=None, end_date=None, n_months=None):
        """
        Find the total emissions at each grid location over a timeseries
        """
        _slice = self.month_slice(start_date, end_date, n_months)

        return self.co2.sel(time=_slice).sum(dim='time')


class CMIP5EmissionsGrid(EmissionsGrid):
    """
    The CMIP5 emissions dataset
    """

    def __init__(self, em_data, months=None, glob=None):
        """
        Initialize
        """
        self.name = 'CMIP5'
        self.glob = glob
        self.emissions = em_data

        self.lat_grid, self.lon_grid = np.meshgrid(em_data.lat.values, em_data.lon.values,
                                                   indexing='ij')

        timestamp = ' '.join(em_data.time.units.split(' ')[2:])
        if months is None:
            self.months = pd.date_range(start=timestamp, periods=len(em_data.time), freq='M')
        else:
            self.months = months

        self.co2 = self.emissions.FF * self.emissions.AREA * (
                    self.months.days_in_month[:, None, None].values * 24 * 60 * 60)  # in gC

        self.ppm_0 = PPM_C_1752 - self.gC_to_ppm(
                    self.series_emissions(timestamp, '1752').sum()).values

    @classmethod
    def from_disk(cls, glob=None, chunks=(('time_counter', 12),), **kwargs):
        if glob is None:
            glob = os.path.join(HERE, 'CMIP5', 'CMIP5_gridcar_CO2_*.nc')

        em_data = xr.open_mfdataset(glob, decode_times=False, chunks=dict(chunks), **kwargs)

        timestamp = ' '.join(em_data.time_counter.units.split(' ')[2:])
        time = pd.date_range(start=timestamp, periods=len(em_data.time_counter), freq='M')
        em_data.time_counter.values = time.values
        em_data = em_data.rename({'time_counter': 'time', 'Longitude': 'lon', 'Latitude': 'lat'})

        cmip = cls(em_data, months=time, glob=glob)
        return cmip

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

    def month_slice(self, start_date=None, end_date=None, n_months=None):
        """
        Get the series indexes from a subseries specified by two of three:
        start_date, end_date, n_months.
        """
        start = pd.Timestamp(start_date, freq='M') + 0  # set to end of month
        end = pd.Timestamp(end_date, freq='M') - 1  # set to previous month

        if start_date and end_date:
            idx_start = self.months.get_loc(start)
            idx_end = self.months.get_loc(end) + 1
        elif start_date and n_months:
            idx_start = self.months.get_loc(start)
            idx_end = idx_start + n_months
        elif end_date and n_months:
            idx_end = self.months.get_loc(end) + 1
            idx_start = idx_end - n_months
        else:
            raise ValueError('Must specify at least two of: start_date, end_date, n_months.')

        return slice(idx_start, idx_end)

    def series_emissions(self, start_date=None, end_date=None, n_months=None):
        """
        Find the total emissions at each grid location over a timeseries
        """
        _slice = self.month_slice(start_date, end_date, n_months)

        return self.co2[_slice, :, :].sum(axis=0)
