import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df1 = pd.read_csv("csv1.csv")
df2 = pd.read_csv("csv2.csv")

fig, ax = plt.subplots(figsize=(8, 12))
plt.rcParams.update({'font.size': 10})
s = 3
alpha = 0.5
# ax.scatter(df1['bp_rp'], df1['phot_g_mean_mag'], s=s, color='grey', alpha=alpha)
ax.plot(df1['x_back'], df1['y_back'], color='blue', lw=1, label="BP-RP")
ax.plot(df2['x_back'], df2['y_back'], color='darkorange', lw=1, label="(BP-RP) - E(B-V)")
ax.invert_yaxis()
ax.set_xlabel("BP - RP")
ax.set_ylabel("G MAG")
ax.legend()
plt.title("Color Before and After Accounting for Dust")

# ax.scatter(df1['bp_rp'], df1['phot_g_mean_mag'], s=s, color='grey', alpha=alpha)


plt.savefig("save_comparison.png")
plt.show()