from typing import List, Dict, Tuple
from dataclasses import dataclass

from game.enums import *
from game.observer import Observer

from .globals import *
from .utils import *
from .components import *

@dataclass(frozen=True)
class PlayerMeta:
    PLAYER_ID: int
    PLAYER_NAME: str
    PLAYER_TYPE: PlayerType
    PLAYER_STATE: PlayerState
    IS_ADMIN: bool
    PLAY_ORDER: int
    PLAYER_POINTS: int

class Player(Observer):
    def __init__(self, board: Board, name: str):
        super().__init__()
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

        self.set_player_state(PlayerState.LOBBY_WAITING)  # Created player waits in the lobby

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
        if self._player_state == player_state: return
        print(f'Player ({self._player_id}) State:  {PlayerState.to_string(self._player_state)} -> {PlayerState.to_string(player_state)}')
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
        self._player_state = PlayerState.LOBBY_READY

    def widthdraw(self) -> None:
        self._player_state = PlayerState.LOST

    def play_turn(self) -> Tuple[int, WORD]:
        if not (self._player_state == PlayerState.PLAYING):
            return None, None
        return None, None

    def get_serialized_rack(self) -> Dict[LETTER, int]:
        return self._rack.serialize()

    def remove_from_rack(self, tile: TILE) -> None:
        self._rack.remove_tile(tile)

    def initialize_rack(self, tile_bag: TileBag) -> None:
        self._rack.clear()
        for _ in range(INITIAL_TILE_COUNT):
            self._rack.add_tile(tile_bag.get_random_tile())

    def add_tile(self, tile: TILE) -> None:
        self._rack.add_tile(tile)

    def add_tiles(self, tiles: List[TILE]) -> None:
        for tile in tiles:
            self._rack.add_tile(tile)

    def get_rack(self) -> List[TILE]:
        return self._rack.get_rack()
