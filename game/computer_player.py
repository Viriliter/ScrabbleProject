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

    def play_turn(self, word: WORD) -> Tuple[int, WORD]:
        if not (self._player_state == PlayerState.PLAYING):
            return None, None
        return self.find_best_play()
        
    def best_opening_play(self, rack_tiles: List[TILE]) -> Tuple[int, WORD]:
        ruck = "".join(t.letter if t.letter else " " for t in rack_tiles)
        dictionary = self._board.get_dictionary()

        choices = dictionary.find_anagrams(ruck)
        drow = random.randint(0, 1)
        dcol = (drow + 1) % 2
        vertical = dcol == 0
        best_score = 0
        best_word = []
        
        for choice in choices:
            placements: List[TILE] = []
            shrunk_rack = rack_tiles[:]
            for c in choice:
                rack_tile = next((t for t in shrunk_rack if t.letter == c), None) or next((t for t in shrunk_rack if t.is_blank), None)
                assert rack_tile, "Can't do this with the available tiles"
                # Placement will be fixed later
                placements.append(TILE(0, 0, c, rack_tile.point, rack_tile.is_blank))
                shrunk_rack.remove(rack_tile)
            
            mid = self._board.midcol if vertical else self._board.midrow
            for end in range(mid, mid + len(choice)):
                row, col = (mid, end) if vertical else (end, mid)
                score = self._board.score_play(row, col, drow, dcol, placements)
                score += self._board.calculate_bonus(len(placements))
                
                if score > best_score:
                    best_score = score
                    for i, placement in enumerate(placements):
                        pos = end - len(placements) + i + 1
                        placement.col = self._board.midcol if dcol == 0 else pos * dcol
                        placement.row = self._board.midrow if drow == 0 else pos * drow
                    
                    print("£££££££££££££")
                    PRINT_WORD(best_word)
                    print("£££££££££££££")

                    best_word = placements
                    
                    #TODO report the placement
                    #report({"placements": placements, "word": choice, "score": score})
        
        return (best_score, best_word)

    def find_best_play(self) -> Tuple[int, WORD]:
        dictionary = self._board.get_dictionary()

        rack_letters = self._rack.get_rack()
        rack_tiles: List[TILE] = []
        for letter in rack_letters:
            is_blank = True if letter == BLANK_LETTER else False
            rack_tiles.append(TILE(0, 0, letter, dictionary.get_alphabet()[letter][1], is_blank, False))

        rack_tiles = sorted(rack_tiles, key=lambda t: (-t.point, t.letter))

        best_score = 0
        best_word: WORD = []
        anchored = False
                
        # Has at least one anchor been explored? If there are no anchors, we need to compute an opening play
        anchored = False

        for col in range(self._board.cols):
            for row in range(self._board.rows):
                # An anchor is any square that has a tile and has an
                # adjacent blank that can be extended into to form a word
                if self._board.is_anchor(row, col):
                    if not anchored:
                        # What letters can be used to form a valid cross word? 
                        # The whole alphabet if the rack contains a blank, the rack otherwise.
                        available = dictionary.get_all_letters() if any(t.is_blank for t in rack_tiles) else [t.letter for t in rack_tiles]
                        self._board.compute_cross_checks(available)
                        anchored = True

                    anchor_tile = self._board.at(row, col)

                    roots = dictionary.get_sequence_roots(anchor_tile.letter)
                    for anchor_node in roots:
                        # Try and back up then forward through the dictionary to find longer sequences across
                        self._board.back(row, col, 0, 1,
                                         rack_tiles, 0,
                                         anchor_node, anchor_node,
                                         [ anchor_tile ])

                        # down
                        self._board.back(row, col, 1, 0,
                                         rack_tiles, 0,
                                         anchor_node, anchor_node,
                                         [ anchor_tile ])

        return self._board.get_best_move()

        if not anchored:
            best_score, best_word = self.best_opening_play(rack_tiles)
        
        return best_score, best_word
