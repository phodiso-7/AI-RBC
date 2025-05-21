import chess

def generate_capture_resulting_fens(fen, capture_square_str):
    board = chess.Board(fen)
    target_square = chess.SQUARE_NAMES.index(capture_square_str)
    next_fens = set()

    # Add moves that capture on the specified square
    for move in board.pseudo_legal_moves:
        if move.to_square == target_square and board.is_capture(move):
            new_board = board.copy()
            new_board.push(move)
            next_fens.add(new_board.fen())

    # Print sorted FENs
    for f in sorted(next_fens):
        print(f)

# Read inputs with no prompt strings
fen_input = input().strip()
capture_square_input = input().strip().lower()
generate_capture_resulting_fens(fen_input, capture_square_input)
