from typing import List, Dict, Tuple
from dataclasses import dataclass

from .globals import *
from .utils import *
from .components import *

from .player import *

class ComputerPlayer(Player):
    def __init__(self, board: Board, name=""):
        super().__init__(board, name)
        self._player_name: str = name
        self._player_type: PlayerType = PlayerType.COMPUTER
        self._player_privileges: PlayerPrivileges = PlayerPrivileges.PLAYER
        
        self.set_player_state(PlayerState.READY)

    def play_turn(self) -> Tuple[Optional[int], Optional[WORD]]:
        if not (self._player_state == PlayerState.PLAYING):
            return None, None
        
        best_moves = self._board.find_best_play(self._rack.get_rack())
        best_move: MOVE = best_moves[0]
        return best_move.score, best_move.word
