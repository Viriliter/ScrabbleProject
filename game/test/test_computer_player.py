import unittest

from game.components import Board, DictionaryWrapper
from game.computer_player import ComputerPlayer
from game.globals import *
from game.enums import PlayerState
from game.utils import *

class TestBoard(unittest.TestCase):

    def setUp(self):
        language = LANGUAGES['ENG']
        self.dict = DictionaryWrapper(language)
        self.dict.load_language(LANGUAGE(ALPH_ENGLISH, "dictionaries/Oxford_5000.dict"))
    
    @measure_time
    def test_find_best_play(self):
        board = Board(self.dict, BOARD_ROW, BOARD_COL, PREMIUM_CELLS)
        player = ComputerPlayer(board, None, "bot")

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

        board.deserialize(serialized_board)
        board.enable_debug()

        player.add_tiles([TILE(letter="E"), TILE(letter="I"), TILE(letter="I"), TILE(letter="Y",), 
                          TILE(letter="A"), TILE(letter="H"), TILE(letter=" "), TILE(letter=" ",)])
        player.set_player_state(PlayerState.PLAYING)
        best_move = player.get_possible_moves()[0]  # Get most scored move
        exp_best_score = 30
        exp_best_word = [TILE(letter="E"), TILE(letter="Y"), TILE(letter="E"), TILE(letter="L"), 
                         TILE(letter="A"), TILE(letter="S"), TILE(letter="H")]
        board.print()
        board.place_word(best_move.word)
        board.print()
        
        self.assertEqual(best_move.score, exp_best_score, f"Wrong best score: {best_move.score} ({exp_best_score})")

    @measure_time
    def test_find_best_play_2(self):
        board = Board(self.dict, BOARD_ROW, BOARD_COL, PREMIUM_CELLS)
        player = ComputerPlayer(board, None, "bot")

        serialized_board = ""
        serialized_board += "     A  B  C  D  E  F  G  H  I  J  K  L  M  N  O\n"
        serialized_board += "   +----------------------------------------------+\n"
        serialized_board += " 1 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 2 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 3 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 4 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 5 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 6 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 7 | .  .  .  G  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 8 | .  .  .  C  R  A  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 9 | .  .  .  T  O  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += "10 | .  .  .  S  T  E  P  .  .  .  .  .  .  .  .  |\n"
        serialized_board += "11 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += "12 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += "13 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += "14 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += "15 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += "   +----------------------------------------------+\n"

        board.deserialize(serialized_board)
        board.enable_debug()

        player.add_tiles([TILE(letter="A"), TILE(letter="C"), TILE(letter="R"), TILE(letter="P")])
        player.set_player_state(PlayerState.PLAYING)
        move_0 = player.get_possible_moves()[0]  # Get most scored move
        exp_move_0_score = 3
        exp_move_0_word = [TILE(letter="E"), TILE(letter="A"), TILE(letter="R")]       
        board.print()
        board.print(move_0.word)
        self.assertEqual(move_0.score, exp_move_0_score, f"Wrong score: {move_0.score} ({exp_move_0_score})")

        is_same_word  = True
        for i, tile in enumerate(move_0.word):
            if tile.is_similar(exp_move_0_word[i]):
                pass
            else:
                is_same_word &= False

        self.assertTrue(is_same_word, f"Wrong best word: {move_0.word} ({exp_move_0_word})")

    @measure_time
    def test_find_best_play_3(self):
        board = Board(self.dict, BOARD_ROW, BOARD_COL, PREMIUM_CELLS)
        player = ComputerPlayer(board, None, "bot")

        serialized_board = ""
        serialized_board += "     A  B  C  D  E  F  G  H  I  J  K  L  M  N  O\n"
        serialized_board += "   +----------------------------------------------+\n"
        serialized_board += " 1 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 2 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 3 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 4 | .  .  .  O  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 5 | .  .  .  P  .  .  .  A  .  .  .  .  .  .  .  |\n"
        serialized_board += " 6 | .  .  .  E  .  .  .  S  .  W  .  .  .  .  .  |\n"
        serialized_board += " 7 | .  .  .  R  .  P  Y  T  H  O  N  .  .  .  .  |\n"
        serialized_board += " 8 | .  .  .  A  L  A  .  R  .  R  O  L  E  .  .  |\n"
        serialized_board += " 9 | .  .  .  .  .  .  .  O  .  L  .  .  .  .  .  |\n"
        serialized_board += "10 | .  .  .  .  .  .  .  N  .  D  .  .  .  .  .  |\n"
        serialized_board += "11 | .  .  .  H  E  L  L  O  .  .  .  .  .  .  .  |\n"
        serialized_board += "12 | .  .  .  .  .  .  .  M  U  M  M  Y  .  .  .  |\n"
        serialized_board += "13 | .  .  .  .  .  .  .  Y  .  .  .  A  Y  E  .  |\n"
        serialized_board += "14 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += "15 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += "   +----------------------------------------------+\n"

        board.deserialize(serialized_board)
        board.enable_debug()

        player.add_tiles([TILE(letter="A"), TILE(letter="C"), TILE(letter="R"), TILE(letter="P")])
        player.set_player_state(PlayerState.PLAYING)
        move_0 = player.get_possible_moves()[0]  # Get most scored move
        exp_move_0_score = 13
        exp_move_0_word = [TILE(letter="M"), TILE(letter="A"), TILE(letter="P")]       
        board.print()
        board.print(move_0.word)
        self.assertEqual(move_0.score, exp_move_0_score, f"Wrong score: {move_0.score} ({exp_move_0_score})")

        is_same_word  = True
        for i, tile in enumerate(move_0.word):
            if tile.is_similar(exp_move_0_word[i]):
                pass
            else:
                is_same_word &= False

        self.assertTrue(is_same_word, f"Wrong best word: {move_0.word} ({exp_move_0_word})")

    @measure_time
    def test_find_best_play_4(self):
        board = Board(self.dict, BOARD_ROW, BOARD_COL, PREMIUM_CELLS)
        player = ComputerPlayer(board, None, "bot")

        serialized_board = ""
        serialized_board += "     A  B  C  D  E  F  G  H  I  J  K  L  M  N  O\n"
        serialized_board += "   +----------------------------------------------+\n"
        serialized_board += " 1 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 2 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 3 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 4 | .  .  .  O  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += " 5 | .  .  .  P  .  .  .  A  .  .  .  .  .  .  .  |\n"
        serialized_board += " 6 | .  .  .  E  .  .  .  S  .  W  .  .  .  .  .  |\n"
        serialized_board += " 7 | .  .  .  R  .  P  Y  T  H  O  N  .  .  .  .  |\n"
        serialized_board += " 8 | .  .  .  A  L  A  .  R  .  R  O  L  E  .  .  |\n"
        serialized_board += " 9 | .  .  .  .  .  .  .  O  .  L  .  .  .  .  .  |\n"
        serialized_board += "10 | .  .  .  .  .  .  .  N  .  D  .  .  .  .  .  |\n"
        serialized_board += "11 | .  .  .  H  E  L  L  O  .  .  .  .  .  .  .  |\n"
        serialized_board += "12 | .  .  .  .  .  .  .  M  U  M  M  Y  .  .  .  |\n"
        serialized_board += "13 | .  .  .  .  .  .  .  Y  .  .  .  A  Y  E  .  |\n"
        serialized_board += "14 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += "15 | .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  |\n"
        serialized_board += "   +----------------------------------------------+\n"

        board.deserialize(serialized_board)
        board.enable_debug()

        player.add_tiles([TILE(letter="E"), TILE(letter="I"), TILE(letter="I"), TILE(letter="Y",), 
                          TILE(letter="A"), TILE(letter="H"), TILE(letter=" "), TILE(letter=" ",)])
        player.set_player_state(PlayerState.PLAYING)
        move_0 = player.get_possible_moves()[0]  # Get most scored move
        exp_move_0_score = 28
        exp_move_0_word = [TILE(letter="H"), TILE(letter="A"), TILE(letter="I"), TILE(letter="R"), TILE(letter="Y")]       
        board.print()
        board.print(move_0.word)
        self.assertEqual(move_0.score, exp_move_0_score, f"Wrong score: {move_0.score} ({exp_move_0_score})")

        is_same_word  = True
        for i, tile in enumerate(move_0.word):
            if tile.is_similar(exp_move_0_word[i]):
                pass
            else:
                is_same_word &= False

        self.assertTrue(is_same_word, f"Wrong best word: {move_0.word} ({exp_move_0_word})")

if __name__ == '__main__':
    unittest.main()
