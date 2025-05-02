# py_mesa_interpolation

```py_mesa_interpolation``` is a tool that is designed to be used with [py_mesa_reader](https://github.com/wmwolf/py_mesa_reader) and [MESA stellar astrophysics program](https://docs.mesastar.org/en/latest/) to create isochrone plots over multiple tracks.

### functions:
```
load_models(mesa_data) # takes a 2d array of mesa data
plot_isochrone(desired_age) # plots an isochrone of a desired year over a hr diagram
plot_evolutionary_tracks() # plots a colorful hr diagram
show() # shows the plot that has been created
```
<strong>Optional flags for ```plot_isochrone()```</strong><br>

defaults are shown:
- change color of isochrone track: ```track_color='red'```
- change number of points in the graph: ```resolution=100```
- change % difference from desired age allowed: ```tolerance=10```
- show hr tracks behind isochrones: ```show_hr=True```


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
plotter.plot_isochrone(1e9, track_color='green', tolerance=5)

# Show plot
plotter.show()
```

### Interpolation algorithm

To solve the non-monoticity problem, we must find a polynomial function:<br>
$P:P(t) = (x(t), y(t)) \textrm{ where } x(t) \textrm{ is log temperature, } y(t) \textrm{ is log luminocity, and }$ <br>
$t \textrm{ is a time parameter where } t = [0, ..., n-1]$

$n = \lvert \textrm{log effective temperature} \rvert = \lvert \textrm{log luminocity} \rvert = \lvert t \rvert$

$\Rightarrow \exists \textrm{ cubic spline functions } x_{teff}(t) \textrm{ and } y_{logL}(t) : P_{isochrone} = (x_{teff}(t), y_{logL}(t))$


















