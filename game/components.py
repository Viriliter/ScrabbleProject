import os
import random
import copy
import heapq

from io import BytesIO
from typing import List, Dict, Tuple, Optional
from deprecated import deprecated
from dataclasses import dataclass

import numpy as np

from .globals import *
from .utils import *
from externals.dictionary import Dictionary, LetterNode

class TileBag:
    """
    @brief Class to represent the tile bag.
    The tile bag is a collection of tiles that can be drawn from.
    The bag is initialized with a set of tiles, and tiles can be drawn randomly.
    """
    def __init__(self):
        self.__reference_tiles: ALPHABET = {}
        self.__tiles: ALPHABET = {}
        self.__remaining_tiles: int = 0
        self.__picked_letters: List[LETTER] = []

    def clear(self) -> None:
        """
        @brief Clear the tile bag
        """
        self.__reference_tiles = {}
        self.__tiles = {}
        self.__remaining_tiles = 0
        self.__picked_letters = []

    def load(self, alphabet: ALPHABET) -> None:
        """
        @brief Load the tile bag with the given alphabet.
        @param alphabet: ALPHABET object containing letter information
        """
        self.clear()

        self.__reference_tiles = alphabet
        for letter, (count, points, _, _) in alphabet.items():
            if letter in self.__tiles:
                self.__tiles[letter] = (self.__tiles[letter][0] + count, points)
            else:
                self.__tiles[letter] = (count, points)
            self.__remaining_tiles += count

    def get_random_tile(self) -> Optional[TILE]:
        """
        @brief Get a random tile from the bag.
        @return: Random TILE object or None if the bag is empty
        @note: The tile is selected based on its occurance weight.
        """
        if self.__remaining_tiles == 0:
            return None  # Bag is empty

        # Randomly pick a letter according to its occurance weight
        letters, weights = zip(*[(letter, count) for letter, (count, _) in self.__tiles.items()])

        letter = random.choices(letters, weights=weights, k=1)[0]
        count, points = self.__tiles[letter]

        # Decrease the count of the letter in the bag
        if count > 1:
            self.__tiles[letter] = (count - 1, points)
        else:
            del self.__tiles[letter]  # Remove letter if no more left

        self.__remaining_tiles -= 1

        is_blank = (letter == BLANK_LETTER)
        return TILE(-1, -1, letter, points, is_blank, False)

    def put_back_letter(self, letter: LETTER) -> None:
        """
        @brief Put back a letter into the bag.
        @param letter: Letter to be put back
        """
        if letter in self.__tiles:
            count, points = self.__tiles[letter]
            self.__tiles[letter] = (count + 1, points)
        else:
            self.__tiles[letter] = (1, self.__reference_tiles[letter][1])
        self.__remaining_tiles += 1

    def get_remaining_tiles(self) -> int:
        """
        @brief Get the number of remaining tiles in the bag.
        @return: Number of remaining tiles
        """
        return self.__remaining_tiles

    def pick_letter_for_order(self) -> LETTER:
        """
        @brief Pick a letter for order.
        @return: Random letter from the bag
        """
        available_letters = set(self.__tiles.keys()) - set(self.__picked_letters)
        if not available_letters:
            raise ValueError("No available letters left to pick.")
    
        letter = random.choice(list(available_letters))
        self.__picked_letters.append(letter)
        return letter

    def get_alphabet(self) -> ALPHABET:
        """
        @brief Get the alphabet of the tile bag.
        @return: ALPHABET object
        """
        return self.__reference_tiles

class Rack:
    """
    @brief Class to represent the rack.
    The rack is a collection of tiles that can be used to form words.
    """
    def __init__(self):
        self.__container: List[TILE] = []
        
    def add_letter(self, letter: LETTER, alphabet: ALPHABET=None) -> None:
        """
        @brief Add a letter to the rack.
        @param letter: Letter to be added
        @param alphabet: Alphabet object containing letter information
        """
        is_blank = True if letter == BLANK_LETTER else False
        point = alphabet[letter][1] if alphabet is not None else 0
        point = 0 if is_blank else point
        tile = TILE(letter=letter, is_blank=is_blank, point=point, is_locked=False)
        self.__container.append(tile)

    def add_tile(self, tile: TILE) -> None:
        """
        @brief Add a tile to the rack.
        @param tile: TILE object to be added
        """
        self.__container.append(tile)

    def remove_tile(self, tile: TILE) -> None:
        """
        @brief Remove a tile from the rack.
        @param tile: TILE object to be removed
        """
        for i, t in enumerate(self.__container):
            print(f"{t.letter}({t.is_blank})==={tile.letter}({tile.is_blank})  is_similar:{t.is_similar(tile)}")
            if t.is_similar(tile):
                del self.__container[i]
                break

    def get_rack_length(self) -> int:
        """
        @brief Get the length of the rack
        @return: Length of the rack
        """
        return self.__container.__len__()

    def serialize(self) -> Dict[LETTER, int]:
        """
        @brief Serialize the rack to a dictionary representation.
        @return: Dictionary representation of the rack
        """
        letter_counts = {}
        for tile in self.__container:
            if tile.letter in letter_counts:
                letter_counts[tile.letter] += 1
            else:
                letter_counts[tile.letter] = 1
        return letter_counts

    def clear(self) -> None:
        """
        @brief Clear the rack
        """
        self.__container.clear()

    def count(self) -> int:
        """
        @brief Get the number of tiles in the rack
        @return: Number of tiles in the rack
        """
        return self.__container.__len__()
    
    def get_sorted_rack(self, reverse: bool= False) -> List[LETTER]:
        """
        @brief Get the sorted rack
        @param reverse: If True, sort in descending order
        @return: Sorted list of letters in the rack
        """
        copy_container = copy.deepcopy(self.__container)
        copy_container.sort(key=lambda x: ord(x), reverse=reverse)
        return copy_container

    def get_rack(self) -> List[TILE]:
        """
        @brief Get the rack
        @return: List of TILE objects in the rack
        """
        copy_container = copy.deepcopy(self.__container)
        return copy_container

    def get_letters(self) -> List[TILE]:
        """
        @brief Get the letters from the rack.
        @return: List of letters in the rack
        """
        letters = []
        for tile in self.__container:
            letters.append(tile.letter)

        return letters

    def stringify(self) -> str:
        """
        @brief Serializes the rack to string (for debugs)
        @return: String representation of the rack
        """
        return str(self.__container)

class DictionaryWrapper:
    """
    @brief Class to represent the dictionary wrapper.
    The dictionary is loaded from a file and provides methods to check if a word exists,
    find anagrams, and get letter frequencies.
    """
    def __init__(self, language: LANGUAGE):
        self.__alphabet: ALPHABET = language.alphabet.copy()
        self.__uri: str = get_absolute_path(language.uri)

        self.__dic = Dictionary("myDictionary")

        with open(os.path.join(os.path.dirname(__file__), 'data', self.__uri), 'rb') as f:
            data = f.read()
        self.__dic.load_dawg(BytesIO(data))

    def load_language(self, language: LANGUAGE) -> None:
        """
        @brief Load a new language dictionary
        @param language: Language object
        """
        self.__alphabet: ALPHABET = language.alphabet.copy()
        self.__uri: str = get_absolute_path(language.uri)

        self.__dic = Dictionary("myDictionary")

        with open(os.path.join(os.path.dirname(__file__), 'data', self.__uri), 'rb') as f:
            data = f.read()
        self.__dic.load_dawg(BytesIO(data))

        #TODO Add whitelist (not applicable)

        self.__dic.add_links()

    def has_word(self, word: str) -> bool:
        """
        @brief Check if the word exists in the dictionary.
        @param word: Word to check
        @return: True if the word exists, False otherwise
        """
        if len(word) == 0: return False
        return True if self.__dic.has_word(word) else False

    def has_sequence(self, word: str) -> bool:
        """
        @brief Check if the word has a sequence in the dictionary.
        @param word: Word to check
        @return: True if the word has a sequence, False otherwise
        """
        if len(word) == 0: return False
        return True if self.__dic.has_sequence(word) else False

    def get_sequence_roots(self, word: str) -> Optional[List[LetterNode]]:
        """
        @brief Get the sequence roots for the given word.
        @param word: Word to check
        @return: List of LetterNode objects representing the sequence roots
        """
        if len(word) == 0: return None
        return self.__dic.get_sequence_roots(word) if self.__dic.has_sequence(word) else None

    def find_anagrams(self, word: str) -> List[str]:
        """
        @brief Find anagrams for the given word.
        @param word: Word to find anagrams for
        @return: List of anagrams
        """
        return self.__dic.find_anagrams(word)

    def get_alphabet(self) -> ALPHABET:
        """
        @brief Get the alphabet of the dictionary.
        @return: ALPHABET object
        """
        return self.__alphabet

    def get_vowels(self) -> List[LETTER]:
        """
        @brief Get the vowels from the alphabet.
        @return: List of vowels
        """
        vowels = []
        for letter in self.__alphabet.keys():
            if (letter==BLANK_LETTER): continue
            if self.__alphabet[letter][2] == LetterType.VOWEL:
                vowels.append(letter)
        return vowels

    def get_consonants(self) -> List[LETTER]:
        """
        @brief Get the consonants from the alphabet.
        @return: List of consonants
        """
        consonants = []
        for letter in self.__alphabet.keys():
            if (letter==BLANK_LETTER): continue
            if self.__alphabet[letter][2] == LetterType.CONSONANT:
                consonants.append(letter)
        return consonants

    def get_letter_frequency(self, letter: LETTER) -> float:
        """
        @brief Get the frequency of the letter in the alphabet.
        @param letter: Letter to check
        @return: Frequency of the letter
        """
        if letter in self.__alphabet:
            return self.__alphabet[letter][3]
        return 0

    def get_all_letters(self) -> List[LETTER]:
        """
        @brief Get all letters from the alphabet.
        @return: List of all letters
        """
        out: List[LETTER] = []
        for letter in self.__alphabet.keys():
            if (letter==BLANK_LETTER): continue
            out.append(letter)
        return out

class BoardContainer(np.ndarray):
    """
    @brief Class to represent the board container.
    The board is represented as a 2D array of cells, where each cell can contain a tile.
    The board also contains premium cells that can affect the score of the words formed.
    """
    def __new__(cls, rows: int, cols: int, default_value: Optional[TILE]=None):
        obj = super().__new__(cls, shape=(rows, cols), dtype=object)
        if default_value is not None:
            for row in range(rows):
                for col in range(cols):
                    obj[row, col] = default_value  # Copy default value
        return obj

    def __getitem__(self, index: int) -> Optional[TILE]:
        return super().__getitem__(index)

    def __setitem__(self, index: int, value: Optional[TILE]) -> None:
        super().__setitem__(index, value)

    def __str__(self) -> str:
        return '\n'.join(' '.join(f"{x}" for x in row) for row in self)

    @property
    def rows(self) -> int:
        return self.shape[0]

    @property
    def cols(self) -> int:
        return self.shape[1]

    @property
    def midrow(self) -> int:
        return self.shape[0] // 2

    @property
    def midcol(self) -> int:
        return self.shape[1] // 2

    def at(self, row: int, col: int) -> Optional[TILE]:
        """
        @brief Get the tile at the specified position.
        @param row: Row index
        @param col: Column index
        @return: TILE object at the specified position
        """
        return self[row, col]

    def set(self, row: int, col: int, value: Optional[TILE]) -> None:
        """
        @brief Set the tile at the specified position.
        @param row: Row index
        @param col: Column index
        @param value: TILE object to be set
        """
        self[row, col] = value

    def pop(self, row: int, col: int) -> Optional[TILE]:
        """
        @brief Pop the tile at the specified position.
        @param row: Row index
        @param col: Column index
        @return: TILE object at the specified position
        """
        value = self[row, col]
        self[row, col] = None
        return value

    def is_empty(self, row: int, col: int) -> bool:
        """
        @brief Check if the cell is empty
        @param row: Row index
        @param col: Column index
        @return: True if the cell is empty, False otherwise
        """
        try:
            if (self[row, col] is None):
                return True
            return False
        except IndexError:
            return False
        
    def has_locked_tile(self ,row: int, col: int) -> bool:
        """
        @brief Check if the cell has a locked tile
        @param row: Row index
        @param col: Column index
        @return: True if the cell has a locked tile, False otherwise
        """
        # If no tile is placed, return False
        if (self[row, col] is None):
            return False
        
        # If tile is placed and locked, return True
        if self.at(row, col).is_locked:
            return True
        return False

    def is_within_bounds(self, row: int, col: int) -> bool:
        """
        @brief Check if the given row and column are within the bounds of the board.
        @param row: Row index
        @param col: Column index
        @return: True if within bounds, False otherwise
        """
        if row < 0 or row > self.rows:
            return False
        if col < 0 or col > self.cols:
            return False
        return True

    def clear(self) -> None:
        """
        @brief Clear the board by filling it with None values.
        """
        self.fill(None)

    def serialize(self) -> Dict[str, LETTER]:
        """
        @brief Serialize the board to a dictionary representation.
        @return: Dictionary representation of the board
        """
        result = {}
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.is_empty(row,col):
                    result[str(CL(row, col))] = self.at(row, col).letter
        return result

class Board:
    """
    @brief Class to represent the board of the game.
    The board is represented as a 2D array of cells, where each cell can contain a tile.
    The board also contains premium cells that can affect the score of the words formed.
    """
    class Direction:
        Vertical = 0
        Horizontal = 1
        Undefined = 2

    def __init__(self,
                 dictionary: DictionaryWrapper,
                 row=BOARD_ROW,
                 col=BOARD_COL, 
                 premium_cells: Dict[CL, CT]=PREMIUM_CELLS):
        self.__dictionary: DictionaryWrapper = dictionary
        self.__row: int = row
        self.__col: int = col
        self.__cells = BoardContainer(self.__row, self.__col)  # [['' for _ in range(self.__col)] for _ in range(self.__row)]
        self.__premium_cells = copy.deepcopy(premium_cells)

        self._cross_checks: List[List[List[List[str]]]] = []
        self.best_score: int = 0
        self.best_moves: List[MOVE] = []

        self.is_debug_enabled = False
        self.debug_time_start_ns: int = 0
        self.debug_total_move_count: int = 0

        self.clear()

    @property
    def rows(self):
        return self.__cells.rows

    @property
    def cols(self):
        return self.__cells.cols

    @property
    def midrow(self) -> int:
        return self.__cells.midrow

    @property
    def midcol(self) -> int:
        return self.__cells.midcol

    def get_dictionary(self) -> DictionaryWrapper:
        """
        @brief Get the dictionary object
        @return: DictionaryWrapper object
        """
        return self.__dictionary

    def get_locked_tiles(self) -> List[TILE]:
        """
        @brief Get all locked tiles on the board.
        @return: List of locked TILE objects
        """
        return [tile for tile in self.__cells if isinstance(tile, TILE) and tile.is_locked]

    def at(self, row: int, col: int) -> Optional[TILE]:
        """
        @brief Get the tile at the specified position.
        @param row: Row index
        @param col: Column index
        @return: TILE object at the specified position
        """
        return self.__cells.at(row, col)

    def check_boundary(self, tile: TILE) -> bool:
        """
        @brief Check if the tile is within the board boundaries.
        @param tile: TILE object to be checked
        @return: True if the tile is within bounds, False otherwise
        """
        # Check if the row and column are within bounds of board
        if tile.row < 0 or tile.row >= self.__row:
            return False
        if tile.col < 0 or tile.col >= self.__col:
            return False
        return True

    def place_tile(self, tile: TILE) -> bool:
        """
        @brief Place a tile on the board.
        @param tile: TILE object to be placed
        @return: True if the tile was successfully placed, False otherwise
        """
        if self.__cells.is_empty(tile.row, tile.col):
            tile.is_blank = True if tile.letter == BLANK_LETTER else False
            tile.point = self.__dictionary.get_alphabet()[tile.letter][1]
            tile.point = 0 if tile.is_blank else tile.point
            tile.is_locked = True
            self.__cells.set(tile.row, tile.col, tile)
            return True
        else:
            # Cannot be placed since it is already occupied cell
            return False

    def place_word(self, word: WORD) -> bool:
        """
        @brief Place a word on the board.
        @param word: List of TILE objects representing the word
        @return: True if the word was successfully placed, False otherwise
        """
        if word is None or len(word) == 0:
            return False
        
        is_placed = True
        for tile in word:
            is_placed &= self.place_tile(tile)
        return is_placed

    def serialize_word(self, word: WORD) -> str:
        """
        @brief Serialize the word to a string representation.
        @param word: List of TILE objects representing the word
        @return: Serialized string representation of the word
        """
        for tile in word:
            if not self.check_boundary(tile): return ""
            if not self.__cells.is_empty(tile.row, tile.col): return ""

        rows: Dict[int, WORD] = {}
        cols: Dict[int, WORD] = {}
        
        for tile in word:
            rows.setdefault(tile.row, []).append(tile)
            cols.setdefault(tile.col, []).append(tile)

        # Helper function to complete words by filling missing blanks
        def complete_word(word: WORD, direction) -> WORD:
            new_word: WORD = []
            if direction == Board.Direction.Horizontal:
                row = word[0].row
                col_range = range(word[0].col, word[-1].col + 1)
                for col in col_range:
                    existing_tile = next((t for t in word if t.col == col), None)
                    if existing_tile is not None:
                        new_word.append(existing_tile)
                    elif not self.__cells.is_empty(row, col):  # Fill missing letters
                        new_word.append(TILE(row, col, self.__cells.at(row, col).letter))
                    else:
                        return []  # Incomplete word, return empty
            elif direction == Board.Direction.Vertical:
                col = word[0].col
                row_range = range(word[0].row, word[-1].row + 1)
                for row in row_range:
                    existing_tile = next((t for t in word if t.row == row), None)
                    if existing_tile is not None:
                        new_word.append(existing_tile)
                    elif not self.__cells.is_empty(row, col):  # Fill missing letters
                        new_word.append(TILE(row, col, self.__cells.at(row, col).letter))
                    else:
                        return []  # Incomplete word, return empty
            return new_word

        # Check horizontal word formation
        if len(cols.items()) == len(word) and len(rows.items()) == 1:
            for row, tiles in rows.items():
                sorted_tiles = sorted(tiles, key=lambda x: x.col)  # Sort by column
                completed_tiles = complete_word(sorted_tiles, Board.Direction.Horizontal)
                if completed_tiles and all(completed_tiles[i].col == completed_tiles[i - 1].col + 1 for i in range(1, len(completed_tiles))):
                    serialized_word = ''.join(tile.letter for tile in completed_tiles)
                    #print(f"Word in row {row}: {serialized_word}")
                    return serialized_word

        # Check vertical word formation
        if len(rows.items()) == len(word) and len(cols.items()) == 1:
            for col, tiles in cols.items():
                sorted_tiles = sorted(tiles, key=lambda x: x.row)  # Sort by row
                completed_tiles = complete_word(sorted_tiles, Board.Direction.Vertical)
                if completed_tiles and all(completed_tiles[i].row == completed_tiles[i - 1].row + 1 for i in range(1, len(completed_tiles))):
                    serialized_word = ''.join(tile.letter for tile in completed_tiles)
                    #print(f"Word in column {col}: {serialized_word}")
                    return serialized_word

        return ""

    def validate_word(self, word: WORD) -> Tuple[bool, str]:
        """
        @brief Validate the word if it is a valid word in the dictionary (used in unit tests)
        """
        serialized_word = self.serialize_word(word)
        if serialized_word == "": False, ""

        return self.__dictionary.has_word(serialized_word), serialized_word

    @staticmethod
    def get_bonus(ct: CT) -> Tuple[int, int]:
        """
        @brief Get the bonus points for the cell type
        @param ct: Cell type
        @return: Tuple of (letter multiplier, word multiplier)
        """
        if ct == CT.DOUBLE_LETTER:
            return (2, 1)
        elif ct == CT.TRIPLE_LETTER:
            return (3, 1)
        elif ct == CT.DOUBLE_WORD:
            return (1, 2)
        elif ct == CT.TRIPLE_WORD:
            return (1, 3)
        else:
            return (1, 1)

    def calculate_points(self, word: WORD, check_center=True) -> int:
        """
        @brief Calculate the points of the word
        """
        if check_center:
            # Check any tile placed on center cell. 
            # If it is not, the word should be placed on the center
            is_center_empty = True if self.__cells.is_empty(self.midrow, self.midcol) else False
            
            # Check whether the word is placed on a valid cell
            is_word_in_center = False
            for tile in word:
                if not self.check_boundary(tile): return 0
                #if not self.__cells.is_empty(tile.row, tile.col): return 0
                if tile.row == self.midrow and tile.col == self.midcol: is_word_in_center = True

            # If the center cell is empty and the word should be placed on the center
            if is_center_empty and not is_word_in_center:
                return 0  # The first word should be placed on the center

        direction = self.find_word_direction(word)

        if (direction == Board.Direction.Horizontal):
            sorted_ = sorted(word, key=lambda x: x.col, reverse=False)

            o_words: List[Dict[str, int]] = []
            completed_word = self.complete_word(sorted_[0].row, sorted_[0].col, 0, 1, sorted_)

            score = self.score_play(completed_word[-1].row, completed_word[-1].col, 0, 1, completed_word, o_words)
            #print(f"Horizontal Score: {score} words : {o_words}")
            # Check all founded words are valid
            flag = True
            for t_word in o_words:
                flag &= self.__dictionary.has_word(t_word['word'])

            return score if flag else 0
        elif (direction == Board.Direction.Vertical):
            sorted_ = sorted(word, key=lambda x: x.row, reverse=False)

            o_words: List[Dict[str, int]] = []
            completed_word = self.complete_word(sorted_[0].row, sorted_[0].col, 1, 0, sorted_)
            score = self.score_play(completed_word[-1].row, completed_word[-1].col, 1, 0, completed_word, o_words)
            #print(f"Vertical Score: {score} words : {o_words}")
            # Check all founded words are valid
            flag = True
            for t_word in o_words:
                flag &= self.__dictionary.has_word(t_word['word'])

            return score if flag else 0
        else:  # Undefined direction
            return 0

    def clear(self) -> None:
        """
        @brief Clear the board
        """
        self.__cells.clear()

    def serialize(self) -> Dict[str, LETTER]:
        """
        @brief Serialize the board to a dictionary representation.
        @return: Dictionary representation of the board
        """
        return self.__cells.serialize()

    def stringify(self) -> str:
        """
        @brief Convert the board to a string representation for debugging.
        @return: String representation of the board
        """
        output = ""
        # Get the number of rows and columns
        rows = self.__cells.rows
        cols = self.__cells.cols
        
        # Generate column headers (A, B, C, ...)
        column_headers = string.ascii_uppercase[:cols]
        
        # Create a 2D grid representation of the board
        board = [["." for _ in range(cols)] for _ in range(rows)]
        
        # Populate the board with the current letters
        for r in range(rows):
            for c in range(cols):
                if not self.__cells.is_empty(r, c):
                    # If the cell is not empty, get the letter and place it on the board
                    board[r][c] = self.__cells.at(r, c).letter
        
        # Print the column headers
        output += "     " + "  ".join(column_headers) + "\n"

        # Print the top border
        output += "   +-" + "---" * cols + "+" + "\n"
        
        # Print the board with row numbering
        for r in range(rows):
            # Print the row number (aligned with two spaces for better formatting)
            output += f"{r+1:2} |" + " "
            
            # Print the row contents
            for c in range(cols):
                output += f"{board[r][c]} " + " "
            
            # Print the right border
            output += "|" + "\n"

        # Print the bottom border
        output += "   +-" + "---" * cols + "+" + "\n"

        return output

    def deserialize(self, serialized_board: str) -> None:
        """
        @brief Deserialize the board from a string representation.
        @param serialized_board: String representation of the board
        """
        alphabet = self.__dictionary.get_alphabet()
        # Split the board into lines
        lines = serialized_board.split("\n")

        # Extract only the board rows (ignoring the first two and last lines)
        r = 0
        for line in lines[2:-1]:  # Ignore headers and the border
            if not (line.split("|").__len__() == 3): continue
            
            row_content = line.split("|")[1].strip()
            row_tiles = row_content.split("  ")  # Split into individual tiles
            for c, l in enumerate(row_tiles):
                l = l.strip()
                if l == ".": continue
                is_blank = True if l == "_" else False
                l = BLANK_LETTER if l == "_" else l

                tile = TILE(r, c, l, alphabet[l][1], is_blank)
                self.place_tile(tile)
            r += 1

    def print(self, tentative_tiles: List[TILE]=[]) -> None:
        """
        @brief Print the board with the given tentative tiles.
        @param tentative_tiles: List of tiles to be placed on the board
        """
        modified_cells: List[Tuple[int, int]] = []

        # Try to place all tiles if cell is empty
        for tentative_tile in tentative_tiles:
            if self.__cells.is_empty(tentative_tile.row, tentative_tile.col):
                self.__cells.set(tentative_tile.row, tentative_tile.col, tentative_tile)
                modified_cells.append((tentative_tile.row, tentative_tile.col))

        print(self.stringify())

        # Clean up tile that was placed before
        for (r, c) in modified_cells:
            modified_cell = self.__cells.pop(r, c)
            modified_cell.is_locked = False

    def enable_debug(self) -> None:
        """
        @brief Enable debug mode
        """
        self.is_debug_enabled = True

    def print_statistics(self) -> None:
        """
        @brief Print debug statistics
        """
        print(f"Total valid words: {self.debug_total_move_count}")
        print(f"Total optimal words: {len(self.best_moves)}")
        print(f"Total duration (ms): {(time.perf_counter_ns()-self.debug_time_start_ns)/1000000}")

    def score_play(self, row: int, col: int, drow: int, dcol: int, tiles: List[TILE], words: Optional[List[Dict[str, int]]] = None) -> int:
        """
        @brief Given a play at col, row, compute it's score. Used in
        findBestPlay, and must perform as well as possible.
        Note: does *not* include any bonuses due to number of tiles played.
        
        @param row: the row of the LAST letter
        @param col: the col of the LAST letter
        @param drow: 1 if the word is being played down
        @param dcol: 1 if the word being played across
        @param tiles: a list of tiles that are being placed
        @param words: optional list to be populated with words that have been created by the play
        @return: the score of the play.
        """
        word_score = 0
        cross_words_score = 0
        word_multiplier = 1
        alphabet: ALPHABET = self.__dictionary.get_alphabet()

        # One behind first tile offset
        c = col - dcol * len(tiles)
        r = row - drow * len(tiles)

        for tile in tiles:
            r += drow
            c += dcol
            cell_type = self.__premium_cells.get(CL(r, c), CT.ORDINARY)
            lm, wm = Board.get_bonus(cell_type)
            tile_score = alphabet[tile.letter][1] if tile.point <0 else tile.point

            if not self.__cells.is_empty(r, c):
                word_score += tile_score
                continue  
            
            letter_score = tile_score * lm
            word_score += letter_score
            word_multiplier *= wm

            cross_word = ""
            cross_word_score = 0

            # Look left/up
            cp = c - drow
            rp = r - dcol
            while cp >= 0 and rp >= 0 and not self.__cells.is_empty(rp, cp):
                cross_letter = self.__cells.at(rp, cp).letter
                cross_word = cross_letter + cross_word
                cross_word_score += alphabet[cross_letter][1]  # Add score of cross tile
                cp -= drow
                rp -= dcol

            cross_word += tile.letter

            # Look right/down
            cp = c + drow
            rp = r + dcol
            while cp < self.__cells.cols and rp < self.__cells.rows and not self.__cells.is_empty(rp, cp):
                cross_letter = self.__cells.at(rp, cp).letter
                cross_word += cross_letter
                cross_word_score += alphabet[cross_letter][1]  # Add score of cross tile
                cp += drow
                rp += dcol

            if cross_word_score > 0:
                # This tile (and bonuses) contribute to cross words
                cross_word_score += letter_score
                cross_word_score *= wm
                if words is not None:
                    words.append({"word": cross_word, "score": cross_word_score})
                cross_words_score += cross_word_score

        word_score *= word_multiplier

        if words is not None:
            words.append({"word": "".join(tile.letter for tile in tiles), "score": word_score})

        return word_score + cross_words_score

    @staticmethod
    def intersection(a: List[str], b: List[str]) -> List[str]:
        """
        @brief Find the intersection of two lists
        @param a: First list
        @param b: Second list
        @return: List of common elements
        """
        return [letter for letter in a if letter in b]

    def is_anchor(self, row: int, col: int) -> bool:
        """
        @brief Check if the cell is an anchor point for a word.
        
        Unlike Appel and Jacobsen, who anchor plays on empty squares,
        we anchor plays on a square with a tile that has an adjacent
        (horizontal or vertical) non-empty square.

        @param row: Row index
        @param col: Column index
        @return: True if the cell is an anchor point, False otherwise
        """
        if not self.__cells.is_empty(row, col):
            return ((col > 0 and self.__cells.is_empty(row, col-1)) or
                    (col < self.__cells.cols - 1 and self.__cells.is_empty(row, col+1)) or
                    (row > 0 and self.__cells.is_empty(row-1, col)) or
                    (row < self.__cells.rows - 1 and self.__cells.is_empty(row+1, col)))
        return False

    def is_empty(self, row: int, col: int) -> bool:
        """
        @brief Check if the cell is empty
        @param row: Row index
        @param col: Column index
        @return: True if the cell is empty, False otherwise
        """
        return self.__cells.is_empty(row, col)

    def find_word_direction(self, word: WORD) -> Direction:
        """
        @brief Find the direction of the word (horizontal or vertical)
        @param word: List of TILE objects representing the word
        @return: Direction of the word (horizontal or vertical)
        """
        rows: Dict[int, WORD] = {}
        cols: Dict[int, WORD] = {}

        # Add tiles according to their row and indexes
        for tile in word:
            rows.setdefault(tile.row, []).append(tile)
            cols.setdefault(tile.col, []).append(tile)

        # If length of the word is 1, then we need to look its around to understand its direction
        if len(word) == 1:
            # Look upwards
            if not self.__cells.is_empty(word[0].row+1, word[0].col):
                return Board.Direction.Vertical

            # Look downwards
            if not self.__cells.is_empty(word[0].row-1, word[0].col):
                return Board.Direction.Vertical

            # Look left
            if not self.__cells.is_empty(word[0].row, word[0].col-1):
                return Board.Direction.Horizontal

            # Look right
            if not self.__cells.is_empty(word[0].row, word[0].col+1):
                return Board.Direction.Horizontal

        if len(cols.items()) == len(word) and len(rows.items()) == 1:
            return Board.Direction.Horizontal

        if len(rows.items()) == len(word) and len(cols.items()) == 1:
            return Board.Direction.Vertical

        return Board.Direction.Undefined

    def complete_word(self, row: int, col: int, drow: int, dcol: int, word: WORD) -> WORD:
        """
        @brief Completes a word by finding missing letters from the board.

        @param row: the row of the LAST letter
        @param col: the col of the LAST letter
        @param drow: 1 if the word is being played down
        @param dcol: 1 if the word being played across
        @param word: List of TILE objects representing the known word part.
        @return: Completed list of TILE objects forming the full word.
        """
        frow = row-drow  # Move left of the first letter
        fcol = col-dcol  # Move up of the first letter

        completed_word: List[TILE] = copy.deepcopy(word)

        # Move left or up, to find index of first letter in the word
        while(frow>=0 and fcol>=0):
            if self.__cells.is_empty(frow, fcol):
                frow += drow
                fcol += dcol
                break

            completed_word.insert(0, TILE(frow, fcol, self.__cells.at(frow, fcol).letter))
            frow -= drow
            fcol -= dcol

        if drow==1:  # Vertical word
            completed_word = sorted(completed_word, key=lambda x: x.col, reverse=True)
        else:  # Horizontal word
            completed_word = sorted(completed_word, key=lambda x: x.row, reverse=True)

        i = 0  # index to insert new letters 
        while (frow < self.__cells.rows and fcol < self.__cells.cols):
            if (i >= len(completed_word)):
                tile = self.__cells.at(frow, fcol)
                if tile is None:
                    return completed_word
                completed_word.insert(i, tile)
            else:
                if not(completed_word[i].row == frow and completed_word[i].col == fcol):
                    tile = self.__cells.at(frow, fcol)
                    if tile is None:
                        return completed_word
                    completed_word.insert(i, tile)
                i += 1
            
            frow += drow
            fcol += dcol

        return completed_word

    def calculate_bonus(self, tilesPlaced: int) -> int:
        """
        @brief Calculate the bonus points for the number of tiles placed.

        Not implemented yet.

        @param tilesPlaced: Number of tiles placed
        @return: Bonus points
        """
        return 0

    def find_nearest_premium(self, row: int, col: int) -> Tuple[int, CT]:
        """
        @brief Calculate the Manhattan distance to the nearest premium cell.
        @param row: Row index of the cell.
        @param col: Column index of the cell.
        @return: Tuple of (distance, cell type) to the nearest premium cell.
        """
        min_distance = -1
        nearest_premium = None
        
        for cl, ct in PREMIUM_CELLS.items():
            distance = abs(row - cl.row) + abs(col - cl.col)
            
            if distance < min_distance:
                min_distance = distance
                nearest_premium = ct
                
        return (min_distance, nearest_premium) if min_distance >= 0 else (None, None)

    def _compute_cross_checks(self, available: List[LETTER]) -> None:
        """
        @brief Determine which letters can fit in each square and form a valid
        horizontal or vertical cross word.
        @param available: set of available letters
        """
        x_checks: List[List[List[List[str]]]] = []

        for col in range(self.cols):
            this_col = []
            x_checks.append(this_col)

            for row in range(self.rows):
                this_cell = [[], []]
                this_col.append(this_cell)
                
                if not self.__cells.is_empty(row, col):
                    this_cell[0].append(self.at(row, col).letter)
                    this_cell[1].append(self.at(row, col).letter)
                    continue

                # Find the words above and below
                word_above = ""
                r = row - 1
                while r >= 0 and not self.__cells.is_empty(r, col):
                    word_above = self.at(r, col).letter + word_above
                    r -= 1

                word_below = ""
                r = row + 1
                while r < self.rows and not self.__cells.is_empty(r, col):
                    word_below += self.at(r, col).letter
                    r += 1

                # Find the words left and right
                word_left = ""
                c = col - 1
                while c >= 0 and not self.__cells.is_empty(row, c):
                    word_left = self.at(row, c).letter + word_left
                    c -= 1

                word_right = ""
                c = col + 1
                while c < self.cols and not self.__cells.is_empty(row, c):
                    word_right += self.at(row, c).letter
                    c += 1

                # Find which letters form a valid cross word
                for letter in available:
                    h = word_left + letter + word_right
                    h_is_word = len(h) == 1 or self.__dictionary.has_word(h)
                    h_is_seq = h_is_word or col > 0 and self.__dictionary.has_sequence(h)

                    v = word_above + letter + word_below
                    v_is_word = len(v) == 1 or self.__dictionary.has_word(v)
                    v_is_seq = v_is_word or row > 0 and self.__dictionary.has_sequence(v)

                    if h_is_word and v_is_seq:
                        this_cell[0].append(letter)
                    if v_is_word and h_is_seq:
                        this_cell[1].append(letter)

        self._cross_checks = x_checks[:]

    def _forward(self, row: int, col: int, 
                drow: int, dcol: int, 
                rack_tiles: List[TILE], tiles_played: int, 
                d_node: LetterNode, word_so_far: List[TILE]) -> None:
        """
        @brief Recursively extend a word on the board by adding valid letters from the rack or existing tiles.
        @param row: Current row position on the board.
        @param col: Current column position on the board.
        @param drow: Direction of movement in rows (1 for down, 0 for across).
        @param dcol: Direction of movement in columns (1 for across, 0 for down).
        @param rack_tiles: Tiles remaining on the rack.
        @param tiles_played: Number of tiles played so far.
        @param current_node: Current node in the dictionary trie.
        @param word_so_far: Letters of the word formed so far.
        """
        # Square we're hopefully extending into
        erow = row + drow
        ecol = col + dcol

        # Tail recursion
        if (d_node.isEndOfWord and len(word_so_far) >= 2 and tiles_played > 0 and
            (ecol == self.cols or erow == self.rows or self.__cells.is_empty(erow, ecol))):
            words = []

            score = self.score_play(row, col, drow, dcol, word_so_far, words)

            if self.is_debug_enabled and score > 0: self.debug_total_move_count += 1

            if score > self.best_score:
                # This is best score so far
                self.best_score = score
                heapq.heappush(self.best_moves, MOVE(score, word_so_far[:]))

                #self.print(word_so_far)
                #
                #print("*************")
                #print("score:", score)
                #print("word_so_far:", word_so_far)
                #print("*************")
        
        available = []  # List of letters that can be extended with
        played_tile = 0
        
        if ecol < self.cols and erow < self.rows:
            if self.__cells.is_empty(erow, ecol):
                have_blank = any(t.is_blank for t in rack_tiles)
                xc = self._cross_checks[ecol][erow][dcol]

                available = Board.intersection(d_node.postLetters,
                                               xc if have_blank else Board.intersection([t.letter for t in rack_tiles], xc))
                played_tile = 1
            else:
                available = [self.at(erow, ecol).letter]
        else :
            pass

        for letter in available:
            shrunk_rack = rack_tiles[:]
            
            if played_tile > 0:
                rack_tile = next((tile for tile in shrunk_rack if tile.letter == letter), 
                                next((tile for tile in shrunk_rack if tile.is_blank), None))

                word_so_far.append(TILE(erow, ecol, letter, rack_tile.point, rack_tile.is_blank))
                shrunk_rack = [t for t in shrunk_rack if t != rack_tile]
            else:
                word_so_far.append(self.at(erow, ecol))
            
            for post in d_node.postNodes:
                if post.letter == letter:
                    self._forward(erow, ecol, 
                                 drow, dcol, 
                                 shrunk_rack, tiles_played + played_tile, 
                                 post, word_so_far)
            
            word_so_far.pop()

    def _back(self, row: int, col: 
             int, drow: int, dcol: int, 
             rack_tiles: List[TILE], tiles_played: int, anchor_node: LetterNode, 
             d_node: LetterNode, word_so_far: List[TILE]):
        """
        @brief Try to back up before extending the word in the given direction.
        @param col: Column index of the last letter in the word so far
        @param row: Row index of the last letter in the word so far
        @param dcol: Direction indicator for horizontal movement
        @param drow: Direction indicator for vertical movement
        @param rack_tiles: List of available tiles from the player's rack
        @param tiles_played: Number of tiles used from the rack
        @param anchor_node: Starting dictionary node for backing up
        @param d_node: Current dictionary node
        @param word_so_far: List of tiles forming the current word in reverse order
        """
        # Square we're hopefully extending into
        erow = row - drow
        ecol = col - dcol

        available = []  # Set of possible candidate letters
        played_tile = 0

        # Check if we have an adjacent empty cell to back up into
        if ecol >= 0 and erow >= 0:
            if self.__cells.is_empty(erow, ecol):
                # Find common letters between rack, cross-checks, and dictionary node prefixes
                have_blank = any(tile.is_blank for tile in rack_tiles)
                xc = self._cross_checks[ecol][erow][dcol]

                available = Board.intersection(d_node.preLetters,
                                               xc if have_blank else Board.intersection([t.letter for t in rack_tiles], xc))               
                played_tile = 1
            else:
                # Non-empty square, use its letter
                available = [self.at(erow, ecol).letter]
        
        # Head recursion to explore longer words first
        for letter in available:
            shrunk_rack = rack_tiles[:]
            if played_tile > 0:
                # Letter came from the rack
                tile = next((t for t in shrunk_rack if t.letter == letter), None) or next((t for t in shrunk_rack if t.is_blank), None)

                #FIXME tile = next((t for t in shrunk_rack if t.letter == letter), 
                #            next((t for t in shrunk_rack if t.is_blank), None))

                # Placement is not used in score calculation
                word_so_far.insert(0, TILE(erow, ecol, letter, tile.point, tile.is_blank))
                shrunk_rack = [t for t in shrunk_rack if t.is_similar(tile)]
            else:
                # Letter already on the self
                word_so_far.insert(0, self.at(erow, ecol))

            for pre in d_node.preNodes:
                if pre.letter == letter:
                    self._back(erow, ecol, 
                              drow, dcol, 
                              shrunk_rack, tiles_played + played_tile, anchor_node, 
                              pre, word_so_far)
            
            word_so_far.pop(0)

        # If this is the start of a valid word and we're at the board edge or an empty cell
        #FIXME if not d_node.preNodes and (erow < 0 or ecol < 0 or self.__cells.is_empty(erow, ecol)):
        if len(d_node.preNodes) == 0 and (erow < 0 or ecol < 0 or self.__cells.is_empty(erow, ecol)):
            self._forward(row + drow * (len(word_so_far) - 1),
                         col + dcol * (len(word_so_far) - 1),
                         drow, dcol,
                         rack_tiles, tiles_played,
                         anchor_node, word_so_far)
    
    def best_opening_play(self, rack_tiles: List[TILE]) -> Tuple[int, WORD]:
        """
        @brief Find the best opening play for the given rack tiles.
        @param rack_tiles: List of available tiles from the player's rack
        @return: Tuple of (best score, best word).
        """
        ruck = "".join(t.letter if t.letter else " " for t in rack_tiles)

        choices = self.__dictionary.find_anagrams(ruck)
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
            
            mid = self.midcol if vertical else self.midrow
            for end in range(mid, mid + len(choice)):
                row, col = (mid, end) if vertical else (end, mid)
                score = self.score_play(row, col, drow, dcol, placements)
                score += self.calculate_bonus(len(placements))
                
                if score > best_score:
                    best_score = score
                    for i, placement in enumerate(placements):
                        pos = end - len(placements) + i + 1
                        placement.col = self.midcol if dcol == 0 else pos * dcol
                        placement.row = self.midrow if drow == 0 else pos * drow
                    
                    TILE.print_word(best_word)

                    best_word = placements
                    
                    #TODO report the placement
                    #report({"placements": placements, "word": choice, "score": score})
        
        return (best_score, best_word)

    def get_best_moves(self) -> List[MOVE]:
        """
        @brief Get the best moves found during the search.
        @return: List of best moves
        """
        return self.best_moves
    
    def get_possible_moves(self, rack_tiles: List[TILE]) -> List[MOVE]:
        """
        @brief Get all possible moves for the given rack tiles.
        @param rack_tiles: List of available tiles from the player's rack
        @return: List of possible moves.
        """
        if self.is_debug_enabled:
            self.debug_total_move_count = 0
            self.debug_time_start_ns = time.perf_counter_ns()

        self.best_moves.clear()
        self.best_score = 0
        self._cross_checks.clear()

        # Sort the rack tiles by point value and then by letter
        rack_tiles = sorted(rack_tiles, key=lambda t: (-t.point, t.letter))

        best_score = 0
        best_word: WORD = []
        anchored = False
                
        # Has at least one anchor been explored? If there are no anchors, we need to compute an opening play
        anchored = False

        for col in range(self.cols):
            for row in range(self.rows):
                # An anchor is any square that has a tile and has an
                # adjacent blank that can be extended into to form a word
                if self.is_anchor(row, col):
                    if not anchored:
                        # What letters can be used to form a valid cross word? 
                        # The whole alphabet if the rack contains a blank, the rack otherwise.
                        available = self.__dictionary.get_all_letters() if any(t.is_blank for t in rack_tiles) else [t.letter for t in rack_tiles]
                        self._compute_cross_checks(available)
                        anchored = True

                    anchor_tile = self.at(row, col)

                    roots = self.__dictionary.get_sequence_roots(anchor_tile.letter)
                    for anchor_node in roots:
                        # Try and back up then forward through the dictionary to find longer sequences across
                        self._back(row, col, 0, 1,
                                         rack_tiles, 0,
                                         anchor_node, anchor_node,
                                         [ anchor_tile ])

                        # down
                        self._back(row, col, 1, 0,
                                         rack_tiles, 0,
                                         anchor_node, anchor_node,
                                         [ anchor_tile ])

        if not anchored:
            best_score, best_word = self.best_opening_play(rack_tiles)
            if self.is_debug_enabled: self.print_statistics()
            return [ MOVE(best_score, best_word) ]
        else:
            best_moves = self.get_best_moves()
            if self.is_debug_enabled: self.print_statistics()
            return best_moves
