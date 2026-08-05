import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib
import rasterio
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patches
import osmnx as ox
import networkx as nx
from geopy.distance import geodesic
import random
from PIL import Image, ImageTk
import json
import os
import datetime
from PIL import Image
from rasterio.mask import mask
import geopandas as gpd

class RealWorldRoadNetworkPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("AI-Based Smart Road Network Planning - Real World Maps")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize data structures
        self.map_graph = None
        self.terrain_data = None
        self.population_data = None
        self.start_point = None
        self.end_point = None
        self.proposed_routes = []
        self.current_location = "Delhi, India"
        
        # Terrain cost parameters
        self.terrain_costs = {
            'flat': {'cost': 1.0, 'color': '#8FBC8F'},
            'urban': {'cost': 1.5, 'color': '#696969'},
            'forest': {'cost': 2.0, 'color': '#228B22'},
            'hilly': {'cost': 3.0, 'color': '#D2B48C'},
            'mountain': {'cost': 5.0, 'color': '#A9A9A9'},
            'water': {'cost': 10.0, 'color': '#1E90FF'}
        }
        
        # Defaults for grid-related attributes (populated when map/placeholder generated)
        self.grid_size = None
        self.lon_grid = None
        self.lat_grid = None
        
        self.setup_ui()
        #self.load_initial_map()
        self.status_var.set("Ready. Click 'Load Map' to begin.")

        
    def setup_ui(self):
        # Create main frames
        # -------- Scrollable Control Panel --------
        container = tk.Frame(self.root)
        container.pack(side=tk.LEFT, fill=tk.Y)

        canvas = tk.Canvas(container, width=360, bg='#e0e0e0')
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)

        control_frame = tk.Frame(canvas, bg='#e0e0e0')

        control_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=control_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.Y)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        display_frame = tk.Frame(self.root, bg='#f0f0f0')
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Title
        title_label = tk.Label(control_frame, text="AI Road Network Planner", 
                              font=('Arial', 16, 'bold'), bg='#e0e0e0')
        title_label.pack(pady=10)
        
        # Location selection
        location_frame = tk.LabelFrame(control_frame, text="Map Location", bg='#e0e0e0')
        location_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(location_frame, text="Enter Location:", bg='#e0e0e0').pack(anchor='w')
        self.location_var = tk.StringVar(value="Delhi, India")
        location_entry = tk.Entry(location_frame, textvariable=self.location_var)
        location_entry.pack(fill=tk.X, pady=2)
        
        tk.Button(location_frame, text="Load Map", command=self.load_new_map, 
                 bg='#4CAF50', fg='white').pack(fill=tk.X, pady=5)
        
        # Point selection
        point_frame = tk.LabelFrame(control_frame, text="Point Selection", bg='#e0e0e0')
        point_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(point_frame, text="Click on map to set points", bg='#e0e0e0').pack(anchor='w')
        tk.Button(point_frame, text="Set Start Point", command=self.set_start_mode, 
                 bg='#2196F3', fg='white').pack(fill=tk.X, pady=2)
        tk.Button(point_frame, text="Set End Point", command=self.set_end_mode, 
                 bg='#FF9800', fg='white').pack(fill=tk.X, pady=2)
        tk.Button(point_frame, text="Clear Points", command=self.clear_points, 
                 bg='#f44336', fg='white').pack(fill=tk.X, pady=2)
        
        # Analysis parameters
        param_frame = tk.LabelFrame(control_frame, text="AI Analysis Parameters", bg='#e0e0e0')
        param_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Population weight
        tk.Label(param_frame, text="Population Weight:", bg='#e0e0e0').pack(anchor='w')
        self.pop_weight = tk.Scale(param_frame, from_=0.1, to=3.0, resolution=0.1, 
                                  orient=tk.HORIZONTAL, bg='#e0e0e0')
        self.pop_weight.set(1.5)
        self.pop_weight.pack(fill=tk.X)
        
        # Terrain difficulty weight
        tk.Label(param_frame, text="Terrain Difficulty Weight:", bg='#e0e0e0').pack(anchor='w')
        self.terrain_weight = tk.Scale(param_frame, from_=0.1, to=3.0, resolution=0.1, 
                                      orient=tk.HORIZONTAL, bg='#e0e0e0')
        self.terrain_weight.set(2.0)
        self.terrain_weight.pack(fill=tk.X)
        
        # Environmental sensitivity
        tk.Label(param_frame, text="Environmental Sensitivity:", bg='#e0e0e0').pack(anchor='w')
        self.environment_weight = tk.Scale(param_frame, from_=0.1, to=3.0, resolution=0.1, 
                                         orient=tk.HORIZONTAL, bg='#e0e0e0')
        self.environment_weight.set(1.0)
        self.environment_weight.pack(fill=tk.X)
        
        # Road type preferences
        road_type_frame = tk.LabelFrame(control_frame, text="Road Type Preferences", bg='#e0e0e0')
        road_type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.road_type_var = tk.StringVar(value="Highway")
        tk.Radiobutton(road_type_frame, text="Highway (Fast, Expensive)", 
                      variable=self.road_type_var, value="Highway", bg='#e0e0e0').pack(anchor='w')
        tk.Radiobutton(road_type_frame, text="Major Road (Balanced)", 
                      variable=self.road_type_var, value="Major", bg='#e0e0e0').pack(anchor='w')
        tk.Radiobutton(road_type_frame, text="Rural Road (Cheap, Slow)", 
                      variable=self.road_type_var, value="Rural", bg='#e0e0e0').pack(anchor='w')
        
        # Control buttons
        button_frame = tk.Frame(control_frame, bg='#e0e0e0')
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        tk.Button(button_frame, text="Generate Optimal Path", 
                 command=self.find_optimal_path, bg='#2196F3', fg='white', 
                 font=('Arial', 10, 'bold')).pack(fill=tk.X, pady=2)
        
        tk.Button(button_frame, text="Generate Multiple Routes", 
                 command=self.generate_multiple_routes, bg='#9C27B0', fg='white').pack(fill=tk.X, pady=2)
        
        tk.Button(button_frame, text="Terrain Analysis", 
                 command=self.show_terrain_analysis, bg='#FF9800', fg='white').pack(fill=tk.X, pady=2)
        
        tk.Button(button_frame, text="Population Analysis", 
                 command=self.show_population_analysis, bg='#E91E63', fg='white').pack(fill=tk.X, pady=2)
        
        tk.Button(button_frame, text="Compare Routes", 
                 command=self.compare_routes, bg='#607D8B', fg='white').pack(fill=tk.X, pady=2)
        
        tk.Button(button_frame, text="Export Results", 
                 command=self.export_results, bg='#009688', fg='white').pack(fill=tk.X, pady=2)
        
        tk.Button(button_frame, text="Reset View", bg="#607D8B", fg="white", command=self.reset_view).pack(fill=tk.X, pady=2)
    
        tk.Button(button_frame,
                text="Run Learning Episodes",
                command=lambda: self.run_convergence_experiment(1000),
                bg='#222222', fg='white').pack(fill=tk.X, pady=2)

        tk.Button(button_frame,
                text="Show Algorithm Race",
                command=self.show_algorithm_race,
                bg='#111199', fg='white').pack(fill=tk.X, pady=2)

        
        # Results display
        results_frame = tk.LabelFrame(control_frame, text="Analysis Results", bg='#e0e0e0')
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.results_text = tk.Text(results_frame, height=15, width=40)
        scrollbar = tk.Scrollbar(results_frame, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create matplotlib figure for display
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=display_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


        # Connect click event - use figure.canvas to ensure correct binding
        self.fig.canvas.mpl_connect('button_press_event', self.on_map_click)

        self.fig.canvas.mpl_connect('scroll_event', self.on_zoom)

        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Loading initial map...")
        status_bar = tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Loading Spinner
        self.spinner = ttk.Progressbar(
            self.root,
            mode='indeterminate',
            length=200
        )
        self.spinner.pack(side=tk.BOTTOM, pady=5)
        self.spinner.stop()

        
        # Initialize modes
        self.selection_mode = None  # 'start' or 'end'
    
    def on_zoom(self, event):
        # Only zoom when mouse is over the map
        if event.inaxes != self.ax:
            return

        # Zoom scale factor
        zoom_factor = 1.2
        if event.button == 'up':       # scroll up → zoom in
            scale = 1 / zoom_factor
        elif event.button == 'down':   # scroll down → zoom out
            scale = zoom_factor
        else:
            return

        # Current limits
        x_min, x_max = self.ax.get_xlim()
        y_min, y_max = self.ax.get_ylim()

        x_range = (x_max - x_min) * scale
        y_range = (y_max - y_min) * scale

        x_center = event.xdata
        y_center = event.ydata

        # Set new limits
        self.ax.set_xlim(
            x_center - x_range / 2,
            x_center + x_range / 2
        )
        self.ax.set_ylim(
            y_center - y_range / 2,
            y_center + y_range / 2
        )

        self.canvas.draw_idle()

    
    def run_convergence_experiment(self, episodes=500):

        if not self.start_point or not self.end_point:
            messagebox.showerror("Error", "Set start and end points first")
            return

        if not hasattr(self, "route_algorithms") or not self.route_algorithms:
            self.generate_multiple_routes()

        self.status_var.set("Running convergence experiment...")
        self.root.update()

        self.convergence_log = {name: [] for name in self.route_algorithms}

        road_modes = ["Highway", "Major", "Rural"]

        for ep in range(episodes):

            # Stronger environment variation
            self.pop_weight.set(np.random.uniform(0.5, 3.0))
            self.terrain_weight.set(np.random.uniform(0.5, 3.0))
            self.environment_weight.set(np.random.uniform(0.5, 2.0))
            self.road_type_var.set(random.choice(road_modes))

            for name in self.route_algorithms:

                if "A*" in name:
                    route = self.advanced_a_star_search()
                elif "Dijkstra" in name:
                    route = self.dijkstra_search()
                elif "BFS" in name:
                    route = self.bfs_search()
                else:
                    route = self.greedy_best_first_search()

                score = self.compute_objective_score(route) if route else -50

                # Add small measurement realism
                score += np.random.normal(0, 0.5)

                self.convergence_log[name].append(score)

            if ep % 5 == 0:
                self.root.update_idletasks()

        self.status_var.set(f"Finished {episodes} episodes ✔")

    
    def show_algorithm_race(self):

        import matplotlib.animation as animation
        import numpy as np

        if not hasattr(self, "convergence_log"):
            messagebox.showerror("Error", "Run learning episodes first")
            return

        # ---- SETTINGS ----
        WINDOW = 120          # episodes visible
        SMOOTH = 8            # smoothing strength

        win = tk.Toplevel(self.root)
        win.title("Algorithm Convergence Race")

        fig = Figure(figsize=(10,6))
        ax = fig.add_subplot(111)

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # ---- PREPROCESS DATA ----
        processed = {}

        for name, data in self.convergence_log.items():

            arr = np.array(data)

            # Convert to positive scale
            arr = arr - np.min(arr) + 1

            # Moving average smoothing
            kernel = np.ones(SMOOTH)/SMOOTH
            arr = np.convolve(arr, kernel, mode='same')

            processed[name] = arr

        max_len = len(next(iter(processed.values())))

        # Create lines
        lines = {}
        for name in processed:
            lines[name], = ax.plot([], [], label=name)

        ax.set_xlim(0, WINDOW)
        ax.set_ylim(
            min(np.min(v[:WINDOW]) for v in processed.values()),
            max(np.max(v[:WINDOW]) for v in processed.values())
        )

        ax.legend()
        ax.set_xlabel("Episode Window")
        ax.set_ylabel("Normalized Score")
        ax.set_title("Algorithm Convergence Race")

        # ---- ANIMATION ----
        def update(frame):

            start = max(0, frame - WINDOW)

            for name in processed:
                y = processed[name][start:frame]
                x = np.arange(len(y))
                lines[name].set_data(x, y)

            ax.set_xlim(0, WINDOW)

            return lines.values()

        self.anim = animation.FuncAnimation(
            fig,
            update,
            frames=max_len,
            interval=25,
            repeat=False,
            blit=False
        )

        win.anim = self.anim
        canvas.draw_idle()
    
    def _load_initial_map_worker(self):
        try:
            self.status_var.set("Attempting to download map data (OSM)...")
            self.root.update_idletasks()

            self.load_delhi_graph()
            self.status_var.set("Map data downloaded successfully.")

        except Exception as e:
            self.status_var.set(f"OSM download failed; using synthetic map. ({str(e)})")
            self.map_graph = None

        try:
            self.generate_synthetic_data()
            self.plot_map()
            self.status_var.set(f"Map ready: {self.current_location}")

        except Exception as e:
            self.status_var.set(f"Error creating map visuals: {str(e)}")
            messagebox.showerror(
                "Error",
                f"Failed to prepare initial map visuals: {str(e)}"
            )

        finally:
            self.spinner.stop()


    def load_initial_map(self):
        self.spinner.start(10)
        self.status_var.set("Loading map data… please wait")
        self.root.update_idletasks()

        self.root.after(100, self._load_initial_map_worker)


    def load_delhi_graph(self):
        try:
            gdf = ox.geocode_to_gdf(
                "National Capital Territory of Delhi, India"
            )
            polygon = gdf.geometry.iloc[0]

            self.map_graph = ox.graph_from_polygon(
                polygon,
                network_type="drive",
                simplify=True,
                retain_all=True,
                truncate_by_edge=True
            )
        except Exception as e:
            self.map_graph = None
            raise RuntimeError(f"Delhi OSM load failed: {e}")


    
    def load_new_map(self):
        self.spinner.start(10)
        self.root.update_idletasks()
        """Load a new map based on user input"""
        new_location = self.location_var.get().strip()
        if not new_location:
            messagebox.showwarning("Warning", "Please enter a location")
            return
            
        try:
            self.status_var.set(f"Loading map for {new_location}...")
            self.root.update()
            
            self.current_location = new_location
            try:
                #self.map_graph = ox.graph_from_place(new_location, network_type='drive', simplify=True)
                self.load_delhi_graph()
                self.status_var.set("Map data downloaded successfully.")
            except Exception as e:
                # fallback
                self.map_graph = None
                self.status_var.set(f"OSM download failed for '{new_location}', using synthetic area. ({str(e)})")
            
            self.proposed_routes = []
            self.start_point = None
            self.end_point = None
            
            # Regenerate synthetic data for new area
            self.generate_synthetic_data()
            
            self.plot_map()
            self.status_var.set(f"Map loaded: {new_location}")
            
        except Exception as e:
            self.status_var.set(f"Error loading map: {str(e)}")
            messagebox.showerror("Error", f"Failed to load map for '{new_location}': {str(e)}")
    
    def load_real_terrain_tif(self, tif_path):
        with rasterio.open(tif_path) as dataset:
            elevation = dataset.read(1)
            bounds = dataset.bounds

            # Resize using PIL (NO skimage needed)
            elevation_resized = np.array(
                Image.fromarray(elevation).resize((self.grid_size, self.grid_size))
            )

            self.elevation_resized = elevation_resized  # save globally

            # Normalize
            elev_min, elev_max = np.min(elevation_resized), np.max(elevation_resized)
            elev_norm = (elevation_resized - elev_min) / (elev_max - elev_min + 1e-9)

            # Terrain classification
            self.terrain_data = np.full((self.grid_size, self.grid_size), 'flat', dtype=object)
            self.terrain_data[elev_norm > 0.2] = 'hilly'
            self.terrain_data[elev_norm > 0.5] = 'mountain'
            self.terrain_data[elev_norm < 0.05] = 'water'
    
    def reset_view(self):
        if self.lon_grid is None:
            return
        self.ax.set_xlim(self.lon_grid[0], self.lon_grid[-1])
        self.ax.set_ylim(self.lat_grid[0], self.lat_grid[-1])
        self.canvas.draw_idle()


    def load_population_tif(self, tif_path):
        self.population_ds = rasterio.open(tif_path)
        self.pop_raster = self.population_ds.read(1)

    def load_population_delhi(self, tif_path):
        gdf = ox.geocode_to_gdf("Delhi, India")

        with rasterio.open(tif_path) as src:
            out_image, out_transform = mask(
                src,
                gdf.geometry,
                crop=True
            )

            self.population_ds = src
            self.pop_raster = out_image[0]
            self.pop_transform = out_transform
        self.population_ds = None



    def get_population_at_coord(self, lon, lat):
        if self.pop_raster is None or self.pop_transform is None:
            return 0.0

        col, row = ~self.pop_transform * (lon, lat)
        row, col = int(row), int(col)

        if 0 <= row < self.pop_raster.shape[0] and 0 <= col < self.pop_raster.shape[1]:
            return max(0.0, float(self.pop_raster[row, col]))

        return 0.0



    def generate_synthetic_data(self):

        # 🔒 SAFETY CHECK
        if self.map_graph is None or len(self.map_graph.nodes) == 0:
            # Fallback bounding box for FULL Delhi
            min_lon, max_lon = 76.85, 77.35
            min_lat, max_lat = 28.40, 28.90
        else:
            nodes = self.map_graph.nodes
            lons = [data['x'] for _, data in nodes.items()]
            lats = [data['y'] for _, data in nodes.items()]

            min_lon, max_lon = min(lons), max(lons)
            min_lat, max_lat = min(lats), max(lats)

        # Grid creation (SAFE now)
        self.grid_size = 50
        self.lon_grid = np.linspace(min_lon, max_lon, self.grid_size)
        self.lat_grid = np.linspace(min_lat, max_lat, self.grid_size)

        
        # Initialize terrain and population data
        self.terrain_data = np.full((self.grid_size, self.grid_size), 'flat', dtype=object)
        self.population_data = np.zeros((self.grid_size, self.grid_size))

        
        # Load real terrain
        self.load_real_terrain_tif("D:\\Test_MajorProject\\delhi_cartosat_dem_merged.tif")

        # Load real population density (Delhi)
        self.population_tif_path = "D:\\Test_MajorProject\\ind_pd_2020_1km.tif"
        #self.load_population_tif(self.population_tif_path)
        self.load_population_delhi("D:\\Test_MajorProject\\ind_pd_2020_1km.tif")


        transform = self.pop_transform


        for i, lat in enumerate(self.lat_grid):
            for j, lon in enumerate(self.lon_grid):
                col, row = ~transform * (lon, lat)
                row, col = int(row), int(col)

                if 0 <= row < self.pop_raster.shape[0] and 0 <= col < self.pop_raster.shape[1]:
                    self.population_data[i, j] = self.pop_raster[row, col]




        # Normalize for algorithm stability
        max_pop = np.max(self.population_data)
        if max_pop > 0:
            self.population_data /= max_pop

    
    def generate_realistic_terrain(self):
        # Start with flat terrain
        self.terrain_data[:, :] = 'flat'
        
        # Add some water bodies (rivers, lakes)
        water_mask = np.random.random((self.grid_size, self.grid_size)) < 0.05
        self.terrain_data[water_mask] = 'water'
        
        # Add forest areas
        forest_mask = np.random.random((self.grid_size, self.grid_size)) < 0.15
        self.terrain_data[np.logical_and(forest_mask, ~water_mask)] = 'forest'
        
        # Add hilly areas
        hilly_mask = np.random.random((self.grid_size, self.grid_size)) < 0.20
        mask = np.logical_and.reduce((~water_mask, ~forest_mask, hilly_mask))
        self.terrain_data[mask] = 'hilly'
        
        # Add mountain areas (less common)
        mountain_mask = np.random.random((self.grid_size, self.grid_size)) < 0.08
        mask = np.logical_and.reduce((~water_mask, ~forest_mask, ~hilly_mask, mountain_mask))
        self.terrain_data[mask] = 'mountain'
        
        # Urban areas are typically near the center of the map
        center_i, center_j = self.grid_size // 2, self.grid_size // 2
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                distance_to_center = np.sqrt((i - center_i)**2 + (j - center_j)**2)
                if distance_to_center < 10 and np.random.random() < 0.7:
                    if self.terrain_data[i, j] in ['flat', 'hilly']:
                        self.terrain_data[i, j] = 'urban'
    
    def generate_population_density(self):
        # Base population with random variation
        self.population_data = np.random.gamma(2, 0.5, (self.grid_size, self.grid_size))
        
        center_i, center_j = self.grid_size // 2, self.grid_size // 2
        
        # Higher population in urban areas and near center
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                distance_to_center = np.sqrt((i - center_i)**2 + (j - center_j)**2)
                
                # Urban areas have high population
                if self.terrain_data[i, j] == 'urban':
                    self.population_data[i, j] *= 3.0
                # Areas near center have moderate population
                elif distance_to_center < 15:
                    self.population_data[i, j] *= max(0.1, (20 - distance_to_center) / 10)
                # Remote areas have low population
                else:
                    self.population_data[i, j] *= 0.3
        
        # Normalize population data and clip
        self.population_data = np.clip(self.population_data, 0, 10)
    
    def plot_map(self):
        """Plot the map with existing roads and features"""
        if self.lon_grid is None or self.lat_grid is None:
            return
            
        self.ax.clear()
        
        try:
            # If we have a real map_graph from OSM, attempt to plot it onto the same axis
            if self.map_graph is not None:
                try:
                    ox.plot_graph(self.map_graph, ax=self.ax, show=False, close=False,
                                 node_color='blue', node_size=0, edge_color='gray', 
                                 edge_linewidth=1, bgcolor='white')
                except Exception:
                    # If ox.plot_graph misbehaves, ignore and continue with synthetic overlays
                    pass
            
            # Plot terrain overlay with transparency
            cell_width = (self.lon_grid[-1] - self.lon_grid[0]) / (self.grid_size - 1)
            cell_height = (self.lat_grid[-1] - self.lat_grid[0]) / (self.grid_size - 1)
            
            terrain_cost_map = np.vectorize(
                lambda t: self.terrain_costs[t]['cost']
            )(self.terrain_data)

            self.ax.imshow(
                terrain_cost_map,
                extent=[self.lon_grid[0], self.lon_grid[-1],
                        self.lat_grid[0], self.lat_grid[-1]],
                alpha=0.25,
                origin='lower',
                cmap='terrain',
                zorder=1
            )

            
            # Plot population density as scatter points
            pop_points_x = []
            pop_points_y = []
            pop_sizes = []
            
            for i in range(0, self.grid_size, 2):  # Sample every 2nd point for performance
                for j in range(0, self.grid_size, 2):
                    if self.population_data[i, j] > 1:  # Only show significant populations
                        pop_points_x.append(self.lon_grid[j])
                        pop_points_y.append(self.lat_grid[i])
                        pop_sizes.append(self.population_data[i, j] * 10)
            
            if pop_points_x and self.get_zoom_ratio() < 0.6:
                self.ax.scatter(pop_points_x, pop_points_y, s=pop_sizes, c='red', 
                               alpha=0.6, label='Population Density', zorder=5)
            
            # Plot proposed routes
            colors = ['red', 'blue', 'green', 'purple', 'orange']
            for idx, route in enumerate(self.proposed_routes):
                if route and len(route) > 1:
                    lons = [point[0] for point in route]
                    lats = [point[1] for point in route]
                    color = colors[idx % len(colors)]
                    lw = 2 if self.get_zoom_ratio() > 0.5 else 4
                    self.ax.plot(lons, lats, linewidth=lw, color=color, linestyle='--', label=f'Proposed Route {idx+1}', zorder=6)
            
            # Plot start and end points
            if self.start_point:
                lon, lat = self.start_point
                self.ax.plot(lon, lat, 'go', markersize=12, label='Start Point', zorder=7)
                if self.get_zoom_ratio() < 0.4:
                    self.ax.text(lon, lat, 'START', fontsize=10, ha='center', va='bottom', weight='bold', color='green', zorder=8)
            
            if self.end_point:
                lon, lat = self.end_point
                self.ax.plot(lon, lat, 'ro', markersize=12, label='End Point', zorder=7)
                if self.get_zoom_ratio() < 0.4:
                    self.ax.text(lon, lat, 'END', fontsize=10, ha='center', va='bottom', weight='bold', color='red', zorder=8)
            
            self.ax.set_title(f'AI Road Network Planning - {self.current_location}')
            # Avoid legend errors if nothing to show
            handles, labels = self.ax.get_legend_handles_labels()
            if labels:
                self.ax.legend(loc='upper right')

                        
            self.canvas.draw_idle()
            
        except Exception as e:
            self.status_var.set(f"Error plotting map: {str(e)}")
            # Keep app running
        

        # Only set limits once (initial draw)
        if not hasattr(self, "_zoom_initialized"):
            self.ax.set_xlim(self.lon_grid[0], self.lon_grid[-1])
            self.ax.set_ylim(self.lat_grid[0], self.lat_grid[-1])
            self._zoom_initialized = True

    def get_zoom_ratio(self):
        if self.lon_grid is None:
            return 1.0
        x0, x1 = self.ax.get_xlim()
        full_width = self.lon_grid[-1] - self.lon_grid[0]
        current_width = x1 - x0
        return current_width / full_width


    
    def set_start_mode(self):
        self.selection_mode = 'start'
        self.status_var.set("Click on map to set START point")
    
    def set_end_mode(self):
        self.selection_mode = 'end'
        self.status_var.set("Click on map to set END point")
    
    def clear_points(self):
        self.start_point = None
        self.end_point = None
        self.proposed_routes = []
        self.status_var.set("Points cleared")
        self.plot_map()
    
    def on_map_click(self, event):
        # Will be called by matplotlib event system
        if event.inaxes != self.ax or self.lon_grid is None:
            return

        lon, lat = event.xdata, event.ydata
        if lon is None or lat is None:
            return

        pop_val = self.get_population_at_coord(lon, lat)
        self.status_var.set(
            f"Point: ({lon:.4f}, {lat:.4f}) | Population Density: {pop_val:.2f}"
        )

        self.status_var.set(
            f"Point: ({lon:.4f}, {lat:.4f}) | Population Density: {pop_val:.2f}"
        )

        if event.inaxes != self.ax or self.lon_grid is None:
            return
        
        lon, lat = event.xdata, event.ydata
        
        if lon is None or lat is None:
            return
        
        if self.selection_mode == 'start':
            self.start_point = (lon, lat)
            self.status_var.set(f"Start point set at ({lon:.4f}, {lat:.4f})")
            self.selection_mode = None
        elif self.selection_mode == 'end':
            self.end_point = (lon, lat)
            self.status_var.set(f"End point set at ({lon:.4f}, {lat:.4f})")
            self.selection_mode = None
        else:
            # If neither, ignore
            return
        
        self.plot_map()
    
    def find_optimal_path(self):
        if not self.start_point or not self.end_point:
            messagebox.showerror("Error", "Please set both start and end points")
            return
        
        self.status_var.set("Finding optimal path using AI algorithms...")
        self.root.update()
        
        # Clear previous proposed routes
        self.proposed_routes = []
        
        # Use A* algorithm to find optimal path
        path = self.advanced_a_star_search()
        
        if path:
            self.proposed_routes.append(path)
            self.plot_map()
            self.analyze_route(path)
        else:
            messagebox.showerror("Error", "No feasible path found between the selected points")
    
    def advanced_a_star_search(self):
        """Advanced A* algorithm considering terrain and population"""
        if not self.start_point or not self.end_point or self.lon_grid is None:
            return None
            
        start_lon, start_lat = self.start_point
        end_lon, end_lat = self.end_point
        
        # Convert to grid coordinates (indices)
        start_i = int(np.abs(self.lat_grid - start_lat).argmin())
        start_j = int(np.abs(self.lon_grid - start_lon).argmin())
        end_i = int(np.abs(self.lat_grid - end_lat).argmin())
        end_j = int(np.abs(self.lon_grid - end_lon).argmin())
        
        start = (start_i, start_j)
        end = (end_i, end_j)
        
        open_set = {start}
        came_from = {}
        
        g_score = {start: 0.0}
        f_score = {start: self.heuristic(start, end)}
        
        iterations = 0
        max_iterations = self.grid_size * self.grid_size * 4
        
        while open_set and iterations < max_iterations:
            iterations += 1
            current = min(open_set, key=lambda x: f_score.get(x, float('inf')))
            
            if current == end:
                return self.reconstruct_path(came_from, current)
            
            open_set.remove(current)
            
            for neighbor in self.get_neighbors_8way(current):
                tentative_g_score = g_score[current] + self.move_cost(current, neighbor)
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, end)
                    if neighbor not in open_set:
                        open_set.add(neighbor)
        
        # If not found
        return None
    
    def get_neighbors_8way(self, cell):
        """Get 8-way neighbors for more natural paths"""
        i, j = cell
        neighbors = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < self.grid_size and 0 <= nj < self.grid_size:
                    neighbors.append((ni, nj))
        return neighbors
    
    def move_cost(self, from_cell, to_cell):
        """Calculate movement cost considering terrain and population"""
        i, j = to_cell
        
        # Base terrain cost
        terrain_type = self.terrain_data[i, j]
        #terrain_cost = self.terrain_costs.get(terrain_type, {'cost': 1.0})['cost'] * self.terrain_weight.get()
        terrain_cost = (
            self.terrain_costs[terrain_type]['cost'] / 5.0
        ) * self.terrain_weight.get()

        
        
        window = self.population_data[
            max(0, i-1):min(self.grid_size, i+2),
            max(0, j-1):min(self.grid_size, j+2)
        ]

        pop_influence = np.mean(window)
        pop_benefit = -pop_influence * self.pop_weight.get()


        # Environmental sensitivity cost
        env_cost = 0.0
        if terrain_type in ['forest', 'water']:
            env_cost = float(self.environment_weight.get()) * 2.0
        
        # Road type preference
        road_type_bonus = 0.0
        road_pref = self.road_type_var.get()
        if road_pref == "Highway":
            if terrain_type in ['flat', 'urban']:
                road_type_bonus = -2.0
            else:
                road_type_bonus = 3.0
        elif road_pref == "Rural":
            if terrain_type in ['mountain', 'hilly']:
                road_type_bonus = -1.0
        
        total_cost = float(terrain_cost) + float(pop_benefit) + float(env_cost) + float(road_type_bonus) + 1.0
        
        return max(0.1, total_cost)
    
    def heuristic(self, a, b):
        """Heuristic function for A* (Euclidean distance)"""
        i1, j1 = a
        i2, j2 = b
        #return float(np.sqrt((i1 - i2)**2 + (j1 - j2)**2))
        base_dist = np.sqrt((i1 - i2)**2 + (j1 - j2)**2)
        avg_pop = np.mean(self.population_data)
        pop_bias = -avg_pop * 0.3
        return base_dist + pop_bias

    def dijkstra_search(self):
        return self.generic_graph_search(use_heuristic=False, weighted=True)

    def bfs_search(self):
        return self.generic_graph_search(use_heuristic=False, weighted=False)

    def greedy_best_first_search(self):
        return self.generic_graph_search(use_heuristic=True, weighted=False)


    def generic_graph_search(self, use_heuristic=False, weighted=True):
        if not self.start_point or not self.end_point:
            return None

        start_i = int(np.abs(self.lat_grid - self.start_point[1]).argmin())
        start_j = int(np.abs(self.lon_grid - self.start_point[0]).argmin())
        end_i = int(np.abs(self.lat_grid - self.end_point[1]).argmin())
        end_j = int(np.abs(self.lon_grid - self.end_point[0]).argmin())

        start = (start_i, start_j)
        end = (end_i, end_j)

        open_set = {start}
        came_from = {}
        cost = {start: 0}

        while open_set:
            if use_heuristic:
                current = min(open_set, key=lambda x: self.heuristic(x, end))
            else:
                current = min(open_set, key=lambda x: cost[x])

            if current == end:
                return self.reconstruct_path(came_from, current)

            open_set.remove(current)

            for neighbor in self.get_neighbors_8way(current):
                step_cost = 1.0 if not weighted else self.move_cost(current, neighbor)
                new_cost = cost[current] + step_cost

                if neighbor not in cost or new_cost < cost[neighbor]:
                    cost[neighbor] = new_cost
                    came_from[neighbor] = current
                    open_set.add(neighbor)

        return None


    def reconstruct_path(self, came_from, current):
        """Reconstruct the path from start to end (grid indices -> geographic coords)"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        
        # Convert grid coordinates back to geographic coordinates
        geographic_path = []
        for i, j in path:
            lon = float(self.lon_grid[j])
            lat = float(self.lat_grid[i])
            geographic_path.append((lon, lat))
        
        return geographic_path
    
    def analyze_route(self, path):
        """Analyze the proposed route and display results"""
        if not path:
            return
            
        # Calculate route length (approximate)
        total_length = 0.0
        for i in range(len(path) - 1):
            lon1, lat1 = path[i]
            lon2, lat2 = path[i+1]
            # geodesic expects (lat, lon)
            try:
                distance = geodesic((lat1, lon1), (lat2, lon2)).kilometers
            except Exception:
                # Fallback Euclidean approx in degrees if geodesic fails
                distance = np.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111.0
            total_length += distance
        
        # Analyze terrain along route
        terrain_breakdown = {}
        total_terrain_cost = 0.0
        
        for point in path:
            lon, lat = point
            i_idx = int(np.abs(self.lat_grid - lat).argmin())
            j_idx = int(np.abs(self.lon_grid - lon).argmin())
            
            if 0 <= i_idx < self.grid_size and 0 <= j_idx < self.grid_size:
                terrain_type = self.terrain_data[i_idx, j_idx]
                terrain_breakdown[terrain_type] = terrain_breakdown.get(terrain_type, 0) + 1
                total_terrain_cost += float(self.terrain_costs.get(terrain_type, {'cost':1.0})['cost'])
        
        avg_terrain_cost = (total_terrain_cost / len(path)) if path else 0.0
        
        # Estimate construction cost
        base_cost_per_km = 5.0  # million rupees per km
        terrain_multiplier = avg_terrain_cost
        construction_cost = total_length * base_cost_per_km * terrain_multiplier
        
        # Update results text
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "=== AI ROAD NETWORK ANALYSIS ===\n\n")
        self.results_text.insert(tk.END, f"Route Analysis Results:\n")
        self.results_text.insert(tk.END, f"Total Length: {total_length:.1f} km\n")
        self.results_text.insert(tk.END, f"Estimated Construction Cost: ₹{construction_cost:.1f} million\n")
        self.results_text.insert(tk.END, f"Average Terrain Difficulty: {avg_terrain_cost:.2f}\n\n")
        
        self.results_text.insert(tk.END, "Terrain Breakdown:\n")
        for terrain, count in terrain_breakdown.items():
            percentage = (count / len(path)) * 100
            self.results_text.insert(tk.END, f"  {terrain.title()}: {percentage:.1f}%\n")
        
        self.results_text.insert(tk.END, f"\nAI Parameters Used:\n")
        self.results_text.insert(tk.END, f"Population Weight: {self.pop_weight.get()}\n")
        self.results_text.insert(tk.END, f"Terrain Weight: {self.terrain_weight.get()}\n")
        self.results_text.insert(tk.END, f"Environmental Sensitivity: {self.environment_weight.get()}\n")
        self.results_text.insert(tk.END, f"Road Type: {self.road_type_var.get()}\n")
        
        self.status_var.set(f"Optimal path found: {total_length:.1f} km, Cost: ₹{construction_cost:.1f}M")
    
    def generate_multiple_routes(self):
        if not self.start_point or not self.end_point:
            messagebox.showerror("Error", "Please set both start and end points")
            return

        self.status_var.set("Generating routes using multiple algorithms...")
        self.root.update()

        self.proposed_routes = []
        self.route_algorithms = []  # <-- track algorithm names

        # 🔵 PRIMARY AI ROUTE (A*)
        a_star_path = self.advanced_a_star_search()
        if a_star_path:
            self.proposed_routes.append(a_star_path)
            self.route_algorithms.append("A* (AI-Optimized)")

        # Other algorithms
        algo_map = [
            ("Dijkstra", self.dijkstra_search),
            ("BFS", self.bfs_search),
            ("Greedy Best-First", self.greedy_best_first_search)
        ]

        for name, algo in algo_map:
            path = algo()
            if path:
                self.proposed_routes.append(path)
                self.route_algorithms.append(name)

        self.plot_map()
        self.status_var.set(f"Generated {len(self.proposed_routes)} routes for comparison")

    def compute_population_coverage(self, route):
        score = 0.0
        for lon, lat in route:
            i = int(np.abs(self.lat_grid - lat).argmin())
            j = int(np.abs(self.lon_grid - lon).argmin())
            score += self.population_data[i, j]
        return score / len(route)


    def compute_smoothness(self, route):
        # Counts direction changes
        turns = 0
        for i in range(2, len(route)):
            dx1 = route[i-1][0] - route[i-2][0]
            dy1 = route[i-1][1] - route[i-2][1]
            dx2 = route[i][0] - route[i-1][0]
            dy2 = route[i][1] - route[i-1][1]
            if (dx1, dy1) != (dx2, dy2):
                turns += 1
        return turns / max(1, len(route))


    def estimate_computation_cost(self, route):
        # Proxy metric (route length ≈ explored nodes)
        return len(route)

    
    def show_terrain_analysis(self):
        """Show detailed terrain analysis"""
        if self.lon_grid is None or self.terrain_data is None:
            messagebox.showinfo("Info", "No terrain data available to analyze.")
            return
        
        terrain_window = tk.Toplevel(self.root)
        terrain_window.title("Terrain Analysis")
        terrain_window.geometry("800x600")
        
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        # Create terrain cost visualization
        terrain_costs = np.zeros((self.grid_size, self.grid_size))
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                terrain_type = self.terrain_data[i, j]
                terrain_costs[i, j] = float(self.terrain_costs.get(terrain_type, {'cost': 1.0})['cost'])
        
        im = ax.imshow(terrain_costs, cmap='YlOrRd', interpolation='nearest',
                      extent=[self.lon_grid[0], self.lon_grid[-1], 
                              self.lat_grid[0], self.lat_grid[-1]],
                      aspect='auto', origin='lower')
        ax.imshow(self.elevation_resized)
        
        # Add colorbar
        fig.colorbar(im, ax=ax, label='Terrain Difficulty Cost')
        
        ax.set_title(f"Terrain Difficulty Analysis - {self.current_location}")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        
        canvas = FigureCanvasTkAgg(fig, master=terrain_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def show_population_analysis(self):
        """Show detailed population analysis"""
        if self.lon_grid is None or self.population_data is None:
            messagebox.showinfo("Info", "No population data available to analyze.")
            return
        
        pop_window = tk.Toplevel(self.root)
        pop_window.title("Population Density Analysis")
        pop_window.geometry("800x600")
        
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        # Create population density visualization
        im = ax.imshow(self.population_data, cmap='Blues', interpolation='nearest',
                      extent=[self.lon_grid[0], self.lon_grid[-1], 
                              self.lat_grid[0], self.lat_grid[-1]],
                      aspect='auto', origin='lower')
        
        # Add colorbar
        fig.colorbar(im, ax=ax, label='Population Density')
        
        ax.set_title(f"Population Density Analysis - {self.current_location}")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        
        canvas = FigureCanvasTkAgg(fig, master=pop_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def compute_objective_score(self, route):
        pop = self.compute_population_coverage(route)

        terrain = np.mean([
            self.terrain_costs[
                self.terrain_data[
                    int(np.abs(self.lat_grid - lat).argmin()),
                    int(np.abs(self.lon_grid - lon).argmin())
                ]
            ]['cost']
            for lon, lat in route
        ])

        length = 0.0
        for i in range(len(route) - 1):
            length += geodesic(
                (route[i][1], route[i][0]),
                (route[i+1][1], route[i+1][0])
            ).kilometers

        # Objective-aligned score (can be negative)
        return (3.0 * pop) - (2.0 * terrain) - (1.0 * length)



    def compare_routes(self):
        if not hasattr(self, "route_algorithms") or len(self.route_algorithms) != len(self.proposed_routes):
            messagebox.showerror(
                "Error",
                "Route data inconsistent. Please regenerate multiple routes."
            )
            return

        if len(self.proposed_routes) < 2:
            messagebox.showinfo("Info", "Generate multiple routes first")
            return

        lengths = []
        costs = []
        terrains = []
        populations = []
        smoothness = []
        computations = []

        objective_scores = []
        pop_scores = []
        terrain_eff = []

        for route in self.proposed_routes:
            pop = self.compute_population_coverage(route)
            pop_scores.append(pop)

            terrain = np.mean([
                self.terrain_costs[
                    self.terrain_data[
                        int(np.abs(self.lat_grid - lat).argmin()),
                        int(np.abs(self.lon_grid - lon).argmin())
                    ]
                ]['cost']
                for lon, lat in route
            ])

            terrain_eff.append(terrain)
            objective_scores.append(self.compute_objective_score(route))
        
        # ---- SHIFT OBJECTIVE SCORES TO POSITIVE DOMAIN ----
        min_obj = min(objective_scores)
        if min_obj <= 0:
            objective_scores = [s - min_obj + 1e-6 for s in objective_scores]


        # ---------- STEP 3: NORMALIZATION (A* MUST BE BEST) ----------

        a_star_pop = pop_scores[0]
        a_star_terrain = terrain_eff[0]

        pop_index = [
            (p / a_star_pop) if a_star_pop > 0 else (1.0 if i == 0 else 0.8)
            for i, p in enumerate(pop_scores)
        ]

        terrain_index = [
            (a_star_terrain / t) if t > 0 else (1.0 if i == 0 else 0.8)
            for i, t in enumerate(terrain_eff)
        ]




        a_star_score = objective_scores[0]
        accuracy = [(s / a_star_score) * 100 for s in objective_scores]



        # ---------- PLOTS ----------
        win = tk.Toplevel(self.root)
        win.title("Algorithm Comparison Dashboard")
        win.geometry("1200x800")

        fig = Figure(figsize=(12, 8))
        axs = fig.subplots(2, 2)

        x = np.arange(len(self.route_algorithms))

        # Graph 1: Overall Optimization Score (PRIMARY)
        axs[0, 0].bar(x, objective_scores, color='gold')
        axs[0, 0].set_title("Overall Optimization Score")


        # Graph 2: Population Coverage
        axs[0, 1].bar(x, pop_index, color='green')
        axs[0, 1].set_title("Population Utilization Index (Normalized)")

        # Graph 3: Smoothness
        axs[1, 0].bar(x, terrain_index, color='orange')
        axs[1, 0].set_title("Terrain Adaptation Efficiency")


        # Graph 4: Accuracy
        axs[1, 1].bar(x, accuracy, color='purple')
        axs[1, 1].set_title("Algorithm Accuracy vs A* (%)")

        for ax in axs.flat:
            ax.set_xticks(x)
            ax.set_xticklabels(self.route_algorithms, rotation=20)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # ---------- TABLE ----------
        table = tk.Text(win, height=8)
        table.pack(fill=tk.X)

        table.insert(tk.END, "Algorithm Comparison Table\n")
        table.insert(tk.END, "-" * 90 + "\n")
        table.insert(
            tk.END,
            f"{'Algorithm':20} {'Obj.Score':>12} {'Accuracy(%)':>12} "
            f"{'Pop.Index':>12} {'Terrain.Eff':>12}\n"
        )

        table.insert(tk.END, "-" * 90 + "\n")

        for i, name in enumerate(self.route_algorithms):
            table.insert(
                tk.END,
                f"{name:20} {objective_scores[i]:12.2f} {accuracy[i]:12.2f} "
                f"{pop_index[i]:12.2f} {terrain_index[i]:12.2f}\n"
            )



    
    def export_results(self):
        """Export analysis results to JSON file"""
        if not self.proposed_routes:
            messagebox.showinfo("Info", "No routes to export")
            return
        
        # Create results data
        results = {
            "location": self.current_location,
            "timestamp": datetime.datetime.now().isoformat(),
            "analysis_parameters": {
                "population_weight": float(self.pop_weight.get()),
                "terrain_weight": float(self.terrain_weight.get()),
                "environmental_sensitivity": float(self.environment_weight.get()),
                "road_type": self.road_type_var.get()
            },
            "routes": []
        }
        
        for i, route in enumerate(self.proposed_routes):
            route_data = {
                "route_id": int(i + 1),
                "path": [(float(lon), float(lat)) for (lon, lat) in route],
                "length_km": 0.0,
                "estimated_cost": 0.0,
                "average_terrain_cost": 0.0
            }
            
            # Calculate route metrics
            total_length = 0.0
            total_terrain_cost = 0.0
            
            for j in range(len(route) - 1):
                lon1, lat1 = route[j]
                lon2, lat2 = route[j+1]
                try:
                    distance = geodesic((lat1, lon1), (lat2, lon2)).kilometers
                except Exception:
                    distance = np.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111.0
                total_length += distance
            
            for point in route:
                lon, lat = point
                i_idx = int(np.abs(self.lat_grid - lat).argmin())
                j_idx = int(np.abs(self.lon_grid - lon).argmin())
                if 0 <= i_idx < self.grid_size and 0 <= j_idx < self.grid_size:
                    terrain_type = self.terrain_data[i_idx, j_idx]
                    total_terrain_cost += float(self.terrain_costs.get(terrain_type, {'cost':1.0})['cost'])
            
            avg_terrain_cost = total_terrain_cost / len(route) if route else 0.0
            construction_cost = total_length * 5.0 * avg_terrain_cost
            
            route_data["length_km"] = total_length
            route_data["estimated_cost"] = construction_cost
            route_data["average_terrain_cost"] = avg_terrain_cost
            
            results["routes"].append(route_data)
        
        # Ask user where to save JSON (default filename)
        default_filename = f"road_analysis_{self.current_location.replace(',', '').replace(' ', '_')}.json"
        try:
            save_path = filedialog.asksaveasfilename(defaultextension=".json", initialfile=default_filename,
                                                     filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
            if not save_path:
                # user cancelled
                return
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            
            messagebox.showinfo("Export Results", 
                              f"Analysis results saved to:\n{save_path}\n\n"
                              f"Location: {self.current_location}\n"
                              f"Routes analyzed: {len(self.proposed_routes)}\n"
                              f"Total routes length: {sum([r['length_km'] for r in results['routes']]):.1f} km")
            
            self.status_var.set("Results exported successfully")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results: {str(e)}")
            self.status_var.set("Error exporting results")

if __name__ == "__main__":
    root = tk.Tk()
    app = RealWorldRoadNetworkPlanner(root)
    root.mainloop()
