# ArcSpectra - User Guide & Archaeological Remote Sensing Handbook

Welcome to the **ArcSpectra** wiki guide! This page provides a comprehensive manual covering the archaeological context of vegetation stress, configuration templates for multispectral sensors, and a detailed reference for all user interface controls.

---

## 🏛️ Archaeological Context: Cropmarks & Soilmarks

Multispectral remote sensing in archaeology leverages the spectral signatures of vegetation to detect buried, non-visible cultural heritage:

*   **Positive Cropmarks**: In filled-in features (such as ditches, pits, or postholes), the soil layer is deeper, looser, and holds more moisture and nutrients. Plants growing above these features develop stronger root systems, grow taller, contain more chlorophyll, and remain green longer. This is reflected in higher NIR reflectance values.
*   **Negative Cropmarks**: Over buried stone walls, paved roads, or building foundations, the topsoil layer is shallow. Plants suffer from restricted root space, water deficiency, and nutrient stress. They mature faster, are smaller, contain less chlorophyll, and wilt earlier. This manifests as lower NIR reflectance values and higher Red reflectance.
*   **Soilmarks**: In bare agricultural fields, differences in subsoil composition (e.g., exposed limestone foundations, light clay fill in ditches) create soil color anomalies visible in visible (RGB) and Near-Infrared spectra.

---

## 🎛️ Detailed UI Fields & Controls Directory

### 1. Settings Sidebar
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
  - *Description:* Coefficient `s` defining the soil line slope in the NIR-Red spectral space.
  - *Archaeological Value:* Corrects for soil background noise. Subtracting `s * Red` from the `NIR` channel isolates true plant signatures from bare ground reflectance.
- **Reflectance Scaling Mode**:
  - *Description:* Specifies how raw Digital Numbers (DN) are normalized to physical reflectance values range `[0.0 - 1.0]`.
  - *Options:*
    - `Automatic (recommended)`: Auto-detects 8-bit (0-255) or 16-bit (0-65535) integer files and applies division factors dynamically.
    - `1.0 (No scaling)`: Retains raw values unmodified.
    - `Custom Value`: Enables scaling by a custom user-defined denominator.
- **Custom Factor**:
  - *Description:* Numeric input denominator active only when "Custom Value" scaling mode is selected.

### 2. Main Interface Tabs
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

---

## 🛠️ Sensor Configuration Examples

Multispectral cameras arrange their sensors in differing order. Here is how to configure ArcSpectra for common setups using the **Sensor Template Builder**:

### 1. DJI Multispectral (e.g., Phantom 4 Multispectral)
Typical DJI band arrangement:
1.  **Band 1**: Blue (B)
2.  **Band 2**: Green (G)
3.  **Band 3**: Red (R)
4.  **Band 4**: RedEdge (RE)
5.  **Band 5**: Near-Infrared (NIR)

*Configuration in Builder:*
- `Red` ➡️ `3`
- `Green` ➡️ `2`
- `Blue` ➡️ `1`
- `RedEdge` ➡️ `4`
- `NIR` ➡️ `5`

### 2. MicaSense Sequoia
Typical Sequoia band arrangement:
1.  **Band 1**: Green (G)
2.  **Band 2**: Red (R)
3.  **Band 3**: RedEdge (RE)
4.  **Band 4**: Near-Infrared (NIR)

*Configuration in Builder:*
- `Green` ➡️ `1`
- `Red` ➡️ `2`
- `RedEdge` ➡️ `3`
- `NIR` ➡️ `4`
- `Blue` ➡️ `None` (not captured by the sensor)

---

## 📊 Archaeological Index Reference

ArcSpectra comes with key indices calibrated specifically for vegetation stress detection:

*   **NDVI (Normalized Difference Vegetation Index)**: `(NIR - Red) / (NIR + Red)`
    - *Utility:* The primary index for mapping canopy biomass. Highlights positive cropmarks over moisture-retaining ditches (lush growth) and negative cropmarks over buried walls (drought stress).
*   **GNDVI (Green NDVI)**: `(NIR - Green) / (NIR + Green)`
    - *Utility:* Uses green wavelengths. Excellent for mapping early crop chlorosis and canopy water stress over structural remains.
*   **SAVI (Soil Adjusted Vegetation Index)**: `(1.5 * (NIR - Red)) / (NIR + Red + 0.5)`
    - *Utility:* Adjusts for bare ground backscatter. Essential for archaeological prospection in open, semi-arid, or sparsely cropped agricultural fields.
*   **WDVI (Weighted Difference Vegetation Index)**: `NIR - (s * Red)`
    - *Utility:* Adjusts for the local soil line slope `s`. Provides soil-noise-free cropmark highlighting.
*   **NAVI & NAI**: `(NIR - RedEdge) / (RedEdge + NIR)`
    - *Utility:* Targets the sensitive "Red-Edge" band. Maximizes contrast differences between healthy crop canopies and plants stressed by archaeological features.
*   **NDWI (Normalized Difference Water Index)**: `(Green - NIR) / (Green + NIR)`
    - *Utility:* Directly correlates with plant leaf moisture content, highlighting damp archaeological anomalies.
