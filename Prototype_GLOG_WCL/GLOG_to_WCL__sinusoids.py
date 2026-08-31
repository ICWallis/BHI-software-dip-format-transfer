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
# # Process GLOG data to WCL conventions and export to csv

# ###### Function starts here #######
# # Units are not included inside the function. 
# # User will need to remove this row and add it back into the result


# # Make a WCL Depth column from GLOG.DEPTH_PLANE and GLOG.DEPTH.
# # If a sinsuoid is partial (ie has a start and end azimuth), 
# # then GLOG.DEPTH_PLANE == WCL Depth and GLOG.DEPTH == WCL Feature Depth.
# # If a sinusoid is complete (has no start and end azimuth), 
# # then GLOG.DEPTH_PLANE has no values amd GLOG.DEPTH == WCL Depth and WCL Feature Depth.
# # In this method, GLOG.DEPTH_PLANE NaN values are filled with GLOG.DEPTH values 
# # when there is complete sinusoids and the infilled column of GLOG.DEPTH_PLANE 
# # is used as WCL Depth. We will only generate WCL Depth for import into WCL because the software will
# # calculate the feature depth depending on CALA.

# # Infill GLOG.DEPTH_PLANE with GLOG.DEPTH values where GLOG.DEPTH_PLANE is NaN
# GLOG = GLOG.fillna({'DEPTH_PLANE': GLOG['DEPTH']})
# GLOG

# # Make a visible azimuth range column in the WCL format
# GLOG["AZI_START"] = GLOG["AZI_START"].round(1)
# GLOG["AZI_END"] = GLOG["AZI_END"].round(1)
# GLOG['AZI_RANGE'] = GLOG['AZI_START'].astype(str) + '-' + GLOG['AZI_END'].astype(str)
# GLOG['AZI_RANGE'] = GLOG['AZI_RANGE'].replace('nan-nan', ' ')

# # Make a dummy Aperture column
# GLOG['APERTURE'] = 0

# # Subselect the columns needed for the WCL file
# WCL = GLOG[[
#     'DEPTH_PLANE', # Equivalent to WCL Depth
#     'AZIMUTH', # Azimuth
#     'DIP', # Dip
#     'APERTURE', # Aperture
#     'AZI_RANGE', # Visible Azimuth Range
#     'CATEGORY', # Type
#     'NOTES', # Notes
# ]].copy()

# # Rename the columns to match the WCL format (names in the row comments)
# WCL.rename(columns={
#     'DEPTH_PLANE': 'Depth',
#     'AZIMUTH': 'Azimuth',
#     'DIP': 'Dip',
#     'APERTURE': 'Aperture',
#     'AZI_RANGE': 'Visible Azimuth Ranges',
#     'CATEGORY': 'Type',
# }, inplace=True)


# ###### Function ends here #######




# %%

def glog_to_wcl_sinusoids(glog: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Convert sinusoid dip picks from Geolog (GLOG) convention to WellCAD (WCL) convention.

    Args:
        glog (pd.DataFrame): Input Geolog dataframe. Required columns are:
            - DEPTH_PLANE
            - DEPTH
            - AZI_START
            - AZI_END
            - AZIMUTH
            - DIP
            - CATEGORY
            - NOTES

    Kwargs:
        round_decimals (int, optional): Number of decimals used when rounding
            AZI_START and AZI_END before building the visible azimuth range.
            Defaults to 1.
        aperture_value (int | float, optional): Constant value assigned to the
            output Aperture column. Defaults to 0.
        empty_azi_range_value (str, optional): Replacement value for rows where
            both AZI_START and AZI_END are missing (rendered as "nan-nan").
            Defaults to a single blank space " ".
        azi_range_separator (str, optional): Separator used to combine AZI_START
            and AZI_END into the WCL visible azimuth range. Defaults to "-".

    Returns:
        pd.DataFrame: WCL-formatted dataframe with columns:
            Depth, Azimuth, Dip, Aperture, Visible Azimuth Ranges, Type, NOTES.

    Conventions:
        - Unit rows are intentionally not handled here. Add/remove units outside
          this function as needed by import/export workflows.
        - WCL Depth is derived from Geolog DEPTH_PLANE, with missing DEPTH_PLANE
          infilled from DEPTH.
        - Partial sinusoids (start/end azimuth provided):
          DEPTH_PLANE maps to WCL Depth and DEPTH maps to WCL Feature Depth.
        - Complete sinusoids (no start/end azimuth):
          DEPTH_PLANE is typically empty; DEPTH is used as both WCL Depth and
          WCL Feature Depth after infill.
        - Only WCL Depth is produced here because WCL computes feature depth
          based on CALA during interpretation.
    """
    round_decimals = kwargs.get('round_decimals', 1)
    aperture_value = kwargs.get('aperture_value', 0)
    empty_azi_range_value = kwargs.get('empty_azi_range_value', ' ')
    azi_range_separator = kwargs.get('azi_range_separator', '-')

    glog_processed = glog.copy()

    # Infill DEPTH_PLANE for complete sinusoids where only DEPTH is available.
    glog_processed = glog_processed.fillna({'DEPTH_PLANE': glog_processed['DEPTH']})

    # Build WCL visible azimuth range from rounded start/end values.
    glog_processed['AZI_START'] = glog_processed['AZI_START'].round(round_decimals)
    glog_processed['AZI_END'] = glog_processed['AZI_END'].round(round_decimals)
    glog_processed['AZI_RANGE'] = (
        glog_processed['AZI_START'].astype(str)
        + azi_range_separator
        + glog_processed['AZI_END'].astype(str)
    )
    glog_processed['AZI_RANGE'] = glog_processed['AZI_RANGE'].replace(
        'nan' + azi_range_separator + 'nan',
        empty_azi_range_value,
    )

    # Aperture is kept as a constant placeholder for this transfer format.
    glog_processed['APERTURE'] = aperture_value

    wcl = glog_processed[[
        'DEPTH_PLANE',
        'AZIMUTH',
        'DIP',
        'APERTURE',
        'AZI_RANGE',
        'CATEGORY',
        'NOTES',
    ]].copy()

    wcl.rename(columns={
        'DEPTH_PLANE': 'Depth',
        'AZIMUTH': 'Azimuth',
        'DIP': 'Dip',
        'APERTURE': 'Aperture',
        'AZI_RANGE': 'Visible Azimuth Ranges',
        'CATEGORY': 'Type',
    }, inplace=True)

    return wcl


# Separate use case for the new function (original workflow above is unchanged).
WCL = glog_to_wcl_sinusoids(GLOG)
WCL.head()

# %%

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