"""
PLAYER DNA v2 - MENU INTEGRATION GUIDE
======================================

This guide shows how to integrate the GOD-LEVEL Player DNA v2 system
into the existing menu system and exploit reports.
"""

# ============================================================================
# INTEGRATION POINT 1: MENU.PY - ADD TO _player_dna_analysis()
# ============================================================================

def _player_dna_analysis_v2(username: str):
    """
    ENHANCED PLAYER DNA ANALYSIS - GOD-LEVEL EDITION
    
    Builds comprehensive statistical opening repertoire with:
    - Complete lifetime repertoire
    - Live stats from Chess.com/Lichess
    - Game annotation and analysis
    - Playing style detection
    - Weakness identification
    - Counter-strategy generation
    - Executive summary
    """
    print("\n" + "="*80)
    print("[DNA v2] GOD-LEVEL PLAYER DNA ANALYSIS")
    print("Comprehensive lifetime repertoire with automatic strategy generation")
    print("="*80)
    
    try:
        from chess_analyzer.player_dna_complete import analyze_player_complete
        from chess_analyzer.utils.helpers import load_config
        
        config = load_config()
        
        # Get games
        game_count_str = input("\nGames to analyze (recommended 500+, default 1000): ").strip()
        try:
            game_count = int(game_count_str) if game_count_str else 1000
        except:
            game_count = 1000
        
        # Color selection
        print("\nPlayer color:")
        print("  1. White")
        print("  2. Black")
        print("  3. Both")
        color_choice = input("Select (1-3, default 3): ").strip()
        color_map = {'1': 'white', '2': 'black', '3': None}
        color = color_map.get(color_choice, None)
        
        # Fetch games
        print(f"\n[FETCH] Fetching up to {game_count} games from Chess.com...")
        player_games, counts = _fetch_games(username, game_count, config=config)
        
        if not player_games:
            print(f"[ERROR] No games found for {username}")
            input("\nPress Enter to continue...")
            return
        
        print(f"[OK] Retrieved {len(player_games)} games")
        
        # Run complete analysis
        print(f"\n[ANALYZE] Running GOD-LEVEL player DNA analysis...")
        print(f"  • Fetching Chess.com/Lichess live stats...")
        print(f"  • Analyzing lifetime repertoire...")
        print(f"  • Extracting game-level annotations...")
        print(f"  • Detecting playing style...")
        print(f"  • Identifying weaknesses...")
        print(f"  • Generating counter-strategies...")
        
        try:
            profile = analyze_player_complete(
                username,
                player_games,
                color=color,
                fetch_live_stats=True
            )
            
            if not profile or profile.total_games_analyzed == 0:
                print(f"[ERROR] Failed to analyze games")
                input("\nPress Enter to continue...")
                return
            
        except Exception as e:
            print(f"[ERROR] Exception during analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            input("\nPress Enter to continue...")
            return
        
        # Display executive summary
        print(profile.generate_executive_summary())
        
        # Export options
        print("\n" + "="*80)
        print("[EXPORT OPTIONS]")
        print("="*80)
        
        export_choice = input("\nExport results? (j=JSON, t=Text, b=Both, n=No): ").strip().lower()
        
        if export_choice in ['j', 'b']:
            json_file = f"repertoires/{username}_profile_v2.json"
            profile.export_json(json_file)
            print(f"✓ Exported JSON: {json_file}")
        
        if export_choice in ['t', 'b']:
            txt_file = f"repertoires/{username}_profile_v2.txt"
            profile.save_report(txt_file)
            print(f"✓ Exported Text: {txt_file}")
        
        print("\n[SUCCESS] Player DNA v2 analysis complete!")
        input("\nPress Enter to continue...")
        
    except ImportError:
        print("[ERROR] Player DNA v2 modules not found")
        print("Please install: pip install -r requirements.txt")
        input("\nPress Enter to continue...")
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to continue...")


# ============================================================================
# INTEGRATION POINT 2: EXPLOIT REPORT - ADD PLAYER DNA SECTION
# ============================================================================

def add_dna_section_to_exploit_report(profile, username):
    """
    Add Player DNA v2 section to exploit report HTML.
    
    Inserts comprehensive opponent profile into the HTML report.
    """
    from chess_analyzer.exploit_report_generator import generate_enhanced_exploit_report
    
    html_section = f"""
    <!-- PLAYER DNA v2 SECTION -->
    <div class="dna-section" style="margin: 30px 0; padding: 20px; background: #f8f9fa; border-left: 4px solid #dc3545;">
        <h2 style="color: #dc3545; margin-top: 0;">⚔️ PLAYER DNA - LIFETIME REPERTOIRE</h2>
        
        <div class="dna-summary" style="margin: 20px 0; padding: 15px; background: white; border-radius: 8px;">
            <h3>Lifetime Statistics</h3>
            <ul style="columns: 2;">
                <li><strong>Total Games:</strong> {profile.total_games_analyzed}</li>
                <li><strong>Unique Openings:</strong> {profile.total_unique_openings}</li>
                <li><strong>Playing Style:</strong> {profile.playing_tendencies.get('style', 'Unknown')}</li>
            </ul>
        </div>
        
        <div class="exploitation-targets" style="margin: 20px 0; padding: 15px; background: white; border-radius: 8px;">
            <h3>🎯 EXPLOITATION TARGETS (Weak Lines)</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #f0f0f0; border-bottom: 2px solid #ddd;">
                        <th style="padding: 10px; text-align: left;">Opening</th>
                        <th style="padding: 10px; text-align: center;">Games</th>
                        <th style="padding: 10px; text-align: center;">Win Rate</th>
                        <th style="padding: 10px; text-align: left;">Action</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for i, weakness in enumerate(profile.key_weaknesses[:5]):
        html_section += f"""
                    <tr style="border-bottom: 1px solid #ddd; background: {'#ffe6e6' if i % 2 else 'white'};">
                        <td style="padding: 10px;">{weakness['opening']}</td>
                        <td style="padding: 10px; text-align: center;">{weakness['games']}</td>
                        <td style="padding: 10px; text-align: center; color: #dc3545; font-weight: bold;">{weakness['win_rate']:.1f}%</td>
                        <td style="padding: 10px;">{weakness['recommendation']}</td>
                    </tr>
        """
    
    html_section += """
                </tbody>
            </table>
        </div>
        
        <div class="opponent-strengths" style="margin: 20px 0; padding: 15px; background: white; border-radius: 8px;">
            <h3>⚠️ OPPONENT STRENGTHS (DO NOT PLAY)</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #f0f0f0; border-bottom: 2px solid #ddd;">
                        <th style="padding: 10px; text-align: left;">Opening</th>
                        <th style="padding: 10px; text-align: center;">Games</th>
                        <th style="padding: 10px; text-align: center;">Win Rate</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for i, weapon in enumerate(profile.favorite_weapons[:5]):
        html_section += f"""
                    <tr style="border-bottom: 1px solid #ddd; background: {'#e6f0ff' if i % 2 else 'white'};">
                        <td style="padding: 10px;">{weapon['opening']}</td>
                        <td style="padding: 10px; text-align: center;">{weapon['games']}</td>
                        <td style="padding: 10px; text-align: center; color: #0066cc; font-weight: bold;">{weapon['win_rate']:.1f}%</td>
                    </tr>
        """
    
    html_section += """
                </tbody>
            </table>
        </div>
        
        <div class="counter-strategies" style="margin: 20px 0; padding: 15px; background: white; border-radius: 8px;">
            <h3>💡 RECOMMENDED COUNTER-STRATEGIES</h3>
            <ol>
    """
    
    for strategy in profile.counter_strategies[:3]:
        html_section += f"""
                <li>
                    <strong>{strategy['opening']}</strong><br>
                    {strategy['strategy']}<br>
                    <em>Expected advantage: +{strategy['expected_win_rate']:.1f}%</em>
                </li>
        """
    
    html_section += """
            </ol>
        </div>
        
        <div class="pregame-checklist" style="margin: 20px 0; padding: 15px; background: #fff8dc; border-radius: 8px;">
            <h3>🏆 PRE-GAME CHECKLIST</h3>
            <ul>
                <li>□ Study opponent's weak openings</li>
                <li>□ Prepare counter-strategies</li>
                <li>□ Avoid opponent's strength openings</li>
                <li>□ Be ready for opponent's playing style</li>
                <li>□ Review prepared trap variations</li>
            </ul>
        </div>
    </div>
    <!-- END PLAYER DNA v2 SECTION -->
    """
    
    return html_section


# ============================================================================
# INTEGRATION POINT 3: COMPLETE WORKFLOW
# ============================================================================

def complete_opponent_preparation_workflow(username: str):
    """
    Complete workflow: Fetch -> Analyze -> Report -> Export
    
    This demonstrates the full integration of Player DNA v2 with exploit reports.
    """
    from chess_analyzer.player_dna_complete import analyze_player_complete
    from chess_analyzer.exploit_report_generator import generate_enhanced_exploit_report
    from chess_analyzer.utils.helpers import load_config
    
    print("\n" + "="*80)
    print("COMPLETE OPPONENT PREPARATION WORKFLOW")
    print("="*80)
    
    # Step 1: Fetch games
    print(f"\n[1/4] Fetching games from Chess.com...")
    config = load_config()
    games, counts = _fetch_games(username, 1000, config=config)
    print(f"  ✓ Retrieved {len(games)} games")
    
    # Step 2: Complete DNA analysis
    print(f"\n[2/4] Running Player DNA v2 analysis...")
    profile = analyze_player_complete(username, games, fetch_live_stats=True)
    print(f"  ✓ Analyzed {profile.total_games_analyzed} games")
    print(f"  ✓ Found {len(profile.key_weaknesses)} exploitable weaknesses")
    print(f"  ✓ Generated {len(profile.counter_strategies)} counter-strategies")
    
    # Step 3: Generate exploit report with DNA section
    print(f"\n[3/4] Generating exploit report with DNA section...")
    
    # Generate base exploit report
    exploit_html = generate_enhanced_exploit_report({
        'total_games': profile.total_games_analyzed,
        'favorite_openings': [w['opening'] for w in profile.key_weaknesses],
        # ... other data
    }, username)
    
    # Add DNA section
    dna_section = add_dna_section_to_exploit_report(profile, username)
    enriched_html = exploit_html.replace(
        '</body>',
        f'{dna_section}\n</body>'
    )
    print(f"  ✓ Added Player DNA section to report")
    
    # Step 4: Export everything
    print(f"\n[4/4] Exporting results...")
    
    # Save HTML report
    html_file = f"reports/{username}_complete_analysis.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(enriched_html)
    print(f"  ✓ HTML Report: {html_file}")
    
    # Save JSON profile
    json_file = f"profiles/{username}_dna_v2.json"
    profile.export_json(json_file)
    print(f"  ✓ JSON Profile: {json_file}")
    
    # Save text summary
    txt_file = f"profiles/{username}_summary.txt"
    profile.save_report(txt_file)
    print(f"  ✓ Text Summary: {txt_file}")
    
    print("\n" + "="*80)
    print("✓ COMPLETE PREPARATION DONE!")
    print("="*80)
    print(f"\nYou can now:")
    print(f"  1. Open {html_file} in browser for visual report")
    print(f"  2. Print text summary for the game")
    print(f"  3. Review JSON profile for detailed analysis")
    print(f"\n🚀 Ready to dominate {username}!")


# ============================================================================
# HOW TO USE
# ============================================================================

"""
INTEGRATION STEPS:

1. Add menu option to menu.py:
   - Add "11. Player DNA v2 Analysis (GOD-LEVEL)" to menu
   - Call _player_dna_analysis_v2() when selected

2. Update exploit_report_generator.py:
   - Import player_dna_complete
   - Call add_dna_section_to_exploit_report()
   - Insert HTML section into report

3. Test the integration:
   - Run menu and select Player DNA v2
   - Generate exploit report
   - Verify DNA section appears in HTML
   - Check exports (JSON, text)

4. Full workflow:
   - Run complete_opponent_preparation_workflow(username)
   - Get comprehensive HTML report with DNA section
   - Export for reference

THAT'S IT! You now have a god-level system integrated!
"""
