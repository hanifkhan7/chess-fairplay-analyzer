// Global variables
let board;
let game;
let currentFEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    game = new Chess();
    initializeBoard();
});

function initializeBoard() {
    const cfg = {
        draggable: true,
        position: 'start',
        onDragStart: onDragStart,
        onDrop: onDrop,
        onSnapEnd: onSnapEnd,
        pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png'
    };
    board = ChessBoard('board', cfg);
}

function onDragStart(source, piece, position, orientation) {
    if (game.game_over()) return false;
    if ((game.turn() === 'w' && piece.search(/^w/) === -1) ||
        (game.turn() === 'b' && piece.search(/^b/) === -1)) {
        return false;
    }
}

function onDrop(source, target) {
    const move = game.move({
        from: source,
        to: target,
        promotion: 'q'
    });

    if (move === null) return 'snapback';

    updateAfterMove(move.san);
}

function onSnapEnd() {
    board.position(game.fen());
}

function startTraining() {
    const opponent = document.getElementById('opponent').value.trim();
    const games = document.getElementById('games').value;
    const colors = document.getElementById('colors').value;
    const statusDiv = document.getElementById('setup-status');

    if (!opponent) {
        showStatus(statusDiv, 'Please enter an opponent username', 'error');
        return;
    }

    showStatus(statusDiv, 'Initializing trainer...', 'loading');
    
    fetch('/api/setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ opponent, games, colors })
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            showStatus(statusDiv, data.error, 'error');
            return;
        }
        
        // Show trainer screen
        document.getElementById('setup-screen').classList.remove('active');
        document.getElementById('trainer-screen').classList.add('active');
        
        // Show stats
        showStatus(document.getElementById('status-message'), 
            `✓ Trainer initialized! ${data.stats.games} games, ${data.stats.positions} positions, ${data.stats.colors}`, 
            'success');
        
        // Start new game
        startNewGame();
    })
    .catch(err => showStatus(statusDiv, err.message, 'error'));
}

function startNewGame() {
    fetch('/api/game/new', { method: 'POST' })
    .then(r => r.json())
    .then(data => {
        game = new Chess(data.fen);
        board.position(game.fen());
        currentFEN = data.fen;
        updateTopMoves(data.top_responses);
        updateStats();
    });
}

function playMove() {
    const moveInput = document.getElementById('move-input').value.trim().toUpperCase();
    
    if (!moveInput) {
        showStatus(document.getElementById('status-message'), 'Please enter a move', 'error');
        return;
    }

    // Check if it's a number (selection from top moves)
    if (/^\d+$/.test(moveInput)) {
        selectMove(parseInt(moveInput));
        document.getElementById('move-input').value = '';
        return;
    }

    fetch('/api/game/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ move: moveInput })
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            let msg = data.error;
            if (data.legal_moves && data.legal_moves.length > 0) {
                msg += ` | Legal: ${data.legal_moves.join(', ')}`;
            }
            showStatus(document.getElementById('status-message'), msg, 'error');
            return;
        }

        // Update board
        game = new Chess(data.fen);
        board.position(game.fen());

        // Show message
        let message = `✓ You played: ${data.user_move}`;
        if (data.opponent_move) {
            message += ` → Opponent played: ${data.opponent_move}`;
            message += ` (${(data.opponent_stats.win_rate).toFixed(1)}% win rate)`;
        } else if (data.message) {
            message = data.message;
        }

        showStatus(document.getElementById('status-message'), message, 
                  data.in_repertoire ? 'success' : 'warning');

        // Update moves
        updateTopMoves(data.top_responses);
        updateStats();
        document.getElementById('move-input').value = '';

        if (data.game_over) {
            showStatus(document.getElementById('status-message'), 'Game Over!', 'warning');
        }
    });
}

function selectMove(num) {
    fetch('/api/game/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selection: num })
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            showStatus(document.getElementById('status-message'), data.error, 'error');
            return;
        }

        game = new Chess(data.fen);
        board.position(game.fen());

        const msg = `✓ Selected move ${num}: ${data.selected_move} (${(data.selected_stats.win_rate).toFixed(1)}% win rate)`;
        showStatus(document.getElementById('status-message'), msg, 'success');

        updateTopMoves(data.top_responses);
        updateStats();
    });
}

function undoMove() {
    fetch('/api/game/undo', { method: 'POST' })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            showStatus(document.getElementById('status-message'), data.error, 'error');
            return;
        }

        game = new Chess(data.fen);
        board.position(game.fen());
        updateTopMoves(data.top_responses);
        updateStats();
    });
}

function resetGame() {
    if (confirm('Reset game to starting position?')) {
        fetch('/api/game/reset', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            game = new Chess(data.fen);
            board.position(game.fen());
            updateTopMoves(data.top_responses);
            updateStats();
            showStatus(document.getElementById('status-message'), 'Game reset', 'success');
        });
    }
}

function updateAfterMove(moveSan) {
    // Auto-submit the move via API
    const moveInput = document.getElementById('move-input');
    moveInput.value = moveSan;
    playMove();
}

function updateTopMoves(moves) {
    const listDiv = document.getElementById('top-moves-list');
    
    if (!moves || moves.length === 0) {
        listDiv.innerHTML = '<p class="placeholder">No moves available</p>';
        return;
    }

    let html = '';
    moves.forEach((move, index) => {
        html += `
        <div class="move-item" onclick="selectMove(${index + 1})">
            <div class="move-item-header">
                <span class="move-item-move">${index + 1}. ${move.move}</span>
                <span class="move-item-count">${move.count}x</span>
            </div>
            <div class="move-item-stats">
                <div class="stat-box">
                    <div class="stat-value">${move.win_rate.toFixed(1)}%</div>
                    <div class="stat-label">Win</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">${move.draw_rate.toFixed(1)}%</div>
                    <div class="stat-label">Draw</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">${move.loss_rate.toFixed(1)}%</div>
                    <div class="stat-label">Loss</div>
                </div>
            </div>
        </div>
        `;
    });
    
    listDiv.innerHTML = html;
}

function updateStats() {
    fetch('/api/game/stats')
    .then(r => r.json())
    .then(data => {
        document.getElementById('stat-moves').textContent = data.moves_played;
        document.getElementById('stat-in-rep').textContent = data.in_repertoire_count;
        document.getElementById('stat-out-rep').textContent = data.out_of_repertoire_count;
        document.getElementById('stat-win-rate').textContent = data.estimated_win_rate.toFixed(1) + '%';
        
        const moveSeq = document.getElementById('move-sequence');
        if (data.move_sequence) {
            moveSeq.innerHTML = `<code>${data.move_sequence}</code>`;
            moveSeq.classList.remove('placeholder');
        } else {
            moveSeq.innerHTML = '<p class="placeholder">No moves yet</p>';
            moveSeq.classList.add('placeholder');
        }
    });
}

function showStatus(element, message, type) {
    element.textContent = message;
    element.className = 'status-message ' + type;
    
    if (type === 'error') {
        setTimeout(() => {
            element.textContent = '';
            element.className = 'status-message';
        }, 5000);
    }
}
