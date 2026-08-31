# bhi-dip-format-transfer

Borehole image (BHI) log software packages generate outputs and expect imports with different conventions and formats. This is a barrier to collaboration and to using existing data in a new software package. Ideally, all BHI software should follow the [SPWLA Dip Exchange Format](https://www.spwla.org/SPWLAArchived/SPWLA/Chapters_SIGs/SIGs/Borehole_Imaging/Borehole_Imaging.aspx). But a single universal standard is a lofty goal and will not resolve issues with legacy data. 

The `bhi-dip-format-transfer` package converts the sinusoid (fractures, beds etc.) and stick (drilling-induced damage) format between ALT WellCAD and Aspen Geolog. Get in touch (irene@cubicearth.nz) if you use other software and would like to contribute a conversion method to this project.


![Standards](https://imgs.xkcd.com/comics/standards.png)

*([xkcd.com/927](https://xkcd.com/927))*


## Installation

```bash
pip install bhi-dip-format-transfer
```

## Usage

```python
import bhi_dip_format_transfer as dt
```

See [examples/](examples/) for complete worked examples with test data, including the required input columns and output conventions for each function. Note unit handling and that CALA must be converted to radius in meters.

## Available Functions

- `glog_to_wcl_sinusoids` / `wcl_to_glog_sinusoids` — convert dip picks (sinusoids) between Geolog and WellCAD conventions.
- `glog_to_wcl_sticks` / `wcl_to_glog_sticks` — convert drilling-induced damage picks (sticks and boxes) between Geolog and WellCAD conventions.
- `process_azimuth_range` — parse a WellCAD "Visible Azimuth Ranges" string into start/end values.
- `crack_tip_positions` / `apply_crack_tip_calculation` — compute the axial and circumferential position of a tensile crack's tips on a cylinder, used when converting damage picks from WellCAD (which does not record tip positions) to Geolog (which does).


## License

Apache License 2.0. See [LICENSE](LICENSE).
