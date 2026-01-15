"""
Command-line interface for Chess Fairplay Analyzer.
"""
import click
import sys
import os
from pathlib import Path
from typing import Optional

# Local imports - FIXED IMPORTS
from .fetcher import fetch_player_games
from .analyzer import ChessAnalyzer  # Changed from analyze_games
from .reporter import generate_report
from .utils.helpers import setup_logging, load_config, validate_username, find_stockfish_windows

# For colored output on Windows
try:
    import colorama
    colorama.init()
except ImportError:
    colorama = None

def print_banner():
    """Print the tool banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║      ♟️ CHESS FAIRPLAY ANALYZER v1.0.0 ♟️            ║
    ║      Forensic analysis for chess fair play           ║
    ╚═══════════════════════════════════════════════════════╝
    """
    click.echo(banner)

@click.command()
@click.argument('username', required=False)
@click.option('--games', '-g', default=50, help='Maximum number of games to analyze (default: 50).')
@click.option('--format', '-f', default='html', 
              type=click.Choice(['html', 'text', 'json', 'all'], case_sensitive=False),
              help='Output format (default: html).')
@click.option('--output', '-o', default=None, help='Output file/directory name.')
@click.option('--config', '-c', default='config.yaml', help='Path to configuration file.')
@click.option('--depth', '-d', default=None, type=int, help='Stockfish analysis depth (overrides config).')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging.')
@click.option('--list-formats', is_flag=True, help='List available output formats and exit.')
@click.option('--check-stockfish', is_flag=True, help='Check Stockfish installation and exit.')
@click.version_option(version='1.0.0', prog_name='Chess Fairplay Analyzer')
def main(username: Optional[str], games: int, format: str, output: Optional[str], 
         config: str, depth: Optional[int], verbose: bool, 
         list_formats: bool, check_stockfish: bool):
    """
    Analyze Chess.com games for potential fair play violations.
    
    USERNAME: Chess.com username to analyze (optional if using --check-stockfish).
    
    Examples:
    
      chess-analyzer magnuscarlsen --games 100 --format html
      
      chess-analyzer hikaru --depth 20 --output report
      
      chess-analyzer --check-stockfish
    """
    
    # Print banner
    print_banner()
    
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(level=log_level)
    
    # Load configuration
    cfg = load_config(config)
    
    # Handle special flags
    if list_formats:
        click.echo("\n📊 Available output formats:")
        click.echo("  html  - Interactive HTML report with charts (recommended)")
        click.echo("  text  - Plain text summary for quick review")
        click.echo("  json  - Machine-readable JSON data")
        click.echo("  all   - Generate all formats")
        return
    
    if check_stockfish:
        click.echo("\n🔍 Checking Stockfish installation...")
        stockfish_path = find_stockfish_windows()
        if stockfish_path:
            click.echo(f"✅ Stockfish found at: {stockfish_path}")
            
            # Test if it runs
            import subprocess
            try:
                result = subprocess.run([stockfish_path, "--version"], 
                                      capture_output=True, text=True, timeout=2)
                if "Stockfish" in result.stdout:
                    click.echo(f"✅ Stockfish version: {result.stdout.split()[1]}")
                else:
                    click.echo("⚠️  Stockfish found but version check failed")
            except Exception as e:
                click.echo(f"⚠️  Stockfish found but couldn't run: {e}")
        else:
            click.echo("❌ Stockfish not found!")
            click.echo("\n📥 Installation options:")
            click.echo("  1. Download from https://stockfishchess.org/download/")
            click.echo("  2. Extract to C:\\Users\\zaibi\\stockfish\\")
            click.echo("  3. Update engine_path in config.yaml")
        return
    
    # Validate username if provided
    if not username:
        click.echo("❌ Error: Username is required.")
        click.echo("\nUsage: chess-analyzer [USERNAME] [OPTIONS]")
        click.echo("\nTry 'chess-analyzer --help' for more information.")
        sys.exit(1)
    
    if not validate_username(username):
        click.echo(f"❌ Error: Invalid username format: {username}")
        click.echo("Username can only contain letters, numbers, underscores, and hyphens.")
        sys.exit(1)
    
    # Override config with CLI options
    if depth:
        cfg['analysis']['engine_depth'] = depth
    
    # Determine output file name
    if output is None:
        output = f"report_{username}"
    
    click.echo(f"\n🔍 Starting analysis for player: {click.style(username, fg='cyan', bold=True)}")
    click.echo(f"📊 Games to analyze: {click.style(str(games), fg='yellow')}")
    click.echo(f"📄 Output format: {click.style(format, fg='yellow')}")
    click.echo(f"⚙️  Analysis depth: {click.style(str(cfg['analysis']['engine_depth']), fg='yellow')}")
    
    # Step 1: Fetch games
    click.echo("\n📥 Fetching games from Chess.com...")
    try:
        games_data = fetch_player_games(username, max_games=games, config=cfg)
        if not games_data:
            click.echo("❌ No games found or error fetching data.")
            sys.exit(1)
        
        click.echo(f"✅ Successfully fetched {click.style(str(len(games_data)), fg='green', bold=True)} games")
        
    except Exception as e:
        click.echo(f"❌ Error fetching games: {str(e)}")
        if verbose:
            import traceback
            click.echo(traceback.format_exc())
        sys.exit(1)
    
    # Step 2: Analyze games - UPDATED TO ANALYZE ALL GAMES
    click.echo("\n🧠 Analyzing games with Stockfish (this will take time)...")
    click.echo(f"   Analyzing {len(games_data)} games at depth {cfg['analysis']['engine_depth']}")
    click.echo("   Progress will be shown below:\n")
    
    try:
        # Create analyzer and analyze ALL games
        analyzer = ChessAnalyzer(cfg)
        
        # Use tqdm for progress bar if available
        try:
            from tqdm import tqdm
            # Analyze with progress bar
            with tqdm(total=len(games_data), desc="Analyzing games", unit="game") as pbar:
                # We need to modify analyzer to use callback
                player_analysis = analyzer.analyze_games(games_data)
                pbar.update(len(games_data))
        except ImportError:
            # Without tqdm
            player_analysis = analyzer.analyze_games(games_data)
        
        # Generate report data
        analysis_results = analyzer.generate_detailed_report(player_analysis)
        
        click.echo(f"\n✅ Analysis complete!")
        click.echo(f"   Games fetched: {len(games_data)}")
        click.echo(f"   Games analyzed: {player_analysis.games_analyzed}")
        
        if player_analysis.games_analyzed > 0:
            click.echo(f"   Suspicion score: {player_analysis.suspicion_score:.1f}/100")
            click.echo(f"   Risk level: {player_analysis.risk_level}")
        
        # Cleanup analyzer
        analyzer.cleanup()
        
    except Exception as e:
        click.echo(f"\n❌ Error during analysis: {str(e)}")
        if verbose:
            import traceback
            click.echo(traceback.format_exc())
        
        # Create minimal results
        analysis_results = {
            'username': username,
            'summary': {
                'total_games_fetched': len(games_data),
                'games_analyzed': 0,
                'suspicion_score': 0,
                'risk_level': 'ERROR',
                'avg_engine_correlation': 0,
                'avg_centipawn_loss': 999,
            }
        }
    
    # Step 3: Generate report(s)
    click.echo("\n📄 Generating report...")
    
    formats_to_generate = [format] if format != 'all' else ['html', 'text', 'json']
    
    for fmt in formats_to_generate:
        try:
            output_file = generate_report(
                analysis_results, 
                username, 
                format=fmt, 
                output_file=output,
                config=cfg
            )
            
            if output_file and os.path.exists(output_file):
                file_size = os.path.getsize(output_file) / 1024  # KB
                click.echo(f"✅ {fmt.upper()} report saved: {click.style(output_file, fg='green')} ({file_size:.1f} KB)")
            else:
                click.echo(f"⚠️  {fmt.upper()} report generation may have failed")
                
        except Exception as e:
            click.echo(f"❌ Error generating {fmt} report: {str(e)}")
            if verbose:
                import traceback
                click.echo(traceback.format_exc())
    
    # Final summary
    click.echo("\n" + "="*50)
    click.echo(click.style("📋 ANALYSIS COMPLETE", fg='green', bold=True))
    click.echo("="*50)
    click.echo(f"Player: {username}")
    click.echo(f"Games analyzed: {analysis_results['summary'].get('games_analyzed', 0)}")
    
    if 'suspicion_score' in analysis_results['summary']:
        click.echo(f"Suspicion score: {analysis_results['summary']['suspicion_score']:.1f}/100")
        click.echo(f"Risk level: {analysis_results['summary']['risk_level']}")
    
    # Show where reports are
    if format == 'all':
        click.echo(f"Reports generated:")
        for fmt in ['html', 'text', 'json']:
            report_file = f"{output}.{fmt}" if fmt != 'html' else f"{output}.html"
            if os.path.exists(report_file):
                click.echo(f"  • {fmt.upper()}: {report_file}")
    else:
        report_file = f"{output}.{format}" if format != 'html' else f"{output}.html"
        if os.path.exists(report_file):
            click.echo(f"Report: {report_file}")
    
    click.echo("\n⚠️  IMPORTANT DISCLAIMER:")
    click.echo("   This tool provides statistical indicators only.")
    click.echo("   It does NOT prove cheating. Use results responsibly.")
    click.echo("   Final judgment rests with Chess.com's Fair Play team.")

if __name__ == '__main__':
    # Handle Ctrl+C gracefully
    try:
        main()
    except KeyboardInterrupt:
        click.echo("\n\n⚠️  Operation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        click.echo(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)