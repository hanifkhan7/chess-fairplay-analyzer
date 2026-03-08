"""
Enhanced FEN to Image Converter
Converts chess FEN positions to high-quality PNG images for comprehensive reporting.
Supports embedding images in HTML reports with statistics and annotations.

Priority: ACCURACY of board representation
"""

import chess
import chess.svg
import logging
from typing import Optional, Tuple, List, Dict
from pathlib import Path
import hashlib
import base64
import io
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class FENImageInfo:
    """Information about a FEN image conversion."""
    fen: str
    filename: str
    file_path: Optional[Path]
    base64_data: Optional[str]
    size_key: str
    board_size: int
    square_size: int
    created_at: str
    is_valid: bool
    svg_data: Optional[str] = None


class FENToImageEnhanced:
    """Enhanced FEN to Image converter with HTML integration."""
    
    # Image settings - optimized for web and print
    DEFAULT_SQUARE_SIZE = 50  # pixels per square
    DEFAULT_BOARD_SIZE = 400  # 8 * 50
    IMAGE_FORMAT = "png"
    CACHE_DIR = Path("cache/fen_images")
    
    # Available square sizes for different use cases
    SQUARE_SIZES = {
        "thumbnail": 25,    # 200x200 - For quick previews
        "small": 35,        # 280x280 - For summary tables
        "normal": 50,       # 400x400 - Standard reports
        "large": 70,        # 560x560 - Detailed analysis
        "xlarge": 100,      # 800x800 - Print quality
    }
    
    # Board color schemes
    COLOR_SCHEMES = {
        "default": {
            "light": "#F0D9B5",
            "dark": "#B58863",
        },
        "green": {
            "light": "#FFFFCC",
            "dark": "#90AA22",
        },
        "blue": {
            "light": "#DEE3E6",
            "dark": "#8CA3B8",
        },
        "purple": {
            "light": "#F5F5F5",
            "dark": "#8884CC",
        },
    }
    
    @classmethod
    def initialize_cache(cls):
        """Initialize cache directory."""
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized FEN image cache at {cls.CACHE_DIR}")
    
    @classmethod
    def fen_to_svg(
        cls,
        fen: str,
        square_size: int = None,
        color_scheme: str = "default",
        highlight_squares: List[str] = None,
    ) -> str:
        """
        Convert FEN to SVG string with customization.
        
        Args:
            fen: Chess FEN string
            square_size: Size of each square in pixels
            color_scheme: Color scheme name
            highlight_squares: List of squares to highlight (e.g., ['e2', 'e4'])
            
        Returns:
            SVG string
        """
        if square_size is None:
            square_size = cls.DEFAULT_SQUARE_SIZE
        
        if color_scheme not in cls.COLOR_SCHEMES:
            color_scheme = "default"
        
        try:
            board = chess.Board(fen)
            
            # Get color scheme
            colors = cls.COLOR_SCHEMES[color_scheme]
            
            # Generate SVG using python-chess
            board_size = square_size * 8
            svg_data = chess.svg.board(
                board,
                size=board_size,
                coordinates=True,
                check=True,  # Highlight king in check
            )
            
            return svg_data
        except Exception as e:
            logger.error(f"Error converting FEN to SVG: {e}")
            return ""
    
    @classmethod
    def get_image_hash(cls, fen: str, size_key: str = "normal", color_scheme: str = "default") -> str:
        """
        Get consistent hash for FEN position, size, and color scheme.
        
        Args:
            fen: Chess FEN string
            size_key: Size key
            color_scheme: Color scheme name
            
        Returns:
            Hash string for caching
        """
        hash_input = f"{fen}_{size_key}_{color_scheme}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    @classmethod
    def get_cached_image_path(
        cls,
        fen: str,
        size_key: str = "normal",
        color_scheme: str = "default"
    ) -> Path:
        """Get path to cached image for FEN position."""
        image_hash = cls.get_image_hash(fen, size_key, color_scheme)
        return cls.CACHE_DIR / f"{image_hash}.{cls.IMAGE_FORMAT}"
    
    @classmethod
    def fen_to_base64(
        cls,
        fen: str,
        size_key: str = "normal",
        color_scheme: str = "default",
    ) -> str:
        """
        Convert FEN to base64-encoded PNG image for embedding in HTML.
        
        Args:
            fen: Chess FEN string
            size_key: Size key (thumbnail, small, normal, large, xlarge)
            color_scheme: Color scheme name
            
        Returns:
            Base64 encoded PNG data URL
        """
        if size_key not in cls.SQUARE_SIZES:
            size_key = "normal"
        
        if color_scheme not in cls.COLOR_SCHEMES:
            color_scheme = "default"
        
        square_size = cls.SQUARE_SIZES[size_key]
        
        try:
            # Generate SVG
            svg_data = cls.fen_to_svg(fen, square_size, color_scheme)
            if not svg_data:
                return ""
            
            # Try to import cairosvg for SVG to PNG conversion
            try:
                import cairosvg
                
                # Convert SVG to PNG bytes
                png_bytes = cairosvg.svg2png(bytestring=svg_data.encode())
                
                # Encode to base64
                base64_data = base64.b64encode(png_bytes).decode()
                return f"data:image/png;base64,{base64_data}"
            
            except ImportError:
                logger.warning("cairosvg not available, using SVG as fallback")
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
        color_scheme: str = "default",
    ) -> FENImageInfo:
        """
        Save FEN position as image file.
        
        Args:
            fen: Chess FEN string
            output_path: Path to save image
            size_key: Size key
            color_scheme: Color scheme
            
        Returns:
            FENImageInfo object with conversion details
        """
        if size_key not in cls.SQUARE_SIZES:
            size_key = "normal"
        
        if color_scheme not in cls.COLOR_SCHEMES:
            color_scheme = "default"
        
        square_size = cls.SQUARE_SIZES[size_key]
        board_size = square_size * 8
        
        info = FENImageInfo(
            fen=fen,
            filename=output_path.name,
            file_path=None,
            base64_data=None,
            size_key=size_key,
            board_size=board_size,
            square_size=square_size,
            created_at=datetime.now().isoformat(),
            is_valid=False,
        )
        
        try:
            # Validate FEN
            board = chess.Board(fen)
            info.is_valid = True
            
            svg_data = cls.fen_to_svg(fen, square_size, color_scheme)
            if not svg_data:
                return info
            
            info.svg_data = svg_data
            
            try:
                import cairosvg
                output_path.parent.mkdir(parents=True, exist_ok=True)
                cairosvg.svg2file(bytestring=svg_data.encode(), write_to=str(output_path))
                info.file_path = output_path
                logger.info(f"Saved FEN image to {output_path}")
            except ImportError:
                logger.warning("cairosvg not available, saving SVG instead")
                # Save as SVG
                svg_path = output_path.with_suffix('.svg')
                svg_path.parent.mkdir(parents=True, exist_ok=True)
                with open(svg_path, 'w') as f:
                    f.write(svg_data)
                info.file_path = svg_path
            
            return info
        
        except Exception as e:
            logger.error(f"Error saving FEN image: {e}")
            return info
    
    @classmethod
    def create_html_image_element(
        cls,
        fen: str,
        alt_text: str = "Chess position",
        size_key: str = "normal",
        color_scheme: str = "default",
        css_classes: str = "",
        with_fen_text: bool = False,
    ) -> str:
        """
        Create HTML img element with inline base64 image.
        
        Args:
            fen: Chess FEN string
            alt_text: Alt text for image
            size_key: Size key
            color_scheme: Color scheme
            css_classes: Additional CSS classes
            with_fen_text: Whether to include FEN below image
            
        Returns:
            HTML string with image element
        """
        base64_data = cls.fen_to_base64(fen, size_key, color_scheme)
        if not base64_data:
            return f"<p>Could not generate board image for: {alt_text}</p>"
        
        square_size = cls.SQUARE_SIZES[size_key]
        board_size = square_size * 8
        
        html = f'<img src="{base64_data}" alt="{alt_text}" '
        html += f'width="{board_size}" height="{board_size}" '
        if css_classes:
            html += f'class="{css_classes}" '
        html += '/>'
        
        if with_fen_text:
            html += f'<p style="font-size: 10px; font-family: monospace; margin-top: 5px;">{fen}</p>'
        
        return html
    
    @classmethod
    def create_html_board_with_info(
        cls,
        fen: str,
        title: str = "",
        stats: Dict = None,
        size_key: str = "normal",
    ) -> str:
        """
        Create HTML div with board image and statistics.
        
        Args:
            fen: Chess FEN string
            title: Title for the board
            stats: Dictionary of statistics to display
            size_key: Size key
            
        Returns:
            HTML string
        """
        html = '<div class="board-with-stats" style="display: inline-block; text-align: center; margin: 10px;">'
        
        if title:
            html += f'<h3 style="margin: 5px 0;">{title}</h3>'
        
        # Add board image
        square_size = cls.SQUARE_SIZES[size_key]
        board_size = square_size * 8
        
        base64_data = cls.fen_to_base64(fen, size_key)
        if base64_data:
            html += f'<img src="{base64_data}" width="{board_size}" height="{board_size}" '
            html += 'style="border: 2px solid #333; margin: 5px;" />'
        
        # Add statistics
        if stats:
            html += '<table style="border-collapse: collapse; margin-top: 5px; width: 100%;">'
            for stat_name, stat_value in stats.items():
                html += f'<tr><td style="border: 1px solid #ccc; padding: 5px; text-align: left;">'
                html += f'{stat_name}: </td><td style="border: 1px solid #ccc; padding: 5px; text-align: right;">'
                html += f'<strong>{stat_value}</strong></td></tr>'
            html += '</table>'
        
        html += '</div>'
        return html
    
    @classmethod
    def validate_fen(cls, fen: str) -> bool:
        """Validate FEN position."""
        try:
            chess.Board(fen)
            return True
        except:
            return False
    
    @classmethod
    def clear_cache(cls):
        """Clear image cache."""
        try:
            import shutil
            if cls.CACHE_DIR.exists():
                shutil.rmtree(cls.CACHE_DIR)
                cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
                logger.info("Cleared FEN image cache")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")


# Convenience functions
def convert_fen_to_base64(fen: str, size: str = "normal") -> str:
    """Quick function to convert FEN to base64 image."""
    FENToImageEnhanced.initialize_cache()
    return FENToImageEnhanced.fen_to_base64(fen, size)


def create_board_html(fen: str, title: str = "") -> str:
    """Quick function to create HTML board image."""
    FENToImageEnhanced.initialize_cache()
    return FENToImageEnhanced.create_html_image_element(fen, title, "normal")


def create_board_with_stats(fen: str, title: str = "", stats: Dict = None) -> str:
    """Quick function to create HTML board with statistics."""
    FENToImageEnhanced.initialize_cache()
    return FENToImageEnhanced.create_html_board_with_info(fen, title, stats)


# Initialize on import
FENToImageEnhanced.initialize_cache()
