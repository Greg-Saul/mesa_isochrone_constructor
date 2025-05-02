from mesa_reader import MesaData
from mesa_isochrone import mesa_isochrone

# Initialize and load data
plotter = mesa_isochrone()
md = []
name = ["0.5mass", "0.7mass", "0.9mass", "1mass", "1.2mass", "1.4mass", 
        "1.6mass", "1.8mass", "2mass", "2.2mass", "2.4mass", "2.6mass", 
        "3mass", "4mass", "5mass", "6mass", "7mass", "8mass", "9mass", "10mass"]

for n in name:
    md.append(MesaData('gregsWork/work/LOGS/' + n + '.data'))

plotter.load_models(md)

# Add isochrones
plotter.plot_isochrone(1e8, track_color='green')
plotter.plot_isochrone(3.16e8, track_color='orange')
plotter.plot_isochrone(1e9, track_color='green')
plotter.plot_isochrone(3.16e9, track_color='blue')
plotter.plot_isochrone(1e10, track_color='purple')

# Show plot
plotter.show()
