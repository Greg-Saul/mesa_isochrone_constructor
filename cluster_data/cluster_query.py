import pandas as pd
from astroquery.gaia import Gaia
import numpy as np
import matplotlib.pyplot as plt

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
df[["bp_rp", "phot_g_mean_mag", "parallax"]].to_csv(output_file, index=False)

# plt.show()
