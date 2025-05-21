import chess

def parse_window(window_str):
    window = {}
    entries = window_str.strip().split(';')
    for entry in entries:
        if entry:
            square, piece = entry.split(':')
            window[square] = piece
    return window

def fen_matches_window(fen, window):
    board = chess.Board(fen)
    for square_str, expected_piece in window.items():
        square = chess.parse_square(square_str)
        piece = board.piece_at(square)

        if expected_piece == '?':
            if piece is not None:
                return False
        else:
            # Compare symbol() — lowercase for black, uppercase for white
            if piece is None or piece.symbol() != expected_piece:
                return False
    return True

def filter_fens_by_window(fens, window_str):
    window = parse_window(window_str)
    consistent_fens = []

    for fen in fens:
        if fen_matches_window(fen, window):
            consistent_fens.append(fen)

    for fen in sorted(consistent_fens):
        print(fen)

# Read input — no prompts
N = int(input())
fens = [input().strip() for _ in range(N)]
window_description = input().strip()

filter_fens_by_window(fens, window_description)
