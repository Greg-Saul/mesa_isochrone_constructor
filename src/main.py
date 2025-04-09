from mesa_reader import MesaData
import isoFns as iso

md = []
name = ["0.5mass", "0.7mass", "0.9mass", "1mass", "1.2mass", "1.4mass", 
        "1.6mass", "1.8mass", "2mass", "2.2mass", "2.4mass", "2.6mass", "3mass", "4mass", 
        "5mass", "6mass", "7mass", "8mass", "9mass", "10mass"]

# fill the md array with MESA tracks using mesa_reader
for i in range(len(name)):
  md.append(MesaData('gregsWork/work/LOGS/' + name[i] + '.data'))

# iso.hr(md) # plots a simple hr diagram
iso.isochrone(md, 1e8, 'red')  # plots an isochrone for 100 megayears
iso.isochrone(md, 3.16e8, 'orange')  # plots an isochrone for 316 megayears
iso.isochrone(md, 1e9, 'green')  # plots an isochrone for 1 gigayear
iso.isochrone(md, 3.16e9, 'blue')  # plots an isochrone for 3.16 gigayears
iso.isochrone(md, 1e10, 'purple')  # plots an isochrone for 10 gigiyears
iso.show_plot()  # shows the plots
