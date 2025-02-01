#!/usr/bin/env python3
import os
import sys
import json
import random
import string

from typing import List, Dict, Tuple
from dataclasses import dataclass

from flask import Flask, render_template, Response, request, url_for, flash, redirect, jsonify
from flask_socketio import SocketIO, emit
from werkzeug.exceptions import abort

app = Flask(__name__)
app.config["SECRET_KEY"] = "admin"
socketio = SocketIO(app)

@dataclass(frozen=True)
class CL:
    row: int
    col: int

class CT:
    ORDINARY = 0
    DOUBLE_LETTER = 1
    DOUBLE_WORD = 2
    TRIPLE_LETTER = 3
    TRIPLE_WORD = 4

BOARD_ROW = 15

BOARD_COL = 15

# (CellLocation, CellType)
SPECIAL_CELLS: Dict[CL, CL] = {
    CL(0,0),    CT.TRIPLE_WORD,
    CL(0,7),    CT.TRIPLE_WORD,
    CL(0,14),   CT.TRIPLE_WORD,
    CL(7,0),    CT.TRIPLE_WORD,
    CL(7,14),   CT.TRIPLE_WORD,
    CL(14,0),   CT.TRIPLE_WORD,
    CL(14,7),   CT.TRIPLE_WORD,
    CL(14,14),  CT.TRIPLE_WORD,
    CL(1,5),    CT.TRIPLE_LETTER,
    CL(1,9),    CT.TRIPLE_LETTER,
    CL(5,1),    CT.TRIPLE_LETTER,
    CL(5,5),    CT.TRIPLE_LETTER,
    CL(5,9),    CT.TRIPLE_LETTER,
    CL(5,13),   CT.TRIPLE_LETTER,
    CL(9,1),    CT.TRIPLE_LETTER,
    CL(9,5),    CT.TRIPLE_LETTER,
    CL(9,9),    CT.TRIPLE_LETTER,
    CL(9,13),   CT.TRIPLE_LETTER,
    CL(13,5),   CT.TRIPLE_LETTER,
    CL(13,9),   CT.TRIPLE_LETTER,
    CL(7,7),    CT.DOUBLE_WORD, # Center Cell
    CL(1,1),    CT.DOUBLE_WORD,
    CL(2,2),    CT.DOUBLE_WORD,
    CL(3,3),    CT.DOUBLE_WORD,
    CL(4,4),    CT.DOUBLE_WORD,
    CL(10,10),  CT.DOUBLE_WORD,
    CL(11,11),  CT.DOUBLE_WORD,
    CL(12,12),  CT.DOUBLE_WORD,
    CL(13,13),  CT.DOUBLE_WORD,
    CL(1,13),   CT.DOUBLE_WORD,
    CL(2,12),   CT.DOUBLE_WORD,
    CL(3,11),   CT.DOUBLE_WORD,
    CL(4,10),   CT.DOUBLE_WORD,
    CL(10,4),   CT.DOUBLE_WORD,
    CL(11,3),   CT.DOUBLE_WORD,
    CL(12,2),   CT.DOUBLE_WORD,
    CL(13,1),   CT.DOUBLE_WORD,
    CL(0,3),    CT.DOUBLE_LETTER,
    CL(0,11),   CT.DOUBLE_LETTER,
    CL(2,6),    CT.DOUBLE_LETTER,
    CL(2,8),    CT.DOUBLE_LETTER,
    CL(3,0),    CT.DOUBLE_LETTER,
    CL(3,7),    CT.DOUBLE_LETTER,
    CL(3,14),   CT.DOUBLE_LETTER,
    CL(6,2),    CT.DOUBLE_LETTER,
    CL(6,6),    CT.DOUBLE_LETTER,
    CL(6,8),    CT.DOUBLE_LETTER,
    CL(6,12),   CT.DOUBLE_LETTER,
    CL(7,3),    CT.DOUBLE_LETTER,
    CL(7,11),   CT.DOUBLE_LETTER,
    CL(8,2),    CT.DOUBLE_LETTER,
    CL(8,6),    CT.DOUBLE_LETTER,
    CL(8,8),    CT.DOUBLE_LETTER,
    CL(8,12),   CT.DOUBLE_LETTER,
    CL(11,0),   CT.DOUBLE_LETTER,
    CL(11,7),   CT.DOUBLE_LETTER,
    CL(11,14),  CT.DOUBLE_LETTER,
    CL(12,6),   CT.DOUBLE_LETTER,
    CL(12,8),   CT.DOUBLE_LETTER,
    CL(14,3),   CT.DOUBLE_LETTER,
    CL(14,11),  CT.DOUBLE_LETTER
} 

# Letter: (Points, Count)
ENGLISH_TILES: Dict[str, Tuple[int, int]] = {
    'A': (9, 1),
    'B': (2, 3),
    'C': (2, 3),
    'D': (4, 2),
    'E': (12, 1),
    'F': (2, 4),
    'G': (3, 2),
    'H': (2, 4),
    'I': (9, 1),
    'J': (1, 8),
    'K': (1, 5),
    'L': (4, 1),
    'M': (2, 3),
    'N': (6, 1),
    'O': (8, 1),
    'P': (2, 3),
    'Q': (1, 10),
    'R': (6, 1),
    'S': (4, 1),
    'T': (6, 1),
    'U': (4, 1),
    'V': (2, 4),
    'W': (2, 4),
    'X': (1, 8),
    'Y': (2, 4),
    'Z': (1, 10),
    ' ': (2, 0)
}

# Declare initial tile count for each player
INITIAL_TILE_COUNT: int = 7

AI_PLAYER_NAMES = ["William", "Olivia", "Benjamin", "Charlotte"]

@dataclass(frozen=True)
class LETTER:
    row: int
    col: int
    letter: chr

# Define WORD as a List of LETTERs
WORD = List[LETTER]

class TileBag:
    __reference_tiles: Dict[str, Tuple[int, int]] = None
    __tiles: Dict[str, Tuple[int, int]] = {}
    __remaning_tiles: int = 0

    def __init__(self):
        self.__reference_tiles = {}
        self.__tiles = {}
        self.__remaning_tiles = 0

    def load(self, tiles: Dict[str, int]) -> None:
        self.__reference_tiles = tiles
        for letter, (count, points) in tiles.items():
            if letter in self.__tiles:
                self.__tiles[letter] = (self.__tiles[letter][0] + count, points)
            else:
                self.__tiles[letter] = (count, points)
            self.__remaning_tiles += count

    def get_random_letter(self) -> chr:
        if self.__remaning_tiles == 0:
            return None  # Bag is empty
        
        # Randomly pick a letter
        letter = random.choice(list(self.__tiles.keys()))
        count, points = self.__tiles[letter]
        
        # Decrease the count of the letter in the bag
        if count > 1:
            self.__tiles[letter] = (count - 1, points)
        else:
            del self.__tiles[letter]  # Remove letter if no more left
        
        self.__remaning_tiles -= 1
        return letter

    def put_back_letter(self, letter: chr) -> None:
        if letter in self.__tiles:
            count, points = self.__tiles[letter]
            self.__tiles[letter] = (count + 1, points)
        else:
            self.__tiles[letter] = (1, self.__reference_tiles[letter][1])
        self.__remaning_tiles += 1

    def get_remaining_tiles(self) -> int:
        return self.__remaning_tiles

class Rack:
    __tile_bag: TileBag = None
    __rack: List[chr] = []

    def __init__(self, tile_bag: TileBag):
        self.__tile_bag = tile_bag
        self.initialize()

    def add_to_rack(self) -> None:
        letter = self.__tile_bag.get_random_letter()
        self.__rack.append(letter)

    def remove_from_rack(self, letter: chr) -> None:
        self.__rack.remove(letter)

    def get_rack_length(self) -> int:
        return self.__rack.__len__()

    def get_letters(self) -> List[chr]:
        return self.__rack.copy()

    def replenish_rack(self) -> None:
        while self.get_rack_length() < INITIAL_TILE_COUNT and self.__tile_bag.get_remaining_tiles() > 0:
            self.add_to_rack()

    def initialize(self) -> None:
        for _ in range(INITIAL_TILE_COUNT):
            self.add_to_rack()

class Dictionary:
    __tiles: Dict[str, int] = {}

    def __init__(self, tiles: Dict[str, int]):
        self.__tiles = tiles.copy()

    @staticmethod
    def validate_word(word: str) -> bool:
        return False

    @staticmethod
    def calculate_points(word: str) -> int:
        word_points = 0
        for letter in word:
            word_points += Dictionary.__tiles[letter][1]
        return word_points

    @staticmethod
    def get_word_points(word: str) -> int:
        return Dictionary.calculate_points(word)

class PlayerType:
    UNDEFINED = "UNDEFINED"
    AI = "AI"
    HUMAN = "HUMAN"

class PlayerPrivileges:
    UNDEFINED = 0
    ADMIN = 1
    PLAYER = 2

class PlayerState:
    UNDEFINED   = 0   # The player has not been initialized yet
    NOT_READY   = 1   # The player has entered lobby screen but not clicked the ready button yet
    READY       = 2   # After player has clicked the ready button on lobby screen
    WAITING     = 3   # Player is waiting for its next turn to play
    PLAYING     = 4   # Player is playing its turn
    WON         = 5   # Player has won the game
    LOST        = 6   # Player has lost the game

@dataclass(frozen=True)
class PlayerMeta:
    PLAYER_ID: int
    PLAYER_NAME: str
    PLAYER_TYPE: PlayerType
    PLAYER_STATE: PlayerState
    IS_ADMIN: bool
    PLAY_ORDER: int
    PLAYER_POINT: int

class Player:
    __player_id: str = ''
    __player_name: str = ""
    __player_type: PlayerType = PlayerType.UNDEFINED
    __player_state: PlayerState = PlayerState.UNDEFINED
    __is_admin: PlayerPrivileges = PlayerPrivileges.UNDEFINED
    __points: int = 0
    __skipCount: int = 0
    __play_order: int = -1
    __rack: Rack = None

    def __init__(self, player_type=PlayerType.HUMAN):
        self.__player_id = generate_unique_id()
        self.__player_type = player_type

        if self.__player_type == PlayerType.AI:
            self.set_player_state(PlayerState.READY)

    def set_as_admin(self) -> None:
        self.__is_admin = True

    def is_admin(self) -> bool:
        if self.__is_admin == PlayerPrivileges.ADMIN: return True
        else: return False

    def set_player_state(self, player_state: PlayerState) -> None:
        self.__player_state = player_state

    def get_player_state(self) -> PlayerState:
        return self.__player_state
   
    def get_player_id(self) -> str:
        return self.__player_id

    def get_player_name(self) -> str:
        return self.__player_name

    def set_player_name(self, player_name: str) -> None:
        self.__player_name = player_name

    def get_play_order(self) -> int:
        return self.__play_order

    def set_play_order(self, play_order: int) -> None:
        self.__play_order = play_order

    def get_player_meta(self) -> PlayerMeta:
        return PlayerMeta(self.__player_id, self.__player_name, self.__player_type, self.__player_state, self.is_admin(), self.__play_order, self.__points)

    def get_player_type(self) -> PlayerType:
        return self.__player_type

    def set_player_type(self, player_type: PlayerType) -> None:
        self.__player_type = player_type

    def get_points(self) -> int:
        return self.__points

    def set_points(self, points: int) -> None:
        self.__points = points

    def add_points(self, points: int) -> None:
        self.__points += points

    def remove_points(self, points: int) -> None:
        self.__points -= points

    def increment_skip_count(self) -> None:
        self.__skipCount += 1

    def get_skip_count(self) -> int:
        return self.__skipCount
    
    def enter_game(self, tile_bag: TileBag) -> None:
        self.__player_state = PlayerState.READY
        self.__rack = Rack(tile_bag)

    def widthdraw(self) -> None:
        self.__player_state = PlayerState.LOST

    def play_turn(self, word: WORD) -> None:
        if not (self.__player_state == PlayerState.PLAYING):
            return

    def remove_from_rack(self, letter: chr) -> None:
        self.__rack.remove_from_rack(letter)

class Board:
    __row: int = 0
    __col: int = 0
    __cells: List[chr] = []
    __special_cells: Dict[CL, CL] = {}
    __tiles: Dict[str, Tuple[int, int]]
    
    def __init__(self, row=BOARD_ROW, col=BOARD_COL, tiles=ENGLISH_TILES, special_cells=SPECIAL_CELLS):
        self.__row = row
        self.__col = col
        self.__special_cells = special_cells.copy()
        self.__tiles = tiles.copy()

        #Dictionary(ENGLISH_TILES)

        self.clear()

    def is_placable(self, letter: LETTER) -> bool:
        if not (self.__cells[letter.row][letter.col] == ''):
            return True
        else:
            return False

    def place_tile(self, letter: LETTER) -> bool:
        if self.is_placable(letter):
            self.__cells[letter.row][letter.col] == letter.letter
            return True
        else:
            # Cannot be placed to already occupied cell
            return False

    def place_word(self, word: WORD) -> bool:
        is_placed = True
        for letter in word:
            is_placed &= self.place_tile(letter)
        return is_placed

    def calculate_points(self, word: WORD) -> int:
        for letter in word:
            if not self.is_placable(letter): return 0

        return 0

    def clear(self) -> None:
        self.__cells = [['' for _ in range(self.__col)] for _ in range(self.__row)]


class GameState:
    UNDEFINED               = 0  # Initial state
    WAITING_FOR_PLAYERS     = 1  # Waiting for players to join the game
    PLAYER_ORDER_SELECTION  = 2  # Players are selecting the order of play
    GAME_STARTED            = 3  # Game has started
    GAME_OVER               = 4  # Game is over

class Game:
    __game_id: str = ''
    __state: GameState = GameState.UNDEFINED

    __players: List[Player] = []
    __player_order: List[Player] = []
    __player_count: int = 0
    __active_player_count = 0

    __tile_bag: TileBag = None

    __board: Board = None

    __order_counter: int = -1
    __turn_count: int = 0

    def __init__(self, player_count=2):
        self.__game_id = generate_unique_id()
        self.__player_count = player_count
        self.__tile_bag = TileBag()
        self.__players.clear()
        self.__player_order.clear()
        self.__board.clear()

        self.__set_state(GameState.WAITING_FOR_PLAYERS)

    def get_game_id(self) -> str:
        return self.__game_id

    def get_game_state(self) -> GameState:
        return self.__state

    def __set_state(self, state: GameState):
        self.__state = state
        self.update(self)

    def create_player(self, player_type=PlayerType.HUMAN) -> str:
        if (self.__active_player_count >= self.__player_count):
            return -1
        
        player = Player(player_type)
        self.__players.append(player)
        self.__active_player_count += 1

        # FIXME: Add player to the play order list according to picked letter
        self.__player_order.append(player)

        return player.get_player_id()

    def set_player_as_admin(self, player_id: str) -> bool:
        for player in self.__players:
            if player.get_player_id() == player_id:
                player.set_as_admin()
                return True
        return False

    def set_player_name(self, player_id: str, player_name: str) -> bool:
        for player in self.__players:
            if player.get_player_id() == player_id:
                player.set_player_name(player_name)
                return True
        return False

    def get_players_name(self) -> List[str]:
        return [player.get_player_name() for player in self.__players]

    def get_players_meta(self) -> List[PlayerMeta]:
        return [player.get_player_meta() for player in self.__players]

    def found_player(self, player_id: str) -> Player:
        for player in self.__players:
            if player.get_player_id() == player_id:
                return player
        return None

    def get_player_count(self) -> int:
        return len(self.__players)

    def get_player_order(self, player_id: str) -> int:
        order_counter = 0
        for player in self.__player_order:
            if (player.get_player_id() == player_id):
                return order_counter
        return -1  # No player order found with provided id       

    def get_first_player(self) -> Player:
        return None if self.__player_order.__len__() == 0 else self.__player_order[0]

    def is_all_players_ready(self) -> bool:
        for player in self.__players:
            if not player.get_player_state() == PlayerState.READY:
                return False
        return True

    def is_game_has_admin(self) -> bool:
        for player in self.__players:
            if player.is_admin():
                return True
        return False

    def is_game_started(self) -> bool:
        return self.get_game_state() == GameState.GAME_STARTED
    
    def withdraw_player(self, player_id: str) -> bool:
        player = self.found_player(player_id)
        if player is None:
            return False
        else:
            player.widthdraw()
            self.__active_player_count -= 1
            return True

    def shuffle_order() -> None:
        pass
    
    def enter_player_to_game(self, player_id: str) -> bool:
        player = self.found_player(player_id)
        if player is None:
            return False
        else:
            player.enter_game(self.__tile_bag)
        
        if not self.is_all_players_ready():
            return True

        # If all players in ready state (aka entered the game), 
        # then set all players state to waiting
        for player in self.__players:
            player.set_player_state(PlayerState.WAITING)

        self.__set_state(GameState.PLAYER_ORDER_SELECTION)
        update_game()

        return True

    def update_clients(self) -> None:
        players_meta: List[PlayerMeta] = self.get_players_meta()
        # Emit the notification to all connected clients
        socketio.emit('update-game', {"playersMeta": [player.__dict__ for player in players_meta]})
        #socketio.emit('update-board', {"board": [player.__dict__ for player in players_meta]})

    def update(self) -> None:
        if self.__state == GameState.WAITING_FOR_PLAYERS:
            # Check if all players are ready
            if self.is_all_players_ready():
                self.__set_state(GameState.PLAYER_ORDER_SELECTION)
        elif self.__state == GameState.PLAYER_ORDER_SELECTION:
            # Check if all players have selected their order
            if self.__turn_count == len(self.get_player_count()):
                self.__set_state(GameState.GAME_STARTED)
        elif self.__state == GameState.GAME_STARTED:
            # Check if game is over
            if self.check_game_over():
                self.__set_state(GameState.GAME_OVER)
                self.__state = GameState.GAME_OVER
            else:
                if (self.__currentPlayer == None):
                    self.__currentPlayer = self.get_first_player()
                    self.__currentPlayer.set_player_state(PlayerState.PLAYING)
                
                iter = 0
                while self.__currentPlayer.get_player_state != PlayerState.PLAYING and iter < self.__player_count:
                    self.__currentPlayer = self.next_turn()  # Move to next player

                self.__currentPlayer.set_player_state(PlayerState.PLAYING)

        elif self.__state == GameState.GAME_OVER:
            pass
        else:
            raise ValueError("Invalid game state")

        self.update_clients()

    def submit(self, player_id: str, word: WORD) -> int:
        if self.__state != GameState.GAME_STARTED:
            return
        
        player = self.found_player(player_id)
        if player is None:
            return

        # Only current player submit its word
        if not (player.get_player_id() == self.__currentPlayer.get_player_id()):
            return

        points = self.__board.calculate_points()

        if points > 0:
            player.add_points(points)

            for letter in word:
                player.remove_from_rack(letter.letter)

            self.update()

        return points

    ##
    # @brief Calculate the point of the player's word and pass the turn to the next player
    # @param word The word that the player has played
    # @return The player who will play next
    ##
    def next_turn(self) -> Player:
        self.__order_counter = (self.__order_counter + 1) % self.__player_order.__len__()
        return self.__order_counter[self.__order_counter]
    
    ##
    # @brief Skip the turn of the current player
    # @return The player who will play next
    ##
    def skip_turn(self) -> Player:
        self.__order_counter = (self.__order_counter + 1) % self.__player_order.__len__()
        return self.__order_counter[self.__order_counter]
    
    def check_game_over(self) -> bool:
        if (self.__active_player_count <= 1):
            return True
        if (self.__tile_bag.get_remaining_tiles() == 0):
            return True
        
        skip_count_flag = True
        for player in self.__players:
            if player.get_skip_count() >= 2:
                skip_count_flag &= True
        if (skip_count_flag):
            return True
        
        return False

    def get_winner(self) -> Player:
        max_points = 0
        winner = None
        for player in self.__players:
            if player.get_points() > max_points and player.is_active():
                max_points = player.get_points()
                winner = player
        return winner

class GameStateMachine:
    __game: Game = None
    __turnCount: int = 0
    __state: GameState = GameState.UNDEFINED
    __currentPlayer: Player = None

    def __init__(self, game: Game):
        self.__game = game
        self.__state = GameState.WAITING_FOR_PLAYERS

    def get_game(self):
        return self.__game

    def select_order(self):
        self.__state = GameState.PLAYER_ORDER_SELECTION
        self.__game.shuffle_order()

    def start_game(self):
        self.__state = GameState.GAME_STARTED

    def transition(self):
        if self.__state == GameState.WAITING_FOR_PLAYERS:
            # Check if all players are ready
            if self.__game.is_all_players_ready():
                self.select_order()
        elif self.__state == GameState.PLAYER_ORDER_SELECTION:
            # Check if all players have selected their order
            if self.__turnCount == len(self.__game.get_player_count()):
                self.start_game()
        elif self.__state == GameState.GAME_STARTED:
            # Check if game is over
            if self.__game.check_game_over():
                self.__game.end_game()
                self.__state = GameState.GAME_OVER
            else:
                if (self.__currentPlayer == None):
                    self.__currentPlayer = self.__game.get_first_player()
                
                while self.__currentPlayer.get_player_state != PlayerState.PLAYING:
                    self.__currentPlayer = self.__game.next_turn()  # Move to next player

        elif self.__state == GameState.GAME_OVER:
            pass
        else:
            raise ValueError("Invalid game state")
        self.__turnCount += 1

games: List[Game] = []

def create_game(player_count: int) -> Game:
    game = Game(player_count)
    games.append(game)
    return game

def get_game(game_id: str) -> Game:
    for game in games:
        if game.get_game_id() == game_id:
            return game
    return None

def generate_unique_id(length=8) ->str :
    """Generate a random ID consisting of letters and digits."""
    characters = string.ascii_letters + string.digits
    unique_id = ''.join(random.choice(characters) for _ in range(length))
    return unique_id

@app.route("/")
def index() -> Response:
    return render_template('game.html')

@app.route("/create-new-game", methods=["POST"])
def create_new_game() -> Response:
    request_json = request.get_json()

    if request_json is None:
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    player_types = request_json if isinstance(request_json, list) else []

    game = create_game(player_types.__len__())
    game_id = game.get_game_id()

    admin_player_id = -1

    player_type = player_types[0]
    if player_type == "AI":
        player_id = game.create_player(PlayerType.AI)
    elif player_type == "HUMAN":
        player_id = game.create_player(PlayerType.HUMAN)
    else:
        return jsonify({"status": "error", "message": "Invalid player type"}), 400

    if not game.is_game_has_admin():
        game.found_player(player_id).set_as_admin()
        admin_player_id = player_id

    update_lobby(game)

    # Player that creates the game is always admin
    return jsonify({"status": "success", "gameID": game_id, "playerID": admin_player_id, "isAdmin": True}), 200

@app.route("/join-game", methods=["POST"])
def join_game() -> Response:
    request_json = request.get_json()

    if request_json is None:
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    game_id = request_json["gameID"]
    player_type = request_json["playerType"]

    game = get_game(game_id)
    if game is None:
        return jsonify({"status": "error", "message": "Game not found"}), 404
    else:
        if game.is_game_started():
            return jsonify({"status": "error", "message": "Game already started"}), 400

        if player_type == "AI":
            player_id = game.create_player(PlayerType.AI)
        elif player_type == "HUMAN":
            player_id = game.create_player(PlayerType.HUMAN)
        else:
            return jsonify({"status": "error", "message": "Invalid player type"}), 400

        player = game.found_player(player_id)
        update_lobby(game)

        return jsonify({"status": "success", "gameID": game.get_game_id(), "playerID": player.get_player_id(), "isAdmin": player.is_admin()}), 200

@app.route("/set-player-name", methods=["POST"])
def set_player_name() -> Response:
    request_json = request.get_json()

    if request_json is None:
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    game_id = request_json.get("gameID")
    player_id = request_json.get("playerID")
    player_name = request_json.get("playerName")

    if not game_id or not player_id or not player_name:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400

    game = get_game(game_id)
    if game is None:
        return jsonify({"status": "error", "message": "Game not found"}), 404
    else:
        if game.is_game_started():
            return jsonify({"status": "error", "message": "Game already started. Cannot change player name"}), 400

        player = game.found_player(player_id)
        if player is not None:  # If player is found
            player.set_player_name(player_name)
    
            update_lobby(game)

            return jsonify({"status": "success", "gameID": game_id, "playerID": player_id, "playerName": player_name}), 200
        else:
            return jsonify({"status": "error", "message": "Player not found"}), 404

@app.route("/ready-user", methods=["POST"])
def ready_user() -> Response:
    request_json = request.get_json()

    if request_json is None:
        return jsonify({"status": "error", "message": "Invalid request"}), 400
    
    game_id = request_json["gameID"]
    player_id = request_json["playerID"]

    game = get_game(game_id)
    if game is None:
        return jsonify({"status": "error", "message": "Game not found"}), 404
    else:
        if game.is_game_started():
            return jsonify({"status": "error", "message": "Game already started. Cannot set player to ready state"}), 400

        player = game.found_player(player_id)
        if player is not None:
            player.set_player_state(PlayerState.READY)
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "message": "Player not found"}), 404 

def update_lobby(game: Game):
    players_meta: List[PlayerMeta] = game.get_players_meta()
    # Emit the notification to all connected clients
    socketio.emit('update-lobby', {"playersMeta": [player.__dict__ for player in players_meta]})

@app.route("/enter-game", methods=["POST"])
def enter_game() -> Response:
    request_json = request.get_json()

    if request_json is None:
        return jsonify({"status": "error", "message": "Invalid request"}), 400
    
    game_id = request_json["gameID"]
    player_id = request_json["playerID"]

    print(f"Player trying to enter game (Game ID: {game_id}, Player ID: {player_id})")

    game = get_game(game_id)
    if game is None:
        return jsonify({"status": "error", "message": "Game not found"}), 404
    else :
        if game.is_game_started():
            return jsonify({"status": "error", "message": "Game already started"}), 400

        is_entered = game.enter_player_to_game(player_id)
        update_lobby(game)

        if is_entered:
            return redirect(url_for('game', game_id=game_id, user_id=player_id))
        else:
            return jsonify({"status": "error", "message": "Player cannot enter to game"}), 400

@app.route("/game/<game_id>/<player_id>")
def game(game_id: str, player_id: str) -> Response:
    # Your logic to render the game page
    return render_template('game.html', game_id=game_id, user_id=user_id)

@app.route("/game/<game_id>/<player_id>/verify-word", methods=["POST"])
def verify_word(game_id: str, player_id: str) -> Response:
    request_json = request.get_json()

    tiles = request_json if isinstance(request_json, list) else []

    # Print each tile's properties
    for tile in tiles:
        print(f"Letter: {tile['letter']}, ID: {tile['tileID']}, Location: {tile['location']}")

    calculated_points = 10
    
    return jsonify({"status": "success", "points": calculated_points}), 200

@app.route("/game/<game_id>/<player_id>/submit", methods=["POST"])
def submit(game_id: str, player_id: str) -> Response:
    request_json = request.get_json()

    if request_json is None:
        return jsonify({"status": "error", "message": "Invalid request"}), 400
    
    #game_id = request_json.get("gameID")
    #player_id = request_json.get("playerID")
    submitted_word = request_json.get("word")

    if not game_id or not player_id or not submitted_word:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400
    
    game = get_game(game_id)
    if game is not None:
        player = game.found_player(player_id)
        if player is not None:
            calculated_point = game.submit(player_id, submitted_word)  # FIXME convert to WORD type
            if calculated_point > 0:
                return jsonify({"status": "success", "point": calculated_point}), 200
            else:
                return jsonify({"status": "error", "message": "Word cannot be submitted"}), 400
        else:
            return jsonify({"status": "error", "message": "Player not found"}), 404
    else:
        return jsonify({"status": "error", "message": "Game not found"}), 404

@app.route("/settings")
def settings() -> Response:
    return render_template('settings.html')

@app.route("/about")
def about() -> Response:
    return render_template('about.html')

if __name__ == "__main__":
    # You need to generate ssl certificate prior to run the project 
    # if you do not want to ssl certification failure in browser. 
    # Apply following steps:
    # 1-Run following commands in the terminal:
    #   $ openssl genrsa -des3 -out server.key 1024
    #   $ openssl req -new -key server.key -out server.csr
    #   $ cp server.key server.key.org
    #   $ openssl rsa -in server.key.org -out server.key
    #   $ openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
    # 2- Include .crt and .key files into the project folder ./cert :
    

    context = ("./cert/---.crt", "./cert/---.key")  # certificate and key files (if needed rename them)

    if os.path.exists(context[0]) and os.path.exists(context[1]):
        app.run(host="0.0.0.0", debug=True, ssl_context=context)
    else:
        app.run(host="0.0.0.0", debug=True, ssl_context="adhoc")