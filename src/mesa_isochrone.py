import matplotlib
import matplotlib.pyplot as plt
from scipy.interpolate import *
import numpy as np
import os
import pandas as pd
import re

matplotlib.use('TkAgg')

class mesa_isochrone:
    def __init__(self, figsize=(8, 12)):
        """Initialize the HR Diagram plotter"""
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.models = None
        self.min_age_length = None
        self.ax.invert_xaxis()

    
    def load_models(self, model_data):
        """Load stellar evolution models"""
        self.models = model_data
        self.__extract_model_properties()

    def md_to_csv(self, filename):
        os.makedirs(filename, exist_ok=True)
        df = pd.DataFrame(self.temperatures)
        df.to_csv(filename + '/temp.csv', index=False, header=False)
        df = pd.DataFrame(self.ages)
        df.to_csv(filename + '/ages.csv', index=False, header=False)
        df = pd.DataFrame(self.luminosities)
        df.to_csv(filename + '/lum.csv', index=False, header=False)

    def extract_csv(self, foldername):
        self.luminosities = []
        self.temperatures = []
        self.ages = []

        temp_df = pd.read_csv(foldername + '/temp.csv', header=None)
        self.temperatures = [
            row[~np.isnan(row)].tolist() for row in temp_df.values
        ]

        age_df = pd.read_csv(foldername + '/ages.csv', header=None)
        self.ages = [
            row[~np.isnan(row)].tolist() for row in age_df.values
        ]

        lum_df = pd.read_csv(foldername + '/lum.csv', header=None)
        self.luminosities = [
            row[~np.isnan(row)].tolist() for row in lum_df.values
        ]
    
    def __extract_model_properties(self):
        """Extract common properties from all models"""
        self.luminosities = []
        self.temperatures = []
        self.masses = []
        self.ages = []
        self.age_lengths = []
        self.filenames = []
        
        for model in self.models:
            self.luminosities.append(model.data('log_L'))
            self.temperatures.append(model.data('log_Teff'))
            self.masses.append(model.star_mass[0])
            self.ages.append(model.star_age)
            self.age_lengths.append(len(model.star_age))
            self.filenames.append(os.path.basename(model.file_name))
        
        self.min_age_length = min(self.age_lengths)
    
    def plot_evolutionary_tracks(self):
        """Plot the evolutionary tracks for all loaded models"""
            
        for i in range(len(self.ages)):
            self.ax.plot(self.temperatures[i], 
                        self.luminosities[i], 
                        linewidth=2)
    
    def plot_isochrone(self, desired_age, **kwargs):
        """Plot an isochrone for the specified age"""

        track_color = kwargs.get("track_color", "red")
        resolution = kwargs.get("resolution", 100)
        tolerance = kwargs.get("tolerance", 10)
        show_hr = kwargs.get("show_hr", True)
        show_points = kwargs.get("show_points", False)
        interp = kwargs.get("interpolation_method", "cubic_spline")
            
        new_temps = []
        new_lums = []
        
        for i in range(len(self.ages)):
            indices = self.__find_closest_age_index(self.ages[i], desired_age)
            
            if indices[2] < tolerance:  # Only use if error < 10%
                new_temps.append(self.temperatures[i][indices[1]])
                new_lums.append(self.luminosities[i][indices[1]])
                # Plot evolutionary track in grey for reference
                # Will change to make optional
                if show_hr:
                    self.ax.plot(self.temperatures[i], 
                                self.luminosities[i], 
                                color='grey')
        
        # Create smooth isochrone using cubic spline
        # Uses a parametric interpolation method to combat nonmonoticity
        t = np.arange(len(new_temps))
        t_fine = np.linspace(0, len(new_temps) - 1, resolution)
        
        #this uses the cubic spline interpolation method -- default
        if interp == "cubic_spline":
            temp = CubicSpline(t, new_temps)
            lum = CubicSpline(t, new_lums)
        # this uses the linear interpolationvmethod
        elif interp == "PCHIP":
            temp = PchipInterpolator(t, new_temps)
            lum = PchipInterpolator(t, new_lums)	
        
        temp_smooth = temp(t_fine)
        lum_smooth = lum(t_fine)
        
        # Plot the isochrone
        self.ax.plot(temp_smooth, 
                     lum_smooth, 
                     linestyle='--', 
                     color=track_color, 
                     label= "age (years): " + "{:,}".format(desired_age))
        
        # Plot the original points
        if show_points:
            self.ax.plot(new_temps, new_lums, 'ko')
    
    def show(self):
        """Display the HR diagram with proper formatting"""
        # self.ax.invert_xaxis()
        self.ax.set_ylabel('Log Luminosity', fontsize=14)
        self.ax.set_xlabel('Log Effective Temperature', fontsize=14)
        self.ax.set_title('Luminosity vs. Temperature', fontsize=16)
        self.ax.legend(loc="lower right", fontsize=10)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        plt.show()

    def save(self, **kwargs):
        """Display the HR diagram with proper formatting"""
        image_name = kwargs.get("image_name", "isochrone_diagram")

        # self.ax.invert_xaxis()
        self.ax.set_ylabel('Log Luminosity', fontsize=14)
        self.ax.set_xlabel('Log Effective Temperature', fontsize=14)
        self.ax.set_title('Luminosity vs. Temperature', fontsize=16)
        self.ax.legend(loc="lower right", fontsize=10)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        plt.savefig(image_name + ".png", dpi=300)
    
    @staticmethod
    def __find_closest_age_index(age_array, desired_age):
        """Find the index in age_array closest to desired_age"""
        age_array = np.array(age_array)
        idx = (np.abs(age_array - desired_age)).argmin()
        percent_error = 100 * abs(age_array[idx] - desired_age) / desired_age
        return age_array[idx], idx, percent_error

    def sort_by_mass_key(self, filename):
        match = re.search(r'(\d+(?:\.\d+)?)(?:m|mass)|(?:m|mass)(\d+(?:\.\d+)?)', filename, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return float('inf')
    
