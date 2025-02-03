#!/usr/bin/env python3
import os
import sys
import json
import random
import string

from typing import List, Dict, Tuple

from flask import Flask, render_template, Response, request, url_for, flash, redirect, jsonify
from flask_socketio import SocketIO, emit
from werkzeug.exceptions import abort

from game import PlayerMeta, PlayerType, PlayerState, Game

app = Flask(__name__)
app.config["SECRET_KEY"] = "admin"
socketio = SocketIO(app)

def create_game(player_count: int) -> Game:
    game = Game(socketio, player_count)
    games.append(game)
    return game

def get_game(game_id: str) -> Game:
    for game in games:
        if game.get_game_id() == game_id:
            return game
    return None

def update_lobby(game: Game):
    players_meta: List[PlayerMeta] = game.get_players_meta()
    # Emit the notification to all connected clients
    socketio.emit('update-lobby', {"playersMeta": [player.__dict__ for player in players_meta]})

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
    return render_template('game.html', game_id=game_id, player_id=player_id)

@app.route("/game/<game_id>/<player_id>/verify-word", methods=["POST"])
def verify_word(game_id: str, player_id: str) -> Response:
    request_json = request.get_json()

    tiles = request_json if isinstance(request_json, list) else []

    # Print each tile's properties
    for tile in tiles:
        print(f"Letter: {tile['letter']}, ID: {tile['tileID']}, Location: {tile['location']}")

    calculated_points = 10
    
    return jsonify({"status": "success", "points": calculated_points}), 200

@app.route("/verify-word", methods=["POST"])
def verify_word_debug() -> Response:
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

    # This container holds all game sessions in the server
    games: List[Game] = []

    if os.path.exists(context[0]) and os.path.exists(context[1]):
        app.run(host="0.0.0.0", debug=True, ssl_context=context)
    else:
        app.run(host="0.0.0.0", debug=True, ssl_context="adhoc")