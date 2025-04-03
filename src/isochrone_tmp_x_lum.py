from mesa_reader import MesaData
import matplotlib
import tkinter as tk
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt 
from scipy.interpolate import interp1d
from scipy.interpolate import CubicSpline
import numpy as np

colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 
          'red', 'orange', 'yellow', 'green', 'blue', 'purple', 
          'red', 'orange', 'yellow', 'green', 'blue', 'purple', 
          'red', 'orange', 'yellow', 'green', 'blue', 'purple']

name = ["0.5mass", "0.7mass", "0.9mass", "1mass", "1.2mass", "1.4mass", 
        "1.6mass", "1.8mass", "2mass", "2.4mass", "2.6mass", "3mass", "4mass", 
        "5mass", "6mass", "7mass", "8mass", "9mass", "10mass"]
md = []
lum = []
tmp = []
ages = []
ages2 = []
newtmp = []
newlogL = []

desired_age = 2e9

def find_indices(arr, desired_year):
    inx = (np.abs(arr-desired_year)).argmin()
    return arr[inx], inx

for i in range(len(name)):
    md.append(MesaData('gregsWork/work/LOGS/' + name[i] + '.data'))
    lum.append(md[i].data('log_L'))
    tmp.append(md[i].data('log_Teff'))
    ages.append(len(md[i].star_age))
    ages2.append(md[i].star_age)

min_age_length = min(ages)
masses = np.array([0.5, 0.7, 0.9, 1, 1.2, 1.4, 1.6, 1.8 , 2, 2.4, 2.6, 3, 4, 5, 6, 7, 8, 9, 10])

print(ages)

fig, ax = plt.subplots(figsize=(12, 8))

# HR diagram
for i in range(len(name)):
    age = md[i].star_age[:min_age_length]
    tmp[i] = tmp[i][:min_age_length]
    lum[i] = lum[i][:min_age_length]
    ages2[i] = ages2[i][:min_age_length]

    newtmp.append(tmp[i][find_indices(ages2[i], desired_age)[1]])
    newlogL.append(lum[i][find_indices(ages2[i], desired_age)[1]])

    plt.plot(tmp[i], lum[i], color=colors[i], label=name[i], linewidth=2)


# Interpolation
##############################################################################################################

# f = CubicSpline(newtmp, newlogL)
# x = np.linspace(min(newtmp), max(newtmp), 100)

# plt.plot(x, f(x), 'k--')

spline_tmp = CubicSpline(masses, newtmp)
spline_lum = CubicSpline(masses, newlogL)

param_fine = np.linspace(masses[0], masses[-1], 100)
tmp_fine = spline_tmp(param_fine)
lum_fine = spline_lum(param_fine)

plt.plot(tmp_fine, lum_fine, 'k--')
plt.plot(newtmp, newlogL, 'ko')
plt.plot(newtmp, newlogL, 'k-', linewidth='1', color='red')

################################################################################################################

ax.invert_xaxis()

plt.ylabel('Log Luminosity', fontsize=14)
plt.xlabel('Log Effective Temperature', fontsize=14)
plt.title('Luminosity vs. Temperature', fontsize=16)
plt.legend(loc="lower left", fontsize=10)
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()
