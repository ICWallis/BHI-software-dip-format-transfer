# convert and damage pick format between GeoLog and WellCAD

# %%
import pandas as pd
import numpy as np


# %%
# read in the GLOG export
geolog_test_file = r"test_sticks.csv"

glog_export = pd.read_csv(
    geolog_test_file,
    na_values=['', ' ', '-999.25'], # handles expected nan values
    skiprows=[1], # skips the second row which contains units
    )

# Units are currently handled manually in this method. They are first stripped
# from the import file and then manually defined and added to the WCL export file. 

print(glog_export.columns)
glog_export.head()

########## Function starts here ##########

# %%
# Convert GLOG tilt to WCL tilt convention (opposite direction relative to the borehole axis)
glog_export['WCL_TILT_DEG'] = glog_export['TILT'] * -1

# replace nan values in WCL_TILT_DEG with 0
glog_export['WCL_TILT_DEG'] = glog_export['WCL_TILT_DEG'].fillna(0)

# if WCL_TILT_DEG is < 0.01, set that value to 0
glog_export['WCL_TILT_DEG'] = np.where(glog_export['WCL_TILT_DEG'] < 0.1, 0, glog_export['WCL_TILT_DEG'])

# replace nan values in 'AWIDTH' with 0
glog_export['AWIDTH'] = glog_export['AWIDTH'].fillna(0)

# Subselect the columns needed for the WCL file
wcl_damage = glog_export[[
    'DEPTH', # Depth
    'AZIMUTH', # Azimuth
    'WCL_TILT_DEG', # Tilt
    'HEIGHT', # Length
    'AWIDTH', # Opening
    'CATEGORY', # Type
    'NOTES', # Notes
]].copy()

# Rename the columns to match the WCL format (names in the row comments)
wcl_damage.rename(columns={
    'DEPTH': 'Depth',
    'AZIMUTH': 'Azimuth',
    'WCL_TILT_DEG': 'Tilt',
    'HEIGHT': 'Length',
    'AWIDTH': 'Opening',
    'CATEGORY': 'Type',
}, inplace=True)


########## Function ends here ##########

# Add a row at the top of the dataframe with units [m, deg, deg, m, deg, '']
wcl_damage.loc[-1] = ['m', 'deg', 'deg', 'm', 'deg', '', '']
wcl_damage.index = wcl_damage.index + 1  # shifting index
wcl_damage = wcl_damage.sort_index()  # sorting by index

# Export to a new CSV file called damage.csv
wcl_damage.to_csv(r"GLOG_to_WCL__sticks_result.csv", index=False)

wcl_damage.head()


# %%
