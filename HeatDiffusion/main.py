import tkinter as tk
from tkinter import ttk
import numpy as np

from engine import HeatEngine
from renderer import HeatRenderer
from interaction import InteractionHandler
from analytics import AnalyticsTracker

class HeatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive 2D Heat Diffusion Laboratory")
        self.root.geometry("1100x800")
        
        # Grid parameters
        self.nx = 60
        self.ny = 60
        self.alpha = 0.5
        
        # Heat injection parameters
        self.heat_params = {'radius': 3, 'intensity': 50}
        
        # Simulation State
        self.running = False
        self.steps_per_frame = 2 # Simulation speed
        
        # Components
        self.engine = HeatEngine(nx=self.nx, ny=self.ny, alpha=self.alpha)
        
        self.setup_ui()
        
        self.renderer = HeatRenderer(self.render_frame, self.nx, self.ny)
        self.analytics = AnalyticsTracker(self.analytics_frame)
        self.interaction = InteractionHandler(self.renderer, self.engine, self.heat_params)
        
        # Start the loop
        self.update_loop()

    def setup_ui(self):
        # Main layout
        self.main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True)
        
        # Left Panel (Controls)
        self.control_frame = ttk.Frame(self.main_pane, padding=10, width=250)
        self.main_pane.add(self.control_frame)
        
        # Center Panel (Heatmap)
        self.render_frame = ttk.Frame(self.main_pane, padding=10)
        self.main_pane.add(self.render_frame)
        
        # Right Panel (Analytics)
        self.analytics_frame = ttk.Frame(self.main_pane, padding=10, width=300)
        self.main_pane.add(self.analytics_frame)
        
        # --- Controls Sections ---
        ttk.Label(self.control_frame, text="SIMULATION CONTROLS", font=('Arial', 10, 'bold')).pack(pady=(0, 10))
        
        # Play/Pause/Reset
        self.btn_play = ttk.Button(self.control_frame, text="Start", command=self.toggle_running)
        self.btn_play.pack(fill=tk.X, pady=2)
        
        ttk.Button(self.control_frame, text="Reset Grid", command=self.reset_sim).pack(fill=tk.X, pady=2)
        ttk.Button(self.control_frame, text="Clear Plots", command=lambda: self.analytics.reset()).pack(fill=tk.X, pady=2)
        
        # Diffusivity (Alpha)
        ttk.Separator(self.control_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(self.control_frame, text="Thermal Diffusivity (\u03b1)").pack()
        self.alpha_scale = ttk.Scale(self.control_frame, from_=0.01, to=2.0, value=self.alpha, command=self.on_alpha_change)
        self.alpha_scale.pack(fill=tk.X)
        self.lbl_alpha = ttk.Label(self.control_frame, text=f"{self.alpha:.2f}")
        self.lbl_alpha.pack()
        
        # Heat Source Intensity
        ttk.Separator(self.control_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(self.control_frame, text="Heat Intensity").pack()
        self.int_scale = ttk.Scale(self.control_frame, from_=5, to=200, value=self.heat_params['intensity'], 
                                   command=lambda v: self.heat_params.update({'intensity': float(v)}))
        self.int_scale.pack(fill=tk.X)
        
        # Brush Radius
        ttk.Label(self.control_frame, text="Brush Radius").pack()
        self.rad_scale = ttk.Scale(self.control_frame, from_=1, to=10, value=self.heat_params['radius'], 
                                   command=lambda v: self.heat_params.update({'radius': int(float(v))}))
        self.rad_scale.pack(fill=tk.X)

        # Simulation Speed (steps per frame)
        ttk.Label(self.control_frame, text="Sim Speed (Steps/Frame)").pack()
        self.speed_scale = ttk.Scale(self.control_frame, from_=1, to=10, value=self.steps_per_frame, 
                                     command=lambda v: setattr(self, 'steps_per_frame', int(float(v))))
        self.speed_scale.pack(fill=tk.X)

        # Boundary Conditions
        ttk.Separator(self.control_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(self.control_frame, text="Boundary Condition").pack()
        self.bc_var = tk.StringVar(value='dirichlet')
        bc_types = [('Fixed (Cold)', 'dirichlet'), ('Insulated', 'neumann'), ('Periodic', 'periodic')]
        for text, mode in bc_types:
            ttk.Radiobutton(self.control_frame, text=text, variable=self.bc_var, value=mode, 
                            command=self.on_bc_change).pack(anchor=tk.W)

    def toggle_running(self):
        self.running = not self.running
        self.btn_play.config(text="Pause" if self.running else "Start")

    def reset_sim(self):
        self.engine.reset()
        self.renderer.update(self.engine.u)
        self.analytics.reset()

    def on_alpha_change(self, val):
        self.alpha = float(val)
        self.lbl_alpha.config(text=f"{self.alpha:.2f}")
        self.engine.alpha = self.alpha
        self.engine.update_dt()

    def on_bc_change(self):
        self.engine.bc_type = self.bc_var.get()

    def update_loop(self):
        """Main simulation and visualization loop."""
        if self.running:
            # Perform numerical steps
            for _ in range(self.steps_per_frame):
                self.engine.step()
            
            # Update visuals
            stats = self.engine.get_stats()
            self.renderer.update(self.engine.u)
            self.analytics.update(self.engine.u, stats)
        
        # Schedule next update (approx 30 FPS target for UI)
        self.root.after(30, self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = HeatApp(root)
    root.mainloop()
