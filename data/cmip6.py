import os
import numpy as np
import xarray as xr
import pandas as pd

from data.grid import MOLAR_MASS_C
from data.grid import MOLAR_MASS_CO2
from data.grid import EmissionsGrid

HERE = os.path.dirname(__file__)


class CMIP6EmissionsGrid(EmissionsGrid):
    """
    The CMIP6 emissions dataset
    """
    def __init__(self, em_data, months=None, glob=None):
        self.name = 'CMIP6'
        self.glob = glob

        self.lat_grid, self.lon_grid = np.meshgrid(em_data.lat.values, em_data.lon.values,
                                                   indexing='ij')

        timestamp = str(np.datetime_as_string(em_data.time[0].values, unit='D'))
        if months is None:
            months = pd.date_range(start=timestamp, periods=len(em_data.time), freq='M')

        co2 = em_data.sum('sector').CO2_em_anthro
        co2 = co2 * em_data.area * (months.days_in_month[:, None, None].values * 24 * 60 * 60) \
            * 1000. / MOLAR_MASS_CO2 * MOLAR_MASS_C  # in gC

        super().__init__(em_data=em_data, co2=co2, months=months, timestamp=timestamp)

    @classmethod
    def from_disk(cls, glob=None, chunks=(('time', 12),), **kwargs):
        if glob is None:
            glob = os.path.join(HERE, 'CMIP6', 'CO2-*.nc')

        em_data = xr.open_mfdataset(glob, decode_times=False, chunks=dict(chunks), **kwargs)

        timestamp = ' '.join(em_data.time.units.split(' ')[2:])
        time = pd.date_range(start=timestamp, periods=len(em_data.time), freq='M')
        em_data.time.values = time.values

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
