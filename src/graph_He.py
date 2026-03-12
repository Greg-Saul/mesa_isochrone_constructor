from mesa_reader import MesaData
from mesa_isochrone import mesa_isochrone
import glob
import time
import matplotlib.pyplot as plt
import numpy as np

md = MesaData("./data/sun/1_m_0.014_z.data")

# plt.plot(md.data('model_number'), 1-md.data('he_core_mass'))
plt.plot(md.data('model_number'), md.data('he_core_mass'))
# plt.plot(md.data('model_number'), np.log(md.data('star_age')))
plt.show()
