# convert dip and damage pick format between WCL and GLOG

# %%
import pandas as pd
import numpy as np


# %%
# Import the WCL data and drop the unit row

damage_filename = r"to be created.csv"
wcl_damage = pd.read_csv(
    damage_filename,
    na_values=['', ' ', '-999.25'],
    skiprows=[1],
    )


# %%
# Process the WCL damage dataframe to match GLOG conventions

# if the Tilt value is not 0, then flip the value. Otherwise, set it to NaN
wcl_damage['Tilt'] = wcl_damage['Tilt'].replace(0, np.nan)
wcl_damage['GLOG Tilt'] = wcl_damage['Tilt'] * -1


# %%


wcl_damage.rename(columns={
    'Depth': 'DEPTH', 
    'Azimuth': 'AZIMUTH',  
    'Tilt': 'Tilt', 
    'Length': 'HEIGHT', 
    'Opening': 'AWIDTH', 
    'Type': 'CATEGORY', 
    'Notes': 'NOTES',
    'GLOG Tilt': 'TILT',
}, inplace=True)

# drop the Tilt column
wcl_damage.drop(columns=['Tilt'], inplace=True)

# # Replace NAN values with -999.25
wcl_damage.fillna(-999.25, inplace=True)

wcl_damage.columns


# %%
# Add a row at the top of the dataframe with units [ft, ft, deg, deg, mm, deg, '', '']
wcl_damage.loc[-1] = ['ft', 'deg', 'ft', 'deg', '', '', 'deg',]
wcl_damage.index = wcl_damage.index + 1  # shifting index
wcl_damage = wcl_damage.sort_index()  # sorting by index

wcl_damage.to_csv(r"0__converter__WCL_to_GLOG__damage__result.csv", index=False)

# %%


# %%


# %%


# %%