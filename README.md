# 🌿🏛️ ArcSpectra - Multispectral Vegetation Index Processor for Archaeological Prospection

**ArcSpectra** is a professional, high-performance Python application designed for **remote sensing archaeology and non-destructive prospection**. By calculating optical spectral indices from multispectral drone (UAV) or satellite imagery, ArcSpectra reveals subsurface archaeological remains (such as buried stone walls, brick foundations, ancient roads, filled-in ditches, postholes, and pits) through crop canopy anomalies (**cropmarks**) and soil moisture patterns (**soilmarks**).

Cropmarks occur due to differential plant stress:
- **Positive cropmarks** (taller, healthier plants with higher chlorophyll content) develop over filled-in archaeological features like ditches or pits, which hold more moisture and nutrients.
- **Negative cropmarks** (stunted, chlorotic, or dry vegetation) occur over buried walls, floors, or paved roads, which limit root depth and restrict water availability.

---

## 🗺️ System Components

ArcSpectra is powered by a shared, optimized calculation backend and provides two separate workflows:

1.  **Desktop Dashboard ([gui.py](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/gui.py))**: An interactive CustomTkinter desktop interface featuring automated metadata scanning, interactive OpenStreetMap-footprint drawing, dynamic light/dark theme switching, and live results visualization.
2.  **Jupyter Research Notebook ([multispectral_processing.ipynb](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/multispectral_processing.ipynb))**: A fully documented notebook for batch processing, scripting, and reproducible scientific workflows in Python.

---

## 🛠️ Sensor Template Builder & Configuration

Different multispectral sensors capture bands in varying channel order. The **Sensor Template Builder** solves this by letting you define templates where each required band (e.g., `NIR`, `RedEdge`, `Red`, `Green`) is assigned a default band index (channel number) in the source GeoTIFF file. 

These configurations are stored in the local file [sensor_templates.json](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/sensor_templates.json).

### 1. DJI Multispectral Example (e.g. Phantom 4 Multispectral)
Typical band channels for a DJI P4M output:
- Band 1: Blue (B)
- Band 2: Green (G)
- Band 3: Red (R)
- Band 4: RedEdge (RE)
- Band 5: Near-Infrared (NIR)

In the **Sensor Template Builder** (accessed via `🛠️ Build` in the sidebar), this is configured by:
1. Creating a new template name: `DJI Multispectral`.
2. Mapping the bands:
   - `Red` ➡️ `3`
   - `Green` ➡️ `2`
   - `Blue` ➡️ `1`
   - `RedEdge` ➡️ `4`
   - `NIR` ➡️ `5`
3. Saving the template. When selected in the main GUI sidebar, ArcSpectra dynamically adapts to pull the correct bands from the TIFF for index calculations.

### 2. MicaSense Sequoia Example
Typical band channels for a MicaSense Sequoia:
- Band 1: Green (G)
- Band 2: Red (R)
- Band 3: RedEdge (RE)
- Band 4: Near-Infrared (NIR)

In the **Sensor Template Builder**, this is mapped as:
- `Green` ➡️ `1`
- `Red` ➡️ `2`
- `RedEdge` ➡️ `3`
- `NIR` ➡️ `4`
- `Blue` ➡️ `None` (Sequoia does not capture a Blue band)

---

## 📝 Geopera Index Editor

ArcSpectra is pre-compiled with a database of **182 optical spectral indices** parsed from the Geopera Spectral Database (docs.geopera.com/spectral-indices) and saved in [compiled_indices.json](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/compiled_indices.json).

In the **📝 Index Editor** tab, you can search and filter the database:
- **Search Bar**: Query by abbreviation, name, or formula.
- **Category Filter**: Filter indices by application (e.g., `vegetation`, `water`, `soil`, or `archaeology`).
- **Formula Editor**: Edit any index formula directly in the text input box. Custom parameters (such as `s` for WDVI or `eta` for GEMI) and multi-step formulas (semicolon-separated) are fully supported.
- **Add Custom Index**: Click `➕ Add Custom Index` to append new indices. The system automatically parses the required band names from the formula.
- **Save Selection**: Activating the checkboxes next to the indices and clicking `💾 Save Selection & Apply to Sidebar` updates [project_indices.json](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/project_indices.json). Only the selected indices will appear as checkable options in the main sidebar, keeping the workspace clutter-free.

---

## 🔬 Core Parameters for Archaeologists

- **WDVI Slope (s)**: Slope of the soil line in the NIR-Red spectral space. Because soil reflectance varies based on wetness or composition, the slope coefficient `s` allows the **Weighted Difference Vegetation Index (WDVI)** to subtract the bare soil background signal. This is critical for highlighting subtle cropmarks in fields with sparse vegetation or open soil patches.
- **Reflectance Scaling**: Scales digital pixel values (Digital Numbers, DN) to physical surface reflectance range `[0.0 - 1.0]`. ArcSpectra automatically detects if scaling is required (e.g., if DN ranges up to 255 or 65535) and scales it, preventing formula saturation and calculation errors (particularly vital for NDVI, SAVI, and GEMI).

---

## 🚀 Installation & Running

### 1. Requirements Setup
Ensure Python is installed, then install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run the Desktop GUI
To launch the ArcSpectra desktop application:
- **Windows Double-Click**: Open [run_gui.bat](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/run_gui.bat).
- **Via Terminal**:
  ```bash
  python gui.py
  ```

### 3. Run the Jupyter Notebook
To run research scripts and batch processing:
- **Windows Double-Click**: Open [run_notebook.bat](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/run_notebook.bat).
- **Via Terminal**:
  ```bash
  jupyter notebook multispectral_processing.ipynb
  ```

---

## 📁 File Structure

- [gui.py](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/gui.py): Main Tkinter GUI application, layouts, and OpenStreetMap rendering logic.
- [processor.py](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/processor.py): Dynamic math calculations engine utilizing Rasterio and NumPy.
- [multispectral_processing.ipynb](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/multispectral_processing.ipynb): Jupyter Notebook implementing the shared calculations engine.
- [compiled_indices.json](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/compiled_indices.json): Pre-compiled database containing 182 Geopera formulas.
- [sensor_templates.json](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/sensor_templates.json): Persisted sensor presets.
- [project_indices.json](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/project_indices.json): Persisted active indices list.
- `input/`: Folder where input multispectral GeoTIFF files should be placed.
- `output/`: Folder where computed rasters and PNG plots are exported, categorized by raster name.
