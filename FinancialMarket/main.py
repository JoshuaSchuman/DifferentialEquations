import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

from market import Market
from analytics import MarketAnalytics
from visuals import AgentVisualizer

class FinancialMarketSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Financial Market Dynamics Lab")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2C3E50")

        # Market state
        self.market = Market()
        self.analytics = MarketAnalytics()
        self.running = False
        self.sim_speed = 50 # ms delay
        
        self.setup_ui()
        self.reset_simulation()

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#34495E", height=50)
        header.pack(side="top", fill="x")
        tk.Label(header, text="Financial Market Dynamics Simulator", font=("Helvetica", 18, "bold"), 
                 bg="#34495E", fg="#ECF0F1").pack(pady=10)

        # Main horizontal split
        main_frame = tk.Frame(self.root, bg="#2C3E50")
        main_frame.pack(side="top", fill="both", expand=True)

        # Left Column: Controls
        self.controls_frame = tk.Frame(main_frame, bg="#2C3E50", width=300)
        self.controls_frame.pack(side="left", fill="y", padx=20, pady=20)
        self.setup_controls()

        # Right Column: Visuals
        self.visuals_frame = tk.Frame(main_frame, bg="#2C3E50")
        self.visuals_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # Agent Canvas (Top Right)
        self.canvas_label = tk.Label(self.visuals_frame, text="Agent Sentiment (Green: Buy | Red: Sell)", 
                                    font=("Helvetica", 10), bg="#2C3E50", fg="#BDC3C7")
        self.canvas_label.pack()
        
        self.agent_canvas = tk.Canvas(self.visuals_frame, width=400, height=250, bg="#1B2631", highlightthickness=0)
        self.agent_canvas.pack(fill="x", pady=5)
        self.agent_viz = AgentVisualizer(self.agent_canvas, width=600, height=250)

        # Plotting Area (Bottom Right)
        self.setup_plots()

    def setup_controls(self):
        # Simulation State Controls
        state_group = tk.LabelFrame(self.controls_frame, text="Simulation Control", bg="#2C3E50", fg="#ECF0F1")
        state_group.pack(fill="x", pady=10)
        
        self.start_btn = tk.Button(state_group, text="START", command=self.toggle_running, bg="#27AE60", fg="white", font=("bold"))
        self.start_btn.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        tk.Button(state_group, text="RESET", command=self.reset_simulation, bg="#C0392B", fg="white", font=("bold")).pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        # Composition Group
        comp_group = tk.LabelFrame(self.controls_frame, text="Agent Composition", bg="#2C3E50", fg="#ECF0F1")
        comp_group.pack(fill="x", pady=10)
        
        self.num_funda = self.create_slider(comp_group, "Fundamentalists", 0, 100, 30)
        self.num_moment = self.create_slider(comp_group, "Momentum Traders", 0, 100, 20)
        self.num_noise = self.create_slider(comp_group, "Noise Traders", 0, 100, 50)
        
        # Behavior Parameters
        param_group = tk.LabelFrame(self.controls_frame, text="Market Behavior", bg="#2C3E50", fg="#ECF0F1")
        param_group.pack(fill="x", pady=10)
        
        self.herding_str = self.create_slider(param_group, "Herding Strength", 0, 0.5, 0.05, resolution=0.01)
        self.market_liq = self.create_slider(param_group, "Price Impact (1/Liq)", 0.01, 1.0, 0.1, resolution=0.01)
        self.ext_noise = self.create_slider(param_group, "External Noise", 0, 0.5, 0.05, resolution=0.01)

        # Shocks
        shock_group = tk.LabelFrame(self.controls_frame, text="Market Shocks", bg="#2C3E50", fg="#ECF0F1")
        shock_group.pack(fill="x", pady=10)
        
        tk.Button(shock_group, text="Positive Value Shock", command=lambda: self.market.apply_shock(20), bg="#2980B9", fg="white").pack(fill="x", pady=2)
        tk.Button(shock_group, text="Negative Value Shock", command=lambda: self.market.apply_shock(-20), bg="#E67E22", fg="white").pack(fill="x", pady=2)

    def create_slider(self, parent, label, min_val, max_val, default, resolution=1):
        frame = tk.Frame(parent, bg="#2C3E50")
        frame.pack(fill="x", padx=5, pady=2)
        tk.Label(frame, text=label, bg="#2C3E50", fg="#ECF0F1", font=("Helvetica", 9)).pack(anchor="w")
        slider = tk.Scale(frame, from_=min_val, to=max_val, orient="horizontal", resolution=resolution, 
                         bg="#2C3E50", fg="#ECF0F1", troughcolor="#34495E", highlightthickness=0)
        slider.set(default)
        slider.pack(fill="x")
        return slider

    def setup_plots(self):
        plt.style.use('dark_background')
        self.fig, (self.ax_price, self.ax_sentiment) = plt.subplots(2, 1, figsize=(6, 5), facecolor="#2C3E50")
        self.fig.tight_layout(pad=3.0)
        
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=self.visuals_frame)
        self.canvas_plot.get_tk_widget().pack(fill="both", expand=True)

        self.price_line, = self.ax_price.plot([], [], color="#3498DB", label="Market Price")
        self.value_line, = self.ax_price.plot([], [], color="#E74C3C", linestyle="--", alpha=0.5, label="Fundamental Value")
        self.ax_price.set_title("Market Price Dynamics", color="#ECF0F1")
        self.ax_price.legend(loc="upper left", fontsize='x-small')

        self.sentiment_line, = self.ax_sentiment.plot([], [], color="#2ECC71", label="Net Sentiment")
        self.ax_sentiment.set_title("Global Agent Sentiment", color="#ECF0F1")
        self.ax_sentiment.set_ylim(-1.1, 1.1)

        self.history_limit = 200
        self.p_hist = []
        self.v_hist = []
        self.s_hist = []

    def toggle_running(self):
        self.running = not self.running
        if self.running:
            self.start_btn.config(text="PAUSE", bg="#F1C40F")
            # Update market composition before starting
            self.sync_params()
            self.update_loop()
        else:
            self.start_btn.config(text="START", bg="#27AE60")

    def sync_params(self):
        """Update market settings from UI sliders."""
        params = {
            'f_anchor': 0.15,
            'm_sens': 2.5,
            'n_level': 0.6
        }
        self.market.herding_strength = self.herding_str.get()
        self.market.liquidity = self.market_liq.get()
        self.market.external_noise = self.ext_noise.get()
        
        # If agent counts changed, repopulate
        current_counts = (self.num_funda.get(), self.num_moment.get(), self.num_noise.get())
        if not hasattr(self, '_last_counts') or self._last_counts != current_counts:
            self.market.add_agents(*current_counts, params)
            self.agent_viz.initialize_agents(self.market.agents)
            self._last_counts = current_counts

    def reset_simulation(self):
        self.running = False
        self.start_btn.config(text="START", bg="#27AE60")
        self.market = Market()
        self.analytics.reset()
        self.p_hist = []
        self.v_hist = []
        self.s_hist = []
        self.sync_params()
        self.update_display(reset_axes=True)

    def update_loop(self):
        if not self.running:
            return
            
        # Step the market
        self.sync_params() # Continuously update params
        state = self.market.update()
        
        # Record history
        self.p_hist.append(state['price'])
        self.v_hist.append(self.market.fundamental_value)
        self.s_hist.append(state['sentiment'])
        
        if len(self.p_hist) > self.history_limit:
            self.p_hist.pop(0)
            self.v_hist.pop(0)
            self.s_hist.pop(0)

        # Update visuals
        self.agent_viz.update(self.market.agents)
        self.update_display()
        
        # Schedule next
        self.root.after(self.sim_speed, self.update_loop)

    def update_display(self, reset_axes=False):
        if not self.p_hist:
            return

        # Update lines
        x = np.arange(len(self.p_hist))
        self.price_line.set_data(x, self.p_hist)
        self.value_line.set_data(x, self.v_hist)
        self.sentiment_line.set_data(x, self.s_hist)

        # Rescale axes
        self.ax_price.relim()
        self.ax_price.autoscale_view()
        self.ax_sentiment.relim()
        self.ax_sentiment.autoscale_view(scaley=False)
        
        self.canvas_plot.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = FinancialMarketSimulator(root)
    root.mainloop()
