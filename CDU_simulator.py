import tkinter as tk
from tkinter import messagebox, simpledialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from flight_planner import FlightPlanner
from waypoints_manager import WaypointManager

class CDUSimulator:
    def __init__(self, master):
        self.master = master
        master.title("Flight Management System - CDU Simulator")
        master.geometry("1000x700")  # Taille ajustée pour inclure le graphique

        # Initialize components
        self.waypoint_manager = WaypointManager("airport_data.json")
        self.flight_planner = FlightPlanner(self.waypoint_manager)

        # Create main frame
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Create display screen
        self.display_screen = tk.Text(self.main_frame, height=10, width=80, font=('Courier', 12))
        self.display_screen.pack(pady=10)

        # Create button frame
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(pady=10)

        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Flight Trajectory")
        self.ax.set_xlabel("Longitude")
        self.ax.set_ylabel("Latitude")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.main_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(pady=20)

        # Create buttons
        buttons = [
            ("RTE", self.plan_route),
            ("LEGS", self.view_legs)
        ]

        for i, (label, command) in enumerate(buttons):
            btn = tk.Button(self.button_frame, text=label, command=command, width=10)
            btn.grid(row=i // 3, column=i % 3, padx=5, pady=5)

        # Create additional buttons to simulate CDU interface
        additional_buttons = [
            ("INIT", lambda: self.switch_page("INIT")),
            ("IDENT", lambda: self.switch_page("IDENT")),
            ("PERF", lambda: self.switch_page("PERF")),
            ("ROUTE", lambda: self.switch_page("ROUTE")),
            ("LEGS", lambda: self.switch_page("LEGS")),
            ("VNAV", lambda: self.switch_page("VNAV")),
            ("EXEC", lambda: self.switch_page("EXEC")),
            ("DIR INTC", self.dir_intc_page)
        ]

        for i, (label, command) in enumerate(additional_buttons, start=len(buttons)):
            btn = tk.Button(self.button_frame, text=label, command=command, width=10)
            btn.grid(row=i // 3, column=i % 3, padx=5, pady=5)

    def update_display(self, message):
        """Update the display screen."""
        self.display_screen.delete(1.0, tk.END)
        self.display_screen.insert(tk.END, message)

    def clear_plot(self):
        """Clear the matplotlib plot."""
        self.ax.clear()
        self.ax.set_title("Flight Trajectory")
        self.ax.set_xlabel("Longitude")
        self.ax.set_ylabel("Latitude")

    def plot_trajectory(self, trajectory):
        """Plot the flight trajectory on the map."""
        self.clear_plot()

        # Extract latitudes and longitudes
        latitudes = [point[0] for point in trajectory]
        longitudes = [point[1] for point in trajectory]
        labels = [point[2] for point in trajectory]

        # Plot the points and lines
        self.ax.plot(longitudes, latitudes, marker='o', linestyle='-', color='blue', label="Optimal Path")
        for i, label in enumerate(labels):
            self.ax.text(longitudes[i], latitudes[i], label, fontsize=8, ha='right')
        self.ax.legend()
        self.canvas.draw()

    def plan_route(self):
        """Plan a flight route."""
        start_icao = simpledialog.askstring("RTE", "Enter the ICAO code for the starting airport:").strip().upper()
        end_icao = simpledialog.askstring("RTE", "Enter the ICAO code for the destination airport:").strip().upper()

        start_wp = self.waypoint_manager.find_by_icao(start_icao)
        end_wp = self.waypoint_manager.find_by_icao(end_icao)

        if not start_wp or not end_wp:
            messagebox.showerror("Error", "Invalid ICAO codes!")
            return

        start = (start_wp['latitude'], start_wp['longitude'], start_wp['icao_code'])
        end = (end_wp['latitude'], end_wp['longitude'], end_wp['icao_code'])

        waypoints_in_route = self.flight_planner.filter_waypoints(start, end)
        optimal_path = self.flight_planner.dijkstra(
            [(wp['latitude'], wp['longitude'], wp['icao_code']) for wp in waypoints_in_route],
            start, end
        )

        message = "\nOptimal Path:\n" + "\n".join(f"{p[2]} ({p[0]:.4f}, {p[1]:.4f})" for p in optimal_path)
        self.update_display(message)

        # Plot the trajectory on the map
        self.plot_trajectory(optimal_path)

    def view_legs(self):
        """View flight legs (optional implementation)."""
        messagebox.showinfo("LEGS", "Legs feature is under development.")

    def switch_page(self, page_name):
        # Switch between different pages
        if page_name == "INIT":
            self.init_page()
        elif page_name == "IDENT":
            self.ident_page()
        elif page_name == "PERF":
            self.perf_init_page()
        elif page_name == "ROUTE":
            self.route_page()
        elif page_name == "LEGS":
            self.legs_page()
        elif page_name == "VNAV":
            self.vnav_page()
        elif page_name == "EXEC":
            self.execute_changes()

    def init_page(self):
        self.update_display("Initializing IRS...")
        # Simulate IRS initialization process
        messagebox.showinfo("IRS", "IRS alignment in progress. Please wait...")

    def ident_page(self):
        self.update_display("IDENT Page")
        # Display aircraft and database information
        info = "Aircraft: Boeing 737-800 WL\nENG RATING: 26K\nAIRAC Cycle: 1809\nDatabase Valid: 16 Aug - 12 Sep 2018\nProgram Version: U10.8A"
        messagebox.showinfo("IDENT", info)

    def perf_init_page(self):
        self.update_display("PERF INIT Page")
        # Simulate input fields for Cost Index, Reserves, ZFW, and planned fuel
        cost_index = simpledialog.askfloat("Cost Index", "Enter Cost Index:")
        reserves = simpledialog.askfloat("Reserves", "Enter Reserves (tonnes):")
        zfw = simpledialog.askfloat("ZFW", "Enter Zero Fuel Weight (tonnes):")
        planned_fuel = simpledialog.askfloat("Planned Fuel", "Enter Planned Fuel (tonnes):")

        # Calculate Gross Weight and optimal flight level
        gross_weight = zfw + planned_fuel
        optimal_fl = 390  # Example calculation

        # Display calculated information
        info = f"GROSS WEIGHT: {gross_weight} tonnes\nOPTIMAL FL: {optimal_fl}"
        messagebox.showinfo("PERF INIT Calculations", info)

    def route_page(self):
        self.update_display("ROUTE Page")
        # Placeholder for route management

    def legs_page(self):
        self.update_display("LEGS Page")
        # Placeholder for legs management

    def vnav_page(self):
        self.update_display("VNAV Page")
        # Placeholder for vertical navigation setup

    def execute_changes(self):
        # Simulate execution of changes
        messagebox.showinfo("EXEC", "Changes executed successfully.")

    def dir_intc_page(self):
        self.update_display("DIR INTC Page")
        # Placeholder for direct intercept operations

if __name__ == "__main__":
    root = tk.Tk()
    app = CDUSimulator(root)
    root.mainloop()
