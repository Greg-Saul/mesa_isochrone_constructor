# py_mesa_interpolation

```py_mesa_interpolation``` is a tool that is designed to be used with [py_mesa_reader](https://github.com/wmwolf/py_mesa_reader) and [MESA stellar astrophysics program](https://docs.mesastar.org/en/latest/) to create isochrone plots over multiple tracks.

### dependencies:
- py_mesa_reader
- pandas
- numpy
- matplotlib
- scipy

### installation directions (in terminal):

1) check dependencies and make sure they are all properly installed
2) ```git clone https://github.com/Greg-Saul/mesa_isochrone_constructor.git```
3) ```cd mesa_isochrone_constructor/src```
4) ```python3 main_sample1.py```
5) ```python3 main_sample2.py```
6) if these run and pop up an isochrone, mesa_isochrone_constructor is properly installed and ready for use


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
- show points from mesa data: ```show_points=False```

<strong>Optional flags for ```save()```</strong><br>

defaults are shown:
 - set image name: ```image_name="isochrone_diagram"```

### Sample usage

<strong>Please see:</strong>
- main_sample1.py (generates csv files from mesa data objects)
- main_sample2.py (generates isochrones from csv files created in main_sample1.py)
- main_sample3.py (generates isochrones directly from mesa data objects)

### Interpolation algorithm

To solve the non-monoticity problem, we must find a polynomial function:<br>
$P:P(t) = (x(t), y(t)) \textrm{ where } x(t) \textrm{ is log temperature, } y(t) \textrm{ is log luminocity, and }$ <br>
$t \textrm{ is a time parameter where } t = [0, ..., n-1]$

$n = \lvert \textrm{log effective temperature} \rvert = \lvert \textrm{log luminosity} \rvert = \lvert t \rvert = \text{number of tracks}$

$i = [0, ..., \text{ desired resolution}]$

$\Rightarrow \exists \textrm{ cubic spline functions } x_\text{teff}(i) \textrm{ and } y_\text{logL}(i) : P_\text{isochrone}(i) = (x_\text{teff}(i), y_\text{logL}(i))$


















