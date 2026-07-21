# convert dip and damage pick format between WCL and GLOG

# %%
from os import replace

import pandas as pd
import numpy as np
import math

# %%
# Import the WCL data and drop the unit row

damage_filename = r"GLOG_to_WCL__sticks_result.csv"

WCL = pd.read_csv(
    damage_filename,
    na_values=['', ' ', '-999.25'],
    skiprows=[1],
    )

WCL

# %%
# Process the WCL damage dataframe to match GLOG conventions

# Set WCL.Tilt values of 0 to NaN
WCL['Tilt'] = WCL['Tilt'].replace(0, np.nan)

# Invert the sign of the Tilt column to match GLOG convention
WCL['GLOG Tilt'] = WCL['Tilt'] * -1

# Need to export the caliper log and calculate the radius at the depth of each feature. 
WCL['Radius'] = 215.9 / 2 / 1000    # Placeholder value in meters 
                                    # replace with actual radius
                                    # It's CALA in mm / 2 for radius and converted to meters
                                    # Method assumes meters, so will need to handle units

WCL.head()

# %%
# Endpoint calculation 

def crack_tip_positions(
    radius_m: float,    # Cylinder radius in meters
    z_center_m: float,  # Axial (depth) position of crack center (meters)
    theta_deg: float,   # Circumferential angle of crack center (degrees CW from origin)
    omega_deg: float,   # Tilt of crack CW from long axis (degrees, can be negative)
    L_axial_m: float    # Total crack length projected onto the cylinder's long axis (meters)
):
    """
    Returns the axial position (m) and circumferential angle (degrees CW from origin)
    of the two tips of an inclined tensile crack on a cylinder surface.

    Sign convention for omega (tilt, CW from long axis):
      +omega : as z increases, theta increases (clockwise shift)
      -omega : as z increases, theta decreases (counter-clockwise shift)

    Tips are labelled by their axial position:
      'high_z_tip' : tip at z_center + dz  (always higher axial position)
      'low_z_tip'  : tip at z_center - dz  (always lower axial position)

    The circumferential shift of each tip follows naturally from the sign of omega.
    """

    # ── Input validation ───────────────────────────────────────────────────────
    if radius_m <= 0:
        raise ValueError(f"radius_m must be positive, got {radius_m}")
    if L_axial_m <= 0:
        raise ValueError(f"L_axial_m must be positive, got {L_axial_m}")
    if not (-90.0 < omega_deg < 90.0):
        raise ValueError(
            f"omega_deg must be between -90 and +90 (exclusive), got {omega_deg}. "
            "A crack at ±90° would be purely circumferential with no axial projection."
        )
        # NOTE: the last validation may be an issue where some software 
        # conventions allow omega to be ±180°. Check data examples to confirm 
        # the expected range of omega.

    # ── Geometry ───────────────────────────────────────────────────────────────
    C         = 2.0 * math.pi * radius_m        # Circumference (m)
    dz        = L_axial_m / 2.0                 # Half axial extent (m)
    omega_rad = math.radians(omega_deg)
    ds        = dz * math.tan(omega_rad)        # Half circumferential extent (m)
                                                # sign of ds matches sign of omega
    d_theta   = (ds / C) * 360.0                # Convert to degrees

    # ── Tip positions ──────────────────────────────────────────────────────────
    # High-z tip: move +dz axially, +d_theta circumferentially
    # (d_theta is negative when alpha is negative, so this is self-consistent)
    z_high      = z_center_m + dz
    theta_high  = (theta_deg + d_theta) % 360.0

    # Low-z tip: move -dz axially, -d_theta circumferentially
    z_low       = z_center_m - dz
    theta_low   = (theta_deg - d_theta) % 360.0

    return {
        "high_z_tip": {"z_m": z_high, "theta_deg": theta_high},
        "low_z_tip":  {"z_m": z_low,  "theta_deg": theta_low},
        "d_theta_deg": d_theta,           # signed circumferential half-offset
        "dz_m": dz,                       # axial half-offset (always positive)
    }


# %%
# Apply the crack tip calculation to each row in the dataframe
def apply_crack_tip_calculation(row):
    # Test for cases where endpoints are not calculated (e.g., missing Tilt or Length)
    if pd.isna(row['Tilt']) or pd.isna(row['Length']):
        return pd.Series({
            'high_z_tip_z_m': np.nan,
            'high_z_tip_theta_deg': np.nan,
            'low_z_tip_z_m': np.nan,
            'low_z_tip_theta_deg': np.nan,
            'd_theta_deg': np.nan,
            'dz_m': np.nan,
        })
    else:
        result = crack_tip_positions(
            radius_m=row['Radius'],
            z_center_m=row['Depth'],
            theta_deg=row['Azimuth'],
            omega_deg=row['Tilt'],
            L_axial_m=row['Length'],
        )
        return pd.Series({
            'high_z_tip_z_m': result['high_z_tip']['z_m'],
            'high_z_tip_theta_deg': result['high_z_tip']['theta_deg'],
            'low_z_tip_z_m': result['low_z_tip']['z_m'],
            'low_z_tip_theta_deg': result['low_z_tip']['theta_deg'],
            'd_theta_deg': result['d_theta_deg'],
            'dz_m': result['dz_m'],
        })

tip_positions_df = WCL.apply(apply_crack_tip_calculation, axis=1)
WCL = pd.concat([WCL, tip_positions_df], axis=1)
WCL.head()

# %%
# drop the Tilt column
WCL.drop(columns=['Tilt'], inplace=True)

# # Replace NAN values with -999.25
WCL.fillna(-999.25, inplace=True)
WCL

# %%
WCL.rename(columns={
    'Depth': 'DEPTH', 
    'Azimuth': 'AZIMUTH', 
    'high_z_tip_theta_deg': 'AZI_END',
    'low_z_tip_theta_deg': 'AZI_START',
    'GLOG Tilt': 'TILT', 
    'Length': 'HEIGHT',
    'Opening': 'AWIDTH', 
    'Type': 'CATEGORY', 
    'Notes': 'NOTES',
}, inplace=True)

# Make a new dataframe that only contains the columns that were renamed above
GLOG = WCL[[
    'DEPTH', 
    'AZIMUTH', 
    'AZI_END',
    'AZI_START',
    'TILT', 
    'HEIGHT',
    'AWIDTH', 
    'CATEGORY', 
    'NOTES',
]].copy()



GLOG.columns


# %%
# Add a row at the top of the dataframe with units for each column, then export to CSV
GLOG.loc[-1] = ['m', 'deg', 'deg', 'deg', 'deg', 'm', 'deg', '', '',]
GLOG.index = GLOG.index + 1  # shifting index
GLOG = GLOG.sort_index()  # sorting by index

GLOG.to_csv(r"WCL_to_GLOG__sticks__result.csv", index=False)
GLOG

# %%


# %%


# %%


# %%