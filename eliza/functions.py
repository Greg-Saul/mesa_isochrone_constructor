#!/usr/local/Anaconda2024/bin/python3

#######################################
#						              
#   	   Function Library
#		Created: April 1, 2025	
#		Updated: May 27, 2025		  
#	     Author: Eliza Frankel       
#                                                             
#######################################

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import mesa_reader as mr
from glob import glob
import pandas as pd

plt.rcParams['axes.prop_cycle'] = plt.cycler(color=[plt.cm.tab20b(i) for i in range(plt.cm.tab20b.N)])

"""
ISOCHRONES
"""


def make_tracklist(tracklist):
	tracklist = glob(tracklist)
	tracklist.sort()

	return tracklist


def plotting_tracks(T_eff, Lum, label, color_index, ax): #, colormap='tab20b'):

	# EAF - determining if we should plot the tracks
	ax.plot(T_eff, Lum, linewidth=2, zorder=2, label=label)


def plotting_points(closest_Teff, closest_Lum, target_age, label, ax):

	ax.scatter(closest_Teff, closest_Lum, color='k', s=150, zorder=3)


def draw_line(x1, y1, x2, y2, name, color):

	for i in range(0, 2, 2):
	    plt.plot([x1, x2], [y1, y2], color, '-', label=name)


def connect_the_dots(x, y, name, color):

	for i in range(len(x) - 1):
		draw_line(x[i], y[i], x[i+1], y[i+1], name, color)
	# plt.legend()

	# plt.show()


def actually_plot_isochrone(T_eff, Lum, name, color):

	# plt.plot(figsize=(16,9))
	plt.gca().invert_xaxis()

	connect_the_dots(T_eff, Lum, name, color)


def plot_isochrone_from_csv(file, name, color):
	df = pd.read_csv(file)

	# EAF - extracting Temperature and Luminosity columns from csv
	T_eff = df["Temperature"].to_numpy()
	luminosity = df["Luminosity"].to_numpy()

	actually_plot_isochrone(T_eff, luminosity, name, color)




def finding_isochrone(target_age, tracklist, model_name, ax, row, column, plotting=True, plot_tracks=False, save_csv=False, colormap='tab20b'):
	""" Plots isochrones over stellar tracks. Used in create_isochrone or on its own

	*** USED TO BE CALLED PLOT_ISOCHRONE

	Parameters:
	-----------
	target_age (int or float) - the target age to look for in a list; in years
	tracklist (list or string) - list of filenames of data or path to data
	ax (plt axis object)
	rows (int) - number of rows of panels in subplot
	columns (int) - number of rows of columns in subplot
	plot_tracks (Boolean) - says if this is the first instance. If true, plot tracks.
		If false, just plot isochrone points
	colormap (string) - name of a colormap to use in plotting. if not specified,
		tab20b is the default
	"""

	labels = []

	T = []
	L = []

	for file in tracklist:

		data = mr.MesaData(file)
		list_ages = data.star_age

		# EAF - calls find_nearest to find the closest index. 
		#		[0] returns just the index
		age_index = find_nearest(list_ages, target_age)[0]

		closest_Teff = data.log_Teff[age_index]
		closest_Lum = data.log_L[age_index]

		mass = file.split('history_m')[1].split('_z')[0]
		labels.append(mass)

		# EAF - Determining the isochrone point and plot it
		if within_epsilon(list_ages[age_index], target_age, 1):
			T.append(closest_Teff)
			L.append(closest_Lum)

		i = len(labels) - 1
		# EAF - determining if we should plot the tracks
		if plotting == True:
			if plot_tracks == True:
				plotting_tracks(data.log_Teff, data.log_L, mass, i, ax)
			

			# EAF - adding gridlines and inverting the x-axis for each subplot
			ax.grid(True, zorder=1)
			ax.xaxis.set_inverted(True)

			# EAF - setting axis labels and subplot titles
			ax.set_xlabel('log(T$_{eff}$)')
			ax.set_ylabel('log(L)')
			ax.set_title(str(target_age / 1e9) + ' billion years')

			if within_epsilon(list_ages[age_index], target_age, 1):
				plotting_points(closest_Teff, closest_Lum, target_age, mass, ax)


	if save_csv == True:

		age = target_age / 1e9

		df = pd.DataFrame(list(zip(T, L)), columns =['Temperature', 'Luminosity'])
		csv = df.to_csv(f'temperature_luminosity_age{age}Gyr_{model_name}.csv')

	return min(labels), max(labels), T, L



def create_isochrone(target_age, tracklist_path, tracklist_directory, save_fig=True, figure_name=None, legend=False, save_csv=False, rows=1, columns=1, colormap='tab20b'):
	""" Creates isochrone based on modeled MESA data, found in tracklist. Plots data.

	Parameters:
	-----------
	target_age (list of floats or ints) - the target age to look for in a list; in Gyr
	tracklist (list or string) - list of filenames of data or path to data
	save_fig (Boolean) - True if you want a figure saved, False otherwise.
		Defaults to True
	figure_name (string) - name to save figure as. If left blank, defaults to:
		target_age_{AGE}_stellar_grid_with_isochrone_mass_{MIN}-{MAX}_Msun.png
	legend (Boolean) - determines if a legend is viewed. Defaults to False
	rows (int) - number of rows of panels in subplot
	columns (int) - number of rows of columns in subplot
	colormap (string) - name of a colormap to use in plotting. if not specified,
		tab20b is the default
	"""

	# EAF - accounting for a path to the data
	tracklist = make_tracklist(tracklist_path + tracklist_directory)
	name = tracklist_directory.split('/')[0]

	# EAF - converts from years to Gyrs
	target_age = np.array(target_age)
	age = target_age * 1e9

	fig, ax = plt.subplots(ncols=columns, nrows=rows, figsize=(16,9))

	row_counter = 0
	col_counter = 0

	for target in range(len(age)):
		# EAF - setting x as a variable to determine which column
		x = target + 1

		# EAF - determining how many subpanels there will be - if just one, then
		#		only plot the stellar tracks once

		if rows == 1 and columns == 1:
			if target == 0:
				plot_tracks = True
		
			min_mass, max_mass, T, L = finding_isochrone(age[target], tracklist, name, ax, 1, 1, plotting=True, plot_tracks = plot_tracks, save_csv=True, colormap=colormap)

		# EAF - code for plotting on multiple panels
		else:
			# EAF - Getting the correct rows to plot on correct subplot
			for i in range(rows):
				if x / rows <= (rows - i):
					r = rows - (i + 1)

			# EAF - determining which column
			c = (x % columns) - 1

			# EAF - defining ax objects depending on if it is a 1D or 2D array
			if rows == 1 and columns != 1:
				ax1 = ax[c]
			elif columns == 1 and rows != 1:
				ax1 = ax[r]
			elif rows == 1 and columns == 1:
				ax1 = ax
			else:
				ax1 = ax[r, c]

			min_mass, max_mass, T, L = finding_isochrone(age[target], tracklist, ax1,\
				r, c, plotting=True, plot_tracks = plot_tracks, save_csv=True, colormap=colormap)
	
	if legend:
		plt.legend()
	if save_fig:
		if figure_name == None:
			fig_name = f"age_{target_age}_{name}_stellar_grid_with_isochrone_mass_{min_mass}-{max_mass}_Msun.png"
		else:
			fig_name = figure_name
		plt.savefig(fig_name, dpi=300)

	plt.show()



def find_nearest(array, value):
	""" Finds the index closest to the value in array

	Parameters:
	-----------
	array (np.array) - list of instances/information
	value (float or int) - value to look for in array

	Returns:
	---------
	index (int) - index of the array instance closest to value
	array[indx] (float or int) - the value in array closest to value
	"""

	indx = np.absolute(array - value).argmin()
	return indx, array[indx]



def within_epsilon(age, target_age, epsilon=0.05):
	""" Determines if the age from an array is within epsilon of target_age

	Parameters:
	-----------
	age (int or float) - Age of star from model, in years
	target_age (int or float) - the target age to look for in model, in years
	epsilon (float or int) - tolerance of target_age, to determine if the age is
		viable
		If not specified, it defaults to 5%

	"""

	if (np.absolute(age - target_age) / age) < epsilon:
		return True
	else:
		return False



"""
COLORS AND COLORMAPPING
"""

def get_cmap_colors(cmap_name, num_colors):
	""" Function to get a matplotlib color map and segment it into N colors (num_colors)
	
	Parameters:
	-----------
	cmap_name (str) - name of matplotlib colormap
	num_colors (int) - number of colors the colormap should be split into.

	Returns:
	--------
	colors (list) - in the format (X, Y, Z, 1.0)

	Note:
	-----
	written by Gabby Graham

	cmaps:
	# gist_rainbow - pretty rainbow; very bright
	# gnuplot - nice range of colors
	# PuOr - purple and orange
	# viridis - classic purples blues greens yellows
	# plasma - pretty blue purple pink orange yellow
	# magma - like plasma but dark
	# tab20b - nice neutral rainbow vibes - discrete
	# turbo - pretty rainbow, ends with black
	"""

	cmap = plt.cm.get_cmap(cmap_name, num_colors)
	colors = [cmap(i) for i in range(cmap.N)]
	return colors



def cmap_discrete(cmap_name, num_colors):
	""" Function to create a custom discrete color map with N colors - meant for 
		plotting colorbars. Uses function get_cmap_colors()

	Parameters:
	-----------
	cmap_name (str) - name of matplotlib colormap
	num_colors (int) - number of colors the colormap should be split into.

	Returns:
	--------
	norm (matplotlib.colors.BoundaryNorm obect) - to be used in plt.scatter()
		This determines the number of colors used in colorbar.

	Note:
	-----
	Should be used as follows:
	>  plt.scatter(x, y, c=$sequence_numbers_mapped_using_cmap_norm, cmap=$COLOR_MAP, norm=norm)
	or
	>  plt.scatter(x, y, c=$c, cmap=$COLOR_MAP, norm=cmap_discrete($COLOR_MAP, $NUM_COLORS))
	"""

	segments = get_cmap_colors(cmap_name, num_colors)
	cmap = mpl.colors.LinearSegmentedColormap.from_list('Custom cmap', segments, cmap_name.N)

	bounds = np.linspace(0, num_colors, num_colors + 1)
	norm - mpl.colors.BoundaryNorm(segments, cmap_name.N)

	return norm


