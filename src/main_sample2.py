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
# plotter.plot_isochrone("../../../../M92/isochrone_age13.8Gyr_z0.000130_a1.10_toleranceNA_tracks212.eliza", 1.34e10, track_color="red", interpolation_method="akima", show_points=True, show_hr=False)
plotter.plot_isochrone("../../../../M92/isochrone_age13.8Gyr_z0.000130_a1.10_toleranceNA_tracks212.eliza", 1.34e10, track_color="red", interpolation_method="akima", show_hr=False)

# plotter.plot_isochrone()
# plotter.plot_isochrone("M92.json", 12.7e9, interp="akima", show_hr=False)
# plotter.plot_isochrone("M92.json", 12.7e9, interp="akima", track_color="green", reinterpolate=False, show_hr=False)
plotter.gaia_stack("../cluster_data/csv2.csv")
# plotter.show_clean()
t1 = time.time()
# plotter.gaia_stack("../cluster_data/clustercsv/NGC6397_gaia_data_log_format.csv")
# print timing information
print("created isochrone in", t1-t0, "seconds")

# plotter.fill("unit")

# Show plot and save plot
# plotter.save(image_name="M92for3-5-26")
# plotter.save(image_name="interpVSreinterp")


# plotter.show_clean()
plotter.show()

# plotter.temp('6397tst.png')