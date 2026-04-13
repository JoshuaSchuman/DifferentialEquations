# Wealth Inequality Dynamics Simulator

An interactive, agent-based economic modeling tool designed to explore the mechanics of wealth distribution and the emergence of macroscopic inequality from microscopic transactions. 

This application functions as a "mini economic laboratory," providing users with real-time visualization, dynamic parameter adjustment, and continuous mathematical plotting to intuitively understand complex statistical mechanics phenomena, such as the Yard-Sale Model.

---

## 🎯 Project Overview

In free-market models where agents engage in random, symmetrical trades, wealth does not typically distribute normally. Instead, statistical mechanics predict that without external redistribution or saving behaviors, the economy tends toward an oligarchic state where a single agent holds all wealth—a phenomenon known as the "Yard-Sale Model."

This educational simulator allows users to witness this phenomenon unfold in real-time, test the efficacy of interventions (like taxation and redistribution), and explore how individual "saving propensity" changes macroscopic inequality. 

---

## 🚀 Features

- **Agent-Based Modeling:** Simulate up to 1,500 independent economic agents interacting concurrently.
- **Real-Time Visualizations:** Watch the economy evolve on a 2D canvas where agent size and color indicate relative wealth.
- **Dynamic Analytical Plots:** Real-time generation of the Wealth Histogram and the Gini Coefficient over time.
- **Multiple Exchange Models:**
  - *Random Exchange*: Agents risk all their wealth in random transactions.
  - *Saving Propensity*: Agents only risk a certain percentage of their wealth, acting as a stabilizing force against absolute inequality.
- **Global Macro Dynamics:** Introduce exogenous continuous variables like exponential economic growth and stochastic market noise.
- **Policy Testing:** Toggle taxation and wealth redistribution to observe their real-time impact on the Gini coefficient.
- **Historical Scrubbing:** Pause the simulation and scrub backward through time to analyze the exact moment inequality accelerated.

---

## 🛠️ Installation & Usage

### Prerequisites
- Python 3.8+
- Tkinter (usually bundled with standard Python distributions)

### Setup
1. Clone this repository or download the source code.
2. Navigate to the project directory:
   ```bash
   cd WealthInequality
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the simulation:
   ```bash
   python main.py
   ```

---

## 🧠 Architecture & Workflow

The application is structured into cleanly decoupled, professional-grade layers:

1. **`main.py` (Controller & UI Layer)**: Utilizes Tkinter to construct a three-panel interface. It orchestrates the real-time parameter binding, manages the simulation loop, and binds the Matplotlib canvases.
2. **`simulation.py` (Model Layer)**: A pure mathematical engine that processes the `N` concurrent agents. It handles the stochastic pairwise matching of agents and applies continuous Euler integration for global ODEs.
3. **`visualization.py` (View Layer)**: Manages the high-performance Tkinter Canvas. Agents are updated via a custom Brownian-motion algorithm to give the economy a visually "alive" feeling.
4. **`metrics.py` (Analytics Layer)**: A stateless module optimized with NumPy to compute complex statistical formulas (like the Gini coefficient) in real-time without bottlenecking the UI.

---

## 📐 Mathematical Models

### 1. The Exchange Mechanisms

During each timestep $dt$, randomly paired agents interact. Let $w_i$ and $w_j$ be the wealth of agent $i$ and agent $j$. Let $\lambda$ be the saving rate (fraction of wealth protected from trade).

The "stake" each agent puts up is:
$$\text{Stake}_i = w_i (1 - \lambda)$$
$$\text{Stake}_j = w_j (1 - \lambda)$$

The total staked pool is $S = \text{Stake}_i + \text{Stake}_j$. A random variable $\epsilon \in [0, 1]$ determines the split of the pool.
The updated wealth becomes:
$$w_i(t+1) = w_i(t) - \text{Stake}_i + S \cdot \epsilon$$
$$w_j(t+1) = w_j(t) - \text{Stake}_j + S \cdot (1 - \epsilon)$$

*If $\lambda = 0$, this acts as a pure random "Yard-Sale" exchange, rapidly converging to an oligarchy (Gini $\to 1$).*

### 2. Global Continuous Dynamics

In addition to discrete trades, the engine integrates continuous macroeconomic variables:
$$\frac{dw}{dt} = r w + \mathcal{N}(0, \sigma)$$
Where:
- $r$ is the exogenous growth rate.
- $\mathcal{N}$ represents additive stochastic market noise, scaled by $\sigma$.

Taxes ($T$) are applied discretely per step and optionally redistributed equally among all $N$ agents:
$$w_i \gets w_i(1 - T) + \frac{\sum_{k=1}^N w_k T}{N}$$

---

## 📊 Inequality Metrics

### Gini Coefficient
The Gini Coefficient ($G$) is the standard economic measurement of inequality. 
- $G = 0.0$ implies perfect equality (everyone has the exact same wealth).
- $G = 1.0$ implies absolute inequality (one person has everything).

The simulation computes this in real-time using the formula:
$$G = \frac{\sum_{i=1}^n \sum_{j=1}^n |w_i - w_j|}{2n \sum_{i=1}^n w_i}$$
*(Optimized in code via array sorting and weighted indices).*

### Top 10% Wealth Share
A more tangible metric. It computes the sum of the wealth of the wealthiest 10% of agents and divides it by the total global wealth. In highly unequal scenarios, this metric quickly approaches $99.9\%$.