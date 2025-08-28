import pandas as pd
from astroquery.gaia import Gaia
import numpy as np
import matplotlib.pyplot as plt

name = "NGC6397"

# Galactic coordinates of the globular cluster
# Example: Aladin lite can search the cluster by target identifier: https://aladin.cds.unistra.fr/AladinLite/
ra_new = 265.175375
dec_new = -53.674333

# Proper motion coordinates of the cluster
# Example database: https://simbad.u-strasbg.fr/simbad/sim-basicIdent=m33&submit=SIMBAD+search
centerx, centery = -17.600	, 3.300	

# Cutoff radius in the proper motion space 
# rad is the distance from the center of the cluster, rad2 is the radius of the circle within which we keep the members
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
    """
)


df = job.get_results().to_pandas()

# Compute squared distance for filtering
distance_sq = (df.pmdec - centerx) ** 2 + (df.pmra - centery) ** 2
df = df[(distance_sq > rad**2) & (distance_sq < rad2**2)]

# Filter out rows with NaN in 'bp_rp'
df = df[df['bp_rp'].notna()]

def c(i_bp, i_rp, i_g):
    return (i_bp + i_rp) / i_g

# Constants
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

# Apply filtering: Keep rows where c_diff is within ±sigma_c 
df = df[(df['c_diff'] >= -df['sigma_c']) & (df['c_diff'] <= df['sigma_c'])]
fig, ax = plt.subplots(figsize=(8, 12))
ax.invert_yaxis()
plt.scatter(df.bp_rp, df.phot_g_mean_mag, s=5, color="gray")

output_file = "NGC6397_gaia_data.csv"
df[["bp_rp", "phot_g_mean_mag", "parallax"]].to_csv(output_file, index=False)

plt.show()