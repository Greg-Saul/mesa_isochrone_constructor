########################################################
# This sample main is to show loading mesa data objects 
# into a folder of csv files for later use. see 
# main_sample2.py for csv use.
#
# 5/29/25
########################################################

from mesa_reader import MesaData
from mesa_isochrone import mesa_isochrone
import glob
import time

t0 = time.time()

# Initialize plotter library
plotter = mesa_isochrone()
md1 = []
md2 = []

# find filepaths to mesa data
file_paths1 = glob.glob("./data/histories9-25/*.data")
file_paths2 = glob.glob("./data/histories10-1/*.data")

file_paths1 = sorted(file_paths1, key=plotter.sort_by_mass_key)
file_paths2 = sorted(file_paths2, key=plotter.sort_by_mass_key)

# # load mesa data objects into an array
for path in file_paths1:
  md1.append(MesaData(path))

for path in file_paths2:
    md2.append(MesaData(path))

plotter.load_models(md1)
plotter.export('z_0.014.json', file_type="json")
plotter.load_models(md2)
plotter.export('z_0.028.json', file_type="json")

t1 = time.time()

print("created files in", t1 - t0, "seconds")

