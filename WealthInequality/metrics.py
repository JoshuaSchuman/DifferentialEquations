import numpy as np

def calculate_gini(wealth):
    """
    Calculate the Gini coefficient of a numpy array of wealth values.
    The Gini coefficient is a measure of statistical dispersion intended to 
    represent the income or wealth inequality within a nation or any other group of people.
    
    A Gini coefficient of 0 expresses perfect equality, where all values are the same.
    A Gini coefficient of 1 (or 100%) expresses maximal inequality among values.
    """
    wealth = np.asarray(wealth, dtype=np.float64)
    # Ensure all values are non-negative
    if np.amin(wealth) < 0:
        wealth -= np.amin(wealth)
        
    # Add a tiny epsilon to prevent division by zero in empty or zero-wealth economies
    wealth += 1e-9 
    wealth = np.sort(wealth)
    
    n = len(wealth)
    index = np.arange(1, n + 1)
    
    # Mathematical definition of Gini coefficient
    return ((np.sum((2 * index - n  - 1) * wealth)) / (n * np.sum(wealth)))

def calculate_top_10_share(wealth):
    """
    Calculate the share of total wealth held by the wealthiest 10% of agents.
    """
    if len(wealth) == 0:
        return 0.0
        
    wealth = np.sort(np.asarray(wealth, dtype=np.float64))
    n = len(wealth)
    top_10_idx = int(n * 0.9) # Index where the top 10% begins
    
    top_10_wealth = np.sum(wealth[top_10_idx:])
    total_wealth = np.sum(wealth)
    
    if total_wealth == 0:
        return 0.0
        
    return top_10_wealth / total_wealth

def calculate_lorenz_curve(wealth):
    """
    Calculates the points for a Lorenz curve.
    Returns the cumulative share of population (x) and cumulative share of wealth (y).
    """
    wealth = np.sort(np.asarray(wealth, dtype=np.float64))
    wealth += 1e-9
    
    n = len(wealth)
    cum_wealth = np.cumsum(wealth)
    total_wealth = cum_wealth[-1]
    
    x = np.linspace(0.0, 1.0, n)
    y = cum_wealth / total_wealth
    
    # Prepend zeros to start curve at origin
    return np.insert(x, 0, 0.0), np.insert(y, 0, 0.0)
