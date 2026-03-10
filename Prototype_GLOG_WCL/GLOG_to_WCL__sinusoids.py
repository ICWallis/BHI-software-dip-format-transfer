# convert and damage pick format between geolog and wellcad

# %%
import pandas as pd
import numpy as np


# %%
# read in the GLOG export
geolog_test_file = r"test_sinusoids.csv"

glog_export = pd.read_csv(
    geolog_test_file,
    na_values=['', ' ', '-999.25'],
    skiprows=[1],
    )

print(glog_export.columns)
glog_export.head()

# %%
# Check the units in the firs row
unit_check = pd.read_csv(
    geolog_test_file,
    )   

unit_check.head(2)

# %%
# Split the glog_export into two dataframes, one for dips and one for damage picks


# Print the unique values in the 'CATEGORY' column for each dataframe
print("CATEGORY unique values in glog_dips:")
print(glog_export["CATEGORY"].unique())
print("CATEGORY unique values in glog_damage:")
print(glog_export["CATEGORY"].unique())


# %%

glog_export


# %%
# Process the glog_dips dataframe

# Make a new empty float coloumn called 'WCL_Depth'
glog_export['WCL_Depth'] = np.nan
# Make a new empty float column called 'WCL_Feature_Depth'
glog_export['WCL_Feature_Depth'] = np.nan

# Iterate through the rows of the glog_export dataframe
for index, row in glog_export.iterrows():
    # If 'DEPTH_PLANE' is NaN, set 'WCL_Depth' to the value in 'DEPTH'
    if pd.isna(row['AZI_START']):
        print(f"Row {index} has NaN in 'AZI_START', using 'DEPTH' for WCL_Depth and WCL_Feature_Depth")
        glog_export.at[index, 'WCL_Depth'] = row['DEPTH']
        # Set 'WCL_Feature_Depth' to the value in 'DEPTH'
        glog_export.at[index, 'WCL_Feature_Depth'] = row['DEPTH']
    else:
        print(f"Row {index} has value in 'AZI_START', using 'DEPTH_PLANE' for WCL_Depth and 'DEPTH' for WCL_Feature_Depth")
        # If 'DEPTH_PLANE' is not NaN, set 'WCL_Depth' to the value in 'DEPTH_PLANE'
        glog_export.at[index, 'WCL_Depth'] = row['DEPTH']
        # Set 'WCL_Feature_Depth' to the value in 'DEPTH'
        glog_export.at[index, 'WCL_Feature_Depth'] = row['DEPTH_PLANE']

glog_export.head()

# %%
# Make a new column called 'AZIMUTH' that is the average of 'AZI_START' and 'AZI_END'
# Round the azimuth values to the nearest 2 decimal places
glog_export["AZI_START"] = glog_export["AZI_START"].round(1)
glog_export["AZI_END"] = glog_export["AZI_END"].round(1)

# Make a 'AZI_RANGE' column
glog_export['AZI_RANGE'] = glog_export['AZI_START'].astype(str) + '-' + glog_export['AZI_END'].astype(str)
glog_export['AZI_RANGE'] = glog_export['AZI_RANGE'].replace('nan-nan', ' ')

# Infill depth plane column (half way along partial sinuosids, equivlant to the 'Feature Depth' in WCL)
# with the depth column values (depth is the midpoint of the entire sinusoid))
glog_export['DEPTH_PLANE'] = glog_export['DEPTH_PLANE'].fillna(glog_export['DEPTH'])

# Make a dummy Aperture column, if required
glog_export['APERTURE'] = 0

# Subselect the columns needed for the WCL file
wcl_dips = glog_export[[
    'WCL_Feature_Depth', # Feature Depth
    'WCL_Depth', # Depth
    'AZIMUTH', # Azimuth
    'DIP', # Dip
    'APERTURE', # Aperture
    'AZI_RANGE', # Visible Azimuth Range
    'CATEGORY', # Type
    'NOTES', # Notes
]].copy()

# Rename the columns to match the WCL format (names in the row comments)
wcl_dips.rename(columns={
    'WCL_Feature_Depth': 'Feature Depth', # half way down the sinusoid
    'WCL_Depth': 'Depth', # mid point of the entire sinusoid
    'AZIMUTH': 'Azimuth',
    'DIP': 'Dip',
    'APERTURE': 'Aperture',
    'AZI_RANGE': 'Visible Azimuth Ranges',
    'CATEGORY': 'Type',
}, inplace=True)

# Add a row at the top of the dataframe with units [m, m, deg, deg, mm, deg, '']
wcl_dips.loc[-1] = ['m', 'm', 'deg', 'deg', 'mm', 'deg', '', '']
wcl_dips.index = wcl_dips.index + 1  # shifting index
wcl_dips = wcl_dips.sort_index()  # sorting by index

# Export to a new CSV file called dips.csv
wcl_dips.to_csv(r"GLOG_to_WCL__sinusoids_result.csv", index=False)

wcl_dips.head()

# %%
