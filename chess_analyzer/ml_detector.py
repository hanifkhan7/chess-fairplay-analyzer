"""
ML Cheat Detector: High-level interface for cheat detection

This module provides the MLCheatDetector class that:
- Loads pre-trained models
- Analyzes games for potential cheating
- Provides confidence scores and explanations
- Integrates with existing analyzer framework
"""

import os
import numpy as np
import chess
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import json

from .tensor_converter import TensorConverter
from .models import load_model

try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False


class MLCheatDetector:
    """High-level ML-based cheat detection interface."""
    
    def __init__(self, model_path: str, threshold: float = 0.7):
        """
        Initialize ML cheat detector.
        
        Args:
            model_path: Path to pre-trained model (.h5 file)
            threshold: Confidence threshold for flagging as cheating (0-1)
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required for ML detection")
        
        self.model_path = model_path
        self.threshold = threshold
        self.model = None
        self.converter = TensorConverter()
        
        # Try to load model
        if os.path.exists(model_path):
            self.model = load_model(model_path)
            if self.model:
                print(f"✓ Loaded ML model from {model_path}")
        else:
            print(f"⚠ Model not found at {model_path}")
            print(f"  ML detection will be unavailable until model is trained")
    
    def is_available(self) -> bool:
        """Check if detector is available (model loaded)."""
        return self.model is not None
    
    def analyze_game(self, game_moves: List[chess.Move], 
                    sequence_length: int = 20) -> Dict:
        """
        Analyze a single game for potential cheating.
        
        Args:
            game_moves: List of chess.Move objects in the game
            sequence_length: Number of consecutive positions per sample
            
        Returns:
            Dict with analysis results
        """
        if not self.is_available():
            return {'error': 'Model not loaded'}
        
        if len(game_moves) < sequence_length:
            return {'error': f'Game too short (min {sequence_length} moves)'}
        
        try:
            # Convert game to tensors
            board = chess.Board()
            sequences = self.converter.game_to_tensors(board, game_moves, sequence_length)
            
            if sequences.size == 0:
                return {'error': 'Could not create tensor sequences'}
            
            # Make predictions
            predictions = self.model.predict(sequences, verbose=0)
            
            # Extract probabilities
            # Class 0: Human, Class 1: Engine
            human_probs = predictions[:, 0]
            engine_probs = predictions[:, 1]
            
            # Calculate statistics
            mean_engine_prob = float(np.mean(engine_probs))
            max_engine_prob = float(np.max(engine_probs))
            min_engine_prob = float(np.min(engine_probs))
            std_engine_prob = float(np.std(engine_probs))
            
            # Suspicious positions (high engine probability)
            suspicious_positions = np.where(engine_probs > self.threshold)[0].tolist()
            
            # Determine if game is likely cheated
            is_cheating = mean_engine_prob > 0.5
            
            return {
                'is_cheating': is_cheating,
                'mean_engine_probability': mean_engine_prob,
                'max_engine_probability': max_engine_prob,
                'min_engine_probability': min_engine_prob,
                'std_engine_probability': std_engine_prob,
                'num_suspicious_positions': len(suspicious_positions),
                'suspicious_position_indices': suspicious_positions,
                'all_engine_probabilities': engine_probs.tolist(),
                'num_positions_analyzed': len(sequences),
            }
        
        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}
    
    def analyze_games(self, games_data: List[Dict]) -> List[Dict]:
        """
        Analyze multiple games.
        
        Args:
            games_data: List of dicts with 'moves' key containing List[chess.Move]
            
        Returns:
            List of analysis results
        """
        results = []
        
        for i, game_data in enumerate(games_data):
            if 'moves' not in game_data:
                results.append({'error': 'No moves in game data'})
                continue
            
            result = self.analyze_game(game_data['moves'])
            results.append(result)
        
        return results
    
    def explain_prediction(self, analysis_result: Dict) -> str:
        """
        Generate human-readable explanation of detection result.
        
        Args:
            analysis_result: Result from analyze_game()
            
        Returns:
            Explanation string
        """
        if 'error' in analysis_result:
            return f"Analysis Error: {analysis_result['error']}"
        
        explanation = []
        
        mean_prob = analysis_result.get('mean_engine_probability', 0)
        is_cheating = analysis_result.get('is_cheating', False)
        suspicious_count = analysis_result.get('num_suspicious_positions', 0)
        total_positions = analysis_result.get('num_positions_analyzed', 0)
        
        # Overall assessment
        if is_cheating:
            explanation.append("🚩 LIKELY CHEATING DETECTED")
            explanation.append(f"   Average engine similarity: {mean_prob:.1%}")
        else:
            explanation.append("✓ Likely human play")
            explanation.append(f"   Average engine similarity: {mean_prob:.1%}")
        
        # Suspicious positions
        if suspicious_count > 0:
            pct = (suspicious_count / total_positions) * 100 if total_positions > 0 else 0
            explanation.append(f"\n⚠ {suspicious_count}/{total_positions} positions ({pct:.1f}%) match engine play")
        
        # Confidence
        confidence = max(mean_prob, 1 - mean_prob)
        if confidence > 0.9:
            explanation.append("   Confidence: Very High")
        elif confidence > 0.75:
            explanation.append("   Confidence: High")
        elif confidence > 0.6:
            explanation.append("   Confidence: Moderate")
        else:
            explanation.append("   Confidence: Low")
        
        return "\n".join(explanation)
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        if not self.is_available():
            return {'status': 'Model not loaded'}
        
        return {
            'status': 'Model loaded',
            'model_path': self.model_path,
            'input_shape': self.model.input_shape,
            'output_shape': self.model.output_shape,
            'num_layers': len(self.model.layers),
            'num_parameters': self.model.count_params(),
            'threshold': self.threshold,
        }
    
    def set_threshold(self, threshold: float):
        """
        Set confidence threshold for flagging suspicious positions.
        
        Args:
            threshold: Threshold value (0-1)
        """
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        
        self.threshold = threshold
    
    def save_results(self, results: List[Dict], output_file: str):
        """
        Save analysis results to JSON file.
        
        Args:
            results: List of analysis results
            output_file: Path to save JSON file
        """
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to {output_file}")


class MLDetectionReport:
    """Generate detailed reports from ML detection results."""
    
    @staticmethod
    def create_report(detector: MLCheatDetector,
                     analysis_results: List[Dict],
                     player_name: str = "Unknown") -> str:
        """
        Create detailed report from detection results.
        
        Args:
            detector: MLCheatDetector instance
            analysis_results: List of game analysis results
            player_name: Name of analyzed player
            
        Returns:
            HTML report string
        """
        cheating_games = [r for r in analysis_results if r.get('is_cheating')]
        
        html = f"""
        <html>
        <head>
            <title>ML Cheat Detection Report - {player_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .game {{ border: 1px solid #ccc; padding: 10px; margin: 10px 0; }}
                .cheating {{ background: #ffcccc; }}
                .legitimate {{ background: #ccffcc; }}
                .chart {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>ML Cheat Detection Report</h1>
            <p>Player: <strong>{player_name}</strong></p>
            
            <div class="summary">
                <h2>Summary</h2>
                <p>Total games analyzed: {len(analysis_results)}</p>
                <p>Flagged as cheating: {len(cheating_games)} ({len(cheating_games)/len(analysis_results)*100:.1f}%)</p>
                <p>Model confidence: {detector.get_model_info()['threshold']*100:.0f}%</p>
            </div>
            
            <h2>Results by Game</h2>
        """
        
        for i, result in enumerate(analysis_results):
            if 'error' in result:
                css_class = "legitimate"
                status = "⚠ Error"
            else:
                css_class = "cheating" if result.get('is_cheating') else "legitimate"
                status = "🚩 Cheating Suspected" if result.get('is_cheating') else "✓ Legitimate"
            
            html += f"""
            <div class="game {css_class}">
                <h3>Game {i+1}: {status}</h3>
                <p>Average engine probability: {result.get('mean_engine_probability', 0)*100:.1f}%</p>
                <p>Suspicious positions: {result.get('num_suspicious_positions', 0)}/{result.get('num_positions_analyzed', 0)}</p>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html


# Convenience functions
def analyze_game_with_ml(game_moves: List[chess.Move],
                        model_path: str,
                        threshold: float = 0.7) -> Dict:
    """Quick function to analyze a game with ML."""
    detector = MLCheatDetector(model_path, threshold)
    return detector.analyze_game(game_moves)


def get_ml_detector(model_path: str) -> Optional[MLCheatDetector]:
    """Get detector instance, or None if model not found."""
    if not os.path.exists(model_path):
        return None
    
    try:
        return MLCheatDetector(model_path)
    except Exception as e:
        print(f"Error creating detector: {e}")
        return None
