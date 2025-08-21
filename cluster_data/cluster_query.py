import pandas as pd
from astroquery.gaia import Gaia
import numpy as np

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
    SELECT
        a.teff_gspphot,
        a.lum_flame,
        a.mass_flame
    FROM gaiadr3.gaia_source AS g
    JOIN gaiadr3.astrophysical_parameters AS a
        ON g.source_id = a.source_id
    WHERE DISTANCE({ra_new}, {dec_new}, g.ra, g.dec) < 5./60.
        AND g.astrometric_params_solved != 3
    """,
    dump_to_file=True
)

df = job.get_results().to_pandas()

df['log_L'] = np.where(df['lum_flame'] > 0, np.log10(df['lum_flame']), np.nan)
df['log_Teff'] = np.where(df['teff_gspphot'] > 0, np.log10(df['teff_gspphot']), np.nan)

df = df.dropna()

log_output_file = "NGC6397_gaia_data_log_format.csv"

df[["log_L", "log_Teff", "mass_flame"]].to_csv(log_output_file, index=False)