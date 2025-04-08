#!/usr/bin/env python3
import os
import sys
import json
import random
import string
import threading

from typing import List, Dict, Tuple

from flask import Flask, render_template, Response, request, url_for, flash, redirect, jsonify
from flask_socketio import SocketIO, emit
from werkzeug.exceptions import abort

from game import PlayerMeta, PlayerType, PlayerState, GameState, Scrabble, verbalize
from game.enums import PlayerStrategy
from game.globals import TILE

app = Flask(__name__)
app.config["SECRET_KEY"] = "admin"
socketio = SocketIO(app, cors_allowed_origins="*")

# This container holds all game sessions in the server
games: List[Scrabble] = []

GAME_CLEAN_INTERVAL = 10  # in seconds

def clean_games() -> None:
    global games
    for game in games:
        print(game.get_game_state())
        if game.get_game_state() == GameState.GAME_OVER:
            print(f"GameID: {game.get_game_id()} cleaned.")
            games.remove(game)
            break

    threading.Timer(GAME_CLEAN_INTERVAL, clean_games).start()  # Run every 10 seconds

def create_game(player_types: int) -> Scrabble:
    game = Scrabble(socketio, len(player_types))   
    games.append(game)
    return game

def get_game(game_id: str) -> Scrabble:
    for game in games:
        if game.get_game_id() == game_id:
            return game
    return None

def update_lobby(game: Scrabble) -> None:
    players_meta: List[PlayerMeta] = game.get_players_meta()
    # Emit the notification to all connected clients
    socketio.emit('update-lobby', {"playersMeta": [player.__dict__ for player in players_meta]})

def extract_url(url: str) -> (Tuple[str, str] | Tuple[None, None]):
    if url is None:
        return None, None

    parts = url.split("/")
    if len(parts) >= 6:
        game_id = parts[-2]
        player_id = parts[-1]
        return game_id, player_id
    
    return None, None

@socketio.on("connect")
def handle_connect():
    sid = request.sid  # Unique session ID for each client
    path = request.headers.get("Referer")  # Get the URL from which client connected

    game_id, player_id = extract_url(path)
    if game_id is None or player_id is None:
        return

    game = get_game(game_id)
    if game is None:
        return
    
    # If player is referee, add referee SID
    # Otherwise, add player SID
    if player_id == "referee": game.add_referee_sid(sid, player_id)
    else: game.add_sid(sid, player_id)
    print(f"APP >>> Player {player_id} joined Game {game_id} (SID: {sid})")

@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    path = request.headers.get("Referer")  # Get the URL from which client disconnected

    game_id, player_id = extract_url(path)
    if game_id is None or player_id is None:
        return

    game = get_game(game_id)
    if game is None:
        return

    if player_id == "referee": game.remove_referee_sid(sid, player_id)
    else: game.remove_sid(sid, player_id)
    print(f"APP >>> Player {player_id} disconnected from Game {game_id} (SID: {sid})")

# Home Page

@app.route("/")
def index() -> Response:
    return render_template('lobby.html')

# Lobby POSTS

@app.route("/create-new-game", methods=["POST"])
def create_new_game() -> Response:
    request_json = request.get_json()

    if request_json is None:
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    player_types = request_json if isinstance(request_json, list) else []

    game = create_game(player_types)
    if game is None:
        return jsonify({"status": "error", "message": "Cannot create the game (invalid number players maybe?)"}), 400

    game_id = game.get_game_id()

    for i, player_type in enumerate(player_types):
        # First player type is human, create the player
        if player_type=='HUMAN' and i==0:
            player_id = game.create_player(PlayerType.HUMAN)
            if player_id is None:
                return jsonify({"status": "error", "message": "Cannot create the player"}), 400
        # Create computer player 
        elif player_type == "COMPUTER":
            player_id = game.create_player(PlayerType.COMPUTER)
            if player_id is None:
                return None
            # If first player is computer redirect to referee page        
            #if i == 0:
            #    timer = threading.Timer(3.0, lambda: redirect(url_for('game', game_id=game_id, player_id="referee")))
            #    timer.start()
        else:
            continue

    admin_player_id = game.get_admin_id()
    is_player_admin = False
    if admin_player_id is None:
        player_ids = game.get_player_ids()
        if len(player_ids) == 0:
            return jsonify({"status": "error", "message": "Cannot create the player"}), 400
        game.found_player(player_ids[0]).set_as_admin()  # Make first player admin
        admin_player_id = player_ids[0]
        is_player_admin = True

    update_lobby(game)

    # Player that creates the game is always admin
    return jsonify({"status": "success", "gameID": game_id, "playerID": admin_player_id, "isAdmin": is_player_admin}), 200

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

        if player_type == "COMPUTER":
            player_id = game.create_player(PlayerType.COMPUTER)
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
    print(f"APP >>> Player trying to set its name game (Game ID: {game_id}, Player ID: {player_id})")

    if not game_id or not player_id or not player_name:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400

    game = get_game(game_id)
    if game is None:
        return jsonify({"status": "error", "message": "Game not found"}), 404
    else:
        if game.is_game_started():
            return jsonify({"status": "error", "message": "Game already started. Cannot change player name"}), 400

        player = game.found_player(player_id)
        if player is not None and player.get_player_type() == PlayerType.HUMAN:  # If player is found and its type is HUMAN
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
        if player is not None and player.get_player_type() == PlayerType.HUMAN:
            player.set_player_state(PlayerState.LOBBY_READY)
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

    print(f"APP >>> Player trying to enter game (Game ID: {game_id}, Player ID: {player_id})")

    game = get_game(game_id)
    if game is None:
        return jsonify({"status": "error", "message": "Game not found"}), 404
    else :
        # If the player is not entered game, enter it
        is_entered = game.is_player_entered(player_id)
        if not is_entered: 
            is_entered = game.enter_player_to_game(player_id)
            update_lobby(game)

        if is_entered:
            return redirect(url_for('game', game_id=game_id, player_id=player_id))
        else:
            return jsonify({"status": "error", "message": "Player cannot enter to game"}), 400

# Game POSTS
@app.route("/game/<game_id>/referee")
def referee(game_id: str) -> Response:
    return render_template('referee.html', game_id=game_id, player_id="referee")

@app.route("/game/<game_id>/<player_id>")
def game(game_id: str, player_id: str) -> Response:
    return render_template('game.html', game_id=game_id, player_id=player_id)

@app.route("/game/<game_id>/<player_id>/get-player-name", methods=["POST"])
def get_player_name(game_id: str, player_id: str) -> Response:
    game = get_game(game_id)
    if game is None:
        return jsonify({"status": "error", "message": "Game could not found"}), 404

    player = game.found_player(player_id)
    if player is None:
        return jsonify({"status": "error", "message": "Player could not be found"}), 404
    print(f"APP >>> Stored player name {player.get_player_name()} for id of {player_id}")
    return jsonify({"status": "success", "playerName": player.get_player_name()}), 200

@app.route("/game/<game_id>/<player_id>/request-update", methods=["POST"])
def request_update(game_id: str, player_id: str) -> Response:
    game = get_game(game_id)
    print(f'APP >>> Update requested by Player: {player_id}')

    if game is not None:
        game.update_clients()
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Game could not found"}), 404

@app.route("/game/<game_id>/<player_id>/request-order", methods=["POST"])
def request_order(game_id: str, player_id: str) -> Response:
    game = get_game(game_id)
    if game is None:
        return jsonify({"status": "error", "message": "Game could not found"}), 404

    print(f'APP >>> Order requested by Player: {player_id}')
    letter = game.request_play_order(player_id)
    if letter is not None:
        return jsonify({"status": "success", "letter": letter}), 200
    else:
        return jsonify({"status": "error", "message": "Player cannot request play order"}), 400

@app.route("/game/<game_id>/<player_id>/request-rack", methods=["POST"])
def request_rack(game_id: str, player_id: str) -> Response:
    game = get_game(game_id)
    if game is None:
        return jsonify({"status": "error", "message": "Game could not found"}), 404

    print(f'APP >>> Rack requested by Player: {player_id}')
    player = game.found_player(player_id)
    if player is None:
        return jsonify({"status": "error", "message": "Player could not be found"}), 404

    rack = player.get_serialized_rack()
    if rack is not None:
        return jsonify({"status": "success", "rack": rack}), 200
    else:
        return jsonify({"status": "error", "message": "Player cannot request its rack"}), 400

@app.route("/game/<game_id>/<player_id>/verify-word", methods=["POST"])
def verify_word(game_id: str, player_id: str) -> Response:
    request_json = request.get_json()

    if request_json is None:
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    tiles = request_json if isinstance(request_json, list) else []

    if not game_id or not player_id or len(tiles) == 0:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400

    print(f'APP >>> Word verifing for Player: {player_id}')

    # Print each tile's properties
    for tile in tiles:
        print(f"(Letter: {tile['letter']}, ID: {tile['tileID']}, Location: {tile['location']})", end=" ")
    print("")

    game = get_game(game_id)
    if game is not None:
        word = verbalize(tiles)
        print(f"APP >>> Verbalized Word Letter: {word}")

        calculated_points = game.verify_word(word)
        if calculated_points > 0:
            return jsonify({"status": "success", "points": calculated_points}), 200
        else:
            return jsonify({"status": "error", "message": "Verification failed"}), 200
    else:
        return jsonify({"status": "error", "message": "Game not found"}), 404

@app.route("/verify-word", methods=["POST"])
def verify_word_debug() -> Response:
    request_json = request.get_json()

    tiles = request_json if isinstance(request_json, list) else []

    # Print each tile's properties
    for tile in tiles:
        print(f"Letter: {tile['letter']}, ID: {tile['tileID']}, Location: {tile['location']}")

    calculated_points = 10
    
    return jsonify({"status": "success", "points": calculated_points}), 200

@app.route("/game/<game_id>/<player_id>/exchange-letter", methods=["POST"])
def exchange_letter(game_id: str, player_id: str) -> Response:
    request_json = request.get_json()

    if request_json is None:
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    letter = request_json["letter"]

    if not letter or len(letter) == 0:
        return jsonify({"status": "error", "message": "Missing parameter(s)"}), 400

    game = get_game(game_id)
    if game is not None:
        isSucccess = game.exchange_letter(player_id, letter)
        if isSucccess:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "message": "Cannot change the tile. Tile bag may be empty."}), 200
    else:
        return jsonify({"status": "error", "message": "Game not found"}), 404

@app.route("/game/<game_id>/<player_id>/skip-turn", methods=["POST"])
def skip_turn(game_id: str, player_id: str) -> Response:
    if not game_id or not player_id:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400
    
    game = get_game(game_id)
    if game is not None:
        player = game.found_player(player_id)
        if player is not None and player.get_player_type() == PlayerType.HUMAN:
            is_skipped = game.skip_turn(player_id)
            if is_skipped:
                return jsonify({"status": "success"}), 200
            else:
                return jsonify({"status": "error", "message": "Word cannot be submitted"}), 400
        else:
            return jsonify({"status": "error", "message": "Player not found"}), 404
    else:
        return jsonify({"status": "error", "message": "Game not found"}), 404

@app.route("/game/<game_id>/<player_id>/submit", methods=["POST"])
def submit(game_id: str, player_id: str) -> Response:
    request_json = request.get_json()
    print(f'APP >>> A word is about to be submitted by Player: {player_id}')

    if request_json is None:
        return jsonify({"status": "error", "message": "Invalid request"}), 400
    
    tiles = request_json if isinstance(request_json, list) and all(isinstance(tile, dict) for tile in request_json) else []

    if not game_id or not player_id or len(tiles) == 0:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400
    
    game = get_game(game_id)
    if game is not None:
        player = game.found_player(player_id)
        if player is not None and player.get_player_type() == PlayerType.HUMAN:
            word = verbalize(tiles)
            calculated_points = game.submit(player_id, word)
            if calculated_points > 0:
                return jsonify({"status": "success", "points": calculated_points}), 200
            else:
                return jsonify({"status": "error", "message": "Word cannot be submitted"}), 200
        else:
            return jsonify({"status": "error", "message": "Player not found"}), 404
    else:
        return jsonify({"status": "error", "message": "Game not found"}), 404

@app.route("/game/<game_id>/<player_id>/request-hint", methods=["POST"])
def request_hint(game_id: str, player_id: str) -> Response:
    request_json = request.get_json()

    if request_json is None:
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    letters = request_json if isinstance(request_json, list) else []

    if not game_id or not player_id or len(letters) == 0:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400

    if len(letters) == 1:
        return jsonify({"status": "error", "message": "No hint found"}), 200

    print(f'APP >>> Hint request by Player: {player_id}')

    game = get_game(game_id)
    if game is not None:
        hints = game.get_hint(player_id, letters)
        if len(hints)>0:
            best_hint = hints[0]
            return jsonify({"status": "success", "hint": str(TILE.stringify_word(best_hint.word) + f" Points: {best_hint.score}" )}), 200
        else:
            return jsonify({"status": "error", "message": "No hint found"}), 200
    else:
        return jsonify({"status": "error", "message": "Game not found"}), 404

@app.route("/game/<game_id>/<player_id>/quit-game", methods=["POST"])
def quit_game(game_id: str, player_id: str) -> Response:
    print(f'APP >>> Player {player_id} is about to quit game {game_id}')
   
    if not game_id or not player_id:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400
    
    game = get_game(game_id)
    if game is not None:
        player = game.found_player(player_id)
        if player is not None:
            is_kicked = game.kick_player(player_id)
            if is_kicked:
               return redirect('/')
            else:
                return jsonify({"status": "error", "message": "Player cannot be kicked"}), 200
        else:
            return jsonify({"status": "error", "message": "Player not found"}), 404
    else:
        return jsonify({"status": "error", "message": "Game not found"}), 404

@app.route("/game/<game_id>/<player_id>/set-player-strategy", methods=["POST"])
def set_player_strategy(game_id: str, player_id: str) -> Response:
    if not player_id == "referee":
        return jsonify({"status": "error", "message": "Player strategy can be only changed by referee."}), 400 

    request_json = request.get_json()

    if request_json is None:
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    player_name = request_json.get("playerName")
    strategy = request_json.get("strategy")
    
    game = get_game(game_id)
    if game is None:
        return jsonify({"status": "error", "message": "Game could not found"}), 404

    target_player_id = game.get_player_id(player_name)

    player = game.found_player(target_player_id)
    if player is None:
        return jsonify({"status": "error", "message": "Player could not be found"}), 404

    if (strategy=="GREEDY"):
        player.set_player_strategy(PlayerStrategy.GREEDY)
    else:
        player.set_player_strategy(PlayerStrategy.BALANCED)
    
    return jsonify({"status": "success", "playerName": player_name, "strategy": strategy}), 200

# Other POSTS

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

    #clean_games()  # This function cleans games if it is finished. It is called receursivelly in certain time intervals

    if os.path.exists(context[0]) and os.path.exists(context[1]):
        app.run(host="0.0.0.0", debug=True, ssl_context=context)
    else:
        app.run(host="0.0.0.0", debug=True, ssl_context="adhoc")