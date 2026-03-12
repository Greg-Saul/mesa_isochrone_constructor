import pandas as pd
from astroquery.gaia import Gaia
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

class NGC6397:
    def cluster_query():

        name = "NGC6397"

        ra_new = 265.175375
        dec_new = -53.674333

        centerx, centery = -17.600, 3.300

        rad, rad2 = 0, 1.5

        tables = Gaia.load_tables(only_names=True)

        job = Gaia.launch_job_async(
            f"""
            SELECT TOP 10000
                g.source_id,
                g.ra,
                g.dec,
                g.pmra,
                g.pmdec,
                g.phot_g_mean_mag,
                g.bp_rp,
                g.astrometric_params_solved,
                g.phot_g_mean_flux,
                g.phot_bp_mean_flux,
                g.phot_rp_mean_flux,
                g.parallax,
                DISTANCE({ra_new}, {dec_new}, g.ra, g.dec)
            FROM gaiadr3.gaia_source AS g
            JOIN gaiadr3.astrophysical_parameters AS a
                ON g.source_id = a.source_id
            WHERE DISTANCE({ra_new}, {dec_new}, g.ra, g.dec) < 5./60.
                AND g.phot_bp_mean_mag < 20.3
                AND g.astrometric_params_solved != 3
                AND g.parallax > 0
                AND g.parallax_over_error > 3.5
            """
        )

        df = job.get_results().to_pandas()

        distance_sq = (df.pmdec - centerx) ** 2 + (df.pmra - centery) ** 2
        df = df[(distance_sq > rad**2) & (distance_sq < rad2**2)]
        df = df[df['bp_rp'].notna()]

        def c(i_bp, i_rp, i_g):
            return (i_bp + i_rp) / i_g

        c0 = 0.0059898 
        c1 = 8.817481e-11  
        c3 = 7.618399

        def sigma_c(g_m):
            return c0 + c1 * g_m**c3

        def f(g_bprp):
            return (
                1.154360 + 0.033772 * g_bprp + 0.032277 * g_bprp**2
                if g_bprp < 0.5
                else 1.162004 + 0.011464 * g_bprp + 0.049255 * g_bprp**2
            )

        df['c'] = df.apply(lambda row: c(row['phot_bp_mean_flux'], row['phot_rp_mean_flux'], row['phot_g_mean_flux']), axis=1)
        df['sigma_c'] = df['phot_g_mean_mag'].apply(sigma_c)
        df['c_star'] = df['bp_rp'].apply(f)
        df['c_diff'] = df['c'] - df['c_star']

        df = df[(df['c_diff'] >= -df['sigma_c']) & (df['c_diff'] <= df['sigma_c'])]

        fig, ax = plt.subplots(figsize=(8, 12))
        ax.invert_yaxis()
        plt.scatter(df.bp_rp, df.phot_g_mean_mag, s=5, color="gray")

        print(len(df.bp_rp))

        output_file = "NGC6397_gaia_data.csv"
        df[["ra", "dec", "bp_rp", "phot_g_mean_mag", "parallax",]].to_csv(output_file, index=False)

        # plt.show()

    def plot_cluster():

        df = pd.read_csv("dustmap/coords_with_ebv.csv")

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

        df["bp_rp"] = df["bp_rp"] - (1.3 * df["ebv"])
        # print(df.bp_rp)

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

        df[['x_back', 'y_back', 'log_Teff', 'log_L']].to_csv('NGC6397_fine_isochrone.csv', index=False)

        # theory
        # ax.scatter(df['log_Teff'], df['log_L'], s=s, color='grey', alpha=alpha)
        # ax.plot(df['x_back'], df['y_back'], color='darkorange', lw=3, label="corrected ridgeline")
        # ax.invert_xaxis()
        # ax.set_xlabel(r'$\log T_{\mathrm{eff}}$ [K]')
        # ax.set_ylabel(r'$\log L\ [L_\odot]$')

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



n = NGC6397

n.plot_cluster()
