from flask_socketio import SocketIO, emit

from typing import List, Dict, Tuple
from dataclasses import dataclass

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
    __socketio: SocketIO = None

    __game_id: str = ""
    __game_state: GameState = GameState.UNDEFINED

    __players: List[Player] = []
    __player_count: int = 0
    __active_player_count = 0
    __currentPlayer: Player = None

    __tile_bag: TileBag = None

    __board: Board = None

    __order_counter: int = -1
    __turn_count: int = 0

    def __init__(self, socketio, player_count=2):
        self.__socketio = socketio
        self.__game_id = generate_unique_id()
        self.__player_count = player_count
        self.__players.clear()

        # Create game components
        self.__tile_bag = TileBag()
        self.__tile_bag.load(ENGLISH_TILES)  #TODO Move loading of tiles in seperate function to support different languages
        self.__board = Board()  
        
        self.__set_game_state(GameState.WAITING_FOR_PLAYERS)

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
        
        player = Player(self.__board, player_type)

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

            # If admin leaves the game, end the game
            if player.get_player_privilege() == PlayerPrivileges.ADMIN:
                self.__set_game_state(GameState.GAME_OVER)
            return True

    def pick_order(self, player_id: str) -> None:
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
            player.set_player_state(PlayerState.WAITING_ORDER)

        self.__set_game_state(GameState.PLAYER_ORDER_SELECTION)
        self.update_clients()

        return True

    def request_play_order(self, player_id: str) -> chr:
        player = self.found_player(player_id)
        if player is None: return None
        
        letter = self.__tile_bag.pick_letter_for_order()
        if letter is None: return None

        order = ord(letter) - ord('A') + 1
        player.set_play_order(order)

        self.__players.sort(key=lambda p: p.get_play_order())

        player.set_player_state(PlayerState.WAITING)
        
        self.update()

        return letter

    def __on_waiting_for_players(self):
        # Check if all players are ready
        if self.is_all_players_ready():
            self.__set_game_state(GameState.PLAYER_ORDER_SELECTION)

    def __on_player_order_selection(self):
        # Check if all players have selected their order
        for player in self.__players:
            if not (player.get_player_state() == PlayerState.WAITING):
                return
        print('Game has been started!!!!!!!!!!!!!')
        self.__set_game_state(GameState.GAME_STARTED)

    def __on_game_started(self):
        # Check if game is over
        if self.check_game_over():
            self.__set_game_state(GameState.GAME_OVER)
        else:
            if (self.__currentPlayer == None):
                self.__currentPlayer = self.get_first_player()
                self.__currentPlayer.set_player_state(PlayerState.PLAYING)
            
            iter = 0
            while self.__currentPlayer.get_player_state != PlayerState.PLAYING and iter < self.__player_count:
                self.__currentPlayer = self.next_turn()  # Move to next player

            self.__currentPlayer.set_player_state(PlayerState.PLAYING)
        
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

    def submit(self, player_id: str, word: WORD) -> int:
        if self.__game_state != GameState.GAME_STARTED:
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
            
            letter_count = word.__len__()
            for letter in word:
                player.remove_from_rack(letter.letter)

            for _ in range(letter_count):
                newLetter = self.__tile_bag.get_random_letter()
                player.add_to_rack(newLetter)

            self.update()

        return points

    ##
    # @brief Calculate the point of the player's word and pass the turn to the next player
    # @param word The word that the player has played
    # @return The player who will play next
    ##
    def next_turn(self) -> Player:
        self.__turn_count += 1
        self.__order_counter = (self.__order_counter + 1) % self.__players.__len__()
        return self.__players[self.__order_counter]
    
    ##
    # @brief Skip the turn of the current player
    # @return The player who will play next
    ##
    def skip_turn(self) -> Player:
        self.__turn_count += 1
        self.__order_counter = (self.__order_counter + 1) % self.__players.__len__()
        return self.__order_counter[self.__order_counter]
    
    def check_game_over(self) -> bool:
        print('-----------0')
        if (self.get_game_state() == GameState.GAME_OVER):
            return True
        print('-----------1')
        # If game has not been started yet game is not over
        if (self.get_game_state() != GameState.GAME_STARTED):
            return False

        print('self.__active_player_count:', self.__active_player_count)
        if (self.__active_player_count <= 1):
            return True
        print('self.__tile_bag.get_remaining_tiles():', self.__tile_bag.get_remaining_tiles())
        if (self.__tile_bag.get_remaining_tiles() == 0):
            return True
        
        print('-----------2')
        skip_count_flag = True
        for player in self.__players:
            if player.get_skip_count() >= 2:
                skip_count_flag &= True
            else:
                skip_count_flag &= False
        if skip_count_flag:
            return True
        
        print('-----------3')
        return False

    def get_winner(self) -> Player:
        max_points = 0
        winner = None
        for player in self.__players:
            if player.get_points() > max_points and player.is_active():
                max_points = player.get_points()
                winner = player
        return winner

    def update_clients(self) -> None:
        players_meta: List[PlayerMeta] = self.get_players_meta()
        # Emit the notification to all connected clients
        self.__socketio.emit('update-players', {"playersMeta": [player.__dict__ for player in players_meta]})
        self.__socketio.emit('update-game', {"gameMeta": self.get_game_meta().__dict__})
        self.__socketio.emit('update-board', {"board": self.__board.serialize()})
        #self.__socketio.emit('update-racks', {"racks": [player.get_serialized_rack() for player in self.__players]})
