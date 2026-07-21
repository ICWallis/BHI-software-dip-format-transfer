# convert dip and damage pick format between WCL and GLOG

# %%
import pandas as pd
import numpy as np


# %%
# Import the WCL data and drop the unit row
dips_filename = r"WCL_export.csv"

WCL = pd.read_csv(
    dips_filename, 
    na_values=['', ' ', '-999.25'],
    skiprows=[1],
    )
WCL.head()

# %%
# Process the WCL dips dataframe to match GLOG conventions
# WCL['Visible Azimuth Ranges'] = WCL['Visible Azimuth Ranges'].replace(' ', pd.NA)

# def process_azimuth_range(row):
#     if isinstance(row, str):
#         start, end = row.strip().split('-')
#         return pd.Series({'Visible Azimuth Ranges Start': float(start), 'Visible Azimuth Ranges End': float(end)})
#     else:
#         return pd.Series({'Visible Azimuth Ranges Start': np.nan, 'Visible Azimuth Ranges End': np.nan})

# WCL[['Visible Azimuth Ranges Start', 'Visible Azimuth Ranges End']] = WCL['Visible Azimuth Ranges'].apply(process_azimuth_range)

WCL['Visible Azimuth Ranges'] = WCL['Visible Azimuth Ranges'].replace(' ', pd.NA)

def process_azimuth_range(row):
    if isinstance(row, str):
        parts = row.strip().split('-')
        if len(parts) == 2:
            # Standard format: start-end
            return pd.Series({
                'Azi Range Start': float(parts[0]), 
                'Azi Range End': float(parts[1]),
                # 'Azi Range Start__second': np.nan, 
                # 'Azi Range End__second': np.nan
            })
        elif len(parts) == 4:
            # Extended format: start1-end1-start2-end2
            print(f"Warning: Two visible azimuth ranges: {row}")
            return pd.Series({
                'Azi Range Start': float(parts[0]), 
                'Azi Range End': float(parts[1]),
                # 'Azi Range Start__second': float(parts[2]), 
                # 'Azi Range End__second': float(parts[3])
            })
        else:
            # Handle unexpected format
            print(f"Warning: Unexpected format in row: {row}")
            return pd.Series({
                'Azi Range Start': np.nan, 
                'Azi Range End': np.nan,
                # 'Azi Range Start__second': np.nan, 
                # 'Azi Range End__second': np.nan
            })
    else:
        return pd.Series({
            'Azi Range Start': np.nan, 
            'Azi Range End': np.nan,
            # 'Azi Range Start__second': np.nan, 
            # 'Azi Range End__second': np.nan
        })

WCL[[
    'Azi Range Start', 
    'Azi Range End',
    # 'Azi Range  Start__second',
    # 'Azi Range End__second'
    ]] = WCL['Visible Azimuth Ranges'].apply(process_azimuth_range)

WCL

# %%

WCL['GLG_Depth'] = np.nan
WCL['GLG_Depth_Plane'] = np.nan

# Iterate through the rows of the WCL dataframe
for index, row in WCL.iterrows():
    # If 'Azi Range Start' is NaN, set 'GLG_Depth' to the value in 'DEPTH'
    if pd.isna(row['Azi Range Start']):
        WCL.at[index, 'GLG_Depth'] = row['Depth']
        # Set 'GLG_Depth_Plane' to the value in 'DEPTH'
        WCL.at[index, 'GLG_Depth_Plane'] = None
    else:
        # If 'Azi Range Start' is not NaN, set 'GLG_Depth' to the value in 'DEPTH_PLANE'
        WCL.at[index, 'GLG_Depth'] = row['Feature Depth']  
        # Set 'GLG_Depth_Plane' to the value in 'DEPTH'
        WCL.at[index, 'GLG_Depth_Plane'] = row['Depth']


# %%
# If there is no column called 'NOTES' in the dataframe WCL, create it and fill it with nan values
if 'NOTES' not in WCL.columns:
    WCL['NOTES'] = np.nan

# Rename the columns to match the GLOG format
WCL.rename(columns={
    'GLG_Depth': 'DEPTH', 
    'GLG_Depth_Plane': 'DEPTH_PLANE', 
    'Azimuth': 'AZIMUTH', 
    'Dip': 'DIP', 
    'Type': 'CATEGORY', 
    'Notes': 'NOTES',
    'Azi Range Start': 'AZI_START', 
    'Azi Range End': 'AZI_END',
}, inplace=True)


# Subselect the columns needed for the GLOG file
GLOG = WCL[[
    'DEPTH', 
    'DEPTH_PLANE',
    'AZIMUTH',
    'DIP',
    'AZI_END',
    'AZI_START',
    'CATEGORY',
    'NOTES',
    'Aperture'
]].copy()

# Replace NaN values with -999.25
GLOG.fillna(-999.25, inplace=True)

# %%

GLOG.loc[-1] = ['ft', 'ft', 'deg', 'deg', 'deg', 'deg', '',  '', 'mm']

GLOG.index = GLOG.index + 1  # shifting index

GLOG = GLOG.sort_index()  # sorting by index

GLOG.to_csv(r"WCL_to_GLOG__sinusoids__result.csv", index=False)

GLOG


# %%
