# py_mesa_interpolation

### sample usage of isoFns.py

```
from mesa_reader import MesaData
import isoFns as iso

md = []
name = ["0.5mass", "0.7mass", "0.9mass", "1mass", "1.2mass", "1.4mass", 
        "1.6mass", "1.8mass", "2mass", "2.2mass", "2.4mass", "2.6mass", "3mass", "4mass", 
        "5mass", "6mass", "7mass", "8mass", "9mass", "10mass"]


for i in range(len(name)):
  md.append(MesaData('gregsWork/work/LOGS/' + name[i] + '.data'))

iso.hr(md)
iso.isochrone(md, 1e8, 'red')
iso.isochrone(md, 3.16e8, 'orange')
iso.isochrone(md, 1e9, 'green')
iso.isochrone(md, 3.16e9, 'blue')
iso.isochrone(md, 1e10, 'purple')
iso.show_plot()
```
