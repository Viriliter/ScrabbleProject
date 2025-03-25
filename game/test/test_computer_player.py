import unittest

from game.components import Board, DictionaryWrapper
from game.computer_player import ComputerPlayer
from game.globals import *
from game.utils import *

class TestBoard(unittest.TestCase):

    def setUp(self):
        language = LANGUAGES['ENG']
        self.dict = DictionaryWrapper(language)
    
    def test_find_best_play(self):
        board = Board(self.dict, BOARD_ROW, BOARD_COL, SPECIAL_CELLS)
        player = ComputerPlayer(board)

        serialized_board = ""
        serialized_board += "     A  B  C  D  E  F  G  H  I  J  K  L  M  N  O\n"
        serialized_board += "   +----------------------------------------------+\n"
        serialized_board += " 1 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 2 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 3 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 4 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 5 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 6 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 7 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 8 | .  S  E  N  S  O  R  Y  .  .  .  .  .  .  .  |\n"
        serialized_board += " 9 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += "10 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += "11 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += "12 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += "13 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += "14 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += "15 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += "   +----------------------------------------------+\n"

        #serialized_board = ""
        #serialized_board += "     A  B  C  D  E  F  G  H  I  J  K  L  M  N  O\n"
        #serialized_board += "   +----------------------------------------------+\n"
        #serialized_board += " 1 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        #serialized_board += " 2 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        #serialized_board += " 3 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        #serialized_board += " 4 | .  .  .  .  .  .  .  S  .  .  .  .  .  .  .  |\n"
        #serialized_board += " 5 | .  .  .  .  .  .  .  E  .  .  .  .  .  .  .  |\n"
        #serialized_board += " 6 | .  .  .  .  .  .  .  N  .  .  .  .  .  .  .  |\n"
        #serialized_board += " 7 | .  .  .  .  .  .  .  S  .  .  .  .  .  .  .  |\n"
        #serialized_board += " 8 | .  .  .  .  .  .  .  O  .  .  .  .  .  .  .  |\n"
        #serialized_board += " 9 | .  .  .  .  .  .  .  R  .  .  .  .  .  .  .  |\n"
        #serialized_board += "10 | .  .  .  .  .  .  .  Y  .  .  .  .  .  .  .  |\n"
        #serialized_board += "11 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        #serialized_board += "12 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        #serialized_board += "13 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        #serialized_board += "14 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        #serialized_board += "15 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        #serialized_board += "   +----------------------------------------------+\n"

        board.deserialize(serialized_board)

        player.add_tiles(["E", "I", "I", "Y", "A", "H", " ", " "])
        best_score, best_word = player.play_turn()
        exp_best_score = 42
        exp_best_word = [TILE(0,0, "H"), TILE(0,0, "A"), TILE(0,0, "I"), TILE(0,0, "R"),
                         TILE(0,0, "I"), TILE(0,0, "E"), TILE(0,0, "S"), TILE(0,0, "T")]
        board.place_word(best_word)
        board.print()
        
        self.assertEqual(best_score, exp_best_score, f"Wrong best score: {best_score} ({exp_best_score})")

if __name__ == '__main__':
    unittest.main()
