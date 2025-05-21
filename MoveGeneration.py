import os
import chess
import chess.engine

def get_stockfish_path():
    if os.name == 'nt':  # Windows
        return './stockfish.exe'
    else:  # Linux/Mac (automarker)
        return '/opt/stockfish/stockfish'

def get_king_capture_move(board):
    for move in board.pseudo_legal_moves:
        if board.is_capture(move):
            target_square = move.to_square
            captured_piece = board.piece_at(target_square)
            if captured_piece and captured_piece.piece_type == chess.KING:
                return move
    return None

def choose_move(fen):
    board = chess.Board(fen)

    king_capture = get_king_capture_move(board)
    if king_capture:
        return king_capture.uci()

    engine = chess.engine.SimpleEngine.popen_uci(get_stockfish_path(), setpgrp=True)
    result = engine.play(board, chess.engine.Limit(time=0.5))
    engine.quit()

    return result.move.uci()

# Read FEN from input (no prompt)
fen_input = input().strip()
move = choose_move(fen_input)
print(move)
