import numpy as np

class MarketAnalytics:
    """Computes rolling metrics and market indicators."""
    def __init__(self, window_size=20):
        self.window_size = window_size
        self.prices = []
        self.returns = []
        self.volatility = 0.0
        self.max_drawdown = 0.0
        self.moving_avg = 0.0
        self.peak_price = 0.0

    def update(self, current_price):
        """Add new price and compute updated metrics."""
        self.prices.append(current_price)
        if len(self.prices) > self.window_size * 10:
            self.prices.pop(0)

        # Basic stats
        self.moving_avg = np.mean(self.prices[-self.window_size:])
        
        # Returns and Volatility
        if len(self.prices) > 2:
            ret = (self.prices[-1] / self.prices[-2]) - 1
            self.returns.append(ret)
            if len(self.returns) > self.window_size * 5:
                self.returns.pop(0)
            
            if len(self.returns) > 5:
                # Rolling volatility
                self.volatility = np.std(self.returns[-self.window_size:]) * np.sqrt(252) # Scaled

        # Drawdown computation
        if current_price > self.peak_price:
            self.peak_price = current_price
        
        if self.peak_price > 0:
            current_drawdown = (self.peak_price - current_price) / self.peak_price
            if current_drawdown > self.max_drawdown:
                self.max_drawdown = current_drawdown

        return {
            'moving_avg': self.moving_avg,
            'volatility': self.volatility,
            'max_drawdown': self.max_drawdown,
            'last_return': self.returns[-1] if self.returns else 0.0
        }

    def reset(self):
        """Clear all metrics."""
        self.prices = []
        self.returns = []
        self.volatility = 0.0
        self.max_drawdown = 0.0
        self.moving_avg = 0.0
        self.peak_price = 0.0
