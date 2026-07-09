# 🛠️ Sensor Configuration Guide

Multispectral cameras and satellite platforms arrange their spectral bands in different channels or indices. To process your images correctly in ArcSpectra, you must map each index formula variable (e.g., `Red`, `Green`, `Blue`, `NIR`, `RedEdge`) to the corresponding channel number in your GeoTIFF or image stack.

This guide provides the band assignments for all common drone and satellite multispectral presets built into ArcSpectra.

---

## 📋 Quick Reference Table

| Preset Name | Blue | Green | Red | RedEdge | NIR |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **NRW (State Geodata)** | 3 | 2 | 1 | — | 4 |
| **DJI Multispectral (P4M)** | 1 | 2 | 3 | 4 | 5 |
| **DJI Mavic 3M** | — | 1 | 2 | 3 | 4 |
| **MicaSense RedEdge / Altum (Wavelength-Sorted)** | 1 | 2 | 3 | 4 | 5 |
| **MicaSense RedEdge / Altum (Raw / Native)** | 1 | 2 | 3 | 5 | 4 |
| **Parrot Sequoia (SEQ)** | — | 1 | 2 | 3 | 4 |
| **Sentinel-2 (B4,B3,B2,B8,B5)** | 2 | 3 | 4 | 5 | 8 |
| **Landsat 8/9 (B4,B3,B2,B5)** | 2 | 3 | 4 | — | 5 |
| **PlanetScope (4-Band)** | 1 | 2 | 3 | — | 4 |
| **PlanetScope SuperDove (8-Band)** | 2 | 4 | 6 | 7 | 8 |
| **WorldView-2/3 VNIR (8-Band)** | 2 | 3 | 5 | 6 | 7 |
| **RapidEye (5-Band)** | 1 | 2 | 3 | 4 | 5 |
| **MODIS (B1-B4)** | 3 | 4 | 1 | — | 2 |
| **MAPIR Survey3 RGN (Processed)** | — | 2 | 1 | — | 3 |
| **MAPIR Survey3 NGB (Processed)** | 3 | 2 | — | — | 1 |

---

## 🛸 Drone & UAV Multispectral Presets

### 1. DJI Multispectral (P4M)
Used for the **DJI Phantom 4 Multispectral**. Captures five discrete channels.
*   **Blue** ➡️ `1` (450 nm)
*   **Green** ➡️ `2` (560 nm)
*   **Red** ➡️ `3` (650 nm)
*   **RedEdge** ➡️ `4` (730 nm)
*   **NIR** ➡️ `5` (840 nm)

### 2. DJI Mavic 3M
Used for the **DJI Mavic 3 Multispectral**. It features four multispectral sensors (the Blue channel is absent in the multispectral sensor array).
*   **Green** ➡️ `1` (560 nm)
*   **Red** ➡️ `2` (650 nm)
*   **RedEdge** ➡️ `3` (730 nm)
*   **NIR** ➡️ `4` (860 nm)

### 3. MicaSense RedEdge / Altum
MicaSense cameras (RedEdge-MX, RedEdge-P, Altum, Altum-PT) can output files in two different structures depending on the photogrammetry processing pipeline:
*   **Wavelength-Sorted (Processed Orthomosaics):** 
    Wavelength sequence (Blue, Green, Red, RedEdge, NIR).
    *   `Blue: 1`, `Green: 2`, `Red: 3`, `RedEdge: 4`, `NIR: 5`
*   **Raw / Native (Raw sensor outputs or custom pipelines):**
    Native file suffix order (Blue, Green, Red, NIR, RedEdge).
    *   `Blue: 1`, `Green: 2`, `Red: 3`, `NIR: 4`, `RedEdge: 5`

### 4. Parrot Sequoia (SEQ)
Standard 4-band setup for the Parrot Sequoia+ sensor.
*   **Green** ➡️ `1` (550 nm)
*   **Red** ➡️ `2` (660 nm)
*   **RedEdge** ➡️ `3` (735 nm)
*   **NIR** ➡️ `4` (790 nm)

### 5. MAPIR Survey3
For single-sensor modified Bayer cameras processed using MAPIR software:
*   **MAPIR Survey3 RGN (Red, Green, NIR):**
    *   `Red: 1`, `Green: 2`, `NIR: 3`
*   **MAPIR Survey3 NGB (NIR, Green, Blue):**
    *   `NIR: 1`, `Green: 2`, `Blue: 3`

---

## 🛰️ Satellite Presets

### 1. Sentinel-2
Standard band indices matching the official ESA band numbers.
*   **Blue (B2)** ➡️ `2`
*   **Green (B3)** ➡️ `3`
*   **Red (B4)** ➡️ `4`
*   **RedEdge (B5)** ➡️ `5` (705 nm)
*   **NIR (B8)** ➡️ `8` (842 nm)

### 2. Landsat 8/9
Standard band indices matching the USGS Landsat band numbers.
*   **Blue (B2)** ➡️ `2`
*   **Green (B3)** ➡️ `3`
*   **Red (B4)** ➡️ `4`
*   **NIR (B5)** ➡️ `5`

### 3. PlanetScope (SuperDove)
*   **PlanetScope (4-Band):**
    *   `Blue: 1`, `Green: 2`, `Red: 3`, `NIR: 4`
*   **PlanetScope SuperDove (8-Band):**
    *   `Blue: 2`, `Green: 4`, `Red: 6`, `RedEdge: 7`, `NIR: 8`

### 4. WorldView-2 / WorldView-3 VNIR (8-Band)
*   **Blue (B2)** ➡️ `2`
*   **Green (B3)** ➡️ `3`
*   **Red (B5)** ➡️ `5`
*   **RedEdge (B6)** ➡️ `6`
*   **NIR1 (B7)** ➡️ `7`

### 5. RapidEye (5-Band)
*   **Blue** ➡️ `1`
*   **Green** ➡️ `2`
*   **Red** ➡️ `3`
*   **RedEdge** ➡️ `4`
*   **NIR** ➡️ `5`

### 6. MODIS (B1-B4)
*   **Red (B1)** ➡️ `1`
*   **NIR (B2)** ➡️ `2`
*   **Blue (B3)** ➡️ `3`
*   **Green (B4)** ➡️ `4`
