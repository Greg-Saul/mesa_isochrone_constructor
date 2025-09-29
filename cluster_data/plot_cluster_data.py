import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.nonparametric.smoothers_lowess import lowess
from scipy.interpolate import CubicSpline, interp1d

df = pd.read_csv("NGC6397_gaia_data.csv")

def calculate_teff(bp_rp):
    a = 0.00017
    b = 0.00014
    c = 0.000045
    teff = 1 / (a + b * bp_rp + c * bp_rp**2)
    return np.log10(teff)

def compute_log_luminosity(g_mag, parallax):
    d = 1000 / parallax
    abs_mag = g_mag - 5 * np.log10(d) + 5
    M_sun = 4.68
    log_L = (abs_mag - M_sun)/-2.5
    return log_L

df["log_Teff"] = calculate_teff(df["bp_rp"])
df["log_L"] = compute_log_luminosity(df.phot_g_mean_mag, df.parallax)
df = df.dropna(subset=["log_Teff", "log_L"])

# lowess ridge
df = df.sort_values("log_L")
df[["ridge_Teff", "ridge_L"]] = lowess(df["log_Teff"], df["log_L"], frac=0.2)[:, [1, 0]]

def numerical_derivative(x, y):
    x, y = np.asarray(x), np.asarray(y)
    d = np.zeros_like(y)
    d[0] = (y[1] - y[0]) / (x[1] - x[0])
    d[1:-1] = (y[2:] - y[:-2]) / (x[2:] - x[:-2])
    d[-1] = (y[-1] - y[-2]) / (x[-1] - x[-2])
    return d

def rotate_points(x, y, rx, ry, inverse=False):
    a = np.arctan(numerical_derivative(ry, rx))
    if inverse:
        a = -a
    c, s = np.cos(a), np.sin(a)
    x_rot = x * c - y * s
    y_rot = x * s + y * c
    if not inverse:
        y_rot += ry
    return x_rot, y_rot

# Rotate points
df[["x_new", "y_new"]] = np.column_stack(
    rotate_points(df["log_Teff"] - df["ridge_Teff"],
                  df["log_L"] - df["ridge_L"],
                  df["ridge_Teff"], df["ridge_L"])
)
df["x_new0"] = 0
df = df.sort_values("y_new")

# Binning + kde
bins = [-2.25, -2, -1.5, -1, -0.5, 0.5, 0.75, 1, 1.5, 2, df.log_L.max()]
# bins = np.linspace(df.log_L.min(), df.log_L.max(), 10)
bin_labels = [str(b) for b in bins[:-1]]
df["bin"] = pd.cut(df["y_new"], bins=bins, labels=bin_labels, right=False)

def calculate_kde(df, x_col, y_col, bandwidth="scott"):
    results = []
    for bin_label, group in df.groupby("bin", observed=False):
        if group[x_col].empty:
            continue
        fig, ax = plt.subplots()
        kde_plot = sns.kdeplot(group[x_col], bw_method=bandwidth, ax=ax)
        xxx, yyy = kde_plot.lines[0].get_data()
        plt.close(fig)
        idx_max = pd.Series(yyy).idxmax()
        results.append({
            "bin": bin_label,
            "x_at_max_density": xxx[idx_max],
            "median_y": group[y_col].median()
        })
    return results

kde_results = calculate_kde(df, "x_new", "y_new")
results_df = pd.DataFrame(kde_results).sort_values("median_y")
y_sorted = results_df["median_y"].values
x_sorted = results_df["x_at_max_density"].values

# Cubic spline
cs = CubicSpline(y_sorted, x_sorted)
mask = (df["y_new"] >= bins[0]) & (df["y_new"] < bins[-1])
df.loc[mask, "x_interpolate"] = cs(df.loc[mask, "y_new"])
df.loc[~mask, "x_interpolate"] = np.nan

# Rotate back
df["x_back"], df["y_back"] = rotate_points(
    df["x_interpolate"], df["y_new"] - df["ridge_L"],
    df["ridge_Teff"], df["ridge_L"], inverse=True
)
df["x_back"] += df["ridge_Teff"]
df["y_back"] += df["ridge_L"]

# --- Final smoothing ---
df_sorted = df[["x_back", "y_back"]].dropna().sort_values("y_back").reset_index(drop=True)
x_sorted = df_sorted["x_back"].values
y_sorted = df_sorted["y_back"].values
linear_interp = interp1d(y_sorted, x_sorted, kind="linear", fill_value="extrapolate")

y_fine = np.linspace(y_sorted.min(), y_sorted.max(), 5000)
x_fine = linear_interp(y_fine)

plt.rcParams.update({'font.size': 10})
s = 3
alpha = 0.5

fig, ax = plt.subplots(figsize=(8, 12))

ax.scatter(df['log_Teff'], df['log_L'], s=s, color='grey', alpha=alpha)
ax.plot(df['x_back'], df['y_back'], color='darkorange', lw=3, label="corrected ridgeline")
ax.invert_xaxis()
ax.set_xlabel(r'$\log T_{\mathrm{eff}}$ [K]')
ax.set_ylabel(r'$\log L\ [L_\odot]$')

# fig, ax = plt.subplots(2, 2, figsize=(18, 16))

# ax[0, 0].scatter(df['log_Teff'], df['log_L'], s=s, c='grey', alpha=alpha)
# ax[0, 0].plot(df['ridge_Teff'], df['ridge_L'], c="black", lw=3, label="primary ridgeline")
# ax[0, 0].invert_xaxis()
# ax[0, 0].set_xlabel(r'$\log T_{\mathrm{eff}}$ [K]')
# ax[0, 0].set_ylabel(r'$\log L\ [L_\odot]$')
# # ax[0, 0].legend(loc='upper left')

# ax[0, 1].scatter(df['x_new'], df['y_new'], s=s, color='grey', alpha=alpha)
# ax[0, 1].plot(df['x_new0'], df['y_new'], c="black", lw=3, label="primary ridgeline")
# ax[0, 1].set_xlabel('relative Teff')
# ax[0, 1].set_ylabel('relative log L')
# # ax[0, 1].legend(loc='upper left')

# ax[1, 0].scatter(df['x_new'], df['y_new'], s=s, color='grey', alpha=alpha)
# ax[1, 0].scatter(results_df['x_at_max_density'].values,
#                   results_df['median_y'].values,
#                   edgecolor='black', color='navy', zorder=3, label="interpolating points")
# ax[1, 0].plot(df['x_interpolate'], df['y_new'], c="darkorange", zorder=1, lw=3, label="corrected ridgeline")
# ax[1, 0].set_xlabel('relative Teff')
# ax[1, 0].set_ylabel('relative log L')
# # ax[1, 0].legend(loc='upper left')

# ax[1, 1].scatter(df['log_Teff'], df['log_L'], s=s, color='grey', alpha=alpha)
# ax[1, 1].plot(df['x_back'], df['y_back'], color='darkorange', lw=3, label="corrected ridgeline")
# ax[1, 1].invert_xaxis()
# ax[1, 1].set_xlabel(r'$\log T_{\mathrm{eff}}$ [K]')
# ax[1, 1].set_ylabel(r'$\log L\ [L_\odot]$')
# # ax[1, 1].legend()


# plt.tight_layout()

plt.show()

