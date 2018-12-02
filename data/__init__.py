from typing import Type

from data.grid import MOLAR_MASS_AIR
from data.grid import MEAN_MASS_AIR
from data.grid import MOLAR_MASS_C
from data.grid import MOLAR_MASS_CO2
from data.grid import PPM_C_1752

from data.grid import EmissionsGrid
from data.cmip5 import CMIP5EmissionsGrid
from data.cmip6 import CMIP6EmissionsGrid

grid_dispatch = {'CMIP5': CMIP5EmissionsGrid,
                 'CMIP6': CMIP6EmissionsGrid}


def get_emissions_grid(dataset: str) -> Type[EmissionsGrid]:
    """
    A convenience function to locate a CMIP EmisionsGrid; often used as an argparse type
    :param dataset: The name of the CMIP dataset (e.g., 'CMIP5 or 'CMIP6')
    :return: The CMIP EmissionsGrid class
    """
    dataset = dataset.upper()
    grid = grid_dispatch.get(dataset)
    if grid is None:
        raise ValueError(f'{dataset} is not a valid emissions dataset.')
    return grid


__all__ = [MOLAR_MASS_AIR, MEAN_MASS_AIR, MOLAR_MASS_C, MOLAR_MASS_CO2, PPM_C_1752,
           get_emissions_grid]
