import matplotlib
import matplotlib.pyplot as plt
from scipy.interpolate import *
import numpy as np
import os
import pandas as pd
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

matplotlib.use('TkAgg')

class mesa_isochrone:
    def __init__(self, figsize=(8, 12)):
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.models = None
        self.min_age_length = None
        self.ax.invert_xaxis()

    def load_models(self, model_data):
        self.models = None
        self.models = model_data
        self.__extract_model_properties()

    def export(self, filename, **kwargs):
        file_type = kwargs.get("file_type", "csv")
        star_data = {"lum":self.luminosities, "temp":self.temperatures, "ages":self.ages, "masses":self.masses}
        if file_type == "csv":
            if os.path.exists(filename):
                overwrite = input("Folder already exists, would you like to overwrite it? enter 'y' for yes: ")
                if overwrite == "y" or overwrite == "Y":
                    shutil.rmtree(filename)
                else:
                    sys.exit()
            os.makedirs(filename, exist_ok=True)
            df = pd.DataFrame(self.temperatures)
            df.to_csv(filename + '/temp.csv', index=False, header=False)
            df = pd.DataFrame(self.ages)
            df.to_csv(filename + '/ages.csv', index=False, header=False)
            df = pd.DataFrame(self.luminosities)
            df.to_csv(filename + '/lum.csv', index=False, header=False)
            df = pd.DataFrame(self.masses)
            df.to_csv(filename + '/masses.csv', index=False, header=False)
        elif file_type == "json":
            with open(filename, "w") as file:
                json.dump(star_data, file)
        elif file_type == "parquet":
            if os.path.exists(filename):
                overwrite = input("Folder already exists, would you like to overwrite it? enter 'y' for yes: ")
                if overwrite == "y" or overwrite == "Y":
                    shutil.rmtree(filename)
                else:
                    sys.exit()
            os.makedirs(filename)
            df = pd.DataFrame(self.temperatures)
            df.to_parquet(filename + '/temp.parquet')
            df = pd.DataFrame(self.ages)
            df.to_parquet(filename + '/ages.parquet')
            df = pd.DataFrame(self.luminosities)
            df.to_parquet(filename + '/lum.parquet')
            df = pd.DataFrame(self.masses)
            df.to_parquet(filename + '/masses.parquet')

    def extract_file(self, filename):
        self.luminosities = []
        self.temperatures = []
        self.ages = []
        self.masses = []
        self.eliza = False
        if filename.endswith(".json"):
            with open(filename, "r") as file:
                star_data = json.load(file)
            self.luminosities = star_data["lum"]
            self.temperatures = star_data["temp"]
            self.ages = star_data["ages"]
            self.masses = star_data["masses"]
        elif filename.endswith(".eliza"):
            df = pd.read_csv(filename)
            self.temperatures = df["Temperature"]
            self.luminosities = df["Luminosity"]
            self.masses = df["Mass"]
            self.ages = df["age"]
            self.eliza = True
        elif os.path.isdir(filename):
            files = os.listdir(filename)
            if files[0].endswith(".csv"):
                temp_df = pd.read_csv(filename + '/temp.csv', header=None)
                self.temperatures = [row[~np.isnan(row)].tolist() for row in temp_df.values]
                age_df = pd.read_csv(filename + '/ages.csv', header=None)
                self.ages = [row[~np.isnan(row)].tolist() for row in age_df.values]
                lum_df = pd.read_csv(filename + '/lum.csv', header=None)
                self.luminosities = [row[~np.isnan(row)].tolist() for row in lum_df.values]
                mass_df = pd.read_csv(filename + '/masses.csv', header=None)
                self.masses = mass_df[0].tolist()
            if files[0].endswith(".parquet"):
                temp_df = pd.read_parquet(filename + '/temp.parquet')
                self.temperatures = [row[~np.isnan(row)].tolist() for row in temp_df.values]
                age_df = pd.read_parquet(filename + '/ages.parquet')
                self.ages = [row[~np.isnan(row)].tolist() for row in age_df.values]
                lum_df = pd.read_parquet(filename + '/lum.parquet')
                self.luminosities = [row[~np.isnan(row)].tolist() for row in lum_df.values]
                mass_df = pd.read_parquet(filename + '/masses.parquet')
                self.masses = mass_df.iloc[:,0].tolist()
        else:
            print("ERROR: file type not recognized")
            sys.exit()

    def __extract_model_properties(self):
        self.luminosities = []
        self.temperatures = []
        self.masses = []
        self.ages = []
        self.age_lengths = []
        self.filenames = []
        for model in self.models:
            self.luminosities.append(model.data('log_L').tolist())
            self.temperatures.append(model.data('log_Teff').tolist())
            self.masses.append(model.star_mass[0])
            self.ages.append(model.star_age.tolist())
            self.age_lengths.append(len(model.star_age))
            self.filenames.append(os.path.basename(model.file_name))
        self.min_age_length = min(self.age_lengths)

    def plot_evolutionary_tracks(self):
        for i in range(len(self.ages)):
            self.ax.plot(self.temperatures[i], self.luminosities[i], linewidth=2)

    def plot_isochrone(self, filename, desired_age, **kwargs):
        track_color = kwargs.get("track_color", "red")
        resolution = kwargs.get("resolution", 1000)
        tolerance = kwargs.get("tolerance", 10)
        show_hr = kwargs.get("show_hr", True)
        show_points = kwargs.get("show_points", False)
        interp = kwargs.get("interpolation_method", "PCHIP")
        clean = kwargs.get("clean", False)
        reinterp = kwargs.get("reinterpolate", True)

        self.extract_file(filename)

        new_temps = []
        new_lums = []
        masses_used = []
        for i in range(len(self.ages)):
            if not self.eliza and not reinterp:
                indices = self.__find_closest_age_index(self.ages[i], desired_age)
                if indices[2] < tolerance:
                    new_temps.append(self.temperatures[i][indices[1]])
                    new_lums.append(self.luminosities[i][indices[1]])
                    masses_used.append(self.masses[i])
                    if show_hr:
                        self.ax.plot(self.temperatures[i], self.luminosities[i], color='grey')
            elif not self.eliza and reinterp:
                new_temps, new_lums, masses_used = self.find_reinterpolation(desired_age)
            else:
                new_temps = self.temperatures
                new_lums = self.luminosities
                masses_used = self.masses
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
                self.ax.plot(self.temp_smooth, self.lum_smooth, 
                color=track_color, 
                label="age (years): {:.1e}".format(desired_age))
            if clean == True:
                self.ax.axis("off")
                self.ax.plot(self.temp_smooth, self.lum_smooth, linewidth=0.1, color="k")
                # self.fig.tight_layout
            if show_points:
                sc = self.ax.plot(new_temps, new_lums, 'ko')
                # print("Masses for plotted points:", masses_used)
                # print(len(masses_used))
                cursor = mplcursors.cursor(sc, hover=True)
                cursor.connect("add", lambda sel: sel.annotation.set_text(
                    # f""
                    f"Mass: {masses_used[sel.index]:.4f} M☉"
                ))
            

    def find_reinterpolation(self, desired_age):
        new_temps = []
        new_lums = []
        masses_used = []

        for i in range(len(self.ages)):
            ages = self.ages[i]

            for j in range(len(ages) - 1):
                if ages[j] <= desired_age <= ages[j + 1]:
                    idx1 = j
                    idx2 = j + 1
                    break

            age0 = ages[j]
            age1 = ages[j + 1]

            t1 = self.temperatures[i][idx1]
            t2 = self.temperatures[i][idx2]

            l1 = self.luminosities[i][idx1]
            l2 = self.luminosities[i][idx2]

            w = (desired_age - age0) / (age1 - age0)

            interp_temp = t1 + w * (t2 - t1)
            interp_lum  = l1 + w * (l2 - l1)

            new_temps.append(interp_temp)
            new_lums.append(interp_lum)
            masses_used.append(self.masses[i])

        return new_temps, new_lums, masses_used

    def show(self):
        self.ax.set_xlabel(r'$\log T_{\mathrm{eff}}$ [K]')
        self.ax.set_ylabel(r'$\log L\ [L_\odot]$')
        # self.ax.set_title('Luminosity vs. Temperature', fontsize=16)
        self.ax.legend(loc="lower right", fontsize=10)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        plt.show()

    def show_clean(self):
        plt.savefig("clean.png")
        plt.show()

    def gaia_stack(self, filename1, clean=False):
        df = pd.read_csv(filename1)
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)

        if clean:
            # self.fig.tight_layout()
            self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
            max_index_gaia = df.x_back.argmax()
            max_index_mesa = np.argmax(self.temp_smooth)


            self.x_change = self.temp_smooth[max_index_mesa] - df.x_back[max_index_gaia]
            self.y_change = self.lum_smooth[max_index_mesa] - df.y_back[max_index_gaia]

            self.ax.plot(df['x_back'] + self.x_change, df['y_back'] + self.y_change, color='k',
            linewidth=0.1,linestyle='solid')
            ##########################################################################
            # self.ax.scatter(df['log_Teff'], df['log_L'], s=3, color='blue')
            ##########################################################################
            # print(df['x_back'][0], df['y_back'][0])
            # print(self.temp_smooth[0], self.lum_smooth[0])


            self.ax.plot([df['x_back'][0] + self.x_change, self.temp_smooth[0]],
            [df['y_back'][0] + self.y_change, self.lum_smooth[0]],
            color='k',
            linewidth=0.1,
            linestyle='solid'
            )
            self.ax.plot(
                [df['x_back'].iloc[-1] + self.x_change, self.temp_smooth[-1]],
                [df['y_back'].iloc[-1] + self.y_change, self.lum_smooth[-1]],
                color='k',
                linewidth=0.1,
                linestyle='solid'
            )
        else:
            self.ax.plot(df['x_back'], df['y_back'])

    def save(self, **kwargs):
        image_name = kwargs.get("image_name", "isochrone_diagram")
        self.ax.set_xlabel(r'$\log T_{\mathrm{eff}}$ [K]')
        self.ax.set_ylabel(r'$\log L\ [L_\odot]$')
        self.ax.set_title('Luminosity vs. Temperature', fontsize=16)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.legend(loc="lower right", fontsize=10)
        plt.savefig(image_name + ".png")

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

    # updated 10/19/25
    def function_summary(self):
        print("*default kwarg*\n")
        print("- load_models(<list>mesa_data)")
        print('''- export(<string>file_name, **kwargs)
            <string>file_type - *"csv"*, "json", "parquet"''')
        print("- extract_file(<string>file_name)")
        print("- plot_evolutionary_track()")
        print('''- plot_isochrone(<string>file_name, <float>age, **kwargs)
            <string>track_color - *"red"*
            <integer>resolution - *1000*
            <float>tolerance - *10*
            <boolean>show_hr - *True*
            <boolean>show_points - *False*
            <string>interp - *"cubic_spline"*, "PCHIP", "linear", "akima", "make_interp_spline"''')
        print("- show()")
        print('''- save(**kwargs)
            <string>image_name - *"isochrone_diagram"*''')
        print('''- sort_by_mass_key
            example usage: <list>file_paths = sorted(<list>file_paths, key=plotter.sort_by_mass_key)''')

    def temp(self, filename):
        im = Image.open(filename)
        pixels = im.load()
        w, h = im.size

        fill = False

        for i in range(w):
            for j in range(h):
                print("")

    def fill(self, title):
        img = cv2.imread("clean.png")
        h, w = img.shape[:2]
        mask = np.zeros((h+2, w+2), np.uint8)

        cv2.floodFill(img, mask, (1,1), (0,0,255))  # fill from a guaranteed-white point

        cv2.imwrite("filled.png", img)

        im = Image.open('filled.png')
        pixels = im.load()
        w, h = im.size

        fill = False

        im = Image.open("filled.png").convert("RGB")
        pixels = im.load()
        w, h = im.size

        for i in range(w):
            for j in range(h):
                if pixels[i, j] != (255, 255, 255):
                    pixels[i, j] = (0, 0, 0)

        im.save("filled.png")


        count = 0


        for i in range(w):
            for j in range(h):
                if pixels[i,j] != (0,0,0):
                    count += 1

        # print(count)
        f = open(f"{title}.txt", "w")
        f.write(f'''{title} insert unit here
        x translation: {self.x_change}
        y translation: {self.y_change}
        difference: {count} pixels
        unit: ({count}, {self.x_change}, {self.y_change})
        ''')
        f.close()

    def select_files(self):

        root = tk.Tk()
        root.withdraw()

        file_paths = filedialog.askopenfilenames(
            title="Select MESA Files"
        )
        file_paths = list(file_paths)

        file_paths = sorted(file_paths, key=self.sort_by_mass_key)

        return file_paths