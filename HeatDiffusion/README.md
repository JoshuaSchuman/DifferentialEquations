# Interactive 2D Heat Diffusion Laboratory

A high-performance, real-time interactive simulation of thermal conduction in a 2D plane. This tool allows users to explore the physical principles of heat diffusion through direct interaction and live visualization.

## 🌡️ The Physics of Diffusion

This simulator solves the **2D Heat Equation**, a partial differential equation (PDE) that describes how temperature distributes in a given region over time:

$$\frac{\partial u}{\partial t} = \alpha \nabla^2 u$$

Where:
- $u(x, y, t)$ is the temperature field.
- $\alpha$ is the **thermal diffusivity** of the material (how "fast" heat spreads).
- $\nabla^2$ is the **Laplacian operator**, representing the second spatial derivative (the local curvature of the temperature field).

## 🔢 Numerical Implementation

The simulation uses the **Finite Difference Method** with a **Forward Euler** time-stepping scheme (Explicit Method).

### Discretization
Space is discretized into a 2D grid of size $N \times N$. The Laplacian is approximated using a 5-point stencil:
$$\nabla^2 u_{i,j} \approx \frac{u_{i+1,j} + u_{i-1,j} + u_{i,j+1} + u_{i,j-1} - 4u_{i,j}}{\Delta x^2}$$

### Stability
To ensure numerical stability, the time step $\Delta t$ is dynamically calculated based on the **CFL (Courant-Friedrichs-Lewy) condition**:
$$\Delta t \leq \frac{\Delta x^2}{4\alpha}$$
Exceeding this limit would cause the simulation to diverge (blow up).

## 🎮 Features

- **Real-time Interaction:** Left-click and drag to "paint" heat onto the surface. Right-click to cool areas down.
- **Adjustable Parameters:**
  - **Thermal Diffusivity ($\alpha$):** Change material properties on the fly.
  - **Heat Intensity:** Control how much energy is injected by the brush.
  - **Brush Radius:** Change the size of the heat source.
  - **Simulation Speed:** Adjust how many numerical steps occur per visual frame.
- **Selectable Boundary Conditions:**
  - **Fixed (Dirichlet):** Edges are kept at a constant cold temperature (like a heat sink).
  - **Insulated (Neumann):** No heat escapes through the edges (perfect insulation).
  - **Periodic:** Heat leaving one side enters the opposite side (toroidal topology).
- **Live Analytics:**
  - **Average Temperature:** Monitor the total energy in the system.
  - **Temperature Distribution:** View a histogram of the current temperature state.

## 🚀 Installation & Usage

### Prerequisites
- Python 3.8+
- NumPy
- Matplotlib
- Tkinter (usually comes with Python)

### Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the simulator:
   ```bash
   python main.py
   ```

## 🏗️ Architecture

- `engine.py`: The core numerical solver (NumPy-vectorized).
- `renderer.py`: Handles the Matplotlib heatmap visualization.
- `interaction.py`: Manages mouse events and grid mapping.
- `analytics.py`: Generates live plots for physical metrics.
- `main.py`: Coordinates the UI and the simulation loop.

---
*Developed as a standalone scientific visualization tool.*
