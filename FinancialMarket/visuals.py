import tkinter as tk
import random

class AgentVisualizer:
    """Renders agents as particles on a Tkinter Canvas."""
    def __init__(self, canvas, width=400, height=300):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.particles = {}  # agent_id -> item_id
        self.colors = {
            "fundamentalist": "#4A90E2", # Blue
            "momentum": "#F5A623",       # Orange
            "noise": "#7ED321"            # Green
        }
        self.stance_colors = {
            1: "#2ECC71",  # Buying (Green)
            -1: "#E74C3C", # Selling (Red)
            0: "#95A5A6"   # Neutral (Gray)
        }

    def initialize_agents(self, agents):
        """Create initial circles for agents at random positions."""
        self.canvas.delete("all")
        self.particles = {}
        
        for agent in agents:
            x = random.randint(10, self.width - 10)
            y = random.randint(10, self.height - 10)
            
            # Base color by agent type
            base_color = self.colors.get(agent.type, "#000000")
            
            # Create a larger background circle for the type and a smaller inner for the stance
            # But for simplicity, we'll just use the stance color as the outline
            radius = 4
            p_id = self.canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius,
                fill=self.stance_colors[agent.position],
                outline=base_color,
                width=2
            )
            self.particles[agent.id] = (p_id, x, y)

    def update(self, agents):
        """Move particles slightly and update their colors based on stance."""
        for agent in agents:
            if agent.id not in self.particles:
                continue
                
            p_id, x, y = self.particles[agent.id]
            
            # Random jitter to simulate activity
            dx = random.randint(-2, 2)
            dy = random.randint(-2, 2)
            
            # Boundary check
            new_x = max(10, min(self.width - 10, x + dx))
            new_y = max(10, min(self.height - 10, y + dy))
            
            # Update visual properties
            self.canvas.coords(
                p_id, 
                new_x - 4, new_y - 4, new_x + 4, new_y + 4
            )
            self.canvas.itemconfig(
                p_id, 
                fill=self.stance_colors[int(agent.position)]
            )
            
            # Store updated position
            self.particles[agent.id] = (p_id, new_x, new_y)
