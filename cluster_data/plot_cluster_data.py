import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline


# Read the CSV file with specified columns
df = pd.read_csv("NGC6397_gaia_data_mesa_format.csv")

df = df.sort_values(by='mass_flame', ascending=True, na_position='last')

# print(df.lum_flame, df.log_Teff, df.log_L)

t = np.arange(len(df.log_L))
t_fine = np.linspace(0, len(df.log_L) - 1, 100000)

fx = CubicSpline(t, df.log_Teff)
fy = CubicSpline(t, df.log_L)

newx = fx(t_fine)
newy = fy(t_fine)

plt.plot(newx, newy)
plt.show()

# # Drop rows with missing values
# df = df.dropna()

# # Convert lum_flame and teff_gspphot to log_L and log_Teff
# # Handle invalid values (e.g., non-positive values) by setting to NaN
# df['log_L'] = np.where(df['lum_flame'] > 0, np.log10(df['lum_flame']), np.nan)
# df['log_Teff'] = np.where(df['teff_gspphot'] > 0, np.log10(df['teff_gspphot']), np.nan)

# # Print the relevant columns
# print(df[['lum_flame', 'mass_flame', 'teff_gspphot', 'log_L', 'log_Teff']])

# # Save the DataFrame to a new CSV file
# output_file = "NGC6397_gaia_data_mesa_format.csv"
# df.to_csv(output_file, index=False)
# print(f"Results saved to {output_file}")