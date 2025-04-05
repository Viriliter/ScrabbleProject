from typing import List, Dict, Tuple
from dataclasses import dataclass

from game.enums import *
from game.observer import Observer

from .globals import *
from .utils import *
from .components import *

@dataclass(frozen=True)
class PlayerMeta:
    """
    @brief PlayerMeta class representing the metadata of a player.
    @param PLAYER_ID: Unique identifier for the player.
    @param PLAYER_NAME: Name of the player.
    @param PLAYER_TYPE: Type of the player (human or AI).
    @param PLAYER_STATE: Current state of the player (playing, waiting, etc.).
    @param IS_ADMIN: Indicates if the player is an admin.
    @param PLAY_ORDER: Order in which the player plays.
    @param PLAYER_POINTS: Points scored by the player.
    @note: The dataclass decorator automatically generates the __init__, __repr__, and other methods.
    """
    PLAYER_ID: int
    PLAYER_NAME: str
    PLAYER_TYPE: PlayerType
    PLAYER_STATE: PlayerState
    IS_ADMIN: bool
    PLAY_ORDER: int
    PLAYER_POINTS: int

class Player(Observer):
    """
    @brief Player class representing a player in the game.
    """
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
        
        self._player_strategy = PlayerStrategy.UNDEFINED

        # Create game components
        self._rack = Rack()

        self.set_player_state(PlayerState.LOBBY_WAITING)  # Created player waits in the lobby

    def set_as_admin(self) -> None:
        """
        @brief Set the player as an admin.
        """
        self._player_privileges = PlayerPrivileges.ADMIN

    def is_admin(self) -> bool:
        """
        @brief Check if the player is an admin.
        @return True if the player is an admin, False otherwise.
        """
        if self._player_privileges == PlayerPrivileges.ADMIN: return True
        else: return False

    def is_active(self) -> bool:
        """
        @brief Check if the player is active (playing or waiting).
        @return True if the player is active, False otherwise.
        """
        if self._player_state == PlayerState.PLAYING or self._player_state == PlayerState.WAITING:
            return True
        else:
            return False

    def set_player_state(self, player_state: PlayerState) -> None:
        """
        @brief Set the state of the player.
        @param player_state: The new state of the player.
        """
        if self._player_state == player_state: return
        print(f'Player ({self._player_id}) State:  {PlayerState.to_string(self._player_state)} -> {PlayerState.to_string(player_state)}')
        self._player_state = player_state

    def get_player_state(self) -> PlayerState:
        """
        @brief Get the current state of the player.
        @return The current state of the player.
        """
        return self._player_state
   
    def get_player_id(self) -> str:
        """
        @brief Get the unique identifier of the player.
        @return The unique identifier of the player.
        """
        return self._player_id

    def get_player_name(self) -> str:
        """
        @brief Get the name of the player.
        @return The name of the player.
        """
        return self._player_name

    def set_player_name(self, player_name: str) -> None:
        """
        @brief Set the name of the player.
        @param player_name: The new name of the player.
        """
        self._player_name = player_name

    def get_play_order(self) -> int:
        """
        @brief Get the play order of the player.
        @return The play order of the player.
        """
        return self._play_order

    def set_play_order(self, play_order: int) -> None:
        """
        @brief Set the play order of the player.
        @param play_order: The new play order of the player.
        """
        self._play_order = play_order

    def is_order_requested(self) -> bool:
        """
        @brief Check if the player has requested a play order.
        @return True if the player has requested a play order, False otherwise.
        """
        return True if self._play_order < 100 else False

    def is_rack_empty(self) -> bool:
        """
        @brief Check if the player's rack is empty.
        @return True if the rack is empty, False otherwise.
        """
        return True if self._rack is not None and self._rack.count() == 0 else False

    def get_player_meta(self) -> PlayerMeta:
        """
        @brief Get the metadata of the player.
        @return A PlayerMeta object containing the player's metadata.
        """
        return PlayerMeta(self._player_id, self._player_name, self._player_type, self._player_state, self.is_admin(), self._play_order, self._points)

    def get_player_type(self) -> PlayerType:
        """
        @brief Get the type of the player.
        @return The type of the player (human or AI).
        """
        return self._player_type

    def set_player_type(self, player_type: PlayerType) -> None:
        """
        @brief Set the type of the player.
        @param player_type: The new type of the player (human or AI).
        """
        self._player_type = player_type

    def get_player_privilege(self) -> PlayerPrivileges:
        """
        @brief Get the privileges of the player.
        @return The privileges of the player.
        """
        return self._player_privileges

    def get_player_strategy(self) -> PlayerStrategy:
        return self._player_strategy

    def set_player_strategy(self, player_strategy: PlayerStrategy) -> None:
        print(f'Player ({self._player_id}) Strategy:  {PlayerStrategy.to_string(self._player_strategy)} -> {PlayerStrategy.to_string(player_strategy)}')
        self._player_strategy = player_strategy

    def get_points(self) -> int:
        """
        @brief Get the points scored by the player.
        @return The points scored by the player.
        """
        return self._points

    def set_points(self, points: int) -> None:
        """
        @brief Set the points scored by the player.
        @param points: The new points scored by the player.
        """
        self._points = points

    def add_points(self, points: int) -> None:
        """
        @brief Add points to the player's score.
        @param points: The points to be added.
        """
        self._points += points

    def remove_points(self, points: int) -> None:
        """
        @brief Remove points from the player's score.
        @param points: The points to be removed.
        """
        self._points -= points

    def increment_skip_count(self) -> None:
        """
        @brief Increment the skip count of the player.
        """
        self._skip_count += 1

    def get_skip_count(self) -> int:
        """
        @brief Get the skip count of the player.
        @return The skip count of the player.
        """
        return self._skip_count
    
    def enter_game(self, tile_bag: TileBag) -> None:
        """
        @brief Enter the game and initialize the player's rack.
        @param tile_bag: The tile bag from which to draw tiles.
        """
        self._player_state = PlayerState.LOBBY_READY

    def widthdraw(self) -> None:
        """
        @brief Withdraw the player from the game.
        """
        self._player_state = PlayerState.LOST

    def play_turn(self) -> Tuple[int, WORD]:
        """
        @brief Play a turn in the game.
        @return A tuple containing the score and the word played.
        """
        if not (self._player_state == PlayerState.PLAYING):
            return None, None
        return None, None

    def get_serialized_rack(self) -> Dict[LETTER, int]:
        """
        @brief Get the serialized representation of the player's rack.
        @return A dictionary representing the rack, where keys are letters and values are counts.
        """
        return self._rack.serialize()

    def remove_from_rack(self, tile: TILE) -> None:
        """
        @brief Remove a tile from the player's rack.
        @param tile: The tile to be removed.
        """

        self._rack.remove_tile(tile)

    def initialize_rack(self, tile_bag: TileBag) -> None:
        """
        @brief Initialize the player's rack with tiles from the tile bag.
        @param tile_bag: The tile bag from which to draw tiles.
        """
        self._rack.clear()
        for _ in range(INITIAL_TILE_COUNT):
            self._rack.add_tile(tile_bag.get_random_tile())

    def add_tile(self, tile: TILE) -> None:
        """
        @brief Add a tile to the player's rack.
        @param tile: The tile to be added.
        """
        self._rack.add_tile(tile)

    def add_tiles(self, tiles: List[TILE]) -> None:
        """
        @brief Add multiple tiles to the player's rack.
        @param tiles: A list of tiles to be added.
        """
        for tile in tiles:
            self._rack.add_tile(tile)

    def get_rack(self) -> List[TILE]:
        """
        @brief Get the player's rack.
        @return A list of tiles in the player's rack.
        """
        return self._rack.get_rack()
