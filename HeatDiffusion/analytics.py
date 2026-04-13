import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class AnalyticsTracker:
    """
    Handles live plots of simulation metrics (average temperature, etc.).
    """
    def __init__(self, parent_frame):
        # Two subplots: Time series and Histogram
        self.fig, (self.ax_time, self.ax_hist) = plt.subplots(
            2, 1, figsize=(4, 6), tight_layout=True
        )
        
        # Time series data
        self.history = []
        self.max_history = 200
        self.line_time, = self.ax_time.plot([], [], 'r-')
        self.ax_time.set_title("Avg Temperature over Time")
        self.ax_time.set_xlabel("Steps")
        self.ax_time.set_ylabel("Temp (°C)")
        
        # Histogram data
        self.bins = np.linspace(0, 100, 20)
        self.bars = self.ax_hist.bar(self.bins[:-1], np.zeros(len(self.bins)-1), width=5)
        self.ax_hist.set_title("Temperature Distribution")
        self.ax_hist.set_xlabel("Temp (°C)")
        self.ax_hist.set_ylabel("Counts")
        
        # Canvas for Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def update(self, u_field, stats):
        """Update the metrics plots."""
        # 1. Update Time Series
        self.history.append(stats['avg'])
        if len(self.history) > self.max_history:
            self.history.pop(0)
            
        self.line_time.set_data(range(len(self.history)), self.history)
        self.ax_time.set_xlim(0, max(10, len(self.history)))
        if self.history:
            self.ax_time.set_ylim(min(self.history) - 5, max(self.history) + 5)
            
        # 2. Update Histogram
        counts, _ = np.histogram(u_field, bins=self.bins)
        for rect, h in zip(self.bars, counts):
            rect.set_height(h)
        self.ax_hist.set_ylim(0, max(100, max(counts) * 1.1))
            
        self.canvas.draw_idle()

    def reset(self):
        """Reset the history."""
        self.history = []
        self.line_time.set_data([], [])
        for rect in self.bars:
            rect.set_height(0)
        self.canvas.draw_idle()
