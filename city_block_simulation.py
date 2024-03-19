#%%
import matplotlib.pyplot as plt
import numpy as np
import random
import json

INTRA_MOVE = 8 # Cost for moving within the same intersection
INTER_MOVE = 120 # Cost for between intersections

class CityGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.corners = np.empty((width * 2, height * 2), dtype=object)
        self.intersections = []
        self.valid_moves = []
        self.initialize_corners()
        self.output_intersections()
        self.initialize_start_end()
        self.total_time = 0
        self.plot_grid()
        self.get_valid_moves(self.start_position)

    def initialize_corners(self):
        for x in range(self.width * 2):
            for y in range(self.height * 2):
                corner_name = f"C{x}{y}"
                self.corners[x, y] = Corner(corner_name, x, y)

    def plot_grid(self):
        fig, ax = plt.subplots()
        for x in range(self.width * 2):
            for y in range(self.height * 2):
                corner = self.corners[x, y]
                if (x, y) == self.start_position:
                    ax.plot(corner.x, corner.y, 'ms')  # Highlight start position with a pink 'o'
                elif (x, y) == self.end_position:
                    ax.plot(corner.x, corner.y, 'rs')  # Highlight end position with a pink 'o'
                else:
                    ax.plot(corner.x, corner.y, 'bo')  # Blue 'o' for corners
                if x % 2 == 1 and y % 2 == 1:  # Mark intersections
                    ax.plot(corner.x - 0.5, corner.y - 0.5, 'ro')  # Red 'o' for intersections

        plt.grid(True)
        plt.show()

    def initialize_start_end(self):
        # Determine the start point in the first parent
        first_parent_corners = self.intersections[0]['children']
        start_corner_index = random.choice(range(len(first_parent_corners)))
        self.start_position = first_parent_corners[start_corner_index]

        # Determine the end point in the last parent
        last_parent_corners = self.intersections[-1]['children']
        end_corner_index = random.choice(range(len(last_parent_corners)))
        self.end_position = last_parent_corners[end_corner_index]

        self.current_position = self.start_position

        print(f"Start position: {self.start_position}, End position: {self.end_position}")

    def initialize_intersections(self):
        parent_id = 1
        for x in range(0, self.width * 2, 2):
            for y in range(0, self.height * 2, 2):
                corners = [(x, y), (x+1, y), (x, y+1), (x+1, y+1)]
                assigned_timing = random.randint(20, 40)
                current_timing = random.randint(0, assigned_timing)
                intersection = {
                    "parent": parent_id,
                    "children": corners,
                    "valid_direction": random.choice(['x', 'y']),
                    "assigned_timing": assigned_timing,
                    "current_timing": current_timing
                }
                self.intersections.append(intersection)
                parent_id += 1

    def output_intersections(self):
        self.initialize_intersections()
        return json.dumps(self.intersections, indent=2)
    
    def get_valid_moves(self, current_position):
        x, y = current_position
        valid_moves = []
        # Find the parent intersection for the current position
        for intersection in self.intersections:
            if any(x == cx and y == cy for (cx, cy) in intersection['children']):
                valid_direction = intersection['valid_direction']
                current_timing = intersection['current_timing']
                # Check each possible move from the current position
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Left, Right, Down, Up
                    adj_x, adj_y = x + dx, y + dy
                    if 0 <= adj_x < self.width * 2 and 0 <= adj_y < self.height * 2:
                        # Determine if the move is within the same intersection
                        if (x // 2 == adj_x // 2) and (y // 2 == adj_y // 2):
                            if (valid_direction == 'x' and dx != 0) or (valid_direction == 'y' and dy != 0):
                                move_time_cost = INTRA_MOVE  # Moving in the valid direction within the same intersection
                            else:
                                move_time_cost = current_timing + INTRA_MOVE  # Moving against the valid direction
                        else:
                            move_time_cost = INTER_MOVE  # Moving between different intersections
                        valid_moves.append(((adj_x, adj_y), move_time_cost))
                break
        return valid_moves
    
    def get_valid_moves_data(self):
        return [(i, move) for i, move in enumerate(self.valid_moves)]
    
    def process_move(self, chosen_move_index):
        # Get the current list of valid moves
        valid_moves = self.valid_moves  # Use the stored valid moves

        # Ensure the chosen move is valid
        if chosen_move_index < 0 or chosen_move_index >= len(valid_moves):
            return {"error": "Invalid move chosen."}

        # Update player's position based on the chosen move
        move = valid_moves[chosen_move_index]
        self.current_position = move[0]  # Update to the new position from the chosen move
        time_cost = move[1]
        self.total_time += time_cost

        # Update timings and directions
        for intersection in self.intersections:
            intersection['current_timing'] -= time_cost
            while intersection['current_timing'] <= 0:
                intersection['valid_direction'] = 'y' if intersection['valid_direction'] == 'x' else 'x'
                intersection['current_timing'] += intersection['assigned_timing']

        self.valid_moves = self.get_valid_moves(self.current_position)
        return {
            "current_position": self.current_position,
            "time_cost": time_cost,
            "next_moves": self.get_valid_moves_data()
        }

    def choose_move(self, chosen_move_index):
        self.process_move(chosen_move_index)

    def make_move(self, chosen_move_index):
        result = self.choose_move(chosen_move_index)
    
    def get_state(self):
        self.valid_moves = self.get_valid_moves(self.current_position)
        return {
            "current_position": self.current_position,
            "valid_moves": self.get_valid_moves_data()
        }

class Corner:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

    def __repr__(self):
        return f"{self.name}"

# Example usage
city_grid = CityGrid(4, 7)  # Creates a grid with corners that form X*Y intersections
city_grid.get_state()
intersections = json.loads(city_grid.output_intersections())

#%%
city_grid.get_state()
city_grid.make_move(1)
city_grid.get_state()
city_grid.plot_grid()

#%%
