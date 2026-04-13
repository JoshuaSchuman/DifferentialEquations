import numpy as np

class Agent:
    """Base class for trading agents in the financial market."""
    def __init__(self, agent_id, position=0.0):
        self.id = agent_id
        self.position = position  # Current stance: -1 (sell), 0 (neutral), 1 (buy)
        self.wealth = 100.0        # Initial wealth
        self.type = "base"

    def compute_demand(self, market_state):
        """Must be implemented by subclasses."""
        return 0.0

class Fundamentalist(Agent):
    """Buys when price is below fundamental value, sells when above."""
    def __init__(self, agent_id, anchor_strength=0.1):
        super().__init__(agent_id)
        self.anchor_strength = anchor_strength
        self.type = "fundamentalist"

    def compute_demand(self, market_state):
        price = market_state['price']
        value = market_state['fundamental_value']
        # Demand is proportional to undervaluation
        demand = self.anchor_strength * (value - price)
        self.position = np.sign(demand)
        return demand

class MomentumTrader(Agent):
    """Buys when price is rising, sells when falling."""
    def __init__(self, agent_id, sensitivity=2.0):
        super().__init__(agent_id)
        self.sensitivity = sensitivity
        self.type = "momentum"

    def compute_demand(self, market_state):
        price_history = market_state['price_history']
        if len(price_history) < 2:
            return 0.0
        
        # Trend is the most recent change
        trend = price_history[-1] - price_history[-2]
        demand = self.sensitivity * trend
        self.position = np.sign(demand)
        return demand

class NoiseTrader(Agent):
    """Trades randomly, adding volatility and liquidity."""
    def __init__(self, agent_id, noise_level=0.5):
        super().__init__(agent_id)
        self.noise_level = noise_level
        self.type = "noise"

    def compute_demand(self, market_state):
        demand = np.random.normal(0, self.noise_level)
        self.position = np.sign(demand)
        return demand

class Market:
    """The central engine that aggregates demand and updates price."""
    def __init__(self, initial_price=100.0, liquidity=0.1, noise=0.05):
        self.price = initial_price
        self.fundamental_value = initial_price
        self.liquidity = liquidity # Price impact parameter (alpha)
        self.external_noise = noise
        self.price_history = [initial_price]
        self.agents = []
        self.herding_strength = 0.0
        self.current_sentiment = 0.0

    def add_agents(self, num_fundamental, num_momentum, num_noise, params):
        """Repopulate agents based on requested ratios."""
        self.agents = []
        for i in range(num_fundamental):
            self.agents.append(Fundamentalist(len(self.agents), params.get('f_anchor', 0.1)))
        for i in range(num_momentum):
            self.agents.append(MomentumTrader(len(self.agents), params.get('m_sens', 2.0)))
        for i in range(num_noise):
            self.agents.append(NoiseTrader(len(self.agents), params.get('n_level', 0.5)))

    def update(self):
        """Single simulation step: agents decide, price updates."""
        market_state = {
            'price': self.price,
            'fundamental_value': self.fundamental_value,
            'price_history': self.price_history,
            'sentiment': self.current_sentiment
        }

        # Collect aggregate demand
        total_demand = sum(agent.compute_demand(market_state) for agent in self.agents)
        
        # Herding: agents are influenced by global sentiment
        # This adds an extra bias to the total demand based on previous sentiment
        herding_effect = self.herding_strength * self.current_sentiment * len(self.agents)
        total_demand += herding_effect

        # Price formation: Delta P = (NetDemand / Liquidity) + Noise
        # Using a simple log-price or arithmetic update
        # For this model, we'll use arithmetic with a floor
        price_change = (total_demand * self.liquidity) + np.random.normal(0, self.external_noise)
        self.price = max(1.0, self.price + price_change)
        
        self.price_history.append(self.price)
        if len(self.price_history) > 1000:
            self.price_history.pop(0)

        # Update global sentiment (average agent position)
        if self.agents:
            self.current_sentiment = np.mean([a.position for a in self.agents])
        
        return {
            'price': self.price,
            'net_demand': total_demand,
            'sentiment': self.current_sentiment
        }

    def apply_shock(self, magnitude):
        """Sudden shift in fundamental value."""
        self.fundamental_value += magnitude
