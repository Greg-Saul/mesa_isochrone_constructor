import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from scipy.interpolate import CubicSpline, UnivariateSpline, make_splrep
from statsmodels.nonparametric.smoothers_lowess import lowess

matplotlib.use('TkAgg')

fig, ax = plt.subplots(figsize=(8, 12))
ax.invert_xaxis()

df = pd.read_csv("NGC6397_gaia_data_log_format.csv")

df = df.sort_values(by='mass_flame', ascending=True, na_position='last')

df[['ridge_log_Teff', 'ridge_log_L']] = lowess(df['log_Teff'], df['log_L'], frac=0.2)[:, [1, 0]]

plt.title("NGC 6397 Isochrone")
plt.xlabel("Log Teff K")
plt.ylabel("Log Luminosity ☉")
plt.scatter(df.log_Teff, df.log_L, s=5, color="gray")
plt.plot(df.ridge_log_Teff, df.ridge_log_L, color="blue")
plt.show()