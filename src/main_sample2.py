########################################################
# This sample main loads data from a folder of csv files
# generated in main_sample1.py and creates isochrones
# on top of an hr diagram. It will save the plot as
# sample2.png and pop up an interactive plot.
#
# 5/29/25
########################################################

from mesa_isochrone import mesa_isochrone
import time

t0 = time.time()

# Initialize and load data
plotter = mesa_isochrone()

# load csv data from sample1 folder into the needed arrays
plotter.extract_csv('star_data')

# Add isochrones
plotter.plot_isochrone(1e8, track_color='red', resolution=1000)
plotter.plot_isochrone(3.16e8, track_color='orange', show_hr=False, resolution=1000)
plotter.plot_isochrone(1e9, track_color='green', show_hr=False, resolution=1000)
plotter.plot_isochrone(3.16e9, track_color='blue', show_hr=False, resolution=1000)
plotter.plot_isochrone(1e10, track_color='purple', show_hr=False, resolution=1000)

t1 = time.time()

# print timing information
print("created isochrone in", t1-t0, "seconds")

# Show plot and save plot
plotter.save(image_name="sample2")
plotter.show()