# %%
# Example of how to use the WCL to GLOG conversion function 
# for damage (sticks and boxes).


# %%
# Import required libraries and functions
import pandas as pd
import numpy as np
import bhi_dip_format_transfer as dt


# %%
# Import the WCL damage file that will be converted to GLOG format
damage_filename = r"TestData_damage_WCL_format.csv"

WCL = pd.read_csv(
    damage_filename,
    na_values=['', ' ', '-999.25'], # handles expected NaN values
    skiprows=[1], # skip unit row, comment out if not present in your file
    )

WCL.head()

# %%
# Import the caliper data
cala_filename = r"TestData_CALA.csv"

CALA = pd.read_csv(
    cala_filename,
    na_values=['', ' ', '-999.25'],
    skiprows=[1],
    )

CALA.head()

# %%
# Compute the radius at each depth in the WCL data using linear interpolation 

# Radius **MUST** be in meters for the GLOG conversion function to work correctly.
# In this case, the caliper data is in mm, so it is divided by 2 (to make a radius) 
# and then converted to m (/1000).

WCL['Radius'] = np.interp(WCL['Depth'], CALA['Depth'], CALA['CALA'] / 2 / 1000)

# %%
# Undertake the conversion from WCL to GLOG format
GLOG = dt.wcl_to_glog_sticks(WCL)
GLOG.head()

# Output has standard header names for GLOG format: 
# 'DEPTH', 'AZIMUTH', 'AZI_END', 'AZI_START', 'TILT', 'HEIGHT', 'AWIDTH', 'CATEGORY', 'NOTES'


# %%
# Add the correct units into the top of the dataframe. 
# The units in this case are ['m', 'deg', 'deg', 'deg', 'deg', 'm', 'deg', '', '',] for the columns 
# 'DEPTH', 'AZIMUTH', 'AZI_END', 'AZI_START', 'TILT', 'HEIGHT', 'AWIDTH', 'CATEGORY', 'NOTES'
# They may be different in your case.

GLOG.loc[-1] = ['m', 'deg', 'deg', 'deg', 'deg', 'm', 'deg', '', '',] # units row
GLOG.index = GLOG.index + 1  # shifting index
GLOG = GLOG.sort_index()  # sorting by index

GLOG.to_csv(r"Example_WCLtoGLOG_damage__results.csv", index=False)

GLOG

# %%

