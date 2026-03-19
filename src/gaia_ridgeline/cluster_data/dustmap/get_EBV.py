import astropy.units as u
from astropy.table import Table
from astropy.coordinates import SkyCoord
from dustmaps.bayestar import BayestarQuery

data = Table.read('../clustercsv/M92clean.csv')

coords = SkyCoord(
    ra=data['ra'] * u.deg,
    dec=data['dec'] * u.deg,
    distance=(1000 / data['parallax']) * u.pc
)

bayestar = BayestarQuery(version='bayestar2019')

ebv = bayestar(coords, mode='median')

data['ebv_bayestar'] = ebv

data.write('csv_with_dust/M92_with_dust.csv', overwrite=True)

print("Query complete. Results saved")