from reconchess import Player
import chess
import chess.engine
import random
from collections import defaultdict
from reconchess import *
from reconchess.utilities import without_opponent_pieces, is_illegal_castle

def get_king_capture_move(board:chess.Board):
    for move in board.pseudo_legal_moves:
        if board.is_capture(move):
            captured_square = move.to_square
            captured_piece = board.piece_at(captured_square)
            if captured_piece and captured_piece.piece_type == chess.KING:
                return move
    return None

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

def generate_capture_resulting_fens(fen, capture_square_str):
    board = chess.Board(fen)
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

    return sorted(next_fens)

def generate_next_fens(fen):
    board = chess.Board(fen)
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

    return sorted(next_fens)

class RandomSensing(Player):
    def __init__(self):
        super().__init__()
        self.belief_states = []
        self.color = None
        self.engine = None
        self.turn_count = 0

        try:
            # Initialize Stockfish engine
            self.engine = chess.engine.SimpleEngine.popen_uci('/opt/stockfish/stockfish')
        except:
            # Fallback if default path doesn't work
            self.engine = chess.engine.SimpleEngine.popen_uci(r"G:\Downloads\AI-RBC-main\stockfish\stockfish.exe")

    def handle_game_start(self, color:bool, board:chess.Board, opponent_name:str):
        self.color = color
        self.board = board
        #self.belief_states = [board.fen()]     

    def handle_opponent_move_result(self, captured_my_piece:bool, capture_square: Optional[Square]):
        new_beliefs = []
        for fen in self.belief_states:
            #board = chess.Board(fen)
            
            if captured_my_piece:
                # Generate all possible FENs where opponent could have captured
                resulting_fens = generate_capture_resulting_fens(fen, capture_square)
                new_beliefs.extend(resulting_fens)
            else:
                # Generate all possible non-capture moves
                next_fens = generate_next_fens(fen)
                new_beliefs.extend(next_fens)
                
        self.belief_states = list(set(new_beliefs))  # Remove duplicates

        if captured_my_piece:
            self.board.remove_piece_at(capture_square)

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left:float) -> Square:
        #Prioritize sensing around opponent king or center squares
        targets = [chess.E4, chess.E5, chess.D4, chess.D5]
        if self.turn_count < 10:  # Early game
            targets.extend([chess.F8, chess.G8] if self.color == chess.WHITE else [chess.F1, chess.G1])
        return random.choice(sense_actions)
    
    def handle_sense_result(self, sense_result:List[Tuple[Square, Optional[chess.Piece]]]):
        """Update belief states based on sensing results with empty state handling"""
        if not self.belief_states:
            self.belief_states = [chess.STARTING_FEN]
            return
            
        # Convert sense result to window format
        window_str = ';'.join(f"{chess.SQUARE_NAMES[square]}:{piece.symbol() if piece else '?'}" 
                            for square, piece in sense_result)
        
        # Filter matching belief states
        new_beliefs = [fen for fen in self.belief_states 
                    if fen_matches_window(fen, parse_window(window_str))]
        
        if new_beliefs:
            self.belief_states = new_beliefs
        else:
            # If no beliefs match, expand from last known state
            print("Warning: No beliefs match sensing result, expanding possibilities")
            self.belief_states = generate_next_fens(random.choice(self.belief_states[:10]))  # Limit to first 10 to avoid explosion
        for square, piece in sense_result:
            if piece is None:
                self.board.remove_piece_at(square)
            else:
                self.board.set_piece_at(square,piece)

    def choose_move(self, move_actions: List[chess.Move], seconds_left:float)-> Optional[chess.Move]:

        for fen in self.belief_states:
            board = chess.Board(fen)

            # Try to capture the opponent's king
            capture_move = get_king_capture_move(board)
            if capture_move:
                return capture_move

            # Otherwise ask Stockfish
        result = self.engine.play(board, chess.engine.Limit(time=0.1))
        
        sampled_beliefs = random.sample(self.belief_states, min(5, len(self.belief_states)))

        for fen in sampled_beliefs:
            board = chess.Board(fen)

            if result in move_actions:
                return result.move
            # if move in move_counts:
            #     move_counts[move] += 1
            # else:
              #  move_counts[move] = 1

        
    
    def choose_move(self, move_actions, seconds_left):
        self.turn_count += 1
        
        # First check for king captures in any belief state
        for fen in self.belief_states:
            board = chess.Board(fen)
            king_capture = get_king_capture_move(board)
            if king_capture and king_capture.uci() in move_actions:
                # Double-check move legality
                if king_capture in board.legal_moves:
                    return king_capture
                else:
                    print(f"Warning: King capture {king_capture} not legal in position {fen}")

        # Otherwise use Stockfish on sampled belief states
        move_scores = defaultdict(int)
        sampled_beliefs = random.sample(self.belief_states, min(5, len(self.belief_states)))
        
        for fen in sampled_beliefs:
            board = chess.Board(fen)
            try:
                # Get legal moves for this specific board
                legal_moves = list(board.legal_moves)
                
                # Only consider moves that are in both legal_moves and move_actions
                valid_moves = [m for m in legal_moves if m.uci() in move_actions]
                
                if valid_moves:
                    result = self.engine.play(board, chess.engine.Limit(time=0.5), 
                                            root_moves=valid_moves)
                    if result.move and result.move.uci() in move_actions:
                        move_scores[result.move.uci()] += 1
            except Exception as e:
                print(f"Error processing {fen}: {str(e)}")
                continue

        if move_scores:
            best_move = max(move_scores.items(), key=lambda x: x[1])[0]
            return chess.Move.from_uci(best_move)
        
        # Fallback: choose randomly from legal moves
        try:
            board = chess.Board(random.choice(self.belief_states))
            legal_moves = [m for m in board.legal_moves if m.uci() in move_actions]
            return random.choice(legal_moves) if legal_moves else None
        except:
            return None # Fallback

    def handle_move_result(self, requested_move: chess.Move, taken_move:chess.Move, captured_opponent_piece:bool, capture_square:Optional[Square]):
        new_beliefs = []
        for fen in self.belief_states:
            board = chess.Board(fen)
            if taken_move:
                board.push(taken_move)
                new_beliefs.append(board.fen())
        self.belief_states = new_beliefs

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        try:
            # if the engine is already terminated then this call will throw an exception
            self.engine.quit()
        except chess.engine.EngineTerminatedError:
            pass
