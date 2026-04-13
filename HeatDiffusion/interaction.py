class InteractionHandler:
    """
    Handles user interaction with the heatmap (clicks/drags to inject heat).
    """
    def __init__(self, renderer, engine, heat_params):
        """
        :param heat_params: A dictionary with 'radius' and 'intensity'
        """
        self.renderer = renderer
        self.engine = engine
        self.heat_params = heat_params
        self.is_dragging = False
        
        # Connect Matplotlib event handlers
        self.cid_press = renderer.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_release = renderer.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = renderer.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        """Called when a mouse button is pressed."""
        if event.inaxes != self.renderer.ax:
            return
            
        self.is_dragging = True
        self._inject_from_event(event)

    def on_release(self, event):
        """Called when a mouse button is released."""
        self.is_dragging = False

    def on_motion(self, event):
        """Called when mouse is moved."""
        if self.is_dragging and event.inaxes == self.renderer.ax:
            self._inject_from_event(event)

    def _inject_from_event(self, event):
        """Determine grid coordinate from axes click and tell engine to inject heat."""
        # event.xdata/ydata are in axes coords, which we matched to grid indices
        # via the 'extent' in imshow.
        # extent=[0, ny, 0, nx] -> imshow maps data indices [i, j] appropriately
        
        # Grid indices from axes coords
        # j (col) = xdata, i (row) = ydata
        j = int(round(event.xdata)) if event.xdata is not None else -1
        i = int(round(event.ydata)) if event.ydata is not None else -1
        
        if 0 <= i < self.engine.nx and 0 <= j < self.engine.ny:
            # Right-click (button 3) for 'cooling' (negative heat)
            intensity_multiplier = 1.0 if event.button == 1 else -1.0
            
            self.engine.inject_heat(
                i, j, 
                radius=self.heat_params.get('radius', 2), 
                intensity=self.heat_params.get('intensity', 10) * intensity_multiplier
            )
            # Force update for immediate feedback
            self.renderer.update(self.engine.u)

    def disconnect(self):
        """Clean up connections if needed."""
        self.renderer.fig.canvas.mpl_disconnect(self.cid_press)
        self.renderer.fig.canvas.mpl_disconnect(self.cid_release)
        self.renderer.fig.canvas.mpl_disconnect(self.cid_motion)
