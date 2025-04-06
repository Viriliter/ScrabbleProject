import copy
from enum import Enum
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
PREMIUM_CELLS: Dict[CL, CT] = {
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
    def __init__(self, row: int=-1, col: int=-1, letter: str="", point=-1, is_blank=False, is_locked=False):
        self._row = row
        self._col = col
        self._letter = letter
        self._is_blank = True if letter==BLANK_LETTER else is_blank
        self._is_locked = is_locked
        self._point = ALPH_ENGLISH[letter][1] if point == -1 else point

        if (letter==BLANK_LETTER):
            print(f"Tile - row: {row} col:{col} letter: {letter} is_blank: {is_blank}")

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
    def is_locked(self) -> bool:
        return self._is_locked

    @is_locked.setter
    def is_locked(self, is_locked: bool) -> None:
        self._is_locked = is_locked

    @property
    def point(self) -> int:
        return self._point

    @point.setter
    def point(self, point: int) -> None:
        self._point = point

    def is_equal(self, other: 'TILE') -> bool:
        """
        @brief Check if the tiles are at same location and have same letter
        """
        return (self.row == other.row and self.col == other.col and 
                self.letter == other.letter and self.is_blank == other.is_blank)

    def is_similar(self, other: 'TILE') -> bool:
        """
        @brief Check if the tiles have same letter an is_blank
        """
        if self.is_blank and other.is_blank:
            return True
        if not self.is_blank and not other.is_blank:
            return self.letter == other.letter
        return False
    
    @staticmethod
    def print_word(word: 'WORD', file=None) -> None:
        """
        @brief Print the word
        @param word: List of tiles
        @param file: File to write the word
        """
        temp_word: WORD = copy.deepcopy(word)
        if len(temp_word) == 0: return
        
        # Check the direction based on row and column values of the tiles
        rows = [tile.row for tile in temp_word]
        cols = [tile.col for tile in temp_word]

        if len(set(rows)) == 1:  # All tiles are in the same row (across)
            direction = 'across'
            # Sort by column (left to right)
            temp_word = sorted(temp_word, key=lambda tile: tile.col)
            positions = cols
        elif len(set(cols)) == 1:  # All tiles are in the same column (down)
            direction = 'down'
            # Sort by row (top to bottom)
            temp_word = sorted(temp_word, key=lambda tile: tile.row)
            positions = rows
        else:
            print(("Tiles are not aligned. It is not a word"))
            return
        
        # Print the sorted tiles in the determined direction
        result = ""
        for i, tile in enumerate(temp_word):
            if i > 0:  # If it's not the first tile, check for a gap
                # Check if there's a gap between consecutive tiles
                if positions[i] - positions[i - 1] > 1:
                    result += "."
            result += str(tile.letter)

        print(result, file=file)

    @staticmethod
    def stringify_word(word: 'WORD', file=None) -> str:
        def col_to_letter(col_idx):
            result = ''
            while col_idx >= 0:
                result = chr(col_idx % 26 + ord('A')) + result
                col_idx = col_idx // 26 - 1
            return result

        parts = []
        for tile in word:
            col_letter = col_to_letter(tile.col)
            row_number = tile.row + 1  # Adjust for 1-based row display
            parts.append(f"({tile.letter}, {col_letter}{row_number})")

        result_str = ', '.join(parts)
        
        if file:
            print(result_str, file=file)
        
        return result_str

    def __iter__(self):
        for key in self.__dict__:
            yield key, getattr(self, key)

    def __str__(self) -> str:
        return f'({self.row},{self.col},{self.letter})'
    
    def __repr__(self) -> str:
        return self.__str__()
   
# Define WORD as a list of TILEs
WORD = List[TILE]

BLANK_LETTER: str = " "

class LetterType(Enum):
    UNDEFINED = 0
    CONSONANT = 1
    VOWEL = 2

LETTER_COUNT = int
LETTER_POINTS = int
LETTER_FREQUENCY = int

# Define Alphabet as a Dict includes letters with their counts and points   
ALPHABET = Dict[LETTER, Tuple[LETTER_COUNT, LETTER_POINTS, LetterType, LETTER_FREQUENCY]]

@dataclass(frozen=True)
class LANGUAGE:
    alphabet: ALPHABET
    uri: str

@dataclass(frozen=True)
class MOVE:
    score: int
    word: WORD
    
    def __lt__(self, other: 'MOVE') -> bool:
        return self.score > other.score
    
    def serialize(self) -> Tuple[str, int]:
        return ' '.join([str(tile) for tile in self.word]), self.score

BOARD_ROW: int = 15

BOARD_COL: int = 15

# Declare initial tile count for each player
RACK_CAPACITY: int = 7

MIN_PLAYER_COUNT: int = 2

COMPUTER_PLAYER_NAMES = ["Socrates", "Plato", "Aristotle", "Pythagoras"]

# Letter: (Count, Points, LetterType, Frequency)
ALPH_ENGLISH: ALPHABET = {
    'A': (9 , 1 , LetterType.VOWEL    , 8.200),
    'B': (2 , 3 , LetterType.CONSONANT, 1.500),
    'C': (2 , 3 , LetterType.CONSONANT, 2.800),
    'D': (4 , 2 , LetterType.CONSONANT, 4.300),
    'E': (12, 1 , LetterType.VOWEL    , 13.00),
    'F': (2 , 4 , LetterType.CONSONANT, 2.200),
    'G': (3 , 2 , LetterType.CONSONANT, 2.000),
    'H': (2 , 4 , LetterType.CONSONANT, 6.100),
    'I': (9 , 1 , LetterType.VOWEL    , 7.000),
    'J': (1 , 8 , LetterType.CONSONANT, 0.150),
    'K': (1 , 5 , LetterType.CONSONANT, 0.770),
    'L': (4 , 1 , LetterType.CONSONANT, 4.000),
    'M': (2 , 3 , LetterType.CONSONANT, 2.400),
    'N': (6 , 1 , LetterType.CONSONANT, 6.700),
    'O': (8 , 1 , LetterType.VOWEL    , 7.500),
    'P': (2 , 3 , LetterType.CONSONANT, 1.900),
    'Q': (1 , 10, LetterType.CONSONANT, 0.095),
    'R': (6 , 1 , LetterType.CONSONANT, 6.000),
    'S': (4 , 1 , LetterType.CONSONANT, 6.300),
    'T': (6 , 1 , LetterType.CONSONANT, 9.100),
    'U': (4 , 1 , LetterType.VOWEL    , 2.800),
    'V': (2 , 4 , LetterType.CONSONANT, 0.980),
    'W': (2 , 4 , LetterType.CONSONANT, 2.400),
    'X': (1 , 8 , LetterType.CONSONANT, 0.150),
    'Y': (2 , 4 , LetterType.CONSONANT, 2.000),
    'Z': (1 , 10, LetterType.CONSONANT, 0.074),
    ' ': (2 , 0 , LetterType.UNDEFINED, 0.000)
}

ALPH_TURKISH: ALPHABET = {
    'A': (9 , 1 , LetterType.VOWEL,     11.92),
    'B': (2 , 3 , LetterType.CONSONANT, 2.840),
    'C': (2 , 3 , LetterType.CONSONANT, 1.070),
    'Ç': (2 , 3 , LetterType.CONSONANT, 1.250),
    'D': (4 , 2 , LetterType.CONSONANT, 3.290),
    'E': (12, 1 , LetterType.VOWEL,     8.910),
    'F': (2 , 4 , LetterType.CONSONANT, 0.460),
    'G': (3 , 2 , LetterType.CONSONANT, 1.220),
    'Ğ': (3 , 2 , LetterType.CONSONANT, 0.500),
    'H': (2 , 4 , LetterType.CONSONANT, 0.780),
    'I': (9 , 1 , LetterType.VOWEL,     8.600),
    'İ': (9 , 1 , LetterType.VOWEL,     8.600),
    'J': (1 , 8 , LetterType.CONSONANT, 0.030),
    'K': (1 , 5 , LetterType.CONSONANT, 5.680),
    'L': (4 , 1 , LetterType.CONSONANT, 5.920),
    'M': (2 , 3 , LetterType.CONSONANT, 3.810),
    'N': (6 , 1 , LetterType.CONSONANT, 7.980),
    'O': (8 , 1 , LetterType.VOWEL,     3.000),
    'Ö': (8 , 1 , LetterType.VOWEL,     0.380),
    'P': (2 , 3 , LetterType.CONSONANT, 1.020),
    'Q': (1 , 10, LetterType.CONSONANT, 6.720),
    'R': (6 , 1 , LetterType.CONSONANT, 1.840),
    'S': (4 , 1 , LetterType.CONSONANT, 1.140),
    'T': (6 , 1 , LetterType.CONSONANT, 5.630),
    'U': (4 , 1 , LetterType.VOWEL,     3.750),
    'Ü': (4 , 1 , LetterType.VOWEL,     1.850),
    'V': (2 , 4 , LetterType.CONSONANT, 0.630),
    'Y': (2 , 4 , LetterType.CONSONANT, 3.330),
    'Z': (1 , 10, LetterType.CONSONANT, 1.500),
    ' ': (2 , 0 , LetterType.UNDEFINED, 0.000)
}

class LANG_KEYS:
    ENG = "ENG"
    TUR = "TUR"

LANGUAGES: Dict[LANG_KEYS, LANGUAGE] = {LANG_KEYS.ENG: LANGUAGE(ALPH_ENGLISH, "dictionaries/Oxford_5000.dict"),
                                        LANG_KEYS.TUR: LANGUAGE(ALPH_TURKISH, "dictionaries/British_English.dict")}
