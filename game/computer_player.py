from collections import defaultdict
from typing import List, Dict, Tuple
from dataclasses import dataclass

from .globals import *
from .utils import *
from .components import *

from .player import *

class ComputerPlayer(Player):
    def __init__(self, board: Board, tile_bag: TileBag, name=""):
        super().__init__(board, name)
        self._tile_bag = tile_bag
        self._player_name: str = name
        self._player_type: PlayerType = PlayerType.COMPUTER
        self._player_privileges: PlayerPrivileges = PlayerPrivileges.PLAYER
        self.gamma = 0.8  # Discount factor

        self.set_player_state(PlayerState.LOBBY_READY)  # Computer players gets ready automatically
        self.__observed_tiles = defaultdict(int)  # Observed tiles on game
        self.tiles_in_bag = 0  # Number of tiles in the bag

    def _listen(self, message: any) -> None:
        self.lock()  # Prevents recursive calls
        if message == GameState.WAITING_FOR_PLAYERS:
            if (self.get_player_state() == PlayerState.LOBBY_READY):
                self.emit("enter_player_to_game", self._player_id)
        elif message == GameState.PLAYER_ORDER_SELECTION:
            if (self.get_player_state() == PlayerState.WAITING_ORDER):
                letter: LETTER = self.emit("request_play_order", self._player_id)
        elif message == GameState.GAME_STARTED:
            if (self.get_player_state() == PlayerState.PLAYING):
                _, best_move_word = self.play_turn()
                if best_move_word is not None:
                    self.emit("submit", self._player_id, best_move_word)
                else:
                    self.emit("skip_turn", self._player_id)
        else:
            pass
        self.unlock()

    def play_turn(self) -> Tuple[Optional[int], Optional[WORD]]:
        """
        Play a turn and return the best move to play
        @return Score and word to play
        """
        if not (self._player_state == PlayerState.PLAYING):
            return None, None
        
        print(f"Rack of Computer player {self._player_name}: {self._rack.stringify()}")
        best_move = self.choose_best_move()
        print(f"Best move: {best_move}")
        if best_move is None or len(best_move.word) == 0:
            return None, None
        
        return best_move.score, best_move.word
    
    def get_possible_moves(self) -> List[MOVE]:
        """
        Get a list of possible moves to play
        @return List of possible moves
        """
        return self._board.get_possible_moves(self._rack.get_rack())

    def choose_best_move(self) -> MOVE:
        """
        Choose the best move based on immediate reward and future considerations
        @return Best move to play
        """
        possible_moves = self.get_possible_moves()
        
        if not possible_moves:
            return None
        
        # Evaluate each move based on immediate reward and future considerations
        best_move = max(possible_moves, key=lambda move: self.evaluate_move(move))
        
        return best_move
    
    def evaluate_move(self, move: MOVE) -> int:
        """Evaluate a move based on immediate reward and future probabilistic future estimation"""
        self.update_knowledge()
        
        immediate_reward = move.score
        strategic_value = self.calculate_strategic_value(move)
        future_value = self.estimate_future_value(move)
        
        return immediate_reward + strategic_value + self.gamma * future_value

    def update_knowledge(self) -> None:
        """Update knowledge of played tiles and remaining bag count"""
        # Add tiles from our rack
        self.__observed_tiles.clear()
        for letter in self._rack.get_letters():
            self.__observed_tiles[letter] += 1
            
        # Add tiles on board
        for tile in self._board.get_locked_tiles():
            self.__observed_tiles[tile.letter] += 1
            
        self.tiles_in_bag = self._tile_bag.get_remaining_tiles()
        
    def get_tile_probability(self, letter: LETTER) -> float:
        """Get probability that a given tile is in the bag"""
        
        remaining_in_bag = (self._tile_bag.get_alphabet().get(letter, (0,0))[0] - 
                           self.__observed_tiles.get(letter, 0))
        return max(0, remaining_in_bag) / self.tiles_in_bag if self.tiles_in_bag > 0 else 0
    
    def estimate_future_value(self, move: MOVE) -> float:
        """Revised future value estimation using probabilities"""
        tiles_used = len(move.word)
        num_new_tiles = min(tiles_used, self.tiles_in_bag)
        
        if num_new_tiles == 0:
            return 0
            
        # Calculate expected value of new tiles
        total_expected_value = 0
        
        for letter, (count, _) in self._tile_bag.get_alphabet().items():
            prob = self.get_tile_probability(letter)
            total_expected_value += prob * self._tile_bag.get_alphabet().get(letter, (0,0))[1]
            
        # Adjust for multiple draws
        future_value = num_new_tiles * total_expected_value
        
        # Consider rack balance
        balance_factor = self.calculate_balance_probability()
        return future_value * balance_factor
    
    def calculate_balance_probability(self) -> float:
        """Estimate probability of getting a balanced rack"""
        # Count unseen vowels and consonants
        unseen_vowels = 0
        unseen_consonants = 0
        
        vowels = {'A', 'E', 'I', 'O', 'U'}
        for tile, (total, _) in self._tile_bag.get_alphabet().items():
            remaining = total - self.__observed_tiles.get(tile, 0)
            if tile in vowels:
                unseen_vowels += remaining
            else:
                unseen_consonants += remaining
                
        total_unseen = unseen_vowels + unseen_consonants
        if total_unseen == 0:
            return 0.5
            
        vowel_ratio = unseen_vowels / total_unseen
        
        if 0.3 <= vowel_ratio <= 0.5:
            return 1.0
        elif 0.2 <= vowel_ratio <= 0.6:
            return 0.7
        else:
            return 0.4
    
    def calculate_strategic_value(self, move: MOVE) -> float:
        """
        @brief Calculates bonuses/penalties for strategic considerations:
        1. Tile Usage: Rewards using more tiles (especially bingos)
        2. Premium Square Control: Penalizes opening triple/double word scores
        3. Board Position: Rewards creating hooks/blocking opportunities
        4. Rack Balance: Penalizes leaving bad tile combinations
        5. Endgame: Adjusts strategy when tiles are running low
        @return Sum of all strategic bonuses/penalties
        """
        strategic_value = 0.0
        
        # 1. Tile Usage Bonus (encourage playing more tiles)
        tiles_used = len(move.word)
        strategic_value += tiles_used * 1.5  # Base bonus per tile
        
        # Bingo bonus (using all 7 tiles)
        if tiles_used == self._rack.count():
            strategic_value += 35  # Standard Scrabble bingo is 50 extra points
        
        # 2. Premium Square Control
        opened_premiums = self._count_opened_premiums(move)
        strategic_value -= opened_premiums * 2.5  # Penalize for each opened premium
        
        # 3. Board Position Analysis
        strategic_value += self._evaluate_board_position(move)
        
        # 4. Rack Balance
        remaining_tiles = self._get_remaining_rack(move)
        strategic_value -= self._calculate_rack_penalty(remaining_tiles)
        
        # 5. Endgame Adjustment (more aggressive when tiles are scarce)
        if self.tiles_in_bag < 20:  # Approaching endgame
            # Value immediate points more when few tiles remain
            strategic_value *= 0.7  
        
        return strategic_value

    def _count_opened_premiums(self, move: MOVE) -> int:
        """Counts how many premium squares the move exposes"""
        count = 0
        # Implementation depends on your board representation
        # For each tile placed:
        #   1. Check adjacent squares
        #   2. If placing here reveals a premium square, increment count
        return count

    def _evaluate_board_position(self, move: MOVE) -> int:
        """Scores positional advantages"""
        score = 0
        
        # Bonus for creating parallel plays
        if self._creates_parallel_play(move):
            score += 8
            
        # Bonus for blocking opponent's hot spots
        if self._blocks_opponent(move):
            score += 5
            
        # Penalty for placing vowels next to triple letters
        if self._vowels_near_premiums(move):
            score -= 4
            
        return score

    def _get_remaining_rack(self, move: MOVE) -> List[TILE]:
        """Returns tiles that will remain after the move"""
        used_tiles = move.word
        remaining = [t for t in self._rack.get_rack() if not any(t.is_equal(used_tile) for used_tile in used_tiles)]
        return remaining

    def _calculate_rack_penalty(self, remaining_tiles) -> int:
        """Penalizes bad rack compositions"""
        penalty = 0
        vowels = {'A', 'E', 'I', 'O', 'U'}
        
        # 1. Count vowels
        vowel_count = sum(1 for t in remaining_tiles if t in vowels)
        
        # Heavy penalty for all vowels or no vowels
        if vowel_count >= 5:
            penalty += 8
        elif vowel_count <= 1:
            penalty += 6
            
        # 2. Penalize duplicate letters
        tile_counts = {}
        for t in remaining_tiles:
            tile_counts[t] = tile_counts.get(t, 0) + 1
        for t, cnt in tile_counts.items():
            if cnt > 1 and t not in vowels:  # Duplicate consonants worse
                penalty += 3 * (cnt - 1)
                
        # 3. Penalize high-point tiles
        high_point = {'Q', 'Z', 'X', 'J', 'K'}
        penalty += sum(4 for t in remaining_tiles if t in high_point)
        
        return penalty

    def _creates_parallel_play(self, move: MOVE) -> bool:
        return False
        
    def _blocks_opponent(self, move: MOVE) -> bool:
        return False
        
    def _vowels_near_premiums(self, move: MOVE) -> bool:
        vowels = {'A', 'E', 'I', 'O', 'U'}
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
        
        for tile in move.word:  # Assuming each placement is (row, col, letter)
            row, col, letter = tile.row, tile.col, tile.letter
            
            # Only check vowel placements
            if letter not in vowels:
                continue
                
            # Check all adjacent squares
            for dr, dc in directions:
                adj_row, adj_col = row + dr, col + dc
                
                # Skip if out of bounds
                if not (0 <= adj_row < 15 and 0 <= adj_col < 15):
                    continue
                    
                # Check if adjacent cell is a premium letter square
                _, prem_type = self._board.find_nearest_premium(adj_row, adj_col)
                if prem_type in ('TL', 'DL'):  # Triple/Double Letter
                    # Check if premium square is empty
                    if self._board.is_empty(adj_row, adj_col):
                        return True
                        
            return False
