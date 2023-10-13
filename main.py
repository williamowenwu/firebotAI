import random
import time
import math

class Ship():
    def __init__(self) -> None:
        try:
            D = int(input("Enter D x D Dimension: "))
        except ValueError as e:
            print("Needs to be an int")
            exit()
        except Exception as e:
            print(e)
            exit()

        # Up, down, left, right
        self.directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]
        self.D = D # D x D Dimension of ship
        self.ship = []
        self.dead_ends = []
        
        # initial positions of bot, button, fire
        self.bot = (-1, -1)
        self.button = (-1, -1)
        self.fire = (-1, -1)

    def __repr__(self) -> str:
        ship_str = ""
        for row in self.ship:
            ship_str += '[' + ' '.join(row) + ']\n'
        return ship_str

    def find_shortest_path(self, constraints: list) -> list:  
                fringe = dict()
                fringe.update({self.bot: math.dist([self.bot[0], self.bot[1]], [self.button[0], self.button[1]])})
                parent = {}
                visited = []

                sorted_list = [(self.bot[0], self.bot[1])]
                while fringe:
                    smallest_key = sorted_list.pop(0)
                    curr_x, curr_y = smallest_key
                    fringe.pop(smallest_key)

                    # If button is found
                    if curr_x == self.button[0] and curr_y == self.button[1]:
                        path = [(curr_x, curr_y)]
                        while smallest_key in parent and smallest_key != self.bot:
                            path.insert(0, smallest_key)
                            smallest_key = parent[smallest_key]
                        return path
                    
                    for x, y in self.directions:
                        new_x, new_y = x + curr_x, y + curr_y
                        # all of the neighbours inside this if statement are valid neighbours.
                        if 0 <= new_x < self.D and 0 <= new_y < self.D and self.ship[new_x][new_y] != 'X' and (new_x, new_y) not in constraints and (new_x, new_y) not in visited:
                            edist = math.dist([new_x, new_y], [self.button[0], self.button[1]])
                            fringe.update({(new_x, new_y): edist})
                            visited.append((new_x,new_y))
                            parent[(new_x, new_y)] = smallest_key

                    sorted_list = [k for k, _ in sorted(fringe.items(), key=lambda item: item[1])]
                return None
            
    def find_risky_path(self, constraints: list) -> list:
        fringe = {self.bot : math.dist([self.bot[0], self.bot[1]], [self.button[0], self.button[1]])}
        parent = {} # for returning path
        visited = [] # avoid infinite loop

        priority = [(self.bot)] # starts with initial position of bot
        while priority:
            curr_x, curr_y = priority.pop(0)
            # print(fringe)
            # print((curr_x, curr_y))
            # time.sleep(1000)
            fringe.pop((curr_x, curr_y))
            # if button is found/reached
            if curr_x == self.button[0] and curr_y == self.button[1]:
                path = [(curr_x, curr_y)]
                while (curr_x, curr_y) in parent and (curr_x, curr_y) != self.bot:
                    path.insert(0, (curr_x, curr_y))
                    (curr_x, curr_y) = parent[(curr_x, curr_y)]
                return path
            # initial edist of fire to button
            fire_dist = math.dist([constraints[0][0],constraints[0][1]], [self.button[0], self.button[1]])
            
            # closest fire constraint to the button
            for coord in constraints:
                if math.dist([coord[0], coord[1]], [self.button[0], self.button[1]]) > fire_dist:
                    fire_dist = math.dist([coord[0], coord[1]], [self.button[0], self.button[1]])
            
            local_directions = dict()
            remove_optimal = False # decides to remove the most optimal local direction

            # for all possible directions
            for x, y in self.directions:
                new_x, new_y = x + curr_x, y + curr_y
                if 0 <= new_x < self.D and 0 <= new_y < self.D and self.ship[new_x][new_y] != 'X' and (new_x, new_y) not in constraints and (new_x, new_y) not in visited:

                    # distance from bot to the button
                    button_edist = math.dist([new_x, new_y], [self.button[0], self.button[1]])
                    local_directions.update({(new_x, new_y): button_edist})

                    # if button is >= than fire or they are equal --> gun it
                    # take the second, third, fourth path -> remove the first option and reconsider it
                    remove_optimal = True if button_edist >= fire_dist else False
                    parent[(new_x, new_y)] = (curr_x, curr_y)
                    visited.append((new_x, new_y))

            # sorted local is a list
            sorted_local_directions = [k for k, _ in sorted(local_directions.items(), key=lambda item: item[1])]
            priority = [k for k, _ in sorted(fringe.items(), key=lambda item: item[1])]
            if remove_optimal:
                local_directions.pop(sorted_local_directions[0])
                sorted_local_directions.pop(0)

            priority.extend(sorted_local_directions)
            fringe.update(local_directions)
        return None

    # generates and returns a colored block
    def colored_block(self, color: str) -> str:
        color_codes = {
            'r': '\033[31m',  # Red
            'g': '\033[32m',  # Green
            'b': '\033[34m',  # Blue
            'y': '\033[33m',  # Yellow
            'm': '\033[35m',  # Magenta
            'c': '\033[36m',  # Cyan
            'w': '\033[37m',  # White
        }

        reset_color = '\033[0m'

        if color in color_codes:
            return f"{color_codes[color]}\u2588{reset_color}"
        else:
            return f"Invalid color code: {color}"
    
    # given a cordinate and what you're looking for, it will return number of neighbors next to an open cells
    def count_neighbors(self, x: int, y: int, item: str) -> int:
        count = 0
        for move_x, move_y in self.directions: 
            new_x, new_y = x + move_x, y + move_y
            if 0 <= new_x < self.D and 0 <= new_y < self.D and self.ship[new_x][new_y] == item:
                count += 1
        return count
    
    def generate_ship(self) -> None:
        for _ in range(self.D):
            row = ['X'] * self.D
            self.ship.append(row)
        
        # set of all possible square to open
        open_possibilities = set()

        #Choose a square in the interior to ‘open’ at random.
        rand_x_coord = random.randint(0, self.D-1)
        rand_y_coord = random.randint(0, self.D-1)
        self.ship[rand_x_coord][rand_y_coord] = 'O'

        open_possibilities.add((rand_x_coord, rand_y_coord))

        # print(f"\nOpening inital.... {rand_x_coord, rand_y_coord}")
        # print(self)

        while open_possibilities:
            curr_x, curr_y = open_possibilities.pop()
            self.ship[curr_x][curr_y] = 'O'

            for x, y in self.directions:
                new_x, new_y = x + curr_x, y + curr_y
                #if within the ship dimensions and is blocked
                if 0 <= new_x < self.D and 0 <= new_y < self.D and self.ship[new_x][new_y] == 'X':
                    # Check if the square is not already in open_possibilities
                    if (new_x, new_y) in open_possibilities:
                        open_possibilities.remove((new_x, new_y))
                        self.ship[new_x][new_y] = '-' # Not able to open
                    else:
                        open_possibilities.add((new_x,new_y))
        # print(self)

        # now get intial num of deadends
        for x in range(self.D):
            for y in range(self.D):
                if self.ship[x][y] == 'O' and self.count_neighbors(x, y, "O") == 1:
                    self.dead_ends.append((x, y))

        half = len(self.dead_ends) // 2
        # print(f"Number of deadends (init): {len(self.dead_ends)}")

        # make approximately half of deadends non dead ends
        while len(self.dead_ends) > half:
            curr_x, curr_y = random.choice(self.dead_ends)
            # print(f"Removing: {curr_x, curr_y} from dead ends")
            self.dead_ends.remove((curr_x,curr_y))

            # Remove one of the sides arbitrarily from the dead ends
            for x, y in random.sample(self.directions, len(self.directions)):
                new_x, new_y = x + curr_x, y + curr_y
                if  0 <= new_x < self.D and 0 <= new_y < self.D and (self.ship[new_x][new_y] in ['X', '-']):
                    self.ship[new_x][new_y] = 'O'
                    break

            # print(self)
            new_dead_ends = [] # new deadend array to see how many deadends are removed
 
            # recompute the num of deadends
            for x in range(self.D):
                for y in range(self.D):
                    if self.ship[x][y] == 'O' and self.count_neighbors(x, y, "O") == 1:
                        new_dead_ends.append((x,y))
 
            self.dead_ends = new_dead_ends.copy()

            for x in range(self.D):
                for y in range(self.D):
                    if self.ship[x][y] == '-':
                        self.ship[x][y] = 'X' 

        # print(f"Length of deadends: {len(self.dead_ends)}\n" ,"Dead ends:")
        # for x, y in self.dead_ends:
        #     print(f"({x}, {y})")
        # print()
        
        # randomly chooses locations for a button, bot, and fire
        while self.bot == (-1, -1) or self.button == (-1, -1) or self.fire == (-1, -1):
            rand_x_coord = random.randint(0, self.D-1)
            rand_y_coord = random.randint(0, self.D-1)
            
            if self.ship[rand_x_coord][rand_y_coord] == 'O':
                if self.bot == (-1, -1):
                    self.ship[rand_x_coord][rand_y_coord] = self.colored_block('c')
                    self.bot = (rand_x_coord, rand_y_coord)
                elif self.button == (-1, -1):
                    self.ship[rand_x_coord][rand_y_coord] = self.colored_block('g')
                    self.button = (rand_x_coord, rand_y_coord)
                elif self.fire == (-1, -1):
                    self.ship[rand_x_coord][rand_y_coord] = self.colored_block('r')
                    self.fire = (rand_x_coord, rand_y_coord)

    def run_bot_1(self, q) -> None: # run with the type of bot you want
        possible_places = [self.colored_block('c'), 'O']
        fire_possibilties = set()
        curr_x, curr_y = self.fire
        fire = [self.fire]
        
        path = self.find_shortest_path(fire)
        print(path)

        # Initial fire probable locations (up to 4)
        for x, y in self.directions:
            new_x, new_y = x + curr_x, y + curr_y
            if 0 <= new_x < self.D and 0 <= new_y < self.D and self.ship[new_x][new_y] == 'O':
                fire_possibilties.add((new_x, new_y))

        while self.bot != self.button:
            if (path is not None and path not in fire and self.bot not in fire):
                next_step = path.pop(0)
                self.ship[self.bot[0]][self.bot[1]] = "O"
                print(next_step)
                self.bot = next_step
                self.ship[self.bot[0]][self.bot[1]] = self.colored_block('c')
            else:
                print("you lost")
                return
                            
            fire_copy = fire_possibilties.copy()
            for fire_poss in fire_possibilties:
                curr_x, curr_y = fire_poss
                # print(new_x, new_y)
                k = self.count_neighbors(curr_x, curr_y, self.colored_block('r')) # number of fires
                fire_spread_possibility = 1 - (1 - q) ** k
                rand = random.random()
                if fire_spread_possibility > rand:
                    self.ship[curr_x][curr_y] = self.colored_block('r')
                    fire.append((curr_x,curr_y))
                    for x, y in self.directions:
                        new_x, new_y = x + curr_x, y + curr_y
                        if 0 <= new_x < self.D and 0 <= new_y < self.D and self.ship[new_x][new_y] in possible_places:
                            fire_copy.add((new_x, new_y))
                else:
                    fire_copy.add(self.fire)
                fire_possibilties = fire_copy.copy() 
            print(self)
            time.sleep(0.25)

        if self.bot == self.button: 
            print("you won")
        else:
            print("you lost")

    def run_bot_2(self, q) -> None: # run with the type of bot you want
        possible_places = [self.colored_block('c'), 'O']
        fire_possibilties = set()
        curr_x, curr_y = self.fire
        fire = [self.fire]
        
        # Initial fire probable locations (up to 4)
        for x, y in self.directions:
            new_x, new_y = x + curr_x, y + curr_y
            if 0 <= new_x < self.D and 0 <= new_y < self.D and self.ship[new_x][new_y] == 'O':
                fire_possibilties.add((new_x, new_y))

        while self.bot != self.button:
            path = self.find_shortest_path(fire)
            if (path is not None and path not in fire and self.bot not in fire):
                next_step = path.pop(0)
                self.ship[self.bot[0]][self.bot[1]] = "O"
                print(next_step)
                self.bot = next_step
                self.ship[self.bot[0]][self.bot[1]] = self.colored_block('c')
            else:
                print("you lost")   
                return
                            
            fire_copy = fire_possibilties.copy()

            for fire_poss in fire_possibilties:
                curr_x, curr_y = fire_poss
                # print(curr_x, curr_y)
                k = self.count_neighbors(curr_x, curr_y, self.colored_block('r'))
                fire_spread_possibility = 1 - (1 - q) ** k
                rand = random.random()
                if fire_spread_possibility > rand:
                    self.ship[curr_x][curr_y] = self.colored_block('r')
                    fire.append((curr_x,curr_y))
                    for x, y in self.directions:
                        new_x, new_y = x + curr_x, y + curr_y
                        if 0 <= new_x < self.D and 0 <= new_y < self.D and self.ship[new_x][new_y] in possible_places:
                            fire_copy.add((new_x, new_y))
                else:
                    fire_copy.add(self.fire)
            fire_possibilties = fire_copy.copy()
            print(self)
            time.sleep(.25)

        if self.bot == self.button: 
            print("you won")
        else:
            print("you lost")
            
    def run_bot_3(self, q) -> None: # run with the type of bot you want
        possible_places = [self.colored_block('c'), 'O']
        fire_possibilties = set()
        curr_x, curr_y = self.fire
        fire = [self.fire]
        
        # Initial fire probable locations (up to 4)
        for x, y in self.directions:
            new_x, new_y = x + curr_x, y + curr_y
            if 0 <= new_x < self.D and 0 <= new_y < self.D and self.ship[new_x][new_y] == 'O':
                fire_possibilties.add((new_x, new_y)) 

        while self.bot != self.button:

            path = self.find_shortest_path(fire_possibilties)
                
            if (path is not None and path not in fire and self.bot not in fire):
                print("using possibilities path")
                next_step = path.pop(0)
                self.ship[self.bot[0]][self.bot[1]] = "O"
                print(next_step)
                self.bot = next_step
                self.ship[self.bot[0]][self.bot[1]] = self.colored_block('c')
            elif not path:
                print("using actual fire path")
                path = self.find_shortest_path(fire)
                if (path is not None and path not in fire and self.bot not in fire):
                    next_step = path.pop(0)
                    self.ship[self.bot[0]][self.bot[1]] = "O"
                    print(next_step)
                    self.bot = next_step
                    self.ship[self.bot[0]][self.bot[1]] = self.colored_block('c')
                else:
                    print("you lost")
                    return
            else:
                print("you lost")
                return

            fire_copy = fire_possibilties.copy()

            for fire_poss in fire_possibilties:
                curr_x, curr_y = fire_poss
                k = self.count_neighbors(curr_x, curr_y, self.colored_block('r')) # number of fires
                fire_spread_possibility = 1 - (1 - q) ** k
                rand = random.random()
                if fire_spread_possibility > rand:
                    self.ship[curr_x][curr_y] = self.colored_block('r')
                    fire.append((curr_x,curr_y))
                    for x, y in self.directions:
                        new_x, new_y = x + curr_x, y + curr_y
                        if 0 <= new_x < self.D and 0 <= new_y < self.D and self.ship[new_x][new_y] in possible_places:
                            fire_copy.add((new_x, new_y))
                else:
                    fire_copy.add(self.fire)
            fire_possibilties = fire_copy.copy()
            print(self)
            time.sleep(0.25)

        if self.bot == self.button: 
            print("you won")
        else:
            print("you lost")
            
    def run_bot_4(self, q) ->None:
        possible_places = [self.colored_block('c'), 'O']
        fire_possibilties = []
        curr_x, curr_y = self.fire
        fire = [self.fire]
        
        # Initial fire probable locations (up to 4)
        for x, y in self.directions:
            new_x, new_y = x + curr_x, y + curr_y
            if 0 <= new_x < self.D and 0 <= new_y < self.D and self.ship[new_x][new_y] == 'O':
                fire_possibilties.append((new_x, new_y))

        while self.bot != self.button:
            path = self.find_risky_path(fire_possibilties)
            if (path is not None and path not in fire and self.bot not in fire):
                print("using possibilities path")
                next_step = path.pop(0)
                self.ship[self.bot[0]][self.bot[1]] = "O"
                print(next_step)
                self.bot = next_step
                self.ship[self.bot[0]][self.bot[1]] = self.colored_block('c')
            elif not path:
                print("using actual fire path")
                path = self.find_risky_path(fire)
                if (path is not None and path not in fire and self.bot not in fire):
                    next_step = path.pop(0)
                    self.ship[self.bot[0]][self.bot[1]] = "O"
                    print(next_step)
                    self.bot = next_step
                    self.ship[self.bot[0]][self.bot[1]] = self.colored_block('c')
                else:
                    print("you lost")
                    return
            else:
                print("you lost")
                return

            fire_copy = fire_possibilties.copy()

            for fire_poss in fire_possibilties:
                curr_x, curr_y = fire_poss
                k = self.count_neighbors(curr_x, curr_y, self.colored_block('r')) # number of fires
                fire_spread_possibility = 1 - (1 - q) ** k
                rand = random.random()
                if fire_spread_possibility > rand:
                    self.ship[curr_x][curr_y] = self.colored_block('r')
                    fire.append((curr_x,curr_y))
                    for x, y in self.directions:
                        new_x, new_y = x + curr_x, y + curr_y
                        if 0 <= new_x < self.D and 0 <= new_y < self.D and self.ship[new_x][new_y] in possible_places:
                            fire_copy.append((new_x, new_y))
                else:
                    fire_copy.append(self.fire)
            fire_possibilties = fire_copy.copy()
            print(self)
            time.sleep(0.25)

        if self.bot == self.button:
            print("you won")
        else:
            print("you lost")
               
if __name__ == "__main__":
    ship = Ship()
    ship.generate_ship()
    print(ship)

    ans = int(input("Which bot do you want to run?\n1.Bot 1\n2.Bot 2\n3.Bot 3\n4.Bot 4\nBot: "))
    prob = float(input("What is the probablity: "))
    
    match ans:
        case 1:
            ship.run_bot_1(prob)
        case 2:
            ship.run_bot_2(prob)
        case 3:
            ship.run_bot_3(prob)
        case 4:
            ship.run_bot_4(prob)
