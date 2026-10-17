import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
import random
import sqlite3
import json
import os
import time
from pathlib import Path

# Light lavender and indigo theme with a coordinated chessboard.
BG_COLOR = "#EEF0FA"
HEADER_COLOR = "#252744"
SUBHEADER_COLOR = "#555D78"
ACCENT_COLOR = "#6062D8"
ACCENT_HOVER = "#5052C4"
BOARD_LIGHT = "#F5F3FC"
BOARD_DARK = "#B5B3D6"
SIDEBAR_COLOR = "#E3E6F5"
CARD_COLOR = "#F8F7FD"
DIVIDER_COLOR = "#C7CDE2"
SUCCESS_COLOR = "#18714F"
WARNING_COLOR = "#94600D"
DANGER_COLOR = "#B3384B"
GOLD_ACCENT = "#926514"
SURFACE_COLOR = "#E9E6F7"
SELECTION_COLOR = "#C9C4F4"
HIGHLIGHT_COLOR = "#6258A8"
LAST_MOVE_LIGHT = "#E5E0F7"
LAST_MOVE_DARK = "#A29BC9"
PIECE_WHITE = "#FFFCF4"
PIECE_BLACK = "#383750"
PIECE_OUTLINE = "#514B76"

# Premium control panel theme colors
APP_BG = "#EEF0FA"
PANEL_BG = "#E3E6F5"
CARD_BG = "#FAFBFF"
CARD_BORDER = "#C7CDE2"
TEXT_PRIMARY = "#252744"
TEXT_SECONDARY = "#555D78"
START_BUTTON_COLOR = "#17845D"  # Start button color
RESET_BUTTON_COLOR = "#BA4052"  # Reset button color

# --- Chess Piece Constants (Unicode) ---
PIECES = {
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
}

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# --- Piece Learning Information ---
PIECE_INFO = {
    "Pawn": {
        "name": "♙ Pawn",
        "symbol": "♙♟",
        "description": "The foot soldier. Moves forward one square, captures diagonally forward.",
        "special": "First move: Can advance two squares • Promotion at end rank",
        "color": SUCCESS_COLOR
    },
    "Rook": {
        "name": "♖ Rook",
        "symbol": "♖♜",
        "description": "The castle. Moves any number of squares horizontally or vertically.",
        "special": "Castling with king • Powerful in endgames",
        "color": ACCENT_COLOR
    },
    "Knight": {
        "name": "♘ Knight",
        "symbol": "♘♞",
        "description": "The horse. Moves in an 'L' shape: 2 squares in one direction, 1 perpendicular.",
        "special": "Only piece that can jump over others • Great for forks and tactics",
        "color": WARNING_COLOR
    },
    "Bishop": {
        "name": "♗ Bishop",
        "symbol": "♗♝",
        "description": "The diagonal mover. Travels any number of squares along diagonal lines.",
        "special": "Light or dark squared • Two bishops work well together",
        "color": "#7D439D"
    },
    "Queen": {
        "name": "♕ Queen",
        "symbol": "♕♛",
        "description": "The most powerful piece. Combines rook and bishop movement patterns.",
        "special": "Can move in all 8 directions • Most valuable piece",
        "color": DANGER_COLOR
    },
    "King": {
        "name": "♔ King",
        "symbol": "♔♚",
        "description": "The most important piece. Moves one square in any direction.",
        "special": "Must be protected at all costs • Checkmate ends the game",
        "color": WARNING_COLOR
    }
}

# --- Chess Piece Classes (OOP Structure) ---

# base class (parent class for all chess pieces)
"""Chess rules and AI, independent of Tkinter."""
import random
import copy

STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

class Piece:
    """Base class for all chess pieces."""
    def __init__(self, color, position):
        self.color = color   # 'w' or 'b'
        self.position = position  # (row, col)

    @property
    def symbol(self):
        raise NotImplementedError

    def get_legal_moves(self, game):
        raise NotImplementedError


# inheritance (this piece inherits from Piece)
class Pawn(Piece):
    @property
    def symbol(self):
        return 'P' if self.color == 'w' else 'p'

    def get_legal_moves(self, game):
        """Returns list of (row, col) squares the pawn can move to."""
        # exception handling (prevent invalid moves / states)
        if not isinstance(game, ChessGame):
            raise TypeError("get_legal_moves() requires a ChessGame instance")
        # polymorphism (movement behavior depends on piece type)
        moves = []
        start_r, start_c = self.position
        direction = -1 if self.color == 'w' else 1
        
        # Forward move (one square)
        new_r = start_r + direction
        if 0 <= new_r < 8:
            target = game.board[new_r][start_c]
            if target is None:
                moves.append((new_r, start_c))
                
                # Double-step from initial rank
                if (self.color == 'w' and start_r == 6) or (self.color == 'b' and start_r == 1):
                    new_r2 = start_r + 2 * direction
                    if 0 <= new_r2 < 8:
                        target2 = game.board[new_r2][start_c]
                        if target2 is None and game.is_path_clear(start_r, start_c, new_r2, start_c):
                            moves.append((new_r2, start_c))
        
        # Diagonal captures
        for dc in [-1, 1]:
            new_c = start_c + dc
            new_r = start_r + direction
            if 0 <= new_r < 8 and 0 <= new_c < 8:
                target = game.board[new_r][new_c]
                if target is not None and target.color != self.color:
                    moves.append((new_r, new_c))
        
        return moves


# inheritance (this piece inherits from Piece)
class Rook(Piece):
    @property
    def symbol(self):
        return 'R' if self.color == 'w' else 'r'

    def get_legal_moves(self, game):
        """Returns list of (row, col) squares the rook can move to."""
        # exception handling (prevent invalid moves / states)
        if not isinstance(game, ChessGame):
            raise TypeError("get_legal_moves() requires a ChessGame instance")
        # polymorphism (movement behavior depends on piece type)
        moves = []
        start_r, start_c = self.position
        
        # Straight directions (horizontal and vertical)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            for step in range(1, 8):
                new_r = start_r + dr * step
                new_c = start_c + dc * step
                
                if not (0 <= new_r < 8 and 0 <= new_c < 8):
                    break
                
                target = game.board[new_r][new_c]
                if target is None:
                    moves.append((new_r, new_c))
                elif target.color != self.color:
                    moves.append((new_r, new_c))
                    break
                else:
                    break
        
        return moves


# inheritance (this piece inherits from Piece)
class Knight(Piece):
    @property
    def symbol(self):
        return 'N' if self.color == 'w' else 'n'

    def get_legal_moves(self, game):
        """Returns list of (row, col) squares the knight can move to."""
        # exception handling (prevent invalid moves / states)
        if not isinstance(game, ChessGame):
            raise TypeError("get_legal_moves() requires a ChessGame instance")
        # polymorphism (movement behavior depends on piece type)
        moves = []
        start_r, start_c = self.position
        
        # All 8 L-shaped moves
        knight_offsets = [
            (-2, -1), (-2, 1), (2, -1), (2, 1),
            (-1, -2), (-1, 2), (1, -2), (1, 2)
        ]
        
        for dr, dc in knight_offsets:
            new_r = start_r + dr
            new_c = start_c + dc
            if 0 <= new_r < 8 and 0 <= new_c < 8:
                target = game.board[new_r][new_c]
                if target is None or target.color != self.color:
                    moves.append((new_r, new_c))
        
        return moves


# inheritance (this piece inherits from Piece)
class Bishop(Piece):
    @property
    def symbol(self):
        return 'B' if self.color == 'w' else 'b'

    def get_legal_moves(self, game):
        """Returns list of (row, col) squares the bishop can move to."""
        # exception handling (prevent invalid moves / states)
        if not isinstance(game, ChessGame):
            raise TypeError("get_legal_moves() requires a ChessGame instance")
        # polymorphism (movement behavior depends on piece type)
        moves = []
        start_r, start_c = self.position
        
        # Diagonal directions
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in directions:
            for step in range(1, 8):
                new_r = start_r + dr * step
                new_c = start_c + dc * step
                
                if not (0 <= new_r < 8 and 0 <= new_c < 8):
                    break
                
                target = game.board[new_r][new_c]
                if target is None:
                    moves.append((new_r, new_c))
                elif target.color != self.color:
                    moves.append((new_r, new_c))
                    break
                else:
                    break
        
        return moves


# inheritance (this piece inherits from Piece)
class Queen(Piece):
    @property
    def symbol(self):
        return 'Q' if self.color == 'w' else 'q'

    def get_legal_moves(self, game):
        """Returns list of (row, col) squares the queen can move to."""
        # exception handling (prevent invalid moves / states)
        if not isinstance(game, ChessGame):
            raise TypeError("get_legal_moves() requires a ChessGame instance")
        # polymorphism (movement behavior depends on piece type)
        moves = []
        start_r, start_c = self.position
        
        # All 8 directions (combines rook and bishop)
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Rook directions
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Bishop directions
        ]
        
        for dr, dc in directions:
            for step in range(1, 8):
                new_r = start_r + dr * step
                new_c = start_c + dc * step
                
                if not (0 <= new_r < 8 and 0 <= new_c < 8):
                    break
                
                target = game.board[new_r][new_c]
                if target is None:
                    moves.append((new_r, new_c))
                elif target.color != self.color:
                    moves.append((new_r, new_c))
                    break
                else:
                    break
        
        return moves


# inheritance (this piece inherits from Piece)
class King(Piece):
    @property
    def symbol(self):
        return 'K' if self.color == 'w' else 'k'

    def get_legal_moves(self, game):
        """Returns list of (row, col) squares the king can move to.
        Note: Castling is handled separately in is_legal_move() and make_move()."""
        # exception handling (prevent invalid moves / states)
        if not isinstance(game, ChessGame):
            raise TypeError("get_legal_moves() requires a ChessGame instance")
        # polymorphism (movement behavior depends on piece type)
        moves = []
        start_r, start_c = self.position
        
        # All 8 adjacent squares
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                
                new_r = start_r + dr
                new_c = start_c + dc
                
                if 0 <= new_r < 8 and 0 <= new_c < 8:
                    target = game.board[new_r][new_c]
                    if target is None or target.color != self.color:
                        moves.append((new_r, new_c))
        
        return moves


# --- Game Logic Class ---

class ChessGame:
    """Manages the chess board state, validates moves according to chess rules,
    and tracks game status including check, checkmate, and stalemate."""
    def __init__(self, fen=STARTING_FEN):
        if not isinstance(fen, str) or not fen.strip():
            raise ValueError('FEN must be a nonempty string')
        parts = fen.split()
        if len(parts) not in (1, 6):
            raise ValueError('FEN must contain piece placement alone or all six fields')
        self.board = self.fen_to_board(fen)
        self.current_turn = parts[1] if len(parts) > 1 else 'w'
        if self.current_turn not in ('w', 'b'):
            raise ValueError("Invalid FEN turn")
        rights = parts[2] if len(parts) > 2 else '-'
        if rights != '-' and (any(c not in 'KQkq' for c in rights) or len(set(rights)) != len(rights)):
            raise ValueError("Invalid FEN castling rights")
        self.castling_rights = dict(zip(('wK', 'wQ', 'bK', 'bQ'), (c in rights for c in 'KQkq')))
        self.en_passant_target = None
        if len(parts) > 3 and parts[3] != '-':
            self.en_passant_target = self.get_square_coords(parts[3])
            if self.en_passant_target[0] != (2 if self.current_turn == 'w' else 5):
                raise ValueError("Invalid FEN en passant target")
        self.halfmove_clock = int(parts[4]) if len(parts) > 4 else 0
        self.fullmove_number = int(parts[5]) if len(parts) > 5 else 1
        if self.halfmove_clock < 0 or self.fullmove_number < 1:
            raise ValueError("Invalid FEN move counters")
        self.move_history = []
        self.status = "In Progress"
        self.captured_by_white = []
        self.captured_by_black = []
        self.update_game_status()

    def fen_to_board(self, fen):
        classes = dict(zip('prnbqk', (Pawn, Rook, Knight, Bishop, Queen, King)))
        rows = fen.split()[0].split('/')
        if len(rows) != 8:
            raise ValueError("FEN must have eight ranks")
        board = [[None] * 8 for _ in range(8)]
        for r, rank in enumerate(rows):
            c = 0
            for char in rank:
                if char in '12345678':
                    c += int(char)
                elif char.lower() in classes and c < 8:
                    board[r][c] = classes[char.lower()]('w' if char.isupper() else 'b', (r, c))
                    c += 1
                else:
                    raise ValueError("Invalid FEN piece placement")
                if c > 8:
                    raise ValueError("FEN rank exceeds eight squares")
            if c != 8:
                raise ValueError("FEN rank must contain eight squares")
        for color in ('w', 'b'):
            if sum(isinstance(p, King) and p.color == color for row in board for p in row) != 1:
                raise ValueError("FEN must contain one king per color")
        return board

    def get_piece_color(self, piece):
        """Returns 'w' for white piece, 'b' for black, or None."""
        if not piece:
            return None
        return piece.color

    def get_square_coords(self, square_name):
        """Converts algebraic name (e.g., 'e2') to (row, col) coordinates."""
        # exception handling (prevent invalid moves / states)
        try:
            if not isinstance(square_name, str) or len(square_name) != 2 or square_name[1] not in '12345678':
                raise ValueError(f"Invalid square name format: {square_name}")
            col = "abcdefgh".index(square_name[0])
            row = 8 - int(square_name[1])
            if not (0 <= row < 8 and 0 <= col < 8):
                raise ValueError(f"Square coordinates out of bounds: {square_name}")
            return row, col
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid square name '{square_name}': {str(e)}")

    def get_square_name(self, row, col):
        """Converts (row, col) coordinates to algebraic name (e.g., 'e2')."""
        if 0 <= row < 8 and 0 <= col < 8:
            return f"{'abcdefgh'[col]}{8-row}"
        return None
    
    # --- Move Validation Functions ---
    
    def is_path_clear(self, start_r, start_c, end_r, end_c):
        """Checks if the path between start and end is clear for Rook, Bishop, Queen."""
        if not all(0 <= v < 8 for v in (start_r, start_c, end_r, end_c)):
            return False
        if start_r == end_r and start_c == end_c:
            return True
        if start_r != end_r and start_c != end_c and abs(end_r-start_r) != abs(end_c-start_c):
            return False
        dr = 0 if start_r == end_r else (1 if end_r > start_r else -1)
        dc = 0 if start_c == end_c else (1 if end_c > start_c else -1)
        
        r, c = start_r + dr, start_c + dc
        while r != end_r or c != end_c:
            if self.board[r][c]:
                return False
            r, c = r + dr, c + dc
        return True

    def is_legal_move(self, start_sq, end_sq):
        try:
            sr, sc = self.get_square_coords(start_sq)
            er, ec = self.get_square_coords(end_sq)
        except ValueError:
            return False
        piece = self.board[sr][sc]
        target = self.board[er][ec]
        if piece is None or piece.color != self.current_turn:
            return False
        if target and (target.color == piece.color or isinstance(target, King)):
            return False
        enemy = 'b' if piece.color == 'w' else 'w'
        castle = isinstance(piece, King) and sr == er and abs(ec-sc) == 2
        ep = (isinstance(piece, Pawn) and target is None and
              self.en_passant_target == (er, ec) and abs(ec-sc) == 1 and
              er-sr == (-1 if piece.color == 'w' else 1))
        if castle:
            home = 7 if piece.color == 'w' else 0
            rook_col = 7 if ec == 6 else 0
            rook = self.board[home][rook_col]
            if ((sr, sc) != (home, 4) or ec not in (2, 6) or
                not self.castling_rights.get(piece.color + ('K' if ec == 6 else 'Q')) or
                not isinstance(rook, Rook) or rook.color != piece.color or
                any(self.board[home][c] for c in (range(5, 7) if ec == 6 else range(1, 4))) or
                self.is_in_check(piece.color)):
                return False
            # Test the crossing square with the king removed from its old square.
            mid = 5 if ec == 6 else 3
            self.board[sr][sc] = None
            self.board[home][mid] = piece
            try:
                if self.is_square_attacked(home, mid, enemy):
                    return False
            finally:
                self.board[home][mid] = None
                self.board[sr][sc] = piece
        elif ep:
            captured = self.board[sr][ec]
            if not isinstance(captured, Pawn) or captured.color != enemy or sr != (3 if piece.color == 'w' else 4):
                return False
        elif (er, ec) not in piece.get_legal_moves(self):
            return False
        # Restore exact objects and coordinates even if check detection fails.
        saved_board = [row[:] for row in self.board]
        old_position = piece.position
        try:
            self.board[sr][sc] = None
            self.board[er][ec] = piece
            piece.position = (er, ec)
            if ep:
                self.board[sr][ec] = None
            if castle:
                self.board[sr][5 if ec == 6 else 3] = self.board[sr][rook_col]
                self.board[sr][rook_col] = None
            return not self.is_in_check(piece.color)
        finally:
            for row, saved in zip(self.board, saved_board):
                row[:] = saved
            piece.position = old_position

    def is_in_check(self, color):
        """Returns True if the king of 'color' is currently in check."""
        king_pos = None
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if isinstance(piece, King) and piece.color == color:
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        if not king_pos:
            # No king found; treat as in check to prevent illegal states
            return True

        return self.is_square_attacked(king_pos[0], king_pos[1], 'b' if color == 'w' else 'w')

    def is_square_attacked(self, row, col, by_color):
        """Checks if a square is attacked by any piece of 'by_color'."""
        # Directions for sliding pieces
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Rook/Queen
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Bishop/Queen
        ]

        # Knights
        knight_offsets = [
            (-2, -1), (-2, 1), (2, -1), (2, 1),
            (-1, -2), (-1, 2), (1, -2), (1, 2)
        ]

        # Pawns
        pawn_dir = -1 if by_color == 'w' else 1
        pawn_attacks = [(pawn_dir, -1), (pawn_dir, 1)]

        # 1) Knight attacks
        for dr, dc in knight_offsets:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.board[r][c]
                if piece and self.get_piece_color(piece) == by_color and isinstance(piece, Knight):
                    return True

        # 2) Pawn attacks
        for dr, dc in pawn_attacks:
            r, c = row - dr, col - dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = self.board[r][c]
                if piece and self.get_piece_color(piece) == by_color and isinstance(piece, Pawn):
                    return True

        # 3) King attacks (adjacent)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    piece = self.board[r][c]
                    if piece and self.get_piece_color(piece) == by_color and isinstance(piece, King):
                        return True

        # 4) Sliding pieces (rook/bishop/queen)
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                piece = self.board[r][c]
                if piece:
                    if self.get_piece_color(piece) == by_color:
                        if (dr == 0 or dc == 0) and (isinstance(piece, Rook) or isinstance(piece, Queen)):
                            return True
                        if (dr != 0 and dc != 0) and (isinstance(piece, Bishop) or isinstance(piece, Queen)):
                            return True
                    break
                r += dr
                c += dc

        return False
        
    def get_all_legal_moves(self, color):
        if color not in ('w', 'b'):
            raise ValueError("Invalid color")
        previous_turn = self.current_turn
        self.current_turn = color
        try:
            moves = []
            for r in range(8):
                for c in range(8):
                    piece = self.board[r][c]
                    if piece is None or piece.color != color:
                        continue
                    candidates = piece.get_legal_moves(self)
                    if isinstance(piece, King):
                        candidates += [(r, c-2), (r, c+2)]
                    if isinstance(piece, Pawn) and self.en_passant_target and color == previous_turn:
                        candidates.append(self.en_passant_target)
                    for er, ec in set(candidates):
                        start, end = self.get_square_name(r, c), self.get_square_name(er, ec)
                        if end and self.is_legal_move(start, end):
                            moves.append((start, end))
            return moves
        finally:
            self.current_turn = previous_turn

    def make_move(self, start_sq, end_sq, promotion=None):
        """Executes a move and updates the turn."""
        if self.status != "In Progress":
            return False, "Game Over"

        if not self.is_legal_move(start_sq, end_sq):
            return False, "Illegal Move"
        
        try:
            start_r, start_c = self.get_square_coords(start_sq)
            end_r, end_c = self.get_square_coords(end_sq)
        except ValueError as e:
            return False, f"Invalid square coordinates: {str(e)}"
        piece = self.board[start_r][start_c]
        target_before = self.board[end_r][end_c]
        if promotion is not None and (not isinstance(promotion, str) or promotion.upper() not in ('Q', 'R', 'B', 'N')):
            return False, "Invalid promotion: choose Q, R, B, or N"
        
        # Defaults
        prev_en_passant = self.en_passant_target
        self.en_passant_target = None

        # Handle en passant capture (only if landing on previous en passant target)
        if isinstance(piece, Pawn) and target_before is None and abs(end_c - start_c) == 1 and (end_r, end_c) == (prev_en_passant if prev_en_passant else (-1, -1)):
            cap_r = end_r + (1 if piece.color == 'w' else -1)
            captured = self.board[cap_r][end_c]
            if captured and captured.color != piece.color and isinstance(captured, Pawn):
                self.board[cap_r][end_c] = None
                target_before = captured

        # Execute the move
        piece.position = (end_r, end_c)  # Update piece position
        self.board[end_r][end_c] = piece
        self.board[start_r][start_c] = None

        # Set en passant target if pawn moved two squares
        if isinstance(piece, Pawn) and abs(end_r - start_r) == 2:
            mid_r = (start_r + end_r) // 2
            self.en_passant_target = (mid_r, end_c)

        # Record capture
        if target_before:
            if self.current_turn == 'w':
                self.captured_by_white.append(target_before.symbol)
            else:
                self.captured_by_black.append(target_before.symbol)
        # Move history update (simplified)
        self.move_history.append((start_sq, end_sq, copy.deepcopy(piece)))
        
        # ---- REAL castling execution ----
        # Execute castling by moving both king and rook to their final positions
        if isinstance(piece, King) and abs(end_c - start_c) == 2:
            if piece.color == 'w':
                if end_c == 6:  # White king side
                    rook = self.board[7][7]
                    if isinstance(rook, Rook):
                        rook.position = (7, 5)
                    self.board[7][5] = rook; self.board[7][7] = None
                else:  # White queen side
                    rook = self.board[7][0]
                    if isinstance(rook, Rook):
                        rook.position = (7, 3)
                    self.board[7][3] = rook; self.board[7][0] = None
            else:
                if end_c == 6:  # Black king side
                    rook = self.board[0][7]
                    if isinstance(rook, Rook):
                        rook.position = (0, 5)
                    self.board[0][5] = rook; self.board[0][7] = None
                else:  # Black queen side
                    rook = self.board[0][0]
                    if isinstance(rook, Rook):
                        rook.position = (0, 3)
                    self.board[0][3] = rook; self.board[0][0] = None

        # Update castling rights on king/rook move or rook capture
        if isinstance(piece, King) and piece.color == 'w':
            self.castling_rights['wK'] = False; self.castling_rights['wQ'] = False
        if isinstance(piece, King) and piece.color == 'b':
            self.castling_rights['bK'] = False; self.castling_rights['bQ'] = False
        if isinstance(piece, Rook) and piece.color == 'w' and start_r == 7 and start_c == 7:
            self.castling_rights['wK'] = False
        if isinstance(piece, Rook) and piece.color == 'w' and start_r == 7 and start_c == 0:
            self.castling_rights['wQ'] = False
        if isinstance(piece, Rook) and piece.color == 'b' and start_r == 0 and start_c == 7:
            self.castling_rights['bK'] = False
        if isinstance(piece, Rook) and piece.color == 'b' and start_r == 0 and start_c == 0:
            self.castling_rights['bQ'] = False
        # If a rook was captured on its original square, clear right
        if isinstance(target_before, Rook) and target_before.color == 'w' and end_r == 7 and end_c == 7:
            self.castling_rights['wK'] = False
        if isinstance(target_before, Rook) and target_before.color == 'w' and end_r == 7 and end_c == 0:
            self.castling_rights['wQ'] = False
        if isinstance(target_before, Rook) and target_before.color == 'b' and end_r == 0 and end_c == 7:
            self.castling_rights['bK'] = False
        if isinstance(target_before, Rook) and target_before.color == 'b' and end_r == 0 and end_c == 0:
            self.castling_rights['bQ'] = False

        # Promotion
        if isinstance(piece, Pawn) and (end_r == 0 or end_r == 7):
            promo = promotion
            if promo is None:
                promo = 'Q'
            promo = promo.upper() if piece.color == 'w' else promo.lower()
            if promo not in ['Q','R','B','N','q','r','b','n']:
                promo = 'Q' if piece.color == 'w' else 'q'
            
            # Create the promoted piece object
            promo_color = piece.color
            promo_pos = (end_r, end_c)
            if promo.upper() == 'Q':
                self.board[end_r][end_c] = Queen(promo_color, promo_pos)
            elif promo.upper() == 'R':
                self.board[end_r][end_c] = Rook(promo_color, promo_pos)
            elif promo.upper() == 'B':
                self.board[end_r][end_c] = Bishop(promo_color, promo_pos)
            elif promo.upper() == 'N':
                self.board[end_r][end_c] = Knight(promo_color, promo_pos)

        self.halfmove_clock = 0 if isinstance(piece, Pawn) or target_before else self.halfmove_clock + 1
        if self.current_turn == 'b':
            self.fullmove_number += 1
        self.current_turn = 'b' if self.current_turn == 'w' else 'w'
        self.update_game_status()
        return True, "Move Successful"

    def update_game_status(self):
        legal = self.get_all_legal_moves(self.current_turn)
        if not legal:
            if self.is_in_check(self.current_turn):
                self.status = 'White Wins!' if self.current_turn == 'b' else 'Black Wins!'
            else:
                self.status = 'Draw - Stalemate'
        elif self.is_insufficient_material():
            self.status = 'Draw - Insufficient Material'
        else:
            self.status = 'In Progress'

    def is_insufficient_material(self):
        """Recognize guaranteed dead positions without rejecting possible helpmates."""
        material = [(p, r, c) for r,row in enumerate(self.board) for c,p in enumerate(row)
                    if p is not None and not isinstance(p, King)]
        if not material:
            return True
        if len(material) == 1 and isinstance(material[0][0], (Bishop, Knight)):
            return True
        return (all(isinstance(p, Bishop) for p,r,c in material) and
                len({(r+c) % 2 for p,r,c in material}) == 1)

    def to_fen(self):
        ranks = []
        for row in self.board:
            rank, empty = '', 0
            for piece in row:
                if piece is None:
                    empty += 1
                else:
                    if empty:
                        rank += str(empty)
                        empty = 0
                    rank += piece.symbol
            if empty:
                rank += str(empty)
            ranks.append(rank)
        rights = ''.join(c for key,c in zip(('wK','wQ','bK','bQ'),'KQkq') if self.castling_rights[key]) or '-'
        ep = self.get_square_name(*self.en_passant_target) if self.en_passant_target else '-'
        return f"{'/'.join(ranks)} {self.current_turn} {rights} {ep} {self.halfmove_clock} {self.fullmove_number}"

    def copy(self):
        """Create a deep copy of the game state for AI evaluation."""
        return copy.deepcopy(self)

# --- Simple AI Player ---

class SimpleAI:
    """AI player that selects moves randomly from available legal moves."""
    def __init__(self, color):
        self.color = color

    def get_move(self, game_state):
        """Chooses a random legal move."""
        legal_moves = game_state.get_all_legal_moves(self.color)
        if legal_moves:
            return random.choice(legal_moves)
        return None # Stalemate or Checkmate

class StrongAI:
    """Advanced AI that evaluates moves and selects the best option."""
    def __init__(self, color):
        self.color = color
        # Material values: Pawn=1, Knight=3, Bishop=3, Rook=5, Queen=9, King=0
        self.piece_values = {
            'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0,
            'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0
        }

    def evaluate(self, game_state, ai_color):
        """Evaluate board position: material score + mobility score."""
        if 'Wins!' in game_state.status:
            winner = 'w' if game_state.status.startswith('White') else 'b'
            return 100000 if winner == ai_color else -100000
        if game_state.status.startswith('Draw'):
            return 0
        material_score = self._calculate_material(game_state, ai_color)
        mobility_score = self._calculate_mobility(game_state, ai_color)
        return material_score + mobility_score

    def _calculate_material(self, game_state, ai_color):
        """Calculate material difference: AI pieces - opponent pieces."""
        ai_material = 0
        opponent_material = 0
        opponent_color = 'w' if ai_color == 'b' else 'b'
        
        for row in game_state.board:
            for piece in row:
                if piece:
                    value = self.piece_values.get(piece.symbol, 0)
                    piece_color = game_state.get_piece_color(piece)
                    if piece_color == ai_color:
                        ai_material += value
                    elif piece_color == opponent_color:
                        opponent_material += value
        
        return ai_material - opponent_material

    def _calculate_mobility(self, game_state, ai_color):
        """Calculate mobility difference: AI legal moves - opponent legal moves."""
        opponent_color = 'w' if ai_color == 'b' else 'b'
        ai_moves = len(game_state.get_all_legal_moves(ai_color))
        opponent_moves = len(game_state.get_all_legal_moves(opponent_color))
        return ai_moves - opponent_moves

    def get_move(self, game_state):
        """AI move selection: Evaluates all legal moves and chooses the one with highest score.
        Uses minimax-like evaluation considering material advantage and piece mobility.
        Falls back to random selection if evaluation fails."""
        legal_moves = game_state.get_all_legal_moves(self.color)
        if not legal_moves:
            return None
        
        best_move = None
        best_score = float('-inf')
        
        for start_sq, end_sq in legal_moves:
            # Simulate the move on a copied game state to evaluate position
            game_copy = game_state.copy()
            success, _ = game_copy.make_move(start_sq, end_sq)
            
            if success:
                # Evaluate the position after the move (material + mobility)
                score = self.evaluate(game_copy, self.color)
                if score > best_score:
                    best_score = score
                    best_move = (start_sq, end_sq)
        
        # Return best move, or random if no move was evaluated successfully
        if best_move:
            return best_move
        # Safety fallback: ensure we always return a valid move from legal_moves
        if legal_moves:
            return random.choice(legal_moves)
        return None



# --- Tkinter Components ---

class GameDatabase:
    """Local SQLite saves. Only JSON data is loaded, never executable objects."""
    def __init__(self, path=None):
        if path is None:
            root = Path(os.environ.get('LOCALAPPDATA') or (Path.home() / '.local' / 'share'))
            path = root / 'SamaelChess' / 'chess_data.db'
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS games (\n                id INTEGER PRIMARY KEY, updated_at TEXT NOT NULL,\n                mode TEXT NOT NULL, status TEXT NOT NULL, payload TEXT NOT NULL)')

    def connect(self):
        # Connection context managers commit but do not close, so close explicitly.
        return self._connection()

    from contextlib import contextmanager
    @contextmanager
    def _connection(self):
        db = sqlite3.connect(str(self.path), timeout=5)
        try:
            with db:
                yield db
        finally:
            db.close()

    def save(self, game, metadata, game_id=None):
        payload = json.dumps({'version': 1, 'fen': game.to_fen(),
            'history': [(a, b, p.symbol) for a, b, p in game.move_history],
            'captured_white': game.captured_by_white,
            'captured_black': game.captured_by_black,
            'status': game.status, 'metadata': metadata})
        with self.connect() as db:
            if game_id is None:
                return db.execute("INSERT INTO games(updated_at,mode,status,payload) VALUES(strftime('%Y-%m-%dT%H:%M:%fZ','now'),?,?,?)",
                    (metadata['mode'], game.status, payload)).lastrowid
            db.execute("UPDATE games SET updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'), mode=?,status=?,payload=? WHERE id=?",
                (metadata['mode'], game.status, payload, game_id))
        return game_id

    def latest_unfinished(self):
        with self.connect() as db:
            row = db.execute("SELECT id FROM games WHERE status='In Progress' ORDER BY updated_at DESC,id DESC LIMIT 1").fetchone()
        return row[0] if row else None

    def history(self):
        with self.connect() as db:
            return db.execute('SELECT id,updated_at,mode,status,payload FROM games ORDER BY updated_at DESC,id DESC LIMIT 100').fetchall()

    def load(self, game_id):
        with self.connect() as db:
            row = db.execute('SELECT payload FROM games WHERE id=?', (game_id,)).fetchone()
        if row is None:
            raise ValueError('Saved game no longer exists')
        data = json.loads(row[0])
        if data['version'] != 1:
            raise ValueError('Unsupported saved game version')
        game = ChessGame(data['fen'])
        classes = dict(zip('prnbqk', (Pawn,Rook,Knight,Bishop,Queen,King)))
        game.move_history = [(a,b,classes[code.lower()]('w' if code.isupper() else 'b',game.get_square_coords(b)))
                             for a,b,code in data['history']]
        game.captured_by_white = data['captured_white']
        game.captured_by_black = data['captured_black']
        game.status = data['status']
        if data['metadata']['mode'] not in ('PvPPage','HumanVsAIPage'):
            raise ValueError('Invalid saved game mode')
        return game, data['metadata']


class ChessGUI(tk.Tk):
    """Main application window that manages page navigation and game state."""
    def __init__(self):
        super().__init__()
        self.title("Sam@el's Chess - Playable Edition")
        self.state("zoomed") 
        self.configure(bg=BG_COLOR)
        self.configure_theme()
        
        self.game = ChessGame() # Central game state
        self.active_page = None
        self.saved_game_id = None
        self.database = None
        self.storage_error_shown = False
        try:
            self.database = GameDatabase()
        except (OSError, sqlite3.Error) as exc:
            messagebox.showwarning('Storage unavailable', f'Games cannot be saved: {exc}')
        self.protocol('WM_DELETE_WINDOW', self.close_game)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (WelcomePage, ModeSelectionPage, PvPPage, HumanVsAIPage, LearnChessPage):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("WelcomePage")

    def configure_theme(self):
        """Match standard controls to the light lavender panels."""
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Treeview', background=CARD_BG, fieldbackground=CARD_BG,
                        foreground=TEXT_PRIMARY, borderwidth=0, rowheight=26)
        style.configure('Treeview.Heading', background=PANEL_BG,
                        foreground=TEXT_PRIMARY, relief='flat', padding=(6, 5))
        style.map('Treeview', background=[('selected', ACCENT_COLOR)],
                  foreground=[('selected', "#FFFFFF")])
        style.map('Treeview.Heading', background=[('active', SURFACE_COLOR)])
        style.configure('Vertical.TScrollbar', background=CARD_BORDER,
                        troughcolor=PANEL_BG, arrowcolor=TEXT_SECONDARY)
        self.option_add('*Entry.disabledBackground', PANEL_BG)
        self.option_add('*Entry.disabledForeground', TEXT_SECONDARY)
        self.option_add('*Button.disabledForeground', TEXT_SECONDARY)
        self.option_add('*Button.activeForeground', '#FFFFFF')
        self.option_add('*Radiobutton.activeForeground', TEXT_PRIMARY)
        self.option_add('*Radiobutton.disabledForeground', TEXT_SECONDARY)
        self.option_add('*Menubutton.activeForeground', TEXT_PRIMARY)
        self.option_add('*Menubutton.activeBackground', SURFACE_COLOR)
        self.option_add('*Menubutton.disabledForeground', TEXT_SECONDARY)
        self.option_add('*Menu.background', CARD_BG)
        self.option_add('*Menu.foreground', TEXT_PRIMARY)
        self.option_add('*Menu.activeBackground', ACCENT_COLOR)
        self.option_add('*Menu.activeForeground', '#FFFFFF')

    def save_current_game(self):
        page = self.frames.get(self.active_page)
        if not self.database or page is None or not getattr(page, 'match_started', False):
            return
        page._settle_clock()
        metadata = {'mode': self.active_page,
            'white': page.player_white_name, 'black': page.player_black_name,
            'player1': page.player1_name_var.get(), 'player2': page.player2_name_var.get(),
            'white_choice': page.white_choice_var.get(),
            'time_control': page.time_control_var.get(),
            'white_ms': page.white_time_ms, 'black_ms': page.black_time_ms,
            'difficulty': page.ai_difficulty_var.get() if hasattr(page,'ai_difficulty_var') else None}
        try:
            self.saved_game_id = self.database.save(self.game, metadata, self.saved_game_id)
            self.storage_error_shown = False
        except (OSError, sqlite3.Error) as exc:
            if not self.storage_error_shown:
                self.storage_error_shown = True
                messagebox.showwarning('Save failed', f'Your game is still playable, but could not be saved: {exc}')

    def close_game(self):
        self.save_current_game()
        self.destroy()

    def show_frame(self, page_name, reset_game=True):
        if reset_game:
            self.save_current_game()
            for page in self.frames.values():
                if hasattr(page, '_stop_timer'):
                    page._stop_timer()
                    page.match_started = False
            self.active_page = None
            self.saved_game_id = None
            self.game = ChessGame()
            if page_name in ('PvPPage','HumanVsAIPage'):
                self.frames[page_name].reset_match()
        self.frames[page_name].tkraise()

    def continue_game(self):
        if not self.database:
            messagebox.showinfo('Continue Game', 'Game storage is unavailable.')
            return
        try:
            game_id = self.database.latest_unfinished()
            if game_id is None:
                messagebox.showinfo('Continue Game', 'No unfinished saved game yet. Start a match to create one.')
                return
            game, meta = self.database.load(game_id)
        except (OSError, sqlite3.Error, ValueError, KeyError, TypeError) as exc:
            messagebox.showerror('Load failed', str(exc))
            return
        self.show_frame(meta['mode'])
        page = self.frames[meta['mode']]
        self.game = game
        self.active_page = meta['mode']
        self.saved_game_id = game_id
        page.player_white_name, page.player_black_name = meta['white'], meta['black']
        page.player1_name_var.set(meta['player1'])
        page.player2_name_var.set(meta['player2'])
        page.white_choice_var.set(meta['white_choice'])
        page.time_control_var.set(meta['time_control'])
        page.white_time_ms, page.black_time_ms = meta['white_ms'], meta['black_ms']
        page.match_started = True
        page.win_announced = False
        if hasattr(page, 'ai_difficulty_var'):
            page.ai_difficulty_var.set(meta['difficulty'])
            page.ai = StrongAI('b') if meta['difficulty'] == 'World Champion Level' else SimpleAI('b')
        for name in ('player1_entry','player2_entry','player1_radio','player2_radio','difficulty_menu','start_button'):
            widget = getattr(page, name, None)
            if widget is not None:
                widget.config(state='disabled')
        page.start_button.config(text='✅ Match Started')
        page.chessboard.selected_square = None
        page.chessboard.possible_moves = []
        page.chessboard.update_board()
        page.update_status()
        if isinstance(page, HumanVsAIPage):
            page.trigger_ai_move()

    def show_game_history(self):
        if not self.database:
            messagebox.showinfo('Game History', 'Game storage is unavailable.')
            return
        try:
            rows = self.database.history()
        except sqlite3.Error as exc:
            messagebox.showerror('History unavailable', str(exc))
            return
        window = tk.Toplevel(self)
        window.title('Saved Game History')
        window.geometry('800x400')
        window.configure(bg=BG_COLOR)
        columns = ('date','mode','players','result','moves')
        tree = ttk.Treeview(window, columns=columns, show='headings')
        for key, title in zip(columns, ('Saved (UTC)','Mode','Players','Result','Moves')):
            tree.heading(key,text=title)
            tree.column(key,width=150 if key != 'moves' else 60)
        scroll = ttk.Scrollbar(window, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right',fill='y')
        tree.pack(fill='both',expand=True)
        for game_id,date,mode,status,payload in rows:
            data = json.loads(payload)
            meta = data['metadata']
            tree.insert('', 'end', values=(date[:19].replace('T',' '),
                'vs AI' if mode == 'HumanVsAIPage' else 'vs Player',
                f"{meta['white']} / {meta['black']}",status,len(data['history'])))
        tk.Label(window,text='Continue Game resumes the most recently saved unfinished match.', bg=BG_COLOR, fg=SUBHEADER_COLOR).pack(pady=8)


class BasePage(tk.Frame):
    """Base class for all page components providing common UI styling and navigation."""
    # ... (BasePage methods remain mostly the same) ...
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def create_styled_button(self, parent, text, command, bg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, 
                             font_size=14, width=None, height=None):
        btn = tk.Button(
            parent, text=text, font=("SF Pro Display", font_size, "bold"),
            bg=bg_color, fg="white", activebackground=hover_color, activeforeground="white",
            relief="flat", bd=1, cursor="hand2",
            command=command, padx=20, pady=10,
            highlightthickness=0, highlightbackground=bg_color,
            borderwidth=1, highlightcolor=bg_color
        )
        
        if width:
            btn.configure(width=width)
        if height:
            btn.configure(height=height)
            
        def on_enter(e):
            btn.configure(bg=hover_color, highlightbackground=hover_color, highlightcolor=hover_color)
        def on_leave(e):
            btn.configure(bg=bg_color, highlightbackground=bg_color, highlightcolor=bg_color)
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn

    def create_back_button(self, target="ModeSelectionPage"):
        back_frame = tk.Frame(self, bg=BG_COLOR)
        back_frame.pack(side="bottom", fill="x", padx=30, pady=20) 
        
        btn = self.create_styled_button(
            back_frame, "← Back", 
            lambda: self.controller.show_frame(target),
            bg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER
        )
        btn.pack(side="left")

    def create_home_button(self):
        home_frame = tk.Frame(self, bg=BG_COLOR)
        home_frame.pack(side="top", fill="x", padx=30, pady=(10,5))
        
        btn = self.create_styled_button(
            home_frame, "🏠 Home",
            lambda: self.controller.show_frame("WelcomePage"),
            bg_color=RESET_BUTTON_COLOR, hover_color="#A63546",
            font_size=12
        )
        btn.pack(side="right")
        
        
class ChessBoardWidget(tk.Frame):
    """Widget for a centered, 8x8 chessboard including algebraic coordinates and interaction."""
    def __init__(self, parent, controller, square_size=80):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.square_size = square_size
        self.board_squares = {} 
        self.piece_labels = {} 
        self.selected_square = None # Stores the algebraic name of the selected square
        self.possible_moves = [] # Stores end squares for the selected piece
        self.master_page = None  # Set by parent page so we can update status
        self.move_indicators = {}  # sq_name -> indicator widget

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.outer_board_frame = tk.Frame(self, bg=BG_COLOR)
        self.outer_board_frame.grid(row=0, column=0, sticky="n") 
        
        self.draw_board()

    def draw_board(self):
        # Clear previous board
        for widget in self.outer_board_frame.winfo_children():
            widget.destroy()

        # Top captured pieces frame
        self.top_captures = tk.Frame(self.outer_board_frame, bg=BG_COLOR, height=int(self.square_size * 0.5))
        self.top_captures.pack(fill="x", pady=(0, 4))
        self.top_captures.pack_propagate(False)

        board_frame = tk.Frame(self.outer_board_frame, bg=BG_COLOR, padx=8, pady=8,
                               highlightthickness=1, highlightbackground=CARD_BORDER)
        board_frame.pack()

        # Grid configuration: 10 rows (0-9) x 10 columns (0-9)
        # Row 0: Top coordinates
        # Rows 1-8: Board squares with left/right rank labels
        # Row 9: Bottom coordinates
        # Column 0: Left rank labels
        # Columns 1-8: Board squares
        # Column 9: Right rank labels

        # Configure fixed sizes for board squares (no auto-expanding)
        board_frame.grid_rowconfigure(0, weight=0)  # Top coordinates
        for row in range(1, 9):
            board_frame.grid_rowconfigure(row, minsize=self.square_size, weight=0)  # Board rows
        board_frame.grid_rowconfigure(9, weight=0)  # Bottom coordinates

        board_frame.grid_columnconfigure(0, weight=0)  # Left rank labels
        for col in range(1, 9):
            board_frame.grid_columnconfigure(col, minsize=self.square_size, weight=0)  # Board columns
        board_frame.grid_columnconfigure(9, weight=0)  # Right rank labels

        # Top coordinate labels (a-h) - centered above board
        for col in range(8):
            tk.Label(
                board_frame, text="abcdefgh"[col],
                font=("Segoe UI", 12, "bold"),
                bg=BG_COLOR, fg=SUBHEADER_COLOR,
                anchor="center"
            ).grid(row=0, column=col+1)

        # Board squares + left/right rank labels
        for row in range(8):
            # Left rank label (1-8) - centered
            tk.Label(
                board_frame, text=str(8-row),
                font=("Segoe UI", 12, "bold"),
                bg=BG_COLOR, fg=SUBHEADER_COLOR,
                anchor="center"
            ).grid(row=row+1, column=0)

            # Board squares (8x8)
            for col in range(8):
                square_name = f"{'abcdefgh'[col]}{8-row}"
                bg_color = BOARD_LIGHT if (row + col) % 2 == 0 else BOARD_DARK

                cell = tk.Frame(board_frame, bg=bg_color, width=self.square_size, height=self.square_size)
                cell.grid(row=row+1, column=col+1, sticky="")
                cell.grid_propagate(False)

                # Vector pieces scale cleanly and need no downloaded image assets.
                label = tk.Canvas(cell, width=self.square_size, height=self.square_size,
                                  bg=bg_color, highlightthickness=0, bd=0)
                label.grid(row=0, column=0, sticky="nsew")
                cell.grid_rowconfigure(0, weight=1)
                cell.grid_columnconfigure(0, weight=1)
                
                label.bind("<Button-1>", lambda e, sq=square_name: self.handle_click(sq))
                cell.bind("<Button-1>", lambda e, sq=square_name: self.handle_click(sq))

                self.board_squares[square_name] = cell
                self.piece_labels[square_name] = label

            # Right rank label (1-8) - centered
            tk.Label(
                board_frame, text=str(8-row),
                font=("Segoe UI", 12, "bold"),
                bg=BG_COLOR, fg=SUBHEADER_COLOR,
                anchor="center"
            ).grid(row=row+1, column=9)

        # Bottom coordinate labels (a-h) - centered below board
        for col in range(8):
            tk.Label(
                board_frame, text="abcdefgh"[col],
                font=("Segoe UI", 12, "bold"),
                bg=BG_COLOR, fg=SUBHEADER_COLOR,
                anchor="center"
            ).grid(row=9, column=col+1)

        # Bottom captured pieces frame
        self.bottom_captures = tk.Frame(self.outer_board_frame, bg=BG_COLOR, height=int(self.square_size * 0.5))
        self.bottom_captures.pack(fill="x", pady=(4, 0))
        self.bottom_captures.pack_propagate(False)

        self.update_board()

    @staticmethod
    def draw_piece(canvas, code, size):
        """Draw a two-tone chess silhouette using embedded vector shapes."""
        canvas.delete('piece')
        if not code:
            return
        scale = size / 100
        fill = PIECE_WHITE if code.isupper() else PIECE_BLACK
        outline = PIECE_OUTLINE if code.isupper() else '#F0EDFF'
        detail = PIECE_OUTLINE if code.isupper() else '#D5D0ED'
        width = max(1.2, size * .021)
        def points(coords):
            return [v * scale for v in coords]
        def poly(coords, **options):
            canvas.create_polygon(*points(coords), fill=fill, outline=outline,
                                  width=width, tags='piece', **options)
        def oval(coords, color=None):
            canvas.create_oval(*points(coords), fill=fill if color is None else color,
                               outline=outline if color is None else color,
                               width=width, tags='piece')
        def line(coords):
            canvas.create_line(*points(coords), fill=detail, width=width,
                               capstyle='round', joinstyle='round', tags='piece')
        kind = code.lower()
        if kind == 'p':
            poly([43,42,57,42,57,55,65,73,35,73,43,55])
            oval([36,20,64,46])
            line([40,49,60,49])
        elif kind == 'r':
            poly([30,24,30,14,40,14,40,24,46,24,46,14,54,14,
                  54,24,60,24,60,14,70,14,70,34,62,40,62,64,
                  68,73,32,73,38,64,38,40,30,34])
            line([38,40,62,40])
            line([37,64,63,64])
        elif kind == 'n':
            poly([29,73,33,60,47,49,36,45,28,49,22,42,29,28,
                  43,18,44,9,53,17,62,13,71,29,75,49,69,73])
            line([53,27,62,37,65,52,58,66])
            oval([39,29,43,33], detail)
            line([26,42,33,42])
        elif kind == 'b':
            poly([44,45,56,45,58,59,67,73,33,73,42,59])
            poly([50,13,61,24,65,34,60,43,50,48,40,43,35,34,39,24], smooth=True)
            line([54,23,45,37])
            oval([46,8,54,16])
            line([40,53,60,53])
        elif kind == 'q':
            poly([28,29,39,43,40,25,50,40,60,25,61,43,72,29,
                  63,58,65,70,35,70,37,58])
            for x,y in ((28,26),(40,22),(50,16),(60,22),(72,26)):
                oval([x-4,y-4,x+4,y+4])
            line([37,58,63,58])
            line([36,65,64,65])
        else:  # King: cross, rounded crown, tapered body.
            poly([45,10,55,10,55,17,63,17,63,25,55,25,55,33,
                  45,33,45,25,37,25,37,17,45,17])
            poly([35,31,26,37,28,47,39,55,37,65,32,73,
                  68,73,63,65,61,55,72,47,74,37,65,31,50,38], smooth=True)
            line([38,56,62,56])
            line([37,65,63,65])
        # Shared stepped plinth gives the set a consistent visual weight.
        poly([33,72,67,72,71,79,29,79])
        poly([28,79,72,79,76,87,24,87])
        line([32,82,68,82])

    def get_square_color(self, square_name):
        """Returns the original color of the square."""
        r, c = self.controller.game.get_square_coords(square_name)
        return BOARD_LIGHT if (r + c) % 2 == 0 else BOARD_DARK

    def update_board(self):
        """Updates pieces and square colors based on game state and selection."""
        game = self.controller.game
        
        # Clear previous move indicators
        self.clear_move_indicators()

        # Clear existing highlights
        for sq in self.board_squares:
            color = self.get_square_color(sq)
            self.board_squares[sq].config(bg=color)
            if game.move_history and sq in game.move_history[-1][:2]:
                r, c = game.get_square_coords(sq)
                color = LAST_MOVE_LIGHT if (r+c) % 2 == 0 else LAST_MOVE_DARK
                self.board_squares[sq].config(bg=color)
            self.piece_labels[sq].config(bg=color)
            
            # Update piece
            r, c = game.get_square_coords(sq)
            piece = game.board[r][c]
            
            self.draw_piece(self.piece_labels[sq], piece.symbol if piece else None, self.square_size)
            if isinstance(piece, King) and game.is_in_check(piece.color):
                inset = self.square_size * .055
                self.piece_labels[sq].create_rectangle(inset, inset,
                    self.square_size-inset, self.square_size-inset,
                    outline=DANGER_COLOR, width=3, tags='hint')

        # Apply selection/highlight
        if self.selected_square:
            # Highlight selected square
            selected_color = SELECTION_COLOR
            self.board_squares[self.selected_square].config(bg=selected_color)
            self.piece_labels[self.selected_square].config(bg=selected_color)
            
            # Show dot indicators for possible moves
            for move_sq in self.possible_moves:
                mr, mc = game.get_square_coords(move_sq)
                target_piece = game.board[mr][mc]
                selected_r, selected_c = game.get_square_coords(self.selected_square)
                moving = game.board[selected_r][selected_c]
                is_capture = bool(target_piece) or (isinstance(moving, Pawn) and mc != selected_c)
                self.show_move_indicator(move_sq, is_capture)
        
        # Update captured pieces rows
        self.update_captured_pieces()

        # Inform the parent page to update status (turn, win/loss)
        if self.master_page and hasattr(self.master_page, 'update_status'):
            self.master_page.update_status()

    def clear_move_indicators(self):
        for canvas in self.piece_labels.values():
            canvas.delete('hint')
        self.move_indicators.clear()

    def show_move_indicator(self, square_name, is_capture=False):
        """Use small indigo dots and capture rings without obscuring pieces."""
        canvas = self.piece_labels.get(square_name)
        if canvas is None:
            return
        size = self.square_size
        if is_capture:
            pad = size * .075
            canvas.create_oval(pad, pad, size-pad, size-pad,
                               outline=HIGHLIGHT_COLOR, width=2.5, tags='hint')
        else:
            center, radius = size/2, size*.075
            canvas.create_oval(center-radius, center-radius, center+radius, center+radius,
                               fill=HIGHLIGHT_COLOR, outline='', tags='hint')

    def update_captured_pieces(self):
        """Render captured pieces in top (by White) and bottom (by Black)."""
        game = self.controller.game
        # Clear existing
        for child in list(self.top_captures.winfo_children()):
            child.destroy()
        for child in list(self.bottom_captures.winfo_children()):
            child.destroy()

        # Helper to render a row
        def render_row(frame, pieces_list):
            # Render small piece icons in order captured
            for code in pieces_list:
                size = max(22, int(self.square_size * .4))
                icon = tk.Canvas(frame, width=size, height=size, bg=BG_COLOR,
                                 highlightthickness=0, bd=0)
                self.draw_piece(icon, code, size)
                icon.pack(side='left', padx=1)

        # Top aligns with Black's side: show white pieces captured by Black
        render_row(self.top_captures, getattr(game, 'captured_by_black', []))
        # Bottom aligns with White's side: show black pieces captured by White
        render_row(self.bottom_captures, getattr(game, 'captured_by_white', []))

    def handle_click(self, square_name):
        """Handles the logic when a square is clicked."""
        game = self.controller.game
        page = self.master_page
        if (page is None or not page.match_started or
                self.controller.active_page != type(page).__name__):
            return
        page._settle_clock()
        if isinstance(page, HumanVsAIPage) and game.current_turn == 'b':
            return
        # Ignore clicks after game end
        if game.status != "In Progress":
            page.update_status()
            return
        try:
            r, c = game.get_square_coords(square_name)
        except ValueError:
            # Invalid square name - ignore the click
            return
        clicked_piece = game.board[r][c]
        clicked_color = game.get_piece_color(clicked_piece)
        
        if self.selected_square is None:
            # 1. No square selected, select if it's the current player's piece
            if clicked_piece and clicked_color == game.current_turn:
                self.selected_square = square_name
                
                # Calculate legal moves for the selected piece
                all_legal = game.get_all_legal_moves(game.current_turn)
                self.possible_moves = [end_sq for start_sq, end_sq in all_legal if start_sq == self.selected_square]
                
                self.update_board()
        
        elif self.selected_square == square_name:
            # 2. Clicked the same square, deselect
            self.selected_square = None
            self.possible_moves = []
            self.update_board()
            
        elif square_name in self.possible_moves:
            # 3. Clicked a legal move target, make the move
            # Check for promotion need
            try:
                start_r, start_c = game.get_square_coords(self.selected_square)
                end_r, end_c = game.get_square_coords(square_name)
            except ValueError:
                # Invalid square coordinates - reset selection
                self.selected_square = None
                self.possible_moves = []
                self.update_board()
                return
            moving_piece = game.board[start_r][start_c]
            target_piece = game.board[end_r][end_c]
            promotion_choice = None
            # Only prompt for promotion if not capturing a king
            if (
                moving_piece and isinstance(moving_piece, Pawn) and (end_r == 0 or end_r == 7)
                and not (target_piece and isinstance(target_piece, King))
            ):
                # Ask user for promotion piece
                try:
                    choice = simpledialog.askstring("Promotion", "Promote to (Q/R/B/N):", parent=self)
                    if choice:
                        promotion_choice = choice.strip().upper()[0]
                        # Validate promotion choice
                        if promotion_choice not in ['Q', 'R', 'B', 'N']:
                            promotion_choice = 'Q'  # Default to Queen if invalid
                    else:
                        promotion_choice = 'Q'  # Default to Queen if cancelled or empty
                except Exception:
                    promotion_choice = 'Q'  # Default to Queen on any exception
            
            # Promotion dialogs can remain open long enough to exhaust a clock.
            page._settle_clock()
            if game.status != 'In Progress':
                page.update_status()
                return
            # Execute the move with exception handling
            try:
                success, message = game.make_move(self.selected_square, square_name, promotion=promotion_choice)
                
                if success:
                    self.selected_square = None
                    self.possible_moves = []
                    self.update_board()
                    
                    # Trigger AI move if page is HumanVsAIPage
                    if self.master_page and isinstance(self.master_page, HumanVsAIPage) and game.current_turn == 'b' and game.status == "In Progress":
                        expected_game = game
                        page = self.master_page
                        page.after(400, lambda: page.trigger_ai_move() if self.controller.game is expected_game and self.controller.active_page == 'HumanVsAIPage' else None)
                else:
                    messagebox.showwarning("Invalid Move", f"That move is not allowed: {message}")
            except Exception as e:
                messagebox.showerror("Move Error", f"An error occurred while making the move: {str(e)}")
                
        elif clicked_piece and clicked_color == game.current_turn:
            # 4. Clicked a different piece of the same color, change selection
            self.selected_square = square_name
            all_legal = game.get_all_legal_moves(game.current_turn)
            self.possible_moves = [end_sq for start_sq, end_sq in all_legal if start_sq == self.selected_square]
            self.update_board()
            
        else:
            # 5. Clicked an empty or opponent square that is not a legal move target, deselect
            self.selected_square = None
            self.possible_moves = []
            self.update_board()


class WelcomePage(BasePage):
    """Welcome screen displaying the app title, features, and start button."""
    # ... (WelcomePage remains the same) ...
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        main_frame = tk.Frame(self, bg=BG_COLOR)
        main_frame.pack(expand=True, fill="both")
        header_frame = tk.Frame(main_frame, bg=BG_COLOR)
        header_frame.pack(fill="x", pady=(80, 40))
        title_label = tk.Label(
            header_frame, text="Sam@el's Chess",
            font=("SF Pro Display", 48, "bold"), bg=BG_COLOR, fg=HEADER_COLOR
        )
        title_label.pack(pady=(0, 10))
        subtitle_label = tk.Label(
            header_frame, text="PREMIUM CHESS EXPERIENCE",
            font=("SF Pro Display", 16, "bold"), bg=BG_COLOR, fg=GOLD_ACCENT
        )
        subtitle_label.pack()
        tagline_label = tk.Label(
            header_frame, text="It's now time to relax, time to play, and time to learn…",
            font=("SF Pro Display", 16), bg=BG_COLOR, fg=SUBHEADER_COLOR
        )
        tagline_label.pack(pady=(20, 0))
        features_frame = tk.Frame(main_frame, bg=BG_COLOR)
        features_frame.pack(pady=40)
        features = ["🎯 Multiple Game Modes", "🤖 Simple AI Opponent", "📚 Interactive Learning", "⚡ Modern Interface"]
        for i in range(0, len(features), 2):
            row_frame = tk.Frame(features_frame, bg=BG_COLOR)
            row_frame.pack(pady=8)
            for j in range(2):
                if i + j < len(features):
                    feature_label = tk.Label(
                        row_frame, text=features[i + j], font=("Segoe UI", 16),
                        bg=BG_COLOR, fg=SUBHEADER_COLOR
                    )
                    feature_label.pack(side="left", padx=50)
        button_frame = tk.Frame(main_frame, bg=BG_COLOR)
        button_frame.pack(pady=60)
        start_btn = self.create_styled_button(
            button_frame, "🚀 START PLAYING", 
            lambda: controller.show_frame("ModeSelectionPage"),
            font_size=20, width=18, height=2
        )
        start_btn.pack()
        self.create_styled_button(button_frame, 'Continue Game', controller.continue_game).pack(pady=(12, 6))
        self.create_styled_button(button_frame, 'Game History', controller.show_game_history).pack()

        exit_button = tk.Button(
            self,
            text="Exit Game",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#D9534F",   # soft red exit color
            activebackground="#C9302C",
            activeforeground="white",
            command=self.controller.close_game
        )
        exit_button.pack(anchor="se", padx=20, pady=20)

class ModeSelectionPage(BasePage):
    """Page for selecting game mode: Player vs Player, Human vs AI, or Learn Chess."""
    # ... (ModeSelectionPage remains the same) ...
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.create_home_button()
        main_frame = tk.Frame(self, bg=BG_COLOR)
        main_frame.pack(expand=True, fill="both", padx=40, pady=10) 
        header_label = tk.Label(
            main_frame, text="Choose Your Game Mode",
            font=("SF Pro Display", 32, "bold"), bg=BG_COLOR, fg=HEADER_COLOR
        )
        header_label.pack(pady=(10, 20)) 
        cards_container = tk.Frame(main_frame, bg=BG_COLOR)
        cards_container.pack(expand=True, fill="both")
        cards_container.grid_columnconfigure(0, weight=1)
        game_modes = [
            { "title": "Player vs Player", "description": "Challenge a friend in classic chess battle", "icon": "👥", "page": "PvPPage", "color": SUCCESS_COLOR },
            { "title": "Human vs AI", "description": "Test your skills against the Simple AI", "icon": "🤖", "page": "HumanVsAIPage", "color": ACCENT_COLOR },
            { "title": "Learn Chess", "description": "Master the game with interactive tutorials", "icon": "📚", "page": "LearnChessPage", "color": WARNING_COLOR }
        ]
        for i, mode in enumerate(game_modes):
            self.create_mode_card(cards_container, mode, i) 

    def create_mode_card(self, parent, mode_info, index):
        card_frame = tk.Frame(parent, bg=CARD_COLOR, relief="raised", bd=0)
        card_frame.grid(row=index, column=0, pady=8, padx=60, sticky="ew") 
        inner_frame = tk.Frame(card_frame, bg=CARD_COLOR, bd=1, relief="solid", highlightbackground=GOLD_ACCENT, highlightthickness=1)
        inner_frame.pack(fill="both", expand=True, padx=2, pady=2)
        content_frame = tk.Frame(inner_frame, bg=CARD_COLOR)
        content_frame.pack(fill="both", expand=True, padx=30, pady=15) 
        header_frame = tk.Frame(content_frame, bg=CARD_COLOR)
        header_frame.pack(fill="x", pady=(0, 10))
        icon_label = tk.Label(
            header_frame, text=mode_info["icon"],
            font=("SF Pro Display", 36), bg=CARD_COLOR, fg=GOLD_ACCENT
        )
        icon_label.pack(side="left")
        text_frame = tk.Frame(header_frame, bg=CARD_COLOR)
        text_frame.pack(side="left", fill="x", expand=True, padx=(20, 0))
        title_label = tk.Label(
            text_frame, text=mode_info["title"],
            font=("SF Pro Display", 18, "bold"), bg=CARD_COLOR, fg=HEADER_COLOR
        )
        title_label.pack(anchor="w")
        desc_label = tk.Label(
            text_frame, text=mode_info["description"],
            font=("SF Pro Text", 12), bg=CARD_COLOR, fg=SUBHEADER_COLOR
        )
        desc_label.pack(anchor="w", pady=(5, 0))
        button_frame = tk.Frame(content_frame, bg=CARD_COLOR)
        button_frame.pack(fill="x")
        play_btn = self.create_styled_button(
            button_frame, f"PLAY NOW →",
            lambda: self.controller.show_frame(mode_info["page"]),
            bg_color=mode_info["color"], font_size=12, width=12 
        )
        play_btn.pack(side="right")

## ---------------------------------------------------------------------- ##

class PvPPage(BasePage):
    """Player vs Player game interface with board, controls, and move history."""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.create_home_button()

        # Player config state
        self.player1_name_var = tk.StringVar(value="Player 1")
        self.player2_name_var = tk.StringVar(value="Player 2")
        # 'p1' means Player 1 is White, 'p2' means Player 2 is White
        self.white_choice_var = tk.StringVar(value="p1")
        self.player_white_name = "Player 1"
        self.player_black_name = "Player 2"
        self.match_started = False  # Track if match has been started
        # Time control state
        self.time_control_var = tk.StringVar(value="No Time Limit")
        self.white_time_ms = None
        self.black_time_ms = None
        self.timer_job = None
        self.active_clock = None  # 'w' or 'b'
        self._clock_started_at = None
        self.win_announced = False

        # Set page background
        self.config(bg=APP_BG)
        
        main_container = tk.PanedWindow(self, orient="horizontal", bg=APP_BG, sashwidth=0)
        main_container.pack(fill="both", expand=True, padx=20, pady=(0,10)) 

        left_panel = tk.Frame(main_container, bg=PANEL_BG, width=300)
        main_container.add(left_panel, minsize=280)

        right_panel = tk.Frame(main_container, bg=APP_BG)
        main_container.add(right_panel, minsize=600)
        
        # UI elements
        self.turn_label = None
        self.status_label = None

        self.setup_game_controls(left_panel)
        self.create_chessboard_display(right_panel)
        self.create_back_button()
        
        self.update_status()

    def create_home_button(self):
        """Override to create 'Back to Menu' button instead of Home button."""
        home_frame = tk.Frame(self, bg=BG_COLOR)
        home_frame.pack(side="top", fill="x", padx=30, pady=(10,5))
        
        btn = self.create_styled_button(
            home_frame, "← Back to Menu",
            lambda: self.controller.show_frame("ModeSelectionPage"),
            bg_color=RESET_BUTTON_COLOR, hover_color="#A63546",
            font_size=12
        )
        btn.pack(side="right")

    def setup_game_controls(self, panel):
        # (1) PLAYERS SECTION - Card-like block
        players_frame = tk.Frame(panel, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER, bd=0, relief="flat", padx=12, pady=10)
        players_frame.pack(fill="x", pady=(10, 10))
        
        # Header label
        tk.Label(
            players_frame, text="Players",
            font=("Segoe UI", 14, "bold"), bg=CARD_BG, fg=TEXT_PRIMARY
        ).pack(anchor="w", padx=10, pady=(6, 4))
        
        # Two columns using .grid()
        players_grid = tk.Frame(players_frame, bg=CARD_BG)
        players_grid.pack(fill="x", padx=10, pady=(0, 6))
        
        # Column 0
        tk.Label(players_grid, text="Player 1 Name", bg=CARD_BG, fg=TEXT_SECONDARY, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 2))
        self.player1_entry = tk.Entry(players_grid, textvariable=self.player1_name_var, bg=PANEL_BG, fg=TEXT_PRIMARY, bd=0, insertbackground=TEXT_PRIMARY, state="normal")
        self.player1_entry.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(0, 4))
        self.player1_radio = tk.Radiobutton(players_grid, text="White", variable=self.white_choice_var, value="p1", bg=CARD_BG, fg=TEXT_PRIMARY, selectcolor=CARD_BG, activebackground=CARD_BG, font=("Segoe UI", 10))
        self.player1_radio.grid(row=2, column=0, sticky="w", padx=(0, 8))
        
        # Column 1
        tk.Label(players_grid, text="Player 2 Name", bg=CARD_BG, fg=TEXT_SECONDARY, font=("Segoe UI", 10)).grid(row=0, column=1, sticky="w", padx=(8, 0), pady=(0, 2))
        self.player2_entry = tk.Entry(players_grid, textvariable=self.player2_name_var, bg=PANEL_BG, fg=TEXT_PRIMARY, bd=0, insertbackground=TEXT_PRIMARY, state="normal")
        self.player2_entry.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(0, 4))
        self.player2_radio = tk.Radiobutton(players_grid, text="White", variable=self.white_choice_var, value="p2", bg=CARD_BG, fg=TEXT_PRIMARY, selectcolor=CARD_BG, activebackground=CARD_BG, font=("Segoe UI", 10))
        self.player2_radio.grid(row=2, column=1, sticky="w", padx=(8, 0))
        
        players_grid.columnconfigure(0, weight=1)
        players_grid.columnconfigure(1, weight=1)
        
        # (2) CONTROL BAR - All in one horizontal row
        controls_frame = tk.Frame(panel, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER, bd=0, relief="flat", padx=12, pady=10)
        controls_frame.pack(fill="x", pady=(10, 10))
        
        controls_row = tk.Frame(controls_frame, bg=CARD_BG)
        controls_row.pack(fill="x", padx=0, pady=0)
        
        # Left: Time Control OptionMenu
        tc_label = tk.Label(controls_row, text="Time Control", bg=CARD_BG, fg=TEXT_SECONDARY, font=("Segoe UI", 10))
        tc_label.pack(side="left", expand=True, padx=4)
        tc_menu = tk.OptionMenu(controls_row, self.time_control_var, "No Time Limit", "5 Minutes", "10 Minutes", "30 Minutes")
        tc_menu.config(bg=PANEL_BG, fg=TEXT_PRIMARY)
        tc_menu.pack(side="left", expand=True, padx=4)
        
        # Center: Swap Sides button wrapper
        swap_wrapper = tk.Frame(controls_row, bg=CARD_BG)
        swap_wrapper.pack(side="left", expand=True, padx=4, pady=4)
        swap_btn = tk.Button(
            swap_wrapper, text="⇄ Swap Sides",
            command=self.swap_sides,
            bd=0, relief="flat", highlightthickness=0,
            padx=14, pady=8,
            font=("Segoe UI", 11, "bold"),
            fg="white", bg=ACCENT_COLOR, activebackground=ACCENT_HOVER
        )
        swap_btn.pack()
        def swap_enter(e): swap_wrapper.config(bg=ACCENT_COLOR)
        def swap_leave(e): swap_wrapper.config(bg=CARD_BG)
        swap_btn.bind("<Enter>", swap_enter)
        swap_btn.bind("<Leave>", swap_leave)
        swap_wrapper.bind("<Enter>", swap_enter)
        swap_wrapper.bind("<Leave>", swap_leave)
        
        # Right: Start Match button wrapper
        start_wrapper = tk.Frame(controls_row, bg=CARD_BG)
        start_wrapper.pack(side="left", expand=True, padx=4, pady=4)
        self.start_button = tk.Button(
            start_wrapper, text="✅ Start Match",
            command=self.start_match,
            bd=0, relief="flat", highlightthickness=0,
            padx=14, pady=6,
            font=("Segoe UI", 11, "bold"),
            fg="white", bg=START_BUTTON_COLOR, activebackground="#126C4C"
        )
        self.start_button.pack()
        def start_enter(e): start_wrapper.config(bg=START_BUTTON_COLOR)
        def start_leave(e): start_wrapper.config(bg=CARD_BG)
        self.start_button.bind("<Enter>", start_enter)
        self.start_button.bind("<Leave>", start_leave)
        start_wrapper.bind("<Enter>", start_enter)
        start_wrapper.bind("<Leave>", start_leave)
        
        # (3) GAME STATUS SECTION
        status_frame = tk.Frame(panel, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER, bd=0, relief="flat", padx=12, pady=10)
        status_frame.pack(fill="x", pady=(10, 10))
        
        # Header label
        tk.Label(
            status_frame, text="Game Status",
            font=("Segoe UI", 14, "bold"), bg=CARD_BG, fg=TEXT_PRIMARY
        ).pack(anchor="w", padx=10, pady=(6, 4))
        
        # Content
        status_content = tk.Frame(status_frame, bg=CARD_BG)
        status_content.pack(fill="x", padx=10, pady=(0, 6))
        
        self.turn_label = tk.Label(
            status_content, text="Turn: White (w)", font=("Segoe UI", 12, "bold"),
            bg=CARD_BG, fg=TEXT_PRIMARY
        )
        self.turn_label.pack(pady=(4, 2))
        
        self.status_label = tk.Label(
            status_content, text="Status: In Progress", font=("Segoe UI", 10),
            bg=CARD_BG, fg=TEXT_SECONDARY
        )
        self.status_label.pack(pady=(2, 4))
        
        # Clocks (preserving clock logic)
        clocks_row = tk.Frame(status_content, bg=CARD_BG)
        clocks_row.pack(fill="x", pady=(0, 2))
        self.white_clock_label = tk.Label(clocks_row, text="White: --:--", font=("Courier New", 12, "bold"), bg=CARD_BG, fg=TEXT_PRIMARY)
        self.white_clock_label.pack(side="left")
        self.black_clock_label = tk.Label(clocks_row, text="Black: --:--", font=("Courier New", 12, "bold"), bg=CARD_BG, fg=TEXT_PRIMARY)
        self.black_clock_label.pack(side="right")
        
        # (4) RESET BUTTON
        reset_frame = tk.Frame(panel, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER, bd=0, relief="flat", padx=12, pady=10)
        reset_frame.pack(fill="x", pady=(10, 10))
        
        reset_wrapper = tk.Frame(reset_frame, bg=CARD_BG)
        reset_wrapper.pack(pady=4)
        reset_btn = tk.Button(
            reset_wrapper, text="🔄 Reset Game",
            command=self.reset_match,
            bd=0, relief="flat", highlightthickness=0,
            padx=14, pady=6,
            font=("Segoe UI", 11, "bold"),
            fg="white", bg=RESET_BUTTON_COLOR, activebackground="#A63546"
        )
        reset_btn.pack()
        def reset_enter(e): reset_wrapper.config(bg=RESET_BUTTON_COLOR)
        def reset_leave(e): reset_wrapper.config(bg=CARD_BG)
        reset_btn.bind("<Enter>", reset_enter)
        reset_btn.bind("<Leave>", reset_leave)
        reset_wrapper.bind("<Enter>", reset_enter)
        reset_wrapper.bind("<Leave>", reset_leave)
        
        # (5) MOVE HISTORY SECTION - Fill remaining space
        history_frame = tk.Frame(panel, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER, bd=0, relief="flat", padx=12, pady=10)
        history_frame.pack(fill="both", expand=True, pady=(10, 10))
        
        # Header label
        tk.Label(
            history_frame, text="Move History",
            font=("Segoe UI", 14, "bold"), bg=CARD_BG, fg=TEXT_PRIMARY
        ).pack(anchor="w", padx=10, pady=(6, 4))
        
        # Content
        history_content = tk.Frame(history_frame, bg=CARD_BG)
        history_content.pack(fill="both", expand=True, padx=10, pady=(0, 6))
        
        self.move_table = ttk.Treeview(history_content, columns=("white", "black"), show="headings", height=10)
        self.move_table.heading("white", text="White")
        self.move_table.heading("black", text="Black")
        self.move_table.column("white", width=120, anchor="center")
        self.move_table.column("black", width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(history_content, orient="vertical", command=self.move_table.yview)
        self.move_table.configure(yscrollcommand=scrollbar.set)
        
        self.move_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Initialize move list storage
        self.move_list = []

    def create_chessboard_display(self, panel):
        board_container = tk.Frame(panel, bg=BG_COLOR)
        board_container.pack(side="top", anchor="n", padx=40, pady=(0,0)) 
        self.chessboard = ChessBoardWidget(board_container, self.controller, square_size=72) 
        self.chessboard.master_page = self
        self.chessboard.pack(anchor="n", expand=False, pady=(0,0)) 
        
    def update_status(self):
        """Updates the status and history labels."""
        self.controller.save_current_game()
        game = self.controller.game
        # Determine player names based on color
        white_name = getattr(self, 'player_white_name', 'White')
        black_name = getattr(self, 'player_black_name', 'Black')
        turn_text = f"{white_name} (White)" if game.current_turn == 'w' else f"{black_name} (Black)"
        turn_color = SUCCESS_COLOR if game.current_turn == 'w' else HEADER_COLOR
        
        if self.turn_label:
            self.turn_label.config(text=f"Turn: {turn_text}", fg=turn_color)
        
        if self.status_label:
            status_text = game.status
            if status_text.endswith("Wins!"):
                # Map winner color to player name
                if status_text.startswith("White"):
                    status_text = f"{white_name} Wins!"
                elif status_text.startswith("Black"):
                    status_text = f"{black_name} Wins!"
            status_color = SUCCESS_COLOR if game.status == "In Progress" else DANGER_COLOR
            self.status_label.config(text=f"Status: {status_text}", fg=status_color)

        # Clocks and timer handling
        self._update_clock_labels()
        if game.status == "In Progress":
            self._ensure_timer_for_turn(game.current_turn)
        else:
            self._stop_timer()

        # Winner popup once
        if game.status != "In Progress" and 'Wins!' in game.status and not self.win_announced:
            self.win_announced = True
            try:
                winner_text = f"{white_name} Wins!" if game.status.startswith('White') else f"{black_name} Wins!"
                messagebox.showinfo("Game Over", winner_text)
            except Exception:
                pass

        if hasattr(self, 'move_table'):
            # Rebuild move list from game history
            p1_name = self.player1_name_var.get().strip() or "Player 1"
            p2_name = self.player2_name_var.get().strip() or "Player 2"
            p1_color = 'w' if self.white_choice_var.get() == 'p1' else 'b'
            
            self.move_list = []
            for i, move in enumerate(game.move_history):
                start_sq, end_sq, piece = move
                mover_color = piece.color
                move_txt = f"{piece.symbol}:{start_sq}-{end_sq}"
                
                if mover_color == 'w':
                    # White move - start new row
                    self.move_list.append([move_txt, ""])
                else:
                    # Black move - add to last row
                    if self.move_list:
                        self.move_list[-1][1] = move_txt
                    else:
                        self.move_list.append(["", move_txt])
            
            # Update table
            self.move_table.delete(*self.move_table.get_children())
            for white, black in self.move_list:
                self.move_table.insert("", "end", values=(white, black))

    def start_match(self):
        """Apply player names and sides, then start a fresh game with White to move."""
        # If already started, do nothing
        if hasattr(self, 'match_started') and self.match_started:
            return
        
        p1 = self.player1_name_var.get().strip() or "Player 1"
        p2 = self.player2_name_var.get().strip() or "Player 2"
        if self.white_choice_var.get() == 'p1':
            self.player_white_name = p1
            self.player_black_name = p2
        else:
            self.player_white_name = p2
            self.player_black_name = p1

        # Mark as started and disable name fields, radio buttons, and start button
        self.match_started = True
        if hasattr(self, 'player1_entry'):
            self.player1_entry.config(state="disabled")
        if hasattr(self, 'player2_entry'):
            self.player2_entry.config(state="disabled")
        if hasattr(self, 'player1_radio'):
            self.player1_radio.config(state="disabled")
        if hasattr(self, 'player2_radio'):
            self.player2_radio.config(state="disabled")
        if hasattr(self, 'start_button'):
            self.start_button.config(state="disabled")
            self.start_button.config(text="✅ Match Started")

        self.controller.active_page = type(self).__name__
        self.controller.saved_game_id = None
        # Fresh game
        self.controller.game = ChessGame()
        self.controller.game.current_turn = 'w'
        # Initialize time control
        self._init_time_control()
        # Repaint board and labels
        self.chessboard.update_board()
        self.update_status()
        self.win_announced = False

    def reset_match(self):
        """Reset the game state and restore UI to pre-start state."""
        self.controller.save_current_game()
        self.controller.active_page = None
        self.controller.saved_game_id = None
        # Stop timer completely - cancel any running after() callbacks
        self._stop_timer()
        
        # Reset game state
        self.controller.game = ChessGame()
        self.controller.game.current_turn = 'w'
        self.chessboard.selected_square = None
        self.chessboard.possible_moves = []
        self.chessboard.update_board()
        
        # Reset time control dropdown to default
        self.time_control_var.set("No Time Limit")
        
        # Reset timer state variables
        self.white_time_ms = None
        self.black_time_ms = None
        self.active_clock = None
        
        # Update clock labels to show default state
        self._update_clock_labels()
        
        # Clear name fields
        self.player1_name_var.set("")
        self.player2_name_var.set("")
        
        # Re-enable name entry fields
        if hasattr(self, 'player1_entry'):
            self.player1_entry.config(state="normal")
        if hasattr(self, 'player2_entry'):
            self.player2_entry.config(state="normal")
        
        # Re-enable radio buttons
        if hasattr(self, 'player1_radio'):
            self.player1_radio.config(state="normal")
        if hasattr(self, 'player2_radio'):
            self.player2_radio.config(state="normal")
        
        # Re-enable start button
        if hasattr(self, 'start_button'):
            self.start_button.config(state="normal")
            self.start_button.config(text="✅ Start Match")
        
        # Reset match started flag
        self.match_started = False
        
        # Clear move history
        if hasattr(self, 'move_table'):
            self.move_table.delete(*self.move_table.get_children())
            self.move_list = []
        
        self.update_status()
        self.win_announced = False

    def swap_sides(self):
        """Swap which player is White/Black. Only works when game hasn't started."""
        # Only allow swap if game hasn't started
        if hasattr(self, 'match_started') and self.match_started:
            return
        
        # Toggle radio selection
        current = self.white_choice_var.get()
        self.white_choice_var.set('p2' if current == 'p1' else 'p1')
        
        # Update internal player name mappings based on current name values
        p1 = self.player1_name_var.get().strip() or "Player 1"
        p2 = self.player2_name_var.get().strip() or "Player 2"
        if self.white_choice_var.get() == 'p1':
            self.player_white_name = p1
            self.player_black_name = p2
        else:
            self.player_white_name = p2
            self.player_black_name = p1

    # ----- Time Control Helpers -----
    def _minutes_to_ms(self, minutes):
        return int(minutes * 60 * 1000)

    def _init_time_control(self):
        self._stop_timer()
        choice = self.time_control_var.get()
        if choice == "5 Minutes":
            base = self._minutes_to_ms(5)
        elif choice == "10 Minutes":
            base = self._minutes_to_ms(10)
        elif choice == "30 Minutes":
            base = self._minutes_to_ms(30)
        else:
            base = None
        self.white_time_ms = base
        self.black_time_ms = base
        self.active_clock = None
        self._update_clock_labels()

    def _format_ms(self, ms):
        if ms is None:
            return "--:--"
        if ms < 0:
            ms = 0
        total_seconds = ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def _update_clock_labels(self):
        if hasattr(self, 'white_clock_label'):
            self.white_clock_label.config(text=f"White: {self._format_ms(self.white_time_ms)}")
        if hasattr(self, 'black_clock_label'):
            self.black_clock_label.config(text=f"Black: {self._format_ms(self.black_time_ms)}")

    def _ensure_timer_for_turn(self, turn_color):
        if self.controller.active_page != type(self).__name__ or not self.match_started:
            self._stop_timer()
            return
        if self.white_time_ms is None or self.black_time_ms is None:
            self._stop_timer()
            return
        if self.active_clock != turn_color:
            self._stop_timer()
            self.active_clock = turn_color
            self._clock_started_at = time.monotonic()
            self._schedule_tick()

    def _schedule_tick(self):
        self.timer_job = self.after(1000, self._tick)

    def _stop_timer(self):
        self._settle_clock()
        if self.timer_job is not None:
            try:
                self.after_cancel(self.timer_job)
            except Exception:
                pass
            self.timer_job = None
        self.active_clock = None

    def _settle_clock(self):
        started = getattr(self, '_clock_started_at', None)
        if self.active_clock is None or started is None:
            return
        now = time.monotonic()
        elapsed = max(0, int((now - started) * 1000))
        self._clock_started_at = started + elapsed / 1000
        game = self.controller.game
        if game.status != 'In Progress':
            return
        field = 'white_time_ms' if self.active_clock == 'w' else 'black_time_ms'
        remaining = getattr(self, field)
        if remaining is None:
            return
        remaining = max(0, remaining - elapsed)
        setattr(self, field, remaining)
        if remaining == 0:
            winner = 'b' if self.active_clock == 'w' else 'w'
            # A bare king cannot deliver mate, even if the opponent flags.
            can_mate = any(p and p.color == winner and not isinstance(p, King)
                           for row in game.board for p in row)
            game.status = ('White Wins!' if winner == 'w' else 'Black Wins!') if can_mate else 'Draw - Timeout / No Mating Material'

    def _tick(self):
        self.timer_job = None
        game = self.controller.game
        if self.controller.active_page != type(self).__name__ or game.status != 'In Progress':
            self._stop_timer()
            return
        self._settle_clock()
        self._update_clock_labels()
        self.controller.save_current_game()
        if game.status != 'In Progress':
            self.update_status()
            return
        self._schedule_tick()

## ---------------------------------------------------------------------- ##

class HumanVsAIPage(PvPPage):
    """Player vs AI game interface where human plays as White and AI plays as Black."""
    def __init__(self, parent, controller):
        # Initialize AI difficulty state BEFORE super().__init__() calls setup_game_controls()
        self.ai_difficulty_var = tk.StringVar(value="Club Level")
        self.ai = None  # Will be initialized when match starts
        
        # Initialize as PvPPage, but we'll override setup_game_controls
        super().__init__(parent, controller)
        
        # Start White's turn (Human)
        self.update_status()
    
    def setup_game_controls(self, panel):
        """Override to show simple text labels for Human vs AI mode."""
        # (1) PLAYERS SECTION - Simple text labels
        players_frame = tk.Frame(panel, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER, bd=0, relief="flat", padx=12, pady=10)
        players_frame.pack(fill="x", pady=(10, 10))
        
        # Title label
        tk.Label(
            players_frame, text="Human vs AI",
            font=("Segoe UI", 14, "bold"), bg=CARD_BG, fg=TEXT_PRIMARY
        ).pack(anchor="center", padx=10, pady=(6, 4))
        
        # Subtitle label
        tk.Label(
            players_frame, text="You are white and AI is black",
            font=("Segoe UI", 11), bg=CARD_BG, fg=TEXT_SECONDARY
        ).pack(anchor="center", padx=10, pady=(0, 8))
        
        # AI Difficulty row
        ai_row = tk.Frame(players_frame, bg=CARD_BG)
        ai_row.pack(fill="x", padx=10, pady=(4, 6))
        tk.Label(ai_row, text="AI Difficulty", bg=CARD_BG, fg=TEXT_SECONDARY, font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
        self.difficulty_menu = tk.OptionMenu(ai_row, self.ai_difficulty_var, "Club Level", "World Champion Level")
        self.difficulty_menu.config(bg=PANEL_BG, fg=TEXT_PRIMARY, font=("Segoe UI", 10))
        self.difficulty_menu.pack(side="left", fill="x", expand=True)
        
        # (2) CONTROL BAR - All in one horizontal row
        controls_frame = tk.Frame(panel, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER, bd=0, relief="flat", padx=12, pady=10)
        controls_frame.pack(fill="x", pady=(10, 10))
        
        controls_row = tk.Frame(controls_frame, bg=CARD_BG)
        controls_row.pack(fill="x", padx=0, pady=0)
        
        # Left: Time Control OptionMenu
        tc_label = tk.Label(controls_row, text="Time Control", bg=CARD_BG, fg=TEXT_SECONDARY, font=("Segoe UI", 10))
        tc_label.pack(side="left", expand=True, padx=4)
        tc_menu = tk.OptionMenu(controls_row, self.time_control_var, "No Time Limit", "5 Minutes", "10 Minutes", "30 Minutes")
        tc_menu.config(bg=PANEL_BG, fg=TEXT_PRIMARY)
        tc_menu.pack(side="left", expand=True, padx=4)
        
        # Right: Start Match button wrapper
        start_wrapper = tk.Frame(controls_row, bg=CARD_BG)
        start_wrapper.pack(side="left", expand=True, padx=4, pady=4)
        self.start_button = tk.Button(
            start_wrapper, text="✅ Start Match",
            command=self.start_match,
            bd=0, relief="flat", highlightthickness=0,
            padx=14, pady=6,
            font=("Segoe UI", 11, "bold"),
            fg="white", bg=START_BUTTON_COLOR, activebackground="#126C4C"
        )
        self.start_button.pack()
        def start_enter(e): start_wrapper.config(bg=START_BUTTON_COLOR)
        def start_leave(e): start_wrapper.config(bg=CARD_BG)
        self.start_button.bind("<Enter>", start_enter)
        self.start_button.bind("<Leave>", start_leave)
        start_wrapper.bind("<Enter>", start_enter)
        start_wrapper.bind("<Leave>", start_leave)
        
        # (3) GAME STATUS SECTION
        status_frame = tk.Frame(panel, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER, bd=0, relief="flat", padx=12, pady=10)
        status_frame.pack(fill="x", pady=(10, 10))
        
        # Header label
        tk.Label(
            status_frame, text="Game Status",
            font=("Segoe UI", 14, "bold"), bg=CARD_BG, fg=TEXT_PRIMARY
        ).pack(anchor="w", padx=10, pady=(6, 4))
        
        # Content
        status_content = tk.Frame(status_frame, bg=CARD_BG)
        status_content.pack(fill="x", padx=10, pady=(0, 6))
        
        self.turn_label = tk.Label(
            status_content, text="Turn: White (w)", font=("Segoe UI", 12, "bold"),
            bg=CARD_BG, fg=TEXT_PRIMARY
        )
        self.turn_label.pack(pady=(4, 2))
        
        self.status_label = tk.Label(
            status_content, text="Status: In Progress", font=("Segoe UI", 10),
            bg=CARD_BG, fg=TEXT_SECONDARY
        )
        self.status_label.pack(pady=(2, 4))
        
        # Clocks (preserving clock logic)
        clocks_row = tk.Frame(status_content, bg=CARD_BG)
        clocks_row.pack(fill="x", pady=(0, 2))
        self.white_clock_label = tk.Label(clocks_row, text="White: --:--", font=("Courier New", 12, "bold"), bg=CARD_BG, fg=TEXT_PRIMARY)
        self.white_clock_label.pack(side="left")
        self.black_clock_label = tk.Label(clocks_row, text="Black: --:--", font=("Courier New", 12, "bold"), bg=CARD_BG, fg=TEXT_PRIMARY)
        self.black_clock_label.pack(side="right")
        
        # (4) RESET BUTTON
        reset_frame = tk.Frame(panel, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER, bd=0, relief="flat", padx=12, pady=10)
        reset_frame.pack(fill="x", pady=(10, 10))
        
        reset_wrapper = tk.Frame(reset_frame, bg=CARD_BG)
        reset_wrapper.pack(pady=4)
        reset_btn = tk.Button(
            reset_wrapper, text="🔄 Reset Game",
            command=self.reset_match,
            bd=0, relief="flat", highlightthickness=0,
            padx=14, pady=6,
            font=("Segoe UI", 11, "bold"),
            fg="white", bg=RESET_BUTTON_COLOR, activebackground="#A63546"
        )
        reset_btn.pack()
        def reset_enter(e): reset_wrapper.config(bg=RESET_BUTTON_COLOR)
        def reset_leave(e): reset_wrapper.config(bg=CARD_BG)
        reset_btn.bind("<Enter>", reset_enter)
        reset_btn.bind("<Leave>", reset_leave)
        reset_wrapper.bind("<Enter>", reset_enter)
        reset_wrapper.bind("<Leave>", reset_leave)
        
        # (5) MOVE HISTORY SECTION - Fill remaining space
        history_frame = tk.Frame(panel, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER, bd=0, relief="flat", padx=12, pady=10)
        history_frame.pack(fill="both", expand=True, pady=(10, 10))
        
        # Header label
        tk.Label(
            history_frame, text="Move History",
            font=("Segoe UI", 14, "bold"), bg=CARD_BG, fg=TEXT_PRIMARY
        ).pack(anchor="w", padx=10, pady=(6, 4))
        
        # Content
        history_content = tk.Frame(history_frame, bg=CARD_BG)
        history_content.pack(fill="both", expand=True, padx=10, pady=(0, 6))
        
        self.move_table = ttk.Treeview(history_content, columns=("white", "black"), show="headings", height=10)
        self.move_table.heading("white", text="White")
        self.move_table.heading("black", text="Black")
        self.move_table.column("white", width=120, anchor="center")
        self.move_table.column("black", width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(history_content, orient="vertical", command=self.move_table.yview)
        self.move_table.configure(yscrollcommand=scrollbar.set)
        
        self.move_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Initialize move list storage
        self.move_list = []
    
    def start_match(self):
        """Start a fresh game with AI based on selected difficulty."""
        # If already started, do nothing
        if hasattr(self, 'match_started') and self.match_started:
            return
        
        # Set player names (human is always White, AI is always Black)
        self.player_white_name = "You"
        self.player_black_name = "AI"
        
        # Initialize AI based on difficulty (AI is always Black)
        ai_color = 'b'
        difficulty = self.ai_difficulty_var.get()
        if difficulty == "Club Level":
            self.ai = SimpleAI(ai_color)
        elif difficulty == "World Champion Level":
            self.ai = StrongAI(ai_color)
        else:
            self.ai = SimpleAI(ai_color)  # Default fallback
        
        # Mark as started and disable difficulty dropdown and start button
        self.match_started = True
        if hasattr(self, 'difficulty_menu'):
            self.difficulty_menu.config(state="disabled")
        if hasattr(self, 'start_button'):
            self.start_button.config(state="disabled")
            self.start_button.config(text="✅ Match Started")

        self.controller.active_page = type(self).__name__
        self.controller.saved_game_id = None
        # Fresh game - start with white's turn
        self.controller.game = ChessGame()
        self.controller.game.current_turn = 'w'  # White always starts in chess
        # Initialize time control
        self._init_time_control()
        # Repaint board and labels
        self.chessboard.update_board()
        self.update_status()
        self.win_announced = False
    
    def reset_match(self):
        """Reset the game state and restore UI to pre-start state."""
        self.controller.save_current_game()
        self.controller.active_page = None
        self.controller.saved_game_id = None
        # Stop timer completely - cancel any running after() callbacks
        self._stop_timer()
        
        # Reset game state
        self.controller.game = ChessGame()
        self.controller.game.current_turn = 'w'
        self.chessboard.selected_square = None
        self.chessboard.possible_moves = []
        self.chessboard.update_board()
        
        # Reset time control dropdown to default
        self.time_control_var.set("No Time Limit")
        
        # Reset timer state variables
        self.white_time_ms = None
        self.black_time_ms = None
        self.active_clock = None
        
        # Update clock labels to show default state
        self._update_clock_labels()
        
        # Re-enable difficulty dropdown
        if hasattr(self, 'difficulty_menu'):
            self.difficulty_menu.config(state="normal")
        
        # Re-enable start button
        if hasattr(self, 'start_button'):
            self.start_button.config(state="normal")
            self.start_button.config(text="✅ Start Match")
        
        # Reset match started flag
        self.match_started = False
        
        # Clear AI
        self.ai = None
        
        # Clear move history
        if hasattr(self, 'move_table'):
            self.move_table.delete(*self.move_table.get_children())
            self.move_list = []
        
        self.update_status()
        self.win_announced = False
    
    def update_status(self):
        """Override to handle history display for Human vs AI mode."""
        self.controller.save_current_game()
        game = self.controller.game
        # Determine player names based on color
        white_name = getattr(self, 'player_white_name', 'You')
        black_name = getattr(self, 'player_black_name', 'AI')
        turn_text = f"{white_name} (White)" if game.current_turn == 'w' else f"{black_name} (Black)"
        turn_color = SUCCESS_COLOR if game.current_turn == 'w' else HEADER_COLOR
        
        if self.turn_label:
            self.turn_label.config(text=f"Turn: {turn_text}", fg=turn_color)
        
        if self.status_label:
            status_text = game.status
            if status_text.endswith("Wins!"):
                # Map winner color to player name
                if status_text.startswith("White"):
                    status_text = f"{white_name} Wins!"
                elif status_text.startswith("Black"):
                    status_text = f"{black_name} Wins!"
            status_color = SUCCESS_COLOR if game.status == "In Progress" else DANGER_COLOR
            self.status_label.config(text=f"Status: {status_text}", fg=status_color)

        # Clocks and timer handling
        self._update_clock_labels()
        if game.status == "In Progress":
            self._ensure_timer_for_turn(game.current_turn)
        else:
            self._stop_timer()

        # Winner popup once
        if game.status != "In Progress" and 'Wins!' in game.status and not self.win_announced:
            self.win_announced = True
            try:
                winner_text = f"{white_name} Wins!" if game.status.startswith('White') else f"{black_name} Wins!"
                messagebox.showinfo("Game Over", winner_text)
            except Exception:
                pass

        if hasattr(self, 'move_table'):
            # Rebuild move list from game history
            self.move_list = []
            for i, move in enumerate(game.move_history):
                start_sq, end_sq, piece = move
                mover_color = piece.color
                move_txt = f"{piece.symbol}:{start_sq}-{end_sq}"
                
                if mover_color == 'w':
                    # White move - start new row
                    self.move_list.append([move_txt, ""])
                else:
                    # Black move - add to last row
                    if self.move_list:
                        self.move_list[-1][1] = move_txt
                    else:
                        self.move_list.append(["", move_txt])
            
            # Update table
            self.move_table.delete(*self.move_table.get_children())
            for white, black in self.move_list:
                self.move_table.insert("", "end", values=(white, black))
            
    def trigger_ai_move(self):
        """Called after the human player makes a move."""
        game = self.controller.game
        
        if self.controller.active_page != 'HumanVsAIPage' or not self.match_started:
            return
        # Safety check: ensure AI is initialized
        if not hasattr(self, 'ai') or self.ai is None:
            return
        
        if game.current_turn == self.ai.color and game.status == "In Progress":
            # Update AI status label while thinking
            if self.turn_label:
                self.turn_label.config(text="AI Thinking...", fg=WARNING_COLOR)
                self.update_idletasks() # Paint without processing nested game input
            
            # Schedule AI move execution with delay to simulate thinking
            expected_game = game
            self.after(800, lambda: self._execute_ai_move() if self.controller.game is expected_game and self.controller.active_page == 'HumanVsAIPage' else None)
    
    def _execute_ai_move(self):
        """Helper method to execute the AI move after delay."""
        game = self.controller.game
        
        if self.controller.active_page != 'HumanVsAIPage' or not self.match_started:
            return
        self._settle_clock()
        # Safety check: ensure AI is still initialized and it's still AI's turn
        if not hasattr(self, 'ai') or self.ai is None:
            return
        
        if game.current_turn != self.ai.color or game.status != "In Progress":
            # Game state changed, don't execute move
            self.update_status()
            return
        
        try:
            ai_move = self.ai.get_move(game)
            
            if ai_move:
                start_sq, end_sq = ai_move
                try:
                    success, message = game.make_move(start_sq, end_sq)
                    if not success:
                        messagebox.showwarning("AI Move Failed", f"AI attempted an invalid move: {message}")
                        # Update status even if move failed
                        self.update_status()
                        return
                    self.chessboard.update_board()
                except Exception as e:
                    messagebox.showerror("AI Move Error", f"An error occurred during AI move: {str(e)}")
                    self.update_status()
                    return
            else:
                # No legal moves left for AI
                if self.status_label:
                    self.status_label.config(text="Stalemate or Checkmate", fg=DANGER_COLOR)
            
            # Update UI status back to normal
            self.update_status()
        except Exception as e:
            messagebox.showerror("AI Error", f"An error occurred while AI was thinking: {str(e)}")
            # Ensure status is updated even on error
            if self.turn_label:
                self.turn_label.config(text="AI Error", fg=DANGER_COLOR)
            self.update_status()
            
    # The chessboard's handle_click automatically calls this page's update_status
    # and then uses self.master.after to call trigger_ai_move.

## ---------------------------------------------------------------------- ##

class ScrollableFrame(tk.Frame):
    """Helper class for creating vertically scrollable content areas."""
    def __init__(self, parent):
        super().__init__(parent, bg=BG_COLOR)
        
        # Canvas and scrollbar
        self.canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0, bd=0)
        self.vscroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=BG_COLOR)
        
        # Create window for inner frame
        self.inner_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        
        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=self.vscroll.set)
        
        # Layout
        self.vscroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Bind inner frame configure to update scroll region
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Sync inner width with canvas width
        def _sync_width(event):
            self.canvas.itemconfigure(self.inner_window, width=self.canvas.winfo_width())
        self.canvas.bind("<Configure>", _sync_width)
        
        # Mouse wheel support
        self._mousewheel_enabled = False
    
    def enable_mousewheel(self, widget):
        """Enable mouse wheel scrolling for the widget."""
        def on_scroll(event):
            # Normalize scroll delta for different platforms
            if event.num == 4 or event.num == 5:
                # Linux
                delta = -1 if event.num == 4 else 1
            else:
                # Windows/Mac
                delta = -1 if event.delta > 0 else 1
                # Normalize to scroll one unit at a time
                delta = delta * (120 // abs(event.delta)) if event.delta != 0 else delta
            
            self.canvas.yview_scroll(int(delta), "units")
        
        def on_enter(event):
            self.canvas.bind_all("<MouseWheel>", on_scroll)
            self.canvas.bind_all("<Button-4>", on_scroll)
            self.canvas.bind_all("<Button-5>", on_scroll)
        
        def on_leave(event):
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        self._mousewheel_enabled = True

class LearnChessPage(BasePage):
    """Educational page displaying chess piece information and basic rules."""
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        # Header frame at the top (outside scrollable area)
        header_frame = tk.Frame(self, bg=BG_COLOR)
        header_frame.pack(fill="x", pady=(10, 5), padx=20)
        
        # Configure grid with 3 columns: [Title/Subtitle] [expanding space] [Home button]
        header_frame.columnconfigure(0, weight=0)
        header_frame.columnconfigure(1, weight=1)
        header_frame.columnconfigure(2, weight=0)
        
        # Left side: Title and subtitle in column 0
        title_area = tk.Frame(header_frame, bg=BG_COLOR)
        title_area.grid(row=0, column=0, sticky="w")
        
        tk.Label(
            title_area, text="📚 Learn Chess Fundamentals",
            font=("Segoe UI", 24, "bold"), bg=BG_COLOR, fg=HEADER_COLOR
        ).pack(anchor="w", pady=(0, 4))
        
        tk.Label(
            title_area, text="Master the 6 pieces with this comprehensive guide",
            font=("Segoe UI", 12), bg=BG_COLOR, fg=SUBHEADER_COLOR
        ).pack(anchor="w")
        
        # Right side: Home button in column 2
        buttons_area = tk.Frame(header_frame, bg=BG_COLOR)
        buttons_area.grid(row=0, column=2, sticky="e")
        
        home_btn = self.create_styled_button(
            buttons_area, "← Back to Menu",
            lambda: self.controller.show_frame("ModeSelectionPage"),
            bg_color=RESET_BUTTON_COLOR, hover_color="#A63546", font_size=12
        )
        home_btn.pack(pady=(0, 5))
        
        # Scrollable content container
        scroll_container = tk.Frame(self, bg=BG_COLOR)
        scroll_container.pack(fill="both", expand=True, padx=40, pady=0)
        
        # Canvas and scrollbar
        canvas = tk.Canvas(scroll_container, bg=BG_COLOR, highlightthickness=0)
        vscroll = tk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Content frame inside canvas
        content_frame = tk.Frame(canvas, bg=BG_COLOR)
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw", tags="content_window")
        
        # Update scroll region when content changes
        def update_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        content_frame.bind("<Configure>", update_scroll_region)
        
        # Sync content frame width with canvas width for responsive layout
        def _sync_width(event):
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:
                canvas.itemconfig(canvas_window, width=canvas_width)
        canvas.bind("<Configure>", _sync_width)
        
        # Mouse wheel support (Windows/Mac/Linux)
        def on_mousewheel(event):
            if event.num == 4 or event.num == 5:
                # Linux scroll
                delta = -1 if event.num == 4 else 1
            else:
                # Windows/Mac
                delta = -1 if event.delta > 0 else 1
                # Normalize delta
                if abs(event.delta) > 0:
                    delta = delta * (120 // abs(event.delta))
            canvas.yview_scroll(int(delta), "units")
        
        # Bind mouse wheel to canvas and content frame
        canvas.bind("<MouseWheel>", on_mousewheel)
        canvas.bind("<Button-4>", on_mousewheel)
        canvas.bind("<Button-5>", on_mousewheel)
        content_frame.bind("<MouseWheel>", on_mousewheel)
        content_frame.bind("<Button-4>", on_mousewheel)
        content_frame.bind("<Button-5>", on_mousewheel)
        
        # Content wrapper with padding
        content_wrapper = tk.Frame(content_frame, bg=BG_COLOR)
        content_wrapper.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Cards container (6-piece grid - UNCHANGED)
        cards_container = tk.Frame(content_wrapper, bg=BG_COLOR)
        cards_container.pack(fill="both", expand=True, pady=(0, 16))
        cards_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="card_cols")
        cards_container.grid_rowconfigure(0, weight=1, uniform="card_rows")
        cards_container.grid_rowconfigure(1, weight=1, uniform="card_rows")
        card_widgets = []
        for i, (piece_name, info) in enumerate(PIECE_INFO.items()):
            card_widgets.append(self.create_learning_card(cards_container, info, i // 3, i % 3))
        
        # Update wraplength after rendering
        def update_card_wraplengths():
            try:
                self.update_idletasks()
                for card_info in card_widgets:
                    if card_info and 'desc_label' in card_info:
                        try:
                            frame_width = card_info['info_frame'].winfo_width()
                            if frame_width > 50:
                                card_info['desc_label'].config(wraplength=max(150, frame_width - 40))
                        except:
                            pass
                    if card_info and 'bullet_label' in card_info:
                        try:
                            frame_width = card_info['special_frame'].winfo_width()
                            if frame_width > 50:
                                card_info['bullet_label'].config(wraplength=max(150, frame_width - 20))
                        except:
                            pass
            except:
                pass
        
        self.after_idle(update_card_wraplengths)
        self.after(100, update_card_wraplengths)
        
        # The Mind Behind the Move section
        mind_section = tk.LabelFrame(
            content_wrapper, 
            text="✨ The Mind Behind the Move",
            font=("Georgia", 18, "bold"),
            bg=CARD_COLOR,
            fg=GOLD_ACCENT,
            relief="raised",
            bd=2,
            labelanchor="nw"
        )
        mind_section.pack(fill="x", padx=10, pady=(0, 16))
        
        mind_content = tk.Frame(mind_section, bg=CARD_COLOR)
        mind_content.pack(fill="both", padx=15, pady=15)
        
        mind_text = """Chess teaches us something quietly profound.


Every piece has limits —
but every position has possibilities.


The pawn is small, yet it dreams of becoming anything.
The knight moves differently — and that's exactly why it matters.
The rook moves straight, but the path is still yours to choose.
The king moves one square at a time — and still shapes the future.


Just like code:

- We don't always start as the strongest piece.

- We grow by understanding patterns, not memorizing moves.

- We don't win by speed — we win by clarity.


A good engineer doesn't just solve problems —
they see the board,
they find the idea no one else considered,
they make the quiet move that changes everything.


You're not just learning chess.
You're learning how to think.


Move with purpose.
Improve with patience.
And always believe in the pawn inside you."""
        
        mind_label = tk.Label(
            mind_content,
            text=mind_text,
            font=("Georgia", 13, "italic"),
            bg=CARD_COLOR,
            fg=HEADER_COLOR,
            justify="left",
            anchor="w",
            wraplength=680,
            padx=12,
            pady=10
        )
        mind_label.pack(anchor="w", fill="x")
        
        # Spacing before rules section
        tk.Frame(content_wrapper, bg=BG_COLOR, height=20).pack(fill="x")
        
        # Basic rules section (redesigned)
        self.create_basic_rules_section(content_wrapper)
        
        # Bottom padding
        tk.Frame(content_wrapper, bg=BG_COLOR, height=32).pack(fill="x")
        
        # Update scroll region after all content is added
        self.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def create_home_button_in_frame(self, frame):
        btn = self.create_styled_button(
            frame, "🏠 Home",
            lambda: self.controller.show_frame("WelcomePage"),
            bg_color=RESET_BUTTON_COLOR, hover_color="#A63546",
            font_size=12
        )
        btn.pack(side="right")
        
    def create_back_button_grid(self, target="ModeSelectionPage"):
        back_frame = tk.Frame(self, bg=BG_COLOR)
        back_frame.grid(row=2, column=0, sticky="sw", padx=30, pady=20) 
        btn = self.create_styled_button(
            back_frame, "← Back", 
            lambda: self.controller.show_frame(target),
            bg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER
        )
        btn.pack(side="left") 

    def create_learning_card(self, parent, piece_info, row, column):
        card_frame = tk.Frame(parent, bg=CARD_COLOR, relief="raised", bd=2)
        card_frame.grid(row=row, column=column, sticky="nsew", padx=10, pady=10)
        parent.grid_rowconfigure(row, weight=1) 
        card_frame.grid_columnconfigure(0, weight=1)
        content_frame = tk.Frame(card_frame, bg=CARD_COLOR)
        content_frame.pack(fill="both", padx=15, pady=15)
        grid_container = tk.Frame(content_frame, bg=CARD_COLOR)
        grid_container.pack(fill="both", expand=True)
        grid_container.grid_columnconfigure(0, weight=1)
        grid_container.grid_rowconfigure(0, weight=1)  # Make row 0 expand to push row 1 to bottom
        grid_container.grid_rowconfigure(1, weight=0)  # Keep row 1 at fixed position
        header_frame = tk.Frame(grid_container, bg=CARD_COLOR)
        header_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5)) 
        symbol_label = tk.Label(
            header_frame, text=piece_info["symbol"],
            font=("Arial Unicode MS", 32), bg=CARD_COLOR, fg=HEADER_COLOR
        )
        symbol_label.pack(side="left")
        info_frame = tk.Frame(header_frame, bg=CARD_COLOR)
        info_frame.pack(side="left", fill="both", expand=True, padx=(15, 0))
        name_label = tk.Label(
            info_frame, text=piece_info["name"],
            font=("Segoe UI", 16, "bold"), bg=CARD_COLOR, fg=GOLD_ACCENT,
            anchor="w", justify="left"
        )
        name_label.pack(anchor="w", pady=(0, 4))
        desc_label = tk.Label(
            info_frame, text=piece_info["description"],
            font=("Segoe UI", 11), bg=CARD_COLOR, fg=SUBHEADER_COLOR,
            justify="left", anchor="w", wraplength=180
        )
        desc_label.pack(anchor="w", pady=(0, 4))
        
        special_frame = tk.Frame(grid_container, bg=SURFACE_COLOR, relief="groove", bd=1)
        special_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        special_frame.grid_columnconfigure(0, weight=1)
        bullet_label = tk.Label(
            special_frame, text="• " + piece_info["special"],
            font=("Segoe UI", 10), bg=SURFACE_COLOR, fg=piece_info["color"],
            justify="left", anchor="w", wraplength=220, padx=8, pady=6
        )
        bullet_label.grid(row=0, column=0, sticky="w", padx=8, pady=6)
        
        # Return widget references for later wraplength updates
        return {
            'info_frame': info_frame,
            'desc_label': desc_label,
            'special_frame': special_frame,
            'bullet_label': bullet_label
        }

    def create_basic_rules_section(self, parent):
        """Create the Basic Rules section with premium spacing and responsive grid."""
        # Rules header with premium spacing
        rules_header = tk.Frame(parent, bg=BG_COLOR)
        rules_header.pack(fill="x", pady=(32, 12))
        tk.Label(
            rules_header, text="⚔️ Basic Rules Summary",
            font=("Segoe UI", 20, "bold"), bg=BG_COLOR, fg=HEADER_COLOR
        ).pack(anchor="w")
        
        # Rules container with responsive grid
        rules_container = tk.Frame(parent, bg=BG_COLOR)
        rules_container.pack(fill="x", pady=(0, 0))
        
        rules = [
            { "title": "🎯 Objective:", "content": "Checkmate your opponent's king (trapped and attacked).", "color": SUCCESS_COLOR },
            { "title": "🔄 Turn Order:", "content": "White moves first, then players alternate turns.", "color": ACCENT_COLOR },
            { "title": "🏰 Special Moves:", "content": "Castling, En passant, and Pawn Promotion.", "color": WARNING_COLOR },
            { "title": "🏁 Game End:", "content": "Checkmate, Stalemate (draw), or agreement.", "color": DANGER_COLOR }
        ]
        
        # Responsive grid: 4 columns on wide, 2 columns on narrow
        rules_grid = tk.Frame(rules_container, bg=BG_COLOR)
        rules_grid.pack(fill="x", padx=0, pady=0)
        
        # Configure grid columns with uniform sizing
        for col in range(4):
            rules_grid.grid_columnconfigure(col, weight=1, uniform="rule_cols")
        
        # Create rule cards
        for i, rule in enumerate(rules):
            rule_card = tk.Frame(rules_grid, bg=CARD_COLOR, relief="flat", bd=0, highlightthickness=1, highlightbackground=ACCENT_COLOR)
            rule_card.grid(row=0, column=i, padx=8, pady=8, sticky="nsew")
            
            # Card content with consistent padding
            card_content = tk.Frame(rule_card, bg=CARD_COLOR)
            card_content.pack(fill="both", expand=True, padx=16, pady=12)
            
            tk.Label(
                card_content, text=rule["title"],
                font=("Segoe UI", 12, "bold"), bg=CARD_COLOR, fg=rule["color"],
                wraplength=200, justify="left"
            ).pack(anchor="w", pady=(0, 6))
            
            tk.Label(
                card_content, text=rule["content"],
                font=("Segoe UI", 10), bg=CARD_COLOR, fg=SUBHEADER_COLOR,
                wraplength=200, justify="left"
            ).pack(anchor="w")

if __name__ == "__main__":
    app = ChessGUI()
    app.mainloop()
