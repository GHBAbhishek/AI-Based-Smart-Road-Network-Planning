# AI-Based-Smart-Road-Network-Planning
An AI-driven GIS application for optimal road network planning using Python, OpenStreetMap, Cartosat DEM and WorldPop datasets.

## Overview

This project presents an AI-assisted approach to smart road network planning using satellite imagery, terrain elevation, population density, and real-world road network data. The application analyzes geographical constraints and recommends an optimal route between selected locations.

The project integrates Geographic Information Systems (GIS) with Artificial Intelligence techniques to support efficient transportation planning and infrastructure development.

---

## Features

- Interactive GUI developed using Tkinter
- Real-world road network using OpenStreetMap (OSM)
- Terrain analysis using Cartosat DEM
- Population density analysis using WorldPop data
- AI-assisted optimal route planning
- Route visualization on map
- Real-time source and destination selection

---

## Tech Stack

**Programming Language**
- Python

**Libraries Used**
- OSMnx
- GeoPandas
- NetworkX
- Rasterio
- NumPy
- Matplotlib
- Tkinter
- Pillow
- Geopy

**Datasets**
- Cartosat DEM
- WorldPop Population Density
- OpenStreetMap

---

## Repository Structure

```
AI-Based-Smart-Road-Network-Planning/
│
├── Delhi_DEM.zip
├── ind_pd_2020_1km.tif
├── Project_RealWorldMap_RealData_Test.py
└── README.md
```

---

# Important

## Step 1: Extract the DEM File

Before running the project, **extract `Delhi_DEM.zip`** in the project directory.

After extraction, the folder should contain the DEM file required by the application.

Example:

```
Delhi_DEM.zip
        ↓ Extract

delhi_cartosat_dem_merged.tif
```

Do **not** rename the extracted file unless you also update its filename in the Python source code.

---

## Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-Based-Smart-Road-Network-Planning.git
```

Move to the project folder

```bash
cd AI-Based-Smart-Road-Network-Planning
```

Install the required libraries

```bash
pip install osmnx geopandas rasterio networkx matplotlib pillow geopy numpy
```

---

## Required Files

Ensure the following files are present before execution:

```
Project_RealWorldMap_RealData_Test.py
delhi_cartosat_dem_merged.tif      (Extract from Delhi_DEM.zip)
ind_pd_2020_1km.tif
```

---

## Running the Project

Execute the Python file:

```bash
python Project_RealWorldMap_RealData_Test.py
```

---

## Workflow

1. Extract the DEM dataset.
2. Launch the application.
3. Load the Delhi road network.
4. Select source and destination.
5. The application analyzes:
   - Terrain elevation
   - Population density
   - Existing road network
6. The optimal route is generated and displayed.

---

## Applications

- Smart City Planning
- Road Infrastructure Development
- Transportation Planning
- Disaster Management
- GIS-Based Decision Support
- AI-Assisted Route Optimization

---

## Future Scope

- Deep Learning-based road extraction
- Live traffic integration
- Weather-aware routing
- Multi-city support
- Reinforcement Learning-based adaptive routing
- Web deployment using Flask

---

## Author

**Abhishek Sharma**

B.Tech Computer Science & Engineering

---

## License

This project is intended for educational and research purposes only.
