# Import specific classes or functions to expose them at the package level
from .globals import MIN_PLAYER_COUNT, INITIAL_TILE_COUNT, BOARD_ROW, BOARD_COL, SPECIAL_CELLS
from .utils import *
from .components import TileBag, Rack, Board, Dictionary
from .player import PlayerType, PlayerPrivileges, PlayerState, PlayerMeta, Player
from .scrabble import Board, GameMeta, GameState, Game

# Define what is available when importing the package
__all__ = [
    'MIN_PLAYER_COUNT',
    'INITIAL_TILE_COUNT',
    'BOARD_ROW',
    'BOARD_COL',
    'SPECIAL_CELLS',
    'generate_unique_id',
    'TileBag',
    'Rack',
    'Board',
    'Dictionary',
    'PlayerType',
    'PlayerPrivileges',
    'PlayerState',
    'PlayerMeta',
    'Player',
    'GameMeta',
    'GameState',
    'Game'
]