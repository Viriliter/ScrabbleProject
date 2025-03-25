from typing import List, Dict, Tuple
from dataclasses import dataclass

from .globals import *
from .utils import *
from .components import *

from .player import *

class HumanPlayer(Player):
    def __init__(self, board: Board, player_privileges=PlayerPrivileges.PLAYER):
        super().__init__(board)
        self._player_type = PlayerType.HUMAN
        self._player_privileges = player_privileges
