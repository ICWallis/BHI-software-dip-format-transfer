# convert and damage pick format between geolog and wellcad

# %%
import pandas as pd
import numpy as np


# %%
# Export from GLOG that only contains dips (ie no damage picks)
geolog_test_file = r"test_sinusoids.csv"


# %%
# Read and check the GLOG export file
check = pd.read_csv(
    geolog_test_file,
    )   
check.head()


# %%
# Import dip data that was exported from GLOG without header rows and handling NaN values
GLOG = pd.read_csv(
    geolog_test_file,
    na_values=['', ' ', '-999.25'],
    skiprows=[1],
    )
GLOG.head()


# %%
# Process GLOG data to WCL conventions and export to csv

# Make a WCL Depth column from GLOG.DEPTH_PLANE and GLOG.DEPTH.
# If a sinsuoid is partial (has a start and end azimuth), 
# then GLOG.DEPTH_PLANE == WCL Depth and GLOG.DEPTH == WCL Feature Depth.
# If a sinusoid is complete (has no start and end azimuth), 
# then GLOG.DEPTH_PLANE has no values. 
# We will only generate WCL Depth for import, so GLOG.DEPTH_PLANE NaN values 
# are filled with GLOG.DEPTH values for complete sinusoids and this column used as WCL Depth.
GLOG = GLOG.fillna({'DEPTH_PLANE': GLOG['DEPTH']})
GLOG

# Make a visible azimuth range column in the WCL format
GLOG["AZI_START"] = GLOG["AZI_START"].round(1)
GLOG["AZI_END"] = GLOG["AZI_END"].round(1)
GLOG['AZI_RANGE'] = GLOG['AZI_START'].astype(str) + '-' + GLOG['AZI_END'].astype(str)
GLOG['AZI_RANGE'] = GLOG['AZI_RANGE'].replace('nan-nan', ' ')

# Make a dummy Aperture column
GLOG['APERTURE'] = 0

# Subselect the columns needed for the WCL file
WCL = GLOG[[
    'DEPTH_PLANE', # Equivalent to WCL Depth
    'AZIMUTH', # Azimuth
    'DIP', # Dip
    'APERTURE', # Aperture
    'AZI_RANGE', # Visible Azimuth Range
    'CATEGORY', # Type
    'NOTES', # Notes
]].copy()

# Rename the columns to match the WCL format (names in the row comments)
WCL.rename(columns={
    'DEPTH_PLANE': 'Depth',
    'AZIMUTH': 'Azimuth',
    'DIP': 'Dip',
    'APERTURE': 'Aperture',
    'AZI_RANGE': 'Visible Azimuth Ranges',
    'CATEGORY': 'Type',
}, inplace=True)

# Add a row at the top of the dataframe with units [m, m, deg, deg, mm, deg, '']
WCL.loc[-1] = [
    'm', 
    'deg', 
    'deg', 
    'mm', 
    'deg', 
    '', 
    ''
    ]

WCL.index = WCL.index + 1  # shifting index
WCL = WCL.sort_index()  # sorting by index

# Export to a new CSV file called dips.csv
WCL.to_csv(r"GLOG_to_WCL__sinusoids_result.csv", index=False)

WCL.head()

# %%
