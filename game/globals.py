from typing import List, Dict, Tuple
from dataclasses import dataclass

# Cell Location
@dataclass(frozen=True)
class CL:
    row: int
    col: int

# Cell Type
class CT:
    ORDINARY = 0
    DOUBLE_LETTER = 1
    DOUBLE_WORD = 2
    TRIPLE_LETTER = 3
    TRIPLE_WORD = 4

BOARD_ROW = 15

BOARD_COL = 15

# (CellLocation, CellType)
SPECIAL_CELLS: Dict[CL, CT] = {
    CL(0,0),    CT.TRIPLE_WORD,
    CL(0,7),    CT.TRIPLE_WORD,
    CL(0,14),   CT.TRIPLE_WORD,
    CL(7,0),    CT.TRIPLE_WORD,
    CL(7,14),   CT.TRIPLE_WORD,
    CL(14,0),   CT.TRIPLE_WORD,
    CL(14,7),   CT.TRIPLE_WORD,
    CL(14,14),  CT.TRIPLE_WORD,
    CL(1,5),    CT.TRIPLE_LETTER,
    CL(1,9),    CT.TRIPLE_LETTER,
    CL(5,1),    CT.TRIPLE_LETTER,
    CL(5,5),    CT.TRIPLE_LETTER,
    CL(5,9),    CT.TRIPLE_LETTER,
    CL(5,13),   CT.TRIPLE_LETTER,
    CL(9,1),    CT.TRIPLE_LETTER,
    CL(9,5),    CT.TRIPLE_LETTER,
    CL(9,9),    CT.TRIPLE_LETTER,
    CL(9,13),   CT.TRIPLE_LETTER,
    CL(13,5),   CT.TRIPLE_LETTER,
    CL(13,9),   CT.TRIPLE_LETTER,
    CL(7,7),    CT.DOUBLE_WORD, # Center Cell
    CL(1,1),    CT.DOUBLE_WORD,
    CL(2,2),    CT.DOUBLE_WORD,
    CL(3,3),    CT.DOUBLE_WORD,
    CL(4,4),    CT.DOUBLE_WORD,
    CL(10,10),  CT.DOUBLE_WORD,
    CL(11,11),  CT.DOUBLE_WORD,
    CL(12,12),  CT.DOUBLE_WORD,
    CL(13,13),  CT.DOUBLE_WORD,
    CL(1,13),   CT.DOUBLE_WORD,
    CL(2,12),   CT.DOUBLE_WORD,
    CL(3,11),   CT.DOUBLE_WORD,
    CL(4,10),   CT.DOUBLE_WORD,
    CL(10,4),   CT.DOUBLE_WORD,
    CL(11,3),   CT.DOUBLE_WORD,
    CL(12,2),   CT.DOUBLE_WORD,
    CL(13,1),   CT.DOUBLE_WORD,
    CL(0,3),    CT.DOUBLE_LETTER,
    CL(0,11),   CT.DOUBLE_LETTER,
    CL(2,6),    CT.DOUBLE_LETTER,
    CL(2,8),    CT.DOUBLE_LETTER,
    CL(3,0),    CT.DOUBLE_LETTER,
    CL(3,7),    CT.DOUBLE_LETTER,
    CL(3,14),   CT.DOUBLE_LETTER,
    CL(6,2),    CT.DOUBLE_LETTER,
    CL(6,6),    CT.DOUBLE_LETTER,
    CL(6,8),    CT.DOUBLE_LETTER,
    CL(6,12),   CT.DOUBLE_LETTER,
    CL(7,3),    CT.DOUBLE_LETTER,
    CL(7,11),   CT.DOUBLE_LETTER,
    CL(8,2),    CT.DOUBLE_LETTER,
    CL(8,6),    CT.DOUBLE_LETTER,
    CL(8,8),    CT.DOUBLE_LETTER,
    CL(8,12),   CT.DOUBLE_LETTER,
    CL(11,0),   CT.DOUBLE_LETTER,
    CL(11,7),   CT.DOUBLE_LETTER,
    CL(11,14),  CT.DOUBLE_LETTER,
    CL(12,6),   CT.DOUBLE_LETTER,
    CL(12,8),   CT.DOUBLE_LETTER,
    CL(14,3),   CT.DOUBLE_LETTER,
    CL(14,11),  CT.DOUBLE_LETTER
} 

# Letter: (Points, Count)
ENGLISH_TILES: Dict[str, Tuple[int, int]] = {
    'A': (9, 1),
    'B': (2, 3),
    'C': (2, 3),
    'D': (4, 2),
    'E': (12, 1),
    'F': (2, 4),
    'G': (3, 2),
    'H': (2, 4),
    'I': (9, 1),
    'J': (1, 8),
    'K': (1, 5),
    'L': (4, 1),
    'M': (2, 3),
    'N': (6, 1),
    'O': (8, 1),
    'P': (2, 3),
    'Q': (1, 10),
    'R': (6, 1),
    'S': (4, 1),
    'T': (6, 1),
    'U': (4, 1),
    'V': (2, 4),
    'W': (2, 4),
    'X': (1, 8),
    'Y': (2, 4),
    'Z': (1, 10),
    ' ': (2, 0)
}

# Declare initial tile count for each player
INITIAL_TILE_COUNT: int = 7

MIN_PLAYER_COUNT: int = 2

AI_PLAYER_NAMES = ["Balzac", "Orwell", "Shelley", "Agatha"]

@dataclass(frozen=True)
class LETTER:
    row: int
    col: int
    letter: chr

# Define WORD as a List of LETTERs
WORD = List[LETTER]
