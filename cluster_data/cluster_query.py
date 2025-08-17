import pandas as pd
from astroquery.gaia import Gaia
# from scipy import CubicSpline

# Input Variables
# Example: NGC6397

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
        g.source_id,
        g.ra,
        g.dec,
        g.pmra,
        g.pmdec,
        g.phot_g_mean_mag,
        g.parallax,
        a.teff_gspphot,
        a.lum_flame,
        a.mass_flame
    FROM gaiadr3.gaia_source AS g
    JOIN gaiadr3.astrophysical_parameters AS a
        ON g.source_id = a.source_id
    WHERE DISTANCE({ra_new}, {dec_new}, g.ra, g.dec) < 5./60.
        AND g.phot_bp_mean_mag < 20.3
        AND g.astrometric_params_solved != 3
    """,
    dump_to_file=True
)

# ['source_id', 'ra', 'dec', 'pmra', 'pmdec', 'teff_gspphot', 'phot_g_mean_mag', 'parallax', 'astrometric_params_solved', 'dist']
df = job.get_results().to_pandas()

output_file = f"{name}_gaia_data.csv"
df.to_csv(output_file, index=False)
print(f"Results saved to {output_file}")


