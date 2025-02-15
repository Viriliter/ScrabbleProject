from typing import List, Dict, Tuple
import random

from .globals import *

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

class Dictionary:
    def __init__(self, language: LANGUAGE):
        self.__alphabet: ALPHABET = language.alphabet.copy()
        self.__uri: str = language.uri

    def validate_word(self, word: str) -> bool:
        return False

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
                 dictionary: Dictionary,
                 row=BOARD_ROW,
                 col=BOARD_COL, 
                 special_cells: Dict[CL, CT]=SPECIAL_CELLS):
        self.__dictionary = dictionary
        self.__row: int = row
        self.__col: int = col
        self.__cells: List[LETTER] = []
        self.__special_cells = special_cells.copy()

        self.clear()

    def is_placable(self, letter: TILE) -> bool:
        if not (self.__cells[letter.row][letter.col] == ''):
            return True
        else:
            return False

    def place_tile(self, letter: TILE) -> bool:
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

    def serialize(self) -> Dict[Tuple[int, int], LETTER]:
        board_state = {}
        for row in range(self.__row):
            for col in range(self.__col):
                if self.__cells[row][col] != '':
                    board_state[(row, col)] = self.__cells[row][col]
        return board_state

    @staticmethod
    def sort_letters(letters: List[Tuple[LETTER, str]]) -> List[Tuple[LETTER, str]]:
        def key_func(item):
            row, col = item[1][0], int(item[1][1:])
            return (col, row)  # Prioritize column first, then row
        
        return sorted(letters, key=key_func)
