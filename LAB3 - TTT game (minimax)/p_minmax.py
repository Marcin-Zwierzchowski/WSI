"""
Author: Marcin Zwierzchowski
"""

import random
import logging
from board import Board
from player import Player


class MinMaxPlayer(Player):
    def __init__(self, name: str, depth_limit: int):
        super().__init__(name)
        self.depth_limit = depth_limit
        self.clips = 0
        self.sort_moves = True

    def make_move(self, board: Board, your_side: str):
        self.clips = 0  
        _, best_move = self.minimax(board, your_side, 0, float('-inf'), float('inf'))
        print(f"Number of prunings for this move: {self.clips}")  
        return best_move

    def minimax(self, board: Board, side: str, depth: int, alpha: float, beta: float):
        # evaluate only if the depth limit is reached or there is a winner or the board is full
        # if (depth >= self.depth_limit) or (board.who_is_winner() is not None): # who_is_winner() determines if there is a winner in the current state.
        if (depth >= self.depth_limit) or (board.who_is_winner() is not None) or (not board.empty_indexes()):
            return self.evaluate(board, side), None

        if side == board.player_chars[0]:  # Maximizing player

            # print(f"Max - Side :{side}, Playing now: {board.player_chars[board.playing_now_idx]}")
            max_eval = float('-inf')
            moves = board.empty_indexes()
            # random.shuffle(moves) 

            if self.sort_moves: # Sort moves based on scoring matrix (likely better moves first). To not go through all moves, but prune ASAP.
                moves.sort(key=lambda move: self._get_scoring_matrix_value(move, board.size), reverse=True) 

            # print(f"Max player -> Moves: {moves}, scoring matrix: {self._get_scoring_matrix_value(moves[0], board.size)}")

            best_moves = []
            for move in moves:
                cloned_board = board.clone()
                cloned_board.register_move(move)

                eval_score, _ = self.minimax(cloned_board, board.player_chars[1], depth + 1, alpha, beta)


                if eval_score > max_eval:
                    max_eval = eval_score
                    # best_move = move
                    best_moves.clear()
                    best_moves.append(move)
                elif eval_score == max_eval:
                    best_moves.append(move)

                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    self.clips += 1  
                    break

                if not best_moves:
                    raise ValueError("No valid moves found")  
                
            return max_eval, random.choice(best_moves)
            # return max_eval, best_moves
        
        elif side == board.player_chars[1]:  # Minimizing player

            # print(f"Min - Side :{side}, Playing now: {board.player_chars[board.playing_now_idx]}")
            min_eval = float('inf')
            moves = board.empty_indexes()
            # random.shuffle(moves)  
            
            if self.sort_moves:# Sort moves based on scoring matrix (likely better moves first). To not go through all moves, but prune ASAP.
                moves.sort(key=lambda move: self._get_scoring_matrix_value(move, board.size), reverse=True) # Sort moves based on scoring matrix (likely better moves first)
            # print(f"Min player -> Moves: {moves}, scoring matrix: {self._get_scoring_matrix_value(moves[0], board.size)}")

            best_moves = []
            for move in moves:
                cloned_board = board.clone()
                cloned_board.register_move(move)

                eval_score, _ = self.minimax(cloned_board, board.player_chars[0], depth + 1, alpha, beta)
                
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    # best_move = move
                    best_moves.clear()
                    best_moves.append(move)
            
                elif eval_score == min_eval:
                    best_moves.append(move)

                beta = min(beta, eval_score)
                if beta <= alpha:
                    self.clips += 1  
                    break
                
                if not best_moves:
                    raise ValueError("No valid moves found") 
                
            return min_eval, random.choice(best_moves)
            # return min_eval, best_moves
        else:
            raise ValueError(f"Invalid side: {side}. Expected 'x' or 'o'.")

    def _get_scoring_matrix(self, board_size: int):
        if board_size == 3:
            scoring_matrix = [
                [3, 2, 3],
                [2, 4, 2],
                [3, 2, 3]
            ]
        elif board_size == 4:
            scoring_matrix = [
                [3, 2, 2, 3],
                [2, 3, 3, 2],
                [2, 3, 3, 2],
                [3, 2, 2, 3]
            ]

        elif board_size == 5:
            scoring_matrix = [
                [3, 2, 2, 2, 3],
                [2, 3, 3, 3, 2],
                [2, 3, 4, 3, 2],
                [2, 3, 3, 3, 2],
                [3, 2, 2, 2, 3]
            ]
        else:
            raise ValueError(f"Scoring matrix not defined for board size {board_size}")
        return scoring_matrix
    
    def _get_scoring_matrix_value(self, move: int, board_size: int):
        scoring_matrix = self._get_scoring_matrix(board_size)
        row, col = divmod(move, board_size)

        return scoring_matrix[row][col]


    def evaluate(self, board: Board, side: str): # way to evaluate terminal states
        winner = board.who_is_winner()
        if winner == side:
            return 1000
        elif winner is not None:
            return -1000
        elif not board.empty_indexes():
            return 0
        # If no winner and not full, use a scoring matrix
        
        scoring_matrix = self._get_scoring_matrix(board.size)

        score = 0
        for row in range(board.size):
            for col in range(board.size):
                index = row * board.size + col
                if board.board[index] == side:
                    score += scoring_matrix[row][col]
                elif board.board[index] != board.char_empty:
                    score -= scoring_matrix[row][col]

        return score


