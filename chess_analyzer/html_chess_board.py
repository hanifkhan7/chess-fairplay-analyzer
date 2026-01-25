"""
HTML Chess Board Viewer for Opening Trainer
Displays an interactive chess board with move history.
"""
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class HTMLChessBoard:
    """Generate interactive HTML chess board display."""
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize board generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_board_html(self, fen: str, move_history: List[str], opponent_name: str, 
                           top_moves: Optional[List[tuple]] = None) -> str:
        """
        Generate HTML page with interactive chess board.
        
        Args:
            fen: Board position in FEN notation
            move_history: List of moves played (in algebraic notation)
            opponent_name: Name of opponent
            top_moves: List of (move, stats) tuples for top responses
        
        Returns:
            HTML content
        """
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Opening Trainer: {opponent_name}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.2/chess.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            padding: 40px;
        }}
        
        .board-section {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        
        .chessboard {{
            width: 100%;
            max-width: 500px;
            aspect-ratio: 1;
            background: #8B7355;
            border: 3px solid #2c3e50;
            border-radius: 8px;
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 0;
            margin: 20px 0;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
        }}
        
        .square {{
            aspect-ratio: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3em;
            cursor: pointer;
            transition: background 0.2s;
            user-select: none;
        }}
        
        .square.light {{
            background: #F0D9B5;
        }}
        
        .square.dark {{
            background: #B58863;
        }}
        
        .square:hover {{
            background: #BACA44;
        }}
        
        .square.selected {{
            background: #BACA44;
        }}
        
        .info-section {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        
        .info-card {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            border-radius: 8px;
        }}
        
        .info-card h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        
        .move-history {{
            background: white;
            border: 1px solid #e0e0e0;
            padding: 15px;
            border-radius: 8px;
            max-height: 150px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
        }}
        
        .move {{
            display: inline-block;
            margin: 5px;
            padding: 5px 10px;
            background: #667eea;
            color: white;
            border-radius: 4px;
            font-weight: bold;
        }}
        
        .top-moves {{
            background: white;
            border: 1px solid #e0e0e0;
            padding: 15px;
            border-radius: 8px;
        }}
        
        .top-moves table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }}
        
        .top-moves th {{
            background: #2c3e50;
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: 600;
        }}
        
        .top-moves td {{
            padding: 10px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .top-moves tr:hover {{
            background: #f8f9fa;
        }}
        
        .stat-value {{
            font-weight: bold;
            color: #667eea;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .badge-primary {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .controls {{
            display: flex;
            gap: 10px;
            justify-content: center;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        
        button {{
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            background: #667eea;
            color: white;
        }}
        
        button:hover {{
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }}
        
        button.secondary {{
            background: #6c757d;
        }}
        
        button.secondary:hover {{
            background: #5a6268;
        }}
        
        footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e0e0e0;
            font-size: 0.9em;
        }}
        
        @media (max-width: 1024px) {{
            .content {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>♟️ Opening Trainer</h1>
            <p>Interactive Chess Training Against {opponent_name}</p>
            <p style="margin-top: 10px; font-size: 0.9em; opacity: 0.9;">
                FEN: <code>{fen}</code>
            </p>
        </header>
        
        <div class="content">
            <div class="board-section">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">Chess Board</h2>
                <div id="chessboard" class="chessboard"></div>
                
                <div class="controls">
                    <button onclick="undoMove()">↶ Undo</button>
                    <button onclick="resetBoard()" class="secondary">↻ Reset</button>
                    <button onclick="flipBoard()" class="secondary">⟲ Flip Board</button>
                </div>
                
                <div class="move-history" id="moveHistory">
                    <strong>Move History:</strong><br>
                    {' '.join(f'<span class="move">{move}</span>' for move in move_history) if move_history else 'No moves yet'}
                </div>
            </div>
            
            <div class="info-section">
                <div class="info-card">
                    <h3>📊 Position Info</h3>
                    <p><strong>Move Number:</strong> <span class="stat-value">{len(move_history) // 2 + 1}</span></p>
                    <p><strong>Total Moves:</strong> <span class="stat-value">{len(move_history)}</span></p>
                    <p><strong>Status:</strong> <span class="badge badge-primary">In Progress</span></p>
                </div>
                
                <div class="info-card">
                    <h3>🎯 Top Responses by {opponent_name}</h3>
                    {self._generate_moves_table(top_moves) if top_moves else '<p style="color: #999;">No data yet</p>'}
                </div>
                
                <div class="info-card">
                    <h3>ℹ️ Instructions</h3>
                    <ul style="margin-left: 20px;">
                        <li>Click squares to select moves</li>
                        <li>Or enter moves in algebraic notation (e.g., e4, Nf3)</li>
                        <li>View top responses from opponent's repertoire</li>
                        <li>Use Undo to take back moves</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <footer>
            <p>♟️ Chess Fairplay Analyzer v3.2 | Opening Trainer Module</p>
            <p style="margin-top: 10px;">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>
    
    <script>
        const chess = new Chess('{fen}');
        let boardFlipped = false;
        
        function renderBoard() {{
            const board = document.getElementById('chessboard');
            board.innerHTML = '';
            const squares = chess.board();
            
            for (let row = 0; row < 8; row++) {{
                for (let col = 0; col < 8; col++) {{
                    const displayRow = boardFlipped ? 7 - row : row;
                    const displayCol = boardFlipped ? 7 - col : col;
                    
                    const isLight = (displayRow + displayCol) % 2 === 0;
                    const square = document.createElement('div');
                    square.className = `square ${{isLight ? 'light' : 'dark'}}`;
                    square.id = `sq_${{String.fromCharCode(97 + displayCol)}}${{8 - displayRow}}`;
                    
                    const piece = squares[row][col];
                    if (piece) {{
                        const pieceSymbol = {{
                            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
                            'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔'
                        }}[piece.type];
                        square.innerHTML = pieceSymbol;
                        square.style.color = piece.color === 'w' ? '#f0f0f0' : '#2c3e50';
                    }}
                    
                    square.onclick = () => makeMove(square.id.slice(3));
                    board.appendChild(square);
                }}
            }}
        }}
        
        function makeMove(square) {{
            alert(`Move to ${{square}} clicked. (Interactive board feature under development)`);
        }}
        
        function undoMove() {{
            chess.undo();
            renderBoard();
        }}
        
        function resetBoard() {{
            chess.reset();
            renderBoard();
        }}
        
        function flipBoard() {{
            boardFlipped = !boardFlipped;
            renderBoard();
        }}
        
        renderBoard();
    </script>
</body>
</html>
"""
        return html
    
    def _generate_moves_table(self, top_moves: Optional[List[tuple]]) -> str:
        """Generate HTML table for top moves."""
        if not top_moves:
            return '<p style="color: #999;">No data available</p>'
        
        html = '<table>'
        html += '<thead><tr><th>#</th><th>Move</th><th>Win %</th><th>Count</th></tr></thead>'
        html += '<tbody>'
        
        for i, (move, stats) in enumerate(top_moves[:10], 1):
            win_rate = stats.get('win_rate', 0)
            count = stats.get('count', 0)
            html += f'<tr><td>{i}</td><td><strong>{move}</strong></td>'
            html += f'<td><span class="stat-value">{win_rate:.1f}%</span></td>'
            html += f'<td>{count}</td></tr>'
        
        html += '</tbody></table>'
        return html
    
    def save_board_html(self, fen: str, move_history: List[str], opponent_name: str, 
                        top_moves: Optional[List[tuple]] = None) -> str:
        """Save board HTML to file and return path."""
        from datetime import datetime
        
        html_content = self.generate_board_html(fen, move_history, opponent_name, top_moves)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"trainer_{opponent_name}_{timestamp}.html"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return str(filepath)
        except Exception as e:
            raise Exception(f"Failed to save board HTML: {e}")
