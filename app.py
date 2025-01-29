#!/usr/bin/env python3
import os
import sys
import json
import random
import string

from flask import Flask, render_template, Response, request, url_for, flash, redirect, jsonify
from werkzeug.exceptions import abort

import redis
from typing import List, Dict, Tuple
redis_conn = redis.Redis()
try:
    IS_REDIS_CONNECTED = redis_conn.ping()
except:
    IS_REDIS_CONNECTED = False

app = Flask(__name__)
app.config["SECRET_KEY"] = "admin"

class PlayerType:
    UNDEFINED = "UNDEFINED"
    AI = "AI"
    HUMAN = "HUMAN"

class PlayerPrivileges:
    UNDEFINED = 0
    ADMIN = 1
    PLAYER = 2

class PlayerStates:
    UNDEFINED   = 0   # The player has not been initialized yet
    NOT_READY   = 1   # The player has entered lobby screen but not clicked the ready button yet
    READY       = 2   # After player has clicked the ready button on lobby screen
    WAITING     = 3   # Player is waiting for its next turn to play
    PLAYING     = 4   # Player is playing its turn
    WON         = 5   # Player has won the game
    LOST        = 6   # Player has lost the game

class Player:
    __player_id: int = 0
    __player_name: str = ""
    __player_type: PlayerType = PlayerType.UNDEFINED
    __player_state: PlayerStates = PlayerStates.UNDEFINED
    __isAdmin: PlayerPrivileges = PlayerPrivileges.UNDEFINED
    __points: int = 0
    __skipCount: int = 0

    def __init__(self, player_name=''):
        self.__player_id = generate_unique_id()
        self.__player_name = player_name

    def set_as_admin(self):
        self.__isAdmin = True

    def is_admin(self) -> bool:
        return self.__isAdmin

    def set_player_state(self, player_state: PlayerStates):
        self.__player_state = player_state

    def get_player_state(self) -> PlayerStates:
        return self.__player_state
   
    def get_player_id(self) -> int:
        return self.__player_id

    def get_player_name(self) -> str:
        return self.__player_name

    def set_player_name(self, player_name: str):
        self.__player_name = player_name

    def get_player_type(self) -> PlayerType:
        return self.__player_type

    def set_player_type(self, player_type: PlayerType):
        self.__player_type = player_type

    def get_points(self) -> int:
        return self.__points

    def set_points(self, points: int):
        self.__points = points

    def add_points(self, points: int):
        self.__points += points

    def remove_points(self, points: int):
        self.__points -= points

    def increment_skip_count(self):
        self.__skipCount += 1

    def get_skip_count(self) -> int:
        return self.__skipCount
    
    def enter_game(self):
        self.__player_state = PlayerStates.WAITING

    def widthdraw(self):
        self.__player_state = PlayerStates.LOST

class TileBag:
    __reference_tiles: Dict[str, Tuple[int, int]] = None
    __tiles: Dict[str, Tuple[int, int]] = {}
    __total_tiles: int = 0

    def __init__(self):
        self.__reference_tiles = {}
        self.__tiles = {}
        self.__total_tiles = 0

    def load(self, tiles: Dict[str, int]):
        self.__reference_tiles = tiles
        for letter, (count, points) in tiles.items():
            if letter in self.__tiles:
                self.__tiles[letter] = (self.__tiles[letter][0] + count, points)
            else:
                self.__tiles[letter] = (count, points)
            self.__total_tiles += count

    def get_random_letter(self) -> str:
        if self.__total_tiles == 0:
            return None  # Bag is empty
        
        # Randomly pick a letter
        letter = random.choice(list(self.__tiles.keys()))
        count, points = self.__tiles[letter]
        
        # Decrease the count of the letter in the bag
        if count > 1:
            self.__tiles[letter] = (count - 1, points)
        else:
            del self.__tiles[letter]  # Remove letter if no more left
        
        self.__total_tiles -= 1
        return letter

    def put_back_letter(self, letter: str):
        if letter in self.__tiles:
            count, points = self.__tiles[letter]
            self.__tiles[letter] = (count + 1, points)
        else:
            self.__tiles[letter] = (1, self.__reference_tiles[letter][1])
        self.__total_tiles += 1

    def get_total_tiles(self) -> int:
        return self.__total_tiles

class Game:
    __game_id: int = 0
    __players: List[Player] = []
    __player_count: int = 0
    __active_player_count = 0
    __isGameStarted: bool = False
    __tile_bag: TileBag = None
    __play_order: List[Player] = []

    def __init__(self, player_count=2):
        self.__game_id = generate_unique_id()
        self.__player_count = player_count
        self.__tile_bag = TileBag()

    def get_game_id(self) -> int:
        return self.__game_id

    def add_player(self) -> int:
        if (self.__active_player_count >= self.__player_count):
            return None
        player = Player()
        self.__players.append(player)
        self.__active_player_count += 1

        # FIXME: Add player to the play order list according to picked letter
        self.__play_order.append(player)

        return player.get_player_id()

    def set_player_as_admin(self, player_id) -> bool:
        for player in self.__players:
            if player.get_player_id() == player_id:
                player.set_as_admin()
                return True
        return False

    def set_player_name(self, player_id: int, player_name: str) -> bool:
        for player in self.__players:
            if player.get_player_id() == player_id:
                player.set_player_name(player_name)
                return True
        return False

    def get_players_name(self) -> List[str]:
        return [player.get_player_name() for player in self.__players]

    def found_player(self, player_id: int) -> Player:
        for player in self.__players:
            if player.get_player_id() == player_id:
                return player
        return None

    def is_game_has_admin(self) -> bool:
        for player in self.__players:
            if player.is_admin():
                return True
        return False

    def is_game_started(self) -> bool:
        return self.__isGameStarted
    
    def withdraw_player(self, player_id: int) -> bool:
        for player in self.__players:
            if player.get_player_id() == player_id:
                player.widthdraw()
                self.__active_player_count -= 1
                return True
        return False

    def start_game(self):
        self.__isGameStarted = True

    def end_game(self): 
        self.__isGameStarted = False

    def is_all_players_ready(self) -> bool:
        for player in self.__players:
            if not player.get_player_state() == PlayerStates.READY:
                return False
        return True

    def get_player_count(self) -> int:
        return len(self.__players)

    ##
    # @brief Calculate the point of the player's word and pass the turn to the next player
    # @param word The word that the player has played
    # @return The player who will play next
    ##
    def next_turn(self, player: Player, word: str) -> Player:
        pass
    
    ##
    # @brief Skip the turn of the current player
    # @return The player who will play next
    ##
    def skip_turn(self) -> Player:
        pass
    
    def check_game_over(self) -> bool:
        if (self.__active_player_count <= 1):
            return True
        if (self.__tile_bag.get_total_tiles() == 0):
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

class WordCalculator:
    __word: str = ""
    __word_points: int = 0

    def __init__(self, tiles: Dict[str, int], word: str):
        self.__word = word
        self.__word_points = 0

    def calculate_points(self) -> int:
        for letter in self.__word:
            self.__word_points += ENGLISH_TILES[letter][1]
        return self.__word_points

    def get_word_points(self) -> int:
        return self.__word_points

class GameStates:
    UNDEFINED               = 0  # Initial state
    WAITING_FOR_PLAYERS     = 1  # Waiting for players to join the game
    PLAYER_ORDER_SELECTION  = 2  # Players are selecting the order of play
    GAME_STARTED            = 3  # Game has started
    GAME_OVER               = 4  # Game is over

class GameStateMachine:
    __game: Game = None
    __turnCount: int = 0
    __state: GameStates = GameStates.UNDEFINED

    def __init__(self, game: Game):
        self.__game = game
        self.__state = GameStates.WAITING_FOR_PLAYERS

    def select_order(self):
        self.__state = GameStates.PLAYER_ORDER_SELECTION

    def start_game(self):
        self.__state = GameStates.GAME_STARTED

    def transition(self):
        if self.__state == GameStates.WAITING_FOR_PLAYERS:
            # Check if all players are ready
            if self.__game.is_all_players_ready():
                self.select_order()
        elif self.__state == GameStates.PLAYER_ORDER_SELECTION:
            # Check if all players have selected their order
            if self.__turnCount == len(self.__game.get_player_count()):
                self.start_game()
        elif self.__state == GameStates.GAME_STARTED:
            # Check if game is over
            if self.__game.check_game_over():
                self.__game.end_game()
                self.__state = GameStates.GAME_OVER
        elif self.__state == GameStates.GAME_OVER:
            pass
        else:
            raise ValueError("Invalid game state")
        self.__turnCount += 1

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

TILE_COUNT_PER_PLAYER: int = 8

games: List[Game] = []

def create_game() -> Game:
    game = Game()
    games.append(game)
    return game

def get_game(game_id) -> Game:
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
    return render_template('lobby.html')

@app.route("/create-new-game", methods=["POST"])
def create_new_game() -> Response:
    request_json = request.get_json()

    if request_json is None:
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    game = create_game()
    game_id = game.get_game_id()
    player_id = game.add_player()
    game.set_player_as_admin(player_id)
    isAdmin = True

    player_types = request_json if isinstance(request_json, list) else []
    for player_type in player_types:
        if player_type == "AI":
            player_id = game.add_player()
            game.found_player(player_id).set_player_name(PlayerType.AI)
            if not game.is_game_has_admin():
                game.found_player(player_id).set_as_admin()
        #elif player_type == "HUMAN":
        #    player_id = game.add_player()
        #    game.found_player(player_id).set_player_type(PlayerType.HUMAN)
        #    if not game.is_game_has_admin():
        #        game.found_player(player_id).set_as_admin()
        else:
            pass

    return jsonify({"status": "success", "gameID": game_id, "playerID": player_id, "isAdmin": isAdmin}), 200

@app.route("/join-game", methods=["POST"])
def join_game() -> Response:
    request_json = request.get_json()

    if request_json is None:
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    game_id = request_json["gameID"]
    game = get_game(game_id)

    if game is not None:
        if game.is_game_started():
            return jsonify({"status": "error", "message": "Game already started"}), 400

        player_id = game.add_player()
        isAdmin = False

        return jsonify({"status": "success", "gameID": game_id, "playerID": player_id, "isAdmin": isAdmin}), 200
    else:
        return jsonify({"status": "error", "message": "Game not found"}), 404

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

    for game in games:
        if game.get_game_id() == game_id:
            if game.is_game_started():
                return jsonify({"status": "error", "message": "Game already started"}), 400

            player = game.found_player(player_id)
            if player is not None:  # If player is found
                player.set_player_name(player_name)
                return jsonify({"status": "success", "gameID": game_id, "playerID": player_id, "playerName": player_name}), 200
            else:
                return jsonify({"status": "error", "message": "Player not found"}), 404

    return jsonify({"status": "error", "message": "Game not found"}), 404

@app.route("/ready-user", methods=["POST"])
def ready_user() -> Response:
    request_json = request.get_json()

    if request_json is None:
        return jsonify({"status": "error", "message": "Invalid request"}), 400
    
    game_id = request_json["gameID"]
    player_id = request_json["playerID"]

    game = get_game(game_id)
    if game is not None:
        if game.is_game_started():
            return jsonify({"status": "error", "message": "Game already started"}), 400

        player = game.found_player(player_id)
        if player is not None:
            player.set_player_state(PlayerStates.READY)
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "message": "Player not found"}), 404 
    else:
        return jsonify({"status": "error", "message": "Game not found"}), 404

@app.route("/redirect-game", methods=["POST"])
def redirect_game() -> Response:
    request_json = request.get_json()

    if request_json is None:
        return jsonify({"status": "error", "message": "Invalid request"}), 400
    
    game_id = request_json["gameID"]
    player_id = request_json["playerID"]
    print(f"Game ID: {game_id}, Player ID: {player_id}")

    for game in games:
        if game.get_game_id() == game_id:
            if game.is_game_started():
                return jsonify({"status": "error", "message": "Game already started"}), 400

            for player in game.__players:
                if player.get_player_id() == player_id:
                    player.enter_game()
                    return redirect(url_for('game', game_id=game_id, user_id=player_id))
            return jsonify({"status": "error", "message": "Player not found"}), 404
    return jsonify({"status": "error", "message": "Game not found"}), 404

@app.route("/verify-word", methods=["POST"])
def verify_word() -> Response:
    request_json = request.get_json()

    tiles = request_json if isinstance(request_json, list) else []

    # Print each tile's properties
    for tile in tiles:
        print(f"Letter: {tile['letter']}, ID: {tile['tileID']}, Location: {tile['location']}")

    calculated_points = 10
    
    return jsonify({"status": "success", "points": calculated_points}), 200

@app.route("/submit", methods=["POST"])
def submit() -> Response:
    request_json = request.get_json()

    if request_json is None:
        return jsonify({"status": "error", "message": "Invalid request"}), 400
    
    game_id = request_json.get("gameID")
    player_id = request_json.get("playerID")
    submitted_word = request_json.get("word")

    if not game_id or not player_id or not submitted_word:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400
    
    game = get_game(game_id)
    if game is not None:
        player = game.found_player(player_id)
        if player is not None:

            pass
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
    # TODO orientation info of mobile device is only obtained with https path so ssl certificate is needed.
    # You need to generate ssl certificate prior to run the project. Apply following steps:
    # 1-Run following commands in the terminal:
    #   $ openssl genrsa -des3 -out server.key 1024
    #   $ openssl req -new -key server.key -out server.csr
    #   $ cp server.key server.key.org
    #   $ openssl rsa -in server.key.org -out server.key
    #   $ openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
    # 2- Include .crt and .key files into the project folder:
    
    context = ('server.crt', 'server.key')  # certificate and key files

    if os.path.exists(context[0]) and os.path.exists(context[1]):
        app.run(host="0.0.0.0", debug=True, ssl_context=context)
    else:
        app.run(host="0.0.0.0", debug=True, ssl_context="adhoc")