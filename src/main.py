from mesa_reader import MesaData
from mesa_isochrone import mesa_isochrone
import sys
import glob
import time

## Local to M Joyce system 
# sys.path.append('/home/mjoyce/MESA/py_mesa_reader/')
# from mesa_reader import MesaData

t0 = time.time()

# Initialize and load data
plotter = mesa_isochrone()
md = []

file_paths = glob.glob("../histories/*.data")
file_paths.sort()

print(len(file_paths))

for path in file_paths:
  md.append(MesaData(path))

plotter.load_models(md)

# Add isochrones
plotter.plot_isochrone(1e8, track_color='green', show_hr=False, resolution=1000)
plotter.plot_isochrone(3.16e8, track_color='orange', show_hr=False, resolution=1000)
plotter.plot_isochrone(1e9, track_color='green', show_hr=False, resolution=1000)
plotter.plot_isochrone(3.16e9, track_color='blue', show_hr=False, resolution=1000)
plotter.plot_isochrone(1e10, track_color='purple', show_hr=False, resolution=1000)

t1 = time.time()

print("created isochrone in", t1-t0, "seconds")

# Show plot
plotter.save(image_name="test2")
# plotter.show()
