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
md = []

# find filepaths to mesa data
file_paths = glob.glob("./data/*.data")
file_paths.sort()

# load mesa data objects into an array
for path in file_paths:
  md.append(MesaData(path))

# load objects into a folder named testing of csv files
plotter.load_models(md)
plotter.md_to_csv('sample1')

t1 = time.time()

print("created csv's in", t1-t0, "seconds")

