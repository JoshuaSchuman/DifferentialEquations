import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random
from simulation import SimulationEngine
from canvas import VisualizationEngine

class PopulationSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Differential Equations Population Simulator")
        self.root.geometry("1400x900")
        
        self.engine = SimulationEngine()
        self.is_running = False
        self.sim_speed = 1.0
        
        self.setup_ui()
        
        # Initialize visualization engine
        self.viz_engine = VisualizationEngine(self.anim_canvas, 600, 600)
        self.viz_engine.sync_population(self.engine.P, self.engine.H)
        
        self.update_loop()

    def setup_ui(self):
        # Main container with three panels
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # --- Left Panel: Controls ---
        self.left_panel = ttk.Frame(self.main_paned, padding=10, width=300)
        self.main_paned.add(self.left_panel, weight=1)
        
        ttk.Label(self.left_panel, text="Simulation Controls", font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Model Selection
        ttk.Label(self.left_panel, text="Model:").pack(anchor=tk.W)
        self.model_var = tk.StringVar(value="Predator-Prey")
        model_dropdown = ttk.Combobox(self.left_panel, textvariable=self.model_var, 
                                      values=["Exponential", "Logistic", "Predator-Prey", "Custom"])
        model_dropdown.pack(fill=tk.X, pady=5)
        model_dropdown.bind("<<ComboboxSelected>>", self.on_model_change)
        
        # --- Custom Equation Editor (Hidden by Default) ---
        self.custom_frame = ttk.LabelFrame(self.left_panel, text="Custom ODE Editor", padding=5)
        # We pack/unpack this based on model selection
        
        ttk.Label(self.custom_frame, text="dP/dt =").pack(anchor=tk.W)
        self.dpdt_entry = ttk.Entry(self.custom_frame)
        self.dpdt_entry.insert(0, "r * P * (1 - P/K) - a * P * H")
        self.dpdt_entry.pack(fill=tk.X, pady=2)
        self.dpdt_entry.bind("<KeyRelease>", self.update_custom_eqs)
        
        ttk.Label(self.custom_frame, text="dH/dt =").pack(anchor=tk.W)
        self.dhdt_entry = ttk.Entry(self.custom_frame)
        self.dhdt_entry.insert(0, "b * P * H - d * H")
        self.dhdt_entry.pack(fill=tk.X, pady=2)
        self.dhdt_entry.bind("<KeyRelease>", self.update_custom_eqs)
        
        ttk.Label(self.custom_frame, text="Environment Variables (e.g., r=1, K=100)").pack(anchor=tk.W)
        self.env_entry = ttk.Entry(self.custom_frame)
        self.env_entry.pack(fill=tk.X, pady=2)
        self.env_entry.bind("<KeyRelease>", self.update_env_vars)
        
        # Parameters
        self.params_frame = ttk.LabelFrame(self.left_panel, text="Parameters", padding=5)
        self.params_frame.pack(fill=tk.X, pady=10)
        
        self.sliders = {}
        self.param_specs = [
            ("P0", "Initial Prey", 0, 200, 40),
            ("H0", "Initial Predator", 0, 100, 10),
            ("r", "Growth Rate (r)", 0, 5, 1.0),
            ("K", "Carrying Cap (K)", 10, 500, 100),
            ("a", "Predation Rate (a)", 0, 1, 0.1),
            ("b", "Efficiency (b)", 0, 1, 0.05),
            ("d", "Death Rate (d)", 0, 2, 0.5)
        ]
        
        for key, label, low, high, default in self.param_specs:
            frame = ttk.Frame(self.params_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=label).pack(side=tk.LEFT)
            val_label = ttk.Label(frame, text=f"{default:.2f}")
            val_label.pack(side=tk.RIGHT)
            
            slider = ttk.Scale(self.params_frame, from_=low, to=high, orient=tk.HORIZONTAL,
                               command=lambda v, k=key, l=val_label: self.update_param(k, v, l))
            slider.set(default)
            slider.pack(fill=tk.X)
            self.sliders[key] = (slider, val_label)

        # Buttons
        btn_frame = ttk.Frame(self.left_panel)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.toggle_sim)
        self.start_btn.pack(side=tk.LEFT, expand=True, padx=2)
        
        ttk.Button(btn_frame, text="Reset", command=self.reset_sim).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(btn_frame, text="Randomize", command=self.randomize_params).pack(side=tk.LEFT, expand=True, padx=2)
        
        # Simulation Speed
        speed_header = ttk.Frame(self.left_panel)
        speed_header.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(speed_header, text="Sim Speed:").pack(side=tk.LEFT)
        self.speed_label = ttk.Label(speed_header, text="1")
        self.speed_label.pack(side=tk.RIGHT)
        
        self.speed_slider = ttk.Scale(self.left_panel, from_=1, to=10, orient=tk.HORIZONTAL,
                                      command=lambda v: self.speed_label.config(text=str(int(float(v)))))
        self.speed_slider.set(1)
        self.speed_slider.pack(fill=tk.X)
        
        # Toggles
        self.noise_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.left_panel, text="Stochastic Noise", variable=self.noise_var, 
                        command=self.update_noise).pack(anchor=tk.W, pady=5)
        
        # --- Center Panel: Visualization ---
        self.center_panel = ttk.Frame(self.main_paned, padding=5)
        self.main_paned.add(self.center_panel, weight=2)
        
        ttk.Label(self.center_panel, text="World Visualization", font=('Helvetica', 12)).pack()
        self.anim_canvas = tk.Canvas(self.center_panel, width=600, height=600, bg="black", highlightthickness=0)
        self.anim_canvas.pack(pady=10)
        
        # Equation Display
        self.eq_frame = ttk.LabelFrame(self.center_panel, text="Current Model Equations", padding=10)
        self.eq_frame.pack(fill=tk.X, pady=10)
        self.eq_label = ttk.Label(self.eq_frame, text="", font=('Courier', 12), justify=tk.LEFT)
        self.eq_label.pack()
        self.update_equation_text()

        # --- Right Panel: Graphs and Data ---
        self.right_panel = ttk.Frame(self.main_paned, padding=10)
        self.main_paned.add(self.right_panel, weight=2)
        
        # Matplotlib Figures
        self.fig, (self.ax_time, self.ax_phase) = plt.subplots(2, 1, figsize=(6, 8))
        self.fig.tight_layout(pad=3.0)
        
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=self.right_panel)
        self.canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Numerical Readouts
        self.readout_frame = ttk.LabelFrame(self.right_panel, text="Numerical Readouts", padding=10)
        self.readout_frame.pack(fill=tk.X, pady=5)
        
        self.readout_vars = {
            'P': tk.StringVar(value="Prey (P): 0.00"),
            'H': tk.StringVar(value="Predator (H): 0.00"),
            'dPdt': tk.StringVar(value="dP/dt: 0.00"),
            'dHdt': tk.StringVar(value="dH/dt: 0.00"),
            't': tk.StringVar(value="Time (t): 0.00")
        }
        
        for var in self.readout_vars.values():
            ttk.Label(self.readout_frame, textvariable=var, font=('Courier', 10)).pack(anchor=tk.W)

        # Scrub Slider
        self.scrub_frame = ttk.LabelFrame(self.right_panel, text="Time Scrub (History)", padding=10)
        self.scrub_frame.pack(fill=tk.X, pady=5)
        
        self.scrub_slider = ttk.Scale(self.scrub_frame, from_=0, to=0, orient=tk.HORIZONTAL, 
                                      command=self.on_scrub)
        self.scrub_slider.pack(fill=tk.X)

    def update_param(self, key, val, label):
        val = float(val)
        label.config(text=f"{val:.2f}")
        setattr(self.engine, key, val)
        if key in ["P0", "H0"] and not self.is_running:
            self.reset_sim()

    def on_model_change(self, event):
        model = self.model_var.get()
        self.engine.model = model
        
        # Show/Hide custom editor
        if model == "Custom":
            # Re-pack to ensure it appears below the model dropdown
            self.custom_frame.pack(fill=tk.X, pady=5)
            # Move it up in the pack order if needed, but since it's the first thing 
            # after the dropdown it should be fine.
        else:
            self.custom_frame.pack_forget()
            
        self.update_equation_text()
        self.reset_sim()

    def update_custom_eqs(self, event=None):
        self.engine.custom_dPdt = self.dpdt_entry.get()
        self.engine.custom_dHdt = self.dhdt_entry.get()
        self.update_equation_text()

    def update_env_vars(self, event=None):
        raw = self.env_entry.get()
        new_vars = {}
        try:
            # Flexible parsing: r=1 K=100 or r:1, K:100
            import re
            pairs = re.findall(r'([a-zA-Z_]\w*)\s*[=:]\s*([-+]?\d*\.?\d+)', raw)
            for k, v in pairs:
                new_vars[k] = float(v)
            self.engine.env_vars = new_vars
        except:
            pass 

    def update_equation_text(self):
        model = self.model_var.get()
        if model == "Exponential":
            txt = "dP/dt = r * P\n(Simple growth without limits)"
        elif model == "Logistic":
            txt = "dP/dt = r * P * (1 - P/K)\n(Growth limited by carrying capacity K)"
        elif model == "Predator-Prey":
            txt = "dP/dt = r*P*(1-P/K) - a*P*H\ndH/dt = b*P*H - d*H\n(Lotka-Volterra with competition)"
        else:
            txt = f"dP/dt = {self.engine.custom_dPdt}\ndH/dt = {self.engine.custom_dHdt}\n(User-defined Model)"
        self.eq_label.config(text=txt)

    def update_noise(self):
        self.engine.noise = self.noise_var.get()

    def toggle_sim(self):
        self.is_running = not self.is_running
        self.start_btn.config(text="Pause" if self.is_running else "Start")

    def reset_sim(self):
        self.is_running = False
        self.start_btn.config(text="Start")
        self.engine.reset()
        self.viz_engine.reset()
        self.viz_engine.sync_population(self.engine.P, self.engine.H)
        self.update_plots()
        self.update_readouts(0, 0)
        self.scrub_slider.config(to=0)
        self.scrub_slider.set(0)

    def randomize_params(self):
        for key, _, low, high, _ in self.param_specs:
            val = random.uniform(low, high)
            self.sliders[key][0].set(val)
            self.sliders[key][1].config(text=f"{val:.2f}")
            setattr(self.engine, key, val)
        self.reset_sim()

    def on_scrub(self, val):
        if self.is_running:
            return
        
        idx = int(float(val))
        hist = self.engine.history
        if idx < len(hist['t']):
            self.engine.P = hist['P'][idx]
            self.engine.H = hist['H'][idx]
            self.engine.t = hist['t'][idx]
            
            # Sync but don't clear history
            self.viz_engine.sync_population(self.engine.P, self.engine.H)
            self.update_readouts(0, 0) # dPdt/dHdt not saved in history

    def update_readouts(self, dpdt, dhdt):
        self.readout_vars['P'].set(f"Prey (P): {self.engine.P:.2f}")
        self.readout_vars['H'].set(f"Predator (H): {self.engine.H:.2f}")
        self.readout_vars['dPdt'].set(f"dP/dt: {dpdt:.2f}")
        self.readout_vars['dHdt'].set(f"dH/dt: {dhdt:.2f}")
        self.readout_vars['t'].set(f"Time (t): {self.engine.t:.2f}")

    def update_plots(self):
        self.ax_time.clear()
        self.ax_phase.clear()
        
        hist = self.engine.history
        self.ax_time.plot(hist['t'], hist['P'], 'g-', label='Prey')
        if self.engine.model == "Predator-Prey":
            self.ax_time.plot(hist['t'], hist['H'], 'r-', label='Predator')
        
        self.ax_time.set_title("Population vs Time")
        self.ax_time.set_xlabel("Time")
        self.ax_time.set_ylabel("Population")
        self.ax_time.legend()
        
        if self.engine.model == "Predator-Prey":
            self.ax_phase.plot(hist['P'], hist['H'], 'b-')
            self.ax_phase.set_title("Phase Plot (Predator vs Prey)")
            self.ax_phase.set_xlabel("Prey")
            self.ax_phase.set_ylabel("Predator")
        
        self.canvas_plot.draw()

    def update_loop(self):
        if self.is_running:
            # Scale simulation steps by speed
            steps = int(self.speed_slider.get())
            dpdt, dhdt = 0, 0
            for _ in range(steps):
                p, h, t = self.engine.step()
                dpdt, dhdt = self.engine.get_rates()
            
            self.viz_engine.sync_population(self.engine.P, self.engine.H)
            self.update_plots()
            self.update_readouts(dpdt, dhdt)
            
            # Update scrub slider range
            self.scrub_slider.config(to=len(self.engine.history['t']) - 1)
            self.scrub_slider.set(len(self.engine.history['t']) - 1)
        
        self.viz_engine.update_animation()
        
        # 30 ms interval for ~33 FPS
        self.root.after(30, self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = PopulationSimulatorApp(root)
    root.mainloop()
