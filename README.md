# Differential Equations Experimental Laboratory

A collection of interactive, real-time simulators designed to analyze and visualize complex systems governed by differential equations. This repository serves as an experimental workbench for exploring mathematical models across various domains, including physics, biology, finance, and sociology.

> **Status:** ⚠️ This project is an ongoing experimental collection. New models and numerical methods are added as they are developed.

---

## 🧪 Included Models

The repository is organized into specialized laboratories, each focusing on a distinct class of differential equations:

### 1. [Heat Diffusion Lab](./HeatDiffusion)
- **Equation Type:** Partial Differential Equations (PDEs).
- **Core Model:** 2D Heat Equation ($\frac{\partial u}{\partial t} = \alpha \nabla^2 u$).
- **Features:** Interactive heat "painting," selectable boundary conditions (Dirichlet, Neumann, Periodic), and real-time thermal gradient visualization.

### 2. [Population Dynamics Lab](./PredatorPrey)
- **Equation Type:** Ordinary Differential Equations (ODEs).
- **Core Model:** Lotka-Volterra Predator-Prey models.
- **Features:** RK4 numerical integration, agent-based population animations, and phase-space analysis.

### 3. [Financial Market Lab](./FinancialMarket)
- **Equation Type:** Stochastic Differential Equations (SDEs) / Agent-Based Modeling.
- **Core Model:** Price formation based on excess demand and behavioral heuristics.
- **Features:** Heterogeneous agent strategies (Fundamentalist, Momentum, Noise), market sentiment tracking, and volatility clustering analysis.

### 4. [Wealth Inequality Lab](./WealthInequality)
- **Equation Type:** Kinetic Exchange Models / Finite Difference equations.
- **Core Model:** Yard-Sale model and redistribution dynamics.
- **Features:** Gini coefficient tracking, Lorenz curve visualization, and redistribution policy testing.

---

## 🚀 Getting Started

Each model is designed to be self-contained and easy to run.

### Prerequisites
- **Python 3.8+**
- **NumPy**
- **Matplotlib**
- **Tkinter** (usually included with standard Python installations)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/DifferentialEquations.git
   cd DifferentialEquations
   ```
2. Install dependencies for all models:
   ```bash
   pip install -r HeatDiffusion/requirements.txt
   # (Note: Most models share the same core requirements)
   ```

### Running a Simulation
Navigate to the directory of the model you wish to explore and run the `main.py` script:
```bash
# Example: Running the Heat Diffusion Simulator
cd HeatDiffusion
python main.py
```

---

## 🧠 Numerical Methods Employed

This project utilizes various numerical approaches to solve the underlying equations:
- **Finite Difference Method (FDM):** Used for spatial discretization in the Heat Equation.
- **Runge-Kutta 4th Order (RK4):** High-accuracy time-stepping for population ODEs.
- **Forward Euler:** Efficient explicit updates for real-time interaction.
- **Agent-Based Simulation (ABS):** For emergent phenomena in financial and social models.

---

## 🛠️ Roadmap
- [ ] Add **Reaction-Diffusion** systems (Turing patterns).
- [ ] Implement **Navier-Stokes** simplified fluid solver.
- [ ] Add **Wave Equation** 1D/2D visualization.
- [ ] Integrate **Custom ODE Parser** for user-defined equations.

---
*Created as a personal laboratory for computational physics and numerical analysis.*
