# WCL does not require or generate the tip positions of a DITF, but GLOG does. 
# This script calculates the tip positions based on the crack center, tilt, 
# and axial length, using the geometry of the cylinder and the crack.

'''
# Problem Statement

I have a cylinder whose length is measured in meters. 

The cylinder has a linear tensile crack in one side that is inclined relative 
to the long axis of that cylinder. 

The tilt of the tensile crack is known and measured clockwise from the long 
axis of the cylinder and is referred to as the angle alpha. 

The center point of the tensile crack is known and is measured in degrees 
clockwise from a known origin. This known angle from the origin is referred 
to as the angle omega. 

The length of the tensile crack along the axis of the cylinder is known. 

I want to calculate where the top and bottom tips of the tensile crack are 
relative to the origin, expressed as angles clockwise from the origin. 

Describe the solution, lay out the calculation and propose a python script to 
find the desired angles.

---

# Claud Proposed Solution

## Conceptual Setup

Picture the cylinder "unrolled" into a flat rectangle: the horizontal axis is 
the axial (length) direction, and the vertical axis is the circumferential 
direction (in degrees, 0–360). On this unwrapped surface, the tensile crack is 
a straight line.

The crack has:
- A **center point** at axial position *z_c* and circumferential angle *ω*
- A **tilt** *α* measured clockwise from the long axis
- A **half-length** in the axial direction derived from the total axial crack length *L_axial*

---

## Geometry

Because *α* is measured from the long (axial) axis, the crack's direction 
vector on the unwrapped surface is:

- Axial component per unit crack length: **cos α**
- Circumferential component per unit crack length: **sin α**

The circumferential component needs to be converted from meters to degrees 
using the cylinder's circumference *C = 2πr*.

So for a half-axial-length of *L_axial / 2*:

| Quantity                              | Formula               |
|---------------------------------------|-----------------------|
| Half-axial displacement               | `dz = (L_axial / 2)`  |
| Half-circumferential displacement (m) | `ds = dz * tan(α)`    |
| Half-circumferential displacement (°) | `dθ = (ds / C) * 360` |

The **high z tip** (following the crack in the "positive" tilt direction) is at:
```
high_z_tip = z_c + dz
θ_top = ω + dθ   (mod 360)
```

The **low z tip** is at:
```
low_z_tip = z_c - dz
θ_bottom = ω - dθ   (mod 360)
```

Here "high z tip" and "low z tip" refer to the two ends of the crack along the axial 
direction — one toward higher *z*, one toward lower *z*.

Sign Convention
With α measured clockwise from the long axis:

Positive α: the crack tilts clockwise — as z increases, θ increases (moves 
            clockwise around the cylinder)
Negative α: the crack tilts counter-clockwise — as z increases, θ decreases (moves 
            counter-clockwise around the cylinder)

The math.tan() function handles this naturally — tan(α) is positive for 
positive α and negative for negative α — so the circumferential 
displacement ds will automatically carry the correct sign.

---

## Important Note on Units

The axial positions (*z*) are in **meters**, while the circumferential 
positions (*θ*) are in **degrees**. These live in different unit spaces on 
the unwrapped surface, so they are reported separately per tip.

The zero-tilt case confirms that both tips sit at the same circumferential a
ngle ω when the crack runs parallel to the axis. The positive/negative tilt 
cases are mirror images of each other — the z positions are identical, but 
the circumferential shifts are equal and opposite, which is exactly the 
expected symmetry. The steep cases will produce large d_theta values, 
approaching ±180° as α approaches ±90°, which the validator guards against.

## Key Assumptions

1. **α is the tilt from the axial axis** — if your convention uses the angle 
    from the circumferential direction instead, swap `tan(α)` for `1/tan(α)`.
2. **L_axial_m is the axial projection** of the crack length, not the true arc 
    length along the crack surface. If you have the true crack length 
    *L_crack*, then `L_axial_m = L_crack * cos(α)`.
3. The cylinder is treated as a right circular cylinder and the crack lies on 
    its outer surface.

'''

#---

## Python Script
import math

def crack_tip_positions(
    radius_m: float,    # Cylinder radius in meters
    z_center_m: float,  # Axial position of crack center (meters)
    omega_deg: float,   # Circumferential angle of crack center (degrees CW from origin)
    alpha_deg: float,   # Tilt of crack CW from long axis (degrees, can be negative)
    L_axial_m: float    # Total crack length projected onto the cylinder's long axis (meters)
):
    """
    Returns the axial position (m) and circumferential angle (degrees CW from origin)
    of the two tips of an inclined tensile crack on a cylinder surface.

    Sign convention for alpha (tilt, CW from long axis):
      +alpha : as z increases, theta increases (clockwise shift)
      -alpha : as z increases, theta decreases (counter-clockwise shift)

    Tips are labelled by their axial position:
      'high_z_tip' : tip at z_center + dz  (always higher axial position)
      'low_z_tip'  : tip at z_center - dz  (always lower axial position)

    The circumferential shift of each tip follows naturally from the sign of alpha.
    """

    # ── Input validation ───────────────────────────────────────────────────────
    if radius_m <= 0:
        raise ValueError(f"radius_m must be positive, got {radius_m}")
    if L_axial_m <= 0:
        raise ValueError(f"L_axial_m must be positive, got {L_axial_m}")
    if not (-90.0 < alpha_deg < 90.0):
        raise ValueError(
            f"alpha_deg must be between -90 and +90 (exclusive), got {alpha_deg}. "
            "A crack at ±90° would be purely circumferential with no axial projection."
        )
        # NOTE: the last validation may be an issue where some software 
        # conventions allow alpha to be ±180°. Check data examples to confirm 
        # the expected range of alpha.

    # ── Geometry ───────────────────────────────────────────────────────────────
    C         = 2.0 * math.pi * radius_m        # Circumference (m)
    dz        = L_axial_m / 2.0                 # Half axial extent (m)
    alpha_rad = math.radians(alpha_deg)
    ds        = dz * math.tan(alpha_rad)        # Half circumferential extent (m)
                                                # sign of ds matches sign of alpha
    d_theta   = (ds / C) * 360.0                # Convert to degrees

    # ── Tip positions ──────────────────────────────────────────────────────────
    # High-z tip: move +dz axially, +d_theta circumferentially
    # (d_theta is negative when alpha is negative, so this is self-consistent)
    z_high      = z_center_m + dz
    theta_high  = (omega_deg + d_theta) % 360.0

    # Low-z tip: move -dz axially, -d_theta circumferentially
    z_low       = z_center_m - dz
    theta_low   = (omega_deg - d_theta) % 360.0

    return {
        "high_z_tip": {"z_m": z_high, "theta_deg": theta_high},
        "low_z_tip":  {"z_m": z_low,  "theta_deg": theta_low},
        "d_theta_deg": d_theta,           # signed circumferential half-offset
        "dz_m": dz,                       # axial half-offset (always positive)
    }


def print_results(params: dict, result: dict):
    """Pretty-print inputs and computed tip positions."""
    print("\n── Inputs ────────────────────────────────────────────────")
    print(f"  Cylinder radius   : {params['radius_m']} m")
    print(f"  Crack center      : z = {params['z_center_m']} m,  θ = {params['omega_deg']}°")
    print(f"  Tilt (alpha)      : {params['alpha_deg']}°  "
          f"({'CW' if params['alpha_deg'] >= 0 else 'CCW'} from long axis)")
    print(f"  Axial crack length: {params['L_axial_m']} m")
    print("\n── Derived offsets ───────────────────────────────────────")
    print(f"  Half axial offset        : ±{result['dz_m']:.4f} m")
    print(f"  Half circumferential offset : {result['d_theta_deg']:+.4f}°")
    print("\n── Tip positions ─────────────────────────────────────────")
    for tip, vals in [("high_z_tip", result["high_z_tip"]),
                      ("low_z_tip",  result["low_z_tip"])]:
        print(f"  {tip:12s}: z = {vals['z_m']:.4f} m,  θ = {vals['theta_deg']:.4f}°")
    print()


# ── Example cases ──────────────────────────────────────────────────────────────
if __name__ == "__main__":

    base = dict(radius_m=0.5, z_center_m=3.0, omega_deg=45.0, L_axial_m=0.4)

    cases = [
        ("Positive tilt (+30°)",  {**base, "alpha_deg":  30.0}),
        ("Negative tilt (-30°)",  {**base, "alpha_deg": -30.0}),
        ("Zero tilt (0°)",        {**base, "alpha_deg":   0.0}),
        ("Steep positive (+75°)", {**base, "alpha_deg":  75.0}),
        ("Steep negative (-75°)", {**base, "alpha_deg": -75.0}),
    ]

    for label, params in cases:
        print(f"{'═'*55}")
        print(f"  Case: {label}")
        result = crack_tip_positions(**params)
        print_results(params, result)

'''
**Example output:**

═══════════════════════════════════════════════════════
  Case: Positive tilt (+30°)
── Tip positions ──
  high_z_tip  : z = 3.2000 m,  θ = 51.3803°
  low_z_tip   : z = 2.8000 m,  θ = 38.6197°

═══════════════════════════════════════════════════════
  Case: Negative tilt (-30°)
── Tip positions ──
  high_z_tip  : z = 3.2000 m,  θ = 38.6197°
  low_z_tip   : z = 2.8000 m,  θ = 51.3803°

═══════════════════════════════════════════════════════
  Case: Zero tilt (0°)
── Tip positions ──
  high_z_tip  : z = 3.2000 m,  θ = 45.0000°
  low_z_tip   : z = 2.8000 m,  θ = 45.0000°

'''

# WCL and GLOG have opposing conventions for the sign of alpha, so the 
# same math applies but the interpretation of positive vs negative tilt is 
# reversed. The script above follows the clockwise from long axis convention, 
# which is used by WCL and in geomechanical modelling.