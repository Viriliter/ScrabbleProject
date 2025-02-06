from typing import List, Dict, Tuple
from dataclasses import dataclass

from .globals import *
from .utils import *
from .components import *

class PlayerType:
    UNDEFINED = "UNDEFINED"
    AI = "AI"
    HUMAN = "HUMAN"

class PlayerPrivileges:
    UNDEFINED = 0   # N/A
    ADMIN = 1       # ADMIN is the player who creates the game
    PLAYER = 2      # PLAYER is ordinary 
    REFEREE = 3     # REFEREE does not join the game just watches players' action

class PlayerState:
    UNDEFINED       = 0   # The player has not been initialized yet
    NOT_READY       = 1   # The player has entered lobby screen but not clicked the ready button yet
    READY           = 2   # After player has clicked the ready button on lobby screen
    WAITING         = 3   # Player is waiting for its next turn to play
    PLAYING         = 4   # Player is playing its turn
    WON             = 5   # Player has won the game
    LOST            = 6   # Player has lost the game
    WAITING_ORDER   = 7   # Player is waiting to be ordered 

@dataclass(frozen=True)
class PlayerMeta:
    PLAYER_ID: int
    PLAYER_NAME: str
    PLAYER_TYPE: PlayerType
    PLAYER_STATE: PlayerState
    IS_ADMIN: bool
    PLAY_ORDER: int
    PLAYER_POINTS: int

class Player:
    __player_id: str = ""
    __player_name: str = ""
    __player_type: PlayerType = PlayerType.UNDEFINED
    __player_state: PlayerState = PlayerState.UNDEFINED
    __player_privileges: PlayerPrivileges = PlayerPrivileges.UNDEFINED
    __points: int = 0
    __skip_count: int = 0
    __play_order: int = 100  # Set something large  
    __rack: Rack = None
    __board: Board = None

    def __init__(self, board, player_type=PlayerType.HUMAN, player_privileges=PlayerPrivileges.PLAYER):
        self.__player_id = generate_unique_id()
        self.__player_type = player_type
        self.__player_privileges = player_privileges

        self.__board = board
        # Create game components
        self.__rack = Rack()

        if self.__player_type == PlayerType.AI:
            self.set_player_state(PlayerState.READY)

    def set_as_admin(self) -> None:
        self.__player_privileges = PlayerPrivileges.ADMIN

    def is_admin(self) -> bool:
        if self.__player_privileges == PlayerPrivileges.ADMIN: return True
        else: return False

    def is_active(self) -> bool:
        if self.__player_state == PlayerState.PLAYING or self.__player_state == PlayerState.WAITING:
            return True
        else:
            return False

    def set_player_state(self, player_state: PlayerState) -> None:
        self.__player_state = player_state

        # AI player 
        if (self.__player_state == PlayerState.PLAYING and self.__player_type == PlayerType.AI):
            self.play_game()

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

    def get_player_privilege(self) -> PlayerPrivileges:
        return self.__player_privileges

    def get_points(self) -> int:
        return self.__points

    def set_points(self, points: int) -> None:
        self.__points = points

    def add_points(self, points: int) -> None:
        self.__points += points

    def remove_points(self, points: int) -> None:
        self.__points -= points

    def increment_skip_count(self) -> None:
        self.__skip_count += 1

    def get_skip_count(self) -> int:
        return self.__skip_count
    
    def enter_game(self, tile_bag: TileBag) -> None:
        self.__player_state = PlayerState.READY

    def widthdraw(self) -> None:
        self.__player_state = PlayerState.LOST

    def play_turn(self, word: WORD) -> None:
        if not (self.__player_state == PlayerState.PLAYING):
            return

    def get_serialized_rack(self) -> None:
        return self.__rack.serialize()

    def remove_from_rack(self, letter: chr) -> None:
        self.__rack.remove_from_rack(letter)

    def add_to_rack(self, letter: chr) -> None:
        self.__rack.add_to_rack(letter)

    def start_game(self, tile_bag: TileBag) -> None:
        # Before starting the game each player gets its tiles from tile bag
        for _ in INITIAL_TILE_COUNT:
            self.__rack.add_to_rack(tile_bag.get_random_letter())

    def play_game() -> None:
        pass
