import unittest

from game.components import Board, DictionaryWrapper
from game.globals import *
from game.utils import *

class TestBoard(unittest.TestCase):

    def setUp(self):
        language = LANGUAGES['ENG']
        self.dict = DictionaryWrapper(language)

    @measure_time
    def test_serialize_words_horizontal(self):
        board = Board(self.dict, BOARD_ROW, BOARD_COL, SPECIAL_CELLS)

        word_list = {
            'ASTRONOMY': [TILE(0, 0, 'A'),TILE(0, 1, 'S'),TILE(0, 2, 'T'),TILE(0, 3, 'R'),TILE(0, 4, 'O'),TILE(0, 5, 'N'),TILE(0, 6, 'O'),TILE(0, 7, 'M'),TILE(0, 8, 'Y')],
            'HELLO':     [TILE(1, 0, 'H'),TILE(1, 1, 'E'),TILE(1, 2, 'L'),TILE(1, 3, 'L'),TILE(1, 4, 'O')],
            'PYTHON':    [TILE(2, 0, 'P'),TILE(2, 1, 'Y'),TILE(2, 2, 'T'),TILE(2, 3, 'H'),TILE(2, 4, 'O'),TILE(2, 5, 'N')],
            'WORLD':     [TILE(3, 0, 'W'),TILE(3, 1, 'O'),TILE(3, 2, 'R'),TILE(3, 3, 'L'),TILE(3, 4, 'D')],
        }

        for expected, word in word_list.items():
            out = board.serialize_word(word)
            self.assertEqual(out, expected)
    
    @measure_time
    def test_serialize_words_verticals(self):
        board = Board(self.dict, BOARD_ROW, BOARD_COL, SPECIAL_CELLS)

        word_list = {
            'PYTHON': [TILE(0, 0, 'P'),TILE(1, 0, 'Y'),TILE(2, 0, 'T'),TILE(3, 0, 'H'),TILE(4, 0, 'O'),TILE(5, 0, 'N')],
            'HELLO':  [TILE(0, 1, 'H'),TILE(1, 1, 'E'),TILE(2, 1, 'L'),TILE(3, 1, 'L'),TILE(4, 1, 'O')],
            'WORLD':  [TILE(0, 2, 'W'),TILE(1, 2, 'O'),TILE(2, 2, 'R'),TILE(3, 2, 'L'),TILE(4, 2, 'D')],
            'EARTH':  [TILE(0, 3, 'E'),TILE(1, 3, 'A'),TILE(2, 3, 'R'),TILE(3, 3, 'T'),TILE(4, 3, 'H')],
        }

        for expected, word in word_list.items():
            out = board.serialize_word(word)
            self.assertEqual(out, expected)

    @measure_time
    def test_validate_words_horizontals(self):
        board = Board(self.dict, BOARD_ROW, BOARD_COL, SPECIAL_CELLS)

        word_list = {
            'ASTRONOMY': [TILE(0, 0, 'A'),TILE(0, 1, 'S'),TILE(0, 2, 'T'),TILE(0, 3, 'R'),TILE(0, 4, 'O'),TILE(0, 5, 'N'),TILE(0, 6, 'O'),TILE(0, 7, 'M'),TILE(0, 8, 'Y')],
            'HELLO':     [TILE(1, 0, 'H'),TILE(1, 1, 'E'),TILE(1, 2, 'L'),TILE(1, 3, 'L'),TILE(1, 4, 'O')],
            'PYTHON':    [TILE(2, 0, 'P'),TILE(2, 1, 'Y'),TILE(2, 2, 'T'),TILE(2, 3, 'H'),TILE(2, 4, 'O'),TILE(2, 5, 'N')],
            'WORLD':     [TILE(3, 0, 'W'),TILE(3, 1, 'O'),TILE(3, 2, 'R'),TILE(3, 3, 'L'),TILE(3, 4, 'D')],
        }

        for expected, word in word_list.items():
            valid, out = board.validate_word(word)
            self.assertEqual(out, expected)
            self.assertTrue(out, valid)
    
    @measure_time
    def test_validate_words_verticals(self):
        board = Board(self.dict, BOARD_ROW, BOARD_COL, SPECIAL_CELLS)

        word_list = {
            'PYTHON': [TILE(0, 0, 'P'),TILE(1, 0, 'Y'),TILE(2, 0, 'T'),TILE(3, 0, 'H'),TILE(4, 0, 'O'),TILE(5, 0, 'N')],
            'HELLO':  [TILE(0, 1, 'H'),TILE(1, 1, 'E'),TILE(2, 1, 'L'),TILE(3, 1, 'L'),TILE(4, 1, 'O')],
            'WORLD':  [TILE(0, 2, 'W'),TILE(1, 2, 'O'),TILE(2, 2, 'R'),TILE(3, 2, 'L'),TILE(4, 2, 'D')],
            'EARTH':  [TILE(0, 3, 'E'),TILE(1, 3, 'A'),TILE(2, 3, 'R'),TILE(3, 3, 'T'),TILE(4, 3, 'H')],
        }

        for expected, word in word_list.items():
            valid, out = board.validate_word(word)
            self.assertEqual(out, expected)
            self.assertTrue(out, valid)

    @measure_time
    def test_validate_words_diagonal(self):
        board = Board(self.dict, BOARD_ROW, BOARD_COL, SPECIAL_CELLS)

        word_list = {
            'PYTHON': [TILE(0, 0, 'P'),TILE(1, 1, 'Y'),TILE(2, 2, 'T'),TILE(3, 3, 'H'),TILE(4, 4, 'O'),TILE(5, 5, 'N')],
            'HELLO': [TILE(0, 0, 'H'),TILE(1, 1, 'E'),TILE(2, 2, 'L'),TILE(3, 3, 'L'),TILE(4, 4, 'O')],
            'WORLD': [TILE(0, 0, 'W'),TILE(1, 1, 'O'),TILE(2, 2, 'R'),TILE(3, 3, 'L'),TILE(4, 4, 'D')],
            'EARTH': [TILE(0, 0, 'E'),TILE(1, 1, 'A'),TILE(2, 2, 'R'),TILE(3, 3, 'T'),TILE(4, 4, 'H')],
        }

        for expected, word in word_list.items():
            valid, out = board.validate_word(word)
            self.assertEqual(out, '')
            self.assertFalse(out, valid)

if __name__ == '__main__':
    unittest.main()
