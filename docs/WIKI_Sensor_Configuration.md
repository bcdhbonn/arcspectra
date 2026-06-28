# 🛠️ Sensor Configuration Guide

Multispectral cameras arrange their sensors in differing order. Here is how to configure ArcSpectra for common setups using the **Sensor Template Builder**:

---

## 1. DJI Multispectral (e.g., Phantom 4 Multispectral)

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

---

## 2. MicaSense Sequoia

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
