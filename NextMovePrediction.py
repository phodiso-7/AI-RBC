import chess

def generate_all_possible_moves(fen):
    board = chess.Board(fen)
    possible_moves = set()

    for move in board.pseudo_legal_moves:
        possible_moves.add(move.uci())

    possible_moves.add('0000')

    # Debugging: print actual output lines
    for move in sorted(possible_moves):
        print(move)

fen_input = input().strip()
generate_all_possible_moves(fen_input)
