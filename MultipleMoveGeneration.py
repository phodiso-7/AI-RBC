import chess
import chess.engine
import os

def get_stockfish_path():
    if os.name == 'nt':
        return r"C:\Users\bokel\OneDrive - University of Witwatersrand\Honours\COMS4033A-AI\Project\AI-RBC\stockfish.exe"
    else:
        return '/opt/stockfish/stockfish'

def find_king_capture(board):
    for move in board.pseudo_legal_moves:
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            if captured_piece and captured_piece.piece_type == chess.KING:
                return move.uci()
    return None

def evaluate_moves(fens):
    engine = chess.engine.SimpleEngine.popen_uci(get_stockfish_path(), setpgrp=True)
    move_frequency = {}

    for fen in fens:
        board = chess.Board(fen)

        # Priority 1: Capture opponent king if possible
        king_capture = find_king_capture(board)
        if king_capture:
            engine.quit()
            return king_capture

        # Otherwise: ask Stockfish
        best_move = engine.play(board, chess.engine.Limit(time=0.1)).move.uci()

        move_frequency[best_move] = move_frequency.get(best_move, 0) + 1

    engine.quit()
    return resolve_majority_vote(move_frequency)

def resolve_majority_vote(move_counts):
    if not move_counts:
        return None

    # Sort alphabetically, then by frequency
    sorted_moves = sorted(move_counts.items())
    most_common_move = max(sorted_moves, key=lambda x: x[1])[0]

    return most_common_move

def main():
    num_boards = int(input())
    fens = [input().strip() for _ in range(num_boards)]

    selected_move = evaluate_moves(fens)
    if selected_move:
        print(selected_move)

if __name__ == '__main__':
    main()
