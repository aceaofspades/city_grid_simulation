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

    def plot_grid(self, current_position=None):
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

        if current_position:
            ax.plot(current_position[0], current_position[1], 'g^', markersize=12)
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
        for intersection in self.intersections:
            if any(x == cx and y == cy for (cx, cy) in intersection['children']):
                valid_direction = intersection['valid_direction']
                current_timing = intersection['current_timing']
                assigned_timing = intersection['assigned_timing']
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Left, Right, Down, Up
                    adj_x, adj_y = x + dx, y + dy
                    if 0 <= adj_x < self.width * 2 and 0 <= adj_y < self.height * 2:
                        if (x // 2 == adj_x // 2) and (y // 2 == adj_y // 2):
                            if (valid_direction == 'x' and dx != 0) or (valid_direction == 'y' and dy != 0):
                                hidden_time_cost = INTRA_MOVE
                                if current_timing <= 5:
                                    hidden_time_cost += current_timing + assigned_timing
                                move_symbol = 'Walk' if current_timing > 10 else str(current_timing)
                            else:
                                hidden_time_cost = current_timing + INTRA_MOVE
                                move_symbol = 'Stop'
                        else:
                            hidden_time_cost = INTER_MOVE
                            move_symbol = 'Block'
                        valid_moves.append(((adj_x, adj_y), move_symbol, hidden_time_cost))
                break
        return valid_moves
    
    def get_valid_moves_data(self):
        return list(enumerate(self.valid_moves))
    
    def process_move(self, chosen_move_index):
        # Get the current list of valid moves
        valid_moves = self.valid_moves  # Use the stored valid moves

        # Ensure the chosen move is valid
        if chosen_move_index < 0 or chosen_move_index >= len(valid_moves):
            print("Invalid move chosen.")
            return {"error": "Invalid move chosen."}

        # Update player's position based on the chosen move
        move = valid_moves[chosen_move_index]
        self.current_position = move[0]  # Update to the new position from the chosen move
        time_cost = move[2]
        self.total_time += time_cost

        # Update timings and directions
        for intersection in self.intersections:
            intersection['current_timing'] -= time_cost
            while intersection['current_timing'] <= 0:
                intersection['valid_direction'] = 'y' if intersection['valid_direction'] == 'x' else 'x'
                intersection['current_timing'] += intersection['assigned_timing']

        self.valid_moves = self.get_valid_moves(self.current_position)
        print("Valid move chosen.")
        return {
            "current_position": self.current_position,
            "time_cost": time_cost,
            "next_moves": self.get_valid_moves_data()
        }

    def choose_move(self, chosen_move_index):
        return self.process_move(chosen_move_index)


    def make_move(self, chosen_move_index):
        return self.choose_move(chosen_move_index)
    
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




# Create class called CityGridGame that make this playable
class CityGridGame:
    '''Class to play the CityGrid game. 
    It takes the width and height of the grid as input and initializes the game. 
    It has methods to make a move, display the grid, get the current state, 
    and get the valid moves. It also has a play method to play the game interactively.
    '''
    def __init__(self, width, height):
        self.city_grid = CityGrid(width, height)
        self.state = self.city_grid.get_state()
        self.valid_moves = self.state['valid_moves']
        self.total_time = 0

    def make_move(self, chosen_move_index):
        move_result = self.city_grid.make_move(chosen_move_index)
        self.state = self.city_grid.get_state()
        self.valid_moves = self.state['valid_moves']
        self.total_time += move_result['time_cost']
        return move_result

    def display_grid(self):
        self.city_grid.plot_grid(self.state['current_position'])

    def get_state(self):
        return self.state

    def get_valid_moves(self):
        return self.valid_moves
    
    def play(self):
        while True:
            print(f"Current position: {self.state['current_position']}")
            print(f"Valid moves: {[(index, (coords, action)) for index, (coords, action, hidden_time_cost) in self.valid_moves]}")
            chosen_move = int(input("Choose a move: "))
            print('chosen_move:', chosen_move)
            print('type(chosen_move):', type(chosen_move))
            move_result = self.make_move(chosen_move)
            print(f"Move result: {move_result}")
            if move_result.get('error', None):
                print(move_result['error'])
                break
            self.display_grid()
            if move_result['current_position'] == self.city_grid.end_position:
                print(f"Congratulations! You reached the end position in {self.total_time} seconds!")
                break
            print(f"Total time: {self.total_time}")
            print("")


# Example usage

#%%
# Play game
NUM_X_INTERSECTIONS = 3
NUM_Y_INTERSECTIONS = 4
game = CityGridGame(width=NUM_X_INTERSECTIONS, height=NUM_Y_INTERSECTIONS)
game.play()

#%%
city_grid = CityGrid(7,4)
intersections = json.loads(city_grid.output_intersections())
