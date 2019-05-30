from main import Piece, Board
from collections import OrderedDict
import numpy as np
# ======================== Class Player =======================================

rules = {'swim': ['Voi', 'Soi', 'Cho', 'Chuot'],
         'jump_horizontal': ['SuTu', 'Ho', 'Bao'],
         'jump_vertical': ['SuTu', 'Ho'],
         'strength': ['Chuot', 'Meo', 'Cho', 'Soi', 'Bao', 'Ho', 'SuTu', 'Voi'],
         }

black_trap = [(9, 3), (8, 4), (9, 5)]
red_trap = [(1, 3), (2, 4), (1, 5)]
goal = {'red': (9, 4), 'black': (1, 4)}



def distance(pos1, pos2):
    delta_x = pos1[0] - pos2[0]
    delta_y = pos1[1] - pos2[1]
    return np.sqrt(delta_x * delta_x + delta_y * delta_y)
def delta_distance(prev_pos, new_pos, goal):
    return distance(prev_pos, goal) - distance(new_pos, goal)

MIN_DISTANCE = distance((1,2), (9,4)) - distance((1,3), (9,4))
MAX_DISTANCE = delta_distance((3,3), (7,3), (9,4))
MAX_STRENGTH = 8
SCORE_GOAL = 100

weights = [0.99405269, 0.40658621, 0.9204814]

class Player():
    # student do not allow to change two first functions
    def __init__(self, str_name):
        self.str = str_name

    def __str__(self):
        return self.str

    # Student MUST implement this function
    # The return value should be a move that is denoted by:
        # piece: selected piece
        # (row, col): new position of selected piece

    def get_strength_score(self, animal):
        if(animal):
            return (rules['strength'].index(animal.type) + 1) / MAX_STRENGTH
        else:
            return 0

    def get_distance_score(self, animal, new_pos, team):
        if(team == 'red'):
            return (distance(animal.position, goal['red']) - distance(new_pos, goal['red'])) / MAX_DISTANCE
        else:
            return (distance(animal.position, goal['black']) - distance(new_pos, goal['black'])) / MAX_DISTANCE

    def get_goal_score(self, new_pos):
        if(new_pos in goal.values()):
            return SCORE_GOAL
        else:
            return 0

    def get_score(self, animal, opponent, new_pos, team):
        return  weights[0] * self.get_strength_score(animal) + \
                weights[1] * self.get_strength_score(opponent) + \
                weights[2] * self.get_distance_score(animal, new_pos, team) + \
                self.get_goal_score(new_pos)

    
    def reward(self, moving_case):
        strategy = moving_case.strategy
        piece = None
        new_pos = None
        max_score = -999
        score = 0
        for animal in strategy:
            l_move = strategy.get(animal)
            # print('animal', animal)
            # print('strength', self.get_strength_score(animal))
            # print('list move', l_move)
            for new_pos_ in l_move:
                opponent = moving_case.have_opponent(new_pos_)
                score = self.get_score(animal, opponent, new_pos_, moving_case.my_team)
                if(score > max_score):
                    piece = animal
                    new_pos = new_pos_
                    max_score = score
        return piece, new_pos
            


    def next_move(self, state):
        # piece = Piece('Voi', (6, 7))
        # new_pos = (7, 7)
        my_strategy = MovingCase(self.str, state)
        my_strategy.get_list_strategy()

        piece, new_pos = self.reward(my_strategy)
        return piece, new_pos


class MovingCase(object):
    def __init__(self, my_team, state):
        self.board_state = state
        if(my_team == 'red'):
            self.opponent_list = state.list_black
            self.ally_list = state.list_red
        else:
            self.opponent_list = state.list_red
            self.ally_list = state.list_black
        self.my_team = my_team
        self.strategy = {}

# public

    def get_ally_strength(self, my_animal):
        if(self.my_team == 'red'):
            if(my_animal.position in black_trap):
                return 0
        else:
            if(my_animal.position in red_trap):
                return 0
        return rules['strength'].index(my_animal.type) + 1

    def get_opponent_strength(self, opponent):
        if(self.my_team == 'red'):
            if(opponent.position in red_trap):
                return 0
        else:
            if(opponent.position in black_trap):
                return 0
        return rules['strength'].index(opponent.type) + 1

    def in_water(self, position):
        x = position[0]
        y = position[1]
        return ((x > 3 and x < 7) and ((y > 1 and y < 4) or (y > 4 and y < 7)))

    def is_change_enviroment(self, pre_pos, new_pos):
        if(self.in_water(pre_pos) and not self.in_water(new_pos)):
            return 1
        elif (not self.in_water(pre_pos) and self.in_water(new_pos)):
            return 1
        else:
            return 0

    def is_left_water(self, pos):
        return pos[0] > 3 and pos[0] < 7 and pos[1] == 1

    def is_middle_water(self, pos):
        return pos[0] > 3 and pos[0] < 7 and pos[1] == 4

    def is_right_water(self, pos):
        return pos[0] > 3 and pos[0] < 7 and pos[1] == 7

    def is_bellow_water(self, pos):
        return (pos[0] == 3 and pos[1] > 1 and pos[1] < 4) or \
                (pos[0] == 3 and pos[1] > 4 and pos[1] < 7)

    def is_above_water(self, pos):
        return (pos[0] == 7 and pos[1] > 1 and pos[1] < 4) or \
                (pos[0] == 7 and pos[1] > 4 and pos[1] < 7)

    def can_swim(self, my_animal):
        return (my_animal.type in rules.get('swim', 'nothing'))

    def have_opponent(self, new_pos):
        for opponent in self.opponent_list:
            if(opponent.position == new_pos):
                return opponent
        return None

    def have_ally(self, new_pos):
        for ally in self.ally_list:
            if(ally.position == new_pos):
                return ally
        return None


    def can_attack(self, my_animal, opponent):
        if(self.is_change_enviroment(my_animal.position, opponent.position)):
            return 0
        elif (my_animal.type == 'Chuot' and opponent.type == 'Voi'):
            return 1
        elif (my_animal.type == 'Voi' and opponent.type == 'Chuot'):
            return 0
        elif (self.get_ally_strength(my_animal) > self.get_opponent_strength(opponent)):
            return 1
        return 0

    def can_move_around(self, my_animal, new_pos):
        opponent = self.have_opponent(new_pos)
        ally = self.have_ally(new_pos)

        # khong duoc nhay vao hang cua minh
        if(self.my_team == 'red'):
            if(new_pos == (1, 4)):
                return 0
        else:
            if(new_pos == (9, 4)):
                return 0
        if(not self.is_valid_position(new_pos)):
            return 0
        if(opponent == None and ally == None):
            if(not self.in_water(new_pos)):
                return 1
            else:
                if(self.can_swim(my_animal)):
                    return 1
        elif(ally != None):
            return 0
        elif(opponent != None):
            if(self.can_attack(my_animal, opponent)):
                return 1
        return 0

    def is_valid_position(self, pos):
        x = pos[0]
        y = pos[1]
        return (1 if (x > 0 and x < 10 and y > 0 and y < 8) else 0)

    def get_list_move(self, my_animal):
        x = my_animal.position[0]
        y = my_animal.position[1]

        empty_list = []

        # check around of animal's position
        above_pos = (x, y+1)
        if(self.can_move_around(my_animal, above_pos)):
            empty_list.append(above_pos)

        bellow_pos = (x, y-1)
        if(self.can_move_around(my_animal, bellow_pos)):
            empty_list.append(bellow_pos)

        right_pos = (x+1, y)
        if(self.can_move_around(my_animal, right_pos)):
            empty_list.append(right_pos)

        left_pos = (x-1, y)
        if(self.can_move_around(my_animal, left_pos)):
            empty_list.append(left_pos)

        # check through water of animal's position
        if(my_animal.type in rules.get('jump_horizontal', 'nothing')):
            if(self.is_left_water(my_animal.position)):
                new_pos = (x, y + 3)
                if(self.can_move_around(my_animal, new_pos)):
                    empty_list.append(new_pos)
            elif(self.is_middle_water(my_animal.position)):
                new_pos_list = [(x, y-3), (x, y+3)]
                for new_pos in new_pos_list:
                    if(self.can_move_around(my_animal, new_pos)):
                        empty_list.append(new_pos)
            elif(self.is_right_water(my_animal.position)):
                new_pos = (x, y - 3)
                if(self.can_move_around(my_animal, new_pos)):
                    empty_list.append(new_pos)

        if (my_animal.type in rules.get('jump_vertical', 'nothing')):
            if(self.is_bellow_water(my_animal.position)):
                new_pos = (x+4, y)
                if(self.can_move_around(my_animal, new_pos)):
                    empty_list.append(new_pos)
            elif(self.is_above_water(my_animal.position)):
                new_pos = (x-4, y)
                if(self.can_move_around(my_animal, new_pos)):
                    empty_list.append(new_pos)
        return empty_list

    def get_list_strategy(self):
        for my_animal in self.ally_list:
            self.strategy[my_animal] = self.get_list_move(my_animal)
