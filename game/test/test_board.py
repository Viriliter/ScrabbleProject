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

    @measure_time
    def test_calculate_points_horizontal(self):
        board = Board(self.dict, BOARD_ROW, BOARD_COL, SPECIAL_CELLS)

        word_list = {
            'ASTRONOMY': ([TILE(0, 0, 'A'),TILE(0, 1, 'S'),TILE(0, 2, 'T'),TILE(0, 3, 'R'),TILE(0, 4, 'O'),TILE(0, 5, 'N'),TILE(0, 6, 'O'),TILE(0, 7, 'M'),TILE(0, 8, 'Y')], 135),
            'HELLO':     ([TILE(1, 0, 'H'),TILE(1, 1, 'E'),TILE(1, 2, 'L'),TILE(1, 3, 'L'),TILE(1, 4, 'O')],                                                                 16),
            'PYTHON':    ([TILE(2, 0, 'P'),TILE(2, 1, 'Y'),TILE(2, 2, 'T'),TILE(2, 3, 'H'),TILE(2, 4, 'O'),TILE(2, 5, 'N')],                                                 28),
            'WORLD':     ([TILE(3, 0, 'W'),TILE(3, 1, 'O'),TILE(3, 2, 'R'),TILE(3, 3, 'L'),TILE(3, 4, 'D')],                                                                 26),
        }

        for expected, (word, exp_score) in word_list.items():
            points = board.calculate_points(word)
            self.assertEqual(points, exp_score)

    @measure_time
    def test_calculate_points_vertical(self):
        board = Board(self.dict, BOARD_ROW, BOARD_COL, SPECIAL_CELLS)

        word_list = {
            'PYTHON': ([TILE(0, 0, 'P'),TILE(1, 0, 'Y'),TILE(2, 0, 'T'),TILE(3, 0, 'H'),TILE(4, 0, 'O'),TILE(5, 0, 'N')], 54),
            'HELLO':  ([TILE(0, 1, 'H'),TILE(1, 1, 'E'),TILE(2, 1, 'L'),TILE(3, 1, 'L'),TILE(4, 1, 'O')]                , 16),
            'WORLD':  ([TILE(0, 2, 'W'),TILE(1, 2, 'O'),TILE(2, 2, 'R'),TILE(3, 2, 'L'),TILE(4, 2, 'D')]                , 18),
            'EARTH':  ([TILE(0, 3, 'E'),TILE(1, 3, 'A'),TILE(2, 3, 'R'),TILE(3, 3, 'T'),TILE(4, 3, 'H')]                , 18),
        }

        for expected, (word, exp_score) in word_list.items():
            points = board.calculate_points(word)
            self.assertEqual(points, exp_score)

    @measure_time
    def test_calculate_points_diagonal(self):
        board = Board(self.dict, BOARD_ROW, BOARD_COL, SPECIAL_CELLS)

        word_list = {
            'PYTHON': ([TILE(0, 0, 'P'),TILE(1, 1, 'Y'),TILE(2, 2, 'T'),TILE(3, 3, 'H'),TILE(4, 4, 'O'),TILE(5, 5, 'N')], 0),
            'HELLO':  ([TILE(0, 0, 'H'),TILE(1, 1, 'E'),TILE(2, 2, 'L'),TILE(3, 3, 'L'),TILE(4, 4, 'O')]                , 0),
            'WORLD':  ([TILE(0, 0, 'W'),TILE(1, 1, 'O'),TILE(2, 2, 'R'),TILE(3, 3, 'L'),TILE(4, 4, 'D')]                , 0),
            'EARTH':  ([TILE(0, 0, 'E'),TILE(1, 1, 'A'),TILE(2, 2, 'R'),TILE(3, 3, 'T'),TILE(4, 4, 'H')]                , 0),
        }

        for expected, (word, exp_score) in word_list.items():
            points = board.calculate_points(word)
            self.assertEqual(points, exp_score, f"Failed for word: {expected}")
    
    @measure_time
    def test_calculate_points_complex(self):
        board = Board(self.dict, BOARD_ROW, BOARD_COL, SPECIAL_CELLS)

        word_list = {
            'ASTRONOMY': ([TILE(4 , 7 , 'A'),TILE(5 , 7 , 'S'),TILE(6 , 7 , 'T'),TILE(7 , 7 , 'R'),TILE(8, 7, 'O'),TILE(9, 7, 'N'),TILE(10, 7, 'O'),TILE(11, 7, 'M'),TILE(12, 7, 'Y')],  34),
            'HELLO':     ([TILE(10, 3 , 'H'),TILE(10, 4 , 'E'),TILE(10, 5 , 'L'),TILE(10, 6 , 'L')],                                                                                     16),
            'PYTHON':    ([TILE(6 , 5 , 'P'),TILE(6 , 6 , 'Y'),TILE(6 , 8 , 'H'),TILE(6 , 9 , 'O'),TILE(6, 10, 'N')],                                                                    22),
            'WORLD':     ([TILE(5 , 9 , 'W'),TILE(7 , 9 , 'R'),TILE(8 , 9 , 'L'),TILE(9 , 9 , 'D')],                                                                                     21),
            'MUMMY':     ([TILE(11, 8 , 'U'),TILE(11, 9 , 'M'),TILE(11, 10, 'M'),TILE(11, 11, 'Y')],                                                                                     28),
            'ROLE':      ([TILE(7 , 10, 'O'),TILE(7 , 11, 'L'),TILE(7 , 12, 'E')],                                                                                                       7),
            'AYE':       ([TILE(12,11 , 'A'),TILE(12, 12, 'Y'),TILE(12, 13, 'E')],                                                                                                       17),
            'PA':        ([TILE(7 , 5 , 'A')],                                                                                                                                           4),
            'LA':        ([TILE(7 , 4 , 'L')],                                                                                                                                           2),
            'OPERA':     ([TILE(3 , 3 , 'O'),TILE(4 , 3 , 'P'),TILE(5 , 3 , 'E'),TILE(6 , 3 , 'R'),TILE(7 , 3 , 'A')],                                                                   20)
        }

        for expected, (word, exp_score) in word_list.items():           
            points = board.calculate_points(word)
            board.place_word(word)
            board.print()
            self.assertEqual(points, exp_score, f"Failed for word: {expected}")
    
    def test_load_from_string(self):
        board = Board(self.dict, BOARD_ROW, BOARD_COL, SPECIAL_CELLS)

        expected_output = ""
        expected_output += "     A  B  C  D  E  F  G  H  I  J  K  L  M  N  O\n"
        expected_output += "   +----------------------------------------------+\n"
        expected_output += " 1 | C  .  .  .  .  .  .  .  .  .  .  .  .  .  A  |\n"
        expected_output += " 2 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        expected_output += " 3 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        expected_output += " 4 | .  .  .  O  .  .  .  .  .  .  .  .  .  .  .  |\n"
        expected_output += " 5 | .  .  .  P  .  .  .  A  .  .  .  .  .  .  .  |\n"
        expected_output += " 6 | .  .  .  E  .  .  .  S  .  W  .  .  .  .  .  |\n"
        expected_output += " 7 | .  .  .  R  .  P  Y  T  H  O  N  .  .  .  .  |\n"
        expected_output += " 8 | .  .  .  A  L  A  .  R  .  R  O  L  E  .  .  |\n"
        expected_output += " 9 | .  .  .  .  .  .  .  O  .  L  .  .  .  .  .  |\n"
        expected_output += "10 | .  .  .  .  .  .  .  N  .  D  .  .  .  .  .  |\n"
        expected_output += "11 | .  .  .  H  E  L  L  O  .  .  .  .  .  .  .  |\n"
        expected_output += "12 | .  .  .  .  .  .  .  M  U  M  M  Y  .  .  .  |\n"
        expected_output += "13 | .  .  .  .  .  .  .  Y  .  .  .  A  Y  E  .  |\n"
        expected_output += "14 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        expected_output += "15 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        expected_output += "   +----------------------------------------------+\n"

        board.deserialize(expected_output)
        result = board.serialize()
        
        self.assertEqual(expected_output, result, f"Failed")

if __name__ == '__main__':
    unittest.main()
