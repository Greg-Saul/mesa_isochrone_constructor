import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.nonparametric.smoothers_lowess import lowess
from scipy.interpolate import CubicSpline, interp1d
from astropy.coordinates import SkyCoord
import astropy.units as u
from dustmaps.config import config
from dustmaps.bayestar import BayestarQuery, fetch
import os

class Collection:
    def __init__(self):
        self.file = "./dustmap/csv_with_dust/M92_with_dust.csv"

    def plot_cluster(self):

        df = pd.read_csv(f"{self.file}")

        df["bp_rp"] = df.bp_rp +  1.29 * df.ebv_bayestar

        def calculate_teff(bp_rp):
            a = 0.00017
            b = 0.00014
            c = 0.000045
            teff = 1 / (a + b * bp_rp + c * bp_rp**2)
            return np.log10(teff)

        def compute_log_luminosity(g_mag, parallax):
            d = 1000 / parallax
            abs_mag = g_mag - 5 * np.log10(d) + 5
            M_sun = 4.67
            log_L = (abs_mag - M_sun)/-2.5
            return log_L

        # Keep track of this. 
        df["bp_rp"] = calculate_teff(df["bp_rp"])
        df["phot_g_mean_mag"] = compute_log_luminosity(df["phot_g_mean_mag"], df["parallax"])

        df = df.dropna(subset=["bp_rp", "phot_g_mean_mag"])


        df = df.sort_values("phot_g_mean_mag")
        df[["ridge_Teff", "ridge_L"]] = lowess(df["bp_rp"], df["phot_g_mean_mag"], frac=0.2)[:, [1, 0]]

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

        df[["x_new", "y_new"]] = np.column_stack(
            rotate_points(df["bp_rp"] - df["ridge_Teff"],
                        df["phot_g_mean_mag"] - df["ridge_L"],
                        df["ridge_Teff"], df["ridge_L"])
        )
        df["x_new0"] = 0
        df = df.sort_values("y_new")

        # bins = [11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5, 19.5, 20.5, 21]
        bins = np.linspace(df.y_new.min() + 1.2, df.y_new.max() - 1, 10)
        print(bins)
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

        cs = CubicSpline(y_sorted, x_sorted)
        mask = (df["y_new"] >= bins[0]) & (df["y_new"] < bins[-1])
        df.loc[mask, "x_interpolate"] = cs(df.loc[mask, "y_new"])
        df.loc[~mask, "x_interpolate"] = np.nan

        df["x_back"], df["y_back"] = rotate_points(
            df["x_interpolate"], df["y_new"] - df["ridge_L"],
            df["ridge_Teff"], df["ridge_L"], inverse=True
        )
        df["x_back"] += df["ridge_Teff"]
        df["y_back"] += df["ridge_L"]

        # Keep track of this
        # df["log_teff_back"] = calculate_teff(df["x_back"])
        # df["log_L_back"] = compute_log_luminosity(df["y_back"], df["parallax"])

        df_sorted = df[["x_back", "y_back"]].dropna().sort_values("y_back").reset_index(drop=True)
        x_sorted = df_sorted["x_back"].values
        y_sorted = df_sorted["y_back"].values
        linear_interp = interp1d(y_sorted, x_sorted, kind="linear", fill_value="extrapolate")

        y_fine = np.linspace(y_sorted.min(), y_sorted.max(), 5000)
        x_fine = linear_interp(y_fine)

        df.to_csv("csv2.csv")

        plt.rcParams.update({'font.size': 10})
        s = 3
        alpha = 0.5

        # fig, ax = plt.subplots(2, 2, figsize=(18, 16))

        # ax[0, 0].scatter(df['bp_rp'], df['phot_g_mean_mag'], s=s, c='grey', alpha=alpha)
        # ax[0, 0].plot(df['ridge_Teff'], df['ridge_L'], c="black", lw=3)
        # ax[0, 0].invert_yaxis()
        # ax[0, 0].set_xlabel("BP - RP")
        # ax[0, 0].set_ylabel("G")

        # ax[0, 1].scatter(df['x_new'], df['y_new'], s=s, color='grey', alpha=alpha)
        # ax[0, 1].plot(df['x_new0'], df['y_new'], c="black", lw=3)
        # ax[0, 1].set_xlabel('relative color')
        # ax[0, 1].set_ylabel('relative G')

        # ax[1, 0].scatter(df['x_new'], df['y_new'], s=s, color='grey', alpha=alpha)
        # ax[1, 0].scatter(results_df['x_at_max_density'].values,
        #                   results_df['median_y'].values,
        #                   edgecolor='black', color='navy', zorder=3)
        # ax[1, 0].plot(df['x_interpolate'], df['y_new'], c="darkorange", zorder=1, lw=3)
        # ax[1, 0].set_xlabel('relative color')
        # ax[1, 0].set_ylabel('relative G')

        # ax[1, 1].scatter(df['bp_rp'], df['phot_g_mean_mag'], s=s, color='grey', alpha=alpha)
        # ax[1, 1].plot(df['x_back'], df['y_back'], color='darkorange', lw=3)
        # ax[1, 1].invert_yaxis()
        # ax[1, 1].set_xlabel("BP - RP")
        # ax[1, 1].set_ylabel("G")

        # plt.tight_layout()
        # plt.savefig("save2.png")
        # plt.show()

        fig, ax = plt.subplots(figsize=(8, 12))

        # ax.scatter(df['bp_rp'], df['phot_g_mean_mag'], s=s, color='grey', alpha=alpha)
        ax.invert_xaxis()
        # ax.scatter(df['x_back'], df['y_back'], s=s)
        ax.plot(df['x_back'], df['y_back'], color='darkorange', lw=2)
        # ax.plot(df['log_teff'], df['log_L'])
        # ax.invert_yaxis()
        # ax.set_xlabel("BP - RP")
        # ax.set_ylabel("G")

        # plt.savefig("save.png")

        plt.scatter(calculate_teff(df.bp_rp), compute_log_luminosity(df.phot_g_mean_mag, df.parallax), s=s, c='grey', alpha=alpha)
        plt.show()

    def proper_motion_cuts(self, in_file):
        df = pd.read_csv(in_file)
        before_cuts = len(df["pmra"])

        pmra_mean = df["pmra"].mean()
        pmdec_mean = df["pmdec"].mean()

        pmra_std = df["pmra"].std()
        pmdec_std = df["pmdec"].std()


        # print("std", std)

        df.drop(df[df['pmra'] < (pmra_mean - pmra_std)].index, inplace=True)
        df.drop(df[df['pmra'] > (pmra_mean + pmra_std)].index, inplace=True)
        df.drop(df[df['pmdec'] < (pmdec_mean - pmdec_std)].index, inplace=True)
        df.drop(df[df['pmdec'] > (pmdec_mean + pmdec_std)].index, inplace=True)

        after_cuts = len(df["pmra"])

        print("before", before_cuts)
        print("after", after_cuts)
        print("Items cut", before_cuts - after_cuts)

        df.to_csv("clustercsv/after_cuts.csv")






n = Collection()
# n.proper_motion_cuts("clustercsv/rawM92.csv")
# n.cluster_query()
n.plot_cluster()
