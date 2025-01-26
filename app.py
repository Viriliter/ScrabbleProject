#!/usr/bin/env python3
import os
import sys
import json
import random
import string

from flask import Flask, render_template, Response, request, url_for, flash, redirect, jsonify
from werkzeug.exceptions import abort

import redis
from typing import List
redis_conn = redis.Redis()
try:
    IS_REDIS_CONNECTED = redis_conn.ping()
except:
    IS_REDIS_CONNECTED = False

app = Flask(__name__)
app.config["SECRET_KEY"] = "admin"

class Player:
    __player_id: int = 0
    __player_name: str = ""
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

    def is_admin(self):
        return self.__isAdmin

    def set_as_ready(self):
        self.__isReady = True

    def is_ready(self): 
        return self.__isReady
    
    def get_player_id(self):
        return self.__player_id

    def get_player_name(self):
        return self.__player_name

    def set_player_name(self, player_name):
        self.__player_name = player_name

    def get_points(self):
        return self.__points

    def set_points(self, points):
        self.__points = points

    def add_points(self, points):
        self.__points += points

    def remove_points(self, points):
        self.__points -= points

    def increment_skip_count(self):
        self.__skipCount += 1

    def get_skip_count(self):
        return self.__skipCount
    
    def enter_game(self):
        self.__isActive = True

    def widthdraw_game(self):
        self.__isActive = False

class Game:
    __game_id: int = 0
    __players: Player = []
    __players: List[Player] = []
    __isGameStarted: bool = False

    def __init__(self):
        self.__game_id = generate_unique_id()
    
    def get_game_id(self) -> int:
        return self.__game_id

    def add_player(self) -> int:
        player = Player()
        self.__players.append(player)
        return player.get_player_id()

    def set_admin(self, player_id) -> bool:
        for player in self.__players:
            if player.get_player_id() == player_id:
                player.set_as_admin()
                return True
        return False

    def set_player_name(self, player_id, player_name):
        for player in self.__players:
            if player.get_player_id() == player_id:
                player.set_player_name(player_name)
                return True
        return False

    def get_players_name(self):
        return [player.get_player_name() for player in self.__players]

    def is_game_started(self):
        return self.__isGameStarted

    def start_game(self):
        self.__isGameStarted = True

    def end_game(self): 
        self.__isGameStarted = False

games: List[Game] = []

def create_game() -> Game:
    game = Game()
    games.append(game)
    return game

def generate_unique_id(length=8):
    """Generate a random ID consisting of letters and digits."""
    characters = string.ascii_letters + string.digits
    unique_id = ''.join(random.choice(characters) for _ in range(length))
    return unique_id

@app.route("/")
def index():
    return render_template('lobby.html')

@app.route("/create-new-game", methods=["POST"])
def create_new_game():

    game = create_game()
    game_id = game.get_game_id()

    player_id = game.add_player()
    game.set_admin(player_id)

    return jsonify({"status": "success", "gameID": game_id, "playerID": player_id}), 200

@app.route("/join-game", methods=["POST"])
def join_game():
    request_json = request.get_json()

    if request_json is None:
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    for game in games:
        if game.get_game_id() == request_json["gameID"]:
            player_id = game.add_player()
            return jsonify({"status": "success", "playerID": player_id}), 200

    return jsonify({"status": "error", "message": "Game not found"}), 404

@app.route("/redirect-lobby", methods=["POST"])
def redirect_lobby():
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
def verify_word():
    request_json = request.get_json()

    tiles = request_json if isinstance(request_json, list) else []

    # Print each tile's properties
    for tile in tiles:
        print(f"Letter: {tile['letter']}, ID: {tile['tileID']}, Location: {tile['location']}")

    calculated_points = 10
    
    return jsonify({"status": "success", "points": calculated_points}), 200

@app.route("/settings")
def settings():
    return render_template('settings.html')

@app.route("/about")
def about():
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