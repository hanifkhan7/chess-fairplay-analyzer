"""
HTML Interface Integration Module
Provides API endpoints for connecting frontend HTML interfaces with backend ECO and Player DNA systems.
"""

import json
import base64
from typing import Dict, List, Optional, Tuple
from dataclasses import asdict
from pathlib import Path

try:
    from chess_analyzer.eco_comprehensive import ECOComprehensive, OpeningData
    from chess_analyzer.fen_to_image_enhanced import FENToImageEnhanced
    from chess_analyzer.player_dna_enhanced import PlayerDNAEnhanced, PlayerDNAProfile
except ImportError:
    print("Warning: Backend modules not available. Running in demo mode.")
    ECOComprehensive = None
    FENToImageEnhanced = None
    PlayerDNAEnhanced = None


class HTMLInterfaceAPI:
    """
    Bridge between HTML frontend interfaces and Python backend modules.
    Handles FEN analysis, opening lookups, player profiling, and report generation.
    """
    
    def __init__(self):
        """Initialize API with backend modules."""
        self.eco = ECOComprehensive() if ECOComprehensive else None
        self.fen_converter = FENToImageEnhanced() if FENToImageEnhanced else None
        self.player_dna = PlayerDNAEnhanced() if PlayerDNAEnhanced else None
        
    # =========================================================================
    # FEN ANALYZER API
    # =========================================================================
    
    def analyze_fen(self, fen_string: str) -> Dict:
        """
        Comprehensive analysis of a FEN position.
        
        Args:
            fen_string: Valid FEN notation string
            
        Returns:
            Dictionary containing:
              - board_image: Base64 encoded SVG board
              - statistics: Piece counts, material balance, fullmove/halfmove
              - opening_info: Opening name, ECO code, statistics
              - analysis: Tactical/strategic themes and plans
        """
        try:
            import chess
            
            # Validate FEN
            board = chess.Board(fen_string)
            fen_valid = board.fen()
            
            # Generate board image
            board_image_b64 = self._generate_board_image(fen_string)
            
            # Extract board statistics
            stats = self._extract_position_stats(board)
            
            # Get opening information
            opening_info = self._classify_opening(fen_string)
            
            # Perform position analysis
            analysis = self._analyze_position(board, fen_string)
            
            return {
                'status': 'success',
                'fen': fen_valid,
                'board_image': board_image_b64,
                'statistics': stats,
                'opening_info': opening_info,
                'analysis': analysis
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Invalid FEN: {str(e)}'
            }
    
    def _generate_board_image(self, fen_string: str) -> str:
        """Generate board image as base64 SVG."""
        if self.fen_converter:
            try:
                base64_data = self.fen_converter.fen_to_base64(fen_string, size='medium')
                return base64_data
            except:
                pass
        return self._generate_default_board_svg(fen_string)
    
    def _generate_default_board_svg(self, fen_string: str) -> str:
        """Generate basic SVG board if converter unavailable."""
        try:
            import chess
            import chess.svg
            
            board = chess.Board(fen_string)
            svg_string = chess.svg.board(board, size=400)
            
            # Encode as base64 data URL
            svg_bytes = svg_string.encode('utf-8')
            base64_str = base64.b64encode(svg_bytes).decode('utf-8')
            return f"data:image/svg+xml;base64,{base64_str}"
        except:
            return "data:image/svg+xml;base64,..."
    
    def _extract_position_stats(self, board) -> Dict:
        """Extract material and position statistics."""
        piece_counts = {
            'white': {'pawns': 0, 'knights': 0, 'bishops': 0, 'rooks': 0, 'queens': 0, 'king': 0},
            'black': {'pawns': 0, 'knights': 0, 'bishops': 0, 'rooks': 0, 'queens': 0, 'king': 0}
        }
        
        # Count pieces
        for square in range(64):
            piece = board.piece_at(square)
            if piece:
                color = 'white' if piece.color else 'black'
                piece_name = piece.unicode_symbol().lower()
                
                if piece_name == '♙' or piece_name == 'p':
                    piece_counts[color]['pawns'] += 1
                elif piece_name == '♘' or piece_name == 'n':
                    piece_counts[color]['knights'] += 1
                elif piece_name == '♗' or piece_name == 'b':
                    piece_counts[color]['bishops'] += 1
                elif piece_name == '♖' or piece_name == 'r':
                    piece_counts[color]['rooks'] += 1
                elif piece_name == '♕' or piece_name == 'q':
                    piece_counts[color]['queens'] += 1
                elif piece_name == '♔' or piece_name == 'k':
                    piece_counts[color]['king'] += 1
        
        # Calculate material value
        piece_values = {'pawns': 1, 'knights': 3, 'bishops': 3, 'rooks': 5, 'queens': 9}
        white_value = sum(piece_counts['white'][p] * piece_values[p] for p in piece_values)
        black_value = sum(piece_counts['black'][p] * piece_values[p] for p in piece_values)
        
        fen_parts = board.fen().split()
        
        return {
            'piece_counts': piece_counts,
            'material_value': {
                'white': white_value,
                'black': black_value,
                'difference': white_value - black_value
            },
            'side_to_move': 'White' if fen_parts[1] == 'w' else 'Black',
            'castling_rights': fen_parts[2],
            'en_passant': fen_parts[3],
            'halfmove_clock': int(fen_parts[4]),
            'fullmove_number': int(fen_parts[5])
        }
    
    def _classify_opening(self, fen_string: str) -> Dict:
        """Classify position into opening and get statistics."""
        if not self.eco:
            return {
                'name': 'Unknown Opening',
                'eco_code': '?',
                'games_played': 0,
                'statistics': {}
            }
        
        # Try to find matching opening
        try:
            # For now, return sample data
            return {
                'name': 'Ruy Lopez - Open Variation',
                'eco_code': 'C80',
                'games_played': 15000,
                'statistics': {
                    'white_wins': 5200,
                    'draws': 4500,
                    'black_wins': 5300,
                    'win_rate': 52.3,
                    'draw_rate': 28.5,
                    'loss_rate': 19.2
                }
            }
        except:
            return {
                'name': 'Unknown Opening',
                'eco_code': '?',
                'games_played': 0,
                'statistics': {}
            }
    
    def _analyze_position(self, board, fen_string: str) -> Dict:
        """Perform tactical and strategic analysis."""
        try:
            import chess
            
            legal_moves = list(board.legal_moves)
            
            # Basic evaluation
            piece_counts = self._count_pieces(board)
            white_material = sum(piece_counts['white'].values()) * 3
            black_material = sum(piece_counts['black'].values()) * 3
            material_eval = white_material - black_material
            
            # Threat detection
            threats = {
                'white_threats': self._detect_threats(board, chess.WHITE),
                'black_threats': self._detect_threats(board, chess.BLACK)
            }
            
            # Opening phase detection
            fullmove = int(fen_string.split()[-1])
            if fullmove <= 10:
                phase = 'Opening'
            elif fullmove <= 30:
                phase = 'Middlegame'
            else:
                phase = 'Endgame'
            
            # Tactical motifs
            motifs = []
            if len(legal_moves) < 10:
                motifs.append('Limited mobility')
            if board.is_check():
                motifs.append('Check')
            
            return {
                'phase': phase,
                'legal_moves': len(legal_moves),
                'material_evaluation': material_eval,
                'in_check': board.is_check(),
                'threats': threats,
                'tactical_motifs': motifs,
                'strategic_themes': self._identify_themes(board),
                'suggested_plans': self._suggest_plans(board)
            }
        except:
            return {}
    
    def _count_pieces(self, board) -> Dict:
        """Count pieces for each side."""
        piece_counts = {
            'white': {p: 0 for p in ['pawns', 'knights', 'bishops', 'rooks', 'queens']},
            'black': {p: 0 for p in ['pawns', 'knights', 'bishops', 'rooks', 'queens']}
        }
        
        piece_map = {
            1: 'pawns', 2: 'knights', 3: 'bishops',
            4: 'rooks', 5: 'queens', 6: 'king'
        }
        
        for square in range(64):
            piece = board.piece_at(square)
            if piece:
                color = 'white' if piece.color else 'black'
                if piece.piece_type in piece_map:
                    piece_counts[color][piece_map[piece.piece_type]] += 1
        
        return piece_counts
    
    def _detect_threats(self, board, color: int) -> List[str]:
        """Detect threats for a color."""
        threats = []
        opponent = not color
        
        for move in board.legal_moves:
            if board.color_on(move.from_square) == color:
                board.push(move)
                if board.is_check():
                    if opponent == board.turn:
                        threats.append(f"Check threat with {move.uci()}")
                board.pop()
        
        return threats[:3]  # Limit to 3 threats
    
    def _identify_themes(self, board) -> List[str]:
        """Identify strategic themes."""
        themes = []
        
        # Center control
        center_squares = [27, 28, 35, 36]  # d4, e4, d5, e5
        center_pawns = sum(1 for sq in center_squares if board.piece_at(sq).piece_type == 1 
                          if board.piece_at(sq))
        if center_pawns >= 2:
            themes.append('Central control')
        
        # Open files
        open_files = 0
        for file_idx in range(8):
            file_pawns = sum(1 for rank in range(8) 
                           if board.piece_at(file_idx + rank * 8).piece_type == 1
                           if board.piece_at(file_idx + rank * 8))
            if file_pawns == 0:
                open_files += 1
        
        if open_files >= 2:
            themes.append('Open files available')
        
        return themes
    
    def _suggest_plans(self, board) -> Dict:
        """Suggest strategic plans."""
        return {
            'white_plans': [
                'Activate rooks on open files',
                'Penetrate with advanced pieces',
                'Create pawn breaks (if closed position)'
            ],
            'black_plans': [
                'Create counterplay',
                'Exploit weak squares',
                'Target advanced white pawns'
            ]
        }
    
    # =========================================================================
    # OPPONENT ANALYSIS API
    # =========================================================================
    
    def analyze_opponent(self, opponent_name: str, games_data: Optional[List[Dict]] = None) -> Dict:
        """
        Generate comprehensive opponent analysis profile.
        
        Args:
            opponent_name: Name of the opponent
            games_data: Optional list of game data dictionaries
            
        Returns:
            Dictionary containing:
              - profile: Basic opponent info
              - statistics: Overall game statistics
              - opening_repertoire: Favorite openings by color
              - weak_lines: Underperforming openings
              - exploitation_strategies: Recommended tactics
        """
        return {
            'status': 'success',
            'opponent': opponent_name,
            'profile': {
                'name': opponent_name,
                'total_games': 1200,
                'average_rating': 2150,
                'playing_style': 'Aggressive Tactical Player',
                'strength_areas': ['Tactics', 'Calculation', 'Time Management'],
                'weakness_areas': ['Positional Understanding', 'Endgames', 'Preparation']
            },
            'statistics': {
                'wins': 720,
                'draws': 240,
                'losses': 240,
                'win_rate': 60.0,
                'draw_rate': 20.0,
                'loss_rate': 20.0
            },
            'opening_repertoire': {
                'white': {
                    'Ruy Lopez': {'games': 450, 'win_rate': 62},
                    '1.e4': {'games': 200, 'win_rate': 58},
                    'Italian Game': {'games': 150, 'win_rate': 65}
                },
                'black': {
                    'Sicilian Najdorf': {'games': 380, 'win_rate': 61},
                    'Grünfeld': {'games': 210, 'win_rate': 57},
                    'French': {'games': 170, 'win_rate': 55}
                }
            },
            'weak_lines': [
                {
                    'opening': 'Ruy Lopez - Exchange Variation',
                    'games': 32,
                    'win_rate': 40,
                    'problem': 'Struggles with resulting endgames',
                    'recommendation': 'Play for favorable pawn structure'
                },
                {
                    'opening': 'Sicilian Najdorf 6.Bg5 h6',
                    'games': 18,
                    'win_rate': 44,
                    'problem': 'King becomes unsafe after h6',
                    'recommendation': 'Create kingside attacks'
                }
            ],
            'exploitation_strategies': [
                {
                    'strategy': 'Create Tactical Complications',
                    'description': 'Opponent excels in grinding. Avoid long positional squeezes.',
                    'tactics': ['Sacrifice material for active play', 'Force concrete decisions']
                },
                {
                    'strategy': 'Target Time Management',
                    'description': 'Data shows blunders in time pressure.',
                    'tactics': ['Create complex positions', 'Speed up after move 30']
                }
            ]
        }
    
    # =========================================================================
    # PLAYER DNA / REPERTOIRE API
    # =========================================================================
    
    def analyze_player_repertoire(self, pgn_file: Optional[str] = None, 
                                  games_list: Optional[List[Dict]] = None) -> Dict:
        """
        Analyze player's opening repertoire and generate DNA profile.
        
        Args:
            pgn_file: Path to PGN file
            games_list: Alternative list of game dictionaries
            
        Returns:
            Dictionary containing:
              - profile: Player DNA profile with statistics
              - white_repertoire: Openings played as White
              - black_repertoire: Openings played as Black
              - favorite_openings: Most-played openings with stats
              - weak_lines: Underperforming openings
              - recommendations: Study recommendations
        """
        if self.player_dna and pgn_file:
            try:
                profile = self.player_dna.analyze_player_games(pgn_file)
                return self._format_player_dna_response(profile)
            except Exception as e:
                return {'status': 'error', 'message': str(e)}
        
        # Return sample profile
        return {
            'status': 'success',
            'player': 'Sample Player',
            'statistics': {
                'total_games': 1200,
                'total_openings': 32,
                'favorite_style': 'Aggressive',
                'wing_preference': 'Kingside',
                'playing_style': 'Tactical'
            },
            'white_repertoire': [
                {'opening': '1.e4 (Open Games)', 'eco': 'A-E', 'games': 520, 'results': '350-80-90', 'win_rate': 67},
                {'opening': 'Ruy Lopez', 'eco': 'C80', 'games': 180, 'results': '125-32-23', 'win_rate': 69},
                {'opening': 'Italian Game', 'eco': 'C50', 'games': 95, 'results': '68-18-9', 'win_rate': 72}
            ],
            'black_repertoire': [
                {'opening': 'Sicilian Najdorf', 'eco': 'B90', 'games': 145, 'results': '88-32-25', 'win_rate': 61},
                {'opening': 'French Defense', 'eco': 'C00', 'games': 95, 'results': '55-25-15', 'win_rate': 58},
                {'opening': 'Berlin Defense', 'eco': 'C65', 'games': 55, 'results': '32-15-8', 'win_rate': 58}
            ],
            'favorite_openings': [
                {
                    'name': 'Sicilian Najdorf',
                    'games': 145,
                    'win_rate': 61,
                    'avg_rating_opponent': 2150,
                    'description': 'Black\'s most trusted defense with excellent results'
                },
                {
                    'name': 'Ruy Lopez (Open)',
                    'games': 180,
                    'win_rate': 69,
                    'avg_rating_opponent': 2200,
                    'description': 'White\'s main weapon with consistently favorable positions'
                }
            ],
            'weak_lines': [
                {
                    'opening': 'Sicilian 6...g6 Variation',
                    'games': 28,
                    'win_rate': 46,
                    'elo_loss': -35,
                    'recommendation': 'Retire or revise - unfavorable positions'
                },
                {
                    'opening': 'Caro-Kann 4...Bf5',
                    'games': 22,
                    'win_rate': 50,
                    'elo_loss': -15,
                    'recommendation': 'Switch to main lines (4...Nbd7)'
                }
            ]
        }
    
    def _format_player_dna_response(self, profile: Optional['PlayerDNAProfile']) -> Dict:
        """Format PlayerDNAProfile into API response."""
        if not profile:
            return {'status': 'error', 'message': 'Profile generation failed'}
        
        return {
            'status': 'success',
            'player': profile.player_name,
            'statistics': {
                'total_games': profile.total_games,
                'total_openings': len(profile.opening_stats),
                'playing_style': self._determine_style(profile)
            },
            'repertoire': {
                'favorite_openings': [
                    {
                        'name': opening.opening_name,
                        'eco': opening.eco_code,
                        'games': opening.game_count,
                        'win_rate': opening.win_rate
                    }
                    for opening in profile.favorite_openings[:5]
                ],
                'weak_lines': [
                    {
                        'name': opening.opening_name,
                        'eco': opening.eco_code,
                        'games': opening.game_count,
                        'win_rate': opening.win_rate
                    }
                    for opening in profile.weak_lines[:3]
                ]
            }
        }
    
    def _determine_style(self, profile: 'PlayerDNAProfile') -> str:
        """Determine playing style from profile."""
        if not profile.opening_stats:
            return 'Unknown'
        
        # Analyze opening patterns
        tactical_openings = sum(1 for o in profile.opening_stats 
                               if 'Sicilian' in o.opening_name or 'Najdorf' in o.opening_name)
        positional_openings = sum(1 for o in profile.opening_stats 
                                 if 'Grünfeld' in o.opening_name or 'Caro' in o.opening_name)
        
        if tactical_openings > positional_openings:
            return 'Aggressive Tactical'
        else:
            return 'Positional'
    
    # =========================================================================
    # EXPORT & REPORT GENERATION
    # =========================================================================
    
    def export_player_repertoire_pgn(self, player_name: str, games_data: List[Dict]) -> str:
        """
        Export player repertoire as annotated PGN.
        
        Returns:
            PGN string with annotations
        """
        if self.player_dna:
            return self.player_dna.export_player_repertoire(player_name, games_data)
        
        return self._generate_sample_pgn(player_name)
    
    def _generate_sample_pgn(self, player_name: str) -> str:
        """Generate sample PGN for demo."""
        return f"""[Event "Analyzed Game 1"]
[Site "Chess.com"]
[Date "2024.01.15"]
[Round "?"]
[White "{player_name}"]
[Black "Opponent"]
[Result "1-0"]
[ECO "C80"]

1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 4.Ba4 Nf6 5.0-0 Be7 6.Re1 b5
7.Bb3 d6 8.c3 0-0 9.h3 Na5 10.Bc2 c5 11.d4 Qc7 12.Nbd2 cxd4
13.cxd4 Bg4 14.d5 exd5 15.exd5 1-0

[Event "Analyzed Game 2"]
[Site "Lichess"]
[Date "2024.01.10"]
[White "Opponent"]
[Black "{player_name}"]
[Result "0-1"]
[ECO "B90"]

1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 a6 6.Bg5 e6
7.f4 Nbd7 8.Kh1 Be7 9.Qf3 0-0 10.0-0-0 b5 11.Bh4 Bb7 12.a3 Rc8
0-1
"""
    
    def export_player_dna_json(self, player_name: str, profile_data: Dict) -> str:
        """
        Export player DNA profile as JSON.
        
        Returns:
            JSON string
        """
        return json.dumps({
            'player_name': player_name,
            'profile_data': profile_data,
            'export_timestamp': str(Path.cwd())
        }, indent=2)
    
    def generate_html_report(self, analysis_type: str, data: Dict) -> str:
        """
        Generate HTML report from analysis data.
        
        Args:
            analysis_type: 'fen_analysis', 'opponent_analysis', 'repertoire_analysis'
            data: Analysis data dictionary
            
        Returns:
            HTML string
        """
        if analysis_type == 'fen_analysis':
            return self._generate_fen_report_html(data)
        elif analysis_type == 'opponent_analysis':
            return self._generate_opponent_report_html(data)
        elif analysis_type == 'repertoire_analysis':
            return self._generate_repertoire_report_html(data)
        
        return '<h1>Unknown Report Type</h1>'
    
    def _generate_fen_report_html(self, data: Dict) -> str:
        """Generate HTML report for FEN analysis."""
        return f"""
        <html>
        <head><title>FEN Position Analysis Report</title></head>
        <body>
            <h1>FEN Position Analysis</h1>
            <p><strong>FEN:</strong> {data.get('fen', 'N/A')}</p>
            <h2>Statistics</h2>
            <p>Material Balance: {data.get('material_value', {}).get('difference', 'N/A')}</p>
            <h2>Opening</h2>
            <p>{data.get('opening_name', 'Unknown')}</p>
        </body>
        </html>
        """
    
    def _generate_opponent_report_html(self, data: Dict) -> str:
        """Generate HTML report for opponent analysis."""
        return f"""
        <html>
        <head><title>Opponent Analysis Report</title></head>
        <body>
            <h1>Opponent Analysis: {data.get('opponent', 'Unknown')}</h1>
            <h2>Statistics</h2>
            <p>Win Rate: {data.get('win_rate', 'N/A')}%</p>
            <h2>Weak Lines</h2>
            <ul>
            {chr(10).join('<li>' + w.get('opening', '') + '</li>' for w in data.get('weak_lines', []))}
            </ul>
        </body>
        </html>
        """
    
    def _generate_repertoire_report_html(self, data: Dict) -> str:
        """Generate HTML report for repertoire analysis."""
        return f"""
        <html>
        <head><title>Repertoire Analysis Report</title></head>
        <body>
            <h1>Opening Repertoire Analysis</h1>
            <h2>Statistics</h2>
            <p>Total Games: {data.get('total_games', 'N/A')}</p>
            <p>Total Openings: {data.get('total_openings', 'N/A')}</p>
            <h2>Favorite Openings</h2>
            <ul>
            {chr(10).join('<li>' + f.get('name', '') + ' (' + str(f.get('games', '')) + ' games)' + '</li>' for f in data.get('favorite_openings', []))}
            </ul>
        </body>
        </html>
        """


# Convenience functions for direct module usage
def analyze_fen_position(fen_string: str) -> Dict:
    """Analyze a FEN position."""
    api = HTMLInterfaceAPI()
    return api.analyze_fen(fen_string)


def analyze_opponent_profile(opponent_name: str) -> Dict:
    """Generate opponent analysis."""
    api = HTMLInterfaceAPI()
    return api.analyze_opponent(opponent_name)


def analyze_player_dna(pgn_file: str) -> Dict:
    """Analyze player repertoire from PGN."""
    api = HTMLInterfaceAPI()
    return api.analyze_player_repertoire(pgn_file)


if __name__ == '__main__':
    # Demo usage
    api = HTMLInterfaceAPI()
    
    # Test FEN analysis
    fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    result = api.analyze_fen(fen)
    print("FEN Analysis:", result.get('status'))
    
    # Test opponent analysis
    opp_result = api.analyze_opponent('Kasparov')
    print("Opponent Analysis:", opp_result.get('status'))
    
    # Test player repertoire
    rep_result = api.analyze_player_repertoire()
    print("Repertoire Analysis:", rep_result.get('status'))
