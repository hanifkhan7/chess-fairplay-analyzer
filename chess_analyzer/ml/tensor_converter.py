"""
Tensor Converter: Convert chess positions to machine learning tensors

This module handles the conversion of chess.Board objects to 12-channel 8x8 tensors
suitable for CNN-LSTM neural networks. The 12-channel representation uses:

Channels (0-11):
- 0-5: White pieces (Pawn, Knight, Bishop, Rook, Queen, King)
- 6-11: Black pieces (Pawn, Knight, Bishop, Rook, Queen, King)

Each channel contains a binary 8x8 grid indicating piece positions.
"""

import numpy as np
import chess
from typing import List, Tuple, Optional


class TensorConverter:
    """Convert chess positions to ML tensor representation."""
    
    # Piece-to-channel mapping
    PIECE_CHANNELS = {
        chess.PAWN: 0,
        chess.KNIGHT: 1,
        chess.BISHOP: 2,
        chess.ROOK: 3,
        chess.QUEEN: 4,
        chess.KING: 5,
    }
    
    # Color offset
    WHITE_OFFSET = 0
    BLACK_OFFSET = 6
    
    @staticmethod
    def board_to_tensor(board: chess.Board) -> np.ndarray:
        """
        Convert a single chess position to a 12x8x8 tensor.
        
        Args:
            board: chess.Board object representing the current position
            
        Returns:
            np.ndarray: Shape (12, 8, 8) representing the board state
                - Channels 0-5: White pieces
                - Channels 6-11: Black pieces
        """
        tensor = np.zeros((12, 8, 8), dtype=np.float32)
        
        # Iterate through all squares
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue
            
            # Get square coordinates (0-7 for rank and file)
            rank = square // 8
            file = square % 8
            
            # Get channel index
            piece_type = piece.piece_type
            color_offset = TensorConverter.WHITE_OFFSET if piece.color == chess.WHITE else TensorConverter.BLACK_OFFSET
            channel = color_offset + TensorConverter.PIECE_CHANNELS[piece_type]
            
            # Set the tensor value
            tensor[channel, rank, file] = 1.0
        
        return tensor
    
    @staticmethod
    def game_to_tensors(board: chess.Board, moves: List[chess.Move], 
                       sequence_length: int = 20) -> np.ndarray:
        """
        Convert a game sequence into temporal tensors for LSTM input.
        
        Args:
            board: Starting board position (usually starting position)
            moves: List of moves in the game
            sequence_length: Number of consecutive positions to capture
            
        Returns:
            np.ndarray: Shape (num_sequences, sequence_length, 12, 8, 8)
                Contains all valid temporal sequences from the game
        """
        sequences = []
        game_board = board.copy()
        
        # Build all board states in the game
        board_states = [TensorConverter.board_to_tensor(game_board.copy())]
        for move in moves:
            game_board.push(move)
            board_states.append(TensorConverter.board_to_tensor(game_board.copy()))
        
        # Extract sequences of specified length
        for i in range(len(board_states) - sequence_length + 1):
            sequence = np.array(board_states[i:i + sequence_length], dtype=np.float32)
            sequences.append(sequence)
        
        if not sequences:
            return np.array([], dtype=np.float32)
        
        return np.array(sequences, dtype=np.float32)
    
    @staticmethod
    def add_turn_channel(tensor: np.ndarray, board: chess.Board) -> np.ndarray:
        """
        Add turn information as 13th channel (1 = White to move, 0 = Black to move).
        
        Args:
            tensor: Base 12-channel tensor
            board: chess.Board object
            
        Returns:
            np.ndarray: Shape (13, 8, 8) with turn information
        """
        turn_channel = np.full((1, 8, 8), 1.0 if board.turn == chess.WHITE else 0.0, 
                              dtype=np.float32)
        return np.vstack([tensor, turn_channel])
    
    @staticmethod
    def add_castling_rights_channel(tensor: np.ndarray, board: chess.Board) -> np.ndarray:
        """
        Add castling rights as encoded channels.
        
        Args:
            tensor: Base tensor
            board: chess.Board object
            
        Returns:
            np.ndarray: Shape (14, 8, 8) with castling rights
        """
        castling_tensor = np.zeros((1, 8, 8), dtype=np.float32)
        
        # Encode castling rights as a single value (0-15 possible states)
        castling_value = 0
        if board.has_kingside_castling_rights(chess.WHITE):
            castling_value += 1
        if board.has_queenside_castling_rights(chess.WHITE):
            castling_value += 2
        if board.has_kingside_castling_rights(chess.BLACK):
            castling_value += 4
        if board.has_queenside_castling_rights(chess.BLACK):
            castling_value += 8
        
        # Normalize to 0-1 range
        castling_tensor[0, 0, 0] = castling_value / 15.0
        
        return np.vstack([tensor, castling_tensor])
    
    @staticmethod
    def normalize_tensors(tensors: np.ndarray) -> np.ndarray:
        """
        Normalize tensors to 0-1 range (already done in conversion, but included for completeness).
        
        Args:
            tensors: np.ndarray of any shape
            
        Returns:
            np.ndarray: Normalized tensors
        """
        # These are already binary (0 or 1), so just return
        return np.clip(tensors, 0.0, 1.0).astype(np.float32)
    
    @staticmethod
    def augment_tensor(tensor: np.ndarray) -> np.ndarray:
        """
        Data augmentation: flip the board horizontally (mirror position).
        
        Args:
            tensor: Shape (12, 8, 8) or (13, 8, 8) or (14, 8, 8)
            
        Returns:
            np.ndarray: Flipped tensor
        """
        # Flip left-right (file axis)
        flipped = np.flip(tensor, axis=2).copy()
        return flipped
    
    @staticmethod
    def tensor_to_board(tensor: np.ndarray, turn: bool = chess.WHITE) -> Optional[chess.Board]:
        """
        Reconstruct a chess.Board from a 12-channel tensor (for debugging).
        
        Args:
            tensor: Shape (12, 8, 8) tensor
            turn: Whose turn it is (chess.WHITE or chess.BLACK)
            
        Returns:
            chess.Board: Reconstructed board or None if invalid
        """
        board = chess.Board()
        board.clear()
        board.turn = turn
        
        for channel in range(12):
            piece_type = channel % 6
            color = chess.WHITE if channel < 6 else chess.BLACK
            
            for rank in range(8):
                for file in range(8):
                    if tensor[channel, rank, file] > 0.5:  # Binary check
                        square = rank * 8 + file
                        piece = chess.Piece(piece_type, color)
                        board.set_piece_at(square, piece)
        
        # Validate the board state
        try:
            board.is_valid()
            return board
        except:
            return None
    
    @staticmethod
    def validate_tensor(tensor: np.ndarray) -> Tuple[bool, str]:
        """
        Validate that a tensor represents a valid chess position.
        
        Args:
            tensor: Shape (12, 8, 8) tensor
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # Check shape
        if tensor.shape != (12, 8, 8):
            return False, f"Invalid shape {tensor.shape}, expected (12, 8, 8)"
        
        # Check values are binary
        if not np.all(np.isin(tensor, [0.0, 1.0])):
            return False, "Tensor values must be binary (0.0 or 1.0)"
        
        # Check max 1 king per color
        for color_offset in [0, 6]:
            king_channel = color_offset + 5
            king_count = np.sum(tensor[king_channel])
            if king_count != 1:
                return False, f"Expected 1 king for color offset {color_offset}, got {int(king_count)}"
        
        # Check reasonable piece count (max 16 per side)
        for color_offset in [0, 6]:
            piece_count = 0
            for piece_channel in range(6):
                piece_count += np.sum(tensor[color_offset + piece_channel])
            if piece_count > 16:
                return False, f"Too many pieces for color offset {color_offset}: {int(piece_count)}"
        
        return True, "Valid tensor"


# Helper functions for convenience
def board_to_tensor(board: chess.Board) -> np.ndarray:
    """Convenience function: convert board to tensor."""
    return TensorConverter.board_to_tensor(board)


def game_to_tensors(board: chess.Board, moves: List[chess.Move], 
                   sequence_length: int = 20) -> np.ndarray:
    """Convenience function: convert game moves to tensor sequences."""
    return TensorConverter.game_to_tensors(board, moves, sequence_length)


def augment_tensor(tensor: np.ndarray) -> np.ndarray:
    """Convenience function: augment tensor by flipping."""
    return TensorConverter.augment_tensor(tensor)
