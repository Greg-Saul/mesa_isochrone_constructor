########################################################
# This sample main loads data from a folder of csv files
# generated in main_sample1.py and creates isochrones
# on top of an hr diagram. It will save the plot as
# sample2.png and pop up an interactive plot.
#
# 5/29/25
########################################################

from mesa_isochrone_2 import mesa_isochrone
import time

t0 = time.time()

# Initialize and load data
plotter = mesa_isochrone()

# Add isochrones
plotter.plot_isochrone('z_0.028.json', 1.34e10, track_color='blue', resolution=1000, tolerance=1, show_points=True, interpolation_method="akima")
plotter.plot_isochrone('z_0.014.json', 1.34e10, track_color='green', show_hr=False, resolution=1000, tolerance=1, show_points=True)

t1 = time.time()

# print timing information
print("created isochrone in", t1-t0, "seconds")

# Show plot and save plot
plotter.save(image_name="sample2")
plotter.show()