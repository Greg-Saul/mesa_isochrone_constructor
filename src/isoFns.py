
import matplotlib
import tkinter as tk
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt 
from scipy.interpolate import interp1d
from scipy.interpolate import CubicSpline
from scipy.interpolate import Rbf
import numpy as np
import os

fig, ax = plt.subplots(figsize=(12, 8))

def hr(md):
  lum = []
  tmp = []
  masses = []
  ages = []
  ages_len = []
  file = []

  for i in range(len(md)):
    lum.append(md[i].data('log_L'))
    tmp.append(md[i].data('log_Teff'))
    masses.append(md[i].star_mass[0])
    ages.append(md[i].star_age)
    ages_len.append(len(md[i].star_age))
    file.append(os.path.basename(md[i].file_name))
  
  # print(file)
  min_age_length = min(ages_len)


  for i in range(len(md)):
    tmp[i] = tmp[i][:min_age_length]
    lum[i] = lum[i][:min_age_length]
    plt.plot(tmp[i], lum[i], linewidth=2, label=f'{file[i]}')

def isochrone(md, desired_age, custom_color):
  lum = []
  tmp = []
  masses = []
  ages = []
  ages_len = []
  newtmp = []
  newlogL = []
  file = []

  for i in range(len(md)):
    lum.append(md[i].data('log_L'))
    tmp.append(md[i].data('log_Teff'))
    masses.append(md[i].star_mass[0])
    ages.append(md[i].star_age)
    ages_len.append(len(md[i].star_age))
    file.append(os.path.basename(md[i].file_name))

    min_age_length = min(ages_len)

  for i in range(len(md)):
    indices = find_indices(ages[i], desired_age)

    if(indices[2] < 50):
      newtmp.append(tmp[i][indices[1]])
      newlogL.append(lum[i][indices[1]])
      # generally leave this commented out
      plt.plot(tmp[i], lum[i], color='grey')
  
  # print(newtmp)

  t = np.arange(len(newtmp))
  t_fine = np.linspace(0, len(newtmp) - 1, 200)

  cs_tmp = CubicSpline(t, newtmp)
  cs_lum = CubicSpline(t, newlogL)

  tmp_smooth = cs_tmp(t_fine)
  lum_smooth = cs_lum(t_fine)

  plt.plot(tmp_smooth, lum_smooth, linestyle='--', color=custom_color, label=f'Isochrone {desired_age}')

  plt.plot(newtmp, newlogL, 'ko')

  # for i in range(len(newlogL) - 1):
  #   if newtmp[i] > newtmp[i + 1]:
  #     f = CubicSpline([newtmp[i + 1], newtmp[i]], [newlogL[i + 1], newlogL[i]])
  #   else:
  #     f = CubicSpline([newtmp[i], newtmp[i + 1]], [newlogL[i], newlogL[i + 1]])
  #   x = np.linspace(min([newtmp[i], newtmp[i + 1]]), max([newtmp[i], newtmp[i + 1]]), 100)

  #   plt.plot(x, f(x), 'k--', color=f'{custom_color}', label=f'{desired_age}')


def show_plot():
  ax.invert_xaxis()
  plt.ylabel('Log Luminosity', fontsize=14)
  plt.xlabel('Log Effective Temperature', fontsize=14)
  plt.title('Luminosity vs. Temperature', fontsize=16)
  plt.legend(loc="lower left", fontsize=10)
  plt.grid(True, linestyle='--', alpha=0.7)
  plt.show()

def find_indices(arr, desired_year):
    inx = (np.abs(arr-desired_year)).argmin()
    percent_error = 100 * abs(arr[inx] - desired_year) / desired_year
    # print(percent_error, inx)
    return arr[inx], inx, percent_error