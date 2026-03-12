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


# # Initialize plotter library
plotter = mesa_isochrone()
# plotter.function_summary()

md1 = []

# find filepaths to mesa data
# file_paths1 = glob.glob("./data/historiesNGC6397/*.data")


# file_paths1 = sorted(file_paths1, key=plotter.sort_by_mass_key)

# file_paths1.sort()

# for i in file_paths1:
#   print(i)

file_paths1 = plotter.select_files()


t0 = time.time()

# load mesa data objects into an array
for path in file_paths1:
  md1.append(MesaData(path))

plotter.load_models(md1)
plotter.export('M92.json', file_type="json")

t1 = time.time()

print("created files in", t1 - t0, "seconds")