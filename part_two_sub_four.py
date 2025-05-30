import chess
import reconchess
from reconchess.utilities import without_opponent_pieces, is_illegal_castle

import chess

def parse_window(window_str):
    """
    Parses the window description into a dictionary:
    {'c8': '?', 'd8': '?', ..., 'd7': 'n'}
    """
    window = {}
    entries = window_str.strip().split(';')
    for entry in entries:
        if entry:
            square, piece = entry.split(':')
            window[square] = piece
    return window

def fen_matches_window(fen, window):
    """
    Checks if the given FEN matches the window observation.
    '?' means the square must be empty.
    Any other piece letter must match exactly.
    """
    board = chess.Board(fen)
    for square_str, expected_piece in window.items():
        square = chess.parse_square(square_str)
        piece = board.piece_at(square)

        if expected_piece == '?':
            if piece is not None:
                return False  # Expected empty square
        else:
            if piece is None or piece.symbol() != expected_piece:
                return False  # Piece mismatch
    return True

def filter_fens_by_window(fens, window_str):
    window = parse_window(window_str)
    consistent_fens = [fen for fen in fens if fen_matches_window(fen, window)]
    for fen in sorted(consistent_fens):
        print(fen)

N = int(input())
fens = [input().strip() for _ in range(N)]
window_description = input().strip()

filter_fens_by_window(fens, window_description)

