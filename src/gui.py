import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from mesa_isochrone import mesa_isochrone
from mesa_reader import MesaData
import os

plotter = mesa_isochrone()
selected_files = []

def open_file_explorer():
    file_paths = filedialog.askopenfilenames(
        title="Select Files",
        filetypes=[("MESA Data Files", "*.data")]
    )
    if file_paths:
        selected_files.extend(file_paths)
        update_file_list()

def update_file_list():
    file_list.delete(0, tk.END)
    for file in selected_files:
        file_list.insert(tk.END, os.path.basename(file))

def load_models():
    if len(selected_files) < 3:
        messagebox.showerror("Error", "Please select at least 3 files.")
        return
    try:
        models = [MesaData(path) for path in selected_files]
        plotter.load_models(models)
        messagebox.showinfo("Success", "Models loaded successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load models: {str(e)}")

def add_isochrone():
    try:
        age = simpledialog.askfloat("Add Isochrone", "Enter desired age (in years):")
        if age is None:
            return
        color = simpledialog.askstring("Add Isochrone", "Enter color for isochrone:", initialvalue="red")
        plotter.plot_isochrone(age, track_color=color or "red", resolution=1000)
        messagebox.showinfo("Success", f"Isochrone for age {age} added.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add isochrone: {str(e)}")

def save_plot():
    file_path = filedialog.asksaveasfilename(
        title="Save Plot",
        defaultextension=".png",
        filetypes=[("PNG Files", "*.png")]
    )
    if not file_path:
        return
    try:
        plotter.save(image_name=os.path.splitext(file_path)[0])
        messagebox.showinfo("Success", f"Plot saved to {file_path}.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save plot: {str(e)}")

def show_plot():
    try:
        plotter.show()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to display plot: {str(e)}")

def reset_gui():
    global plotter, selected_files
    selected_files.clear()
    update_file_list()
    plotter = mesa_isochrone()
    messagebox.showinfo("Reset", "GUI and plotter reset to initial state.")

root = tk.Tk()
root.title("Mesa Isochrone GUI")
root.geometry("600x600")

open_button = tk.Button(root, text="Select Files", command=open_file_explorer)
open_button.pack(pady=10)

file_list_frame = tk.Frame(root)
file_list_frame.pack(pady=10)
file_list_scrollbar = tk.Scrollbar(file_list_frame, orient=tk.VERTICAL)
file_list = tk.Listbox(file_list_frame, height=10, width=50, yscrollcommand=file_list_scrollbar.set)
file_list_scrollbar.config(command=file_list.yview)
file_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
file_list.pack(side=tk.LEFT)

load_button = tk.Button(root, text="Load Models", command=load_models)
load_button.pack(pady=10)

add_isochrone_button = tk.Button(root, text="Add Isochrone", command=add_isochrone)
add_isochrone_button.pack(pady=10)

save_button = tk.Button(root, text="Save Plot", command=save_plot)
save_button.pack(pady=10)

show_button = tk.Button(root, text="Show Plot", command=show_plot)
show_button.pack(pady=10)

reset_button = tk.Button(root, text="Reset", command=reset_gui, bg="red", fg="white")
reset_button.pack(pady=10)

root.mainloop()
