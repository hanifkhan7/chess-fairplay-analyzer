"""
FEN to Image Converter
Converts chess FEN positions to high-quality PNG images for reports.
Uses chess.Board SVG rendering and converts to PNG.

Priority: ACCURACY of board representation
"""

import chess
import chess.svg
import logging
from typing import Optional, Tuple
from pathlib import Path
import hashlib
import base64
import io

logger = logging.getLogger(__name__)


class FENToImage:
    """Convert FEN positions to images."""
    
    # Image settings
    DEFAULT_SQUARE_SIZE = 45  # pixels per square
    DEFAULT_BOARD_SIZE = 360  # 8 * 45
    IMAGE_FORMAT = "png"
    CACHE_DIR = Path("cache/fen_images")
    
    # Available square sizes
    SQUARE_SIZES = {
        "small": 30,    # 240x240
        "normal": 45,   # 360x360
        "large": 60,    # 480x480
        "xlarge": 80,   # 640x640
    }
    
    @classmethod
    def initialize_cache(cls):
        """Initialize cache directory."""
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def fen_to_svg(
        cls,
        fen: str,
        square_size: int = None,
        check_highlight: bool = True,
    ) -> str:
        """
        Convert FEN to SVG string.
        
        Args:
            fen: Chess FEN string
            square_size: Size of each square in pixels
            check_highlight: Whether to highlight check
            
        Returns:
            SVG string
        """
        if square_size is None:
            square_size = cls.DEFAULT_SQUARE_SIZE
        
        try:
            board = chess.Board(fen)
            
            # Generate SVG using python-chess
            svg_data = chess.svg.board(
                board,
                size=square_size * 8,
                coordinates=True,  # Show coordinates
                square_size=square_size,
            )
            
            return svg_data
        except Exception as e:
            logger.error(f"Error converting FEN to SVG: {e}")
            return ""
    
    @classmethod
    def get_image_hash(cls, fen: str, size_key: str = "normal") -> str:
        """
        Get consistent hash for FEN position and size.
        
        Args:
            fen: Chess FEN string
            size_key: Size key (small, normal, large, xlarge)
            
        Returns:
            Hash string for caching
        """
        hash_input = f"{fen}_{size_key}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    @classmethod
    def get_cached_image_path(
        cls,
        fen: str,
        size_key: str = "normal"
    ) -> Path:
        """
        Get path to cached image for FEN position.
        
        Args:
            fen: Chess FEN string
            size_key: Size key
            
        Returns:
            Path to image file
        """
        image_hash = cls.get_image_hash(fen, size_key)
        return cls.CACHE_DIR / f"{image_hash}.{cls.IMAGE_FORMAT}"
    
    @classmethod
    def fen_to_base64(
        cls,
        fen: str,
        size_key: str = "normal",
    ) -> str:
        """
        Convert FEN to base64-encoded PNG image (for embedding in HTML).
        
        Args:
            fen: Chess FEN string
            size_key: Size key (small, normal, large, xlarge)
            
        Returns:
            Base64 encoded PNG data URL
        """
        if size_key not in cls.SQUARE_SIZES:
            size_key = "normal"
        
        square_size = cls.SQUARE_SIZES[size_key]
        
        try:
            # Generate SVG
            svg_data = cls.fen_to_svg(fen, square_size)
            if not svg_data:
                return ""
            
            # Try to import cairosvg for SVG to PNG conversion
            try:
                import cairosvg
                
                # Convert SVG to PNG bytes
                png_bytes = cairosvg.svg2png(bytestring=svg_data)
                
                # Encode to base64
                base64_data = base64.b64encode(png_bytes).decode()
                return f"data:image/png;base64,{base64_data}"
            
            except ImportError:
                logger.warning("cairosvg not available, using SVG directly")
                # Fallback: return SVG as data URL
                svg_b64 = base64.b64encode(svg_data.encode()).decode()
                return f"data:image/svg+xml;base64,{svg_b64}"
            
        except Exception as e:
            logger.error(f"Error converting FEN to base64: {e}")
            return ""
    
    @classmethod
    def fen_to_file(
        cls,
        fen: str,
        output_path: Path,
        size_key: str = "normal",
    ) -> bool:
        """
        Save FEN position as PNG image file.
        
        Args:
            fen: Chess FEN string
            output_path: Path to save PNG
            size_key: Size key
            
        Returns:
            True if successful, False otherwise
        """
        if size_key not in cls.SQUARE_SIZES:
            size_key = "normal"
        
        square_size = cls.SQUARE_SIZES[size_key]
        
        try:
            svg_data = cls.fen_to_svg(fen, square_size)
            if not svg_data:
                return False
            
            try:
                import cairosvg
                cairosvg.svg2file(bytestring=svg_data, write_to=str(output_path))
                logger.info(f"Saved image to {output_path}")
                return True
            except ImportError:
                logger.warning("cairosvg not available, saving SVG instead")
                # Save as SVG
                svg_path = output_path.with_suffix('.svg')
                with open(svg_path, 'w') as f:
                    f.write(svg_data)
                logger.info(f"Saved SVG to {svg_path}")
                return True
        
        except Exception as e:
            logger.error(f"Error saving FEN to file: {e}")
            return False
    
    @classmethod
    def get_board_image_html(
        cls,
        fen: str,
        title: str = "",
        size_key: str = "normal",
        include_fen: bool = True,
    ) -> str:
        """
        Generate HTML for board image with title and metadata.
        
        Args:
            fen: Chess FEN string
            title: Optional title for the position
            size_key: Size key
            include_fen: Whether to include FEN string below image
            
        Returns:
            HTML string
        """
        base64_image = cls.fen_to_base64(fen, size_key)
        if not base64_image:
            return ""
        
        html = f"""
        <div class="board-image-container">
        """
        
        if title:
            html += f'    <h3 class="board-title">{title}</h3>\n'
        
        html += f"""    <img src="{base64_image}" alt="Chess Position" class="board-image board-{size_key}" />
        """
        
        if include_fen:
            html += f"""    <div class="board-fen">
        <small>FEN: <code>{fen}</code></small>
        </div>
        """
        
        html += """    </div>
        """
        
        return html
    
    @classmethod
    def validate_fen(cls, fen: str) -> bool:
        """Validate FEN string."""
        try:
            chess.Board(fen)
            return True
        except:
            return False
    
    @classmethod
    def get_position_info(cls, fen: str) -> dict:
        """
        Get information about a FEN position.
        
        Args:
            fen: Chess FEN string
            
        Returns:
            Dictionary with position info
        """
        try:
            board = chess.Board(fen)
            
            return {
                "valid": True,
                "fen": fen,
                "turn": "White" if board.turn else "Black",
                "move_number": board.fullmove_number,
                "material_count": len(board.pieces(chess.PAWN, True)) + 
                                 len(board.pieces(chess.KNIGHT, True)) * 3 +
                                 len(board.pieces(chess.BISHOP, True)) * 3 +
                                 len(board.pieces(chess.ROOK, True)) * 5 +
                                 len(board.pieces(chess.QUEEN, True)) * 9,
                "is_check": board.is_check(),
                "is_checkmate": board.is_checkmate(),
                "is_stalemate": board.is_stalemate(),
                "legal_moves": board.legal_moves.count(),
            }
        except Exception as e:
            logger.error(f"Error getting position info: {e}")
            return {"valid": False, "error": str(e)}


# Initialize cache on import
FENToImage.initialize_cache()


# Convenience functions
def fen_to_svg(fen: str, size: int = 45) -> str:
    """Convert FEN to SVG."""
    return FENToImage.fen_to_svg(fen, size)


def fen_to_base64(fen: str, size_key: str = "normal") -> str:
    """Convert FEN to base64 image URL."""
    return FENToImage.fen_to_base64(fen, size_key)


def validate_fen(fen: str) -> bool:
    """Validate FEN string."""
    return FENToImage.validate_fen(fen)


def get_position_info(fen: str) -> dict:
    """Get position information."""
    return FENToImage.get_position_info(fen)
