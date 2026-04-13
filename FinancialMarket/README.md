# Financial Market Dynamics Lab

An interactive, agent-based financial market simulator designed to explore emergent market phenomena like bubbles, crashes, herding, and volatility clustering.

## 🌟 Overview

This simulator models a financial market as a collection of heterogeneous trading agents. Unlike traditional models that assume perfectly rational actors, this lab allows you to experiment with behavioral biases and different trading strategies to see how they influence price discovery and market stability.

## 🚀 Features

- **Heterogeneous Agents**:
    - **Fundamentalists**: Trade based on the gap between price and intrinsic value.
    - **Momentum Traders**: Follow trends, buying when prices rise and selling when they fall.
    - **Noise Traders**: Add liquidity and unpredictable volatility to the system.
- **Emergent Dynamics**: Watch as herding behavior and momentum create speculative bubbles and sudden crashes.
- **Interactive Controls**:
    - Adjust agent composition in real-time.
    - Modify market liquidity and herding strength.
    - Trigger "Market Shocks" (sudden changes in fundamental value) to test resilience.
- **Live Visualizations**:
    - **Price Chart**: Real-time price vs. fundamental value.
    - **Sentiment Index**: Aggregate bullishness/bearishness of the market.
    - **Agent Activity**: A particle system showing individual agent stances (Green: Buying, Red: Selling).

## 🛠️ Installation

1. Ensure you have Python 3.8+ installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 How to Run

Execute the main script:
```bash
python main.py
```

## 🧠 Core Modeling Concepts

### Price Formation
The market price updates based on **Excess Demand**. 
If total buy orders exceed sell orders, the price rises proportional to the "Price Impact" (the inverse of liquidity).
$$\Delta P = \alpha \cdot (D_{buy} - D_{sell}) + \epsilon$$

### Agent Strategies
- **Fundamentalist**: $Demand \propto (V_{fundamental} - P_{market})$
- **Momentum**: $Demand \propto (P_{t} - P_{t-1})$
- **Herding**: Agents' bias is amplified by the global sentiment $\bar{S}$, potentially leading to feedback loops.

## 🧪 Experiments to Try

1. **The Stable Market**: Set high Fundamentalist ratio and low Herding. The price should track the fundamental value closely.
2. **Speculative Bubble**: Increase Momentum traders and Herding strength. Watch the price decouple from value in a parabolic move before eventually crashing.
3. **Flash Crash**: Trigger a "Negative Value Shock" while Herding is high to see how panic spreads through the agent population.
4. **Noisy Sideways**: High Noise Traders and low Price Impact will result in a random-walk style market.

## 📜 Technical Stack
- **Python 3**: Core logic.
- **NumPy**: Numerical computations and vector operations.
- **Matplotlib**: Real-time plotting.
- **Tkinter**: Desktop GUI framework.

---
*Created as an educational tool for exploring market microstructure and behavioral finance.*
