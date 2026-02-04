"""
Data Preparation: Convert PGN games to ML training data

This module handles:
- Loading and parsing PGN files
- Converting games to tensor sequences
- Data augmentation
- Train/val/test splitting
- Balancing and handling imbalanced datasets
"""

import numpy as np
import chess
import chess.pgn
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from sklearn.model_selection import train_test_split
from collections import Counter
import io

from .tensor_converter import TensorConverter


class DataPreparator:
    """Prepare chess games data for model training."""
    
    def __init__(self, sequence_length: int = 20, augment: bool = True):
        """
        Initialize data preparer.
        
        Args:
            sequence_length: Number of consecutive positions to use per sample
            augment: Whether to augment data by flipping boards
        """
        self.sequence_length = sequence_length
        self.augment = augment
        self.converter = TensorConverter()
    
    def load_pgn_games(self, pgn_file: str) -> List[chess.pgn.GameNode]:
        """
        Load games from PGN file.
        
        Args:
            pgn_file: Path to PGN file
            
        Returns:
            List of chess.pgn.GameNode objects
        """
        games = []
        
        try:
            with open(pgn_file, 'r', encoding='utf-8', errors='ignore') as f:
                while True:
                    game = chess.pgn.read_game(f)
                    if game is None:
                        break
                    games.append(game)
        except Exception as e:
            print(f"Error loading PGN: {e}")
            return []
        
        return games
    
    def extract_moves_from_game(self, game: chess.pgn.GameNode) -> List[chess.Move]:
        """
        Extract all moves from a game.
        
        Args:
            game: chess.pgn.GameNode
            
        Returns:
            List of chess.Move objects
        """
        moves = []
        board = game.board()
        
        for move in game.mainline_moves():
            moves.append(move)
        
        return moves
    
    def game_to_label(self, game: chess.pgn.GameNode, label: Optional[int] = None) -> int:
        """
        Determine if game is by human (0) or engine (1) based on headers or provided label.
        
        Args:
            game: chess.pgn.GameNode
            label: Explicit label (0=human, 1=engine). If None, infer from game headers
            
        Returns:
            Label (0 or 1)
        """
        if label is not None:
            return label
        
        # Check game headers for indicators
        white = game.headers.get('White', '').lower()
        black = game.headers.get('Black', '').lower()
        
        engine_keywords = ['engine', 'stockfish', 'leela', 'computer', 'bot', 'ai']
        
        for keyword in engine_keywords:
            if keyword in white or keyword in black:
                return 1  # Engine
        
        return 0  # Human
    
    def game_to_tensors(self, game: chess.pgn.GameNode, 
                       label: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert a game to tensor sequences with labels.
        
        Args:
            game: chess.pgn.GameNode
            label: 0 for human, 1 for engine
            
        Returns:
            Tuple of (tensors, labels) where both are numpy arrays
        """
        moves = self.extract_moves_from_game(game)
        
        if len(moves) < self.sequence_length:
            return np.array([]), np.array([])
        
        # Get tensor sequences from game
        board = game.board()
        sequences = self.converter.game_to_tensors(board, moves, self.sequence_length)
        
        if sequences.size == 0:
            return np.array([]), np.array([])
        
        # Create labels for each sequence
        num_sequences = sequences.shape[0]
        labels = np.full((num_sequences, 2), [1, 0] if label == 0 else [0, 1], dtype=np.float32)
        
        # Data augmentation (flip boards)
        if self.augment:
            augmented_sequences = []
            for seq in sequences:
                flipped = np.array([self.converter.augment_tensor(pos) for pos in seq])
                augmented_sequences.append(flipped)
            sequences = np.vstack([sequences, np.array(augmented_sequences)])
            labels = np.vstack([labels, labels])  # Same labels for flipped
        
        return sequences, labels
    
    def prepare_dataset(self, 
                       pgn_file: str,
                       human_label: int = 0,
                       engine_label: int = 1,
                       max_games: Optional[int] = None,
                       test_size: float = 0.1,
                       val_size: float = 0.1) -> Dict:
        """
        Prepare complete train/val/test dataset from PGN file(s).
        
        Args:
            pgn_file: Path to PGN file or directory with PGN files
            human_label: Label for human games
            engine_label: Label for engine games
            max_games: Maximum games to load (for quick testing)
            test_size: Fraction for test set
            val_size: Fraction for validation set
            
        Returns:
            Dict with 'X_train', 'y_train', 'X_val', 'y_val', 'X_test', 'y_test'
        """
        X = []
        y = []
        
        pgn_path = Path(pgn_file)
        
        # Get list of PGN files
        if pgn_path.is_dir():
            pgn_files = list(pgn_path.glob("*.pgn"))
        else:
            pgn_files = [pgn_path]
        
        game_count = 0
        
        for pgn_file_path in pgn_files:
            print(f"Loading games from {pgn_file_path.name}...")
            games = self.load_pgn_games(str(pgn_file_path))
            
            for i, game in enumerate(games):
                if max_games and game_count >= max_games:
                    break
                
                try:
                    label = self.game_to_label(game)
                    sequences, labels = self.game_to_tensors(game, label)
                    
                    if sequences.size > 0:
                        X.append(sequences)
                        y.append(labels)
                        game_count += 1
                        
                        if (i + 1) % 100 == 0:
                            print(f"  Processed {i + 1} games...")
                
                except Exception as e:
                    print(f"  Error processing game: {e}")
                    continue
        
        if not X:
            print("No valid games found!")
            return {}
        
        # Concatenate all data
        X = np.vstack(X)
        y = np.vstack(y)
        
        print(f"\nTotal samples: {X.shape[0]}")
        print(f"Shape: {X.shape}")
        print(f"Label distribution: {np.sum(y, axis=0)}")
        
        # Split into train/val/test
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=np.argmax(y, axis=1)
        )
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, 
            test_size=val_size / (1 - test_size),
            random_state=42,
            stratify=np.argmax(y_temp, axis=1)
        )
        
        return {
            'X_train': X_train,
            'y_train': y_train,
            'X_val': X_val,
            'y_val': y_val,
            'X_test': X_test,
            'y_test': y_test,
        }
    
    def balance_dataset(self, X: np.ndarray, y: np.ndarray,
                       strategy: str = 'oversample') -> Tuple[np.ndarray, np.ndarray]:
        """
        Balance imbalanced dataset.
        
        Args:
            X: Input features
            y: Labels (one-hot encoded)
            strategy: 'oversample' or 'undersample'
            
        Returns:
            Balanced (X, y)
        """
        labels = np.argmax(y, axis=1)
        label_counts = Counter(labels)
        
        if len(label_counts) != 2:
            return X, y
        
        if strategy == 'oversample':
            # Oversample minority class
            max_count = max(label_counts.values())
            
            X_balanced = [X]
            y_balanced = [y]
            
            for label in label_counts:
                if label_counts[label] < max_count:
                    indices = np.where(labels == label)[0]
                    n_needed = max_count - label_counts[label]
                    oversample_indices = np.random.choice(indices, n_needed, replace=True)
                    
                    X_balanced.append(X[oversample_indices])
                    y_balanced.append(y[oversample_indices])
            
            X_balanced = np.vstack(X_balanced)
            y_balanced = np.vstack(y_balanced)
            
        elif strategy == 'undersample':
            # Undersample majority class
            min_count = min(label_counts.values())
            
            X_balanced = []
            y_balanced = []
            
            for label in label_counts:
                indices = np.where(labels == label)[0]
                undersample_indices = np.random.choice(indices, min_count, replace=False)
                
                X_balanced.append(X[undersample_indices])
                y_balanced.append(y[undersample_indices])
            
            X_balanced = np.vstack(X_balanced)
            y_balanced = np.vstack(y_balanced)
        
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        return X_balanced, y_balanced
    
    def calculate_class_weights(self, y: np.ndarray) -> Dict[int, float]:
        """
        Calculate class weights for imbalanced data.
        
        Args:
            y: Labels (one-hot encoded)
            
        Returns:
            Dict mapping class index to weight
        """
        labels = np.argmax(y, axis=1)
        label_counts = Counter(labels)
        
        total = len(labels)
        class_weights = {}
        
        for label, count in label_counts.items():
            # Inverse frequency weighting
            class_weights[label] = total / (len(label_counts) * count)
        
        return class_weights
    
    def normalize_tensors(self, X: np.ndarray) -> np.ndarray:
        """
        Normalize tensors to 0-1 range (already done by converter, but for safety).
        
        Args:
            X: Input tensors
            
        Returns:
            Normalized tensors
        """
        return np.clip(X, 0.0, 1.0).astype(np.float32)
    
    def save_dataset(self, data: Dict, output_dir: str):
        """
        Save prepared dataset to disk.
        
        Args:
            data: Dict with 'X_train', 'y_train', etc.
            output_dir: Directory to save to
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for key, value in data.items():
            if isinstance(value, np.ndarray):
                np.save(output_path / f"{key}.npy", value)
        
        print(f"Dataset saved to {output_dir}")
    
    def load_dataset(self, data_dir: str) -> Dict:
        """
        Load prepared dataset from disk.
        
        Args:
            data_dir: Directory containing saved dataset
            
        Returns:
            Dict with loaded data
        """
        data_path = Path(data_dir)
        data = {}
        
        for key in ['X_train', 'y_train', 'X_val', 'y_val', 'X_test', 'y_test']:
            file_path = data_path / f"{key}.npy"
            if file_path.exists():
                data[key] = np.load(file_path)
        
        return data
