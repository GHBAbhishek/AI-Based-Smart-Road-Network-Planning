# AI-Based Smart Road Network Planning Using Satellite Imagery

A Python-based Geographic Information System (GIS) application that leverages Artificial Intelligence to recommend optimal road routes using satellite imagery, terrain elevation, population density, and OpenStreetMap road network data.

This project demonstrates how AI and geospatial analytics can assist in planning efficient road networks by considering geographical constraints and population distribution.

---

## Project Highlights

- AI-assisted road route planning
- Real-world OpenStreetMap integration
- Terrain analysis using Cartosat DEM
- Population density analysis using WorldPop
- Interactive graphical interface using Tkinter
- Route visualization and comparison
- GIS-based spatial analysis

---

## Repository Structure

```
AI-Based-Smart-Road-Network-Planning
│
├── Delhi_DEM.zip
├── ind_pd_2020_1km.tif
├── Project_RealWorldMap_RealData_Test.py
├── requirements.txt
└── README.md
```

---

# Technologies Used

### Programming Language

- Python

### Libraries

- OSMnx
- GeoPandas
- NetworkX
- Rasterio
- NumPy
- Matplotlib
- Pillow
- Geopy
- Pandas
- Tkinter

### GIS Datasets

- Cartosat DEM
- WorldPop Population Density
- OpenStreetMap

---

# Installation

Clone the repository

```bash
git clone https://github.com/GHBAbhishek/AI-Based-Smart-Road-Network-Planning.git
```

Move into the project directory

```bash
cd AI-Based-Smart-Road-Network-Planning
```

Install the required packages

```bash
pip install -r requirements.txt
```

---

# Before Running the Project

## Step 1 — Extract the DEM File

The terrain dataset has been compressed to reduce repository size.

Extract

```
Delhi_DEM.zip
```

After extraction, you should obtain

```
delhi_cartosat_dem_merged.tif
```

Place the extracted file in the project root directory alongside the Python file.

Your directory should now look like:

```
AI-Based-Smart-Road-Network-Planning
│
├── delhi_cartosat_dem_merged.tif
├── ind_pd_2020_1km.tif
├── Project_RealWorldMap_RealData_Test.py
├── requirements.txt
└── README.md
```

> **Important:** Do not rename the extracted DEM file unless you also update its filename in the Python source code.

---

# Running the Project

Run the application using:

```bash
python Project_RealWorldMap_RealData_Test.py
```

---

# Project Workflow

1. Extract the Cartosat DEM dataset.
2. Launch the application.
3. Load the Delhi road network from OpenStreetMap.
4. Select the source and destination.
5. The application analyzes:
   - Terrain Elevation
   - Population Density
   - Existing Road Network
6. AI-based pathfinding computes the optimal route.
7. The generated route is displayed on the interactive map.

---

# Datasets Used

## 1. Cartosat DEM

Purpose:

- Terrain elevation analysis
- Slope estimation
- Road feasibility assessment

---

## 2. WorldPop Population Dataset

Purpose:

- Population density analysis
- Demand estimation
- Route prioritization

---

## 3. OpenStreetMap

Purpose:

- Real-world road network
- Geographic visualization
- Route generation

---

# Applications

- Smart City Planning
- Transportation Engineering
- Highway Planning
- Disaster Management
- Urban Infrastructure Development
- GIS Research
- AI-Based Navigation Systems

---

# Future Improvements

- Live Traffic Integration
- Weather-aware Route Planning
- Multi-city Support
- Satellite Image-based Road Detection
- Deep Learning-based Terrain Classification
- Reinforcement Learning for Adaptive Routing
- Flask Web Deployment

---

---

# Author

**Abhishek Sharma**

B.Tech Computer Science & Engineering


---

# License

This project is developed for academic, educational, and research purposes only.

---

## Citation

If you use this project in your research or academic work, please provide appropriate attribution.

```
@software{GeoRouteAI,
  author = {Abhishek Sharma},
  title = {AI-Based Smart Road Network Planning Using Satellite Imagery},
  year = {2026}
}
```

---

## Contact

For suggestions or collaboration, feel free to connect through GitHub.
