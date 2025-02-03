from typing import List, Dict, Tuple
import random

from .globals import *

class TileBag:
    __reference_tiles: Dict[str, Tuple[int, int]] = None
    __tiles: Dict[str, Tuple[int, int]] = {}
    __remaning_tiles: int = 0

    def __init__(self):
        self.__reference_tiles = {}
        self.__tiles = {}
        self.__remaning_tiles = 0

    def load(self, tiles: Dict[str, int]) -> None:
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

class Rack:
    __tile_bag: TileBag = None
    __rack: List[chr] = []

    def __init__(self, tile_bag: TileBag):
        self.__tile_bag = tile_bag
        self.initialize()

    def add_to_rack(self) -> None:
        letter = self.__tile_bag.get_random_letter()
        self.__rack.append(letter)

    def remove_from_rack(self, letter: chr) -> None:
        self.__rack.remove(letter)

    def get_rack_length(self) -> int:
        return self.__rack.__len__()

    def get_letters(self) -> List[chr]:
        return self.__rack.copy()

    def replenish_rack(self) -> None:
        while self.get_rack_length() < INITIAL_TILE_COUNT and self.__tile_bag.get_remaining_tiles() > 0:
            self.add_to_rack()

    def initialize(self) -> None:
        for _ in range(INITIAL_TILE_COUNT):
            self.add_to_rack()

class Dictionary:
    __tiles: Dict[str, int] = {}

    def __init__(self, tiles: Dict[str, int]):
        self.__tiles = tiles.copy()

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
    __row: int = 0
    __col: int = 0
    __cells: List[chr] = []
    __special_cells: Dict[CL, CL] = {}
    __tiles: Dict[str, Tuple[int, int]]
    
    def __init__(self, row=BOARD_ROW, col=BOARD_COL, tiles=ENGLISH_TILES, special_cells=SPECIAL_CELLS):
        self.__row = row
        self.__col = col
        self.__special_cells = special_cells.copy()
        self.__tiles = tiles.copy()

        #Dictionary(ENGLISH_TILES)

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
