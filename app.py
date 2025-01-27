#!/usr/bin/env python3
import os
import sys
import json
import random
import string

from flask import Flask, render_template, Response, request, url_for, flash, redirect, jsonify
from werkzeug.exceptions import abort

import redis
from typing import List, Dict
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

class Player:
    __player_id: int = 0
    __player_name: str = ""
    __player_type: PlayerType = PlayerType.UNDEFINED
    __points: int = 0
    __isAdmin: bool = False
    __isReady: bool = False
    __isActive: bool = False
    __skipCount: int = 0

    def __init__(self, player_name=''):
        self.__player_id = generate_unique_id()
        self.__player_name = player_name

    def set_as_admin(self):
        self.__isAdmin = True

    def is_admin(self) -> bool:
        return self.__isAdmin

    def set_as_ready(self):
        self.__isReady = True

    def is_ready(self) -> bool: 
        return self.__isReady
    
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
        self.__isActive = True

    def widthdraw(self):
        self.__isActive = False

class Game:
    __game_id: int = 0
    __players: Player = []
    __players: List[Player] = []
    __isGameStarted: bool = False
    __activePlayerCount = 0

    def __init__(self):
        self.__game_id = generate_unique_id()
    
    def get_game_id(self) -> int:
        return self.__game_id

    def add_player(self) -> int:
        player = Player()
        self.__players.append(player)
        self.__activePlayerCount += 1
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

    def get_players_name(self):
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
                self.__activePlayerCount -= 1
                return True
        return False

    def start_game(self):
        self.__isGameStarted = True

    def end_game(self): 
        self.__isGameStarted = False

    def is_all_players_ready(self) -> bool:
        for player in self.__players:
            if not player.is_ready():
                return False
        return True

class GameStateMachine:
    __game: Game = None

    def __init__(self, game: Game):
        self.__game = game

class Letter:
    __letter: str = ""
    __points: int = 0

    def __init__(self, letter: str, points: int):
        self.__letter = letter
        self.__points = points

    def get_letter(self) -> str:
        return self.__letter

    def get_points(self) -> int:
        return self.__points

class TileBag:
    __tiles: List[str, int, int] = {}

    def __init__(self):
        pass
    
    def load_tiles(self, tiles: Dict[str, int]):
        self.__tiles = tiles.copy()

    def get_letter(self) -> str:
        letters = [letter for letter, count in self.__tiles.items() if count > 0]
        if not letters:
            return None  # No tiles left
        return random.choice(letters)

ENGLISH_TILES: Dict[str, int] = {
    'A': 9,
    'B': 2,
    'C': 2,
    'D': 4,
    'E': 12,
    'F': 2,
    'G': 3,
    'H': 2,
    'I': 9,
    'J': 1,
    'K': 1,
    'L': 4,
    'M': 2,
    'N': 6,
    'O': 8,
    'P': 2,
    'Q': 1,
    'R': 6,
    'S': 4,
    'T': 6,
    'U': 4,
    'V': 2,
    'W': 2,
    'X': 1,
    'Y': 2,
    'Z': 1,
    ' ': 2
}

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

@app.route("/redirect-lobby", methods=["POST"])
def redirect_lobby() -> Response:
    request_json = request.get_json()

    if request_json is None:
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    game_id = request_json.get("gameID")
    player_id = request_json.get("playerID")
    print(f"Game ID: {game_id}, Player ID: {player_id}")

    if not game_id:
        return jsonify({"status": "error", "message": "Missing or invalid gameID"}), 400   
    if not player_id:
        return jsonify({"status": "error", "message": "Missing or invalid playerID"}), 400

    for game in games:
        if game.get_game_id() == game_id:
            return redirect(url_for('lobby', game_id=game_id, user_id=player_id))
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
            player.set_as_ready()
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