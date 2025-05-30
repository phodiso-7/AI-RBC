import chess
import reconchess
from reconchess.utilities import without_opponent_pieces, is_illegal_castle

import chess
from reconchess.utilities import without_opponent_pieces, is_illegal_castle

def generate_capture_resulting_fens(fen, capture_square_str):
    board = chess.Board(fen)
    target_square = chess.SQUARE_NAMES.index(capture_square_str)
    next_fens = set()

    # 1. Check all pseudolegal moves that end on the capture square
    for move in board.pseudo_legal_moves:
        if move.to_square == target_square and board.is_capture(move):
            new_board = board.copy()
            new_board.push(move)
            next_fens.add(new_board.fen())

    # 2. Special RBC castling (very rare, but handle it safely)
    castle_board = without_opponent_pieces(board)
    for move in castle_board.generate_castling_moves():
        if not is_illegal_castle(board, move):
            if move.to_square == target_square and board.is_capture(move):
                new_board = board.copy()
                new_board.push(move)
                next_fens.add(new_board.fen())

    # 3. Return sorted list
    for f in sorted(next_fens):
        print(f)

# Sample Input
fen_input = input("").strip()
capture_square_input = input().strip().lower()
generate_capture_resulting_fens(fen_input, capture_square_input)

