import matplotlib
import matplotlib.pyplot as plt
from scipy.interpolate import *
import numpy as np
import pandas as pd
import os
import re
import json
import sys
import shutil
import mplcursors
import time
import cv2
from PIL import Image
import tkinter as tk
from tkinter import filedialog
import pyarrow
from astropy.table import Table

matplotlib.use('TkAgg')

class mesa_isochrone:
    def __init__(self, figsize=(8, 12)):
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.ax.invert_xaxis()
        self.models = None
        self.star_data = pd.DataFrame(columns=['luminosities', 'temperatures', 'ages', 'masses'])
        self.output_path = "../../outputs"
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def load_models(self, model_data):
        self.models = model_data
        self.__extract_model_properties()
    
    def __extract_model_properties(self):
        for model in self.models:
            self.star_data.loc[len(self.star_data)] = {
            'luminosities': model.data('log_L').tolist(),
            'temperatures': model.data('log_Teff').tolist(),
            'ages': model.star_age.tolist(),
            'masses': model.star_mass[0]
            }

    def export(self, file_name, **kwargs):
        file_type = kwargs.get("file_type", "json")
        # star_data = {"lum":self.luminosities, "temp":self.temperatures, "ages":self.ages, "masses":self.masses}
        if file_type == "csv":
            if os.path.exists(file_name):
                overwrite = input("Folder already exists, would you like to overwrite it? enter 'y' for yes: ")
                if overwrite == "y" or overwrite == "Y":
                    shutil.rmtree(file_name)
                else:
                    sys.exit()
            os.makedirs(file_name, exist_ok=True)
            self.star_data["temperatures"].to_csv(file_name + '/temp.csv', index=False, header=False)
            self.star_data["ages"].to_csv(file_name + '/ages.csv', index=False, header=False)
            self.star_data["luminosities"].to_csv(file_name + '/lum.csv', index=False, header=False)
            self.star_data["masses"].to_csv(file_name + '/masses.csv', index=False, header=False)
        elif file_type == "json":
            self.star_data.to_json(f"{self.output_path}/{file_name}.json")
        elif file_type == "parquet":
            self.star_data.to_parquet(f"{file_name}.parquet")
        elif file_type == "fits":
            data = Table.from_pandas(self.star_data)
            data.write(f"{file_name}.fits")


    def export_specific_age(self, desired_age, file_name, reinterp=True, file_type="txt"):
        new_temps = []
        new_lums = []
        masses_used = []

        for i in range(len(self.star_data.ages)):
            self.eliza = False
            if not self.eliza and not reinterp:
                indices = self.__find_closest_age_index(self.star_data.ages[i], desired_age)
                if indices[2] < tolerance:
                    new_temps.append(self.star_data.temperatures[i][indices[1]])
                    new_lums.append(self.star_data.luminosities[i][indices[1]])
                    masses_used.append(self.masses[i])
                    if show_hr:
                        self.ax.plot(self.star_data.temperatures[i], self.star_data.luminosities[i], color='grey')
            elif not self.eliza and reinterp:
                new_temps, new_lums, masses_used = self.find_reinterpolation(desired_age)

        if file_type == "txt":
            with open(file_name, "w") as f:
                f.write("mass temperature luminosity\n")
                for m, t, l in zip(masses_used, new_temps, new_lums):
                    f.write(f"{m} {t} {l}\n")
        elif file_type == "eliza":
            self.eliza == True
            prep = np.array([new_temps, new_lums, masses_used])
            np.savetxt('../../outputs/output.eliza', prep, delimiter=',', fmt='%d', header='Temperature,Luminosity,Mass')
        else:
            print("ERROR: file type invalid")
            

    def extract_file(self, file_name):
        self.eliza = False
        if file_name.endswith(".json"):
            self.star_data = pd.read_json(file_name)
        elif file_name.endswith(".eliza"):
            df = pd.read_csv(file_name)
            self.temperatures = np.array(df["Temperature"])
            self.luminosities = np.array(df["Luminosity"])
            self.masses = np.array(df["Mass"])
            self.ages = np.array(df["age"])
            self.eliza = True
        elif file_name.endswith(".parquet"):
            df = pd.read_parquet(file_name)
        elif os.path.isdir(file_name):
            files = os.listdir(file_name)
            file_type = files[0].split('.')[-1]
            if file_type == "csv":
                temp_df = pd.read_csv(file_name + '/temp.csv', header=None)
                self.temperatures = np.array([row[~np.isnan(row)] for row in temp_df.values])
                age_df = pd.read_csv(file_name + '/ages.csv', header=None)
                self.ages = np.array([row[~np.isnan(row)] for row in age_df.values])
                lum_df = pd.read_csv(file_name + '/lum.csv', header=None)
                self.luminosities = np.array([row[~np.isnan(row)] for row in lum_df.values])
                mass_df = pd.read_csv(file_name + '/masses.csv', header=None)
                self.masses = np.array(mass_df[0])
            elif file_type == "parquet":
                temp_df = pd.read_parquet(file_name + '/temp.parquet')
                self.temperatures = np.array([row[~np.isnan(row)] for row in temp_df.values])
                age_df = pd.read_parquet(file_name + '/ages.parquet')
                self.ages = np.array([row[~np.isnan(row)] for row in age_df.values])
                lum_df = pd.read_parquet(file_name + '/lum.parquet')
                self.luminosities = np.array([row[~np.isnan(row)] for row in lum_df.values])
                mass_df = pd.read_parquet(file_name + '/masses.parquet')
                self.masses = np.array(mass_df.iloc[:, 0])
        else:
            print("ERROR: file type not recognized")
            sys.exit()

    def plot_evolutionary_tracks(self):
        for i in range(len(self.star_data.ages)):
            self.ax.plot(self.star_data.temperatures[i], self.star_data.luminosities[i], linewidth=2)
            self.ax.scatter(self.star_data.temperatures[i], self.star_data.luminosities[i])

    def plot_isochrone(self, filename, desired_age, **kwargs):
        track_color = kwargs.get("track_color", "red")
        resolution = kwargs.get("resolution", 10000)
        tolerance = kwargs.get("tolerance", 1)
        show_hr = kwargs.get("show_hr", False)
        show_points = kwargs.get("show_points", False)
        interp = kwargs.get("interpolation_method", "PCHIP")
        clean = kwargs.get("clean", False)
        reinterp = kwargs.get("reinterpolate", True)
        legend_type = kwargs.get("legend_type", 1)

        self.extract_file(filename)
        print(self.star_data.columns)
        new_temps = []
        new_lums = []
        masses_used = []

        for i in range(len(self.star_data.ages)):
            if show_hr:
                # print(len(self.star_data.temperatures[i]))
                self.ax.plot(self.star_data.temperatures[i], self.star_data.luminosities[i])
            if not self.eliza and not reinterp:
                indices = self.__find_closest_age_index(self.star_data.ages[i], desired_age)
                if indices[2] < tolerance:
                    new_temps.append(self.star_data.temperatures[i][indices[1]])
                    new_lums.append(self.star_data.luminosities[i][indices[1]])
                    masses_used.append(self.star_data.masses[i])
            elif not self.eliza and reinterp:
                new_temps, new_lums, masses_used = self.find_reinterpolation(desired_age)
        if self.eliza:
            new_temps = self.temperatures.copy()
            new_lums = self.luminosities.copy()
            masses_used = self.masses.copy()

        new_temps = np.array(new_temps)
        new_lums = np.array(new_lums)
        masses_used = np.array(masses_used)

        t = np.arange(len(new_temps))
        t_fine = np.linspace(0, len(new_temps) - 1, resolution)
        if interp == "cubic_spline":
            temp = CubicSpline(t, new_temps)
            lum = CubicSpline(t, new_lums)
        elif interp == "PCHIP":
            temp = PchipInterpolator(t, new_temps)
            lum = PchipInterpolator(t, new_lums)
        elif interp == "linear":
            self.ax.plot(new_temps, new_lums, linestyle='--', 
            color=track_color, 
            label="age (years): {:.3e}".format(desired_age))
            if show_points:
                self.ax.plot(new_temps, new_lums, 'ko')
        elif interp == "make_interp_spline":
            temp = make_interp_spline(t, new_temps)
            lum = make_interp_spline(t, new_lums)
        elif interp == "akima":
            temp = Akima1DInterpolator(t, new_temps)
            lum = Akima1DInterpolator(t, new_lums)
        if interp != "linear":
            self.temp_smooth = temp(t_fine)
            self.lum_smooth = lum(t_fine)
            if clean == False:
                if legend_type == 0:
                    self.ax.plot(self.temp_smooth, self.lum_smooth, 
                    color=track_color)
                elif legend_type == 1:
                    self.ax.plot(self.temp_smooth, self.lum_smooth, 
                    color=track_color, 
                    label="age (years): {:.1e}".format(desired_age))
                elif legend_type == 2:
                    self.ax.plot(self.temp_smooth, self.lum_smooth, 
                    color=track_color, 
                    label=f"file: {os.path.basename(filename)}")
            if clean == True:
                self.ax.axis("off")
                self.ax.plot(self.temp_smooth, self.lum_smooth, linewidth=0.1, color="k")
            if show_points:
                sc, = self.ax.plot(new_temps, new_lums, 'ko')
                cursor = mplcursors.cursor(sc, hover=mplcursors.HoverMode.Transient)

                cursor.connect("add", lambda sel: sel.annotation.set_text(
                    f"Mass: {masses_used[sel.index]:.4f} M☉"
                ))
            

    def find_reinterpolation(self, desired_age):
        new_temps = np.array([])
        new_lums = np.array([])
        masses_used = np.array([])

        for i in range(len(self.star_data['ages'])):
            ages = np.array(self.star_data['ages'].iloc[i])
            temps = np.array(self.star_data['temperatures'].iloc[i])
            lums = np.array(self.star_data['luminosities'].iloc[i])

            # Skip tracks that don't cover desired_age
            if desired_age < ages[0] or desired_age > ages[-1]:
                continue

            # Find the bracketing interval
            idx1 = None
            for j in range(len(ages) - 1):
                if ages[j] <= desired_age <= ages[j + 1]:
                    idx1 = j
                    idx2 = j + 1
                    break

            if idx1 is None:
                continue

            age0, age1 = ages[idx1], ages[idx2]
            t1, t2 = temps[idx1], temps[idx2]
            l1, l2 = lums[idx1], lums[idx2]

            w = (desired_age - age0) / (age1 - age0)
            new_temps = np.append(new_temps, t1 + w * (t2 - t1))
            new_lums = np.append(new_lums, l1 + w * (l2 - l1))
            masses_used = np.append(masses_used, self.star_data['masses'].iloc[i])

        return new_temps, new_lums, masses_used

    def show(self, title="Luminosity vs. Temperature"):
        self.ax.set_xlabel(r'$\log T_{\mathrm{eff}}$ [K]')
        self.ax.set_ylabel(r'$\log L\ [L_\odot]$')
        self.ax.set_title(title, fontsize=16)
        self.ax.legend(loc="upper left", fontsize=6)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        plt.show()

    # def show_clean(self):
    #     plt.savefig("clean.png")
    #     plt.show()

    # def gaia_stack(self, filename1, clean=False):
    #     df = pd.read_csv(filename1)
    #     df.dropna(inplace=True)
    #     df.reset_index(drop=True, inplace=True)

    #     if clean:
    #         # self.fig.tight_layout()
    #         self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    #         max_index_gaia = df.x_back.argmax()
    #         max_index_mesa = np.argmax(self.temp_smooth)


    #         self.x_change = self.temp_smooth[max_index_mesa] - df.x_back[max_index_gaia]
    #         self.y_change = self.lum_smooth[max_index_mesa] - df.y_back[max_index_gaia]

    #         self.ax.plot(df['x_back'] + self.x_change, df['y_back'] + self.y_change, color='k',
    #         linewidth=0.1,linestyle='solid')
    #         ##########################################################################
    #         # self.ax.scatter(df['log_Teff'], df['log_L'], s=3, color='blue')
    #         ##########################################################################
    #         # print(df['x_back'][0], df['y_back'][0])
    #         # print(self.temp_smooth[0], self.lum_smooth[0])


    #         self.ax.plot([df['x_back'][0] + self.x_change, self.temp_smooth[0]],
    #         [df['y_back'][0] + self.y_change, self.lum_smooth[0]],
    #         color='k',
    #         linewidth=0.1,
    #         linestyle='solid'
    #         )
    #         self.ax.plot(
    #             [df['x_back'].iloc[-1] + self.x_change, self.temp_smooth[-1]],
    #             [df['y_back'].iloc[-1] + self.y_change, self.lum_smooth[-1]],
    #             color='k',
    #             linewidth=0.1,
    #             linestyle='solid'
    #         )
    #     else:
    #         self.ax.plot(df['x_back'], df['y_back'])

    def save(self, **kwargs):
        image_name = kwargs.get("image_name", "isochrone_diagram")
        title = kwargs.get("title", "Luminosity vs. Temperature")

        self.ax.set_xlabel(r'$\log T_{\mathrm{eff}}$ [K]')
        self.ax.set_ylabel(r'$\log L\ [L_\odot]$')
        self.ax.set_title(title, fontsize=16)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.legend(loc="lower right", fontsize=10)
        plt.savefig(f"{self.output_path}/" + image_name + ".png")

    def __find_closest_age_index(self, age_array, desired_age):
        age_array = np.array(age_array)
        idx = (np.abs(age_array - desired_age)).argmin()
        percent_error = 100 * abs(age_array[idx] - desired_age) / desired_age
        return age_array[idx], idx, percent_error

    def sort_by_mass_key(self, filename):
        match = re.search(r'(?:m|mass)(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)(?:m|mass)', filename, re.IGNORECASE)
        if match:
            return float(match.group(1) or match.group(2))
        return float('inf')

    # # updated 10/19/25
    # def function_summary(self):
    #     print("*default kwarg*\n")
    #     print("- load_models(<list>mesa_data)")
    #     print('''- export(<string>file_name, **kwargs)
    #         <string>file_type - *"csv"*, "json", "parquet"''')
    #     print("- extract_file(<string>file_name)")
    #     print("- plot_evolutionary_track()")
    #     print('''- plot_isochrone(<string>file_name, <float>age, **kwargs)
    #         <string>track_color - *"red"*
    #         <integer>resolution - *1000*
    #         <float>tolerance - *10*
    #         <boolean>show_hr - *True*
    #         <boolean>show_points - *False*
    #         <string>interp - *"cubic_spline"*, "PCHIP", "linear", "akima", "make_interp_spline"''')
    #     print("- show()")
    #     print('''- save(**kwargs)
    #         <string>image_name - *"isochrone_diagram"*''')
    #     print('''- sort_by_mass_key
    #         example usage: <list>file_paths = sorted(<list>file_paths, key=plotter.sort_by_mass_key)''')

    # def fill(self, title):
    #     img = cv2.imread("clean.png")
    #     h, w = img.shape[:2]
    #     mask = np.zeros((h+2, w+2), np.uint8)

    #     cv2.floodFill(img, mask, (1,1), (0,0,255))  # fill from a guaranteed-white point

    #     cv2.imwrite("filled.png", img)

    #     im = Image.open('filled.png')
    #     pixels = im.load()
    #     w, h = im.size

    #     fill = False

    #     im = Image.open("filled.png").convert("RGB")
    #     pixels = im.load()
    #     w, h = im.size

    #     for i in range(w):
    #         for j in range(h):
    #             if pixels[i, j] != (255, 255, 255):
    #                 pixels[i, j] = (0, 0, 0)

    #     im.save("filled.png")


    #     count = 0


    #     for i in range(w):
    #         for j in range(h):
    #             if pixels[i,j] != (0,0,0):
    #                 count += 1

    #     # print(count)
    #     f = open(f"{title}.txt", "w")
    #     f.write(f'''{title} insert unit here
    #     x translation: {self.x_change}
    #     y translation: {self.y_change}
    #     difference: {count} pixels
    #     unit: ({count}, {self.x_change}, {self.y_change})
    #     ''')
    #     f.close()

    def select_files(self):

        root = tk.Tk()
        root.withdraw()

        file_paths = filedialog.askopenfilenames(
            title="Select MESA Files"
        )
        file_paths = list(file_paths)

        file_paths = sorted(file_paths, key=self.sort_by_mass_key)

        return file_paths