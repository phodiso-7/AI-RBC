import chess
import chess.engine

def get_king_capture_move(board):
    """
    Checks if a move can capture the opponent's king.
    Returns the capturing move if found, otherwise None.
    """
    for move in board.pseudo_legal_moves:
        if board.is_capture(move):
            captured_piece_square = move.to_square
            captured_piece = board.piece_at(captured_piece_square)
            if captured_piece and captured_piece.piece_type == chess.KING:
                return move
    return None

def choose_move(fen):
    board = chess.Board(fen)

    # 1. Try to capture the opponent's king
    capture_move = get_king_capture_move(board)
    if capture_move:
        return capture_move.uci()

    # 2. Ask Stockfish to suggest a move (within 0.5 seconds)
    #engine = chess.engine.SimpleEngine.popen_uci('./stockfish', setpgrp=True)
    engine = chess.engine.SimpleEngine.popen_uci('/opt/stockfish/stockfish', setpgrp=True)

    result = engine.play(board, chess.engine.Limit(time=0.5))
    move = result.move

    engine.quit()
    return move.uci()

# === Input ===
fen_input = input().strip()
selected_move = choose_move(fen_input)
print(selected_move)
