import chess

def generate_next_fens(fen):
    board = chess.Board(fen)
    next_fens = set()

    for move in board.pseudo_legal_moves:
        new_board = board.copy()
        new_board.push(move)
        next_fens.add(new_board.fen())

    new_board = board.copy()
    new_board.push(chess.Move.null())
    next_fens.add(new_board.fen())

    for f in sorted(next_fens):
        print(f)

fen_input = input().strip()
generate_next_fens(fen_input)
