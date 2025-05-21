import chess
import random
import os
from reconchess import Player
import chess.engine

class RandomSensingAgent(Player):
    def __init__(self):
        self.boards = set()
        self.engine = None
        self.color = None

    def handle_game_start(self, color, board, opponent_name):
        self.color = color
        self.boards = {board.fen()}
        self.engine = chess.engine.SimpleEngine.popen_uci('/opt/stockfish/stockfish', setpgrp=True)

    def handle_opponent_move_result(self, captured_my_piece, capture_square):
        new_boards = set()

        for fen in self.boards:
            board = chess.Board(fen)

            if board.turn != self.color:
                possible_moves = list(board.pseudo_legal_moves)

                if captured_my_piece:
                    for move in possible_moves:
                        if board.is_capture(move) and move.to_square == capture_square:
                            new_board = board.copy()
                            new_board.push(move)
                            new_boards.add(new_board.fen())
                else:
                    for move in possible_moves:
                        if not board.is_capture(move):
                            new_board = board.copy()
                            new_board.push(move)
                            new_boards.add(new_board.fen())

                # Add null move to account for unknown pass
                null_board = board.copy()
                null_board.push(chess.Move.null())
                new_boards.add(null_board.fen())

        if new_boards:
            self.boards = new_boards

    def choose_sense(self, sense_actions, move_actions, seconds_left):
        # Exclude edge squares (files a or h, ranks 1 or 8)
        valid_squares = [sq for sq in sense_actions if 0 < chess.square_file(sq) < 7 and 0 < chess.square_rank(sq) < 7]
        return random.choice(valid_squares)

    def handle_sense_result(self, sense_result):
        def matches(board, sense_result):
            for square, piece in sense_result:
                actual_piece = board.piece_at(square)
                if piece is None:
                    if actual_piece is not None:
                        return False
                else:
                    if actual_piece is None or actual_piece.symbol() != piece.symbol():
                        return False
            return True

        filtered_boards = set()
        for fen in self.boards:
            board = chess.Board(fen)
            if matches(board, sense_result):
                filtered_boards.add(fen)

        if filtered_boards:
            self.boards = filtered_boards

    def choose_move(self, move_actions, seconds_left):
        move_counts = {}

        boards = list(self.boards)
        if len(boards) > 10000:
            boards = random.sample(boards, 10000)

        for fen in boards:
            board = chess.Board(fen)

            # Try to capture opponent's king if possible
            for move in board.pseudo_legal_moves:
                if board.is_capture(move):
                    captured_piece = board.piece_at(move.to_square)
                    if captured_piece and captured_piece.piece_type == chess.KING:
                        return move

            # Ask Stockfish for move
            try:
                result = self.engine.play(board, chess.engine.Limit(time=10.0 / len(boards)))
                move = result.move
                if move in move_counts:
                    move_counts[move] += 1
                else:
                    move_counts[move] = 1
            except:
                continue

        if not move_counts:
            return None

        return sorted(move_counts.items(), key=lambda x: (-x[1], x[0]))[0][0]

    def handle_move_result(self, requested_move, taken_move, captured_opponent_piece, capture_square):
        new_boards = set()

        for fen in self.boards:
            board = chess.Board(fen)
            legal_moves = list(board.pseudo_legal_moves)

            for move in legal_moves:
                test_board = board.copy()
                test_board.push(move)
                if move == taken_move:
                    new_boards.add(test_board.fen())

        if new_boards:
            self.boards = new_boards

    def handle_game_end(self, winner_color, win_reason, game_history):
        if self.engine:
            self.engine.quit()
