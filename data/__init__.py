from data.grid import get_emissions_grid

#########################
# Some useful constants #
#########################
MOLAR_MASS_AIR = 28.966  # g/Mol
MEAN_MASS_AIR = 5.1480e21  # g
MOLAR_MASS_C = 12.01  # g/Mol
MOLAR_MASS_CO2 = 44.01  # g/Mol
PPM_C_1752 = 276.39  # Mol/(Mol/1e6)

__all__ = [MOLAR_MASS_AIR, MEAN_MASS_AIR, MOLAR_MASS_C, MOLAR_MASS_CO2, PPM_C_1752,
           get_emissions_grid]
