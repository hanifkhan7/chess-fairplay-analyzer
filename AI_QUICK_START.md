QUICK START GUIDE - AI-Enhanced Chess Analysis
===============================================

INSTALLATION & SETUP
====================

1. Install Required Packages
   pip install openai anthropic requests

2. Obtain API Keys (Optional, based on preferred provider)
   
   For OpenAI (GPT-4/GPT-3.5):
   - Visit: https://platform.openai.com/account/api-keys
   - Create API key
   - Keep it secret!
   
   For Claude (Anthropic):
   - Visit: https://console.anthropic.com/account/keys
   - Create API key
   - Keep it secret!
   
   For Deepseek:
   - Visit: https://platform.deepseek.com/account/keys
   - Create API key
   - Keep it secret!
   
   For Ollama (Local, FREE):
   - Download from: https://ollama.ai
   - Install and run locally
   - No API key needed!

3. Configure (Optional)
   Add to config.yaml:
   ```yaml
   ai:
     current_provider: openai
     api_keys:
       openai: YOUR_API_KEY_HERE
       claude: YOUR_API_KEY_HERE
       deepseek: YOUR_API_KEY_HERE
   ```


RUNNING THE APPLICATION
=======================

Basic Usage:
   python run_menu.py

This opens the main menu. Select Option 10:
   "Opening Repertoire & DNA"

The process:
1. Enter player username (e.g., "hikaru")
2. Select number of games (default: 1000)
3. Select color: White (1), Black (2), or Both (3)
4. Wait for games to be fetched
5. DNA analysis runs
6. When asked "Would you like AI-powered explanation?" → Enter 'y'
7. Select your AI provider
8. [If API key required] Enter API key
9. Select model (uses recommended default)
10. AI generates explanation
11. Report saves with AI analysis


FEATURE WALKTHROUGH
====================

### Without AI (Statistics Only)
Command: Select Option 10 → Say 'n' to AI prompt
Result:  Report with opening statistics

### With OpenAI (GPT-3.5)
Command:
  - Select Option 10
  - Say 'y' to AI
  - Choose "1" (OpenAI)
  - Paste API key when asked
  - Press Enter for default model
Result:  Full report + AI explanation using GPT-3.5-turbo

### With Claude (Anthropic)
Command:
  - Select Option 10
  - Say 'y' to AI
  - Choose "2" (Claude)
  - Paste API key when asked
  - Press Enter for default model
Result:  Full report + AI explanation using Claude 3 Sonnet

### With Ollama (Local, Free)
Prerequisites:
  1. Download Ollama from https://ollama.ai
  2. Run: ollama serve
  3. In new terminal: ollama pull mistral
  4. Leave server running

Command:
  - Select Option 10
  - Say 'y' to AI
  - Choose "3" (Ollama)
  - Press Enter for default server (localhost:11434)
  - Press Enter for default model (mistral)
Result:  Full report + AI explanation using local Mistral model

### With Deepseek
Command:
  - Select Option 10
  - Say 'y' to AI
  - Choose "4" (Deepseek)
  - Paste API key when asked
  - Press Enter for default model
Result:  Full report + AI explanation using Deepseek


EXAMPLE OUTPUTS
===============

Opening Repertoire Report (Sample):

    ======================================================================
    [OPENING TREE] HIKARU
    ======================================================================
    
    Total Games: 500
    Color: WHITE
    
    Record: 275W 50D 175L
    Win Rate: 55.0%
    
    ⭐ FAVORITE OPENINGS (Best Performance):
      1. Ruy Lopez                            (125G)  65.0%
      2. Sicilian Defense                     (85G)   50.0%
      3. Italian Game                         (70G)   48.0%
    
    ⚠️  WEAK LINES (Needs Improvement):
      1. Caro-Kann Defense                    (25G)   28.0%
      2. French Defense                       (20G)   35.0%
      3. Queen's Gambit                       (15G)   40.0%
    
    🎲 RISKY LINES (High Variance):
      1. Scandinavian Defense                 (5G)    80.0%
      2. Nimzo-Larsen Attack                  (3G)    100.0%

AI Explanation (Sample):

    ======================================================================
    [AI ANALYSIS] Powered by OPENAI
    ======================================================================
    
    Hikaru demonstrates a strong classical opening repertoire centered on the
    Ruy Lopez, which serves as their primary weapon with White. The 65% win rate
    suggests deep preparation and comfort in this opening.
    
    Key Observations:
    
    1. **Solid Positional Player**: Heavy reliance on Ruy Lopez and Sicilian
       indicates classical, positional approach rather than tactical tricks.
    
    2. **Weakness Against Flexible Systems**: The Caro-Kann and French defense
       results suggest difficulty against setup-based openings. Consider:
       - Study prophylactic ideas
       - Adjust middle-game planning
    
    3. **Conservative Repertoire**: Limited experimentation despite experimental
       weapons (Scandinavian, Nimzo-Larsen). These high-variance lines might be
       recent additions or tournament gambles.
    
    4. **Opening Preparation**: The consistency across 500 games suggests either
       excellent opening knowledge OR tendency to play familiar positions.
    
    Recommendations:
    - Deepen Sicilian preparation (50% is below potential)
    - Address Caro-Kann weakness with systematic study
    - Continue leveraging Ruy Lopez strength


CONFIGURATION FILES
===================

Reports are saved to: reports/

Files generated:
  - reports/{username}_player_dna_report.txt (Statistics)
  - reports/{username}_player_dna.json (Raw data)
  - reports/{username}_player_dna_with_ai.txt (With AI explanation)


COST ESTIMATES
==============

Per Analysis (500 games, ~2000 moves analyzed):

OpenAI (GPT-3.5):
  - Input tokens: ~2000
  - Output tokens: ~500
  - Estimated cost: $0.01-0.05

Claude (Sonnet):
  - Input tokens: ~2000
  - Output tokens: ~500
  - Estimated cost: $0.01-0.03

Deepseek:
  - Typically cheaper than OpenAI
  - Estimated cost: $0.005-0.01

Ollama (Local):
  - No API costs
  - One-time download (2-30GB depending on model)
  - CPU/GPU usage only


TROUBLESHOOTING
===============

Q: "Failed to build Player DNA"
A: - Ensure 500+ games were fetched
   - Check username spelling
   - Try smaller min_games value

Q: "OpenAI API error: 401 Unauthorized"
A: - Verify API key is correct (no spaces, full key)
   - Check account has credits
   - Try copying key again

Q: "Claude authentication failed"
A: - Verify Anthropic API key (different from OpenAI)
   - Check key permissions
   - Ensure key is from https://console.anthropic.com

Q: "Ollama server not reachable"
A: - Ensure Ollama is running: ollama serve
   - Verify URL is correct (default: http://localhost:11434)
   - Check firewall allows localhost:11434

Q: "Model not found"
A: - For Ollama: run "ollama pull mistral"
   - For OpenAI: use "gpt-3.5-turbo" or "gpt-4"
   - For Claude: use "claude-3-sonnet-20240229"


ENVIRONMENT VARIABLES (Optional)
=================================

Instead of entering API keys in menu, set environment variables:

Windows (CMD):
  set OPENAI_API_KEY=sk-...
  set ANTHROPIC_API_KEY=sk-ant-...
  set DEEPSEEK_API_KEY=sk-...

Windows (PowerShell):
  $env:OPENAI_API_KEY="sk-..."
  $env:ANTHROPIC_API_KEY="sk-ant-..."
  $env:DEEPSEEK_API_KEY="sk-..."

Linux/Mac:
  export OPENAI_API_KEY=sk-...
  export ANTHROPIC_API_KEY=sk-ant-...
  export DEEPSEEK_API_KEY=sk-...

Menu will automatically detect and use these.


NEXT STEPS
==========

1. Test with your favorite player
   - Small dataset (100-200 games) for quick testing
   - Large dataset (500+ games) for comprehensive analysis

2. Try different AI providers
   - Compare output quality
   - See which you prefer
   - Evaluate cost vs quality

3. Explore other menu options
   - Option 1: Basic player analysis
   - Option 5: Accuracy reports
   - Option 7: Multi-player comparison
   - More coming soon with AI integration!

4. Provide feedback
   - Report bugs or issues
   - Suggest improvements
   - Share interesting AI discoveries


SUPPORT
=======

For issues:
1. Check error message in terminal
2. Review TROUBLESHOOTING section above
3. Verify API key/credentials
4. Check internet connection
5. Ensure Ollama is running (if using)

Common file locations:
- config.yaml - Configuration
- reports/ - Generated reports
- .venv/ - Python virtual environment


VERSION & CHANGELOG
===================

Version 1.0 (Current)
✓ Player DNA analysis
✓ AI report generation
✓ Support for 4 AI platforms
✓ Config persistence
✓ Error handling
✓ Report formatting

Future:
- AI integration for other analysis types
- Streaming responses
- Cost optimization
- Additional providers


CREDITS
=======

AI Providers:
- OpenAI: https://openai.com
- Anthropic: https://anthropic.com
- Ollama: https://ollama.ai
- Deepseek: https://deepseek.com

Libraries:
- chess: Python chess library
- requests: HTTP library
- openai: OpenAI SDK
- anthropic: Anthropic SDK

Chess Fairplay Analyzer
Advanced Statistical Analysis for Chess

---
Ready to analyze? Run: python run_menu.py
