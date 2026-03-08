"""
Enhanced ECO System - Comprehensive Opening Database with PGN and FEN
Provides real opening names with variations, canonical PGN snapshots,
and FEN position data for accurate reporting.

Priority: ACCURACY
"""

import chess
import chess.pgn
import logging
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass
import io
import json

logger = logging.getLogger(__name__)


@dataclass
class OpeningInfo:
    """Complete information about an opening."""
    eco_code: str
    name: str
    variation: str
    canonical_pgn: str  # Main line PGN
    final_fen: str      # FEN of final position in main line
    move_count: int     # Number of moves in main line
    frequency_count: int = 0  # Times this ECO appears in analysis
    win_rate: float = 0.0
    draw_rate: float = 0.0
    loss_rate: float = 0.0
    

# Comprehensive ECO Database with Opening Information
# Format: ECO -> {name, variation, canonical_pgn, final_fen}
ECO_COMPREHENSIVE_DATABASE: Dict[str, Dict] = {
    # A-codes: Unusual Openings and King's Indian Attack
    "A00": {
        "name": "Irregular Opening",
        "variation": "Null Move",
        "canonical_pgn": "1.a3",
        "final_fen": "rnbqkbnr/pppppppp/8/8/8/P7/1PPPPPPP/RNBQKBNR b KQkq - 0 1",
    },
    "A01": {
        "name": "Larsen's Opening",
        "variation": "1.b3",
        "canonical_pgn": "1.b3",
        "final_fen": "rnbqkbnr/pppppppp/8/8/8/1P6/P1PPPPPP/RNBQKBNR b KQkq - 0 1",
    },
    "A02": {
        "name": "Bird's Opening",
        "variation": "1.f4",
        "canonical_pgn": "1.f4",
        "final_fen": "rnbqkbnr/pppppppp/8/8/5P2/8/PPPPP1PP/RNBQKBNR b KQkq f3 0 1",
    },
    "A04": {
        "name": "Reti Opening",
        "variation": "1.Nf3",
        "canonical_pgn": "1.Nf3 d5 2.c4",
        "final_fen": "rnbqkbnr/ppp1pppp/8/3p4/2P5/5N2/PP1PPPPP/RNBQKB1R b KQkq c3 0 2",
    },
    "A07": {
        "name": "King's Indian Attack",
        "variation": "1.Nf3 d5 2.g3",
        "canonical_pgn": "1.Nf3 d5 2.g3",
        "final_fen": "rnbqkbnr/ppp1pppp/8/3p4/8/5NP1/PPPPP2P/RNBQKB1R b KQkq - 0 2",
    },
    
    # B-codes: 1.e4 Second Move Defenses
    "B01": {
        "name": "Scandinavian Defense",
        "variation": "1.e4 d5",
        "canonical_pgn": "1.e4 d5 2.exd5 Qxd5 3.Nc3",
        "final_fen": "rnb1kbnr/ppp1pppp/8/3q4/8/2N5/PPPP1PPP/R1BQKBNR b KQkq - 1 3",
    },
    "B02": {
        "name": "Alekhine's Defense",
        "variation": "1.e4 Nf6",
        "canonical_pgn": "1.e4 Nf6 2.e5 Nd5 3.d4",
        "final_fen": "rnbqkb1r/pppppppp/8/3Np3/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 3",
    },
    "B06": {
        "name": "Modern Defense (Robatsch)",
        "variation": "1.e4 g6",
        "canonical_pgn": "1.e4 g6 2.d4 Bg7 3.Nc3",
        "final_fen": "rnbqkbnr/pppp1p1p/6p1/8/3P4/2N5/PPP1PPPP/R1BQKBNR b KQkq - 0 3",
    },
    "B09": {
        "name": "French Defense",
        "variation": "1.e4 e6",
        "canonical_pgn": "1.e4 e6 2.d4 d5 3.Nc3",
        "final_fen": "rnbqkbnr/ppp2ppp/4p3/3p4/3P4/2N5/PPP1PPPP/R1BQKBNR b KQkq d3 0 3",
    },
    "B10": {
        "name": "Caro-Kann Defense",
        "variation": "1.e4 c6",
        "canonical_pgn": "1.e4 c6 2.d4 d5 3.Nc3",
        "final_fen": "rnbqkbnr/pp2pppp/2p5/3p4/3P4/2N5/PPP1PPPP/R1BQKBNR b KQkq d3 0 3",
    },
    # B20-B99: Sicilian Defense variations
    "B20": {
        "name": "Sicilian Defense",
        "variation": "1.e4 c5",
        "canonical_pgn": "1.e4 c5 2.Nf3 d6 3.d4",
        "final_fen": "rnbqkbnr/pp2pppp/3p4/2p5/3P4/5N2/PPP1PPPP/RNBQKB1R b KQkq - 0 3",
    },
    "B30": {
        "name": "Sicilian Defense",
        "variation": "Closed Variation",
        "canonical_pgn": "1.e4 c5 2.Nc3",
        "final_fen": "rnbqkbnr/pp2pppp/8/2p5/4P3/2N5/PPPP1PPP/R1BQKBNR b KQkq - 1 2",
    },
    "B32": {
        "name": "Sicilian Sveshnikov",
        "variation": "1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 e5",
        "canonical_pgn": "1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 e5",
        "final_fen": "rnbqkb1r/pp2p1pp/3p1n2/4p3/4N3/2N5/PPPP1PPP/R1BQKB1R w KQkq - 0 6",
    },
    "B70": {
        "name": "Sicilian Dragon",
        "variation": "1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 g6",
        "canonical_pgn": "1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 g6",
        "final_fen": "rnbqkb1r/pp3p1p/3p1np1/8/4N3/2N5/PPPP1PPP/R1BQKB1R w KQkq - 0 6",
    },
    "B80": {
        "name": "Sicilian Najdorf",
        "variation": "1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 a6",
        "canonical_pgn": "1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 a6",
        "final_fen": "rnbqkb1r/1p2pppp/p2p1n2/8/4N3/2N5/PPPP1PPP/R1BQKB1R w KQkq - 0 6",
    },
    
    # C-codes: 1.e4 e5 Openings
    "C00": {
        "name": "French Defense",
        "variation": "",
        "canonical_pgn": "1.e4 e6",
        "final_fen": "rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
    },
    "C20": {
        "name": "King's Pawn Game",
        "variation": "1.e4 e5",
        "canonical_pgn": "1.e4 e5",
        "final_fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 1",
    },
    "C21": {
        "name": "Danish Gambit",
        "variation": "1.e4 e5 2.d4 exd4 3.c3",
        "canonical_pgn": "1.e4 e5 2.d4 exd4 3.c3",
        "final_fen": "rnbqkbnr/pppp1ppp/8/8/3pp3/2P5/PP1P1PPP/RNBQKBNR b KQkq - 0 3",
    },
    "C24": {
        "name": "Bishop's Opening",
        "variation": "1.e4 e5 2.Bc4",
        "canonical_pgn": "1.e4 e5 2.Bc4 Nf6",
        "final_fen": "rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 1 3",
    },
    "C25": {
        "name": "Vienna Game",
        "variation": "1.e4 e5 2.Nc3",
        "canonical_pgn": "1.e4 e5 2.Nc3 Nf6 3.g3",
        "final_fen": "rnbqkb1r/pppp1ppp/5n2/4p3/4P3/2N3P1/PPPP1P1P/R1BQKBNR b KQkq - 0 3",
    },
    "C30": {
        "name": "King's Gambit",
        "variation": "1.e4 e5 2.f4",
        "canonical_pgn": "1.e4 e5 2.f4 exf4 3.Nf3",
        "final_fen": "rnbqkbnr/pppp1ppp/8/8/4Pp2/5N2/PPPP1PPP/RNBQKB1R b KQkq - 0 3",
    },
    "C40": {
        "name": "Irregular Opening",
        "variation": "1.e4 e5 2.Nf3",
        "canonical_pgn": "1.e4 e5 2.Nf3",
        "final_fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
    },
    "C41": {
        "name": "Philidor Defense",
        "variation": "1.e4 e5 2.Nf3 d6",
        "canonical_pgn": "1.e4 e5 2.Nf3 d6 3.d4",
        "final_fen": "rnbqkbnr/ppp2ppp/3p4/4p3/3PP3/5N2/PPPP1PPP/RNBQKB1R b KQkq d3 0 3",
    },
    "C44": {
        "name": "Scotch Game",
        "variation": "1.e4 e5 2.Nf3 Nc6 3.d4",
        "canonical_pgn": "1.e4 e5 2.Nf3 Nc6 3.d4 exd4 4.Nxd4",
        "final_fen": "r1bqkbnr/pppp1ppp/2n5/8/3NN3/8/PPPP1PPP/R1BQKB1R b KQkq - 0 4",
    },
    "C45": {
        "name": "Scotch Game",
        "variation": "Open",
        "canonical_pgn": "1.e4 e5 2.Nf3 Nc6 3.d4 exd4 4.Nxd4 Nf6 5.Nc3",
        "final_fen": "r1bqkb1r/pppp1ppp/2n2n2/8/3NN3/2N5/PPPP1PPP/R1BQKB1R b KQkq - 1 5",
    },
    "C50": {
        "name": "Italian Game",
        "variation": "Giuoco Piano",
        "canonical_pgn": "1.e4 e5 2.Nf3 Nc6 3.Bc4 Bc5",
        "final_fen": "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 1 4",
    },
    "C51": {
        "name": "Italian Game",
        "variation": "Evans Gambit",
        "canonical_pgn": "1.e4 e5 2.Nf3 Nc6 3.Bc4 Bc5 4.b4",
        "final_fen": "r1bqk1nr/pppp1ppp/2n5/2b1p3/1PB1P3/5N2/P1PP1PPP/RNBQK2R b KQkq b3 0 4",
    },
    "C54": {
        "name": "Italian Game",
        "variation": "Two Knights Defense, Main Line",
        "canonical_pgn": "1.e4 e5 2.Nf3 Nc6 3.Bc4 Nf6 4.Ng5",
        "final_fen": "r1bqkb1r/pppp1ppp/2n2n2/4p1N1/2B1P3/8/PPPP1PPP/RNBQK2R b KQkq - 0 4",
    },
    "C60": {
        "name": "Ruy Lopez (Spanish Opening)",
        "variation": "1.e4 e5 2.Nf3 Nc6 3.Bb5",
        "canonical_pgn": "1.e4 e5 2.Nf3 Nc6 3.Bb5",
        "final_fen": "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 1 3",
    },
    "C65": {
        "name": "Ruy Lopez",
        "variation": "Berlin Defense",
        "canonical_pgn": "1.e4 e5 2.Nf3 Nc6 3.Bb5 Nf6",
        "final_fen": "r1bqkb1r/pppp1ppp/2n2n2/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 2 4",
    },
    "C67": {
        "name": "Ruy Lopez",
        "variation": "Berlin Defense, Open Variation",
        "canonical_pgn": "1.e4 e5 2.Nf3 Nc6 3.Bb5 Nf6 4.0-0 Nxe4 5.d4",
        "final_fen": "r1bqkb1r/pppp1ppp/2n5/1B2P3/3Pn3/5N2/PPPP1PPP/RNBQKB1R b KQkq d3 0 5",
    },
    "C70": {
        "name": "Ruy Lopez",
        "variation": "5...a6",
        "canonical_pgn": "1.e4 e5 2.Nf3 Nc6 3.Bb5 a6",
        "final_fen": "r1bqkbnr/1ppp1ppp/p1n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 4",
    },
    "C77": {
        "name": "Ruy Lopez",
        "variation": "3...Nf6",
        "canonical_pgn": "1.e4 e5 2.Nf3 Nc6 3.Bb5 Nf6",
        "final_fen": "r1bqkb1r/pppp1ppp/2n2n2/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 2 4",
    },
    "C80": {
        "name": "Ruy Lopez",
        "variation": "Open Defense",
        "canonical_pgn": "1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 4.Ba4 Nf6 5.0-0 Nxe4",
        "final_fen": "r1bqkb1r/1ppp1ppp/p1n5/1B2p3/R3n3/5N2/PPPP1PPP/1NBQKB2 b KQkq - 1 5",
    },
    "C85": {
        "name": "Ruy Lopez",
        "variation": "Closed Defense",
        "canonical_pgn": "1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 4.Ba4 Nf6 5.0-0 Be7",
        "final_fen": "r1bqk2r/1ppp1ppp/p1n2n2/1B2p3/R3P3/5N2/PPPP1PPP/1NBQKB1R b KQkq - 0 6",
    },
    "C88": {
        "name": "Ruy Lopez",
        "variation": "Closed, 7...d6",
        "canonical_pgn": "1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 4.Ba4 Nf6 5.0-0 Be7 6.Re1 b5 7.Bb3 d6",
        "final_fen": "r1bqk2r/1p2bppp/p1np1n2/1B2p3/4P3/1B3N2/PPPP1PPP/RNBQ1R1K b KQkq - 0 8",
    },
    "C90": {
        "name": "Ruy Lopez",
        "variation": "Open, 9.h3",
        "canonical_pgn": "1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 4.Ba4 Nf6 5.0-0 Nxe4 6.d4 b5",
        "final_fen": "r1bqkb1r/2pp1ppp/p1n5/1p2p3/R1PPn3/5N2/PPPP1PPP/1NBQKB1R b KQkq - 0 7",
    },
    "C95": {
        "name": "Ruy Lopez",
        "variation": "Closed, 9...h6",
        "canonical_pgn": "1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 4.Ba4 Nf6 5.0-0 Be7 6.Re1 b5 7.Bb3 d6 8.c3 0-0 9.h3",
        "final_fen": "r1bq1rk1/1p2bppp/p1np1n2/1B2p3/4P3/1B3NP1/PPPP1P1P/RNBQ1R1K b KQkq - 0 9",
    },
    
    # D-codes: 1.d4 d5 (Queen's Pawn Openings)
    "D00": {
        "name": "Queen's Pawn",
        "variation": "Irregular",
        "canonical_pgn": "1.d4",
        "final_fen": "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1",
    },
    "D04": {
        "name": "Queen's Pawn",
        "variation": "School Variation",
        "canonical_pgn": "1.d4 d5 2.Nf3 c5 3.dxc5",
        "final_fen": "rnbqkbnr/pp2pppp/8/2pP4/8/5N2/PPP1PPPP/RNBQKB1R b KQkq - 0 3",
    },
    "D05": {
        "name": "Queen's Pawn Game",
        "variation": "Colle System",
        "canonical_pgn": "1.d4 d5 2.Nf3 Nf6 3.e3",
        "final_fen": "rnbqkb1r/ppp1pppp/5n2/3p4/3P4/4PN2/PPP2PPP/RNBQKB1R b KQkq - 1 3",
    },
    "D10": {
        "name": "Queen's Gambit Declined",
        "variation": "Slav, Semi-Slav",
        "canonical_pgn": "1.d4 d5 2.c4 c6",
        "final_fen": "rnbqkbnr/pp1ppppp/2p5/3p4/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3",
    },
    "D15": {
        "name": "Queen's Gambit Declined",
        "variation": "Slav, 3...dxc4",
        "canonical_pgn": "1.d4 d5 2.c4 c6 3.Nc3 Nf6 4.Nf3 dxc4",
        "final_fen": "rnbqkb1r/pp2pppp/2p2n2/8/2pP4/2N2N2/PPP1PPPP/R1BQKB1R w KQkq - 0 5",
    },
    "D20": {
        "name": "Queen's Gambit Accepted",
        "variation": "",
        "canonical_pgn": "1.d4 d5 2.c4 dxc4",
        "final_fen": "rnbqkbnr/pppp1ppp/8/8/3Pp3/8/PPP1PPPP/RNBQKBNR w KQkq e3 0 3",
    },
    "D30": {
        "name": "Queen's Gambit Declined",
        "variation": "Minor Variations",
        "canonical_pgn": "1.d4 d5 2.c4 e6",
        "final_fen": "rnbqkbnr/ppp2ppp/4p3/3p4/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3",
    },
    "D35": {
        "name": "Queen's Gambit Declined",
        "variation": "Positional Line",
        "canonical_pgn": "1.d4 d5 2.c4 e6 3.Nc3 Nf6 4.Bg5 Be7",
        "final_fen": "rnbqk2r/ppp1b1pp/4pn2/3p2B1/2PP4/2N5/PP2PPPP/R2QKBNR b KQkq - 2 4",
    },
    "D40": {
        "name": "Queen's Gambit Declined",
        "variation": "Main Line",
        "canonical_pgn": "1.d4 d5 2.c4 e6 3.Nc3 Nf6",
        "final_fen": "rnbqkb1r/ppp2ppp/4pn2/3p4/2PP4/2N5/PP2PPPP/R1BQKBNR w KQkq - 1 4",
    },
    "D50": {
        "name": "Queen's Gambit Declined",
        "variation": "Anti-Meran, Varna Variation",
        "canonical_pgn": "1.d4 d5 2.c4 e6 3.Nc3 Nf6 4.cxd5 exd5",
        "final_fen": "rnbqkb1r/ppp2ppp/5n2/3p4/3P4/2N5/PPP1PPPP/R1BQKBNR w KQkq - 0 5",
    },
    "D60": {
        "name": "Queen's Gambit Declined",
        "variation": "Orthodox, main line",
        "canonical_pgn": "1.d4 d5 2.c4 e6 3.Nc3 Nf6 4.Bg5 Be7 5.cxd5 exd5",
        "final_fen": "rnbqk2r/ppp1b1pp/5n2/3p2B1/3P4/2N5/PPP1PPPP/R2QKBNR b KQkq - 0 6",
    },
    "D65": {
        "name": "Queen's Gambit Declined",
        "variation": "Orthodox, Capablanca Variation",
        "canonical_pgn": "1.d4 d5 2.c4 e6 3.Nc3 Nf6 4.Bg5 Be7 5.cxd5 exd5 6.Nf3 0-0",
        "final_fen": "rnbq1rk1/ppp1b1pp/5n2/3p2B1/3P4/2N2N2/PPP1PPPP/R2QKB1R w KQ - 1 7",
    },
    
    # E-codes: 1.d4 Nf6 (Indian Defenses)
    "E07": {
        "name": "King's Indian",
        "variation": "Non-Samaraev",
        "canonical_pgn": "1.d4 Nf6 2.c4 g6 3.g3 d6",
        "final_fen": "rnbqkb1r/ppp1p1pp/3pmnp1/8/2PP4/6P1/PP2PPBP/RNBQK1NR w KQkq - 1 4",
    },
    "E15": {
        "name": "Queen's Indian",
        "variation": "Rubinstein Variation",
        "canonical_pgn": "1.d4 Nf6 2.c4 e6 3.Nf3 b6",
        "final_fen": "rnbqkb1r/p1pp1ppp/1pn1p3/8/2PP4/5N2/PPP1PPPP/RNBQKB1R w KQkq - 1 4",
    },
    "E20": {
        "name": "Nimzo-Indian",
        "variation": "Closed",
        "canonical_pgn": "1.d4 Nf6 2.c4 e6 3.Nc3 Bb4",
        "final_fen": "rnbqk2r/pppp1ppp/4pn2/8/1bPP4/2N5/PPP1PPPP/R1BQKBNR w KQkq - 1 4",
    },
    "E25": {
        "name": "Nimzo-Indian",
        "variation": "Main Line",
        "canonical_pgn": "1.d4 Nf6 2.c4 e6 3.Nc3 Bb4 4.d3 0-0 5.a3",
        "final_fen": "rnbq1rk1/pppp1ppp/4pn2/8/1bPP4/P1N1P3/1PP2PPP/R1BQK1NR b KQq - 0 5",
    },
    "E35": {
        "name": "Nimzo-Indian",
        "variation": "Classical",
        "canonical_pgn": "1.d4 Nf6 2.c4 e6 3.Nc3 Bb4 4.Qc2",
        "final_fen": "rnb1k2r/pppp1ppp/4pn2/8/1bPP4/2N5/PPQ1PPPP/R1B1KBNR b KQkq - 1 4",
    },
    "E40": {
        "name": "Nimzo-Indian",
        "variation": "4.e3",
        "canonical_pgn": "1.d4 Nf6 2.c4 e6 3.Nc3 Bb4 4.e3 d5",
        "final_fen": "rnbqk2r/ppp2ppp/4pn2/3p4/1bPP4/2N1P3/PPP2PPP/R1BQKBNR w KQkq - 0 5",
    },
    "E60": {
        "name": "King's Indian",
        "variation": "Flank Variation",
        "canonical_pgn": "1.d4 Nf6 2.c4 g6 3.Nf3",
        "final_fen": "rnbqkb1r/ppp1p1pp/5np1/8/2PP4/5N2/PP2PPPP/RNBQKB1R w KQkq - 1 3",
    },
    "E70": {
        "name": "King's Indian",
        "variation": "Classical Variation",
        "canonical_pgn": "1.d4 Nf6 2.c4 g6 3.Nc3 Bg7 4.e4",
        "final_fen": "rnbqk2r/ppp1p1bp/5np1/8/2PPP3/2N5/PP3PPP/R1BQKBNR b KQkq - 0 4",
    },
    "E75": {
        "name": "King's Indian",
        "variation": "Positional, Classical Main Line",
        "canonical_pgn": "1.d4 Nf6 2.c4 g6 3.Nc3 Bg7 4.e4 d6 5.Nf3 0-0 6.Be2 e5",
        "final_fen": "rnbq1rk1/ppp2pb1/3pp1p1/4p3/2PPP3/2N2N2/PPP1BPPP/R1BQK2R w KQ - 0 7",
    },
    "E90": {
        "name": "King's Indian",
        "variation": "Classical Variation",
        "canonical_pgn": "1.d4 Nf6 2.c4 g6 3.Nc3 Bg7 4.e4 0-0 5.Nf3",
        "final_fen": "rnbq1rk1/ppp1p1bp/5np1/8/2PPP3/2N2N2/PPP2PPP/R1BQKB1R b KQ - 0 5",
    },
    "E95": {
        "name": "King's Indian",
        "variation": "Classical, Positional Main Line",
        "canonical_pgn": "1.d4 Nf6 2.c4 g6 3.Nc3 Bg7 4.e4 d6 5.Nf3 0-0 6.Be2 e5 7.0-0 exd4 8.Nxd4",
        "final_fen": "rnbq1rk1/ppp2pb1/3p2p1/8/2PPN3/2N5/PPP1BPPP/R1BQK2R b KQ - 0 8",
    },
}


class ECOEnhanced:
    """Enhanced ECO system with comprehensive opening data."""
    
    _cache: Dict[str, OpeningInfo] = {}
    _frequency_tracker: Dict[str, int] = defaultdict(int)
    
    @classmethod
    def get_opening_info(cls, eco_code: Optional[str]) -> OpeningInfo:
        """
        Get comprehensive opening information from ECO code.
        
        Args:
            eco_code: ECO code (e.g., 'B32', 'C45')
            
        Returns:
            OpeningInfo dataclass with complete opening information
        """
        if not eco_code:
            return OpeningInfo(
                eco_code="UNK",
                name="Unknown Opening",
                variation="",
                canonical_pgn="",
                final_fen=chess.STARTING_FEN,
                move_count=0,
            )
        
        eco_code = eco_code.upper().strip()
        
        # Check cache first
        if eco_code in cls._cache:
            info = cls._cache[eco_code]
            info.frequency_count = cls._frequency_tracker[eco_code]
            return info
        
        # Check database
        if eco_code in ECO_COMPREHENSIVE_DATABASE:
            data = ECO_COMPREHENSIVE_DATABASE[eco_code]
            # Count moves in PGN
            move_count = len(data.get("canonical_pgn", "").split()) // 2
            
            info = OpeningInfo(
                eco_code=eco_code,
                name=data["name"],
                variation=data.get("variation", ""),
                canonical_pgn=data["canonical_pgn"],
                final_fen=data["final_fen"],
                move_count=move_count,
            )
            cls._cache[eco_code] = info
            cls._frequency_tracker[eco_code] += 1
            info.frequency_count = cls._frequency_tracker[eco_code]
            return info
        
        # Try prefix match
        if len(eco_code) > 3:
            prefix = eco_code[:3]
            if prefix in ECO_COMPREHENSIVE_DATABASE:
                data = ECO_COMPREHENSIVE_DATABASE[prefix]
                move_count = len(data.get("canonical_pgn", "").split()) // 2
                
                info = OpeningInfo(
                    eco_code=prefix,
                    name=data["name"],
                    variation=data.get("variation", ""),
                    canonical_pgn=data["canonical_pgn"],
                    final_fen=data["final_fen"],
                    move_count=move_count,
                )
                cls._cache[eco_code] = info
                cls._frequency_tracker[eco_code] += 1
                info.frequency_count = cls._frequency_tracker[eco_code]
                return info
        
        logger.warning(f"ECO code not found: {eco_code}")
        return OpeningInfo(
            eco_code=eco_code,
            name="Unknown Opening",
            variation="",
            canonical_pgn="",
            final_fen=chess.STARTING_FEN,
            move_count=0,
        )
    
    @classmethod
    def get_all_openings(cls) -> Dict[str, OpeningInfo]:
        """Get all openings in database."""
        result = {}
        for eco_code in ECO_COMPREHENSIVE_DATABASE.keys():
            result[eco_code] = cls.get_opening_info(eco_code)
        return result
    
    @classmethod
    def get_frequency_stats(cls) -> Dict[str, int]:
        """Get frequency statistics for all ECO codes."""
        return dict(cls._frequency_tracker)
    
    @classmethod
    def clear_cache(cls):
        """Clear all caches."""
        cls._cache.clear()
        cls._frequency_tracker.clear()
    
    @classmethod
    def get_opening_pgn_object(cls, eco_code: Optional[str]) -> Optional[chess.pgn.Game]:
        """
        Get the opening as a chess.pgn.Game object.
        
        Args:
            eco_code: ECO code
            
        Returns:
            chess.pgn.Game object or None
        """
        info = cls.get_opening_info(eco_code)
        if not info.canonical_pgn:
            return None
        
        try:
            # Create game from canonical PGN
            game = chess.pgn.Game()
            game.headers["Event"] = "Opening Analysis"
            game.headers["Opening"] = info.name
            game.headers["ECO"] = info.eco_code
            game.headers["Variation"] = info.variation
            
            # Parse moves
            board = chess.Board()
            node = game
            
            moves_str = info.canonical_pgn.split()
            for move_san in moves_str:
                # Skip move numbers
                if move_san.endswith('.'):
                    continue
                
                try:
                    move = board.parse_san(move_san)
                    node = node.add_variation(move)
                    board.push(move)
                except:
                    logger.warning(f"Could not parse move {move_san} in {eco_code}")
                    continue
            
            return game
        except Exception as e:
            logger.error(f"Error creating PGN object for {eco_code}: {e}")
            return None
    
    @classmethod
    def validate_fen(cls, eco_code: Optional[str]) -> bool:
        """Validate FEN position for an ECO code."""
        if not eco_code:
            return False
        
        info = cls.get_opening_info(eco_code)
        try:
            chess.Board(info.final_fen)
            return True
        except:
            logger.error(f"Invalid FEN for {eco_code}: {info.final_fen}")
            return False


# Convenience functions
def get_opening_info(eco_code: Optional[str]) -> OpeningInfo:
    """Quick function to get opening info."""
    return ECOEnhanced.get_opening_info(eco_code)


def get_opening_name(eco_code: Optional[str]) -> str:
    """Quick function to get opening name."""
    info = ECOEnhanced.get_opening_info(eco_code)
    if info.variation:
        return f"{info.name} - {info.variation}"
    return info.name
