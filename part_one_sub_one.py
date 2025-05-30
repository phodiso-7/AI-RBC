import chess

def print_board_from_fen(fen):
    board = chess.Board(fen)
    for rank in range(8, 0, -1):  # 8 to 1
        row = ""
        for file in range(8):  # a to h
            square = chess.square(file, rank - 1)
            piece = board.piece_at(square)
            row += (piece.symbol() if piece else ".") + " "
        print(row.strip())

if __name__ == "__main__":
    fen_input = input()
    print_board_from_fen(fen_input)


