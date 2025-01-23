import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def haversine(lat1, lon1, lat2, lon2):
    """Calculer la distance entre deux points géographiques."""
    R = 6371  # Rayon de la Terre en km
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    a = np.sin(delta_phi / 2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2)**2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

class FlightPlanner:
    def __init__(self, waypoint_manager):
        self.waypoint_manager = waypoint_manager
        self.root = None
        self.ax = None
        self.canvas = None

    def filter_waypoints(self, start, end):
        selected_waypoints = []
        for wp in self.waypoint_manager.waypoints:
            wp_lat, wp_lon = wp['latitude'], wp['longitude']
            # Vérifier si le waypoint est différent du point de départ
            if (wp_lat, wp_lon) != (start[0], start[1]) and (wp_lat, wp_lon) != (end[0], end[1]):
                if min(start[0], end[0]) <= wp_lat <= max(start[0], end[0]) and \
                        min(start[1], end[1]) <= wp_lon <= max(start[1], end[1]):
                    selected_waypoints.append(wp)
        return selected_waypoints

    # Enhanced trajectory calculation using spherical coordinates
    def calculate_trajectory(self, waypoints, start, end, wind_speed=0, fuel_efficiency=1):
        all_points = [start] + waypoints + [end]
        num_points = len(all_points)
        distance_matrix = np.zeros((num_points, num_points))

        # Calculate distances using spherical coordinates
        for i in range(num_points):
            for j in range(num_points):
                if i != j:
                    distance = self.spherical_distance(
                        all_points[i][0], all_points[i][1],
                        all_points[j][0], all_points[j][1]
                    )
                    # Adjust distance based on wind and fuel efficiency
                    adjusted_distance = distance * (1 + wind_speed / 100) * fuel_efficiency
                    distance_matrix[i, j] = adjusted_distance

        # Implement robust equation for optimal trajectory
        return self.optimize_path(distance_matrix, all_points)

    def spherical_distance(self, lat1, lon1, lat2, lon2):
        # Implement spherical distance calculation
        phi1, phi2 = np.radians(lat1), np.radians(lat2)
        delta_phi = np.radians(lat2 - lat1)
        delta_lambda = np.radians(lon2 - lon1)
        a = np.sin(delta_phi / 2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2)**2
        return 6371 * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    def optimize_path(self, distance_matrix, all_points):
        # Implement optimization logic
        visited = [False] * len(all_points)
        distances = [float('inf')] * len(all_points)
        previous = [-1] * len(all_points)
        distances[0] = 0

        for _ in range(len(all_points)):
            min_distance = float('inf')
            min_index = -1
            for i in range(len(all_points)):
                if not visited[i] and distances[i] < min_distance:
                    min_distance = distances[i]
                    min_index = i
            visited[min_index] = True

            for i in range(len(all_points)):
                if not visited[i] and distance_matrix[min_index, i] > 0:
                    new_distance = distances[min_index] + distance_matrix[min_index, i]
                    if new_distance < distances[i]:
                        distances[i] = new_distance
                        previous[i] = min_index

        # Construct the optimal path
        path = []
        current_index = len(all_points) - 1
        while current_index != -1:
            path.insert(0, all_points[current_index])
            current_index = previous[current_index]

        return path

    # Algorithme de Dijkstra pour calculer la trajectoire optimale
    def dijkstra(self, waypoints, start, end):
        # Conserver le point de départ dans la liste des points, mais ne pas l'inclure parmi les waypoints intermédiaires
        all_points = [start] + waypoints + [end]
        num_points = len(all_points)
        distance_matrix = np.zeros((num_points, num_points))

        # Calculer les distances entre tous les points
        for i in range(num_points):
            for j in range(num_points):
                if i != j:
                    distance_matrix[i, j] = haversine(
                        all_points[i][0], all_points[i][1],
                        all_points[j][0], all_points[j][1]
                    )

        visited = [False] * num_points
        distances = [float('inf')] * num_points
        previous = [-1] * num_points
        distances[0] = 0

        for _ in range(num_points):
            min_distance = float('inf')
            min_index = -1
            for i in range(num_points):
                if not visited[i] and distances[i] < min_distance:
                    min_distance = distances[i]
                    min_index = i

            if min_index == -1:
                break

            visited[min_index] = True

            for j in range(num_points):
                if distance_matrix[min_index][j] > 0 and not visited[j]:
                    new_distance = distances[min_index] + distance_matrix[min_index][j]
                    if new_distance < distances[j]:
                        distances[j] = new_distance
                    previous[j] = min_index

        # Reconstruire le chemin optimal
        path = []
        current = num_points - 1
        while current != -1:
            path.append(current)
            current = previous[current]

        path.reverse()

        return [all_points[i] for i in path]

    # Calculate and plot trajectory
    def calculate_and_plot_trajectory(self, waypoints, start, end):
        path = self.calculate_trajectory(waypoints, start, end)

        # Extract latitudes and longitudes
        lats = [point[0] for point in path]
        lons = [point[1] for point in path]

        # Plot trajectory
        self.ax.clear()
        self.ax.plot(lons, lats, marker='o')
        self.ax.set_title("Flight Trajectory")
        self.ax.set_xlabel("Longitude")
        self.ax.set_ylabel("Latitude")
        self.canvas.draw()

        return path

    # Update existing methods to use the new plotting function
    def enhanced_dijkstra(self, waypoints, start, end):
        return self.calculate_and_plot_trajectory(waypoints, start, end)

    def init_plot(self, root):
        self.root = root
        self.ax = plt.axes()
        self.canvas = FigureCanvasTkAgg(self.ax, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
