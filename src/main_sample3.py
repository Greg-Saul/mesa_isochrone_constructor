########################################################
# This sample main is to show loading mesa data objects 
# directly into arrays for isochrone generation. 
# This is the slowest method of rapidly generating 
# multiple isocrones. This saves the plot into 
# sample3.png
#
# 5/29/25
########################################################

from mesa_reader import MesaData
from mesa_isochrone import mesa_isochrone
import glob
import time

t0 = time.time()

# Initialize and load data
plotter = mesa_isochrone()
md = []

file_paths = glob.glob("./data/*.data")
file_paths = sorted(file_paths, key=plotter.sort_by_mass_key)

print(file_paths)

for path in file_paths:
  md.append(MesaData(path))

plotter.load_models(md)

# Add isochrones to plot
plotter.plot_isochrone(1e8, track_color='red', show_hr=False, resolution=1000)
plotter.plot_isochrone(3.16e8, track_color='orange', show_hr=False, resolution=1000)
plotter.plot_isochrone(1e9, track_color='green', show_hr=False, resolution=1000)
plotter.plot_isochrone(3.16e9, track_color='blue', show_hr=False, resolution=1000)
plotter.plot_isochrone(1e10, track_color='purple', show_hr=False, resolution=1000)

t1 = time.time()

print("created isochrones in", t1-t0, "seconds")

# Save plot
plotter.save()
plotter.show()