import chess
import reconchess
from reconchess.utilities import without_opponent_pieces, is_illegal_castle

def generate_next_fens(fen):
    board = chess.Board(fen)
    next_fens = set()

    # 1. Pseudolegal moves
    for move in board.pseudo_legal_moves:
        new_board = board.copy()
        new_board.push(move)
        next_fens.add(new_board.fen())

    # 2. Null move (0000)
    new_board = board.copy()
    new_board.push(chess.Move.null())
    next_fens.add(new_board.fen())

    # 3. Special castling in RBC
    castle_board = without_opponent_pieces(board)
    for move in castle_board.generate_castling_moves():
        if not is_illegal_castle(board, move):
            new_board = board.copy()
            new_board.push(move)
            next_fens.add(new_board.fen())

    # Output sorted FENs
    for f in sorted(next_fens):
        print(f)

# Sample input
fen_input = input().strip()
generate_next_fens(fen_input)
