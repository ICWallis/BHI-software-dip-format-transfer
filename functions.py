import pandas as pd
import numpy as np

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

def wcl_to_glog_sinusoids(wcl: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Convert sinusoid dip picks from WellCAD (WCL) convention to Geolog (GLOG) convention.

    Args:
        wcl (pd.DataFrame): Input WellCAD dataframe. Required columns are:
            - Depth
            - Feature Depth
            - Azimuth
            - Dip
            - Type
            - Visible Azimuth Ranges
            - Aperture

    Kwargs:
        empty_visible_range_value (str, optional): Value treated as empty in
            the input Visible Azimuth Ranges column before parsing. Defaults
            to a single blank space " ".
        nan_fill_value (int | float, optional): Value used to replace NaN in
            the final GLOG output. Defaults to -999.25.

    Returns:
        pd.DataFrame: GLOG-formatted dataframe with columns:
            DEPTH, DEPTH_PLANE, AZIMUTH, DIP, AZI_END, AZI_START,
            CATEGORY, NOTES, Aperture.

    Conventions:
        - Unit rows are intentionally not handled here. Add/remove units
          outside this function as needed by import/export workflows.
        - Visible Azimuth Ranges values are parsed into Azi Range Start and
          Azi Range End using the same parsing behavior as the script-level
          process_azimuth_range helper.
        - If Azi Range Start is missing, the sinusoid is treated as complete:
          DEPTH is assigned from Depth and DEPTH_PLANE is left as missing.
        - If Azi Range Start is present, the sinusoid is treated as partial:
          DEPTH is assigned from Feature Depth and DEPTH_PLANE from Depth.
        - If NOTES does not exist, it is created and filled with NaN before
          renaming/subselection.
        - Final NaN values are replaced with the configured nan_fill_value.
        - Aperture is included from the WCL input but is not handled in GLOG.
          in the same way as WCL. This may need to be deleted before importing
          the data into GLOG. 
    """
    empty_visible_range_value = kwargs.get('empty_visible_range_value', ' ')
    nan_fill_value = kwargs.get('nan_fill_value', -999.25)

    wcl_processed = wcl.copy()
    wcl_processed['Visible Azimuth Ranges'] = wcl_processed[
        'Visible Azimuth Ranges'
    ].replace(empty_visible_range_value, pd.NA)

    wcl_processed[[
        'Azi Range Start',
        'Azi Range End',
    ]] = wcl_processed['Visible Azimuth Ranges'].apply(process_azimuth_range)

    wcl_processed['GLG_Depth'] = np.nan
    wcl_processed['GLG_Depth_Plane'] = np.nan

    # Keep row-wise logic aligned with the original transformation block.
    for index, row in wcl_processed.iterrows():
        if pd.isna(row['Azi Range Start']):
            wcl_processed.at[index, 'GLG_Depth'] = row['Depth']
            wcl_processed.at[index, 'GLG_Depth_Plane'] = None
        else:
            wcl_processed.at[index, 'GLG_Depth'] = row['Feature Depth']
            wcl_processed.at[index, 'GLG_Depth_Plane'] = row['Depth']

    if 'NOTES' not in wcl_processed.columns:
        wcl_processed['NOTES'] = np.nan

    wcl_processed.rename(columns={
        'GLG_Depth': 'DEPTH',
        'GLG_Depth_Plane': 'DEPTH_PLANE',
        'Azimuth': 'AZIMUTH',
        'Dip': 'DIP',
        'Type': 'CATEGORY',
        'Notes': 'NOTES',
        'Azi Range Start': 'AZI_START',
        'Azi Range End': 'AZI_END',
    }, inplace=True)

    glog = wcl_processed[[
        'DEPTH',
        'DEPTH_PLANE',
        'AZIMUTH',
        'DIP',
        'AZI_END',
        'AZI_START',
        'CATEGORY',
        'NOTES',
        'Aperture',
    ]].copy()

    glog.fillna(nan_fill_value, inplace=True)

    return glog