# py_mesa_interpolation

```py_mesa_interpolation``` is a tool that is designed to be used with [py_mesa_reader](https://github.com/wmwolf/py_mesa_reader) and [MESA stellar astrophysics program](https://docs.mesastar.org/en/latest/) to create isochrone plots over multiple tracks.

### functions:
```
load_models(mesa_data) # takes a 2d array of mesa data
plot_isochrone(desired_age, color) # plots an isochrone of a desired year over a hr diagram
plot_evolutionary_tracks() # plots a colorful hr diagram
show() # shows the plot that has been created
```

### Sample usage
```
from mesa_reader import MesaData
from isoFns import isoFns

# Initialize and load data
plotter = isoFns()
md = []
name = ["0.5mass", "0.7mass", "0.9mass", "1mass", "1.2mass", "1.4mass", 
        "1.6mass", "1.8mass", "2mass", "2.2mass", "2.4mass", "2.6mass", 
        "3mass", "4mass", "5mass", "6mass", "7mass", "8mass", "9mass", "10mass"]

for n in name:
    md.append(MesaData('path/to/mesa/data/' + n + '.data'))

plotter.load_models(md)

# Add isochrones
plotter.plot_isochrone(1e9, 'green')

# Show plot
plotter.show()
```
