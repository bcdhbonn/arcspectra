# 🌿🏛️ ArcSpectra - Multispectral Vegetation Index Processor

**ArcSpectra** ist eine leistungsstarke und benutzerfreundliche Python-Anwendung zur Analyse von multispektralen Luft- und Satellitenbildern, speziell entwickelt für die **zerstörungsfreie archäologische Prospektion (Remote Sensing Archaeology)**. 

Das System dient der Erkennung von vegetations- und bodenbezogenen Anomalien – sogenannten **Bewuchsmerkmalen (Cropmarks)** und **Bodenmerkmalen (Soilmarks)** – die auf im Boden verborgene archäologische Strukturen wie Fundamente, Mauern, Gräben, Gruben oder Pfostenschlitze hinweisen.

Befindet sich beispielsweise ein verfüllter Graben im Boden, speichert dieser mehr Feuchtigkeit, was zu üppigerem Pflanzenwachstum führt (positives Bewuchsmerkmal). Liegt dort eine antike Steinmauer, ist der Wurzelraum stark begrenzt, was zu Trockenstress führt (negatives Bewuchsmerkmal). Diese Unterschiede werden durch multispektrale Indizes im Infrarotbereich sichtbar gemacht.

---

## 🗺️ Systemarchitektur & Komponenten

Das Projekt basiert auf Berechnungen der R-Bibliothek `RStoolbox` und der **Geopera Spectral Indices Database** (docs.geopera.com/spectral-indices) und stellt zwei Benutzeroberflächen bereit, die dieselbe optimierte Berechnungs-Engine nutzen:

1. **Desktop-Dashboard (`gui.py`)**: Eine interaktive Desktop-GUI auf Basis von `customtkinter` mit automatischer Metadaten-Inspektion, interaktiver **OpenStreetMap-Footprint-Karte**, dynamischen **archäologischen Tooltips**, einem **Sensor-Template-Builder** und Echtzeit-Ergebnisvisualisierung mit Light/Dark-Umschaltung.
2. **Jupyter Research Notebook (`multispectral_processing.ipynb`)**: Ein vollständig dokumentiertes Forschungs-Notebook für reproduzierbare wissenschaftliche Stapelverarbeitungen in Python.

---

## 📊 Spektralindizes in der Archäologie (Archäologischer Leitfaden)

ArcSpectra lädt eine Datenbank mit **182 optischen Indizes** und bietet eine vorkonfigurierte Kategorie **`archaeology`** mit den für die archäologische Prospektion wichtigsten Indizes:

*   **NDVI (Normalized Difference Vegetation Index)**
    *   *Formel:* `(NIR - Red) / (NIR + Red)`
    *   *Archäologischer Nutzen:* Der Standard-Index für Biomasse und Pflanzenvitalität. Extrem effektiv beim Aufspüren von Bewuchsmerkmalen über verfüllten Befunden (z. B. Gräben) oder massiven Strukturen (z. B. römische Fundamente).
*   **GNDVI (Green NDVI)**
    *   *Formel:* `(NIR - Green) / (NIR + Green)`
    *   *Archäologischer Nutzen:* Verwendet den grünen Kanal anstelle des roten. Reagiert empfindlicher auf Schwankungen des Chlorophyllgehalts und eignet sich hervorragend zur Erkennung früher Phasen von Vegetationsstress über verborgenen Mauern.
*   **SAVI (Soil Adjusted Vegetation Index)**
    *   *Formel:* `(1.5 * (NIR - Red)) / (NIR + Red + 0.5)`
    *   *Archäologischer Nutzen:* Minimiert den störenden Einfluss von offenem Boden. Unerlässlich für die Prospektion auf Äckern mit lückenhaftem Bewuchs oder in trockenen Regionen.
*   **WDVI (Weighted Difference Vegetation Index)**
    *   *Formel:* `NIR - (s * Red)`
    *   *Archäologischer Nutzen:* Bereinigt die Vegetationswerte mithilfe der Steigung der Bodenlinie (`s`). Perfekt geeignet, um Störeffekte von reinem Boden vollständig zu eliminieren.
*   **NAVI (Normalized Archaeological Vegetation Index)** & **NAI (Normalized Archaeological Index)**
    *   *Formel:* `(NIR - RedEdge) / (RedEdge + NIR)`
    *   *Archäologischer Nutzen:* Nutzt die Wellenlängen im Bereich der "Red-Edge"-Kante (~700–800 nm). Maximiert den spektralen Kontrast zwischen gesundem Bewuchs und durch archäologische Strukturen gestresster Vegetation.
*   **NDWI (Normalized Difference Water Index)**
    *   *Formel:* `(Green - NIR) / (Green + NIR)`
    *   *Archäologischer Nutzen:* Reagiert sensitiv auf den Wassergehalt in Blättern und Böden. Ideal zum Aufspüren feuchter Grabenwerke oder feuchter Senken.

---

## 🛠️ Wichtige Parameter & Einstellungen

*   **WDVI Soil Line Slope (s)**: Die Steigung der Bodenlinie im NIR-Red-Spektralraum. Ermöglicht die mathematische Korrektur von Reflexionswerten offener Böden, um Bewuchsmerkmalen exakter zu isolieren.
*   **Reflectance Scaling**: Skaliert die rohen digitalen Pixelwerte (DN) des Sensors (z. B. 0–255 bei 8-Bit oder 0–65535 bei 16-Bit) in physikalisch korrekte Reflexionsgrade zwischen `0.0` und `1.0`. Dies ist für viele Indizes (z. B. GEMI) zwingend erforderlich.

---

## 🚀 Installation & Inbetriebnahme

### 1. Voraussetzungen installieren
Stelle sicher, dass Python installiert ist. Installiere die benötigten Bibliotheken über das Terminal/PowerShell:

```bash
pip install -r requirements.txt
```

### 2. Desktop-GUI starten
Du kannst das grafische Programm auf zwei Arten starten:
*   **Windows (einfacher Doppelklick)**: Öffne die Datei **`run_gui.bat`**.
*   **Über das Terminal**:
    ```bash
    python gui.py
    ```

### 3. Jupyter Notebook starten
Um das Notebook für automatisierte Auswertungen oder eigene Skripte zu nutzen:
*   **Windows (Doppelklick)**: Starte die Datei **`run_notebook.bat`**.
*   **Über das Terminal**:
    ```bash
    jupyter notebook multispectral_processing.ipynb
    ```

---

## 📁 Datenstruktur

*   [gui.py](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/gui.py): Desktop-GUI mit Kartenansichten, Tooltips und Editor-Tabs.
*   [processor.py](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/processor.py): Mathematischer Kern der Rasterberechnung (Rasterio/NumPy).
*   [multispectral_processing.ipynb](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/multispectral_processing.ipynb): Jupyter Notebook zur Nutzung in Python-Skripten.
*   [sensor_templates.json](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/sensor_templates.json): Datei zur dauerhaften Speicherung der Sensor-Kanalkonfigurationen.
*   [compiled_indices.json](file:///c:/Users/langm/sciebo/BCDH_Projektbox/1_BCDH%20Intern/Scripts/multispectral/multispectral/compiled_indices.json): Datenbank aller 182 spektralen Indizes von Geopera.
*   `input/`: Lege hier deine GeoTIFF-Dateien ab, die verarbeitet werden sollen.
*   `output/`: Hier werden die berechneten Raster-Dateien (als einzelne GeoTIFFs) und die Plot-Übersichten als PNG exportiert, automatisch sortiert in Unterordnern nach dem Dateinamen des Eingabebildes.
