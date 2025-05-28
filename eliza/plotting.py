#!/Users/elizafrankel/anaconda3/bin/python3

# Author: E. Frankel
# 5.27.2025

import sys
sys.path.insert(0, '/Users/elizafrankel/Desktop/Research/')
import functions as fn

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import mesa_reader as mr
from glob import glob
import pandas as pd

plt.rcParams['axes.prop_cycle'] = plt.cycler(color=[plt.cm.tab20b(i) for i in range(plt.cm.tab20b.N)])

path = '/Users/elizafrankel/Desktop/holy_grail/week2/histories/'

# EAF - FINDING POINTS ON TRACKS, PLOTTING TRACKS AND POINTS FOR TARGET AGE

fn.create_isochrone([5], path, 'a1.0_z0.014/history_m*.data', save_fig=True,\
	legend=False, rows=1, columns=1, save_csv=True, colormap='tab20b')




# EAF - FINDING THE ISOCHRONE FROM TRACKLIST, SAVING AS CSV, PLOTTING ISOCHRONE
#		(JUST LINES FROM ONE POINT TO ANOTHER)

# rows = 1
# columns = 1

# fig, ax = plt.subplots(ncols=columns, nrows=rows, figsize=(16,9))

# tracklist = path + 'a2.1_z0.014/history_m*.data'

# min_lab, max_lab, T, L = fn.finding_isochrone(10, tracklist, 'a2.1_z0.014', ax, rows, columns, plotting=True, plot_tracks=True, save_csv=True, colormap='tab20b')

# fn.actually_plot_isochrone(T, L)




# EAF - USING SAVED CSV FROM FINDING_ISOCHRONE (could be using either method
#		above) AND PLOTTING THE ISOCHRONE FROM A CSV FILE


# path = ''

# plt.plot(figsize=(16,9))

# fn.plot_isochrone_from_csv('temperature_luminosity_age5.0Gyr_a1.0_z0.014.csv', '_a1.0_z0.014', color='k')
# fn.plot_isochrone_from_csv('temperature_luminosity_age5.0Gyr_a1.5_z0.014.csv', 'a1.5_z0.014', color='b')
# fn.plot_isochrone_from_csv('temperature_luminosity_age5.0Gyr_a2.1_z0.014.csv', 'a2.1_z0.014', color='g')

# plt.plot(np.log10(5027.8535), np.log10(52.11690480510336), 'deeppink', marker = '*', label='300028676')
# plt.plot(np.log10(5872.3467), np.log10(6.089633301914745), 'deeppinl', marker = '*', label='300028676')
# plt.plot(np.log10(5048.2124), np.log10(122.01356014975516), 'goldenrod', marker = '*', label='134041626')
# plt.plot(np.log10(4963.2695), np.log10(130.93277188334187), 'dodgerblue', marker = '*', label='57714798')
# plt.plot(np.log10(4578.3867), np.log10(397.2717821638007), 'slateblue', marker = '*', label='267535271')

# plt.show()
