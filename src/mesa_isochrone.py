import matplotlib
import tkinter as tk
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
import numpy as np
import os

matplotlib.use('TkAgg')

class isoFns:
    def __init__(self, figsize=(12, 8)):
        """Initialize the HR Diagram plotter"""
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.models = None
        self.min_age_length = None
    
    def load_models(self, model_data):
        """Load stellar evolution models"""
        self.models = model_data
        self._extract_model_properties()
    
    def _extract_model_properties(self):
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
        
        # Trim all arrays to minimum age length
        # for i in range(len(self.models)):
        #     self.temperatures[i] = self.temperatures[i][:self.min_age_length]
        #     self.luminosities[i] = self.luminosities[i][:self.min_age_length]
    
    def plot_evolutionary_tracks(self):
        """Plot the evolutionary tracks for all loaded models"""
        if not self.models:
            raise ValueError("No models loaded. Call load_models() first.")
            
        for i in range(len(self.models)):
            self.ax.plot(self.temperatures[i], 
                        self.luminosities[i], 
                        linewidth=2, 
                        label=f'{self.filenames[i]}')
    
    def plot_isochrone(self, desired_age, custom_color):
        """Plot an isochrone for the specified age"""
        if not self.models:
            raise ValueError("No models loaded. Call load_models() first.")
            
        new_temps = []
        new_lums = []
        
        for i in range(len(self.models)):
            indices = self._find_closest_age_index(self.ages[i], desired_age)
            
            if indices[2] < 10:  # Only use if error < 10%
                new_temps.append(self.temperatures[i][indices[1]])
                new_lums.append(self.luminosities[i][indices[1]])
                # Plot evolutionary track in grey for reference
                # Will change to make optional
                self.ax.plot(self.temperatures[i], 
                             self.luminosities[i], 
                             color='grey')
        
        # Create smooth isochrone using cubic spline
        # Uses a parametric interpolation method to combat nonmonoticity
        t = np.arange(len(new_temps))
        t_fine = np.linspace(0, len(new_temps) - 1, 200)
        
        cs_temp = CubicSpline(t, new_temps)
        cs_lum = CubicSpline(t, new_lums)
        
        temp_smooth = cs_temp(t_fine)
        lum_smooth = cs_lum(t_fine)
        
        # Plot the isochrone
        self.ax.plot(temp_smooth, 
                     lum_smooth, 
                     linestyle='--', 
                     color=custom_color, 
                     label=f'Isochrone {desired_age}')
        
        # Plot the original points
        self.ax.plot(new_temps, new_lums, 'ko')
    
    def show(self):
        """Display the HR diagram with proper formatting"""
        self.ax.invert_xaxis()
        self.ax.set_ylabel('Log Luminosity', fontsize=14)
        self.ax.set_xlabel('Log Effective Temperature', fontsize=14)
        self.ax.set_title('Luminosity vs. Temperature', fontsize=16)
        self.ax.legend(loc="lower left", fontsize=10)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        plt.show()
    
    @staticmethod
    def _find_closest_age_index(age_array, desired_age):
        """Find the index in age_array closest to desired_age"""
        idx = (np.abs(age_array - desired_age)).argmin()
        percent_error = 100 * abs(age_array[idx] - desired_age) / desired_age
        return age_array[idx], idx, percent_error
