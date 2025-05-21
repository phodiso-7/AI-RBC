import chess

def print_board_from_fen(fen):
    board = chess.Board(fen)
    for rank in range(8, 0, -1):
        row = []
        for file in range(8):
            square = chess.square(file, rank - 1)
            piece = board.piece_at(square)
            row.append(piece.symbol() if piece else '.')
        print(' '.join(row))

# No prompt strings, just input and output
fen_input = input().strip()
print_board_from_fen(fen_input)
