# py_mesa_interpolation

```py_mesa_interpolation``` is a tool that is designed to be used with [py_mesa_reader](https://github.com/wmwolf/py_mesa_reader) and [MESA stellar astrophysics program](https://docs.mesastar.org/en/latest/) to create isochrone plots over multiple tracks.

### dependencies
- py_mesa_reader
- pandas
- numpy
- matplotlib

### functions:
```
load_models(mesa_data) # takes a 2d array of mesa data
md_to_csv(foldername) # turns relevant mesa data objects into csv files inside a folder
extract_csv(foldername) # loads the csv data from foldername to be used in isochrone generation
plot_isochrone(desired_age) # plots an isochrone of a desired year over a hr diagram
plot_evolutionary_tracks() # plots a colorful hr diagram
show() # shows the plot that has been created
save(imagename) # save plot to imagename.png
```
<strong>Optional flags for ```plot_isochrone()```</strong><br>

defaults are shown:
- change color of isochrone track: ```track_color='red'```
- change number of points in the graph: ```resolution=100```
- change % difference from desired age allowed: ```tolerance=10```
- show hr tracks behind isochrones: ```show_hr=True```


### Sample usage

<strong>Please see:</strong>
- main_sample1.py (generates csv files from mesa data objects)
- main_sample2.py (generates isochrones from csv files created in main_sample1.py)
- main_sample3.py (generates isochrones directly from mesa data objects)

### Interpolation algorithm

To solve the non-monoticity problem, we must find a polynomial function:<br>
$P:P(t) = (x(t), y(t)) \textrm{ where } x(t) \textrm{ is log temperature, } y(t) \textrm{ is log luminocity, and }$ <br>
$t \textrm{ is a time parameter where } t = [0, ..., n-1]$

$n = \lvert \textrm{log effective temperature} \rvert = \lvert \textrm{log luminosity} \rvert = \lvert t \rvert$

$\Rightarrow \exists \textrm{ cubic spline functions } x_\text{teff}(t) \textrm{ and } y_\text{logL}(t) : P_\text{isochrone} = (x_\text{teff}(t), y_\text{logL}(t))$


















