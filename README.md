# mesa_isochrone_constructor

`mesa_isochrone_constructor` is a Python library for generating stellar isochrones from multiple MESA evolutionary tracks. It is designed to work alongside MESA and py_mesa_reader, allowing users to construct smooth isochrones, visualize evolutionary tracks, and export model data in multiple formats.

## Features

- Generate isochrones from collections of MESA stellar evolution tracks
- Plot evolutionary tracks on HR diagrams
- Interpolate stellar properties at arbitrary ages
- Export datasets to JSON, CSV, Parquet, and FITS formats
- Multiple interpolation methods:
  - Linear
  - PCHIP (default)
  - Cubic Spline
  - Akima
  - make_interp_spline
- Interactive mass inspection using mplcursors

## Dependencies

- py_mesa_reader
- numpy
- pandas
- matplotlib
- scipy
- astropy
- pyarrow
- mplcursors

Install with:

```bash
pip install numpy pandas matplotlib scipy astropy pyarrow mplcursors
```

## Installation

```bash
git clone https://github.com/Greg-Saul/mesa_isochrone_constructor.git
cd mesa_isochrone_constructor/src
```

## Basic Usage

### Load MESA Models

```python
from mesa_isochrone import mesa_isochrone

plotter = mesa_isochrone()
plotter.load_models(model_data)
```

`model_data` should be a list of py_mesa_reader `MesaData` objects.

### Export Data

```python
plotter.export("models", file_type="json")
```

Supported formats:

- `"json"`
- `"csv"`
- `"parquet"`
- `"fits"`

### Plot an Isochrone

```python
plotter.plot_isochrone(
    filename="models.json",
    desired_age=1e9
)
```

### Plot Evolutionary Tracks

```python
plotter.plot_evolutionary_tracks()
```

### Display Plot

```python
plotter.show()
```

### Save Plot

```python
plotter.save(image_name="my_isochrone")
```

## plot_isochrone Parameters

| Parameter | Default | Description |
|------------|----------|-------------|
| track_color | `"red"` | Isochrone color |
| resolution | `10000` | Number of interpolated points |
| tolerance | `1` | Allowed age mismatch (%) |
| show_hr | `False` | Plot evolutionary tracks behind isochrone |
| show_points | `False` | Display original interpolation points |
| interpolation_method | `"PCHIP"` | Smoothing method |
| clean | `False` | Produce minimal image without labels |
| reinterpolate | `True` | Interpolate along stellar tracks to desired age |
| legend_type | `1` | Legend formatting style |

Supported interpolation methods:

```python
interpolation_method="linear"
interpolation_method="PCHIP"
interpolation_method="cubic_spline"
interpolation_method="akima"
interpolation_method="make_interp_spline"
```

## Reinterpolation Algorithm

For each stellar track, the code locates the two evolutionary points that bracket the desired age:

```math
age_0 \le age_{desired} \le age_1
```

The corresponding temperature and luminosity values are then linearly interpolated:

```math
w = \frac{age_{desired} - age_0}{age_1 - age_0}
```

```math
T = T_0 + w(T_1 - T_0)
```

```math
L = L_0 + w(L_1 - L_0)
```

This produces a set of temperature-luminosity pairs representing stars of different masses at a common age.

A second interpolation step is then applied across mass tracks to construct a smooth isochrone curve in HR space.

## Example Workflow

```python
plotter = mesa_isochrone()

plotter.load_models(model_data)

plotter.export("tracks", file_type="json")

plotter.plot_isochrone(
    "tracks.json",
    desired_age=5e9,
    interpolation_method="PCHIP",
    show_hr=True
)

plotter.show()
```

## License

MIT License
