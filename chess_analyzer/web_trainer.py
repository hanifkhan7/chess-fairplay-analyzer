"""
Web-based Opening Analysis Tool - Modern Chess.com Style Interface
Interactive exploration of opponent opening repertoires with drag-and-drop moves.
"""
import json
import webbrowser
from pathlib import Path
from threading import Thread
import logging

try:
    from flask import Flask, render_template, request, jsonify
    from flask_cors import CORS
except ImportError:
    raise ImportError("Flask is required. Install with: pip install flask flask-cors")

logger = logging.getLogger(__name__)


def launch_web_trainer(trainer=None, opponent_name=None, port=5000, debug=False):
    """
    Launch modern web-based opening repertoire analyzer.
    
    Args:
        trainer: OpeningTrainer instance (can be None for later loading)
        opponent_name: Name of opponent
        port: Port to run Flask on
        debug: Debug mode
    """
    # Get absolute paths relative to project root
    project_root = Path(__file__).parent.parent
    template_folder = str(project_root / 'templates')
    static_folder = str(project_root / 'static')
    
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    CORS(app)
    
    # Store trainer in app context
    app.trainer = trainer
    app.opponent_name = opponent_name
    
    # ==================== ROUTES ====================
    
    @app.route('/api/setup', methods=['POST'])
    def setup_trainer():
        """Web-based setup: fetch games and build OpeningTrainer dynamically."""
        data = request.json
        username = data.get('username')
        num_games = data.get('games', 'all')
        color = data.get('color', 'both')
        platform = data.get('platform', 'both')

        if not username:
            return jsonify({'success': False, 'error': 'Username required'}), 400

        try:
            # Import here to avoid circular import
            from .opening_trainer import OpeningTrainer
            # Simulate fetching games and building trainer
            # TODO: Replace with real fetch logic for chess.com/lichess
            # For now, just build a dummy trainer with no games
            # You should implement your real fetch logic here!
            games = []
            # Example: games = fetch_games(username, num_games, color, platform)
            trainer = OpeningTrainer(games, opponent_name=username, color=color)
            app.trainer = trainer
            app.opponent_name = username
            return jsonify({'success': True, 'message': f'Repertoire built for {username}'})
        except Exception as e:
            logger.error(f"Error in setup: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    @app.route('/')
    def index():
        """Serve main page."""
        return render_template('opening_analysis.html')
    
    @app.route('/api/opponent/<username>')
    def get_opponent_data(username):
        """Initialize opponent repertoire analysis."""
        if not app.trainer:
            return jsonify({'error': 'No trainer loaded'}), 400
            
        try:
            return jsonify({
                'success': True,
                'opponent': app.opponent_name,
                'games': len(app.trainer.games),
                'positions': app.trainer.stats.get('total_unique_positions', 0),
                'depth': app.trainer.stats.get('repertoire_depth', 0),
                'starting_position': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
            })
        except Exception as e:
            logger.error(f"Error loading opponent data: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/position', methods=['POST'])
    def analyze_position():
        """Get opening analysis for current position (FEN)."""
        if not app.trainer:
            return jsonify({'error': 'No trainer loaded'}), 400
            
        data = request.json
        fen = data.get('fen')
        
        try:
            import chess
            board = chess.Board(fen)
            
            # Get all legal moves with statistics
            moves_data = []
            for move in board.legal_moves:
                move_san = board.san(move)
                moves_data.append({
                    'move': move_san,
                    'uci': move.uci(),
                    'count': 1,
                    'wins': 0,
                    'draws': 0,
                    'losses': 0,
                    'win_percent': 0
                })
            
            return jsonify({
                'success': True,
                'fen': fen,
                'moves': moves_data,
                'total_games': len(app.trainer.games) if app.trainer else 0,
            })
        except Exception as e:
            logger.error(f"Error analyzing position: {e}")
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/move', methods=['POST'])
    def play_move():
        """Play a move in the analysis."""
        data = request.json
        move = data.get('move')
        fen = data.get('fen')
        
        try:
            import chess
            board = chess.Board(fen)
            
            # Parse and execute move
            move_obj = board.parse_san(move) if move.isalpha() else chess.Move.from_uci(move)
            if move_obj not in board.legal_moves:
                return jsonify({'error': 'Illegal move'}), 400
            
            board.push(move_obj)
            new_fen = board.fen()
            
            return jsonify({
                'success': True,
                'fen': new_fen,
                'san': board.san(move_obj),
                'fullmove': board.fullmove_number
            })
        except Exception as e:
            logger.error(f"Error playing move: {e}")
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/stats')
    def get_stats():
        """Get overall repertoire statistics."""
        if not app.trainer:
            return jsonify({'error': 'No trainer loaded'}), 400
            
        return jsonify({
            'success': True,
            'games': len(app.trainer.games),
            'positions': app.trainer.stats.get('total_unique_positions', 0),
            'depth': app.trainer.stats.get('repertoire_depth', 0),
            'opponent': app.opponent_name
        })
    
    # ==================== SERVER STARTUP ====================
    
    def run_server():
        app.run(host='127.0.0.1', port=port, debug=debug, use_reloader=False, threaded=True)
    
    print("\n" + "="*80)
    print("  ♞  OPENING REPERTOIRE WEB ANALYZER  ♞".center(80))
    print("="*80)
    if app.opponent_name and app.trainer:
        print(f"\n  Analyzing: {app.opponent_name}")
        print(f"  Games: {len(app.trainer.games)} | Positions: {app.trainer.stats.get('total_unique_positions', 0)}")
    print(f"\n  🌐 Open your browser: http://127.0.0.1:{port}/")
    print(f"\n  [Press Ctrl+C to stop]\n")
    print("="*80 + "\n")
    
    # Start server in background thread
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Open browser
    import time
    time.sleep(1)
    
    try:
        webbrowser.open(f'http://127.0.0.1:{port}/')
    except Exception as e:
        logger.warning(f"Could not open browser: {e}")
    
    # Keep the server running
    try:
        server_thread.join()
    except KeyboardInterrupt:
        print("\n[STOP] Web analyzer stopped.\n")


if __name__ == '__main__':
    from .opening_trainer import OpeningTrainer


    import chess.pgn
    
    # Test with sample games
    print("Testing web trainer...")
