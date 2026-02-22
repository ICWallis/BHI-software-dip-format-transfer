# convert dip and damage pick format between WCL and GLOG

# %%
import pandas as pd
import numpy as np


# %%
# Import the WCL data and drop the unit row
dips_filename = r"to be created.csv"
wcl_dips = pd.read_csv(
    dips_filename, 
    na_values=['', ' ', '-999.25'],
    skiprows=[1],
    )

# %%
wcl_dips.head()

# %%
# Process the WCL dips dataframe to match GLOG conventions
# wcl_dips['Visible Azimuth Ranges'] = wcl_dips['Visible Azimuth Ranges'].replace(' ', pd.NA)

# def process_azimuth_range(row):
#     if isinstance(row, str):
#         start, end = row.strip().split('-')
#         return pd.Series({'Visible Azimuth Ranges Start': float(start), 'Visible Azimuth Ranges End': float(end)})
#     else:
#         return pd.Series({'Visible Azimuth Ranges Start': np.nan, 'Visible Azimuth Ranges End': np.nan})

# wcl_dips[['Visible Azimuth Ranges Start', 'Visible Azimuth Ranges End']] = wcl_dips['Visible Azimuth Ranges'].apply(process_azimuth_range)

wcl_dips['Visible Azimuth Ranges'] = wcl_dips['Visible Azimuth Ranges'].replace(' ', pd.NA)

def process_azimuth_range(row):
    if isinstance(row, str):
        parts = row.strip().split('-')
        if len(parts) == 2:
            # Standard format: start-end
            return pd.Series({
                'Visible Azimuth Ranges Start': float(parts[0]), 
                'Visible Azimuth Ranges End': float(parts[1]),
                # 'Visible Azimuth Ranges Start__second': np.nan, 
                # 'Visible Azimuth Ranges End__second': np.nan
            })
        elif len(parts) == 4:
            # Extended format: start1-end1-start2-end2
            print(f"Warning: Two visible azimuth ranges: {row}")
            return pd.Series({
                'Visible Azimuth Ranges Start': float(parts[0]), 
                'Visible Azimuth Ranges End': float(parts[1]),
                # 'Visible Azimuth Ranges Start__second': float(parts[2]), 
                # 'Visible Azimuth Ranges End__second': float(parts[3])
            })
        else:
            # Handle unexpected format
            print(f"Warning: Unexpected format in row: {row}")
            return pd.Series({
                'Visible Azimuth Ranges Start': np.nan, 
                'Visible Azimuth Ranges End': np.nan,
                # 'Visible Azimuth Ranges Start__second': np.nan, 
                # 'Visible Azimuth Ranges End__second': np.nan
            })
    else:
        return pd.Series({
            'Visible Azimuth Ranges Start': np.nan, 
            'Visible Azimuth Ranges End': np.nan,
            # 'Visible Azimuth Ranges Start__second': np.nan, 
            # 'Visible Azimuth Ranges End__second': np.nan
        })

wcl_dips[[
    'Visible Azimuth Ranges Start', 
    'Visible Azimuth Ranges End',
    # 'Visible Azimuth Ranges Start__second',
    # 'Visible Azimuth Ranges End__second'
    ]] = wcl_dips['Visible Azimuth Ranges'].apply(process_azimuth_range)

# %%
wcl_dips

# %%

wcl_dips['GLG_Depth'] = np.nan
wcl_dips['GLG_Depth_Plane'] = np.nan

# Iterate through the rows of the wcl_dips dataframe
for index, row in wcl_dips.iterrows():
    # If 'Visible Azimuth Ranges Start' is NaN, set 'GLG_Depth' to the value in 'DEPTH'
    if pd.isna(row['Visible Azimuth Ranges Start']):
        wcl_dips.at[index, 'GLG_Depth'] = row['Depth']
        # Set 'GLG_Depth_Plane' to the value in 'DEPTH'
        wcl_dips.at[index, 'GLG_Depth_Plane'] = None
    else:
        # If 'Visible Azimuth Ranges Start' is not NaN, set 'GLG_Depth' to the value in 'DEPTH_PLANE'
        wcl_dips.at[index, 'GLG_Depth'] = row['Feature Depth']  
        # Set 'GLG_Depth_Plane' to the value in 'DEPTH'
        wcl_dips.at[index, 'GLG_Depth_Plane'] = row['Depth']


# %%
# If there is no column called 'NOTES' in the dataframe wcl_dips, create it and fill it with nan values
if 'NOTES' not in wcl_dips.columns:
    wcl_dips['NOTES'] = np.nan

# Rename the columns to match the GLOG format
wcl_dips.rename(columns={
    'GLG_Depth': 'DEPTH', 
    'GLG_Depth_Plane': 'DEPTH_PLANE', 
    'Azimuth': 'AZIMUTH', 
    'Dip': 'DIP', 
    'Aperture': 'Aperture',
    'Visible Azimuth Ranges': 'Visible Azimuth Ranges', 
    'Type': 'CATEGORY', 
    'Notes': 'NOTES',
    'Visible Azimuth Ranges Start': 'AZI_START', 
    'Visible Azimuth Ranges End': 'AZI_END',
}, inplace=True)


# Subselect the columns needed for the GLOG file
glog_dips = wcl_dips[[
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

# %%

glog_dips.columns

# %%

# Add a row at the top of the dataframe with units [ft, ft, deg, deg, mm, deg, '', '']
glog_dips.loc[-1] = ['ft', 'ft', 'deg', 'deg', 'deg', 'deg', '',  '', 'mm']
glog_dips.index = glog_dips.index + 1  # shifting index
glog_dips = glog_dips.sort_index()  # sorting by index

glog_dips.to_csv(r"0__converter__WCL_to_GLOG__dips__result.csv", index=False)

# %%


# %%


# %%


# %%