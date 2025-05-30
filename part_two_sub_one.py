import chess
import reconchess
from reconchess.utilities import without_opponent_pieces, is_illegal_castle

def generate_all_possible_moves(fen):
    board = chess.Board(fen)
    possible_moves = set()

    # 1. Add all pseudolegal moves
    for move in board.pseudo_legal_moves:
        possible_moves.add(move.uci())

    # 2. Add the null move
    possible_moves.add('0000')

    # 3. Add special castling moves permitted in RBC
    castle_board = without_opponent_pieces(board)
    for move in castle_board.generate_castling_moves():
        if not is_illegal_castle(board, move):
            possible_moves.add(move.uci())

    # 4. Output sorted list of moves
    for move in sorted(possible_moves):
        print(move)

# Sample Input
fen_input = input().strip()
generate_all_possible_moves(fen_input)
