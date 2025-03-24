from typing import List, Dict, Tuple
from dataclasses import dataclass

from .globals import *
from .utils import *
from .components import *

class PlayerType:
    UNDEFINED = "UNDEFINED"
    COMPUTER = "COMPUTER"
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
    WAITING_ORDER   = 3   # Player is waiting to be ordered 
    WAITING         = 4   # Player is waiting for its next turn to play
    PLAYING         = 5   # Player is playing its turn
    WON             = 6   # Player has won the game
    LOST            = 7   # Player has lost the game

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
    def __init__(self, board: Board, name: str):
        self._board = board
        self._player_id: str = generate_unique_id()
        self._player_name: str = name

        self._player_state: PlayerState = PlayerState.UNDEFINED
        self._player_type: PlayerType = PlayerType.UNDEFINED
        self._player_privileges: PlayerPrivileges = PlayerPrivileges.UNDEFINED

        self._points: int = 0
        self._skip_count: int = 0
        self._play_order: int = 100  # Set something large
        
        # Create game components
        self._rack = Rack()

    def set_as_admin(self) -> None:
        self._player_privileges = PlayerPrivileges.ADMIN

    def is_admin(self) -> bool:
        if self._player_privileges == PlayerPrivileges.ADMIN: return True
        else: return False

    def is_active(self) -> bool:
        if self._player_state == PlayerState.PLAYING or self._player_state == PlayerState.WAITING:
            return True
        else:
            return False

    def set_player_state(self, player_state: PlayerState) -> None:
        self._player_state = player_state

    def get_player_state(self) -> PlayerState:
        return self._player_state
   
    def get_player_id(self) -> str:
        return self._player_id

    def get_player_name(self) -> str:
        return self._player_name

    def set_player_name(self, player_name: str) -> None:
        self._player_name = player_name

    def get_play_order(self) -> int:
        return self._play_order

    def set_play_order(self, play_order: int) -> None:
        self._play_order = play_order

    def is_order_requested(self) -> bool:
        return True if self._play_order < 100 else False

    def is_rack_empty(self) -> bool:
        return True if self._rack is not None and self._rack.count() == 0 else False

    def get_player_meta(self) -> PlayerMeta:
        return PlayerMeta(self._player_id, self._player_name, self._player_type, self._player_state, self.is_admin(), self._play_order, self._points)

    def get_player_type(self) -> PlayerType:
        return self._player_type

    def set_player_type(self, player_type: PlayerType) -> None:
        self._player_type = player_type

    def get_player_privilege(self) -> PlayerPrivileges:
        return self._player_privileges

    def get_points(self) -> int:
        return self._points

    def set_points(self, points: int) -> None:
        self._points = points

    def add_points(self, points: int) -> None:
        self._points += points

    def remove_points(self, points: int) -> None:
        self._points -= points

    def increment_skip_count(self) -> None:
        self._skip_count += 1

    def get_skip_count(self) -> int:
        return self._skip_count
    
    def enter_game(self, tile_bag: TileBag) -> None:
        self._player_state = PlayerState.READY

    def widthdraw(self) -> None:
        self._player_state = PlayerState.LOST

    def play_turn(self, word: WORD) -> Tuple[int, WORD]:
        if not (self._player_state == PlayerState.PLAYING):
            return None, None
        return None, None

    def get_serialized_rack(self) -> Dict[LETTER, int]:
        return self._rack.serialize()

    def remove_from_rack(self, letter: LETTER) -> None:
        self._rack.remove_from_rack(letter)

    def add_to_rack(self, letter: LETTER) -> None:
        self._rack.add_to_rack(letter)

    def initialize_rack(self, tile_bag: TileBag) -> None:
        self._rack.clear()
        for _ in range(INITIAL_TILE_COUNT):
            self._rack.add_to_rack(tile_bag.get_random_letter())

    def add_tiles(self, tiles: List[LETTER]) -> None:
        for tile in tiles:
            self._rack.add_to_rack(tile)
