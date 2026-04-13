import tkinter as tk
import random
import numpy as np

class VisualizationEngine:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        
        # Lists of dot IDs
        self.prey_dots = []
        self.predator_dots = []
        
        # Store dot state (x, y, vx, vy)
        self.prey_states = {} # {canvas_id: [x, y, vx, vy]}
        self.predator_states = {}
        
        self.prey_color = "#2ECC71" # Green
        self.predator_color = "#E74C3C" # Red
        self.dot_radius = 3
        self.max_dots = 1000 # Performance cap

    def reset(self):
        for dot_id in self.prey_dots + self.predator_dots:
            self.canvas.delete(dot_id)
        self.prey_dots = []
        self.predator_dots = []
        self.prey_states = {}
        self.predator_states = {}

    def sync_population(self, p_count, h_count):
        p_count = int(min(p_count, self.max_dots))
        h_count = int(min(h_count, self.max_dots))
        
        # Sync Prey
        while len(self.prey_dots) < p_count:
            self._add_dot('prey')
        while len(self.prey_dots) > p_count:
            dot_id = self.prey_dots.pop()
            self.canvas.delete(dot_id)
            del self.prey_states[dot_id]
            
        # Sync Predators
        while len(self.predator_dots) < h_count:
            self._add_dot('predator')
        while len(self.predator_dots) > h_count:
            dot_id = self.predator_dots.pop()
            self.canvas.delete(dot_id)
            del self.predator_states[dot_id]

    def _add_dot(self, type):
        x = random.uniform(10, self.width - 10)
        y = random.uniform(10, self.height - 10)
        vx = random.uniform(-2, 2)
        vy = random.uniform(-2, 2)
        
        color = self.prey_color if type == 'prey' else self.predator_color
        radius = self.dot_radius if type == 'prey' else self.dot_radius + 1
        
        dot_id = self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, 
                                          fill=color, outline=color)
        
        if type == 'prey':
            self.prey_dots.append(dot_id)
            self.prey_states[dot_id] = [x, y, vx, vy]
        else:
            self.predator_dots.append(dot_id)
            self.predator_states[dot_id] = [x, y, vx, vy]

    def update_animation(self):
        # Move Prey
        for dot_id in self.prey_dots:
            state = self.prey_states[dot_id]
            self._move_and_bounce(dot_id, state)
            
        # Move Predators (with slight attraction to nearest prey)
        for h_id in self.predator_dots:
            h_state = self.predator_states[h_id]
            
            # Simple attraction logic if prey exists
            if self.prey_dots:
                # Find nearest prey (only check a few to save performance)
                p_id = random.choice(self.prey_dots)
                p_state = self.prey_states[p_id]
                dx = p_state[0] - h_state[0]
                dy = p_state[1] - h_state[1]
                dist = max(1, np.sqrt(dx**2 + dy**2))
                h_state[2] += 0.1 * dx / dist
                h_state[3] += 0.1 * dy / dist
                
            self._move_and_bounce(h_id, h_state, max_speed=3)

    def _move_and_bounce(self, dot_id, state, max_speed=2):
        # Random motion
        state[2] += random.uniform(-0.2, 0.2)
        state[3] += random.uniform(-0.2, 0.2)
        
        # Cap speed
        speed = np.sqrt(state[2]**2 + state[3]**2)
        if speed > max_speed:
            state[2] = (state[2] / speed) * max_speed
            state[3] = (state[3] / speed) * max_speed
            
        # Update position
        state[0] += state[2]
        state[1] += state[3]
        
        # Bounce off walls
        if state[0] <= 0 or state[0] >= self.width:
            state[2] *= -1
            state[0] = max(0, min(self.width, state[0]))
        if state[1] <= 0 or state[1] >= self.height:
            state[3] *= -1
            state[1] = max(0, min(self.height, state[1]))
            
        self.canvas.coords(dot_id, state[0]-self.dot_radius, state[1]-self.dot_radius, 
                                  state[0]+self.dot_radius, state[1]+self.dot_radius)
