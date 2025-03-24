from flask_socketio import SocketIO, emit

from typing import List, Dict, Tuple
from dataclasses import dataclass

from game.computer_player import ComputerPlayer
from game.human_player import HumanPlayer

from .globals import *
from .utils import *
from .player import *
from .components import *

class GameState:
    UNDEFINED               = 0  # Initial state
    WAITING_FOR_PLAYERS     = 1  # Waiting for players to join the game
    PLAYER_ORDER_SELECTION  = 2  # Players are selecting the order of play
    GAME_STARTED            = 3  # Game has started
    GAME_OVER               = 4  # Game is over

@dataclass(frozen=True)
class GameMeta:
    GAME_ID: str
    GAME_STATE: GameState

class Game:
    default_lang = LANG_KEYS.ENG

    def __init__(self, socketio: SocketIO, player_count=MIN_PLAYER_COUNT):
        self.__socketio = socketio
        self.__connected_clients: Dict[str, str] = {}

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

    def load_language(self, lang_key: LANG_KEYS) -> None:
        self.__dictionary = DictionaryWrapper(LANGUAGES[lang_key])

        self.__tile_bag = TileBag()
        self.__tile_bag.load(self.__dictionary.get_alphabet())

        self.__board = Board(self.__dictionary, BOARD_ROW, BOARD_COL, SPECIAL_CELLS)

    def get_game_id(self) -> str:
        return self.__game_id

    def get_game_state(self) -> GameState:
        return self.__game_state

    def __set_game_state(self, state: GameState):
        print('__set_game_state', self.__game_state, state)
        self.__game_state = state
        self.update()

    def create_player(self, player_type=PlayerType.HUMAN) -> str:
        if (self.__active_player_count >= self.__player_count):
            return -1
        
        if player_type == PlayerType.HUMAN:
            player = HumanPlayer(self.__board)
        elif player_type == PlayerType.COMPUTER:
            player = ComputerPlayer(self.__board)
        else:
            return -1

        if not (player_type == PlayerPrivileges.REFEREE):
            self.__players.append(player)
            self.__active_player_count += 1

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

    def get_game_meta(self) -> GameMeta:
        return GameMeta(self.__game_id, self.__game_state)

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
        for player in self.__players:
            if (player.get_player_id() == player_id):
                return order_counter
            order_counter += 1
        return -1  # No player order found with provided id       

    def get_first_player(self) -> Player:
        return None if self.__players.__len__() == 0 else self.__players[0]

    def get_turn_count(self) -> int:
        return self.__turn_count
    
    def reset_turn_count(self) -> None:
        self.__turn_count = -1

    def is_all_players_ready(self) -> bool:
        if self.__players.__len__() == 0: return False

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

            # If admin leaves the game, end the game
            if player.get_player_privilege() == PlayerPrivileges.ADMIN:
                self.__set_game_state(GameState.GAME_OVER)
            return True
    
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
            player.set_player_state(PlayerState.WAITING_ORDER)

        self.__set_game_state(GameState.PLAYER_ORDER_SELECTION)
        self.update_clients()

        return True

    def request_play_order(self, player_id: str) -> LETTER:
        player = self.found_player(player_id)
        if player is None: return None

        # Player cannot request order again if it has already requested        
        if player.is_order_requested():
            return None

        letter = self.__tile_bag.pick_letter_for_order()
        if letter is None: return None

        order = ord(letter) - ord('A') + 1
        player.set_play_order(order)

        self.__players.sort(key=lambda p: p.get_play_order())

        player.set_player_state(PlayerState.WAITING)
        
        self.update()

        print(player_id, letter)

        return letter

    def __on_waiting_for_players(self):
        # Check if all players are ready
        if self.is_all_players_ready():
            self.__set_game_state(GameState.PLAYER_ORDER_SELECTION)

    def __on_player_order_selection(self):
        if self.__players.__len__() == 0: return

        # Check if all players have selected their order
        for player in self.__players:
            print(player.get_player_state(), PlayerState.WAITING)
            if (player.get_player_state() < PlayerState.WAITING):
                return
        print('Game has been started!!!!!!!!!!!!!')
        self.__set_game_state(GameState.GAME_STARTED)

    def __on_game_started(self):
        # Check if game is over
        if self.check_game_over():
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
                if (self.__currentPlayer.get_player_type() == PlayerType.COMPUTER):
                    score, tiles = self.__currentPlayer.play_turn()
                    self.submit(self.__currentPlayer.get_player_name(), tiles)
            
            iter = 0
            while self.__currentPlayer.get_player_state != PlayerState.PLAYING and iter < self.__player_count:
                self.__currentPlayer.set_player_state(PlayerState.WAITING)
                self.next_turn()  # Move to next player
                iter += 1

            self.__currentPlayer.set_player_state(PlayerState.PLAYING)
            if (self.__currentPlayer.get_player_type() == PlayerType.COMPUTER):
                score, tiles = self.__currentPlayer.play_turn()
                self.submit(self.__currentPlayer.get_player_name(), tiles)
        
    def __on_game_over(self):
        pass
    
    def update(self) -> None:
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

    def verify_word(self, word: WORD) -> int:
        points = self.__board.calculate_points(word)

        return points

    def submit(self, player_id: str, word: WORD) -> int:
        if self.__game_state != GameState.GAME_STARTED:
            return 0
        
        player = self.found_player(player_id)
        if player is None:
            return 0

        # Only current player submit its word
        if not (player.get_player_id() == self.__currentPlayer.get_player_id()):
            return 0

        points = self.verify_word(word)

        if points > 0:
            player.add_points(points)
            
            letter_count = word.__len__()
            for letter in word:
                player.remove_from_rack(letter.letter)

            self.__board.place_word(word)

            for _ in range(letter_count):
                newLetter = self.__tile_bag.get_random_letter()
                player.add_to_rack(newLetter)

            self.next_turn()
            self.update()

        return points

    def next_turn(self) -> Player:
        """
        @brief Calculate the point of the player's word and pass the turn to the next player

        @param word: The player id
        @return: The player who will play next
        """
        self.__turn_count = (self.__turn_count + 1) % self.__players.__len__()
        self.__currentPlayer = self.__players[self.__turn_count]
        return self.__currentPlayer

    def skip_turn(self, player_id: str) -> Player:
        """
        @brief Skip the turn of the current player
        
        @param player_id: The player id
        @return: The player who will play next
        """
        player = self.found_player(player_id)
        if player is None: return None
        if not (player.get_player_state() == PlayerState.PLAYING): return None

        self.__turn_count = (self.__turn_count + 1) % self.__players.__len__()
        self.__currentPlayer = self.__players[self.__turn_count]
        return self.__currentPlayer
    
    def check_game_over(self) -> bool:
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

    def get_winner(self) -> Player:
        max_points = 0
        winner = None
        for player in self.__players:
            if player.get_points() > max_points and player.is_active():
                max_points = player.get_points()
                winner = player
        return winner

    def add_sid(self, sid: str, player_id: str) -> None:
        self.__connected_clients[sid] = player_id

    def remove_sid(self, sid: str, player_id: str) -> None:
        self.__connected_clients.pop(sid, None)

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
