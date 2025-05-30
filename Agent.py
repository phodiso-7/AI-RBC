import chess.engine
import random
from reconchess import *
import os

STOCKFISH_ENV_VAR = 'STOCKFISH_EXECUTABLE'

def parse_window(window_str):
    """
    Parses the window description into a dictionary:
    {'c8': '?', 'd8': '?', ..., 'd7': 'n'}
    """
    window = {}
    entries = window_str.strip().split(';')
    for entry in entries:
        if entry:
            square, piece = entry.split(':')
            window[square] = piece
    return window

def fen_matches_window(fen, window):
    """
    Checks if the given FEN matches the window observation.
    '?' means the square must be empty.
    Any other piece letter must match exactly.
    """
    board = chess.Board(fen)
    for square_str, expected_piece in window.items():
        square = chess.parse_square(square_str)
        piece = board.piece_at(square)

        if expected_piece == '?':
            if piece is not None:
                return False  # Expected empty square
        else:
            if piece is None or piece.symbol() != expected_piece:
                return False  # Piece mismatch
    return True

def filter_fens_by_window(fens, window_str):
    window = parse_window(window_str)
    consistent_fens = [fen for fen in fens if fen_matches_window(fen, window)]
    return sorted(consistent_fens)

def get_king_capture_move(board:chess.Board, move_actions: List[chess.Move],color:bool):
    for move in move_actions:
        if board.is_capture(move):
            captured_square = move.to_square
            captured_piece = board.piece_at(captured_square)
            if captured_piece and captured_piece.piece_type == chess.KING and board.king(not color):
                return move
    return None

def generate_all_possible_moves(board:chess.Board):
    possible_moves = set()

    # 1. Add all pseudolegal moves
    for move in board.pseudo_legal_moves:
        possible_moves.add(move)

    # 2. Add the null move
    possible_moves.add(chess.Move.null())

    # 3. Add special castling moves permitted in RBC
    castle_board = without_opponent_pieces(board)
    for move in castle_board.generate_castling_moves():
        if not is_illegal_castle(board, move):
            possible_moves.add(move)

    # 4. Output sorted list of moves
    return sorted(possible_moves)
    
def generate_next_fens(board:chess.Board):
    next_fens = set()

    # 1. Pseudolegal moves
    for move in board.pseudo_legal_moves:
        new_board = board.copy()
        new_board.push(move)
        next_fens.add(new_board.fen())

    # 2. Null move (0000)
    new_board = board.copy()
    new_board.push(chess.Move.null())
    next_fens.add(new_board.fen())

    # 3. Special castling in RBC
    castle_board = without_opponent_pieces(board)
    for move in castle_board.generate_castling_moves():
        if not is_illegal_castle(board, move):
            new_board = board.copy()
            new_board.push(move)
            next_fens.add(new_board.fen())

    # Output sorted FENs
    return sorted(next_fens)

def generate_capture_resulting_fens(board:chess.Board, capture_square_str):
    target_square = chess.SQUARE_NAMES.index(capture_square_str)
    next_fens = set()

    # 1. Check all pseudolegal moves that end on the capture square
    for move in board.pseudo_legal_moves:
        if move.to_square == target_square and board.is_capture(move):
            new_board = board.copy()
            new_board.push(move)
            next_fens.add(new_board.fen())

    # 2. Special RBC castling (very rare, but handle it safely)
    castle_board = without_opponent_pieces(board)
    for move in castle_board.generate_castling_moves():
        if not is_illegal_castle(board, move):
            if move.to_square == target_square and board.is_capture(move):
                new_board = board.copy()
                new_board.push(move)
                next_fens.add(new_board.fen())

    # 3. Return sorted list
    return sorted(next_fens) 


class TroutBot(Player):
    """
    TroutBot uses the Stockfish chess engine to choose moves. In order to run TroutBot you'll need to download
    Stockfish from https://stockfishchess.org/download/ and create an environment variable called STOCKFISH_EXECUTABLE
    that is the path to the downloaded Stockfish executable.
    """

    def __init__(self):
        self.board = None
        self.color = None
        self.my_piece_captured_square = None

        # make sure stockfish environment variable exists
        if STOCKFISH_ENV_VAR not in os.environ:
            raise KeyError(
                'TroutBot requires an environment variable called "{}" pointing to the Stockfish executable'.format(
                    STOCKFISH_ENV_VAR))

        # make sure there is actually a file
        stockfish_path = os.environ[STOCKFISH_ENV_VAR]
        if not os.path.exists(stockfish_path):
            raise ValueError('No stockfish executable found at "{}"'.format(stockfish_path))

        # initialize the stockfish engine
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path, setpgrp=True)

    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        self.board = board
        self.color = color

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        # if the opponent captured our piece, remove it from our board.
        self.my_piece_captured_square = capture_square
        if captured_my_piece:
            self.board.remove_piece_at(capture_square)

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> \
            Optional[Square]:
        # if our piece was just captured, sense where it was captured
        if self.my_piece_captured_square:
            return self.my_piece_captured_square

        # if we might capture a piece when we move, sense where the capture will occur
        future_move = self.choose_move(move_actions, seconds_left)
        if future_move is not None and self.board.piece_at(future_move.to_square) is not None:
            return future_move.to_square

        # otherwise, just randomly choose a sense action, but don't sense on a square where our pieces are located
        for square, piece in self.board.piece_map().items():
            if piece.color == self.color:
                sense_actions.remove(square)
        return random.choice(sense_actions)

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        # add the pieces in the sense result to our board
        for square, piece in sense_result:
            self.board.set_piece_at(square, piece)

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        # if we might be able to take the king, try to
        enemy_king_square = self.board.king(not self.color)
        if enemy_king_square:
            # if there are any ally pieces that can take king, execute one of those moves
            enemy_king_attackers = self.board.attackers(self.color, enemy_king_square)
            if enemy_king_attackers:
                attacker_square = enemy_king_attackers.pop()
                return chess.Move(attacker_square, enemy_king_square)

        # otherwise, try to move with the stockfish chess engine
        try:
            self.board.turn = self.color
            self.board.clear_stack()
            result = self.engine.play(self.board, chess.engine.Limit(time=0.5))
            return result.move
        except chess.engine.EngineTerminatedError:
            print('Stockfish Engine died')
        except chess.engine.EngineError:
            print('Stockfish Engine bad state at "{}"'.format(self.board.fen()))

        # if all else fails, pass
        return None

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        # if a move was executed, apply it to our board
        if taken_move is not None:
            self.board.push(taken_move)

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        try:
            # if the engine is already terminated then this call will throw an exception
            self.engine.quit()
        except chess.engine.EngineTerminatedError:
            pass