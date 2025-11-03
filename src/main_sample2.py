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
# plotter.function_summary()
# Add isochrones
plotter.plot_isochrone("z_0.014.json", 1.34e10, track_color="red", clean=True, show_hr=False)
plotter.gaia_stack("../cluster_data/NGC6397_fine_isochrone.csv")
t1 = time.time()

# print timing information
print("created isochrone in", t1-t0, "seconds")

# Show plot and save plot
# plotter.save(image_name="isochrone_for_presentation")
# plotter.save(image_name="gaia+mesa")

plotter.show_clean()
# plotter.show()