from flask_socketio import SocketIO, emit

from typing import List, Dict, Tuple
from dataclasses import dataclass

from game.computer_player import ComputerPlayer
from game.human_player import HumanPlayer

from .globals import *
from .utils import *
from .player import *
from .components import *
from .observer import Subject
from .enums import *

@dataclass(frozen=True)
class GameMeta:
    GAME_ID: str
    GAME_STATE: GameState
    TILES_IN_BAG: int

class Scrabble(Subject):
    default_lang = LANG_KEYS.ENG
    BINGO_BONUS: int = 25

    def __init__(self, socketio: SocketIO, player_count=MIN_PLAYER_COUNT):
        super().__init__()
        self.__socketio = socketio
        self.__connected_clients: Dict[str, str] = {}
        self.__referee_clients: Dict[str, str] = {}

        self.__game_id = generate_unique_id()
        self.__game_state: GameState = GameState.UNDEFINED
        
        self.__player_count = player_count
        self.__active_player_count = 0
        self.__players: List[Player] = []
        self.__currentPlayer: Player = None

        # Create game components
        self.__dictionary = None
        self.__tile_bag = None
        self.__board = None

        self.__turn_count: int =  -1

        self.load_language(self.default_lang)  #TODO Make it parametric for different language support
        
        self.__set_game_state(GameState.WAITING_FOR_PLAYERS)

        self.__computer_player_names: List[str] = COMPUTER_PLAYER_NAMES[:]
        random.shuffle(self.__computer_player_names)
        self.__computer_player_count = 0

    # Getter and Setter for Game Properties

    def __set_game_state(self, state: GameState):
        print(f'Game {self.__game_id} State: {GameState.to_string(self.__game_state)} -> {GameState.to_string(state)}')
        self.__game_state = state
        self.__update()

    def load_language(self, lang_key: LANG_KEYS) -> None:
        self.__dictionary = DictionaryWrapper(LANGUAGES[lang_key])
        self.__dictionary.load_language(LANGUAGES[lang_key])

        self.__tile_bag = TileBag()
        self.__tile_bag.load(self.__dictionary.get_alphabet())

        self.__board = Board(self.__dictionary, BOARD_ROW, BOARD_COL, PREMIUM_CELLS)

    def get_game_id(self) -> str:
        return self.__game_id

    def get_game_state(self) -> GameState:
        return self.__game_state

    def generate_computer_player_name(self) -> str:
        if self.__computer_player_count >= len(self.__computer_player_names):
            return ""
        
        name = self.__computer_player_names[self.__computer_player_count]     
        self.__computer_player_count += 1
        return name

    def create_player(self, player_type=PlayerType.HUMAN) -> Optional[str]:
        if (self.__active_player_count >= self.__player_count):
            return None
        
        if player_type == PlayerType.HUMAN:
            player = HumanPlayer(self.__board)
        elif player_type == PlayerType.COMPUTER:
            player = ComputerPlayer(self.__board, self.__tile_bag, self.generate_computer_player_name())
            print(f"Player {player.get_player_id()} picked its name as {player.get_player_name()}.")
        else:
            return None

        if not (player_type == PlayerPrivileges.REFEREE):
            self.__players.append(player)
            self.__active_player_count += 1

        self.attach(player)  # Attach the player to the observer list
        print(f"A new player with id of {player.get_player_id()} created.")

        return player.get_player_id()

    def kick_player(self, player_id: str) -> bool:
        player = self.found_player(player_id)
        if player is None:
            return False
        else:
            player.widthdraw()

            # If admin leaves the game, end the game
            if player.get_player_privilege() == PlayerPrivileges.ADMIN:
                self.__set_game_state(GameState.GAME_OVER)

            self.detach(player)
            self.__players.remove(player)
            self.__active_player_count -= 1

            if (player.get_player_state() == PlayerState.PLAYING):
                self.skip_turn(player_id)
            self.__update()

            return True

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

    def get_game_meta(self) -> GameMeta:
        return GameMeta(self.__game_id, self.__game_state, self.__tile_bag.get_remaining_tiles())

    def get_players_meta(self) -> List[PlayerMeta]:
        return [player.get_player_meta() for player in self.__players]

    def get_player_id(self, player_name: str) -> str:
        for player in self.__players:
            if player.get_player_name() == player_name:
                return player.get_player_id()
        return None

    def found_player(self, player_id: str) -> Player:
        for player in self.__players:
            if player.get_player_id() == player_id:
                return player
        return None

    def get_player_count(self) -> int:
        return len(self.__players)

    def get_player_order(self, player_id: str) -> int:
        order_counter = 0
        for player in self.__players:
            if (player.get_player_id() == player_id):
                return order_counter
            order_counter += 1
        return -1  # No player order found with provided id       

    def get_first_player(self) -> Player:
        return None if len(self.__players) == 0 else self.__players[0]

    def get_board(self) -> Board:
        return self.__board

    def get_turn_count(self) -> int:
        return self.__turn_count
    
    def reset_turn_count(self) -> None:
        self.__turn_count = -1

    def is_all_players_ready(self) -> bool:
        if len(self.__players) == 0: return False

        for player in self.__players:
            if not player.get_player_state() == PlayerState.LOBBY_READY:
                return False
        return True

    def is_game_has_admin(self) -> bool:
        for player in self.__players:
            if player.is_admin():
                return True
        return False

    def is_game_started(self) -> bool:
        return self.get_game_state() == GameState.GAME_STARTED
    
    # Player Actions
    def enter_player_to_game(self, player_id: str) -> bool:
        print(f"Player {player_id} is about to enter the game.")
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
            player.set_player_state(PlayerState.WAITING_ORDER)

        self.__set_game_state(GameState.PLAYER_ORDER_SELECTION)
        self.update_clients()

        return True

    def request_play_order(self, player_id: str) -> LETTER:
        print(f"Player {player_id} is about to request play order.")
        player = self.found_player(player_id)
        if player is None: return None

        # Player cannot request order again if it has already requested        
        if player.is_order_requested():
            print(f"Player {player_id} has already requested order, cannot request again.")
            return None

        letter = self.__tile_bag.pick_letter_for_order()
        if letter is None:
            print(f"Player {player_id} cannot pick letter")
            return None

        order = ord(letter) - ord('A') + 1
        player.set_play_order(order)

        self.__players.sort(key=lambda p: p.get_play_order())

        player.set_player_state(PlayerState.WAITING)
        
        self.__update()

        print(f"Player {player_id} picked letter {letter} for order")
 
        return letter

    def verify_word(self, word: WORD) -> int:
        points = self.__board.calculate_points(word)

        # Add bingo bonus if all letters are used
        if (len(word)==7 and points>0):
            points += Scrabble.BINGO_BONUS

        return points

    def submit(self, player_id: str, word: WORD) -> int:
        print(f"Player {player_id} is about to submit the word: {word}")
        if self.__game_state != GameState.GAME_STARTED:
            return 0
        
        player = self.found_player(player_id)
        if player is None:
            return 0

        # Only current player submit its word
        if not (player.get_player_id() == self.__currentPlayer.get_player_id()):
            return 0

        if word is None:
            return 0

        points = self.verify_word(word)

        # If the word is valid then its points will be greater than 0
        if points > 0:
            player.add_points(points)

            # Place the word on the board
            placed_tiles = self.__board.place_word(word)

            # Remove the tiles from the player's rack
            letter_count = len(placed_tiles)
            for tile in placed_tiles:
                player.remove_from_rack(tile)

            # Refill the rack of the player
            for _ in range(letter_count):
                newTile = self.__tile_bag.get_random_tile()
                player.add_tile(newTile)

            # Finish the turn
            self.next_turn()  # Update the turn count and set the next player
            self.__update()  # Update game state machine 
        
        self.update_clients()  # Notify all clients about the changes

        return points

    def get_hint(self, player_id: str, letters: List[LETTER]) -> List[MOVE]:
        print(f"Player {player_id} is about to request hint: {letters}")
        if self.__game_state != GameState.GAME_STARTED:
            return []
        
        player = self.found_player(player_id)
        if player is None:
            return []

        # Only current player submit its word
        if not (player.get_player_id() == self.__currentPlayer.get_player_id()):
            return []

        if letters is None and len(letters) == 0:
            return []
        
        # Get the possible words from the board
        temp_tiles = []
        for letter in letters:
            temp_tiles.append(TILE(letter=letter))
        possible_words = self.__board.get_possible_moves(temp_tiles)
        
        return possible_words

    def exchange_letter(self, player_id: str, letter: LETTER) -> bool:
        print(f"Player {player_id} is about to exchange its letter.")
        player = self.found_player(player_id)

        if player is None or not (player.get_player_state() == PlayerState.PLAYING):
            return False

        newTile = self.__tile_bag.get_random_tile()
        tiles = player.get_rack()

        if tiles is None or len(tiles) == 0 or newTile is None:
            return False

        for tile in tiles:
            if (tile.letter == letter):
                print(f"Removing tile ({letter}) from the rack")
                player.remove_from_rack(tile)
                break

        self.__tile_bag.put_back_letter(letter)

        player.add_tile(newTile)

        print(player.get_serialized_rack())

        self.skip_turn(player_id)  # Exchanging letter penalizes the player by skipping the turn

        return True

    def next_turn(self) -> Player:
        """
        @brief Calculate the point of the player's word and pass the turn to the next player

        @param word: The player id
        @return: The player who will play next
        """
        self.__currentPlayer.set_player_state(PlayerState.WAITING)
        self.__turn_count = (self.__turn_count + 1) % len(self.__players)
        self.__currentPlayer = self.__players[self.__turn_count]
        self.__currentPlayer.set_player_state(PlayerState.PLAYING)
        return self.__currentPlayer

    def skip_turn(self, player_id: str) -> Player:
        """
        @brief Skip the turn of the current player
        
        @param player_id: The player id
        @return: The player who will play next
        """
        print(f"Player {player_id} is about to skip the turn.")
        player = self.found_player(player_id)
        if player is None: return None
        if not (player.get_player_state() == PlayerState.PLAYING): return None

        self.next_turn()
        self.__update()
        # No need to send message the client that requested the skip
        self.send_message_to_clients("Player " + player.get_player_name() + " has skipped the turn.", exclude_list=[player.get_player_id()])
        return self.__currentPlayer
    
    def get_winner(self) -> Player:
        max_points = 0
        winner = None
        for player in self.__players:
            if player.get_points() > max_points and player.is_active():
                max_points = player.get_points()
                winner = player
        return winner

    # Internal Game Actions

    def __on_waiting_for_players(self):
        # Check if all players are ready
        if self.is_all_players_ready():
            self.__set_game_state(GameState.PLAYER_ORDER_SELECTION)

    def __on_player_order_selection(self):
        if len(self.__players) == 0: return

        # Check if all players have selected their order
        for player in self.__players:
            if (player.get_player_state() < PlayerState.WAITING):
                return
        self.__set_game_state(GameState.GAME_STARTED)

    def __on_game_started(self):
        # Check if game is over
        if self.__check_game_over():
            self.__set_game_state(GameState.GAME_OVER)
        else:
            # At the very beginning of the game
            if (self.__currentPlayer == None):
                for player in self.__players:
                    if player.is_rack_empty():
                        player.initialize_rack(self.__tile_bag)
                
                self.reset_turn_count()
                self.__currentPlayer = self.get_first_player()
                self.__currentPlayer.set_player_state(PlayerState.PLAYING)
                #if (self.__currentPlayer.get_player_type() == PlayerType.COMPUTER):
                #    score, tiles = self.__currentPlayer.play_turn()
                #    self.submit(self.__currentPlayer.get_player_name(), tiles)
            
            iter = 0
            while self.__currentPlayer.get_player_state != PlayerState.PLAYING and iter < self.__player_count:
                self.__currentPlayer.set_player_state(PlayerState.WAITING)
                self.next_turn()  # Move to next player
                iter += 1

            self.__currentPlayer.set_player_state(PlayerState.PLAYING)
            if (self.__currentPlayer.get_player_type() == PlayerType.COMPUTER):
                pass
                #score, tiles = self.__currentPlayer.play_turn()
                #self.submit(self.__currentPlayer.get_player_name(), tiles)
        
    def __on_game_over(self):
        pass
    
    def __update(self) -> None:
        if self.__game_state == GameState.WAITING_FOR_PLAYERS:
            self.__on_waiting_for_players()
        elif self.__game_state == GameState.PLAYER_ORDER_SELECTION:
            self.__on_player_order_selection()
        elif self.__game_state == GameState.GAME_STARTED:
            self.__on_game_started()
        elif self.__game_state == GameState.GAME_OVER:
            self.__on_game_over()
        else:
            raise ValueError("Invalid game state")

        self.update_clients()
        self.notify_all(self.__game_state)  # Notify all players about the game state

    def __check_game_over(self) -> bool:
        if (self.get_game_state() == GameState.GAME_OVER):
            return True
        # If game has not been started yet game is not over
        if (self.get_game_state() != GameState.GAME_STARTED):
            return False

        if (self.__active_player_count <= 1):
            return True

        if (self.__tile_bag.get_remaining_tiles() == 0):
            return True
        
        skip_count_flag = True
        for player in self.__players:
            if player.get_skip_count() >= 2:
                skip_count_flag &= True
            else:
                skip_count_flag &= False
        if skip_count_flag:
            return True
        
        return False

    # Remote Client Actions

    def add_sid(self, sid: str, player_id: str) -> None:
        self.__connected_clients[sid] = player_id

    def add_referee_sid(self, sid: str, _: str) -> None:
        self.__referee_clients[sid] = "REFEREE"

    def remove_sid(self, sid: str, _: str) -> None:
        self.__connected_clients.pop(sid, None)

    def remove_referee_sid(self, sid: str, _: str) -> None:
        self.__referee_clients.pop(sid, None)

    def update_clients(self) -> None:
        players_meta: List[PlayerMeta] = self.get_players_meta()
        # Emit the notification to all connected clients
        self.__socketio.emit('update-players', {"playersMeta": [player.__dict__ for player in players_meta]})
        self.__socketio.emit('update-game', {"gameMeta": self.get_game_meta().__dict__})
        self.__socketio.emit('update-board', {"board": self.__board.serialize()})
        
        for sid, player_id in self.__connected_clients.items():
            player = self.found_player(player_id)
            if player is not None:
                self.__socketio.emit("update-racks", {"racks": player.get_serialized_rack()}, to=sid)

        # Referee clients can access all players' rack
        for sid, _ in self.__referee_clients.items():
            player_racks: Dict[str, Dict[LETTER, int]] = {}
            for player in self.__players:
                player_racks[player.get_player_name()] = player.get_serialized_rack()
            
            if len(player_racks)>0: self.__socketio.emit("update-rack", {"rackInfo": player_racks}, to=sid)

    def send_message_to_clients(self, message: str, exclude_list: List[str]) -> None:
        for sid, player_id in self.__connected_clients.items():
            # Send the message to all connected clients
            # except the one who is excluded
            if player_id in exclude_list:
                continue

            player = self.found_player(player_id)
            if player is not None:
                self.__socketio.emit('game-message', {"message": message})
