import os
import sys
import json
import threading
import traceback
import re
import urllib.request
import math
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
import rasterio
import rasterio.warp
import numpy as np

# Import our backend processor
import processor

# Set appearance mode and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")  # Beautiful green theme representing vegetation

class ScrollableTextHandler:
    """Helper to redirect logs to a CTK Textbox."""
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, text):
        self.textbox.configure(state="normal")
        self.textbox.insert(tk.END, text)
        self.textbox.see(tk.END)
        self.textbox.configure(state="disabled")

    def flush(self):
        pass

class CTkToolTip:
    """A lightweight, clean tooltip widget for CustomTkinter widgets."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
        
    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        # Position the tooltip window slightly offset from the cursor/widget
        x = self.widget.winfo_rootx() + 15
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        # Style as standard tooltip: light yellow background, black border
        label = tk.Label(
            tw, 
            text=self.text, 
            justify="left", 
            background="#ffffe0", 
            foreground="#000000",
            relief="solid", 
            borderwidth=1,
            font=("Arial", "9", "normal"),
            padx=8,
            pady=4,
            wraplength=280 # Nicely wrap the long description text
        )
        label.pack()
        
    def hide_tooltip(self, event=None):
        tw = self.tooltip_window
        self.tooltip_window = None
        if tw:
            tw.destroy()

class SensorTemplateBuilder(ctk.CTkToplevel):
    """Popup modal to create, edit, or delete sensor templates, mapping bands to default numbers."""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("🛠️ Sensor Template Builder")
        self.geometry("550x650")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.selected_template = tk.StringVar(value="")
        self.new_template_name = tk.StringVar(value="")
        self.add_band_name = tk.StringVar(value="")
        
        # List of dicts representing bands and default values: [{"name": "Red", "val": "1"}]
        self.bands_data = []
        self.band_combos_list = [] # List of tuples: (band_name, combo_widget)
        
        self.create_widgets()
        self.load_templates_list()
        
    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1) # Bands scroll frame stretches!
        
        # 1. Template Selector
        sel_frame = ctk.CTkFrame(self)
        sel_frame.grid(row=0, column=0, padx=15, pady=10, sticky="ew")
        sel_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(sel_frame, text="Select Template:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.template_menu = ctk.CTkOptionMenu(sel_frame, variable=self.selected_template, command=self.on_template_select)
        self.template_menu.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # 2. Rename / Create New
        new_frame = ctk.CTkFrame(self)
        new_frame.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        new_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(new_frame, text="New/Rename Template:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.new_name_entry = ctk.CTkEntry(new_frame, textvariable=self.new_template_name, placeholder_text="Enter template name...")
        self.new_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # 3. Add Band Controls
        add_band_frame = ctk.CTkFrame(self)
        add_band_frame.grid(row=2, column=0, padx=15, pady=5, sticky="ew")
        add_band_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(add_band_frame, text="Add Custom Band Name:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.add_band_entry = ctk.CTkEntry(add_band_frame, textvariable=self.add_band_name, placeholder_text="e.g. SWIR1, Thermal...")
        self.add_band_entry.grid(row=0, column=1, padx=(10, 5), pady=10, sticky="ew")
        self.add_band_btn = ctk.CTkButton(add_band_frame, text="➕ Add", width=60, command=self.add_band)
        self.add_band_btn.grid(row=0, column=2, padx=(5, 10), pady=10)
        
        # 4. Bands List Scroll Frame
        ctk.CTkLabel(self, text="Bands Mapped in Template (Band Name & Default Number):", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.bands_scroll = ctk.CTkScrollableFrame(self)
        self.bands_scroll.grid(row=4, column=0, padx=15, pady=5, sticky="nsew")
        self.bands_scroll.grid_columnconfigure(0, weight=1)
        
        # 5. Save & Delete Buttons
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=5, column=0, padx=15, pady=15, sticky="ew")
        action_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.delete_btn = ctk.CTkButton(action_frame, text="🗑️ Delete Template", fg_color="red", hover_color="darkred", command=self.delete_template)
        self.delete_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.save_btn = ctk.CTkButton(action_frame, text="💾 Save Template", command=self.save_template)
        self.save_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
    def load_templates_list(self):
        templates = list(self.parent.sensor_templates.keys())
        if not templates:
            templates = ["NRW (State Geodata)"]
        self.template_menu.configure(values=templates)
        self.selected_template.set(templates[0])
        self.on_template_select(templates[0])
        
    def on_template_select(self, name):
        self.new_template_name.set(name)
        template = self.parent.sensor_templates.get(name, {})
        # Load band key-value pairs
        self.bands_data = [{"name": k, "val": str(v)} for k, v in template.items()]
        self.render_bands()
        
    def save_current_values(self):
        """Read values from current widgets before modifying structure."""
        for name, combo in self.band_combos_list:
            for item in self.bands_data:
                if item["name"] == name:
                    item["val"] = combo.get()
        
    def render_bands(self):
        # Clear old rows
        for w in self.bands_scroll.winfo_children():
            w.destroy()
            
        self.band_combos_list.clear()
            
        for i, item in enumerate(self.bands_data):
            band_name = item["name"]
            band_val = item["val"]
            
            row_frame = ctk.CTkFrame(self.bands_scroll, fg_color=("gray85", "gray25"))
            row_frame.grid(row=i, column=0, padx=5, pady=4, sticky="ew")
            row_frame.grid_columnconfigure(0, weight=1)
            row_frame.grid_columnconfigure(1, weight=0)
            row_frame.grid_columnconfigure(2, weight=0)
            
            lbl = ctk.CTkLabel(row_frame, text=band_name, font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=0, padx=15, pady=6, sticky="w")
            
            # Combobox to select default index
            combo = ctk.CTkComboBox(
                row_frame,
                values=["None"] + [str(x) for x in range(1, 17)],
                width=80
            )
            combo.grid(row=0, column=1, padx=10, pady=6)
            combo.set(band_val)
            self.band_combos_list.append((band_name, combo))
            
            # Delete button (Closure capture key name)
            btn = ctk.CTkButton(
                row_frame, 
                text="❌", 
                width=30, 
                fg_color=("gray75", "gray35"), 
                hover_color="red",
                command=lambda b=band_name: self.remove_band(b)
            )
            btn.grid(row=0, column=2, padx=10, pady=6)
            
    def add_band(self):
        self.save_current_values()
        band = self.add_band_name.get().strip()
        if band:
            if band.lower() in [b["name"].lower() for b in self.bands_data]:
                messagebox.showerror("Error", f"Band '{band}' is already in this template.")
                return
            self.bands_data.append({"name": band, "val": "1"})
            self.add_band_name.set("")
            self.render_bands()
            
    def remove_band(self, name):
        self.save_current_values()
        self.bands_data = [x for x in self.bands_data if x["name"] != name]
        self.render_bands()
            
    def save_template(self):
        self.save_current_values()
        new_name = self.new_template_name.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Please enter a valid template name.")
            return
            
        if not self.bands_data:
            messagebox.showerror("Error", "A template must define at least one band.")
            return
            
        # Rebuild template mapping
        new_mapping = {}
        for item in self.bands_data:
            b_name = item["name"]
            b_val = item["val"]
            if b_val == "None":
                new_mapping[b_name] = "None"
            else:
                new_mapping[b_name] = int(b_val)
            
        # Update templates list
        old_name = self.selected_template.get()
        if old_name in self.parent.sensor_templates and old_name != new_name:
            del self.parent.sensor_templates[old_name]
            
        self.parent.sensor_templates[new_name] = new_mapping
        self.parent.save_sensor_templates()
        self.parent.reload_sensor_presets(new_name)
        
        self.grab_release()
        self.destroy()
        
    def delete_template(self):
        name = self.selected_template.get()
        if len(self.parent.sensor_templates) <= 1:
            messagebox.showerror("Error", "You must keep at least one sensor template.")
            return
            
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the template '{name}'?"):
            if name in self.parent.sensor_templates:
                del self.parent.sensor_templates[name]
                self.parent.save_sensor_templates()
                self.parent.reload_sensor_presets()
                
            self.grab_release()
            self.destroy()

class MultispectralApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("🌿🏛️ ArcSpectra - Multispectral Index Processor")
        self.geometry("1350x880")
        self.minsize(1100, 750)

        # File paths & basic vars
        self.input_file_path = tk.StringVar(value="")
        self.output_dir_path = tk.StringVar(value=os.path.abspath("output"))
        self.sensor_preset = tk.StringVar(value="")
        self.wdvi_s = tk.StringVar(value="1.0")
        self.scale_factor_mode = tk.StringVar(value="Automatic (recommended)")
        self.scale_factor_custom = tk.StringVar(value="1.0")
        
        # Index Editor filter vars
        self.index_search_query = tk.StringVar(value="")
        self.index_category_filter = tk.StringVar(value="All Categories")

        # Load configurations & databases
        self.load_sensor_templates()
        self.load_indices_database()
        self.load_project_indices()

        # UI structures
        self.band_variables = {}   # Dict of {band_name: StringVar}
        self.band_combos = {}      # Dict of {band_name: CTkComboBox}
        
        # Editor control variables
        self.project_indices_vars = {} # Dict of {index_id: BooleanVar} for the Editor list
        self.index_formulas_vars = {}  # Dict of {index_id: StringVar} for formulas in Editor

        # Live session items
        self.file_metadata = {}
        self.processing_thread = None
        self.latest_plot_file = None
        self.plot_image_pil = None
        self.sidebar_checkboxes = {} # Dict of active sidebar checkboxes {index_id: CTkCheckBox}
        self.sidebar_variables = {}  # Dict of active sidebar check states {index_id: BooleanVar}

        # Grid Layout Configuration
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Main panel
        self.grid_rowconfigure(0, weight=1)

        # Create components
        self.create_sidebar()
        self.create_main_content()

        # Configure initial presets
        initial_preset = list(self.sensor_templates.keys())[0]
        self.sensor_preset.set(initial_preset)
        self.on_preset_change(initial_preset)
        
        # Re-render active sidebar indices
        self.refresh_sidebar_indices()

        # Initial folder output creation
        os.makedirs(self.output_dir_path.get(), exist_ok=True)
        
        # Maximize the window on startup on Windows, fallback to standard on other OS
        try:
            if sys.platform.startswith("win"):
                self.state("zoomed")
        except Exception as e:
            print("Could not maximize window on startup:", e)

    # --- CONFIGURATION LOADERS ---
    def load_sensor_templates(self):
        """Load templates from file or create defaults."""
        templates_file = "sensor_templates.json"
        if os.path.exists(templates_file):
            try:
                with open(templates_file, "r", encoding="utf-8") as f:
                    self.sensor_templates = json.load(f)
                return
            except Exception as e:
                print("Error loading sensor_templates.json, using defaults:", e)
                
        # Defaults
        self.sensor_templates = {
            "NRW (State Geodata)": {"Red": 1, "Green": 2, "Blue": 3, "NIR": 4},
            "DJI Multispectral (P4M)": {"Red": 3, "Green": 2, "Blue": 1, "NIR": 5, "RedEdge": 4},
            "DJI Mavic 3M": {"Red": 2, "Green": 1, "NIR": 4, "RedEdge": 3},
            "MicaSense RedEdge / Altum (Wavelength-Sorted)": {"Blue": 1, "Green": 2, "Red": 3, "RedEdge": 4, "NIR": 5},
            "MicaSense RedEdge / Altum (Raw / Native)": {"Blue": 1, "Green": 2, "Red": 3, "NIR": 4, "RedEdge": 5},
            "Parrot Sequoia (SEQ)": {"Red": 2, "Green": 1, "NIR": 4, "RedEdge": 3},
            "Sentinel-2 (B4,B3,B2,B8,B5)": {"Red": 4, "Green": 3, "Blue": 2, "NIR": 8, "RedEdge": 5},
            "Landsat 8/9 (B4,B3,B2,B5)": {"Red": 4, "Green": 3, "Blue": 2, "NIR": 5},
            "PlanetScope (4-Band)": {"Blue": 1, "Green": 2, "Red": 3, "NIR": 4},
            "PlanetScope SuperDove (8-Band)": {"Blue": 2, "Green": 4, "Red": 6, "RedEdge": 7, "NIR": 8},
            "WorldView-2/3 VNIR (8-Band)": {"Blue": 2, "Green": 3, "Red": 5, "RedEdge": 6, "NIR": 7},
            "RapidEye (5-Band)": {"Blue": 1, "Green": 2, "Red": 3, "RedEdge": 4, "NIR": 5},
            "MODIS (B1-B4)": {"Red": 1, "Green": 4, "Blue": 3, "NIR": 2},
            "MAPIR Survey3 RGN (Processed)": {"Red": 1, "Green": 2, "NIR": 3},
            "MAPIR Survey3 NGB (Processed)": {"NIR": 1, "Green": 2, "Blue": 3}
        }
        self.save_sensor_templates()

    def save_sensor_templates(self):
        try:
            with open("sensor_templates.json", "w", encoding="utf-8") as f:
                json.dump(self.sensor_templates, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Error saving sensor_templates.json:", e)

    def load_indices_database(self):
        """Load compiled index registry or define standard fallbacks."""
        indices_file = "compiled_indices.json"
        if os.path.exists(indices_file):
            try:
                with open(indices_file, "r", encoding="utf-8") as f:
                    self.all_indices = json.load(f)
                return
            except Exception as e:
                print("Error loading compiled_indices.json:", e)
                
        # Hardcoded fallback of original 6 indices
        self.all_indices = [
            {"id": "dvi", "abbrev": "DVI", "name": "Difference Vegetation Index", "category": "vegetation", "formula": "NIR - Red", "bands": ["NIR", "Red"]},
            {"id": "ndvi", "abbrev": "NDVI", "name": "Normalized Difference Vegetation Index", "category": "vegetation", "formula": "(NIR - Red) / (NIR + Red)", "bands": ["NIR", "Red"]},
            {"id": "gndvi", "abbrev": "GNDVI", "name": "Green Normalized Difference Vegetation Index", "category": "vegetation", "formula": "(NIR - Green) / (NIR + Green)", "bands": ["NIR", "Green"]},
            {"id": "wdvi", "abbrev": "WDVI", "name": "Weighted Difference Vegetation Index", "category": "vegetation", "formula": "NIR - (s * Red)", "bands": ["NIR", "Red"]},
            {"id": "gemi", "abbrev": "GEMI", "name": "Global Environmental Monitoring Index", "category": "vegetation", "formula": "eta = (2*(NIR**2 - Red**2) + 1.5*NIR + 0.5*Red) / (NIR + Red + 0.5); eta * (1 - 0.25 * eta) - (Red - 0.125) / (1 - Red)", "bands": ["NIR", "Red"]},
            {"id": "ndwi", "abbrev": "NDWI", "name": "Normalized Difference Water Index (McFeeters)", "category": "water", "formula": "(Green - NIR) / (Green + NIR)", "bands": ["Green", "NIR"]}
        ]

    def load_project_indices(self):
        """Load active indices selected for this project."""
        proj_file = "project_indices.json"
        if os.path.exists(proj_file):
            try:
                with open(proj_file, "r", encoding="utf-8") as f:
                    self.project_indices_active = json.load(f)
                return
            except Exception as e:
                print("Error loading project_indices.json:", e)
                
        # Default active selections
        self.project_indices_active = ["dvi", "ndvi", "gndvi", "wdvi", "gemi", "ndwi"]
        self.save_project_indices()

    def save_project_indices(self):
        try:
            with open("project_indices.json", "w", encoding="utf-8") as f:
                json.dump(self.project_indices_active, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Error saving project_indices.json:", e)

    # --- UI LAYOUT BUILDERS ---
    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=380, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar_frame.grid_rowconfigure(9, weight=1)  # Spacer

        # Sidebar Title
        logo_path = "logo.png"
        logo_loaded = False
        if os.path.exists(logo_path):
            try:
                from PIL import Image
                self.logo_img = ctk.CTkImage(
                    light_image=Image.open(logo_path),
                    dark_image=Image.open(logo_path),
                    size=(36, 36)
                )
                self.logo_image_label = ctk.CTkLabel(self.sidebar_frame, image=self.logo_img, text="")
                self.logo_image_label.grid(row=0, column=0, padx=(15, 0), pady=(15, 10), sticky="w")
                
                self.logo_label = ctk.CTkLabel(
                    self.sidebar_frame, 
                    text="ArcSpectra", 
                    font=ctk.CTkFont(size=22, weight="bold")
                )
                self.logo_label.grid(row=0, column=0, padx=(60, 15), pady=(15, 10), sticky="w")
                logo_loaded = True
            except Exception as e:
                print("Could not load logo image:", e)
        
        if not logo_loaded:
            self.logo_label = ctk.CTkLabel(
                self.sidebar_frame, 
                text="⚙️ Configuration", 
                font=ctk.CTkFont(size=20, weight="bold")
            )
            self.logo_label.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # 1. File Selection Frame
        self.io_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.io_frame.grid(row=1, column=0, padx=15, pady=3, sticky="ew")
        self.io_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.io_frame, text="Input GeoTIFF File:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=5, pady=(3, 1))
        
        self.input_entry_frame = ctk.CTkFrame(self.io_frame, fg_color="transparent")
        self.input_entry_frame.grid(row=1, column=0, sticky="ew")
        self.input_entry_frame.grid_columnconfigure(0, weight=1)
        
        self.input_entry = ctk.CTkEntry(self.input_entry_frame, textvariable=self.input_file_path, placeholder_text="Select a GeoTIFF...")
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(5, 5))
        self.input_browse_btn = ctk.CTkButton(self.input_entry_frame, text="Browse...", width=80, command=self.browse_input_file)
        self.input_browse_btn.grid(row=0, column=1, padx=(0, 5))

        CTkToolTip(self.input_entry, "Browse and select the input multispectral orthomosaic (GeoTIFF) file containing geographic metadata.")
        CTkToolTip(self.input_browse_btn, "Browse and select the input multispectral orthomosaic (GeoTIFF) file containing geographic metadata.")

        ctk.CTkLabel(self.io_frame, text="Output Directory:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky="w", padx=5, pady=(5, 1))
        
        self.output_entry_frame = ctk.CTkFrame(self.io_frame, fg_color="transparent")
        self.output_entry_frame.grid(row=3, column=0, sticky="ew")
        self.output_entry_frame.grid_columnconfigure(0, weight=1)

        self.output_entry = ctk.CTkEntry(self.output_entry_frame, textvariable=self.output_dir_path)
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(5, 5))
        self.output_browse_btn = ctk.CTkButton(self.output_entry_frame, text="Browse...", width=80, command=self.browse_output_dir)
        self.output_browse_btn.grid(row=0, column=1, padx=(0, 5))

        CTkToolTip(self.output_entry, "Specify the directory where the generated index rasters and overview plots will be saved.")
        CTkToolTip(self.output_browse_btn, "Specify the directory where the generated index rasters and overview plots will be saved.")

        # 2. Sensor Preset Selection
        self.sensor_frame = ctk.CTkFrame(self.sidebar_frame)
        self.sensor_frame.grid(row=2, column=0, padx=15, pady=4, sticky="ew")
        self.sensor_frame.grid_columnconfigure(0, weight=1)

        # Header panel with Preset selector and Edit builder button
        sensor_header = ctk.CTkFrame(self.sensor_frame, fg_color="transparent")
        sensor_header.grid(row=0, column=0, sticky="ew", padx=10, pady=2)
        sensor_header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(sensor_header, text="Sensor Mapping", font=ctk.CTkFont(weight="bold", size=14)).grid(row=0, column=0, sticky="w")
        self.builder_btn = ctk.CTkButton(sensor_header, text="🛠️ Build", width=60, height=22, font=ctk.CTkFont(size=11), command=self.open_template_builder)
        self.builder_btn.grid(row=0, column=1, padx=(5, 0))

        CTkToolTip(self.builder_btn, "Configure a new sensor template, define custom band names, and assign default band numbers.")

        preset_row = ctk.CTkFrame(self.sensor_frame, fg_color="transparent")
        preset_row.grid(row=1, column=0, sticky="ew", padx=10, pady=2)
        preset_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(preset_row, text="Preset:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.preset_menu = ctk.CTkOptionMenu(
            preset_row,
            values=list(self.sensor_templates.keys()) + ["Custom Configuration"],
            variable=self.sensor_preset,
            command=self.on_preset_change
        )
        self.preset_menu.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        CTkToolTip(self.preset_menu, "Select preset matching your drone/satellite sensor (Sentinel-2, DJI, etc.) to auto-map band numbers.")

        # Dynamic scroll frame for band controls
        self.bands_scroll_frame = ctk.CTkScrollableFrame(self.sensor_frame, height=110, fg_color="transparent")
        self.bands_scroll_frame.grid(row=2, column=0, padx=5, pady=2, sticky="ew")
        self.bands_scroll_frame.grid_columnconfigure(1, weight=1)

        # 3. Active Vegetation Indices checkboxes container
        self.indices_frame = ctk.CTkFrame(self.sidebar_frame)
        self.indices_frame.grid(row=3, column=0, padx=15, pady=3, sticky="ew")
        self.indices_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(self.indices_frame, text="Active Indices", font=ctk.CTkFont(weight="bold", size=14)).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=3)

        # Sub-container for dynamic checkboxes
        self.sidebar_checkboxes_frame = ctk.CTkFrame(self.indices_frame, fg_color="transparent")
        self.sidebar_checkboxes_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        self.sidebar_checkboxes_frame.grid_columnconfigure((0, 1), weight=1)

        # Parameter: WDVI soil line slope
        self.wdvi_param_label = ctk.CTkLabel(self.indices_frame, text="WDVI Slope (s):")
        self.wdvi_param_label.grid(row=4, column=0, sticky="w", padx=10, pady=(3, 5))
        self.wdvi_param_entry = ctk.CTkEntry(self.indices_frame, textvariable=self.wdvi_s, width=80)
        self.wdvi_param_entry.grid(row=4, column=1, sticky="w", padx=10, pady=(3, 5))

        # Tooltip for WDVI Slope
        slope_desc = "Slope of the soil line (s) in the NIR-Red spectral space. Used to correct for bare soil background reflectance in archaeological cropmark detection."
        CTkToolTip(self.wdvi_param_label, slope_desc)
        CTkToolTip(self.wdvi_param_entry, slope_desc)

        # 4. Scaling Factor
        self.scale_frame = ctk.CTkFrame(self.sidebar_frame)
        self.scale_frame.grid(row=4, column=0, padx=15, pady=3, sticky="ew")
        self.scale_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(self.scale_frame, text="Reflectance Scaling", font=ctk.CTkFont(weight="bold", size=14)).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=3)

        self.scale_mode_menu = ctk.CTkOptionMenu(
            self.scale_frame,
            values=["Automatic (recommended)", "1.0 (No scaling)", "Custom Value"],
            variable=self.scale_factor_mode,
            command=self.on_scale_mode_change
        )
        self.scale_mode_menu.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        # Tooltip for Reflectance Scaling
        scale_desc = "Scales raw pixel digital numbers (e.g. 0-255 or 0-65535) to real surface reflectance (0.0 - 1.0). Critical for correct index formula evaluation."
        CTkToolTip(self.scale_frame, scale_desc)
        CTkToolTip(self.scale_mode_menu, scale_desc)

        self.scale_custom_label = ctk.CTkLabel(self.scale_frame, text="Custom Factor:")
        self.scale_custom_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.scale_custom_entry = ctk.CTkEntry(self.scale_frame, textvariable=self.scale_factor_custom, width=100)
        self.scale_custom_entry.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        self.scale_custom_entry.configure(state="disabled")

        # 5. Bottom Start Actions
        self.run_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.run_frame.grid(row=10, column=0, padx=15, pady=(5, 10), sticky="ew")
        self.run_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(self.run_frame, mode="indeterminate")
        self.progress_bar.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.progress_bar.set(0)

        self.start_btn = ctk.CTkButton(
            self.run_frame, 
            text="🚀 Start Processing", 
            font=ctk.CTkFont(size=15, weight="bold"),
            height=40,
            command=self.start_processing
        )
        self.start_btn.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        CTkToolTip(self.start_btn, "Start processing orthomosaic to calculate selected indices and generate cropmark overview plots.")

        self.open_output_btn = ctk.CTkButton(
            self.run_frame,
            text="📁 Open Output Folder",
            fg_color=("gray75", "gray25"),
            hover_color=("gray65", "gray35"),
            command=self.open_output_folder
        )
        self.open_output_btn.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        CTkToolTip(self.open_output_btn, "Open output directory containing generated GeoTIFF index rasters.")

    def create_main_content(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=0) # Header frame
        self.main_frame.grid_rowconfigure(1, weight=1) # Tabs frame

        # --- PREMIUM TOP HEADER ---
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(0, 10))
        self.header_frame.grid_columnconfigure(0, weight=1) # Spacer left

        # Bright/Dark Mode Segmented Button
        theme_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        theme_container.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            theme_container, 
            text="🌓 Theme:", 
            font=ctk.CTkFont(size=12)
        ).grid(row=0, column=0, sticky="e", padx=(0, 5))
        
        self.theme_segment = ctk.CTkSegmentedButton(
            theme_container,
            values=["Dark", "Light"],
            command=self.change_appearance_mode,
            width=90
        )
        self.theme_segment.grid(row=0, column=1, sticky="e", padx=5)
        self.theme_segment.set("Dark")

        # --- TAB VIEW PANELS ---
        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Tabs including the new Index Editor
        self.tab_info = self.tab_view.add("📁 Input Information")
        self.tab_results = self.tab_view.add("📊 Results Visualizer")
        self.tab_editor = self.tab_view.add("📝 Index Editor")
        self.tab_logs = self.tab_view.add("📝 Console Logs")

        # Set up Tab 1: Info (with proper row weights to expand!)
        self.tab_info.grid_columnconfigure(0, weight=1)
        self.tab_info.grid_rowconfigure(0, weight=1)
        
        self.info_scroll = ctk.CTkScrollableFrame(self.tab_info)
        self.info_scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.info_scroll.grid_columnconfigure(0, weight=1)
        
        self.info_welcome = ctk.CTkLabel(
            self.info_scroll, 
            text="No input file selected.\n\nPlease select a GeoTIFF image using the 'Browse...' button in the sidebar to inspect its parameters.",
            font=ctk.CTkFont(size=14, slant="italic"),
            text_color="gray60"
        )
        self.info_welcome.grid(row=0, column=0, pady=100)

        # Set up Tab 2: Results
        self.tab_results.grid_columnconfigure(0, weight=1)
        self.tab_results.grid_rowconfigure(0, weight=1)
        
        self.results_frame = ctk.CTkFrame(self.tab_results, fg_color="transparent")
        self.results_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.results_frame.grid_rowconfigure(0, weight=1)

        self.results_welcome = ctk.CTkLabel(
            self.results_frame,
            text="No processed results to display.\n\nSelect vegetation indices, configure bands, and click 'Start Processing' to generate analysis plots.",
            font=ctk.CTkFont(size=14, slant="italic"),
            text_color="gray60"
        )
        self.results_welcome.grid(row=0, column=0, pady=100)
        
        self.plot_label = ctk.CTkLabel(self.results_frame, text="")
        self.results_frame.bind("<Configure>", self.resize_plot_image)

        # Set up Tab 3: Index Editor (Dynamic Geopera database manager)
        self.setup_index_editor_tab()

        # Set up Tab 4: Logs
        self.tab_logs.grid_columnconfigure(0, weight=1)
        self.tab_logs.grid_rowconfigure(0, weight=1)
        
        self.log_textbox = ctk.CTkTextbox(self.tab_logs, font=ctk.CTkFont(family="Courier New", size=12))
        self.log_textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.log_textbox.configure(state="disabled")
        
        self.log_write("System initialized. Ready to process multispectral images.\n")

    def setup_index_editor_tab(self):
        self.tab_editor.grid_columnconfigure(0, weight=1)
        self.tab_editor.grid_rowconfigure(2, weight=1) # List scroll weight

        # Header filter bar
        filter_bar = ctk.CTkFrame(self.tab_editor)
        filter_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        filter_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(filter_bar, text="🔍 Search:").grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")
        self.editor_search = ctk.CTkEntry(filter_bar, textvariable=self.index_search_query, placeholder_text="Type abbreviation, name, formula...")
        self.editor_search.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.editor_search.bind("<KeyRelease>", lambda event: self.filter_indices_list())

        ctk.CTkLabel(filter_bar, text="📁 Category:").grid(row=0, column=2, padx=5, pady=10, sticky="w")
        categories = ["All Categories"] + sorted(list(set(idx.get("category", "vegetation") for idx in self.all_indices)))
        self.editor_cat = ctk.CTkOptionMenu(filter_bar, values=categories, variable=self.index_category_filter, command=lambda val: self.filter_indices_list())
        self.editor_cat.grid(row=0, column=3, padx=(5, 10), pady=10)

        # Editor configuration bar (source link is now in top header AND here!)
        control_bar = ctk.CTkFrame(self.tab_editor, fg_color="transparent")
        control_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        control_bar.grid_columnconfigure(0, weight=1)

        source_frame = ctk.CTkFrame(control_bar, fg_color="transparent")
        source_frame.grid(row=0, column=0, padx=5, sticky="w")
        
        ctk.CTkLabel(source_frame, text="ℹ️ Database Source: ", font=ctk.CTkFont(size=11, slant="italic"), text_color="gray60").grid(row=0, column=0, sticky="w")
        link_lbl = ctk.CTkLabel(
            source_frame, 
            text="docs.geopera.com/spectral-indices",
            text_color="#10b981",
            font=ctk.CTkFont(size=11, underline=True, slant="italic"),
            cursor="hand2"
        )
        link_lbl.grid(row=0, column=1, sticky="w")
        link_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://docs.geopera.com/spectral-indices"))

        self.apply_editor_btn = ctk.CTkButton(control_bar, text="💾 Save Selection & Apply to Sidebar", font=ctk.CTkFont(weight="bold"), command=self.apply_editor_changes)
        self.apply_editor_btn.grid(row=0, column=1, padx=5)

        self.add_custom_idx_btn = ctk.CTkButton(
            control_bar, 
            text="➕ Add Custom Index", 
            fg_color=("gray75", "gray30"), 
            hover_color=("gray65", "gray40"), 
            command=self.add_custom_index_dialog
        )
        self.add_custom_idx_btn.grid(row=0, column=2, padx=5)

        # Indices table list container
        self.indices_scroll_frame = ctk.CTkScrollableFrame(self.tab_editor)
        self.indices_scroll_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.indices_scroll_frame.grid_columnconfigure((1, 2, 4), weight=1) # headers weight

        # Initial render of matching rows
        self.filter_indices_list()

    # --- SENSOR PRESET DYNAMICS ---
    def reload_sensor_presets(self, select_preset=None):
        presets = list(self.sensor_templates.keys()) + ["Custom Configuration"]
        self.preset_menu.configure(values=presets)
        if select_preset and select_preset in presets:
            self.sensor_preset.set(select_preset)
            self.on_preset_change(select_preset)
        else:
            first = presets[0]
            self.sensor_preset.set(first)
            self.on_preset_change(first)

    def on_preset_change(self, value):
        # Clear existing dynamic variables
        self.band_variables.clear()
        self.band_combos.clear()
        
        # Clear child elements in sidebar scroll frame
        for child in self.bands_scroll_frame.winfo_children():
            child.destroy()

        if value == "Custom Configuration":
            # Show default bands Red, Green, Blue, NIR, RedEdge as editable
            default_bands = ["Red", "Green", "Blue", "NIR", "RedEdge"]
            for i, name in enumerate(default_bands):
                self.create_band_combo_row(name, i, "None" if name in ["Blue", "RedEdge"] else "1")
            return

        # Pre-configured templates
        template = self.sensor_templates.get(value, {})
        for i, (band_name, default_index) in enumerate(template.items()):
            self.create_band_combo_row(band_name, i, str(default_index))

    def create_band_combo_row(self, name, row_idx, default_val):
        row_frame = ctk.CTkFrame(self.bands_scroll_frame, fg_color="transparent")
        row_frame.grid(row=row_idx, column=0, columnspan=2, sticky="ew", pady=3)
        row_frame.grid_columnconfigure(1, weight=1)

        lbl = ctk.CTkLabel(row_frame, text=f"{name}:", anchor="w", font=ctk.CTkFont(size=12))
        lbl.grid(row=0, column=0, sticky="w", padx=5)

        # Variable bindings
        var = tk.StringVar(value=default_val)
        self.band_variables[name] = var

        # Set up combo boxes options (1-8 or actual loaded bands)
        options = ["None", "1", "2", "3", "4", "5", "6", "7", "8"]
        if self.file_metadata:
            options = ["None"] + [str(i) for i in range(1, self.file_metadata["num_bands"] + 1)]

        combo = ctk.CTkComboBox(row_frame, values=options, variable=var, width=100)
        combo.grid(row=0, column=1, sticky="e", padx=5)
        self.band_combos[name] = combo

    def open_template_builder(self):
        # Open popup dialog
        SensorTemplateBuilder(self)

    # --- SIDEBAR ACTIVE INDICES CHECKS ---
    def refresh_sidebar_indices(self):
        """Draw checkboxes inside the sidebar matching only the project_indices_active list."""
        for child in self.sidebar_checkboxes_frame.winfo_children():
            child.destroy()
            
        self.sidebar_checkboxes.clear()
        
        # Sort by abbrev
        active_items = []
        for idx in self.all_indices:
            if idx["id"] in self.project_indices_active:
                active_items.append(idx)
                
        # Specialized archaeological remote sensing tooltips dictionary
        index_tooltips = {
            "dvi": "Difference Vegetation Index. Sensitive to crop canopy density; helpful for general cropmark outlining.",
            "ndvi": "Normalized Difference Vegetation Index. The standard proxy for crop vigor; highly effective at detecting cropmarks over buried ditches or walls.",
            "gndvi": "Green NDVI. Uses green instead of red band. More sensitive to canopy chlorophyll variations, useful for early cropmark stress.",
            "wdvi": "Weighted Difference Vegetation Index. Corrects for background soil line reflectance, critical for sparse crops or dry soils.",
            "gemi": "Global Environmental Monitoring Index. Minimizes atmospheric and soil noise, ideal for regional satellite prospection.",
            "ndwi": "Normalized Difference Water Index. Highlights canopy and soil moisture differences, perfect for revealing buried ditches and pits.",
            "navi": "Normalized Archaeological Vegetation Index. Leverages red-edge wavelengths to maximize contrast for archaeological cropmark detection.",
            "nai": "Normalized Archaeological Index. Exploits red-edge bands for enhanced visibility of buried walls and structural outlines.",
            "ndvi_arch": "NDVI calibrated for archaeological cropmark detection.",
            "gndvi_arch": "Green NDVI calibrated for detecting canopy stress over subsurface archaeological features.",
            "savi_arch": "Soil Adjusted Vegetation Index calibrated to reduce soil noise for archaeology.",
            "sr_arch": "Simple Ratio calibrated for canopy stress over archaeological cropmarks."
        }
                
        # Draw in 2 column grid
        for i, idx in enumerate(active_items):
            idx_id = idx["id"]
            abbrev = idx["abbrev"]
            
            # Check variable
            var = self.sidebar_variables.get(idx_id)
            if var is None:
                var = tk.BooleanVar(value=True)
                self.sidebar_variables[idx_id] = var
                
            row = i // 2
            col = i % 2
            
            cb = ctk.CTkCheckBox(
                self.sidebar_checkboxes_frame, 
                text=abbrev, 
                variable=var, 
                font=ctk.CTkFont(size=12)
            )
            cb.grid(row=row, column=col, padx=8, pady=4, sticky="w")
            self.sidebar_checkboxes[idx_id] = cb

            # Attach tooltip description
            t_text = index_tooltips.get(idx_id, idx.get("name", ""))
            CTkToolTip(cb, t_text)

    # --- INDEX EDITOR METHODS ---
    def filter_indices_list(self):
        search_txt = self.index_search_query.get().strip().lower()
        selected_cat = self.index_category_filter.get()
        
        # Clear scrollable frame children
        for child in self.indices_scroll_frame.winfo_children():
            child.destroy()

        # Grid Headers
        headers = ["Active", "Abbrev", "Name", "Category", "Formula (Edit)", "Bands Required"]
        column_widths = [60, 80, 220, 110, 320, 120]
        
        header_frame = ctk.CTkFrame(self.indices_scroll_frame, fg_color=("gray80", "gray20"))
        header_frame.grid(row=0, column=0, columnspan=6, sticky="ew", pady=(0, 5))
        
        for c_idx, h in enumerate(headers):
            lbl = ctk.CTkLabel(
                header_frame, 
                text=h, 
                width=column_widths[c_idx],
                font=ctk.CTkFont(weight="bold", size=12),
                anchor="w"
            )
            lbl.grid(row=0, column=c_idx, padx=10, pady=6, sticky="w")

        # Filter indices
        rendered_count = 0
        for i, index_def in enumerate(self.all_indices):
            idx_id = index_def["id"]
            abbrev = index_def["abbrev"]
            name = index_def["name"]
            cat = index_def.get("category", "vegetation")
            formula = index_def.get("formula", "")
            bands = index_def.get("bands", [])
            
            # Apply search filters
            if selected_cat != "All Categories" and cat.lower() != selected_cat.lower():
                continue
            if search_txt and not (search_txt in idx_id.lower() or search_txt in abbrev.lower() or search_txt in name.lower() or search_txt in formula.lower()):
                continue

            # Row container
            row_frame = ctk.CTkFrame(self.indices_scroll_frame, fg_color="transparent")
            row_frame.grid(row=rendered_count + 1, column=0, columnspan=6, sticky="ew", pady=2)

            # Check variables
            var = self.project_indices_vars.get(idx_id)
            if var is None:
                var = tk.BooleanVar(value=idx_id in self.project_indices_active)
                self.project_indices_vars[idx_id] = var

            formula_var = self.index_formulas_vars.get(idx_id)
            if formula_var is None:
                formula_var = tk.StringVar(value=formula)
                self.index_formulas_vars[idx_id] = formula_var

            # 1. Checkbox
            cb = ctk.CTkCheckBox(row_frame, text="", variable=var, width=column_widths[0])
            cb.grid(row=0, column=0, padx=10, pady=4, sticky="w")

            # 2. Abbreviation
            ab_lbl = ctk.CTkLabel(row_frame, text=abbrev, font=ctk.CTkFont(weight="bold"), width=column_widths[1], anchor="w")
            ab_lbl.grid(row=0, column=1, padx=10, pady=4, sticky="w")

            # 3. Name
            name_lbl = ctk.CTkLabel(row_frame, text=name, width=column_widths[2], anchor="w", justify="left", wraplength=column_widths[2]-20)
            name_lbl.grid(row=0, column=2, padx=10, pady=4, sticky="w")

            # 4. Category
            cat_lbl = ctk.CTkLabel(row_frame, text=cat, width=column_widths[3], anchor="w")
            cat_lbl.grid(row=0, column=3, padx=10, pady=4, sticky="w")

            # 5. Formula text entry box
            formula_entry = ctk.CTkEntry(row_frame, textvariable=formula_var, width=column_widths[4] - 20)
            formula_entry.grid(row=0, column=4, padx=10, pady=4, sticky="w")

            # 6. Bands Required
            bands_lbl = ctk.CTkLabel(row_frame, text=", ".join(bands), width=column_widths[5], anchor="w")
            bands_lbl.grid(row=0, column=5, padx=10, pady=4, sticky="w")

            rendered_count += 1
            if rendered_count >= 50:
                more_lbl = ctk.CTkLabel(self.indices_scroll_frame, text="... (showing first 50 results. Use search query or category to filter more precisely) ...", font=ctk.CTkFont(slant="italic"))
                more_lbl.grid(row=rendered_count + 2, column=0, columnspan=6, pady=10)
                break

    def apply_editor_changes(self):
        """Save selected indices to active project configuration, and update edited formulas in database."""
        # 1. Update active selections
        new_active = []
        for idx_id, var in self.project_indices_vars.items():
            if var.get():
                new_active.append(idx_id)
                
        # 2. Update formulas in the list database
        for index_def in self.all_indices:
            idx_id = index_def["id"]
            if idx_id in self.index_formulas_vars:
                new_f = self.index_formulas_vars[idx_id].get().strip()
                if new_f:
                    index_def["formula"] = new_f
                    # Dynamic band extraction from edited formula
                    words = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", new_f)
                    standard_bands = ["red", "green", "blue", "nir", "rededge", "swir", "swir1", "swir2", "coastal", "thermal"]
                    extracted_bands = []
                    for w in words:
                        if w.lower() in standard_bands and w not in extracted_bands:
                            extracted_bands.append(w)
                    if extracted_bands:
                        index_def["bands"] = extracted_bands

        # Write updates to project files
        self.project_indices_active = new_active
        self.save_project_indices()
        
        # Save compiled formulas
        try:
            with open("compiled_indices.json", "w", encoding="utf-8") as f:
                json.dump(self.all_indices, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Error saving compiled_indices.json:", e)

        # Refresh sidebar view
        self.refresh_sidebar_indices()
        messagebox.showinfo("Success", f"Index configuration saved!\n{len(new_active)} indices applied to your active project.")

    def add_custom_index_dialog(self):
        # Dialog popups to define custom index
        dialog_window = ctk.CTkToplevel(self)
        dialog_window.title("➕ Add Custom Index")
        dialog_window.geometry("450x380")
        dialog_window.resizable(False, False)
        dialog_window.transient(self)
        dialog_window.grab_set()

        dialog_window.grid_columnconfigure(1, weight=1)

        # Fields
        ctk.CTkLabel(dialog_window, text="Index Abbreviation:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        var_abbrev = tk.StringVar()
        entry_abbrev = ctk.CTkEntry(dialog_window, textvariable=var_abbrev, placeholder_text="e.g. MY_NDVI")
        entry_abbrev.grid(row=0, column=1, padx=15, pady=10, sticky="ew")

        ctk.CTkLabel(dialog_window, text="Full Name:").grid(row=1, column=0, padx=15, pady=10, sticky="w")
        var_name = tk.StringVar()
        entry_name = ctk.CTkEntry(dialog_window, textvariable=var_name, placeholder_text="e.g. My Custom Vegetation Index")
        entry_name.grid(row=1, column=1, padx=15, pady=10, sticky="ew")

        ctk.CTkLabel(dialog_window, text="Category:").grid(row=2, column=0, padx=15, pady=10, sticky="w")
        var_cat = tk.StringVar(value="vegetation")
        entry_cat = ctk.CTkOptionMenu(dialog_window, values=["vegetation", "water", "soil", "burn", "urban", "geology", "archaeology", "custom"], variable=var_cat)
        entry_cat.grid(row=2, column=1, padx=15, pady=10, sticky="ew")

        ctk.CTkLabel(dialog_window, text="Formula:", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, padx=15, pady=10, sticky="w")
        var_formula = tk.StringVar()
        entry_formula = ctk.CTkEntry(dialog_window, textvariable=var_formula, placeholder_text="e.g. (NIR - Red) / (NIR + Red)")
        entry_formula.grid(row=3, column=1, padx=15, pady=10, sticky="ew")

        def submit_custom_index():
            abbrev = var_abbrev.get().strip()
            name = var_name.get().strip()
            cat = var_cat.get()
            formula = var_formula.get().strip()

            if not abbrev or not name or not formula:
                messagebox.showerror("Error", "All bold fields must be filled in.")
                return

            # Check if exists
            idx_id = abbrev.lower().replace(" ", "_")
            if any(x["id"] == idx_id for x in self.all_indices):
                messagebox.showerror("Error", f"An index with abbreviation '{abbrev}' already exists.")
                return

            # Extract band names from formula
            words = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", formula)
            standard_bands = ["red", "green", "blue", "nir", "rededge", "swir", "swir1", "swir2", "coastal", "thermal"]
            bands = []
            for w in words:
                if w.lower() in standard_bands and w not in bands:
                    bands.append(w)

            new_idx = {
                "id": idx_id,
                "abbrev": abbrev,
                "name": name,
                "category": cat,
                "formula": formula,
                "bands": bands
            }

            self.all_indices.append(new_idx)
            
            # Save compiled list
            try:
                with open("compiled_indices.json", "w", encoding="utf-8") as f:
                    json.dump(self.all_indices, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print("Error saving compiled_indices.json:", e)

            # Auto add to project active indices
            self.project_indices_active.append(idx_id)
            self.save_project_indices()

            # Refresh Editor list and Sidebar checks
            self.filter_indices_list()
            self.refresh_sidebar_indices()
            
            dialog_window.grab_release()
            dialog_window.destroy()

        btn_frame = ctk.CTkFrame(dialog_window, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=2, padx=15, pady=15, sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(btn_frame, text="Cancel", fg_color=("gray75", "gray30"), hover_color=("gray65", "gray40"), command=dialog_window.destroy).grid(row=0, column=0, padx=10, sticky="ew")
        ctk.CTkButton(btn_frame, text="Add Index", command=submit_custom_index).grid(row=0, column=1, padx=10, sticky="ew")

    # --- MAIN VIEW LOGS & METADATA ---
    def log_write(self, text):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert(tk.END, text)
        self.log_textbox.see(tk.END)
        self.log_textbox.configure(state="disabled")

    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select Input GeoTIFF",
            filetypes=[("GeoTIFF files", "*.tif *.tiff"), ("All files", "*.*")]
        )
        if filename:
            self.input_file_path.set(filename)
            self.log_write(f"Selected input file: {filename}\n")
            self.load_file_metadata(filename)

    def browse_output_dir(self):
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir_path.get()
        )
        if directory:
            self.output_dir_path.set(directory)
            self.log_write(f"Selected output directory: {directory}\n")

    def on_scale_mode_change(self, value):
        if value == "Custom Value":
            self.scale_custom_entry.configure(state="normal")
        else:
            self.scale_custom_entry.configure(state="disabled")
        self.log_write(f"Changed scaling mode to: {value}\n")

    def load_file_metadata(self, file_path):
        def worker():
            try:
                self.log_write("Reading raster headers...\n")
                with rasterio.open(file_path) as src:
                    num_bands = src.count
                    width = src.width
                    height = src.height
                    crs = str(src.crs) if src.crs else "Unknown"
                    bounds = src.bounds
                    nodata = src.nodata
                    
                meta = {
                    "num_bands": num_bands,
                    "width": width,
                    "height": height,
                    "crs": crs,
                    "bounds": bounds,
                    "nodata": nodata,
                    "filename": os.path.basename(file_path)
                }
                
                # Fetch OSM background map footprint in background
                map_image = self.generate_osm_footprint_map(file_path)
                
                self.after(0, lambda: self.update_metadata_ui(meta, map_image))
            except Exception as e:
                self.log_write(f"Error reading file metadata: {str(e)}\n")
                self.after(0, lambda: messagebox.showerror("Metadata Error", f"Could not read GeoTIFF metadata:\n{str(e)}"))

        threading.Thread(target=worker, daemon=True).start()

    def generate_osm_footprint_map(self, file_path):
        """Extract bounds, project to WGS84, fetch OSM tiles, stitch, draw polygon."""
        try:
            self.log_write("Extracting geo coordinates and converting to WGS84...\n")
            with rasterio.open(file_path) as src:
                bounds = src.bounds
                crs = src.crs
                
            if not crs:
                self.log_write("Warning: CRS not defined in GeoTIFF. Bounding map skipped.\n")
                return None
                
            # Transform bounds to EPSG:4326 (WGS84 Lat/Lon)
            try:
                west, south, east, north = rasterio.warp.transform_bounds(
                    crs, "EPSG:4326", bounds.left, bounds.bottom, bounds.right, bounds.top
                )
            except Exception as e:
                self.log_write(f"Warning: Bounding box transform failed: {str(e)}\n")
                return None
                
            self.log_write(f"Footprint (Lat/Lon): W:{west:.4f}, S:{south:.4f}, E:{east:.4f}, N:{north:.4f}\n")
            
            # Dynamic zoom choice based on bounds span
            lat_span = abs(north - south)
            lon_span = abs(east - west)
            max_span = max(lat_span, lon_span)
            
            if max_span > 10:
                zoom = 4
            elif max_span > 3:
                zoom = 6
            elif max_span > 1:
                zoom = 8
            elif max_span > 0.3:
                zoom = 10
            elif max_span > 0.1:
                zoom = 12
            elif max_span > 0.03:
                zoom = 14
            elif max_span > 0.005:
                zoom = 15
            else:
                zoom = 17
                
            # Helper: WGS84 to tile coordinates
            def latlon_to_tile(lat, lon, z):
                lat_rad = math.radians(lat)
                n = 2.0 ** z
                xtile = int((lon + 180.0) / 360.0 * n)
                # Clamp latitude to Web Mercator limits
                lat_rad = max(-math.radians(85.0511), min(math.radians(85.0511), lat_rad))
                ytile = int((1.0 - math.log(math.tan(lat_rad) + 1.0/math.cos(lat_rad)) / math.pi) / 2.0 * n)
                return xtile, ytile
                
            def latlon_to_pixel(lat, lon, z):
                lat_rad = math.radians(lat)
                n = 2.0 ** z
                x = (lon + 180.0) / 360.0 * n * 256
                lat_rad = max(-math.radians(85.0511), min(math.radians(85.0511), lat_rad))
                y = (1.0 - math.log(math.tan(lat_rad) + 1.0/math.cos(lat_rad)) / math.pi) / 2.0 * n * 256
                return x, y
                
            # Find bounds tile coordinate range
            xtile_min, ytile_min = latlon_to_tile(north, west, zoom)
            xtile_max, ytile_max = latlon_to_tile(south, east, zoom)
            
            x_start = min(xtile_min, xtile_max)
            x_end = max(xtile_min, xtile_max)
            y_start = min(ytile_min, ytile_max)
            y_end = max(ytile_min, ytile_max)
            
            # Clamp grid size to max 4x4 tiles
            max_tiles = 4
            while (x_end - x_start + 1) > max_tiles or (y_end - y_start + 1) > max_tiles:
                zoom -= 1
                if zoom < 1:
                    break
                xtile_min, ytile_min = latlon_to_tile(north, west, zoom)
                xtile_max, ytile_max = latlon_to_tile(south, east, zoom)
                x_start = min(xtile_min, xtile_max)
                x_end = max(xtile_min, xtile_max)
                y_start = min(ytile_min, ytile_max)
                y_end = max(ytile_min, ytile_max)
                
            cols = x_end - x_start + 1
            rows = y_end - y_start + 1
            self.log_write(f"Stitching {cols}x{rows} map tiles at zoom level {zoom}...\n")
            
            # Map canvas
            map_img = Image.new("RGB", (cols * 256, rows * 256))
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.openstreetmap.org/"
            }
            
            # Fetch tiles
            for cy in range(y_start, y_end + 1):
                for cx in range(x_start, x_end + 1):
                    tile_url = f"https://tile.openstreetmap.org/{zoom}/{cx}/{cy}.png"
                    try:
                        req = urllib.request.Request(tile_url, headers=headers)
                        with urllib.request.urlopen(req, timeout=4) as resp:
                            tile = Image.open(resp)
                            px = (cx - x_start) * 256
                            py = (cy - y_start) * 256
                            map_img.paste(tile, (px, py))
                    except Exception as te:
                        self.log_write(f"Warning: Failed to fetch tile {zoom}/{cx}/{cy}: {str(te)}\n")
                        # paste grey placeholder tile
                        placeholder = Image.new("RGB", (256, 256), color="gray80")
                        px = (cx - x_start) * 256
                        py = (cy - y_start) * 256
                        map_img.paste(placeholder, (px, py))
                        
            # Map raster footprint corners: TL, BL, BR, TR
            corners = [
                (north, west),
                (south, west),
                (south, east),
                (north, east)
            ]
            
            local_pts = []
            for lat, lon in corners:
                gx, gy = latlon_to_pixel(lat, lon, zoom)
                lx = int(gx - x_start * 256)
                ly = int(gy - y_start * 256)
                local_pts.append((lx, ly))
                
            # Transparent overlay polygon
            overlay = Image.new("RGBA", map_img.size)
            draw = ImageDraw.Draw(overlay)
            # Semi-transparent emerald polygon
            draw.polygon(local_pts, fill=(16, 185, 129, 70), outline=(16, 185, 129, 255), width=3)
            
            # Combine canvas and polygon
            combined = Image.alpha_composite(map_img.convert("RGBA"), overlay).convert("RGB")
            return combined
            
        except Exception as e:
            self.log_write(f"Warning: Footprint map generation skipped: {str(e)}\n")
            return None

    def update_metadata_ui(self, meta, map_image=None):
        self.file_metadata = meta
        
        # Clear old rows in info tab
        for child in self.info_scroll.winfo_children():
            child.destroy()
            
        # Reconfigure row weights to expand
        self.tab_info.grid_rowconfigure(0, weight=1)
            
        # Update dropdown choice lists in sidebar
        band_options = ["None"] + [str(i) for i in range(1, meta["num_bands"] + 1)]
        for combo in self.band_combos.values():
            combo.configure(values=band_options)

        # Header title
        title_lbl = ctk.CTkLabel(
            self.info_scroll, 
            text=meta["filename"], 
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        title_lbl.grid(row=0, column=0, padx=10, pady=(10, 15), sticky="w")

        # Table Grid Card
        card_frame = ctk.CTkFrame(self.info_scroll)
        card_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        card_frame.grid_columnconfigure(0, weight=0)
        card_frame.grid_columnconfigure(1, weight=1)

        details = [
            ("📁 File Path", self.input_file_path.get()),
            ("📐 Resolution (WxH)", f"{meta['width']} x {meta['height']} pixels"),
            ("🌈 Bands Detected", f"{meta['num_bands']} bands"),
            ("🌐 Coordinate System", meta['crs']),
            ("🚫 NoData Value", str(meta['nodata'])),
            ("🗺️ Bounds (West)", f"{meta['bounds'].left:.6f}"),
            ("🗺️ Bounds (South)", f"{meta['bounds'].bottom:.6f}"),
            ("🗺️ Bounds (East)", f"{meta['bounds'].right:.6f}"),
            ("🗺️ Bounds (North)", f"{meta['bounds'].top:.6f}"),
        ]

        for i, (label, val) in enumerate(details):
            lbl_name = ctk.CTkLabel(card_frame, text=label, font=ctk.CTkFont(weight="bold"), anchor="w")
            lbl_name.grid(row=i, column=0, padx=15, pady=6, sticky="w")
            
            # Use sticky="ew" and anchor="w" to allow clean stretching and wrap
            lbl_val = ctk.CTkLabel(card_frame, text=val, anchor="w", justify="left", wraplength=600)
            lbl_val.grid(row=i, column=1, padx=15, pady=6, sticky="ew")

        # 3. Draw footprint OSM map if present
        if map_image:
            map_frame = ctk.CTkFrame(self.info_scroll)
            map_frame.grid(row=2, column=0, padx=10, pady=15, sticky="ew")
            map_frame.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(
                map_frame, 
                text="🗺️ Geographic Footprint Map (OpenStreetMap)", 
                font=ctk.CTkFont(weight="bold", size=13)
            ).grid(row=0, column=0, padx=15, pady=(12, 6), sticky="w")
            
            # Convert to CTK image, width = 500px
            aspect = map_image.height / map_image.width
            w = 500
            h = int(w * aspect)
            
            ctk_map = ctk.CTkImage(light_image=map_image, dark_image=map_image, size=(w, h))
            
            map_lbl = ctk.CTkLabel(map_frame, image=ctk_map, text="")
            map_lbl.image = ctk_map  # keep reference
            map_lbl.grid(row=1, column=0, padx=15, pady=(5, 15))

        self.log_write(f"Metadata loaded successfully: {meta['width']}x{meta['height']}, {meta['num_bands']} bands.\n")

    # --- IMAGE RESIZING FOR RESULTS ---
    def resize_plot_image(self, event=None):
        if self.latest_plot_file is None or not os.path.exists(self.latest_plot_file):
            return

        try:
            if self.plot_image_pil is None:
                self.plot_image_pil = Image.open(self.latest_plot_file)

            frame_w = self.results_frame.winfo_width()
            frame_h = self.results_frame.winfo_height()

            # Handle inactive tab dimensions (reported as 1x1 by Tkinter before display mapping)
            if frame_w <= 20 or frame_h <= 20:
                frame_w = 800
                frame_h = 600

            target_w = max(frame_w - 20, 100)
            target_h = max(frame_h - 20, 100)

            # Scale and keep aspect ratio
            img_w, img_h = self.plot_image_pil.size
            ratio = min(target_w / img_w, target_h / img_h)
            new_w = int(img_w * ratio)
            new_h = int(img_h * ratio)

            # Draw image in label
            ctk_img = ctk.CTkImage(
                light_image=self.plot_image_pil,
                dark_image=self.plot_image_pil,
                size=(new_w, new_h)
            )

            self.results_welcome.grid_forget()
            self.plot_label.configure(image=ctk_img)
            self.plot_label.image = ctk_img  # Keep reference
            self.plot_label.grid(row=0, column=0)

        except Exception as e:
            self.log_write(f"Error resizing results preview: {str(e)}\n")

    # --- APPEARANCE THEME MANAGER ---
    def change_appearance_mode(self, mode):
        ctk.set_appearance_mode(mode)
        self.log_write(f"Changed appearance theme to: {mode}\n")

    # --- PIPELINE RUNS ---
    def start_processing(self):
        file_path = self.input_file_path.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid input GeoTIFF file first.")
            return

        out_dir = self.output_dir_path.get()
        if not out_dir:
            messagebox.showerror("Error", "Please select an output directory.")
            return

        # Determine checked indices
        active_ids = [idx_id for idx_id, cb_var in self.sidebar_variables.items() if cb_var.get()]
        if not active_ids:
            messagebox.showerror("Error", "Please check at least one active index in the sidebar.")
            return

        # Build active formulas dict
        active_indices_formulas = {}
        for idx in self.all_indices:
            idx_id = idx["id"]
            if idx_id in active_ids:
                active_indices_formulas[idx["abbrev"]] = idx["formula"]

        # Build band mapping
        bands_mapping = {}
        for name, var in self.band_variables.items():
            val = var.get()
            if val != "None":
                try:
                    bands_mapping[name] = int(val)
                except ValueError:
                    messagebox.showerror("Error", f"Band index for '{name}' must be an integer or 'None'.")
                    return

        # Band count checks
        if self.file_metadata:
            total_bands = self.file_metadata["num_bands"]
            for name, val in bands_mapping.items():
                if val < 1 or val > total_bands:
                    messagebox.showerror("Error", f"The chosen {name} band index ({val}) is invalid. Image only has {total_bands} bands.")
                    return

        # WDVI s coefficient checks
        try:
            wdvi_s_val = float(self.wdvi_s.get())
        except ValueError:
            messagebox.showerror("Error", "WDVI Soil line slope (s) must be a numeric value.")
            return

        # Scaling factor Mode
        mode = self.scale_factor_mode.get()
        if mode == "1.0 (No scaling)":
            scale_val = 1.0
        elif mode == "Custom Value":
            try:
                scale_val = float(self.scale_factor_custom.get())
            except ValueError:
                messagebox.showerror("Error", "Custom scaling factor must be a numeric value.")
                return
        else:
            self.log_write("Auto-detecting scale factor based on image data range...\n")
            scale_val = self.detect_scale_factor_value(file_path)
            self.log_write(f"Detected scale factor: {scale_val}\n")

        # Disable UI components
        self.set_ui_state("disabled")
        self.progress_bar.start()
        self.tab_view.set("📝 Console Logs")  # Auto switch to logs tab
        self.log_write("\n" + "="*50 + "\n")
        self.log_write("Starting Background Processing Thread...\n")

        # Background worker run
        def worker():
            try:
                ortho_name, results, saved_files, plot_file = processor.process_raster_file(
                    file_path=file_path,
                    output_dir=out_dir,
                    bands_mapping=bands_mapping,
                    selected_indices_formulas=active_indices_formulas,
                    wdvi_s=wdvi_s_val,
                    scale_factor=scale_val,
                    log_callback=self.log_write
                )

                self.log_write("\nProcessing finished successfully!\n")
                if plot_file:
                    self.log_write(f"Overview plot saved to: {plot_file}\n")
                for idx, tpath in saved_files.items():
                    self.log_write(f"-> Saved index raster: {tpath}\n")

                self.after(0, lambda: self.on_processing_success(plot_file))

            except Exception as e:
                err_msg = traceback.format_exc()
                self.log_write(f"\nProcessing Error:\n{err_msg}\n")
                self.after(0, lambda: self.on_processing_error(str(e)))

        self.processing_thread = threading.Thread(target=worker, daemon=True)
        self.processing_thread.start()

    def detect_scale_factor_value(self, file_path):
        try:
            with rasterio.open(file_path) as src:
                w_h = min(1000, src.height)
                w_w = min(1000, src.width)
                sample = src.read(1, window=((0, w_h), (0, w_w)))
                valid_sample = sample[sample != src.nodata] if src.nodata is not None else sample
                
                if len(valid_sample) > 0:
                    max_val = np.nanmax(valid_sample)
                    if max_val > 1.5:
                        if max_val <= 255.0:
                            return 255.0
                        else:
                            return 65535.0
        except Exception as e:
            self.log_write(f"Warning during auto-scale detection: {str(e)}. Defaulting to 1.0\n")
        return 1.0

    def on_processing_success(self, plot_file):
        self.set_ui_state("normal")
        self.progress_bar.stop()
        self.progress_bar.set(1.0)
        
        self.latest_plot_file = plot_file
        self.plot_image_pil = None  # Force reload
        
        # Switch to Results tab first
        self.tab_view.set("📊 Results Visualizer")
        
        # Wait for Tkinter layout cycle to compute frame dimensions
        self.after(150, self.resize_plot_image)
        
        messagebox.showinfo("Success", "Spectral index calculations completed successfully!\nOverview plot has been saved and rendered.")

    def on_processing_error(self, err_str):
        self.set_ui_state("normal")
        self.progress_bar.stop()
        self.progress_bar.set(0)
        messagebox.showerror("Processing Failed", f"An error occurred during calculations:\n\n{err_str}")

    def set_ui_state(self, state):
        self.start_btn.configure(state=state)
        self.input_browse_btn.configure(state=state)
        self.output_browse_btn.configure(state=state)
        self.preset_menu.configure(state=state)
        self.scale_mode_menu.configure(state=state)
        self.builder_btn.configure(state=state)
        self.apply_editor_btn.configure(state=state)
        self.add_custom_idx_btn.configure(state=state)
        self.theme_segment.configure(state=state)
        
        if state == "normal":
            self.on_scale_mode_change(self.scale_factor_mode.get())
            self.on_preset_change(self.sensor_preset.get())
            self.wdvi_param_entry.configure(state="normal")
        else:
            self.scale_custom_entry.configure(state="disabled")
            self.wdvi_param_entry.configure(state="disabled")
            for combo in self.band_combos.values():
                combo.configure(state="disabled")

    def open_output_folder(self):
        folder = self.output_dir_path.get()
        if os.path.exists(folder):
            try:
                os.startfile(folder)
            except Exception as e:
                self.log_write(f"Error opening directory: {str(e)}\n")
        else:
            messagebox.showerror("Error", "Output folder does not exist yet.")

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    app = MultispectralApp()
    app.mainloop()
