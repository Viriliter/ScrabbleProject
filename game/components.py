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
    
    def get_sorted_rack(self, reverse: bool= False) -> List[LETTER]:
        copy_container = copy.deepcopy(self.__container)
        copy_container.sort(key=lambda x: ord(x), reverse=reverse)
        return copy_container

    def get_rack(self) -> List[LETTER]:
        copy_container = copy.deepcopy(self.__container)
        return copy_container

class DictionaryWrapper:
    def __init__(self, language: LANGUAGE):
        self.__alphabet: ALPHABET = language.alphabet.copy()
        self.__uri: str = get_absolute_path(language.uri)

        self.__dic = Dictionary("myDictionary")

        with open(os.path.join(os.path.dirname(__file__), 'data', self.__uri), 'rb') as f:
            data = f.read()
        self.__dic.load_dawg(BytesIO(data))

    def load_language(self, language: LANGUAGE) -> None:
        self.__alphabet: ALPHABET = language.alphabet.copy()
        self.__uri: str = get_absolute_path(language.uri)

        self.__dic = Dictionary("myDictionary")

        with open(os.path.join(os.path.dirname(__file__), 'data', self.__uri), 'rb') as f:
            data = f.read()
        self.__dic.load_dawg(BytesIO(data))

        #TODO Add whitelist (not applicable)

        self.__dic.add_links()

    def has_word(self, word: str) -> bool:
        if len(word) == 0: return False
        return True if self.__dic.has_word(word) else False

    def has_sequence(self, word: str) -> bool:
        if len(word) == 0: return False
        return True if self.__dic.has_sequence(word) else False

    def get_sequence_roots(self, word: str) -> Optional[List[LetterNode]]:
        if len(word) == 0: return None
        return self.__dic.get_sequence_roots(word) if self.__dic.has_sequence(word) else None

    def find_anagrams(self, word: str) -> List[str]:
        return self.__dic.find_anagrams(word)

    def get_alphabet(self) -> ALPHABET:
        return self.__alphabet

    def get_all_letters(self) -> List[LETTER]:
        out: List[LETTER] = []
        for letter in self.__alphabet.keys():
            if (letter==BLANK_LETTER): continue
            out.append(letter)
        return out

class BoardContainer(np.ndarray):
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
        return self[row, col]

    def set(self, row: int, col: int, value: Optional[TILE]) -> None:
        self[row, col] = value

    def is_empty(self, row: int, col: int) -> bool:
        if (self[row, col] is None):
            return True
        return False

    def has_locked_tile(self ,row: int, col: int) -> bool:
        # If no tile is placed, return False
        if (self[row, col] is None):
            return False
        
        # If tile is placed and locked, return True
        if self.at(row, col).is_locked:
            return True
        return False

    def is_within_bounds(self, row: int, col: int) -> bool:
        if row < 0 or row > self.rows:
            return False
        if col < 0 or col > self.cols:
            return False
        return True

    def clear(self) -> None:
        self.fill(None)

    def serialize(self) -> Dict[str, LETTER]:
        result = {}
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.is_empty(row,col):
                    result[str(CL(row, col))] = self.at(row, col).letter
        return result

class Board:
    class Direction:
        Vertical = 0
        Horizontal = 1
        Undefined = 2

    def __init__(self,
                 dictionary: DictionaryWrapper,
                 row=BOARD_ROW,
                 col=BOARD_COL, 
                 special_cells: Dict[CL, CT]=SPECIAL_CELLS):
        self.__dictionary: DictionaryWrapper = dictionary
        self.__row: int = row
        self.__col: int = col
        self.__cells = BoardContainer(self.__row, self.__col)  # [['' for _ in range(self.__col)] for _ in range(self.__row)]
        self.__special_cells = copy.deepcopy(special_cells)

        self._cross_checks: List[List[List[List[str]]]] = []
        self.best_score: int = 0
        self.best_moves: List[MOVE] = []


        self.clear()

    def get_best_moves(self) -> List[MOVE]:
        return self.best_moves

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
        return self.__dictionary

    def at(self, row: int, col: int) -> Optional[TILE]:
        return self.__cells.at(row, col)

    def check_boundary(self, tile: TILE) -> bool:
        # Check if the row and column are within bounds of board
        if tile.row < 0 or tile.row >= self.__row:
            return False
        if tile.col < 0 or tile.col >= self.__col:
            return False
        return True

    def place_tile(self, tile: TILE) -> bool:
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
        if word is None or len(word) == 0:
            return False
        
        is_placed = True
        for tile in word:
            is_placed &= self.place_tile(tile)
        return is_placed

    def serialize_word(self, word: WORD) -> str:
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
        serialized_word = self.serialize_word(word)
        if serialized_word == "": False, ""

        return self.__dictionary.has_word(serialized_word), serialized_word

    @staticmethod
    def get_bonus(ct: CT) -> Tuple[int, int]:
        if ct == CT.DOUBLE_LETTER:
            return (2, 1)  # Letter Multiplier, Word Multiplier 
        elif ct == CT.TRIPLE_LETTER:
            return (3, 1)
        elif ct == CT.DOUBLE_WORD:
            return (1, 2)
        elif ct == CT.TRIPLE_WORD:
            return (1, 3)
        else:
            return (1, 1)

    def calculate_points(self, word: WORD) -> int:
        direction = self.find_word_direction(word)

        if (direction == Board.Direction.Horizontal):
            sorted_ = sorted(word, key=lambda x: x.col, reverse=False)

            o_words: List[Dict[str, int]] = []
            completed_word = self.complete_word(sorted_[0].row, sorted_[0].col, 0, 1, sorted_)
            
            score = self.score_play(completed_word[-1].row, completed_word[-1].col, 0, 1, completed_word, o_words)
            print(f"Horizontal Score: {score} words : {o_words}")
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
            print(f"Vertical Score: {score} words : {o_words}")
            # Check all founded words are valid
            flag = True
            for t_word in o_words:
                flag &= self.__dictionary.has_word(t_word['word'])

            return score if flag else 0
        else:  # Undefined direction
            return 0

    def clear(self) -> None:
        self.__cells.clear()

    def serialize(self) -> Dict[str, LETTER]:
        return self.__cells.serialize()

    def serialize2str(self) -> str:
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

    def deserialize(self, serialized_board: str):
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

    def print(self) -> None:
        print(self.serialize2str())

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
            cell_type = self.__special_cells.get(CL(r, c), CT.ORDINARY)
            lm, wm = Board.get_bonus(cell_type)
            tile_score = alphabet[tile.letter][1] if tile.point <0 else tile.point

            if not self.__cells.is_empty(r, c):
                print(f"Cell is not empty {r}, {c}")
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
        return [letter for letter in a if letter in b]

    def is_anchor(self, row: int, col: int) -> bool:
        """
        Unlike Appel and Jacobsen, who anchor plays on empty squares,
        we anchor plays on a square with a tile that has an adjacent
        (horizontal or vertical) non-empty square.
        """
        if not self.__cells.is_empty(row, col):
            return ((col > 0 and self.__cells.is_empty(row, col-1)) or
                    (col < self.__cells.cols - 1 and self.__cells.is_empty(row, col+1)) or
                    (row > 0 and self.__cells.is_empty(row-1, col)) or
                    (row < self.__cells.rows - 1 and self.__cells.is_empty(row+1, col)))
        return False

    def find_word_direction(self, word: WORD) -> Direction:
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
        return 0

    def compute_cross_checks(self, available: List[LETTER]) -> None:
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

    def forward(self, row: int, col: int, 
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
            
            if score > self.best_score:
                # This is best score so far
                self.best_score = score
                heapq.heappush(self.best_moves, MOVE(score, word_so_far[:]))

                print("*************")
                print("score:", score)
                print("word_so_far:", word_so_far)
                print("*************")
        
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
                    self.forward(erow, ecol, 
                                 drow, dcol, 
                                 shrunk_rack, tiles_played + played_tile, 
                                 post, word_so_far)
            
            word_so_far.pop()

    def back(self, row: int, col: 
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
            shrunk_rack = rack_tiles
            #FIXME shrunk_rack = rack_tiles[:]
            if played_tile > 0:
                # Letter came from the rack
                tile = next((t for t in shrunk_rack if t.letter == letter), None) or next((t for t in shrunk_rack if t.is_blank), None)

                #FIXME tile = next((t for t in shrunk_rack if t.letter == letter), 
                #            next((t for t in shrunk_rack if t.is_blank), None))

                # Placement is not used in score calculation
                word_so_far.insert(0, TILE(erow, ecol, letter, tile.point, tile.is_blank))
                shrunk_rack = [t for t in shrunk_rack if t != tile]
            else:
                # Letter already on the self
                word_so_far.insert(0, self.at(erow, ecol))

            for pre in d_node.preNodes:
                if pre.letter == letter:
                    self.back(erow, ecol, 
                              drow, dcol, 
                              shrunk_rack, tiles_played + played_tile, anchor_node, 
                              pre, word_so_far)
            
            word_so_far.pop(0)

        # If this is the start of a valid word and we're at the board edge or an empty cell
        #FIXME if not d_node.preNodes and (erow < 0 or ecol < 0 or self.__cells.is_empty(erow, ecol)):
        if len(d_node.preNodes) == 0 and (erow < 0 or ecol < 0 or self.__cells.is_empty(erow, ecol)):
            self.forward(row + drow * (len(word_so_far) - 1),
                         col + dcol * (len(word_so_far) - 1),
                         drow, dcol,
                         rack_tiles, tiles_played,
                         anchor_node, word_so_far)
    
    def best_opening_play(self, rack_tiles: List[TILE]) -> Tuple[int, WORD]:
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
                    
                    print("£££££££££££££")
                    PRINT_WORD(best_word)
                    print("£££££££££££££")

                    best_word = placements
                    
                    #TODO report the placement
                    #report({"placements": placements, "word": choice, "score": score})
        
        return (best_score, best_word)

    def find_best_play(self, rack_letters: List[LETTER]) -> List[MOVE]:
        self.best_moves.clear()
        self.best_score = 0
        self._cross_checks.clear()

        # Convert list of letters to list of tiles
        rack_tiles: List[TILE] = []
        for letter in rack_letters:
            is_blank = True if letter == BLANK_LETTER else False
            rack_tiles.append(TILE(0, 0, letter, self.__dictionary.get_alphabet()[letter][1], is_blank, False))

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
                        self.compute_cross_checks(available)
                        anchored = True

                    anchor_tile = self.at(row, col)

                    roots = self.__dictionary.get_sequence_roots(anchor_tile.letter)
                    for anchor_node in roots:
                        # Try and back up then forward through the dictionary to find longer sequences across
                        self.back(row, col, 0, 1,
                                         rack_tiles, 0,
                                         anchor_node, anchor_node,
                                         [ anchor_tile ])

                        # down
                        self.back(row, col, 1, 0,
                                         rack_tiles, 0,
                                         anchor_node, anchor_node,
                                         [ anchor_tile ])

        if not anchored:
            best_score, best_word = self.best_opening_play(rack_tiles)
            return [ MOVE(best_score, best_word) ]
        else:
            return self.get_best_moves()
