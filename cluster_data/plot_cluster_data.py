import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess

df = pd.read_csv("NGC6397_gaia_data.csv")
df = df[df.parallax > 0.1]
import numpy as np

def calculate_teff(bp_rp):
    a = 0.00017
    b = 0.00014
    c = 0.000045
    teff = 1 / (a + b * bp_rp + c * bp_rp**2)
    return np.log10(teff)

def compute_log_luminosity(g_mag, parallax, bp_rp):
    # find distance in parsecs
    d = 1000 / parallax
    # absolute magnitude calculated from distance modulus
    abs_mag = g_mag - 5 * np.log10(d) + 5
    M_G_sun = 4.68
    # log luminosity
    log_L = (abs_mag - M_G_sun)/-2.5
    return log_L



df["log_Teff"] = calculate_teff(df["bp_rp"])
df["log_L"] = compute_log_luminosity(df.phot_g_mean_mag, df.parallax, df.bp_rp)

df = df.dropna(subset=["log_Teff", "log_L"])

df[["ridge_Teff", "ridge_L"]] = lowess(df.log_Teff, df.log_L, frac=0.2)[:, [1, 0]]

# print(len(df.ridge_L))

fig, ax = plt.subplots(figsize=(8, 12))
plt.plot(df.ridge_Teff, df.ridge_L)
plt.scatter(df.log_Teff, df.log_L, s=5, color="gray", label="Stars")
ax.invert_xaxis()
ax.set_xlabel("log Teff [K]")
ax.set_ylabel("log L [L☉]")
ax.set_title("NGC 6397 HR Diagram")
ax.legend()
plt.show()