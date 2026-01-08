import json
from dataclasses import dataclass
from typing import Tuple
import math
import random

from enum import Enum

class TransportType(Enum):
    TAXI = 1
    BUS = 2
    TUBE = 3
    BOAT = 4


@dataclass(slots=True)
class Node:
    x: int
    y: int
    id: int

@dataclass(slots=True)
class Move:
    player: int
    from_station: int
    to_station: int
    type: TransportType

@dataclass(frozen=True)
class GameState:
    turn: int
    player_locs: Tuple[int, ...] # (..., ..., ..., ...., ..., ...)
    player_cards: Tuple[Tuple, ...] #((taxi, ...), (bus, ...), (tube, ...), (black, ...), (2x, ...))
    current_player: int
    victory_flag: bool



class GameControll:
    def __init__(self):
        self.stopList = ReadStops('station_locations.json')

        self.state = None

        self.players = []
        self.random_locs = []

    def select_station(self, x, y):
        x_low, x_high = x - 23, x + 23
        y_low, y_high = y - 23, y + 23

        # Filter stations within bounding box
        match = [
            node for node in self.stopList
            if x_low <= node.x <= x_high and y_low <= node.y <= y_high
        ]

        return match

    def get_station_coords(self, station_id):
        node = next((n for n in self.stopList if n.id == station_id), None)
        return (node.x, node.y) if node is not None else None

    def add_player(self):
        number_of_players = len(self.players)
        player_name = f"Player: {number_of_players}"
        if number_of_players == 0:
            player_name = "Mister X"
        if number_of_players >= 6:
            return
        
        rand = random.randint(1, 199)
        while rand in self.random_locs:
            rand = random.randint(1, 199)

        self.players.append((player_name, rand))
        self.random_locs.append(rand)

        player_locs = tuple(player[1] for player in self.players)
        player_cards = tuple(self.get_startCards(i) for i in range(len(self.players)))
        self.state = GameState(turn= 0, player_locs= player_locs, player_cards= player_cards, current_player= 0, victory_flag= False)
        
    def set_player_pos(self, index: int, pos_string: str):
        if pos_string == "RNG":
            self.players[index] = (self.players[index][0], self.random_locs[index])
        elif  not pos_string.isdigit():
            return False
        else:
            self.players[index] = (self.players[index][0] ,int(pos_string))
        player_locs = tuple(player[1] for player in self.players)
        player_cards = tuple(self.get_startCards(i) for i in range(len(self.players)))
        self.state = GameState(turn= 0, player_locs= player_locs, player_cards= player_cards, current_player= 0, victory_flag= False)
        return True
        
    def delete_player(self):
        number_of_players = len(self.players)
        if number_of_players <= 3:
            return
        self.players.pop()
        self.random_locs.pop()
        player_locs = tuple(player[1] for player in self.players)
        player_cards = tuple(self.get_startCards(i) for i in range(len(self.players)))
        self.state = GameState(turn= 0, player_locs= player_locs, player_cards= player_cards, current_player= 0, victory_flag= False)

    def start_game(with_UI = True):
        pass

    def replay_game(log_file):
        pass

    def handle_map_redraw_event(wait_for_input):
        pass

    def handle_manual_input():
        pass
    def get_startCards(self, index):
        if index == 0:
            n = len(self.players) - 1
            #mr X get 4 taxi, 3 bus, 3 tube, n black tickets and two double turns
            return (("taxi", 4), ("bus", 3), ("tube", 3), ("black", n), ("x2" ,2))
        else:
            #detectives get 10 taxi, 8 bus and 4 tube tickets
            return (("taxi", 10), ("bus", 8), ("tube", 4), ("black", 0), ("x2" ,0))
        
        

    


    

    



def ReadStops(path):
    with open(path, 'r') as f:
        stops =  json.load(f)
    stopsList = []
    for stop in stops:
        stopsList.append(Node(stop['x'], stop['y'],  stop['id']))
    stopsList.sort(key=lambda n: n.y)  # secondary key

    return stopsList



    
    
    # Example: create nodes from stops
    


