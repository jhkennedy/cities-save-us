import abc

import xarray as xr
import pandas as pd

#########################
# Some useful constants #
#########################
MOLAR_MASS_AIR = 28.966  # g/Mol
MEAN_MASS_AIR = 5.1480e21  # g
MOLAR_MASS_C = 12.01  # g/Mol
MOLAR_MASS_CO2 = 44.01  # g/Mol
PPM_C_1752 = 276.39  # Mol/(Mol/1e6)


class EmissionsGrid(object):
    """
    Class to represent and work with gridded emissions data.
    """

    def __init__(self,  em_data: xr.Dataset, co2: xr.Dataset, months: pd.DatetimeIndex,
                 timestamp: str):

        self.emissions = em_data
        self.months = months
        self.co2 = co2

        self.ppm_0 = self.ppm_0 = PPM_C_1752 - self.gC_to_ppm(
                    self.series_emissions(timestamp, '1752').sum()).values

    # noinspection PyPep8Naming
    @staticmethod
    def gC_to_ppm(emissions: xr.Dataset) -> xr.Dataset:
        """
        Convert gC to ppm
        """
        # (g / g/Mol) / (g / g/Mol) * 1.e6
        # (Mol) / (Mol) * 1.e6
        # ppm
        return (emissions / MOLAR_MASS_C) / (MEAN_MASS_AIR / MOLAR_MASS_AIR) * 1.e6

    @staticmethod
    @abc.abstractmethod
    def month_slice(start_date=None, end_date=None, n_months=None):
        """
        Method that should create a time slice object for a monthly time series from any two of:
        :param start_date: When to begin the time slice
        :param end_date: when to end the time slice
        :param n_months: The number of months in the slice
        :return: a slice object
        """

    def series_emissions(self, start_date=None, end_date=None, n_months=None):
        """
        Find the total emissions at each grid location over a timeseries
        """
        _slice = self.month_slice(start_date, end_date, n_months)

        return self.co2.sel(time=_slice).sum(dim='time')

    def probe(self, end_date='2007-12-31'):
        print('\nInitial Carbon (ppm):       {:.3f} on {}'.format(
            self.ppm_0, (self.months[0] - 1).strftime('%Y-%m-%d')))

        t_em = self.series_emissions(self.months[0], end_date).sum()
        # print('\nTotal cumulative emissions (gC):   {:.3e} at {}'.format(t_em, self.months[-1]))

        ppm_em = self.gC_to_ppm(t_em).values
        print('Total cum. emissions (+ppm): {:.3f} on {}'.format(ppm_em, end_date))
        print('Final Carbon   (ppm):        {:.3f} on {}'.format(self.ppm_0 + ppm_em, end_date))

        print('\nNote: Final carbon is based solely on emissions data and does not include '
              'any of the other carbon sources/sinks in the Earth system.\n')
