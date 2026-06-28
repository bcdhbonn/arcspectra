# 🌿🏛️ ArcSpectra - Multispectral Vegetation Index Processor

**ArcSpectra** is a high-performance Python application designed for remote sensing archaeology and non-destructive prospection. It calculates and visualizes optical spectral indices from multispectral drone (UAV) or satellite imagery to reveal buried archaeological features (cropmarks and soilmarks).

For a detailed explanation of archaeological prospection, DJI & MicaSense sensor mapping examples, and UI controls, please refer to the **[ArcSpectra GitHub Wiki](https://github.com/bcdhbonn/arcspectra/wiki)**.

---

## ✨ Features

- **Dynamic GUI Dashboard**: Built with CustomTkinter for real-time visualization and parameter tuning.
- **Shared Research Notebook**: Jupyter Notebook utilizing the same dynamic calculation backend.
- **Geopera Database Integration**: Full access to 182 optical spectral indices via [Geopera (docs.geopera.com/spectral-indices)](https://docs.geopera.com/spectral-indices).
- **Custom Sensor Template Builder**: Easily map, save, and edit camera band orders (e.g. DJI, Sequoia).
- **OpenStreetMap Footprint**: Automatic UTM conversion to WGS84 to draw image footprint coordinates.
- **Archaeological Focus**: Pre-configured categories (NDVI, GNDVI, WDVI, SAVI, NAVI, NDWI) calibrated for vegetation stress mapping.

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
- [docs/WIKI_Guide.md](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/docs/WIKI_Guide.md): Detailed user manual to be copy-pasted into the GitHub Wiki.
- [compiled_indices.json](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/compiled_indices.json): Pre-compiled database containing 182 Geopera formulas.
- [sensor_templates.json](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/sensor_templates.json): Persisted sensor presets.
- [project_indices.json](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/project_indices.json): Persisted active indices list.
- `input/`: Folder where input multispectral GeoTIFF files should be placed.
- `output/`: Folder where computed rasters and PNG plots are exported.
