from typing import List, Dict, Tuple
import random

from .globals import *

class TileBag:
    def __init__(self):
        self.__reference_tiles: Dict[chr, Tuple[int, int]] = {}
        self.__tiles: Dict[chr, Tuple[int, int]] = {}
        self.__remaning_tiles: int = 0
        self.__picked_letters: List[chr] = []

    def load(self, tiles: Dict[chr, int]) -> None:
        self.__reference_tiles = tiles
        for letter, (count, points) in tiles.items():
            if letter in self.__tiles:
                self.__tiles[letter] = (self.__tiles[letter][0] + count, points)
            else:
                self.__tiles[letter] = (count, points)
            self.__remaning_tiles += count

    def get_random_letter(self) -> chr:
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

    def put_back_letter(self, letter: chr) -> None:
        if letter in self.__tiles:
            count, points = self.__tiles[letter]
            self.__tiles[letter] = (count + 1, points)
        else:
            self.__tiles[letter] = (1, self.__reference_tiles[letter][1])
        self.__remaning_tiles += 1

    def get_remaining_tiles(self) -> int:
        return self.__remaning_tiles

    def pick_letter_for_order(self) -> chr:
        available_letters = set(self.__tiles.keys()) - set(self.__picked_letters)
        if not available_letters:
            raise ValueError("No available letters left to pick.")
    
        letter = random.choice(list(available_letters))
        self.__picked_letters.append(letter)
        return letter

class Rack:
    def __init__(self):
        self.__container: List[chr] = []
        
    def add_to_rack(self, letter: chr) -> None:
        self.__container.append(letter)

    def remove_from_rack(self, letter: chr) -> None:
        self.__container.remove(letter)

    def get_rack_length(self) -> int:
        return self.__container.__len__()

    def get_letters(self) -> List[chr]:
        return self.__container.copy()

    def serialize(self) -> Dict[str, int]:
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

class Dictionary:
    __tiles: Dict[str, int] = {}

    def __init__(self, tiles: Dict[str, int]):
        Dictionary.__tiles = tiles.copy()

    @staticmethod
    def validate_word(word: str) -> bool:
        return False

    @staticmethod
    def calculate_points(word: str) -> int:
        word_points = 0
        for letter in word:
            word_points += Dictionary.__tiles[letter][1]
        return word_points

    @staticmethod
    def get_word_points(word: str) -> int:
        return Dictionary.calculate_points(word)

class Board:
    def __init__(self,
                 row=BOARD_ROW,
                 col=BOARD_COL, 
                 tiles: ALPHABET=ALPH_ENGLISH,
                 special_cells: Dict[CL, CT]=SPECIAL_CELLS):
        self.__row: int = row
        self.__col: int = col
        self.__cells: List[chr] = []
        self.__special_cells = special_cells.copy()
        self.__tiles = tiles.copy()

        #Dictionary(ALPH_ENGLISH)

        self.clear()

    def is_placable(self, letter: LETTER) -> bool:
        if not (self.__cells[letter.row][letter.col] == ''):
            return True
        else:
            return False

    def place_tile(self, letter: LETTER) -> bool:
        if self.is_placable(letter):
            self.__cells[letter.row][letter.col] == letter.letter
            return True
        else:
            # Cannot be placed to already occupied cell
            return False

    def place_word(self, word: WORD) -> bool:
        is_placed = True
        for letter in word:
            is_placed &= self.place_tile(letter)
        return is_placed

    def calculate_points(self, word: WORD) -> int:
        for letter in word:
            if not self.is_placable(letter): return 0

        return 0

    def clear(self) -> None:
        self.__cells = [['' for _ in range(self.__col)] for _ in range(self.__row)]

    def serialize(self) -> Dict[Tuple[int, int], chr]:
        board_state = {}
        for row in range(self.__row):
            for col in range(self.__col):
                if self.__cells[row][col] != '':
                    board_state[(row, col)] = self.__cells[row][col]
        return board_state

    @staticmethod
    def sort_letters(letters: List[Tuple[chr, str]]) -> List[Tuple[chr, str]]:
        def key_func(item):
            row, col = item[1][0], int(item[1][1:])
            return (col, row)  # Prioritize column first, then row
        
        return sorted(letters, key=key_func)
