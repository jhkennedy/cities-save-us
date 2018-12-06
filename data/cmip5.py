import os

import xarray as xr
import pandas as pd

from data.grid import EmissionsGrid


HERE = os.path.dirname(__file__)


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

        timestamp = ' '.join(em_data.time.units.split(' ')[2:])
        if months is None:
            months = pd.date_range(start=timestamp, periods=len(em_data.time), freq='M')

        co2 = em_data.FF * em_data.AREA * months.days_in_month[:, None, None].values \
            * 24 * 60 * 60  # in gC

        super().__init__(em_data=em_data, co2=co2, months=months, timestamp=timestamp)

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


    # def month_slice(self, start_date=None, end_date=None, n_months=None):
    #     """
    #     Get the series indexes from a subseries specified by two of three:
    #     start_date, end_date, n_months.
    #     """
    #     start = pd.Timestamp(start_date, freq='M') + 0  # set to end of month
    #     end = pd.Timestamp(end_date, freq='M') - 1  # set to previous month
    #
    #     if start_date and end_date:
    #         idx_start = self.months.get_loc(start)
    #         idx_end = self.months.get_loc(end) + 1
    #     elif start_date and n_months:
    #         idx_start = self.months.get_loc(start)
    #         idx_end = idx_start + n_months
    #     elif end_date and n_months:
    #         idx_end = self.months.get_loc(end) + 1
    #         idx_start = idx_end - n_months
    #     else:
    #         raise ValueError('Must specify at least two of: start_date, end_date, n_months.')
    #
    #     return slice(idx_start, idx_end)
    #
    # def series_emissions(self, start_date=None, end_date=None, n_months=None):
    #     """
    #     Find the total emissions at each grid location over a timeseries
    #     """
    #     _slice = self.month_slice(start_date, end_date, n_months)
    #
    #     return self.co2[_slice, :, :].sum(axis=0)
