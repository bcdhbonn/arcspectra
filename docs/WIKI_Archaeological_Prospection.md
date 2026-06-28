# 🏛️ Archaeological Prospection Guide

Multispectral remote sensing in archaeology leverages the spectral signatures of vegetation to detect buried, non-visible cultural heritage. Below is an introduction to cropmarks, soilmarks, and the active indices calibrated for archaeological research.

---

## 🌾 Cropmarks & Soilmarks

- **Positive Cropmarks**: In filled-in features (such as ditches, pits, or postholes), the soil layer is deeper, looser, and holds more moisture and nutrients. Plants growing above these features develop stronger root systems, grow taller, contain more chlorophyll, and remain green longer. This is reflected in higher NIR reflectance values.
- **Negative Cropmarks**: Over buried stone walls, paved roads, or building foundations, the topsoil layer is shallow. Plants suffer from restricted root space, water deficiency, and nutrient stress. They mature faster, are smaller, contain less chlorophyll, and wilt earlier. This manifests as lower NIR reflectance values and higher Red reflectance.
- **Soilmarks**: In bare agricultural fields, differences in subsoil composition (e.g., exposed limestone foundations, light clay fill in ditches) create soil color anomalies visible in visible (RGB) and Near-Infrared spectra.

---

## 📊 Archaeological Index Reference

ArcSpectra comes pre-compiled with key indices calibrated specifically for vegetation stress detection:

*   **NDVI (Normalized Difference Vegetation Index)**
    *   *Formula:* `(NIR - Red) / (NIR + Red)`
    *   *Utility:* The primary index for mapping canopy biomass. Highlights positive cropmarks over moisture-retaining ditches (lush growth) and negative cropmarks over buried walls (drought stress).
*   **GNDVI (Green NDVI)**
    *   *Formula:* `(NIR - Green) / (NIR + Green)`
    *   *Utility:* Uses green wavelengths. Excellent for mapping early crop chlorosis and canopy water stress over structural remains.
*   **SAVI (Soil Adjusted Vegetation Index)**
    *   *Formula:* `(1.5 * (NIR - Red)) / (NIR + Red + 0.5)`
    *   *Utility:* Adjusts for bare ground backscatter. Essential for archaeological prospection in open, semi-arid, or sparsely cropped agricultural fields.
*   **WDVI (Weighted Difference Vegetation Index)**
    *   *Formula:* `NIR - (s * Red)`
    *   *Utility:* Adjusts for the local soil line slope `s`. Provides soil-noise-free cropmark highlighting.
*   **NAVI (Normalized Archaeological Vegetation Index)** & **NAI (Normalized Archaeological Index)**
    *   *Formula:* `(NIR - RedEdge) / (RedEdge + NIR)`
    *   *Utility:* Targets the sensitive "Red-Edge" band. Maximizes contrast differences between healthy crop canopies and plants stressed by archaeological features.
*   **NDWI (Normalized Difference Water Index)**
    *   *Formula:* `(Green - NIR) / (Green + NIR)`
    *   *Utility:* Directly correlates with plant leaf moisture content, highlighting damp archaeological anomalies like ditches and moats.
