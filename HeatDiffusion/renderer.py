import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.colors as mcolors

class HeatRenderer:
    """
    Handles the heatmap visualization using Matplotlib.
    """
    def __init__(self, parent_frame, nx, ny):
        self.nx = nx
        self.ny = ny
        
        # Setup Figure and Axes
        self.fig, self.ax = plt.subplots(figsize=(6, 6), tight_layout=True)
        self.ax.set_title("2D Temperature Field")
        
        # Colormap from cold to hot
        # Use 'magma' or custom (blue -> yellow -> red)
        self.cmap = plt.get_cmap('magma')
        
        # Initial empty field
        self.im = self.ax.imshow(
            [[0]*ny for _ in range(nx)], 
            cmap=self.cmap, 
            origin='lower', 
            extent=[0, ny, 0, nx],
            vmin=0, 
            vmax=100
        )
        
        self.cbar = self.fig.colorbar(self.im, ax=self.ax, label="Temperature (°C)")
        
        # Canvas for Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def update(self, u_field, vmin=None, vmax=None):
        """
        Refresh the heatmap display with new temperature data.
        """
        self.im.set_data(u_field)
        
        if vmin is not None and vmax is not None:
            self.im.set_clim(vmin=vmin, vmax=vmax)
        
        self.canvas.draw_idle()

    def set_grid_lines(self, visible):
        """Toggle grid visibility."""
        self.ax.grid(visible, color='white', linestyle='--', alpha=0.3)
        self.canvas.draw_idle()

    def reset(self, nx, ny):
        """Reset the extent and initial data for a new resolution."""
        self.nx = nx
        self.ny = ny
        self.im.set_extent([0, ny, 0, nx])
        self.im.set_data([[0]*ny for _ in range(nx)])
        self.canvas.draw_idle()
