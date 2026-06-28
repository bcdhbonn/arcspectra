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

## 🎛️ Detailed UI Fields & Controls Guide

The ArcSpectra interface is organized into a settings sidebar and a tabbed main content panel. Below is a detailed explanation of what every input field, dropdown, and checkbox does:

### 1. Settings Sidebar Controls
- **Input GeoTIFF File (Entry & Browse Button)**:
  - *What it does:* Specifies the absolute path to the raw multispectral GeoTIFF image to be processed.
  - *Archaeological Context:* The image should be an orthomosaic (stitched drone flight) or satellite scene containing at least three bands (typically Green, Red, and Near-Infrared).
- **Output Directory (Entry & Browse Button)**:
  - *What it does:* The folder where calculated index GeoTIFFs and the overview grid plot will be exported.
  - *Archaeological Context:* Keeps results organized. A subdirectory named after your input file will be created inside this folder.
- **Sensor Mapping Preset (Dropdown)**:
  - *What it does:* Selects a pre-configured band order template matching your multispectral camera.
  - *Options:* Common presets include `DJI Multispectral`, `NRW (State Geodata)`, `SEQ (MicaSense)`, or `Custom Configuration` (for manual entry).
- **Sensor Mapping Builder (`🛠️ Build` Button)**:
  - *What it does:* Opens a modal window to create, rename, edit, or delete sensor templates, mapping bands to channel numbers.
- **Active Vegetation Indices (Checkboxes)**:
  - *What it does:* Allows toggling which spectral indices to compute. Only indices selected in the *Index Editor* will appear here.
- **WDVI Slope (s) (Numeric Entry)**:
  - *What it does:* Sets the slope coefficient `s` of the "soil line" in the Near-Infrared (NIR) vs. Red spectral space (default: `1.0`).
  - *Archaeological Context:* Used by the Weighted Difference Vegetation Index (WDVI). By adjusting `s`, you mathematically subtract background soil reflectance, isolating subtle canopy signals from sparse cropmarks.
- **Reflectance Scaling Mode (Dropdown)**:
  - *What it does:* Defines how the raw pixel values (Digital Numbers, DN) are scaled before calculations.
  - *Options:*
    - `Automatic (recommended)`: Automatically detects whether values represent reflectances (0.0 to 1.0) or digital numbers, and applies scaling coefficients of `255.0` or `65535.0` to normalize them.
    - `1.0 (No scaling)`: Leaves pixel values unmodified.
    - `Custom Value`: Enables the *Custom Factor* entry to scale by a custom user-defined constant.
- **Custom Factor (Numeric Entry)**:
  - *What it does:* Active only when scaling mode is set to "Custom Value". Divides all raw pixel values by this number.
- **Start Processing (Button)**:
  - *What it does:* Starts the background computation thread to execute index calculation.
- **Open Output Folder (Button)**:
  - *What it does:* Opens the resolved destination subdirectory in your system file explorer.

### 2. Main Content Tabs
- **📁 Input Information**:
  - *Metadata Card:* Displays spatial details of the loaded image (width, height, coordinate reference system, and band count).
  - *OSM Footprint Map:* Automatically transforms UTM coordinates to WGS84 and stitches OpenStreetMap tiles, drawing an emerald green polygon outlining your image's physical footprint.
- **📊 Results Visualizer**:
  - *Plot Canvas:* Displays a rescaled 2x3 overview plot of all calculated indices.
  - *Statistics/Interactive Map:* (Active after processing) Shows min, max, mean, and standard deviation for each index.
- **📝 Index Editor**:
  - *Geopera Database Source:* Provides the database connection link to the [Geopera Spectral Database (docs.geopera.com/spectral-indices)](https://docs.geopera.com/spectral-indices).
  - *Search:* Filters the table by index name, formula, or category.
  - *Formula Inputs:* Allows modifying formulas and updating the local JSON.
- **📝 Console Logs**:
  - *Text Console:* Displays real-time logging, processing updates, and error stacktraces.

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

ArcSpectra is pre-compiled with a database of **182 optical spectral indices** parsed from the [Geopera Spectral Database (docs.geopera.com/spectral-indices)](https://docs.geopera.com/spectral-indices) and saved in [compiled_indices.json](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/compiled_indices.json).

In the **📝 Index Editor** tab, you can search and filter the database:
- **Search Bar**: Query by abbreviation, name, or formula.
- **Category Filter**: Filter indices by application (e.g., `vegetation`, `water`, `soil`, or `archaeology`).
- **Formula Editor**: Edit any index formula directly in the text input box. Custom parameters (such as `s` for WDVI or `eta` for GEMI) and multi-step formulas (semicolon-separated) are fully supported.
- **Add Custom Index**: Click `➕ Add Custom Index` to append new indices. The system automatically parses the required band names from the formula.
- **Save Selection**: Activating the checkboxes next to the indices and clicking `💾 Save Selection & Apply to Sidebar` updates [project_indices.json](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/project_indices.json). Only the selected indices will appear as checkable options in the main sidebar, keeping the workspace clutter-free.

---

## 📊 Spectral Indices in Archaeology (Archaeological Guide)

ArcSpectra loads a database of **182 optical indices** and offers a pre-configured **`archaeology`** category with the most relevant indices for archaeological prospection:

*   **NDVI (Normalized Difference Vegetation Index)**
    *   *Formula:* `(NIR - Red) / (NIR + Red)`
    *   *Archaeological Value:* The standard index for biomass and vegetation health. Extremely effective at mapping cropmarks over filled-in features (e.g., ditches, pits) or massive structures (e.g., Roman masonry, foundations).
*   **GNDVI (Green NDVI)**
    *   *Formula:* `(NIR - Green) / (NIR + Green)`
    *   *Archaeological Value:* Uses the green channel instead of red. More sensitive to variations in canopy chlorophyll content, making it excellent for detecting early stages of vegetation stress over buried structures.
*   **SAVI (Soil Adjusted Vegetation Index)**
    *   *Formula:* `(1.5 * (NIR - Red)) / (NIR + Red + 0.5)`
    *   *Archaeological Value:* Minimizes the disturbing influence of bare soil background. Essential for prospection in agricultural fields with sparse crop cover or dry soils.
*   **WDVI (Weighted Difference Vegetation Index)**
    *   *Formula:* `NIR - (s * Red)`
    *   *Archaeological Value:* Corrects vegetation values using the slope of the soil line (`s`). Perfectly suited for completely eliminating background soil reflectance noise.
*   **NAVI (Normalized Archaeological Vegetation Index)** & **NAI (Normalized Archaeological Index)**
    *   *Formula:* `(NIR - RedEdge) / (RedEdge + NIR)`
    *   *Archaeological Value:* Leverages wavelengths along the "Red-Edge" transition zone (~700–800 nm). Maximizes the spectral contrast between healthy surrounding crops and vegetation stressed by subsurface archaeological features.
*   **NDWI (Normalized Difference Water Index)**
    *   *Formula:* `(Green - NIR) / (Green + NIR)`
    *   *Archaeological Value:* Responds to leaf canopy and soil water content. Ideal for detecting buried moisture-retaining ditch systems, moats, and hollows.

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
