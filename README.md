# bhi-dip-format-transfer

Various borehole image (BHI) log software generates outputs and expects imports with different conventions and formats. This package contains methods to improve interoperability between software packages.

Ideally, all BHI software should follow the [SPWLA Dip Exchange Format](https://www.spwla.org/SPWLAArchived/SPWLA/Chapters_SIGs/SIGs/Borehole_Imaging/Borehole_Imaging.aspx). However, in the author's view the LAS 2.0 format would be more universal than the LAS 3.0 format they recommend.

The initial focus of this project is on Geolog and WellCAD. Get in touch (irene@cubicearth.nz) if you use other software and would like to contribute to this project.

## Installation

```bash
pip install bhi-dip-format-transfer
```

## Usage

```python
import bhi_dip_format_transfer as fn
import pandas as pd

glog = pd.read_csv("geolog_sinusoids.csv")
wcl = fn.glog_to_wcl_sinusoids(glog)
```

Available functions:

- `glog_to_wcl_sinusoids` / `wcl_to_glog_sinusoids` — convert dip picks between Geolog and WellCAD sinusoid conventions.
- `glog_to_wcl_sticks` / `wcl_to_glog_sticks` — convert damage picks (sticks and boxes) between Geolog and WellCAD conventions.
- `process_azimuth_range` — parse a WellCAD "Visible Azimuth Ranges" string into start/end values.
- `crack_tip_positions` / `apply_crack_tip_calculation` — compute the axial and circumferential position of a tensile crack's tips on a cylinder, used when converting damage picks from WellCAD (which does not record tip positions) to Geolog (which does).

See [examples/](examples/) for complete worked examples with test data, including the required input columns and output conventions for each function.

## License

Apache License 2.0. See [LICENSE](LICENSE).
