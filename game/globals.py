from typing import List, Dict, Tuple, final
from dataclasses import dataclass

# Cell Location
class CL:
    def __init__(self, row: int, col: int):
        self._row = row
        self._col = col

    @property
    def row(self) -> int:
        return self._row

    @row.setter
    def row(self, value: int):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Row must be a non-negative integer")
        self._row = value

    @property
    def col(self) -> int:
        return self._col

    @col.setter
    def col(self, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError("Column must be a non-negative integer")
        self._col = value
    
    def __hash__(self):
        return hash((self.row, self.col))

    def __eq__(self, other):
        return isinstance(other, CL) and self.row == other.row and self.col == other.col
    
    def __str__(self) -> str:
        return f'{chr(65 + self._col)}{self._row+1}'

    def __iter__(self):
        for key in self.__dict__:
            yield key, getattr(self, key)

# Cell Type
class CT:
    ORDINARY = 0
    DOUBLE_LETTER = 1
    DOUBLE_WORD = 2
    TRIPLE_LETTER = 3
    TRIPLE_WORD = 4

# (CellLocation, CellType)
SPECIAL_CELLS: Dict[CL, CT] = {
    CL(0,0):    CT.TRIPLE_WORD,
    CL(0,7):    CT.TRIPLE_WORD,
    CL(0,14):   CT.TRIPLE_WORD,
    CL(7,0):    CT.TRIPLE_WORD,
    CL(7,14):   CT.TRIPLE_WORD,
    CL(14,0):   CT.TRIPLE_WORD,
    CL(14,7):   CT.TRIPLE_WORD,
    CL(14,14):  CT.TRIPLE_WORD,
    CL(1,5):    CT.TRIPLE_LETTER,
    CL(1,9):    CT.TRIPLE_LETTER,
    CL(5,1):    CT.TRIPLE_LETTER,
    CL(5,5):    CT.TRIPLE_LETTER,
    CL(5,9):    CT.TRIPLE_LETTER,
    CL(5,13):   CT.TRIPLE_LETTER,
    CL(9,1):    CT.TRIPLE_LETTER,
    CL(9,5):    CT.TRIPLE_LETTER,
    CL(9,9):    CT.TRIPLE_LETTER,
    CL(9,13):   CT.TRIPLE_LETTER,
    CL(13,5):   CT.TRIPLE_LETTER,
    CL(13,9):   CT.TRIPLE_LETTER,
    CL(7,7):    CT.DOUBLE_WORD, # Center Cell
    CL(1,1):    CT.DOUBLE_WORD,
    CL(2,2):    CT.DOUBLE_WORD,
    CL(3,3):    CT.DOUBLE_WORD,
    CL(4,4):    CT.DOUBLE_WORD,
    CL(10,10):  CT.DOUBLE_WORD,
    CL(11,11):  CT.DOUBLE_WORD,
    CL(12,12):  CT.DOUBLE_WORD,
    CL(13,13):  CT.DOUBLE_WORD,
    CL(1,13):   CT.DOUBLE_WORD,
    CL(2,12):   CT.DOUBLE_WORD,
    CL(3,11):   CT.DOUBLE_WORD,
    CL(4,10):   CT.DOUBLE_WORD,
    CL(10,4):   CT.DOUBLE_WORD,
    CL(11,3):   CT.DOUBLE_WORD,
    CL(12,2):   CT.DOUBLE_WORD,
    CL(13,1):   CT.DOUBLE_WORD,
    CL(0,3):    CT.DOUBLE_LETTER,
    CL(0,11):   CT.DOUBLE_LETTER,
    CL(2,6):    CT.DOUBLE_LETTER,
    CL(2,8):    CT.DOUBLE_LETTER,
    CL(3,0):    CT.DOUBLE_LETTER,
    CL(3,7):    CT.DOUBLE_LETTER,
    CL(3,14):   CT.DOUBLE_LETTER,
    CL(6,2):    CT.DOUBLE_LETTER,
    CL(6,6):    CT.DOUBLE_LETTER,
    CL(6,8):    CT.DOUBLE_LETTER,
    CL(6,12):   CT.DOUBLE_LETTER,
    CL(7,3):    CT.DOUBLE_LETTER,
    CL(7,11):   CT.DOUBLE_LETTER,
    CL(8,2):    CT.DOUBLE_LETTER,
    CL(8,6):    CT.DOUBLE_LETTER,
    CL(8,8):    CT.DOUBLE_LETTER,
    CL(8,12):   CT.DOUBLE_LETTER,
    CL(11,0):   CT.DOUBLE_LETTER,
    CL(11,7):   CT.DOUBLE_LETTER,
    CL(11,14):  CT.DOUBLE_LETTER,
    CL(12,6):   CT.DOUBLE_LETTER,
    CL(12,8):   CT.DOUBLE_LETTER,
    CL(14,3):   CT.DOUBLE_LETTER,
    CL(14,11):  CT.DOUBLE_LETTER
} 

# Define LETTER as string to represent single character
LETTER = str

@final
class TILE:
    def __init__(self, row: int, col: int, letter: str, is_blank=False, score=0):
        self._row = row
        self._col = col
        self._letter = letter
        self._is_blank = is_blank
        self._score = score

    @property
    def row(self) -> int:
        return self._row

    @row.setter
    def row(self, row: int) -> None:
        self._row = row
    
    @property
    def col(self) -> int:
        return self._col

    @col.setter
    def col(self, col: int) -> None:
        self._col = col
    
    @property
    def letter(self) -> str:
        return self._letter

    @letter.setter
    def letter(self, letter: str) -> None:
        self._letter = letter
    
    @property
    def is_blank(self) -> bool:
        return self._is_blank

    @is_blank.setter
    def is_blank(self, is_blank: bool) -> None:
        self._is_blank = is_blank

    @property
    def score(self) -> int:
        return self._score

    @score.setter
    def score(self, score: int) -> None:
        self._score = score

    def __iter__(self):
        for key in self.__dict__:
            yield key, getattr(self, key)

    def __str__(self) -> str:
        return f'({self.row},{self.col},{self.letter})'

# Define WORD as a list of TILEs
WORD = List[TILE]

# Define Alphabet as a Dict includes letters with their counts and points   
ALPHABET = Dict[LETTER, Tuple[int, int]]

@dataclass(frozen=True)
class LANGUAGE:
    alphabet: ALPHABET
    uri: str

BOARD_ROW: int = 15

BOARD_COL: int = 15

# Declare initial tile count for each player
INITIAL_TILE_COUNT: int = 7

MIN_PLAYER_COUNT: int = 2

AI_PLAYER_NAMES = ["Socrates", "Plato", "Aristotle", "Marx"]

# Letter: (Points, Count)
ALPH_ENGLISH: ALPHABET = {
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

ALPH_TURKISH: ALPHABET = {
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

class LANG_KEYS:
    ENG = "ENG"
    TUR = "TUR"

LANGUAGES: Dict[LANG_KEYS, LANGUAGE] = {LANG_KEYS.ENG: LANGUAGE(ALPH_ENGLISH, "dictionaries/CSW2021_English.dict"),
                                        LANG_KEYS.TUR: LANGUAGE(ALPH_TURKISH, "dictionaries/British_English.dict")}
