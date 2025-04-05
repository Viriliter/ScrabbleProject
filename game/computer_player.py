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

        self._player_strategy = PlayerStrategy.BALANCED  # Computer players starts with balanced policy

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
                    # If no possible moves exist, try to find a sacrificable letter for exchange
                    letter = self.get_sacrificable_letter()
                    # If no sacrificable letter is found, then there is no best move so skip turn
                    is_success = False
                    if letter is not None:
                        is_success = self.emit("exchange_letter", self._player_id, letter)
                        # If exchange failed in some reason, then skip turn
                        if is_success:
                            self.unlock() 
                            return 

                    self.emit("skip_turn", self._player_id)
        else:
            pass
        self.unlock()

    def play_turn(self) -> Tuple[Optional[int], Optional[WORD]]:
        """
        @brief Play a turn and return the best move to play.
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
        @brief Get a list of possible moves to play.
        @return List of possible moves
        """
        return self._board.get_possible_moves(self._rack.get_rack())

    def get_sacrificable_letter(self) -> Optional[LETTER]:
        """
        @brief Get the letter that is most likely to be sacrificed.
        @param tiles: List of tiles in the rack
        @return The letter that is most likely to be sacrificed
        """
         # Filter out tiles that cannot be sacrificed
        candidate_tiles: List[TILE] = [tile for tile in self._rack.get_rack()]

        if not candidate_tiles:
            return None

        # Get letters from tiles
        letters = [tile.letter for tile in candidate_tiles]

        # Count vowels and consonants in rack
        vowel_count = sum(1 for letter in letters if letter in self._board.get_dictionary().get_vowels())
        consonant_count = len(letters) - vowel_count

        # Score each letter according to
        # 1. Points value (higher points = less likely to sacrifice)
        # 2. Frequency (more common = better to sacrifice)
        # 3. Vowel-consonant balance
        # 4. Combination potential (S, and common endings are valuable)
        # 5. Tile usage (more tiles used = less likely to sacrifice)
        tile_scores: List[Tuple[int, TILE]] = []
        for tile in candidate_tiles:
            letter = tile.letter
            # Lower score means better to sacrifice
            score = 0
            
            # 1. Points value (higher points = less likely to sacrifice)
            score -= tile.point * 2  # Weight points heavily
            
            # 2. Frequency (more common = better to sacrifice)
            score += self._board.get_dictionary().get_letter_frequency(letter)
            
            # 3. Vowel-consonant balance
            if letter in self._board.get_dictionary().get_vowels():
                # If we have many vowels, vowels become more sacrificable
                if vowel_count > consonant_count:
                    score += 5 * (vowel_count - consonant_count)
            else:
                # If we have many consonants, consonants become more sacrificable
                if consonant_count > vowel_count:
                    score += 5 * (consonant_count - vowel_count)
            
            # 4. Combination potential (S, and common endings are valuable)
            #TODO this calculation is special to English letters, make it more generic
            if letter == 'S':
                score -= 10  # S is very valuable for plurals
            elif letter == 'E':
                score += 2    # E is very common but also useful
            elif letter in {'D', 'G', 'R', 'T'}:
                score += 1    # Common endings are somewhat valuable
            
            tile_scores.append((score, tile))
        
        # Sort by score (higher score means more sacrificable)
        tile_scores.sort(reverse=True, key=lambda x: x[0])

        return tile_scores[0][1].letter if tile_scores else None

    def choose_best_move(self) -> MOVE:
        """
        @brief Choose the best move based on immediate reward and future considerations.
        @return Best move to play
        """
        possible_moves = self.get_possible_moves()
        
        if not possible_moves or len(possible_moves)==0:
            return None

        if self._player_strategy == PlayerStrategy.GREEDY:                       
            return possible_moves[0]  # First move is highest scored move
        else:
            # Evaluate each move based on immediate reward and future considerations
            scored_moves = [(move, self.evaluate_move(move)) for move in possible_moves]
            scored_moves.sort(key=lambda x: x[1], reverse=True)

            print(f"\n--- Possible Moves--- ({self._player_name}) ")
            for move, score in scored_moves:
                print(f"Word: {''.join([tile.letter for tile in move.word])} | Original score: {move.score} | Estimated Score: {score:.2f}")

            # Return highest scored move
            return scored_moves[0][0]
    
    def evaluate_move(self, move: MOVE) -> int:
        """
        @brief Evaluate a move based on immediate reward and future probabilistic future estimation.
        @param move: The move to evaluate
        @return The score of the move
        """
        self.update_knowledge()
        
        immediate_reward = move.score
        strategic_value = self.calculate_strategic_value(move)
        future_value = self.estimate_future_value(move)
        
        return immediate_reward + strategic_value + self.gamma * future_value

    def update_knowledge(self) -> None:
        """
        @brief Update knowledge of played tiles and remaining bag count
        """
        # Add tiles from our rack
        self.__observed_tiles.clear()
        for letter in self._rack.get_letters():
            self.__observed_tiles[letter] += 1
            
        # Add tiles on board
        for tile in self._board.get_locked_tiles():
            self.__observed_tiles[tile.letter] += 1
            
        self.tiles_in_bag = self._tile_bag.get_remaining_tiles()
        
    def get_tile_probability(self, letter: LETTER) -> float:
        """
        @brief Get probability that a given tile is in the bag.
        @param letter: The letter to check
        @return Probability of the letter being in the bag
        """
        
        remaining_in_bag = (self._tile_bag.get_alphabet().get(letter, (0,0))[0] - 
                           self.__observed_tiles.get(letter, 0))
        return max(0, remaining_in_bag) / self.tiles_in_bag if self.tiles_in_bag > 0 else 0
    
    def estimate_future_value(self, move: MOVE) -> float:
        """
        @brief Revised future value estimation using probabilities.
        @param move: The move to evaluate
        @return Estimated future value of the move
        """
        tiles_used = len(move.word)
        num_new_tiles = min(tiles_used, self.tiles_in_bag)
        
        if num_new_tiles == 0:
            return 0
            
        # Calculate expected value of new tiles
        total_expected_value = 0
        
        for letter, (count, _, _, _) in self._tile_bag.get_alphabet().items():
            prob = self.get_tile_probability(letter)
            total_expected_value += prob * self._tile_bag.get_alphabet().get(letter, (0,0))[1]
            
        # Adjust for multiple draws
        future_value = num_new_tiles * total_expected_value
        
        # Consider rack balance
        balance_factor = self.calculate_balance_probability()
        return future_value * balance_factor
    
    def calculate_balance_probability(self) -> float:
        """
        @brief Estimate probability of getting a balanced rack.
        @return Probability of getting a balanced rack.
        """
        # Count unseen vowels and consonants
        unseen_vowels = 0
        unseen_consonants = 0

        for tile, (total, _, _, _) in self._tile_bag.get_alphabet().items():
            remaining = total - self.__observed_tiles.get(tile, 0)
            if tile in self._board.get_dictionary().get_vowels():
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
        """
        @brief Counts how many premium squares the move exposes.
        @param move: The move to evaluate
        @return Number of opened premium squares
        """
        count = 0
        # Implementation depends on your board representation
        # For each tile placed:
        #   1. Check adjacent squares
        #   2. If placing here reveals a premium square, increment count
        return count

    def _evaluate_board_position(self, move: MOVE) -> int:
        """
        @brief Scores positional advantages.
        @param move: The move to evaluate
        @return Score based on board position
        """
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
        """
        @brief Returns tiles that will remain after the move.
        @param move: The move to evaluate
        @return List of remaining tiles in the rack
        """
        used_tiles = move.word
        remaining = [t for t in self._rack.get_rack() if not any(t.is_equal(used_tile) for used_tile in used_tiles)]
        return remaining

    def _calculate_rack_penalty(self, remaining_tiles) -> int:
        """
        @brief Penalizes bad rack compositions.
        @param remaining_tiles: The tiles remaining in the rack
        @return Total penalty for the rack
        """
        penalty = 0
        
        # 1. Count vowels
        vowel_count = sum(1 for t in remaining_tiles if t in self._board.get_dictionary().get_vowels())
        
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
            if cnt > 1 and t not in self._board.get_dictionary().get_vowels():  # Duplicate consonants worse
                penalty += 3 * (cnt - 1)
                
        # 3. Penalize high-point tiles
        high_point = {'Q', 'Z', 'X', 'J', 'K'}
        penalty += sum(4 for t in remaining_tiles if t in high_point)
        
        return penalty

    def _creates_parallel_play(self, move: MOVE) -> bool:
        """
        @brief Checks if the move creates parallel plays.
        @param move: The move to evaluate
        @return True if it creates parallel plays, False otherwise
        """
        return False
        
    def _blocks_opponent(self, move: MOVE) -> bool:
        """
        @brief Checks if the move blocks opponent's potential plays.
        @param move: The move to evaluate
        @return True if it blocks opponent, False otherwise
        """
        return False
        
    def _vowels_near_premiums(self, move: MOVE) -> bool:
        """
        @brief Checks if the move is close to premium cell.
        @param move: The move to evaluate
        @return True if vowel is near to premiums cell, False otherwise
        """
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
        
        for tile in move.word:  # Assuming each placement is (row, col, letter)
            row, col, letter = tile.row, tile.col, tile.letter
            
            # Only check vowel placements
            if letter not in self._board.get_dictionary().get_vowels():
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
