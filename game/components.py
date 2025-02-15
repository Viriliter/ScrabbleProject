import os
import random
import copy
from io import BytesIO
from typing import List, Dict, Tuple

from .globals import *
from .utils import *
from externals.dictionary import Dictionary

class TileBag:
    def __init__(self):
        self.__reference_tiles: ALPHABET = {}
        self.__tiles: ALPHABET = {}
        self.__remaning_tiles: int = 0
        self.__picked_letters: List[LETTER] = []

    def clear(self) -> None:
        self.__reference_tiles = {}
        self.__tiles = {}
        self.__remaning_tiles = 0
        self.__picked_letters = []

    def load(self, alphabet: ALPHABET) -> None:
        self.clear()

        self.__reference_tiles = alphabet
        for letter, (count, points) in alphabet.items():
            if letter in self.__tiles:
                self.__tiles[letter] = (self.__tiles[letter][0] + count, points)
            else:
                self.__tiles[letter] = (count, points)
            self.__remaning_tiles += count

    def get_random_letter(self) -> LETTER:
        if self.__remaning_tiles == 0:
            return None  # Bag is empty
        
        # Randomly pick a letter
        letter = random.choice(list(self.__tiles.keys()))
        count, points = self.__tiles[letter]
        
        # Decrease the count of the letter in the bag
        if count > 1:
            self.__tiles[letter] = (count - 1, points)
        else:
            del self.__tiles[letter]  # Remove letter if no more left
        
        self.__remaning_tiles -= 1
        return letter

    def put_back_letter(self, letter: LETTER) -> None:
        if letter in self.__tiles:
            count, points = self.__tiles[letter]
            self.__tiles[letter] = (count + 1, points)
        else:
            self.__tiles[letter] = (1, self.__reference_tiles[letter][1])
        self.__remaning_tiles += 1

    def get_remaining_tiles(self) -> int:
        return self.__remaning_tiles

    def pick_letter_for_order(self) -> LETTER:
        available_letters = set(self.__tiles.keys()) - set(self.__picked_letters)
        if not available_letters:
            raise ValueError("No available letters left to pick.")
    
        letter = random.choice(list(available_letters))
        self.__picked_letters.append(letter)
        return letter

class Rack:
    def __init__(self):
        self.__container: List[LETTER] = []
        
    def add_to_rack(self, letter: LETTER) -> None:
        self.__container.append(letter)

    def remove_from_rack(self, letter: LETTER) -> None:
        self.__container.remove(letter)

    def get_rack_length(self) -> int:
        return self.__container.__len__()

    def serialize(self) -> Dict[LETTER, int]:
        letter_counts = {}
        for letter in self.__container:
            if letter in letter_counts:
                letter_counts[letter] += 1
            else:
                letter_counts[letter] = 1
        return letter_counts

    def clear(self) -> None:
        self.__container.clear()

    def count(self) -> int:
        return self.__container.__len__()

class DictionaryWrapper:
    def __init__(self, language: LANGUAGE):
        self.__alphabet: ALPHABET = language.alphabet.copy()
        self.__uri: str = get_absolute_path(language.uri)

        self.__dic = Dictionary("myDictionary")

        with open(os.path.join(os.path.dirname(__file__), 'data', self.__uri), 'rb') as f:
            data = f.read()
        self.__dic.load_dawg(BytesIO(data))

    def validate_word(self, word: str) -> bool:
        return False if len(word)==0 else self.__dic.has_word(word)

    def calculate_points(self, word: str) -> int:
        word_points = 0
        for letter in word:
            word_points += self.__alphabet[letter][1]
        return word_points

    def get_word_points(self, word: str) -> int:
        return self.calculate_points(word)
    
    def get_alphabet(self) -> ALPHABET:
        return self.__alphabet

class Board:
    def __init__(self,
                 dictionary: DictionaryWrapper,
                 row=BOARD_ROW,
                 col=BOARD_COL, 
                 special_cells: Dict[CL, CT]=SPECIAL_CELLS):
        self.__dictionary = dictionary
        self.__row: int = row
        self.__col: int = col
        self.__cells = [['' for _ in range(self.__col)] for _ in range(self.__row)]
        self.__special_cells = copy.deepcopy(special_cells)

        self.clear()

    def check_boundary(self, tile: TILE) -> bool:
        # Check if the row and column are within bounds of board
        if tile.row < 0 or tile.row >= self.__row:
            return False
        if tile.col < 0 or tile.col >= self.__col:
            return False
        return True

    def is_placable(self, tile: TILE) -> bool:
        if (self.__cells[tile.row][tile.col] == ''):
            return True
        else:
            return False

    def place_tile(self, tile: TILE) -> bool:
        if self.is_placable(tile):
            self.__cells[tile.row][tile.col] = tile.letter
            return True
        else:
            # Cannot be placed since it is already occupied cell
            return False

    def place_word(self, word: WORD) -> bool:
        is_placed = True
        for tile in word:
            is_placed &= self.place_tile(tile)
        return is_placed

    def serialize_word(self, word: WORD) -> str:
        for tile in word:
            if not self.check_boundary(tile): return ""
            if not self.is_placable(tile): return ""

        rows: Dict[int, WORD] = {}
        cols: Dict[int, WORD] = {}
        
        for tile in word:
            rows.setdefault(tile.row, []).append(tile)
            cols.setdefault(tile.col, []).append(tile)

        class Direction:
            Vertical = 0
            Horizontal = 1

        # Helper function to complete words by filling missing blanks
        def complete_word(word: WORD, direction) -> WORD:
            new_word: WORD = []
            if direction == Direction.Horizontal:
                row = word[0].row
                col_range = range(word[0].col, word[-1].col + 1)
                for col in col_range:
                    existing_tile = next((t for t in word if t.col == col), None)
                    if existing_tile:
                        new_word.append(existing_tile)
                    elif self.__cells[row][col]:  # Fill missing letters
                        new_word.append(TILE(row, col, self.__cells[row][col]))
                    else:
                        return []  # Incomplete word, return empty
            elif direction == Direction.Vertical:
                col = word[0].col
                row_range = range(word[0].row, word[-1].row + 1)
                for row in row_range:
                    existing_tile = next((t for t in word if t.row == row), None)
                    if existing_tile:
                        new_word.append(existing_tile)
                    elif self.__cells[row][col]:  # Fill missing letters
                        new_word.append(TILE(row, col, self.__cells[row][col]))
                    else:
                        return []  # Incomplete word, return empty
            return new_word

        # Check horizontal word formation
        if not len(rows.items()) == len(word):
            for row, tiles in rows.items():
                sorted_tiles = sorted(tiles, key=lambda x: x.col)
                completed_tiles = complete_word(sorted_tiles, Direction.Horizontal)
                if completed_tiles and all(completed_tiles[i].col == completed_tiles[i - 1].col + 1 for i in range(1, len(completed_tiles))):
                    serialized_word = ''.join(tile.letter for tile in completed_tiles)
                    print(f"Word in row {row}: {serialized_word}")
                    return serialized_word

        # Check vertical word formation
        if not len(cols.items()) == len(word):
            for col, tiles in cols.items():
                sorted_tiles = sorted(tiles, key=lambda x: x.row)
                completed_tiles = complete_word(sorted_tiles, Direction.Vertical)
                if completed_tiles and all(completed_tiles[i].row == completed_tiles[i - 1].row + 1 for i in range(1, len(completed_tiles))):
                    serialized_word = ''.join(tile.letter for tile in completed_tiles)
                    print(f"Word in column {col}: {serialized_word}")
                    return serialized_word

        return ""

    def validate_word(self, word: WORD) -> Tuple[bool, str]:
        serialized_word = self.serialize_word(word)
        if serialized_word == "": False, ""

        return self.__dictionary.validate_word(serialized_word), serialized_word

    def calculate_points(self, word: WORD, is_branched: bool=False) -> int:
        is_valid, s_word = self.validate_word(word)

        total_points = 0
        branched_words = set()

        if not is_valid and len(s_word) < 2:
            return total_points
        
        alphabet = self.__dictionary.get_alphabet()

        word_multiplier = 1
        word_points = 0
        for tile in word:

            # Add the letter points
            _, letter_points = alphabet.get(tile.letter, (None, 0))

            # Check if the current cell has special multiplier
            if not is_branched:
                cell_type = self.__special_cells.get(CL(tile.row, tile.col), CT.ORDINARY)
                if cell_type == CT.DOUBLE_LETTER:
                    word_points += letter_points * 2
                elif cell_type == CT.TRIPLE_LETTER:
                    word_points += letter_points * 3
                elif cell_type == CT.DOUBLE_WORD:
                    word_points += letter_points
                    word_multiplier *= 2
                elif cell_type == CT.TRIPLE_WORD:
                    word_points += letter_points
                    word_multiplier *= 3
                else:
                    word_points += letter_points
        
        total_points =  word_points * word_multiplier

        if (is_branched): return total_points

        # Account for new words formed in either direction (if they exist)
        # Check horizontal new words formed vertically and vice versa
        # For simplicity, here we assume new words forming as valid ones.
        for branched_word in branched_words:
            total_points += self.calculate_points(branched_word, True)  # Assume calculate_word_points exists

        return total_points

        return 0

    def clear(self) -> None:
        self.__cells = [['' for _ in range(self.__col)] for _ in range(self.__row)]

    def serialize(self) -> Dict[str, LETTER]:
        result = {}
        for row in range(self.__row):
            for col in range(self.__col):
                if self.__cells[row][col] != '':
                    result[str(CL(row, col))] = self.__cells[row][col]
        return result
