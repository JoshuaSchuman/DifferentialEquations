import numpy as np

class HeatEngine:
    """
    Core numerical engine for 2D Heat Diffusion.
    Solves du/dt = alpha * laplacian(u) using Finite Difference (Forward Euler).
    """
    def __init__(self, nx=50, ny=50, alpha=0.5, dx=1.0, dy=1.0):
        self.nx = nx
        self.ny = ny
        self.alpha = alpha
        self.dx = dx
        self.dy = dy
        
        # Temperature field
        self.u = np.zeros((nx, ny))
        
        # Boundary condition type: 'dirichlet', 'neumann', or 'periodic'
        self.bc_type = 'dirichlet'
        self.bc_value = 0.0 
        
        self.dt = 0.1 # Initial placeholder
        self.update_dt()

    def set_resolution(self, nx, ny):
        self.nx = nx
        self.ny = ny
        self.u = np.zeros((nx, ny))
        self.update_dt()

    def update_dt(self, safety_factor=0.2):
        # CFL Condition: dt <= dx^2 / (4 * alpha) for 2D
        # Using a conservative safety factor for stability
        self.dt = safety_factor * (min(self.dx, self.dy)**2) / (4 * max(0.001, self.alpha))

    def reset(self):
        self.u.fill(0.0)

    def inject_heat(self, x_idx, y_idx, radius, intensity):
        """
        Add heat in a circular region around (x_idx, y_idx).
        """
        if not (0 <= x_idx < self.nx and 0 <= y_idx < self.ny):
            return
            
        xx, yy = np.ogrid[:self.nx, :self.ny]
        dist_sq = (xx - x_idx)**2 + (yy - y_idx)**2
        mask = dist_sq <= radius**2
        self.u[mask] += intensity
        self.u = np.clip(self.u, -100, 1000)

    def step(self):
        """
        Perform a single time step of the simulation.
        """
        if self.bc_type == 'periodic':
            laplacian = (
                np.roll(self.u, 1, axis=0) + np.roll(self.u, -1, axis=0) +
                np.roll(self.u, 1, axis=1) + np.roll(self.u, -1, axis=1) -
                4 * self.u
            ) / (self.dx * self.dy)
        else:
            laplacian = np.zeros_like(self.u)
            # Interior update
            laplacian[1:-1, 1:-1] = (
                self.u[2:, 1:-1] + self.u[:-2, 1:-1] +
                self.u[1:-1, 2:] + self.u[1:-1, :-2] -
                4 * self.u[1:-1, 1:-1]
            ) / (self.dx * self.dy)
            
            # Apply boundary logic to edges of Laplacian or U
            if self.bc_type == 'neumann':
                # No flux: edges mimic interior
                self.u[0, :] = self.u[1, :]
                self.u[-1, :] = self.u[-2, :]
                self.u[:, 0] = self.u[:, 1]
                self.u[:, -1] = self.u[:, -2]
            elif self.bc_type == 'dirichlet':
                # Fixed temp
                self.u[0, :] = self.bc_value
                self.u[-1, :] = self.bc_value
                self.u[:, 0] = self.bc_value
                self.u[:, -1] = self.bc_value

        self.u += self.alpha * self.dt * laplacian
        
        # Enforce stability clip
        self.u = np.clip(self.u, -200, 1000)

    def get_stats(self):
        return {
            'avg': np.mean(self.u),
            'max': np.max(self.u),
            'min': np.min(self.u)
        }
