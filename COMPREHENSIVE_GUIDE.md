# Comprehensive Guide: Mappa Mundi sine Tempore

Welcome to the official comprehensive guide for **Mappa Mundi sine Tempore**. This document provides an in-depth reference covering what the application is, how to install all prerequisite software, how it works under the hood, how to use all of its features, and step-by-step instructions for modders and developers looking to insert custom provinces, states, or nations.

---

## 1. Program Overview

### What It Is
**Mappa Mundi sine Tempore** is a high-performance, GPU-accelerated interactive web application and sandbox environment designed for grand strategy map editing, geopolitical scenario creation, and Paradox Interactive modding (specifically *Hearts of Iron IV* and *Europa Universalis IV*).

### Key Capabilities
- **60 FPS Real-Time WebGL Engine**: Renders a massive 5120x2560 resolution world map with instant zoom, pan, and dynamic shader effects.
- **Multi-Level Selection**: Edit at the individual Province level or grouped State level.
- **Dynamic Mapmodes**: Toggle seamlessly between Political (Country Ownership), State Division, and National Interest mapmodes.
- **Visual Overlays**:
  - **Dynamic State & Country Borders**: Uses a 4-Color Planar Graph Coloring algorithm to guarantee 0 border collisions.
  - **3D Terrain Heightmap**: GPU hillshading using real elevation data (`heightmap.png`).
  - **Pixel-Perfect Rivers**: Point-sampled river system overlay (`rivers_index.png`).
- **Disk & File Persistence**: Save and load progress via standalone `.json` save files, browser Quick Saves, or Python server presets.
- **Paradox / HOI4 Export**: Import and export Paradox-compatible state files, country definitions, and CSV data.

---

## 2. Prerequisites & Installation Guide

Before running the application or using processing scripts, ensure you have Python and the necessary dependencies installed.

### A. Downloading & Installing Python

#### Windows
1. Visit the official Python download page: [python.org/downloads](https://www.python.org/downloads/).
2. Click **Download Python 3.x.x** (Python 3.10 or newer is recommended).
3. Run the downloaded installer (`python-3.x.x-amd64.exe`).
4. > [!IMPORTANT]
   > **CRITICAL STEP**: On the very first setup screen, check the box at the bottom that says **"Add python.exe to PATH"**. If you skip this step, Windows will not recognize `python` commands in terminal/cmd.
5. Click **Install Now** and approve Windows Administrator privileges when prompted.

#### macOS
1. Install Homebrew (if not already installed) or download the macOS installer from [python.org/downloads/macos](https://www.python.org/downloads/macos/).
2. Alternatively, run in Terminal:
   ```bash
   brew install python
   ```

#### Linux (Ubuntu / Debian / Fedora)
Python 3 is pre-installed on most modern distributions. You can verify or install it via your package manager:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-pil python3-numpy
```

#### Verifying Python Installation
Open Command Prompt (`cmd`), PowerShell, or Terminal and run:
```bash
python --version
```
*(If on Linux/macOS, use `python3 --version`). You should see `Python 3.10.x` or similar.*

---

### B. Installing Required Python Packages (`pip`)

The background data utility scripts (`sync_provinces.py`, `scratch/process_rivers_png.py`, `scratch/bake_and_reset.py`) require image manipulation and array processing libraries.

Open Command Prompt / Terminal and run:
```bash
pip install Pillow numpy
```

#### What these packages do:
* **Pillow (`PIL`)**: Image processing library used to parse, color-index, and generate 5120x2560 map texture PNG files.
* **NumPy**: High-performance multidimensional array library used for rapid matrix pixel calculations across 13-million-pixel map layers.

---

### C. Recommended Map Editing Software

If you plan to modify map graphics (`provinces_index.png` or `rivers.png`), you will need an image editor that supports pixel-perfect editing without anti-aliasing.

> [!WARNING]
> **Avoid Anti-Aliased Brushes**: Never use soft brushes, airbrushes, or anti-aliased eraser tools when editing map textures. Blended border pixels create invalid RGB colors that break province ID mappings!

#### Recommended Editors:
1. **Paint.NET** (Free, Windows) - Highly recommended. Easy to set pencil tool to hard pixel edges.
2. **GIMP** (Free, Open Source, Cross-Platform) - Use the **Pencil Tool** (shortcut `N`) which draws strictly hard pixel edges.
3. **Adobe Photoshop** - Select the **Pencil Tool** (hidden under Brush tool) with Hardness 100% and Smoothing 0%.

---

### D. Running Mappa Mundi sine Tempore

1. Navigate to the project root directory.
2. **Start Server**:
   - On Windows: Double-click [`start_server.bat`](file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/start_server.bat).
   - Alternatively, open terminal and run:
     ```bash
     python server.py
     ```
3. Open your web browser to `http://localhost:8000`.

---

## 3. Technical Architecture & File Structure

### Frontend Stack (`index.html`)
The application runs as a single-page HTML5/WebGL application with an embedded glassmorphic UI overlay.

- **WebGL Shaders (`vsSource` & `fsSource`)**:
  - `u_indexTexture`: Maps 5120x2560 pixels to 24-bit Province IDs (`idx = R + G*256 + B*65536`).
  - `u_lutTexture`: A 2048x16 RGBA Lookup Table (LUT) encoding country colors and packed border hashes (`(cHash * 16) + sHash`).
  - `u_heightmapTexture`: 8-bit heightmap texture sampled for normal-map hillshading.
  - `u_riversTexture`: 5120x2560 RGBA river texture sampled for river rendering.
- **Web Workers (`initLabelWorker`)**:
  - Runs skeletonization and Dijkstra pathfinding in background threads to generate smooth curved country text labels along national spines without UI lag.

### Backend Stack (`server.py`)
- Built on Python’s `http.server.SimpleHTTPRequestHandler`.
- Provides CORS-enabled REST endpoints:
  - `POST /save`: Saves current country definitions and province ownership to `preset_ownership.json`.
  - `POST /saveStraits`: Saves naval strait connection pairs to `straits.json`.

---

### Core Data Files & Formats

| File Name | Format | Purpose |
| :--- | :--- | :--- |
| [`index.html`](file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/index.html) | HTML/JS/WebGL | Main application logic, shaders, UI panels, and map canvas. |
| [`server.py`](file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/server.py) | Python | Local server for file serving and saving JSON presets. |
| [`provinces_index.png`](file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/provinces_index.png) | 5120x2560 PNG | RGB-encoded province index map where pixel RGB = Province ID. |
| [`provinces_meta.json`](file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/provinces_meta.json) | JSON | Precomputed province centers, bounding boxes, water flags, and neighbor graphs. |
| [`definitions.json`](file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/definitions.json) | JSON | Master province database linking Province IDs to names and original RGB values. |
| [`states_config.json`](file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/states_config.json) | JSON | State definitions (State IDs, names, province lists, custom colors). |
| [`preset_ownership.json`](file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/preset_ownership.json) | JSON | Preset ownership file mapping provinces to country tags and defining nation colors/names. |
| [`heightmap.png`](file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/heightmap.png) | PNG | Grayscale elevation map for 3D hillshading. |
| [`rivers_index.png`](file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/rivers_index.png) | 5120x2560 PNG | RGBA river overlay map. |
| [`straits.json`](file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/straits.json) | JSON | Naval strait connection links. |

---

## 4. How to Use Features & Controls

### Canvas Controls & Mouse Navigation
- **Pan Map**: Left-click drag or Middle-click drag across the map.
- **Zoom Map**: Scroll wheel up (zoom in) / down (zoom out).
- **Inspect Pixel**: Left-click on any province to view its Province ID, State ID, Owner Tag, and Name in the **Province Editor** panel.

---

### Selection Modes
Located in the **Selection & Tools** sidebar panel:
- **Province Mode**: Single-clicking selects individual provinces.
- **State Mode**: Single-clicking selects the entire state (all provinces assigned to that state ID).
- **Paint Mode**: Allows painting provinces directly to the currently active country tag by clicking or dragging across the map.

---

### Mapmodes
Located at the top of the sidebar panel:
1. **Political Mapmode**: Displays national boundaries and fills land by country ownership colors.
2. **State Mapmode**: Colors land by state assignments and draws distinct state borders.
3. **National Interest Mapmode**: Displays striped overlay patterns indicating strategic national interest tiers.

---

### Overlays & Visual Toggles
Located in the **Overlays & Exporters** accordion panel:
- **Borders Overlay**: Toggles state and country boundary lines.
- **Heightmap Shading**: Enables 3D terrain elevation hillshading.
- **Rivers Overlay**: Toggles pixel-perfect river paths.

---

### Save & Load Progress System
Located under **Overlays & Exporters** in the sidebar:
- **Download Save (.json)**: Exports your entire active session (countries, tags, names, colors, states, province ownerships, interests) to a timestamped JSON file (`mappa_mundi_save_YYYY-MM-DD.json`).
- **Load Save (.json)**: Restores any previously saved `.json` file directly from your computer into the active canvas.
- **Quick Save (Browser)**: Instantly saves your session to browser `localStorage` without generating a file download.
- **Quick Load (Browser)**: Restores your `localStorage` quick-save session.

---

### State Creator & Editor
1. Click **State Mode** or select a province.
2. The **State Editor** panel will display the state's ID, Name, and Province Count.
3. **Create New State**: Enter a name in the State Creator panel and click **Create State**.
4. **Assign / Remove Provinces**: Select target provinces on the map and use **Add Selected to State** or **Remove Selected from State**.

---

### Country Creator & Editor
1. Open the **Country Editor** sidebar panel.
2. Enter a 3-character Country Tag (e.g., `UKR`, `FRA`, `GER`, `001`).
3. Set the nation's name and choose a country color using the RGB color picker.
4. Click **Create / Update Country**.
5. Select provinces or states and click **Paint Selected to Country** to transfer ownership.
6. Click **Save Preset** to persist changes directly to `preset_ownership.json` on disk via the Python server.

---

## 5. Developer Guide: Adding Custom Data

### A. How to Add or Modify Custom Provinces

To add a new province to the world map:

1. **Edit the Province Map Texture**:
   - Open [`provinces_index.png`](file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/provinces_index.png) (5120x2560) in an image editor (e.g. Photoshop, Paint.NET, GIMP).
   - Choose a unique RGB color `(R, G, B)` that is NOT used by any other province.
   - Calculate its Province ID: `ID = R + G*256 + B*65536`.
   - Paint the province shape using hard edges (disable anti-aliasing on your brush).

2. **Register in `definitions.json`**:
   - Open [`definitions.json`](file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/definitions.json) and add an entry:
     ```json
     "12345": {
       "id": 12345,
       "r": 120,
       "g": 45,
       "b": 200,
       "name": "Custom Province Name"
     }
     ```

3. **Recompute Metadata (`sync_provinces.py`)**:
   - Open command prompt and run:
     ```bash
     python sync_provinces.py
     ```
   - This script automatically calculates bounding boxes, pixel counts, center coordinates, land/water flags, and neighbor graphs, updating [`provinces_meta.json`](file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/provinces_meta.json).

---

### B. How to Add Custom States

To define a new state in the game:

1. **Option 1: Using the In-App Interface**:
   - Open `http://localhost:8000`.
   - Select the provinces for your new state.
   - Enter the state name in the **State Creator** panel and click **Create State**.
   - Click **Export States JSON** to download or save your new states configuration.

2. **Option 2: Editing `states_config.json` Directly**:
   - Open [`states_config.json`](file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/states_config.json).
   - Add your state definition using a unique integer state ID:
     ```json
     "999": {
       "id": 999,
       "name": "New Custom State",
       "provinces": [12345, 12346, 12347],
       "color": [100, 180, 220]
     }
     ```

---

### C. How to Add Custom Nations & Presets

To add a custom nation with starting ownership:

1. **Option 1: Using the In-App Country Editor**:
   - Open the **Country Editor** panel in `http://localhost:8000`.
   - Create a new tag (e.g. `NEW`), set its name and color, paint its provinces, and click **Save Preset**.

2. **Option 2: Editing `preset_ownership.json` Directly**:
   - Open [`preset_ownership.json`](file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/preset_ownership.json).
   - Add the country tag to `countries`:
     ```json
     "countries": {
       "NEW": {
         "name": "New Republic",
         "color": [220, 50, 80],
         "tag": "NEW"
       }
     }
     ```
   - Assign provinces under `ownership`:
     ```json
     "ownership": {
       "12345": "NEW",
       "12346": "NEW"
     }
     ```

---

## 6. Maintenance & Utility Scripts

The project includes several scratch utilities to verify code health and bake changes:

- **Syntax Checker**:
  ```bash
  python scratch/check_syntax.py
  ```
  Verifies that all JavaScript/HTML braces and template strings in `index.html` match perfectly.

- **Preset Baking Utility**:
  ```bash
  python scratch/bake_and_reset.py
  ```
  Extracts country configurations and bakes default presets into `index.html`.

- **Server Launcher / Stopper**:
  - Double-click [`start_server.bat`](file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/start_server.bat) to start the local HTTP server.
  - Double-click [`stop_server.bat`](file:///c:/Users/Faaz/Documents/GitHub/Mappa%20Mundi%20sine%20Tempore/stop_server.bat) to terminate background server processes.

---
*Created for Mappa Mundi sine Tempore - Developers: Faaz Noushad & Pioneerwada.*
