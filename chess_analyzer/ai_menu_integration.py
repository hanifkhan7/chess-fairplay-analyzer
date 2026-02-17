"""
Menu Integration for AI Report Generation.

Adds AI-powered natural language explanations to chess analysis reports.
Integrates with the main menu system to allow users to:
1. Choose an AI provider (OpenAI, Claude, Ollama, Deepseek)
2. Configure API keys or connection settings
3. Generate AI-enhanced reports
4. View explanations alongside statistical data
"""

from __future__ import annotations
import os
import json
import sys
from typing import Optional, Dict, Any, List
from pathlib import Path

# Placeholder for import - will be filled when integrated
try:
    from .ai_integration import (
        AIIntegration, 
        create_ai_integration, 
        get_provider_info,
        AIResponse
    )
except ImportError:
    pass


class AIReportGenerator:
    """Manages AI-enhanced report generation."""
    
    def __init__(self):
        """Initialize AI report generator."""
        self.ai: Optional[AIIntegration] = None
        self.current_provider: Optional[str] = None
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Load AI configuration from config.yaml or create default."""
        config_path = Path('config.yaml')
        if config_path.exists():
            try:
                import yaml
                with open(config_path, 'r') as f:
                    full_config = yaml.safe_load(f) or {}
                    self.config = full_config.get('ai', {})
            except:
                pass
    
    def _save_config(self):
        """Save AI configuration to config.yaml."""
        try:
            import yaml
            config_path = Path('config.yaml')
            
            # Load existing config
            if config_path.exists():
                with open(config_path, 'r') as f:
                    full_config = yaml.safe_load(f) or {}
            else:
                full_config = {}
            
            # Update AI section
            full_config['ai'] = self.config
            
            # Save
            with open(config_path, 'w') as f:
                yaml.dump(full_config, f, default_flow_style=False)
        except:
            pass
    
    def show_provider_selection_menu(self) -> Optional[str]:
        """
        Show menu for selecting AI provider.
        
        Returns:
            Selected provider name or None
        """
        print("\n" + "="*70)
        print("[AI] SELECT AI PROVIDER FOR REPORT GENERATION")
        print("="*70)
        
        providers_info = get_provider_info()
        providers = list(providers_info.keys())
        
        for i, provider in enumerate(providers, 1):
            info = providers_info[provider]
            api_note = " (requires API key)" if info['requires_api_key'] else " (local, no API needed)"
            print(f"\n{i}. {info['name']}")
            print(f"   Models: {', '.join(info['models'][:2])}...")
            print(f"   Cost: {info['cost']}{api_note}")
            print(f"   Latency: {info['latency']}")
            print(f"   Note: {info['description']}")
        
        print(f"\n{len(providers)+1}. Skip AI Enhancement (use statistics only)")
        print(f"{len(providers)+2}. Cancel")
        
        choice = input(f"\nSelect provider (1-{len(providers)+2}): ").strip()
        
        try:
            choice_int = int(choice)
            if choice_int == len(providers) + 1:
                return "skip"
            elif choice_int == len(providers) + 2:
                return None
            elif 1 <= choice_int <= len(providers):
                return providers[choice_int - 1]
        except:
            pass
        
        return None
    
    def configure_provider(self, provider: str) -> bool:
        """
        Configure the selected provider with API keys or settings.
        
        Args:
            provider: Provider name
            
        Returns:
            True if configuration successful
        """
        print("\n" + "="*70)
        print(f"[AI] CONFIGURE {provider.upper()}")
        print("="*70)
        
        providers_info = get_provider_info()
        if provider not in providers_info:
            print(f"Unknown provider: {provider}")
            return False
        
        info = providers_info[provider]
        
        # API Key
        if info['requires_api_key']:
            print(f"\n{info['name']} requires an API key.")
            print("You can get one from their website:")
            
            if provider == 'openai':
                print("  → https://platform.openai.com/account/api-keys")
            elif provider == 'claude':
                print("  → https://console.anthropic.com/account/keys")
            elif provider == 'deepseek':
                print("  → https://platform.deepseek.com/account/keys")
            
            # Try to get from environment or config
            env_var = f"{provider.upper()}_API_KEY"
            default_key = os.getenv(env_var) or self.config.get('api_keys', {}).get(provider, '')
            
            api_key = input(f"\nEnter API key (or press Enter to use default/env): ").strip()
            
            if not api_key and not default_key:
                print("\n✗ No API key provided and none found in config or environment")
                return False
            
            api_key = api_key or default_key
        else:
            api_key = None
        
        # Model selection
        print(f"\nAvailable models: {', '.join(info['models'])}")
        model = input(f"Enter model name (default: {info['models'][0]}): ").strip()
        model = model or info['models'][0]
        
        # Provider-specific settings
        kwargs = {}
        if provider == 'ollama':
            base_url = input("\nOllama server URL (default: http://localhost:11434): ").strip()
            if base_url:
                kwargs['base_url'] = base_url
        
        # Try to initialize
        print(f"\nInitializing {provider}...")
        try:
            from .ai_integration import create_ai_integration
            self.ai = create_ai_integration(provider, api_key=api_key, model=model, **kwargs)
            
            if self.ai:
                print(f"✓ {provider} initialized successfully")
                self.current_provider = provider
                
                # Save to config
                if 'api_keys' not in self.config:
                    self.config['api_keys'] = {}
                self.config['api_keys'][provider] = api_key if api_key else ""
                self.config['model'] = model
                self.config['current_provider'] = provider
                self._save_config()
                
                return True
            else:
                print(f"✗ Failed to initialize {provider}")
                return False
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False
    
    def prompt_for_ai(self, analysis_name: str = "") -> bool:
        """
        Prompt user whether they want AI enhancement.
        
        Args:
            analysis_name: Description of the analysis
            
        Returns:
            True if user wants AI
        """
        print(f"\n{'─'*70}")
        use_ai = input(f"Would you like AI-powered explanation of {analysis_name or 'these results'}? (y/n): ").strip().lower()
        
        if use_ai != 'y':
            return False
        
        # Check if already configured
        if self.ai and self.current_provider:
            reuse = input(f"Use existing {self.current_provider} configuration? (y/n): ").strip().lower()
            if reuse == 'y':
                return True
        
        # New configuration
        provider = self.show_provider_selection_menu()
        
        if provider == "skip":
            return False
        elif provider is None:
            return False
        else:
            return self.configure_provider(provider)
    
    def generate_ai_explanation(self, analysis_type: str, data: Dict[str, Any],
                               player_name: str = "", context: str = "") -> Optional[str]:
        """
        Generate AI explanation for analysis results.
        
        Args:
            analysis_type: Type of analysis ('player_dna', 'strength_profile', etc.)
            data: Analysis data
            player_name: Player name for context
            context: Additional context
            
        Returns:
            AI-generated explanation or None if failed
        """
        if not self.ai:
            return None
        
        try:
            print(f"\n[AI] Generating {self.current_provider} explanation...")
            
            # Choose appropriate explanation method
            if analysis_type == 'player_dna':
                response = self.ai.explain_opening_repertoire(data)
            elif analysis_type == 'cheat_detection':
                response = self.ai.explain_cheat_detection(data)
            elif analysis_type == 'comparison':
                # Need player names for comparison
                if 'player1_name' in data and 'player2_name' in data:
                    response = self.ai.compare_players_ai(
                        data.get('player1_stats', {}),
                        data.get('player2_stats', {}),
                        data['player1_name'],
                        data['player2_name']
                    )
                else:
                    response = self.ai.explain_statistics(analysis_type, data, player_name)
            else:
                # Generic explanation
                response = self.ai.explain_statistics(analysis_type, data, player_name)
            
            if response.success:
                print("✓ AI explanation generated")
                return response.content
            else:
                print(f"✗ AI error: {response.error}")
                return None
        
        except Exception as e:
            print(f"✗ Error generating explanation: {str(e)}")
            return None
    
    def append_ai_to_report(self, report_path: str, ai_explanation: str, 
                           provider: str) -> bool:
        """
        Append AI explanation to existing report file.
        
        Args:
            report_path: Path to report file
            ai_explanation: AI-generated explanation
            provider: Provider name
            
        Returns:
            True if successful
        """
        try:
            section = f"\n\n{'='*70}\n"
            section += f"[AI ANALYSIS] Powered by {provider.upper()}\n"
            section += f"{'='*70}\n\n"
            section += ai_explanation
            section += f"\n\n{'='*70}\n"
            section += "Note: AI analysis is for reference and should not be considered professional advice.\n"
            section += "Always verify important findings with human expert review.\n"
            section += f"{'='*70}\n"
            
            with open(report_path, 'a') as f:
                f.write(section)
            
            return True
        except Exception as e:
            print(f"✗ Error appending to report: {str(e)}")
            return False
    
    def create_ai_enhanced_report(self, analysis_type: str, data: Dict[str, Any],
                                 base_report: str, player_name: str = "") -> str:
        """
        Create a combined report with statistics and AI explanation.
        
        Args:
            analysis_type: Type of analysis
            data: Analysis data
            base_report: Base report content (statistics)
            player_name: Player name
            
        Returns:
            Combined report with AI explanation
        """
        report = base_report
        
        if self.ai:
            ai_explanation = self.generate_ai_explanation(analysis_type, data, player_name)
            if ai_explanation:
                report += f"\n\n{'='*70}\n"
                report += f"[AI ANALYSIS] Powered by {self.current_provider.upper()}\n"
                report += f"{'='*70}\n\n"
                report += ai_explanation
                report += f"\n\n{'='*70}\n"
        
        return report


def integrate_ai_with_menu(menu_function):
    """
    Decorator to add AI enhancement to menu functions.
    
    Usage:
        @integrate_ai_with_menu
        def analyze_player():
            ...
    """
    def wrapper(*args, **kwargs):
        # Run original function
        result = menu_function(*args, **kwargs)
        
        # Optionally add AI enhancement
        # This is handled by the AIReportGenerator class
        return result
    
    return wrapper


def interactive_ai_setup() -> Optional['AIIntegration']:
    """
    Interactive setup for AI integration.
    Guide user through selecting and configuring their preferred AI provider.
    
    Returns:
        Configured AIIntegration or None
    """
    print("\n" + "="*70)
    print("[AI SETUP] Chess Analysis AI Enhancement")
    print("="*70)
    print("\nThis tool can use AI to explain your chess analysis results")
    print("in natural language. Choose your preferred AI platform:\n")
    
    generator = AIReportGenerator()
    provider = generator.show_provider_selection_menu()
    
    if provider is None:
        print("\n[INFO] AI enhancement cancelled")
        return None
    elif provider == "skip":
        print("\n[INFO] Using statistics only (no AI enhancement)")
        return None
    
    if generator.configure_provider(provider):
        print(f"\n✓ AI integration ready!")
        print(f"  Provider: {provider}")
        print(f"  Model: {generator.ai.current_provider.__class__.__name__}")
        return generator.ai
    else:
        print("\n✗ AI integration failed")
        return None


if __name__ == '__main__':
    # Test the interactive setup
    ai = interactive_ai_setup()
    
    if ai:
        # Try a test explanation
        test_data = {
            'total_games': 100,
            'win_rate': 55.0,
            'draw_rate': 10.0,
            'loss_rate': 35.0
        }
        
        response = ai.explain_statistics('strength_profile', test_data, 'test_player')
        if response.success:
            print("\n[TEST] AI Response:")
            print(response.content)
        else:
            print(f"\n[ERROR] {response.error}")
