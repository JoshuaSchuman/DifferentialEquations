import numpy as np
import random
from metrics import calculate_gini, calculate_top_10_share

class WealthSimulationEngine:
    """
    Core engine handling agent states, pairwise interactions, and global 
    macroeconomic dynamics (continuous growth, taxation, noise).
    """
    def __init__(self, num_agents=500, initial_distribution="uniform", initial_wealth=100.0):
        # Simulation Base Config
        self.num_agents = num_agents
        self.initial_distribution = initial_distribution
        self.initial_wealth = initial_wealth
        
        # Microscopic / Agent Interaction Parameters
        self.model_type = "random" # "random" or "saving"
        self.saving_rate = 0.0 # Fraction of wealth protected during trade (for "saving" model)
        self.trade_intensity = 1.0 # Fraction of total possible agent pairs that interact per step
        
        # Macroscopic / Global Parameters
        self.tax_rate = 0.0 # Percentage tax per step
        self.redistribution = False # Whether collected taxes are redistributed equally
        self.noise_level = 0.0 # Amount of random Brownian noise applied to wealth
        self.growth_rate = 0.0 # Exogenous exponential growth or decay (dw/dt = r*w)
        
        # Time and Integration
        self.dt = 0.1 # Integration timestep for ODEs
        self.time = 0.0
        
        # Pre-allocate wealth array
        self.wealth = np.zeros(self.num_agents, dtype=np.float64)
        
        self.reset()

    def reset(self):
        """
        Reinitialize the economy based on the chosen starting wealth distribution.
        """
        self.time = 0.0
        
        # Adjust wealth array size if num_agents changed
        if len(self.wealth) != self.num_agents:
            self.wealth = np.zeros(self.num_agents, dtype=np.float64)
            
        if self.initial_distribution == "uniform":
            self.wealth.fill(self.initial_wealth)
            
        elif self.initial_distribution == "random":
            # Uniformly distributed noise around the mean initial wealth
            self.wealth = np.random.uniform(0.0, self.initial_wealth * 2, self.num_agents)
            
        elif self.initial_distribution == "normal":
            # Normally distributed, avoiding negative numbers via clipping
            self.wealth = np.random.normal(self.initial_wealth, self.initial_wealth / 3, self.num_agents)
            self.wealth = np.clip(self.wealth, 0.0, None)
            
        elif self.initial_distribution == "pareto":
            # Heavy-tailed (inequality-heavy) initial state
            self.wealth = np.random.pareto(a=1.16, size=self.num_agents)
            # Scale to roughly match initial mean wealth
            scale_factor = self.initial_wealth / max(1e-9, np.mean(self.wealth))
            self.wealth *= scale_factor
            
        # Store metrics history for plotting and scrubbing
        self.history = {
            'time': [self.time],
            'gini': [calculate_gini(self.wealth)],
            'top_10': [calculate_top_10_share(self.wealth)]
        }

    def _agent_interaction(self):
        """
        Stochastically pairs agents up to trade wealth based on the selected exchange model.
        """
        # Determine number of pairs to interact this step
        # At trade_intensity = 1.0, every agent is involved in an interaction on average (N/2 pairs)
        num_trades = int((self.num_agents / 2) * self.trade_intensity)
        
        if num_trades <= 0:
            return
            
        # Randomly select interacting pairs without replacement if possible, 
        # or just sample randomly for performance and statistical mixing
        # We will use random sampling of pairs
        idx1 = np.random.randint(0, self.num_agents, size=num_trades)
        idx2 = np.random.randint(0, self.num_agents, size=num_trades)
        
        w1 = self.wealth[idx1]
        w2 = self.wealth[idx2]
        
        # To avoid vectorization complexities with overlapping indices in single step, 
        # we compute deltas and add them sequentially or accept minor collision errors 
        # as noise in a large agent pool. We will use a fast loop for accurate conservation.
        
        for i in range(num_trades):
            i1, i2 = idx1[i], idx2[i]
            if i1 == i2: continue # Cannot trade with oneself
            
            cw1, cw2 = self.wealth[i1], self.wealth[i2]
            
            if self.model_type == "random":
                # Pure Random Exchange (Yard-Sale model variant without saving)
                # Agents pool their wealth and split it randomly
                total = cw1 + cw2
                frac = random.random()
                self.wealth[i1] = total * frac
                self.wealth[i2] = total * (1.0 - frac)
                
            elif self.model_type == "saving":
                # Saving Propensity Model
                # Agents save a fraction of their wealth, and only risk the rest
                stake1 = cw1 * (1.0 - self.saving_rate)
                stake2 = cw2 * (1.0 - self.saving_rate)
                
                total_stake = stake1 + stake2
                
                # Winner takes all the stake, or random split of the stake
                # Let's use random split of the staked pool to ensure continuity
                frac = random.random()
                
                # New wealth = saved wealth + fraction of the pooled stakes
                self.wealth[i1] = (cw1 - stake1) + total_stake * frac
                self.wealth[i2] = (cw2 - stake2) + total_stake * (1.0 - frac)

    def _apply_global_dynamics(self):
        """
        Applies system-wide continuous ODEs and macro-economic factors.
        """
        # 1. Taxation & Redistribution
        if self.tax_rate > 0.0:
            taxes_collected = np.sum(self.wealth * self.tax_rate)
            self.wealth *= (1.0 - self.tax_rate)
            
            if self.redistribution and taxes_collected > 0:
                redistributed_amount = taxes_collected / self.num_agents
                self.wealth += redistributed_amount
                
        # 2. Continuous Growth/Decay (Euler integration for dw/dt = r*w)
        if self.growth_rate != 0.0:
            self.wealth += self.wealth * self.growth_rate * self.dt
            
        # 3. Additive Economic Noise (Brownian motion proxy)
        if self.noise_level > 0.0:
            # Noise is scaled by dt and current wealth level to avoid immediate negative values 
            # for low wealth agents, or just simple uniform noise.
            noise = np.random.normal(0, self.noise_level * np.sqrt(self.dt), self.num_agents)
            self.wealth += noise
            
        # Ensure zero lower bound constraint (wealth cannot be negative in this simple model)
        np.clip(self.wealth, 0.0, None, out=self.wealth)

    def step(self):
        """
        Advances the simulation by one discrete timestep, integrating micro and macro dynamics.
        """
        # Execute micro-level trades
        self._agent_interaction()
        
        # Execute macro-level continuous dynamics
        self._apply_global_dynamics()
        
        self.time += self.dt
        
        # Record periodic history metrics
        self.history['time'].append(self.time)
        self.history['gini'].append(calculate_gini(self.wealth))
        self.history['top_10'].append(calculate_top_10_share(self.wealth))
        
        return self.wealth, self.time
