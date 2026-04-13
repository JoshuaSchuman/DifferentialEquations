import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from simulation import WealthSimulationEngine
from visualization import VisualizationEngine

class WealthSimulatorApp:
    """
    Main Controller and UI layer for the Wealth Inequality Simulator.
    Manages the Tkinter interface, bridges user inputs to the simulation engine,
    and updates the visualization components (plots and canvas).
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Wealth Inequality Dynamics Simulator")
        self.root.geometry("1400x900")
        
        # Initialize Core Engines
        self.engine = WealthSimulationEngine()
        self.is_running = False
        
        # Build UI
        self.setup_ui()
        
        # Initialize canvas rendering engine after UI is built
        self.viz_engine = VisualizationEngine(self.anim_canvas, 600, 500)
        self.viz_engine.sync_agents(self.engine.wealth)
        
        # Initial Render
        self.update_plots()
        self.update_readouts()
        
        # Start main simulation loop
        self.update_loop()

    def setup_ui(self):
        """Builds the 3-panel UI layout (Controls, Canvas, Plots)."""
        # Paned window to divide screen dynamically
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # --- Left Panel: Controls ---
        self.left_panel = ttk.Frame(self.main_paned, padding=10, width=350)
        self.main_paned.add(self.left_panel, weight=1)
        
        ttk.Label(self.left_panel, text="Simulation Controls", font=('Helvetica', 16, 'bold')).pack(pady=10)
        
        # Basic Settings (Distribution & Model Type)
        settings_frame = ttk.LabelFrame(self.left_panel, text="Initial Settings", padding=10)
        settings_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(settings_frame, text="Initial Distribution:").pack(anchor=tk.W)
        self.dist_var = tk.StringVar(value="uniform")
        dist_dropdown = ttk.Combobox(settings_frame, textvariable=self.dist_var, 
                                      values=["uniform", "random", "normal", "pareto"], state="readonly")
        dist_dropdown.pack(fill=tk.X, pady=5)
        dist_dropdown.bind("<<ComboboxSelected>>", self.on_reset)
        
        ttk.Label(settings_frame, text="Exchange Model:").pack(anchor=tk.W, pady=(5, 0))
        self.model_var = tk.StringVar(value="random")
        model_dropdown = ttk.Combobox(settings_frame, textvariable=self.model_var, 
                                      values=["random", "saving"], state="readonly")
        model_dropdown.pack(fill=tk.X, pady=5)
        model_dropdown.bind("<<ComboboxSelected>>", self.on_model_change)
        
        # Economic Parameters
        self.params_frame = ttk.LabelFrame(self.left_panel, text="Economic Parameters", padding=10)
        self.params_frame.pack(fill=tk.X, pady=10)
        
        self.sliders = {}
        # Format: (key, label, min, max, default, is_integer)
        self.param_specs = [
            ("num_agents", "Number of Agents", 10, 1500, 500, True),
            ("saving_rate", "Saving Rate", 0.0, 0.99, 0.0, False),
            ("trade_intensity", "Trade Intensity", 0.0, 1.0, 1.0, False),
            ("tax_rate", "Tax Rate", 0.0, 0.1, 0.0, False),
            ("growth_rate", "Growth Rate (r)", -0.05, 0.05, 0.0, False),
            ("noise_level", "Market Noise", 0.0, 5.0, 0.0, False)
        ]
        
        for key, label, low, high, default, is_int in self.param_specs:
            frame = ttk.Frame(self.params_frame)
            frame.pack(fill=tk.X, pady=5)
            ttk.Label(frame, text=label).pack(side=tk.LEFT)
            val_label = ttk.Label(frame, text=f"{default:.2f}" if not is_int else str(int(default)))
            val_label.pack(side=tk.RIGHT)
            
            slider = ttk.Scale(self.params_frame, from_=low, to=high, orient=tk.HORIZONTAL,
                               command=lambda v, k=key, l=val_label, ii=is_int: self.update_param(k, v, l, ii))
            slider.set(default)
            slider.pack(fill=tk.X)
            self.sliders[key] = (slider, val_label)
            
        self.redist_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.params_frame, text="Enable Wealth Redistribution", 
                        variable=self.redist_var, command=self.update_redist).pack(anchor=tk.W, pady=5)

        # Simulation Buttons & Speed
        btn_frame = ttk.Frame(self.left_panel)
        btn_frame.pack(fill=tk.X, pady=15)
        
        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.toggle_sim)
        self.start_btn.pack(side=tk.LEFT, expand=True, padx=2)
        
        ttk.Button(btn_frame, text="Reset", command=self.on_reset).pack(side=tk.LEFT, expand=True, padx=2)
        
        speed_frame = ttk.Frame(self.left_panel)
        speed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(speed_frame, text="Sim Speed:").pack(side=tk.LEFT)
        self.speed_label = ttk.Label(speed_frame, text="1")
        self.speed_label.pack(side=tk.RIGHT)
        self.speed_slider = ttk.Scale(speed_frame, from_=1, to=20, orient=tk.HORIZONTAL,
                                      command=lambda v: self.speed_label.config(text=str(int(float(v)))))
        self.speed_slider.set(1)
        self.speed_slider.pack(fill=tk.X, padx=10)
        
        # --- Center Panel: Visualization Canvas & Readouts ---
        self.center_panel = ttk.Frame(self.main_paned, padding=10)
        self.main_paned.add(self.center_panel, weight=2)
        
        ttk.Label(self.center_panel, text="Agent Economy Visualization", font=('Helvetica', 14)).pack(pady=5)
        self.anim_canvas = tk.Canvas(self.center_panel, width=600, height=500, bg="#1a1a1a", highlightthickness=0)
        self.anim_canvas.pack(pady=10, expand=True, fill=tk.BOTH)
        
        # Real-time Metrics Readout
        self.readout_frame = ttk.LabelFrame(self.center_panel, text="Real-time Statistics", padding=10)
        self.readout_frame.pack(fill=tk.X, pady=10)
        
        self.metrics = {
            'time': tk.StringVar(value="Time: 0.0"),
            'gini': tk.StringVar(value="Gini Coefficient: 0.00"),
            'top10': tk.StringVar(value="Top 10% Share: 0.0%"),
            'total': tk.StringVar(value="Total Wealth: 0.0")
        }
        
        for k in ['time', 'gini', 'top10', 'total']:
            ttk.Label(self.readout_frame, textvariable=self.metrics[k], font=('Courier', 12, 'bold')).pack(anchor=tk.W)
        
        # --- Right Panel: Analytical Plots ---
        self.right_panel = ttk.Frame(self.main_paned, padding=10)
        self.main_paned.add(self.right_panel, weight=2)
        
        self.fig, (self.ax_hist, self.ax_gini) = plt.subplots(2, 1, figsize=(5, 8))
        self.fig.tight_layout(pad=4.0)
        
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=self.right_panel)
        self.canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # History Scrubbing
        self.scrub_frame = ttk.LabelFrame(self.right_panel, text="History Scrub (Pause to Use)", padding=10)
        self.scrub_frame.pack(fill=tk.X, pady=5)
        self.scrub_slider = ttk.Scale(self.scrub_frame, from_=0, to=0, orient=tk.HORIZONTAL, command=self.on_scrub)
        self.scrub_slider.pack(fill=tk.X)

    def update_param(self, key, val, label, is_int):
        """Handles real-time updates from sliders."""
        val = float(val)
        if is_int:
            val = int(val)
            label.config(text=str(val))
        else:
            label.config(text=f"{val:.3f}")
            
        setattr(self.engine, key, val)
        
        # Changing agent count forces a reset
        if key == "num_agents" and not self.is_running:
            self.on_reset()

    def update_redist(self):
        self.engine.redistribution = self.redist_var.get()
        
    def on_model_change(self, event=None):
        self.engine.model_type = self.model_var.get()

    def toggle_sim(self):
        self.is_running = not self.is_running
        self.start_btn.config(text="Pause" if self.is_running else "Start")

    def on_reset(self, event=None):
        """Resets the simulation to time t=0 with current parameters."""
        self.is_running = False
        self.start_btn.config(text="Start")
        
        self.engine.initial_distribution = self.dist_var.get()
        self.engine.model_type = self.model_var.get()
        self.engine.reset()
        
        self.viz_engine.reset()
        self.viz_engine.sync_agents(self.engine.wealth)
        
        self.update_plots()
        self.update_readouts()
        
        self.scrub_slider.config(to=0)
        self.scrub_slider.set(0)

    def on_scrub(self, val):
        """Allows scrubbing through history when paused."""
        if self.is_running:
            return
            
        idx = int(float(val))
        hist = self.engine.history
        
        if idx < len(hist['time']):
            t = hist['time'][idx]
            g = hist['gini'][idx]
            top = hist['top_10'][idx]
            
            self.metrics['time'].set(f"Time: {t:.1f}")
            self.metrics['gini'].set(f"Gini Coefficient: {g:.3f} (History)")
            self.metrics['top10'].set(f"Top 10% Share: {top*100:.1f}% (History)")

    def update_readouts(self):
        """Updates numeric labels on the UI."""
        self.metrics['time'].set(f"Time: {self.engine.time:.1f}")
        self.metrics['gini'].set(f"Gini Coefficient: {self.engine.history['gini'][-1]:.3f}")
        self.metrics['top10'].set(f"Top 10% Share: {self.engine.history['top_10'][-1]*100:.1f}%")
        self.metrics['total'].set(f"Total Wealth: {np.sum(self.engine.wealth):.1f}")

    def update_plots(self):
        """Redraws matplotlib figures efficiently."""
        # 1. Wealth Histogram
        self.ax_hist.clear()
        wealth = self.engine.wealth
        
        if len(wealth) > 0:
            # Dynamically size bins based on maximum wealth
            max_val = max(np.max(wealth), 200)
            bins = np.linspace(0, max_val, 50)
            
            self.ax_hist.hist(wealth, bins=bins, color='skyblue', edgecolor='black', alpha=0.7)
            self.ax_hist.axvline(np.mean(wealth), color='red', linestyle='dashed', linewidth=1.5, label=f'Mean: {np.mean(wealth):.1f}')
            self.ax_hist.axvline(np.median(wealth), color='green', linestyle='dashed', linewidth=1.5, label=f'Median: {np.median(wealth):.1f}')
            self.ax_hist.legend()
            
        self.ax_hist.set_title("Wealth Distribution")
        self.ax_hist.set_xlabel("Wealth")
        self.ax_hist.set_ylabel("Number of Agents")
        
        # 2. Gini Plot over Time
        self.ax_gini.clear()
        hist = self.engine.history
        
        self.ax_gini.plot(hist['time'], hist['gini'], color='purple', label='Gini Coefficient')
        self.ax_gini.set_title("Inequality (Gini) over Time")
        self.ax_gini.set_xlabel("Time")
        self.ax_gini.set_ylabel("Gini Coefficient")
        self.ax_gini.set_ylim(-0.05, 1.05)
        self.ax_gini.grid(True, alpha=0.3)
        
        self.canvas_plot.draw()

    def update_loop(self):
        """The main periodic callback running the simulation and UI updates."""
        if self.is_running:
            # Execute multiple engine steps per visual frame to accelerate simulation
            steps = int(self.speed_slider.get())
            for _ in range(steps):
                self.engine.step()
                
            # Sync states visually
            self.viz_engine.sync_agents(self.engine.wealth)
            self.update_plots()
            self.update_readouts()
            
            # Update history scrub slider
            max_idx = max(0, len(self.engine.history['time']) - 1)
            self.scrub_slider.config(to=max_idx)
            self.scrub_slider.set(max_idx)
            
        # Animate agents continuously (even when paused, for UI liveliness)
        self.viz_engine.update_animation()
        
        # Request next frame (~33 FPS)
        self.root.after(30, self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = WealthSimulatorApp(root)
    root.mainloop()
