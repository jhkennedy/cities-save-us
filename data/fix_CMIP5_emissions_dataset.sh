#!/usr/bin/env bash

# Change the missing_value and _FillValue attributes from the string:
#    -1.e34f
# to 
#    -1.e34
# so that netCDF4-python can read in the data. 
# (Else you get a can't convert string to number error.)

ncatted -O -a missing_value,AREA,o,d,-1.e34 CMIP5_gridcar_CO2_emissions_fossil_fuel_Andres_1751-1900_monthly_SC_mask11.nc
ncatted -O -a missing_value,FF,o,d,-1.e34 CMIP5_gridcar_CO2_emissions_fossil_fuel_Andres_1751-1900_monthly_SC_mask11.nc
ncatted -O -a _FillValue,FF,o,d,-1.e34 CMIP5_gridcar_CO2_emissions_fossil_fuel_Andres_1751-1900_monthly_SC_mask11.nc
ncatted -O -a _FillValue,AREA,o,d,-1.e34 CMIP5_gridcar_CO2_emissions_fossil_fuel_Andres_1751-1900_monthly_SC_mask11.nc

ncatted -O -a missing_value,AREA,o,d,-1.e34 CMIP5_gridcar_CO2_emissions_fossil_fuel_Andres_1901-2007_monthly_SC_mask11.nc
ncatted -O -a missing_value,FF,o,d,-1.e34 CMIP5_gridcar_CO2_emissions_fossil_fuel_Andres_1901-2007_monthly_SC_mask11.nc
ncatted -O -a _FillValue,FF,o,d,-1.e34 CMIP5_gridcar_CO2_emissions_fossil_fuel_Andres_1901-2007_monthly_SC_mask11.nc
ncatted -O -a _FillValue,AREA,o,d,-1.e34 CMIP5_gridcar_CO2_emissions_fossil_fuel_Andres_1901-2007_monthly_SC_mask11.nc

# ncatted -O -a missing_value,AREA,o,d,-1.e34 CMIP5_gridcar_CO2_emissions_fossil_fuel_Andres_1751-2007_monthly_SC_mask11.nc
# ncatted -O -a missing_value,FF,o,d,-1.e34 CMIP5_gridcar_CO2_emissions_fossil_fuel_Andres_1751-2007_monthly_SC_mask11.nc
# ncatted -O -a _FillValue,FF,o,d,-1.e34 CMIP5_gridcar_CO2_emissions_fossil_fuel_Andres_1751-2007_monthly_SC_mask11.nc
# ncatted -O -a _FillValue,AREA,o,d,-1.e34 CMIP5_gridcar_CO2_emissions_fossil_fuel_Andres_1751-2007_monthly_SC_mask11.nc
