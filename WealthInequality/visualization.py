import tkinter as tk
import random
import numpy as np
import colorsys

class VisualizationEngine:
    """
    Handles the 2D canvas rendering of the agent economy.
    Maps agent wealth to visual properties (size, color) and handles basic 
    Brownian animation for aesthetic "aliveness".
    """
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        
        self.agents = []
        # Store state as: [x, y, vx, vy] for each agent
        self.agent_states = {} 
        
        # Performance cap: limit number of dots rendered if agent count is too high
        self.max_agents = 1500

    def get_color(self, normalized_wealth):
        """
        Maps a normalized wealth value (0.0 to 1.0) to a color gradient.
        Low wealth = cool colors (blue/purple)
        High wealth = warm colors (red/orange)
        """
        # HSV: 0.66 is blue, 0.0 is red
        hue = (1.0 - normalized_wealth) * 0.66 
        hue = max(0.0, min(0.66, hue))
        
        r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
        # Convert RGB to Tkinter hex string
        return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
        
    def reset(self):
        """
        Clears the canvas and resets all agent visual states.
        """
        for agent_id in self.agents:
            self.canvas.delete(agent_id)
        self.agents = []
        self.agent_states = {}

    def sync_agents(self, wealth_array):
        """
        Synchronizes the canvas objects with the current simulation state.
        Adds/removes dots to match agent count and updates their size/color based on wealth.
        """
        num_agents = min(len(wealth_array), self.max_agents)
        
        # 1. Add new agents if the population increased
        while len(self.agents) < num_agents:
            # Spawn at random locations with slight initial velocity
            x = random.uniform(10, self.width - 10)
            y = random.uniform(10, self.height - 10)
            vx = random.uniform(-0.5, 0.5)
            vy = random.uniform(-0.5, 0.5)
            
            # Create an initial small dot
            agent_id = self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="blue", outline="")
            self.agents.append(agent_id)
            self.agent_states[agent_id] = [x, y, vx, vy]
            
        # 2. Remove agents if the population decreased
        while len(self.agents) > num_agents:
            agent_id = self.agents.pop()
            self.canvas.delete(agent_id)
            del self.agent_states[agent_id]
            
        # 3. Update size and color based on current wealth distribution
        if num_agents > 0:
            # We normalize against the maximum wealth to keep visuals scaled appropriately
            max_wealth = np.max(wealth_array)
            if max_wealth <= 0:
                max_wealth = 1.0 # Prevent division by zero
                
            for i, agent_id in enumerate(self.agents):
                w = wealth_array[i]
                # Log-like or sqrt scaling could be used, but linear normalization 
                # is fine for most distributions up to moderate Ginis
                norm_w = min(1.0, w / max_wealth)
                
                # Radius maps from 2px (poor) to 12px (wealthy)
                radius = max(2.0, 2.0 + norm_w * 10.0) 
                color = self.get_color(norm_w)
                
                state = self.agent_states[agent_id]
                x, y = state[0], state[1]
                
                # Update canvas object
                self.canvas.coords(agent_id, x-radius, y-radius, x+radius, y+radius)
                self.canvas.itemconfig(agent_id, fill=color)

    def update_animation(self):
        """
        Applies a single step of physics (Brownian motion) to all agents to make 
        the visualization feel "alive". Called frequently by the UI loop.
        """
        for agent_id in self.agents:
            state = self.agent_states[agent_id]
            
            # Add random brownian acceleration (jiggle)
            state[2] += random.uniform(-0.5, 0.5)
            state[3] += random.uniform(-0.5, 0.5)
            
            # Apply friction/drag to cap maximum speed and smooth motion
            state[2] *= 0.9
            state[3] *= 0.9
            
            # Update position by velocity
            state[0] += state[2]
            state[1] += state[3]
            
            # Simple boundary collision (bounce)
            if state[0] <= 0 or state[0] >= self.width:
                state[2] *= -1
                state[0] = max(0, min(self.width, state[0]))
            if state[1] <= 0 or state[1] >= self.height:
                state[3] *= -1
                state[1] = max(0, min(self.height, state[1]))
                
            # Update position on canvas (maintaining current radius)
            coords = self.canvas.coords(agent_id)
            if coords:
                # Calculate current radius from bounding box to preserve wealth scaling
                r_x = (coords[2] - coords[0]) / 2
                r_y = (coords[3] - coords[1]) / 2
                
                # Apply new coordinates
                self.canvas.coords(agent_id, 
                                   state[0]-r_x, state[1]-r_y, 
                                   state[0]+r_x, state[1]+r_y)
