# 🎛️ User Interface Guide

A complete reference directory of all input fields, dropdown menus, sliders, and tab views inside the ArcSpectra desktop dashboard.

---

## 1. Settings Sidebar

- **Input GeoTIFF File**:
  - *Description:* Absolute path to the source multispectral GeoTIFF image.
  - *Use Case:* Browse and select your stitched drone orthomosaic or satellite image.
- **Output Directory**:
  - *Description:* Target folder where index GeoTIFFs and plots are exported.
  - *Use Case:* ArcSpectra automatically creates a subfolder named after the input file to keep your files organized.
- **Sensor Mapping Preset**:
  - *Description:* Dropdown menu containing templates to map Red, Green, Blue, RedEdge, and NIR wavelengths to the corresponding channel numbers of your raw GeoTIFF file.
- **Sensor Mapping Builder (`🛠️ Build` Button)**:
  - *Description:* Modal window to customize, create, edit, or delete sensor templates.
- **Active Vegetation Indices**:
  - *Description:* Checkboxes to toggle which indices to compute in the upcoming run. Only the active selections from the *Index Editor* will appear here.
- **WDVI Slope (s)**:
  - *Description:* Coefficient `s` defining the soil line slope in the NIR-Red spectral space (default: `1.0`).
  - *Archaeological Value:* Corrects for soil background noise. Subtracting `s * Red` from the `NIR` channel isolates true plant signatures from bare ground reflectance.
- **Reflectance Scaling Mode**:
  - *Description:* Specifies how raw Digital Numbers (DN) are normalized to physical reflectance values range `[0.0 - 1.0]`.
  - *Options:*
    - `Automatic (recommended)`: Auto-detects 8-bit (0-255) or 16-bit (0-65535) integer files and applies division factors dynamically.
    - `1.0 (No scaling)`: Retains raw values unmodified.
    - `Custom Value`: Enables scaling by a custom user-defined denominator.
- **Custom Factor**:
  - *Description:* Numeric input denominator active only when "Custom Value" scaling mode is selected.

---

## 2. Main Tab Panels

- **📁 Input Information**:
  - *Metadata Table:* Shows file properties like dimensions, band count, and spatial CRS.
  - *OSM Footprint Map:* Draws an emerald green bounding polygon over a stitched OpenStreetMap tile map, visualising where the orthomosaic is located on the globe.
- **📊 Results Visualizer**:
  - *Grid Canvas:* Displays a 2x3 overview plot of calculated index maps stretched using local percentiles.
  - *Statistics panel:* Lists min, max, mean, and standard deviation for each computed index.
- **📝 Index Editor**:
  - *Geopera Database Source:* Connection link to the [Geopera Spectral Database (docs.geopera.com/spectral-indices)](https://docs.geopera.com/spectral-indices).
  - *Search & Filter:* Query the database of 182 indices by name, category, or formula.
  - *Formula Editor:* Edit index formulas dynamically or add new custom ones.
- **📝 Console Logs**:
  - *Log Output:* Live display of computation logs, background thread statuses, and error reports.
