# 📊 Differential Equations Population Simulator

An interactive, real-time population dynamics simulator that solves Ordinary Differential Equations (ODEs) using high-order numerical methods. This tool allows users to visualize biological models like Predator-Prey relationships through both mathematical plots and agent-based animations.

---

## 🚀 Features

- **Multiple Models**: Choose between Exponential Growth, Logistic Growth, and Lotka-Volterra Predator-Prey models.
- **Custom ODE Editor**: Input your own differential equations and environment variables directly into the GUI.
- **Real-time Visualization**:
  - **Dynamic Canvas**: An agent-based animation where "prey" (green) and "predators" (red) interact in a 2D space.
  - **Live Plotting**: Time-series and Phase-space plots updated in real-time using Matplotlib.
- **Interactive Controls**: Adjust growth rates, carrying capacities, and predation efficiency on the fly.
- **Advanced Simulation**:
  - **RK4 Integrator**: Uses the Runge-Kutta 4th Order method for high numerical accuracy.
  - **Stochastic Noise**: Toggle environmental randomness to see how it affects population stability.
  - **Time Scrubbing**: Pause the simulation and scrub through the history to analyze specific events.

---

## 🛠️ Getting Started

### Prerequisites
- Python 3.x
- NumPy
- Matplotlib
- Tkinter (usually bundled with Python)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/DifferentialEquations.git
   cd DifferentialEquations
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

---

## 🧠 How It Works (Program Workflow)

The program is architected into three primary layers: **UI/Controller**, **Simulation Engine**, and **Visualization Engine**.

### 1. Initialization Phase
- `main.py` initializes the `PopulationSimulatorApp`.
- The `SimulationEngine` is instantiated to handle the mathematical state.
- The `VisualizationEngine` is linked to the Tkinter Canvas to handle the dot-based animation.

### 2. The Simulation Loop (`update_loop`)
The program runs a recursive loop every ~30ms:
1. **Math Update**: The `SimulationEngine` performs $N$ steps of numerical integration (scaled by the "Sim Speed" slider) using the **Runge-Kutta (RK4)** method.
2. **State Sync**: The new population counts ($P$ and $H$) are passed to the `VisualizationEngine`.
3. **Agent Sync**: The `VisualizationEngine` adds or removes "dots" on the canvas to match the current population counts.
4. **Animation Update**: Every agent (dot) calculates its next position based on simple physics (velocity + bouncing) and "hunting" logic (predators move toward prey).
5. **Plot Rendering**: Matplotlib updates the Time-series and Phase-space graphs with the latest data points from the simulation history.

### 3. User Interaction
- **Parameter Adjustments**: Moving a slider updates the `SimulationEngine` parameters instantly without resetting the simulation.
- **Model Switching**: Changing the model resets the state and switches the derivative functions used by the integrator.
- **Custom Equations**: When the "Custom" model is selected, the engine uses Python's `eval()` with a safe context to parse user-defined strings into mathematical logic.

---

## 📁 Project Organization

```text
DifferentialEquations/
├── main.py            # Entry point; manages the Tkinter GUI and orchestration logic.
├── simulation.py      # The mathematical core; contains RK4 integrator and ODE models.
├── canvas.py          # The animation engine; handles agent-based rendering on the UI.
├── requirements.txt   # List of necessary Python libraries.
└── .diffEQ/           # (Internal) Configuration or cached data.
```

### Component Details
- **`main.py`**: Acts as the "Controller". It handles layout, event binding for sliders/buttons, and the main `after()` loop that drives the app.
- **`simulation.py`**: Acts as the "Model". It stores the state ($P, H, t$) and history. It's agnostic of the UI and only cares about solving equations.
- **`canvas.py`**: Acts as the "View". It manages the lifecycle of Tkinter canvas objects, ensuring hundreds of dots can be moved efficiently while simulating basic "behavior".

---

## 🧪 Mathematical Models

### Predator-Prey (Lotka-Volterra)
The default complex model follows:
$$\frac{dP}{dt} = rP(1 - \frac{P}{K}) - aPH$$
$$\frac{dH}{dt} = bPH - dH$$
*Where:*
- $r$: Growth rate
- $K$: Carrying capacity
- $a$: Predation rate
- $b$: Predator efficiency
- $d$: Predator death rate
