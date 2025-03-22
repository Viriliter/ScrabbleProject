import os
import random
import copy
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

class DictionaryWrapper:
    def __init__(self, language: LANGUAGE):
        self.__alphabet: ALPHABET = language.alphabet.copy()
        self.__uri: str = get_absolute_path(language.uri)

        self.__dic = Dictionary("myDictionary")

        with open(os.path.join(os.path.dirname(__file__), 'data', self.__uri), 'rb') as f:
            data = f.read()
        self.__dic.load_dawg(BytesIO(data))

    def has_word(self, word: str) -> bool:
        if len(word) == 0: return False
        return True if self.__dic.has_word(word) else False

    def has_sequence(self, word: str) -> bool:
        if len(word) == 0: return False
        return True if self.__dic.has_sequence(word) else False

    def get_sequence(self, word: str) -> Optional[List[str]]:
        if len(word) == 0: return None
        return self.__dic.get_sequence_roots(word) if self.__dic.has_sequence(word) else None

    def get_alphabet(self) -> ALPHABET:
        return self.__alphabet

@dataclass(frozen=True)
class Neighbors:
    up:     Tuple[int, int]
    right:  Tuple[int, int]
    down:   Tuple[int, int]
    left:   Tuple[int, int]

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

    def at(self, row: int, col: int) -> Optional[TILE]:
        return self[row, col]

    def set(self, row: int, col: int, value: Optional[TILE]) -> None:
        self[row, col] = value

    def is_empty(self, row: int, col: int) -> bool:
        if (self[row, col] is None):
            return True
        return False

    def is_within_bounds(self, row: int, col: int) -> bool:
        if row < 0 or row > self.rows:
            return False
        if col < 0 or col > self.cols:
            return False
        return True

    def has_neighbor(self, row: int, col: int) -> Neighbors:
        """
        Check if the cell has any neighbors and returns its neighbors
        """
        neighbors: Neighbors = None
        if row > 0 and not self.is_empty(row - 1, col):
            neighbors.up = (row - 1, col)
        else:
            neighbors.up = None
        if row < self.rows - 1 and not self.is_empty(row + 1, col):
            neighbors.down = (row + 1, col)
        else:
            neighbors.down = None
        if col > 0 and not self.is_empty(row, col - 1):
            neighbors.left = (row, col-1)
        else:
            neighbors.left = None
        if col < self.cols - 1 and not self.is_empty(row, col + 1):
            neighbors.right = (row + 1, col+1)
        else:
            neighbors.right = None
        return neighbors


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

        self.__cross_checks = []
        self.__best_score = 0


        self.clear()

    def check_boundary(self, tile: TILE) -> bool:
        # Check if the row and column are within bounds of board
        if tile.row < 0 or tile.row >= self.__row:
            return False
        if tile.col < 0 or tile.col >= self.__col:
            return False
        return True

    def place_tile(self, tile: TILE) -> bool:
        if self.__cells.is_empty(tile.row, tile.col):
            self.__cells.set(tile.row, tile.col, tile)
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

    @deprecated(version='0.1.0', reason="This method cannot handle cross-words so it is deprecated")
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
        for tile in word:
            if not self.check_boundary(tile): return 0
            if not self.__cells.is_empty(tile.row, tile.col): return 0

        for tile in word:
            print(f"Letter2: {tile.letter}, row2: {tile.row}, col2: {tile.col}")

        rows: Dict[int, WORD] = {}
        cols: Dict[int, WORD] = {}
        
        score = 0

        for tile in word:
            rows.setdefault(tile.row, []).append(tile)
            cols.setdefault(tile.col, []).append(tile)
        
        # Check word is horizontal
        if len(cols.items()) == len(word) and len(rows.items()) == 1:
            sorted_ = sorted(word, key=lambda x: x.col, reverse=False)
            r_sorted = sorted(word, key=lambda x: x.col, reverse=True)

            o_words: List[Dict[str, int]] = []
            print(f"r_sorted[0].row, r_sorted[0].col: {r_sorted[0].row}, {r_sorted[0].col}")
            score = self.score_play(r_sorted[0].row, r_sorted[0].col, 0, 1, sorted_, o_words)
            print(f"Horizontal Score: {score} words : {o_words}")
            # Check all founded words are valid
            flag = True
            for t_word in o_words:
                flag &= self.__dictionary.has_word(t_word['word'])

            return score if flag else 0

        # Check word is vertical
        if len(rows.items()) == len(word) and len(cols.items()) == 1:
            sorted_ = sorted(word, key=lambda x: x.row, reverse=False)
            r_sorted = sorted(word, key=lambda x: x.row, reverse=True)

            o_words: List[Dict[str, int]] = []
            score = self.score_play(r_sorted[0].row, r_sorted[0].col, 1, 0, sorted_, o_words)
            print(f"Vertical Score: {score} words : {o_words}")
            # Check all founded words are valid
            flag = True
            for t_word in o_words:
                flag &= self.__dictionary.has_word(t_word['word'])

            return score if flag else 0

        return score

    def clear(self) -> None:
        self.__cells.clear()

    def serialize(self) -> Dict[str, LETTER]:
        return self.__cells.serialize()

    @staticmethod
    def intersection(a: List[str], b: List[str]) -> List[str]:
        return [letter for letter in a if letter in b]

    def is_anchor(self, row: int, col: int) -> bool:
        if self.__cells.is_empty(row, col):
            return False

        # Check if any adjacent cell is empty
        left_empty = col > 0 and self.__cells.is_empty(row, col - 1)
        right_empty = col < self.__cells.cols - 1 and self.__cells.is_empty(row, col + 1)
        top_empty = row > 0 and self.__cells.is_empty(row - 1, col)
        bottom_empty = row < self.__cells.rows - 1 and self.__cells.is_empty(row + 1, col)

        return left_empty or right_empty or top_empty or bottom_empty

    def _forward(self, row: int, col: int, drow: int, dcol: int, 
                rack_tiles: WORD, tiles_played: int, d_node: LetterNode, word_so_far: WORD):
        # Square we're hopefully extending into
        erow = row + drow
        ecol = col + dcol

        # Tail recurse; report words as soon as we find them
        # Are we sitting at the end of a scoring word?
        if d_node.isEndOfWord and len(word_so_far) >= 2 and tiles_played > 0 and (
                erow == self.__cells.rows or ecol == self.__cells.cols or not self.__cells.is_empty(erow, ecol)):
            words = []
            score = self.score_play(row, col, drow, dcol, word_so_far, words)

            if score > self.__best_score:
                self.__best_score = score
                # Report the move
                #report(Move(
                #    placements=[t for t in word_so_far if not board.at(t.col, t.row).tile],
                #    words=words,
                #    score=score
                #))

        available = []  # List of letters that can be extended with
        played_tile = 0

        if erow < self.__cells.rows and ecol < self.__cells.cols:
            # Do we have an empty cell we can extend into?
            if self.__cells.is_empty(erow, ecol):
                have_blank = any(l.is_blank for l in rack_tiles)
                xc = self.__cross_checks[erow][ecol][dcol]

                available = Board.intersection(d_node.postLetters, xc if not have_blank else Board.intersection(rack_tiles, xc)
                )
                played_tile = 1
            else:
                # Have pre-placed tile
                available = [self.__cells.at(erow, ecol).letter]
        else:  # Off the board
            available = []

        for letter in available:
            shrunk_rack = rack_tiles
            if played_tile > 0:
                # Letter played from the rack
                rack_tile = next((l for l in shrunk_rack if l.letter == letter), None) or \
                            next((l for l in shrunk_rack if l.is_blank), None)
                word_so_far.append(TILE(row=erow, col=ecol, letter=letter, point=rack_tile.point, is_blank=rack_tile.is_blank))
                shrunk_rack = [t for t in shrunk_rack if t != rack_tile]
            else:
                word_so_far.append(self.__cells.at(erow, ecol))

            for post in d_node.postNodes:
                if post.letter == letter:
                    self._forward(erow, ecol, drow, dcol, shrunk_rack, tiles_played + played_tile, post, word_so_far)

            word_so_far.pop()

    def _back(self, row: int, col: int, drow: int, dcol: int,
             rack_tiles: WORD, tiles_played: int, anchor_node: LetterNode, d_node: LetterNode, word_so_far: WORD):
        # Square we're hopefully extending into
        erow = row - drow
        ecol = col - dcol

        available = []  # the set of possible candidate letters
        played_tile = 0

        # Do we have an adjacent empty cell we can back up into?
        if erow >= 0 and ecol >= 0:
            if self.__cells.is_empty(erow ,ecol):
                # Find common letters between the rack, cross checks, and dNode pre.
                have_blank = any(l.is_blank for l in rack_tiles)
                xc = self.__cross_checks[erow][ecol][dcol]

                available = Board.intersection(d_node.preLetters, xc if not have_blank else Board.intersection([l.letter for l in rack_tiles], xc)
                )
                played_tile = 1
            else:
                # Non-empty square, might be able to walk back through it
                available = [self.__cells.at(erow, ecol).letter]
        else:
            # Off the board, nothing available for backing up
            available = []

        # Head recurse; longer words are more likely to be high scoring, so want to find them first
        for letter in available:
            shrunk_rack = rack_tiles
            if played_tile > 0:
                # Letter came from the rack
                tile = next((l for l in shrunk_rack if l.letter == letter), None) or next((l for l in shrunk_rack if l.is_blank), None)
                word_so_far.insert(0, TILE(row=erow, col=ecol, letter=letter, point=tile.point, is_blank=tile.is_blank))
                shrunk_rack = [t for t in shrunk_rack if t != tile]
            else:
                # Letter already on the board
                word_so_far.insert(0, self.__cells.at(erow, ecol))

            for pre in d_node.preNodes:
                if pre.letter == letter:
                    self._back(erow, ecol, drow, dcol, shrunk_rack, tiles_played + played_tile, anchor_node, pre, word_so_far)

            word_so_far.pop(0)

        # If this is the start of a word in the dictionary, and we're at the edge of the board or the prior cell is empty,
        # then we have a valid word start.
        if len(d_node.preNodes) == 0 and (erow < 0 or ecol < 0 or self.__cells.is_empty(erow, ecol)):
            # Try extending down beyond the anchor, with the letters
            # that we have determined comprise a valid rooted sequence.
            self._forward(row + drow * (len(word_so_far) - 1), col + dcol * (len(word_so_far) - 1), drow, dcol,
                    rack_tiles, tiles_played, anchor_node, word_so_far)

    def compute_cross_checks(self, available) -> None:
        xChecks = []
        for col in range(self.__cells.cols):
            this_col = []
            xChecks.append(this_col)

            for row in range(self.__cells.rows):
                this_cell = [[], []]
                this_col.append(this_cell)

                if not self.__cells.is_empty(row, col):
                    # The cell isn't empty, only this letter is valid.
                    letter = self.__cells.at(row, col).letter
                    this_cell[0].append(letter)
                    this_cell[1].append(letter)
                    continue

                # Find the words above and below
                word_above = ""
                r = row - 1
                while r >= 0 and not self.__cells.is_empty(r, col):
                    word_above = self.__cells.at(r, col).letter + word_above
                    r -= 1

                word_below = ""
                r = row + 1
                while r < self.__cells.rows and not self.__cells.is_empty(r, col):
                    word_below += self.__cells.at(r, col).letter
                    r += 1

                # Find the words left and right
                word_left = ""
                c = col - 1
                while c >= 0 and not self.__cells.is_empty(row, c):
                    word_left = self.__cells.at(row, c).letter + word_left
                    c -= 1

                word_right = ""
                c = col + 1
                while c < self.__cells.cols and not self.__cells.is_empty(row, c):
                    word_right += self.__cells.at(row, c).letter
                    c += 1

                # Find which (if any) letters form a valid cross word
                for letter in available:
                    h = word_left + letter + word_right

                    # Check if h is a valid word or a legal sequence
                    h_is_word = len(h) == 1 or self.__dictionary.has_word(h)
                    h_is_seq = h_is_word or (col > 0 and self.__dictionary.has_sequence(h))

                    v = word_above + letter + word_below
                    v_is_word = len(v) == 1 or self.__dictionary.has_word(v)
                    v_is_seq = v_is_word or (row > 0 and self.__dictionary.has_sequence(v))

                    if h_is_word and v_is_seq:
                        this_cell[0].append(letter)  # Valid down word

                    if v_is_word and h_is_seq:
                        this_cell[1].append(letter)  # Valid across word
        
        self.__cross_checks = xChecks

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

    def print(self):
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
        print("     " + "  ".join(column_headers))

        # Print the top border
        print("   +-" + "---" * cols + "+")
        
        # Print the board with row numbering
        for r in range(rows):
            # Print the row number (aligned with two spaces for better formatting)
            print(f"{r+1:2} |", end=" ")
            
            # Print the row contents
            for c in range(cols):
                print(f"{board[r][c]} ", end=" ")
            
            # Print the right border
            print("|")

        # Print the bottom border
        print("   +-" + "---" * cols + "+")
