import chess

def execute_move(fen, move_str):
    board = chess.Board(fen)
    move = chess.Move.from_uci(move_str)
    
    if move in board.legal_moves:
        board.push(move)
        print(board.fen())
    else:
        print("Illegal move")

if __name__ == "__main__":
    fen_input = input().strip()
    move_input = input().strip()
    execute_move(fen_input, move_input)

