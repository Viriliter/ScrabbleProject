# Import specific classes or functions to expose them at the package level
from .globals import MIN_PLAYER_COUNT, INITIAL_TILE_COUNT, BOARD_ROW, BOARD_COL, PREMIUM_CELLS
from .utils import *
from .observer import Observer, Subject
from .components import TileBag, Rack, Board, DictionaryWrapper
from .player import PlayerMeta, Player
from .computer_player import ComputerPlayer
from .human_player import HumanPlayer
from .scrabble import Board, GameMeta, Scrabble
from .enums import PlayerPrivileges, PlayerState, PlayerType, GameState

# Define what is available when importing the package
__all__ = [
    'MIN_PLAYER_COUNT',
    'INITIAL_TILE_COUNT',
    'BOARD_ROW',
    'BOARD_COL',
    'PREMIUM_CELLS',
    'generate_unique_id',
    'get_absolute_path',
    'Observer', 
    'Subject',
    'TileBag',
    'Rack',
    'Board',
    'DictionaryWrapper',
    'PlayerType',
    'PlayerPrivileges',
    'PlayerState',
    'PlayerMeta',
    'Player',
    'ComputerPlayer',
    'HumanPlayer',
    'GameMeta',
    'GameState',
    'Scrabble'
]