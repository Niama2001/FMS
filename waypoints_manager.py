import json

class WaypointManager:
    def __init__(self, file_path):
        self.file_path = "airport_data.json"
        self.waypoints = self.load_waypoints()

    def load_waypoints(self):
        """Charger les waypoints depuis un fichier JSON."""
        with open(self.file_path, 'r') as file:
            data = json.load(file)
        return data

    def find_by_icao(self, icao_code):
        """Trouver un point par son code ICAO."""
        for wp in self.waypoints:
            if wp.get("icao_code") == icao_code:
                return wp
        return None
