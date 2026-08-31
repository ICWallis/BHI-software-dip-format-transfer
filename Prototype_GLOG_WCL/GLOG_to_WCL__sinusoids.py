# convert and damage pick format between geolog and wellcad

# %%
import pandas as pd


# %%
# Import the GLOG dip file to be converted to WCL format
geolog_test_file = r"test_sinusoids.csv"

GLOG = pd.read_csv(
    geolog_test_file,
    na_values=['', ' ', '-999.25'], # handles expected NaN values
    skiprows=[1], # skip unit row
    )
GLOG.head()

# Units are currently handled manually in this method. They are first stripped
# from the import file and then manually defined and added to the WCL export file. 


# %%
# Process GLOG data to WCL conventions and export to csv

# Make a WCL Depth column from GLOG.DEPTH_PLANE and GLOG.DEPTH.
# If a sinsuoid is partial (ie has a start and end azimuth), 
# then GLOG.DEPTH_PLANE == WCL Depth and GLOG.DEPTH == WCL Feature Depth.
# If a sinusoid is complete (has no start and end azimuth), 
# then GLOG.DEPTH_PLANE has no values amd GLOG.DEPTH == WCL Depth and WCL Feature Depth.
# In this method, GLOG.DEPTH_PLANE NaN values are filled with GLOG.DEPTH values 
# when there is complete sinusoids and the infilled column of GLOG.DEPTH_PLANE 
# is used as WCL Depth. We will only generate WCL Depth for import into WCL because the software will
# calculate the feature depth depending on CALA.

# Infill GLOG.DEPTH_PLANE with GLOG.DEPTH values where GLOG.DEPTH_PLANE is NaN
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
