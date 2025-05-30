import chess.engine

def get_king_capture_move(board):
    for move in board.pseudo_legal_moves:
        if board.is_capture(move):
            captured_square = move.to_square
            captured_piece = board.piece_at(captured_square)
            if captured_piece and captured_piece.piece_type == chess.KING:
                return move
    return None

def choose_move(fens):
    move_counts = {}

    # Start the engine once
    engine = chess.engine.SimpleEngine.popen_uci(r"G:\Downloads\AI-RBC-main\stockfish\stockfish.exe", setpgrp=True)
    #engine = chess.engine.SimpleEngine.popen_uci('/opt/stockfish/stockfish', setpgrp=True)

    for fen in fens:
        board = chess.Board(fen)

        # Try to capture the opponent's king
        capture_move = get_king_capture_move(board)
        if capture_move:
            return capture_move.uci()

        # Otherwise ask Stockfish
        result = engine.play(board, chess.engine.Limit(time=0.1))

        move = result.move.uci()
        if move in move_counts:
            move_counts[move] += 1
        else:
            move_counts[move] = 1

    engine.quit()

    return move_counts

def main():
    N = int(input())
    fens = [input().strip() for _ in range(N)]

    move_counts = choose_move(fens)

    # Find most common move; break ties alphabetically
    most_common_move = None
    highest_count = 0

    for move in sorted(move_counts):  # Alphabetical tie-breaker
        count = move_counts[move]
        if count > highest_count:
            highest_count = count
            most_common_move = move

    print(most_common_move)

if __name__ == '__main__':
    main()
