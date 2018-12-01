from data import MOLAR_MASS_C
from data import MEAN_MASS_AIR
from data import MOLAR_MASS_AIR
from data.cmip5 import CMIP5EmissionsGrid
from data.cmip6 import CMIP6EmissionsGrid

grid_dispatch = {'CMIP5': CMIP5EmissionsGrid,
                 'CMIP6': CMIP6EmissionsGrid}


def get_emissions_grid(dataset: str):
    dataset = dataset.upper()
    grid = grid_dispatch.get(dataset)
    if grid is None:
        raise ValueError(f'{dataset} is not a valid emissions dataset.')
    return grid


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
