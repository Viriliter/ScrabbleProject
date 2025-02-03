from flask_socketio import SocketIO, emit

from typing import List, Dict, Tuple
from dataclasses import dataclass

from .globals import *
from .utils import *
from .player import *
from .components import *

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
    __socketio: SocketIO = None

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

    def __init__(self, socketio, player_count=2):
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
        self.update_clients()

        return True

    def update_clients(self) -> None:
        players_meta: List[PlayerMeta] = self.get_players_meta()
        # Emit the notification to all connected clients
        self.__socketio.emit('update-game', {"playersMeta": [player.__dict__ for player in players_meta]})
        #self.__socketio.emit('update-board', {"board": [player.__dict__ for player in players_meta]})

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
