import numpy as np

class SimulationEngine:
    def __init__(self):
        # Default Parameters
        self.r = 1.0  # Prey growth rate
        self.K = 100.0 # Carrying capacity
        self.a = 0.1  # Predation rate
        self.b = 0.05 # Predator efficiency
        self.d = 0.5  # Predator death rate
        
        # Initial Conditions
        self.P0 = 40.0
        self.H0 = 10.0
        
        # State
        self.t = 0.0
        self.P = self.P0
        self.H = self.H0
        
        # History
        self.history = {'t': [0.0], 'P': [self.P0], 'H': [self.H0]}
        
        self.dt = 0.05
        self.model = 'Predator-Prey' # 'Exponential', 'Logistic', 'Predator-Prey', 'Custom'
        self.noise = False
        self.noise_intensity = 0.1
        
        # Custom Equation Support
        self.custom_dPdt = "r * P * (1 - P/K) - a * P * H"
        self.custom_dHdt = "b * P * H - d * H"
        self.env_vars = {} # Dictionary for custom variables

    def reset(self):
        self.t = 0.0
        self.P = self.P0
        self.H = self.H0
        self.history = {'t': [0.0], 'P': [self.P0], 'H': [self.H0]}

    def derivatives(self, P, H):
        if self.model == 'Exponential':
            dPdt = self.r * P
            dHdt = 0.0
        elif self.model == 'Logistic':
            dPdt = self.r * P * (1 - P/self.K)
            dHdt = 0.0
        elif self.model == 'Predator-Prey':
            dPdt = self.r * P * (1 - P/self.K) - self.a * P * H
            dHdt = self.b * P * H - self.d * H
        else: # Custom
            # Combine standard params, state, and env_vars for evaluation
            context = {
                'P': P, 'H': H, 't': self.t,
                'r': self.r, 'K': self.K, 'a': self.a, 'b': self.b, 'd': self.d,
                'np': np, 'sin': np.sin, 'cos': np.cos, 'exp': np.exp, 'log': np.log, 'sqrt': np.sqrt
            }
            context.update(self.env_vars)
            try:
                dPdt = eval(self.custom_dPdt, {"__builtins__": {}}, context)
                dHdt = eval(self.custom_dHdt, {"__builtins__": {}}, context)
            except Exception as e:
                # Fallback to zero if equation is invalid
                dPdt, dHdt = 0.0, 0.0
        
        return dPdt, dHdt

    def step(self):
        # Runge-Kutta 4th Order
        k1P, k1H = self.derivatives(self.P, self.H)
        
        k2P, k2H = self.derivatives(self.P + 0.5 * self.dt * k1P, 
                                    self.H + 0.5 * self.dt * k1H)
        
        k3P, k3H = self.derivatives(self.P + 0.5 * self.dt * k2P, 
                                    self.H + 0.5 * self.dt * k2H)
        
        k4P, k4H = self.derivatives(self.P + self.dt * k3P, 
                                    self.H + self.dt * k3H)
        
        self.P += (self.dt / 6.0) * (k1P + 2*k2P + 2*k3P + k4P)
        self.H += (self.dt / 6.0) * (k1H + 2*k2H + 2*k3H + k4H)
        
        if self.noise:
            self.P += np.random.normal(0, self.noise_intensity * np.sqrt(self.dt))
            self.H += np.random.normal(0, self.noise_intensity * np.sqrt(self.dt))
        
        # Populations can't be negative
        self.P = max(0.0, self.P)
        self.H = max(0.0, self.H)
        
        self.t += self.dt
        
        self.history['t'].append(self.t)
        self.history['P'].append(self.P)
        self.history['H'].append(self.H)
        
        return self.P, self.H, self.t

    def get_rates(self):
        return self.derivatives(self.P, self.H)
