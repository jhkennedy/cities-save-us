"""
Classes for working with these datasets
"""

from netCDF4 import Dataset
from util import EmissionsGrid


class CMIP5EmissionsGrid(EmissionsGrid):
    """
    The CMIP5 emissions dataset
    """
    
    @classmethod
    def from_file(cls, _file, mode='r', **kwargs):
        """
        Create a new CMIP5Emissions from a netCDF file.
        """
        if mode != 'r':
            data = Dataset(_file, mode=mode, **kwargs)
            cmip5 = cls.from_data(data)
        else: 
            with Dataset(_file, mode=mode, **kwargs) as data:
                cmip5 = cls.from_data(data)

        return cmip5 


    @classmethod
    def from_data(cls, data):
        """
        Create a new CMIP5Emissions from a netCDF Dataset.
        """
        cmip5 = cls(lat=data.variables['Latitude'][:],
                    lon=data.variables['Longitude'][:], 
                    area=data.variables['AREA'][:, :],
                    ff_co2=data.variables['FF'][:, :, :],
                    start_date=str.join(' ', data.variables['time_counter'].getncattr('units').split(' ')[2:]),
                    n_months=len(data.variables['time_counter'][:])
                    )
        
        return cmip5
