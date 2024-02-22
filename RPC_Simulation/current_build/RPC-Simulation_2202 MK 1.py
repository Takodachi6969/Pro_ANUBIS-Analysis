###################################################################################################################
#The Purpose of this code is to simulate the passage and detection of Muons through a layered RPC Tracking station#
###################################################################################################################

#Generate Muon population.
#Generate random velocity from zenith angle distribution.
#Measure efficiency of single RPC in lab using scintillator and RPC setup.

import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy.optimize import curve_fit

# Setting the Seaborn theme
sns.set_theme(style="darkgrid")

class RPC:

    def __init__(self,gas_mixture,efficiency,dimensions,height,voltage):

        self.gas_mixture = gas_mixture
        #Enter gas mixture as array from GUI

        self.efficiency = efficiency
        #Enter empirically determined efficiency of RPC
        #Clustering ?

        self.dimensions = dimensions
        #Dimensions of RPC 

        self.height = height
        #Z position of this specific RPC.

        self.voltage = voltage
        #Voltage applied across electrodes in the RPC, measuredin kV.

    #RPC will have attributes of dimensions, efficiency, gas mixture etc...
    #Use Garfield++ to find breakdown voltages of gas mixture
    #Experimentally determine which breakdown voltage would be good to use. 

    #Prompt for gas mixture, prompt for voltage for each detector would be good. 
    #Coordinates for RPCs.


    #Use GUI interface, generate stack of RPCs, choose gas mixtures and voltages for each. Run simulation of muon count.
        
class RPCSimulatorApp:

    def __init__(self, master):

        self.master = master
        master.title("RPC Tracking station simulation")

        # Frame for RPC Input
        self.frame = ttk.Frame(master)
        self.frame.pack(padx=10, pady=10)

        # #Input how many RPC Plates you would like.

        # self.Number_RPCs = tk.IntVar()
        # self.Number_RPCs = ttk.Entry(self.frame, textvariable = self.Number_RPCs)
        # self.Number_RPCs.pack(pady=5)
        # self.Number_RPCs_label = ttk.Label(self.frame, text= "How many RPCs would you like to simulate: ")
        # self.Number_RPCs_label.pack(pady=5)

        # Button to start generating RPC list
        self.load_button = ttk.Button(self.frame, text="Add RPC plate", command=self.create_rpc_window)
        self.load_button.pack(pady=5)

        # Array to store RPC objects
        self.rpc_list = []

        # Button to calculate results, disabled initially
        self.calc_button = ttk.Button(self.frame, text="Calculate efficiencies", state='disabled', command=self.calc_efficiences)
        self.calc_button.pack(pady=5)

        self.plot_button = ttk.Button(self.frame, text="Plot the RPC Setup", state='disabled', command=self.plot_stations)
        self.plot_button.pack(pady=5)

        self.view_log_button = ttk.Button(self.frame, text="View RPC Log", command=self.view_log)
        self.view_log_button.pack(pady=5)


        
        #Calculate the track reconstruction efficiencies.
        #Hit reconstruction efficiencies. 

    #Allowing the entered RPC plates to be shown
    def show_entry(self, var, widget):
        #Decide whether or not to enable a widget passed on a user checkbox
        if var.get():
            widget.configure(state='normal')
        else:
            widget.configure(state='disabled')
    #Allowing new RPC plates to be created
    def create_rpc_window(self):
        rpc_window = tk.Toplevel(self.master)
        rpc_window.title("Add RPC Plate")

        # Generate UI elements for RPC attributes
        self.create_rpc_attributes_ui(rpc_window)

        save_button = ttk.Button(rpc_window, text="Save RPC", command=lambda: self.save_rpc(rpc_window))
        save_button.pack(pady=5) 
    #Allowing the RPC plate list to be updated by modify the logging to include a unique identifier and update the dropdown menu
    def update_rpc_list(self):
        self.rpc_combobox['values'] = [f"RPC {idx+1}: Height={rpc.height}m, Dimensions={rpc.dimensions}m" for idx, rpc in enumerate(self.rpc_list)]
        if self.rpc_list:
            self.rpc_combobox.current(0)
    #Allowing RPC plates to be removed
    def remove_rpc(self):
        current_selection = self.rpc_combobox.current()
        if current_selection >= 0:  # Ensure there is a selection
            removed_rpc = self.rpc_list.pop(current_selection)
            self.update_rpc_list()  # Update the dropdown list
            # Optionally, log the removal
            with open("rpc_log.txt", "a") as log_file:
                log_file.write(f"Removed RPC Plate - Height: {removed_rpc.height}m, Dimensions: {removed_rpc.dimensions}m\n")
    #Allowing RPC attributes to be created using combobox
    def create_rpc_attributes_ui(self, rpc_window):


        #UI Elements for entering the attributes of the RPC being added.

        # Height of RPC
        self.height_var_label = ttk.Label(rpc_window, text="Height (in metres) of the RPC plate: ")
        self.height_var_label.pack(pady=5)
        self.height_var = tk.DoubleVar()
        self.height_var_entry = ttk.Entry(rpc_window, textvariable=self.height_var)
        self.height_var_entry.pack(pady=5)
        
        # Voltage across the RPC plate in kV
        self.voltage_var_label = ttk.Label(rpc_window, text="Voltage applied across the RPC electrode (kV): ")
        self.voltage_var_label.pack(pady=5)
        self.voltage_var = tk.DoubleVar()
        self.voltage_var_entry = ttk.Entry(rpc_window, textvariable=self.voltage_var)
        self.voltage_var_entry.pack(pady=5)
        
        # Dimensions of RPC (assumed rectangular)
        self.x_var_label = ttk.Label(rpc_window, text="Width of RPC (m): ")
        self.x_var_label.pack(pady=5)
        self.x_var = tk.DoubleVar()
        self.x_var_entry = ttk.Entry(rpc_window, textvariable=self.x_var)
        self.x_var_entry.pack(pady=5)
        
        self.y_var_label = ttk.Label(rpc_window, text="Length of RPC (m): ")
        self.y_var_label.pack(pady=5)
        self.y_var = tk.DoubleVar()
        self.y_var_entry = ttk.Entry(rpc_window, textvariable=self.y_var)
        self.y_var_entry.pack(pady=5)

        self.t_var_label = ttk.Label(rpc_window, text="Thickness of RPC (mm): ")
        self.t_var_label.pack(pady=5)
        self.t_var = tk.DoubleVar()
        self.t_var_entry = ttk.Entry(rpc_window, textvariable=self.t_var)
        self.t_var_entry.pack(pady=5)
        
        # Gas mixture of RPC
        self.gases = ["Isobutane", "Argon", "CO2", "N2"]
        self.selected_gases = {}
        self.gas_percentage = {}

        for gas in self.gases:

            # Gas percentage entry box
            gas_frame = ttk.Frame(rpc_window)
            gas_frame.pack(side="top", fill="x", pady=5)

            self.gas_percentage_var = tk.DoubleVar()
            self.gas_percentage_entry = ttk.Entry(gas_frame, textvariable=self.gas_percentage_var, state="disabled")
            self.gas_percentage_entry.pack(side="left", padx=5)

            # Checkbox
            self.select_gas = tk.BooleanVar()
            chk = ttk.Checkbutton(rpc_window, text=gas, variable=self.select_gas, command=lambda v=self.select_gas, e=self.gas_percentage_entry: self.show_entry(v, e))
            chk.pack(side="top", anchor="w", pady=5)

            # Gas percentage label
            self.gas_percentage_var_label = ttk.Label(gas_frame, text="% Of Gas mixture by volume: ")
            self.gas_percentage_var_label.pack(side="left")

            self.gas_percentage[gas]=self.gas_percentage_var.get()
                    
        # Efficiency of RPC
        self.efficiency_var_label = ttk.Label(rpc_window, text="Hit efficiency of the RPC: ")
        self.efficiency_var_label.pack(pady=5)
        self.efficiency_var = tk.DoubleVar()
        self.efficiency_var_entry = ttk.Entry(rpc_window, textvariable=self.efficiency_var)
        self.efficiency_var_entry.pack(pady=5)
    
    #Logging Features for storing
    def log_rpc(self, rpc):
        with open("rpc_log.txt", "a") as log_file:
            log_entry = f"RPC Plate - Height: {rpc.height}m, Voltage: {rpc.voltage}kV, Dimensions: {rpc.dimensions}m, Efficiency: {rpc.efficiency}, Gas Mixture: {rpc.gas_mixture}\n"
            log_file.write(log_entry)
    #Allow you to view the log by reading the logged content
    def view_log(self):
            try:
                with open("rpc_log.txt", "r") as log_file:
                    log_content = log_file.read()
                messagebox.showinfo("RPC Log", log_content)
            except FileNotFoundError:
                messagebox.showerror("Error", "Log file not found.")
    
    def save_rpc(self, rpc_window):

        # Get user inputs and create RPC object

        height = float(self.height_var.get())
        voltage = float(self.voltage_var.get())
        dimensions = [float(self.x_var.get()), float(self.y_var.get()),float(self.y_var.get())]
        efficiency = float(self.efficiency_var.get())
        gas_mixture = [gas for gas, var in self.selected_gases.items() if var.get()]
        new_rpc = RPC(height=height,efficiency=efficiency,
                        dimensions=dimensions,voltage=voltage,gas_mixture=gas_mixture)
        
        self.log_rpc(new_rpc)
        
        # Add RPC object to the array
        self.rpc_list.append(new_rpc)

        # Close the RPC window
        rpc_window.destroy()

    def plot_stations(self):
        pass

    def calc_efficiences(self):
        pass



if __name__ == "__main__":
    root = tk.Tk()
    app = RPCSimulatorApp(root)
    root.mainloop()

#Later ideas:
        # Generate a decaying particle, some set lifetime.
        # Create charge products, trace paths of products, do animation.
        # Run example for ANUBIS tracking station. 




