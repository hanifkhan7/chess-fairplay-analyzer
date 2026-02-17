"""
AI Integration Module: LLM-based natural language explanations for chess analysis.

Supports multiple AI platforms for explaining statistical outputs:
- OpenAI (GPT-4, GPT-3.5-turbo)
- Anthropic Claude (Claude 3 models)
- Ollama (local open-source models)
- Deepseek (local/API-based)

Each provider has consistent interface for prompting and parsing responses.
"""

import os
import json
import logging
from typing import Dict, Optional, List, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AIResponse:
    """Standardized AI response wrapper."""
    success: bool
    content: str
    model: str
    provider: str
    error: Optional[str] = None
    tokens_used: Optional[Dict] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize provider.
        
        Args:
            api_key: API key if required
            model: Model name/ID
        """
        self.api_key = api_key
        self.model = model
        self.provider_name = self.__class__.__name__
    
    @abstractmethod
    def generate_response(self, prompt: str, max_tokens: int = 1024) -> AIResponse:
        """
        Generate LLM response.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens in response
            
        Returns:
            AIResponse object
        """
        pass
    
    @abstractmethod
    def validate_credentials(self) -> bool:
        """Validate API credentials/setup."""
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider (GPT-4, GPT-3.5)."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (or from OPENAI_API_KEY env var)
            model: Model name (default: gpt-3.5-turbo)
        """
        super().__init__(api_key, model)
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1"
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize OpenAI client."""
        try:
            import openai
            if self.api_key:
                openai.api_key = self.api_key
            self.client = openai
        except ImportError:
            logger.warning("OpenAI library not installed. Install with: pip install openai")
    
    def validate_credentials(self) -> bool:
        """Validate OpenAI API key."""
        if not self.api_key:
            return False
        
        try:
            import openai
            # Try a simple API call to validate
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5,
                api_key=self.api_key
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI validation failed: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """List available OpenAI models."""
        return ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"]
    
    def generate_response(self, prompt: str, max_tokens: int = 1024) -> AIResponse:
        """Generate response using OpenAI API."""
        try:
            if not self.client or not self.api_key:
                return AIResponse(
                    success=False,
                    content="",
                    model=self.model,
                    provider="OpenAI",
                    error="OpenAI client not initialized or API key missing"
                )
            
            import openai
            openai.api_key = self.api_key
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            tokens = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
            
            return AIResponse(
                success=True,
                content=content,
                model=self.model,
                provider="OpenAI",
                tokens_used=tokens
            )
        
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return AIResponse(
                success=False,
                content="",
                model=self.model,
                provider="OpenAI",
                error=str(e)
            )


class ClaudeProvider(LLMProvider):
    """Anthropic Claude API provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        """
        Initialize Claude provider.
        
        Args:
            api_key: Anthropic API key (or from ANTHROPIC_API_KEY env var)
            model: Model name (default: claude-3-sonnet-20240229)
        """
        super().__init__(api_key, model)
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize Anthropic client."""
        try:
            from anthropic import Anthropic
            if self.api_key:
                self.client = Anthropic(api_key=self.api_key)
            else:
                self.client = Anthropic()
        except ImportError:
            logger.warning("Anthropic library not installed. Install with: pip install anthropic")
    
    def validate_credentials(self) -> bool:
        """Validate Claude API key."""
        if not self.api_key:
            return False
        
        try:
            # Simple test call
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=5,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception as e:
            logger.error(f"Claude validation failed: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """List available Claude models."""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
    
    def generate_response(self, prompt: str, max_tokens: int = 1024) -> AIResponse:
        """Generate response using Claude API."""
        try:
            if not self.client:
                return AIResponse(
                    success=False,
                    content="",
                    model=self.model,
                    provider="Claude",
                    error="Claude client not initialized"
                )
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            tokens = {
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens
            }
            
            return AIResponse(
                success=True,
                content=content,
                model=self.model,
                provider="Claude",
                tokens_used=tokens
            )
        
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return AIResponse(
                success=False,
                content="",
                model=self.model,
                provider="Claude",
                error=str(e)
            )


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, model: str = "mistral", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama provider.
        
        Args:
            model: Model name (e.g., mistral, neural-chat, llama2)
            base_url: Ollama server URL (default: localhost:11434)
        """
        super().__init__(None, model)
        self.base_url = base_url
        self.available_models = []
        self._check_server()
    
    def _check_server(self):
        """Check if Ollama server is running."""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [m['name'].split(':')[0] for m in data.get('models', [])]
                logger.info(f"Ollama server online. Available models: {self.available_models}")
            else:
                logger.warning("Ollama server not responding correctly")
        except Exception as e:
            logger.warning(f"Ollama server not reachable at {self.base_url}: {e}")
    
    def validate_credentials(self) -> bool:
        """Check if Ollama server is running."""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[str]:
        """List available Ollama models."""
        return self.available_models or ["mistral", "neural-chat", "llama2", "orca"]
    
    def generate_response(self, prompt: str, max_tokens: int = 1024) -> AIResponse:
        """Generate response using Ollama."""
        try:
            import requests
            
            # Check if model is available
            if self.model not in self.available_models:
                return AIResponse(
                    success=False,
                    content="",
                    model=self.model,
                    provider="Ollama",
                    error=f"Model '{self.model}' not available. Available: {self.available_models}"
                )
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "num_predict": max_tokens
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return AIResponse(
                    success=False,
                    content="",
                    model=self.model,
                    provider="Ollama",
                    error=f"HTTP {response.status_code}"
                )
            
            data = response.json()
            content = data.get('response', '')
            
            return AIResponse(
                success=True,
                content=content,
                model=self.model,
                provider="Ollama"
            )
        
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return AIResponse(
                success=False,
                content="",
                model=self.model,
                provider="Ollama",
                error=str(e)
            )


class DeepseekProvider(LLMProvider):
    """Deepseek API provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat"):
        """
        Initialize Deepseek provider.
        
        Args:
            api_key: Deepseek API key (or from DEEPSEEK_API_KEY env var)
            model: Model name (default: deepseek-chat)
        """
        super().__init__(api_key, model)
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.base_url = "https://api.deepseek.com/v1"
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize Deepseek client (uses OpenAI-compatible API)."""
        try:
            from openai import OpenAI
            if self.api_key:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
        except ImportError:
            logger.warning("OpenAI library not installed (required for Deepseek)")
    
    def validate_credentials(self) -> bool:
        """Validate Deepseek API key."""
        if not self.api_key:
            return False
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"Deepseek validation failed: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """List available Deepseek models."""
        return ["deepseek-chat", "deepseek-coder"]
    
    def generate_response(self, prompt: str, max_tokens: int = 1024) -> AIResponse:
        """Generate response using Deepseek API."""
        try:
            if not self.client:
                return AIResponse(
                    success=False,
                    content="",
                    model=self.model,
                    provider="Deepseek",
                    error="Deepseek client not initialized"
                )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            tokens = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
            
            return AIResponse(
                success=True,
                content=content,
                model=self.model,
                provider="Deepseek",
                tokens_used=tokens
            )
        
        except Exception as e:
            logger.error(f"Deepseek API error: {e}")
            return AIResponse(
                success=False,
                content="",
                model=self.model,
                provider="Deepseek",
                error=str(e)
            )


class AIIntegration:
    """Main AI Integration manager."""
    
    PROVIDERS = {
        'openai': OpenAIProvider,
        'claude': ClaudeProvider,
        'ollama': OllamaProvider,
        'deepseek': DeepseekProvider,
    }
    
    def __init__(self):
        """Initialize AI integration."""
        self.current_provider: Optional[LLMProvider] = None
        self.provider_name: Optional[str] = None
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available providers."""
        return list(cls.PROVIDERS.keys())
    
    def initialize_provider(self, provider: str, api_key: Optional[str] = None,
                           model: Optional[str] = None, **kwargs) -> bool:
        """
        Initialize a specific provider.
        
        Args:
            provider: Provider name ('openai', 'claude', 'ollama', 'deepseek')
            api_key: API key if required
            model: Model name
            **kwargs: Additional provider-specific arguments
            
        Returns:
            True if successful
        """
        provider_lower = provider.lower()
        
        if provider_lower not in self.PROVIDERS:
            logger.error(f"Unknown provider: {provider}. Available: {list(self.PROVIDERS.keys())}")
            return False
        
        try:
            if provider_lower == 'openai':
                self.current_provider = OpenAIProvider(api_key=api_key, model=model or 'gpt-3.5-turbo')
            elif provider_lower == 'claude':
                self.current_provider = ClaudeProvider(api_key=api_key, model=model or 'claude-3-sonnet-20240229')
            elif provider_lower == 'ollama':
                base_url = kwargs.get('base_url', 'http://localhost:11434')
                self.current_provider = OllamaProvider(model=model or 'mistral', base_url=base_url)
            elif provider_lower == 'deepseek':
                self.current_provider = DeepseekProvider(api_key=api_key, model=model or 'deepseek-chat')
            
            self.provider_name = provider_lower
            
            # Validate credentials if needed
            if provider_lower != 'ollama' and not self.current_provider.validate_credentials():
                logger.warning(f"{provider} credentials validation failed")
                return False
            
            logger.info(f"Provider '{provider}' initialized successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to initialize {provider}: {e}")
            return False
    
    def explain_statistics(self, analysis_type: str, stats: Dict[str, Any],
                          player_name: str = "") -> AIResponse:
        """
        Generate natural language explanation of chess statistics.
        
        Args:
            analysis_type: Type of analysis (e.g., 'player_dna', 'strength_profile', 'fatigue')
            stats: Dictionary of statistics
            player_name: Player name for context
            
        Returns:
            AIResponse with explanation
        """
        if not self.current_provider:
            return AIResponse(
                success=False,
                content="",
                model="",
                provider="",
                error="No AI provider initialized"
            )
        
        prompt = self._build_explanation_prompt(analysis_type, stats, player_name)
        return self.current_provider.generate_response(prompt, max_tokens=1024)
    
    def _build_explanation_prompt(self, analysis_type: str, stats: Dict,
                                 player_name: str) -> str:
        """Build a prompt for explaining statistics."""
        base_prompt = f"""As a chess expert, explain the following {analysis_type} analysis for {player_name or 'a player'}.
Focus on what the numbers mean for their playing style and strength.
Be concise but insightful. Highlight notable patterns and weaknesses.

Statistics:
{json.dumps(stats, indent=2)}

Provide a natural language explanation that a casual chess player would understand."""
        
        return base_prompt
    
    def explain_cheat_detection(self, analysis_results: Dict) -> AIResponse:
        """Generate explanation for cheat detection results."""
        if not self.current_provider:
            return AIResponse(
                success=False,
                content="",
                model="",
                provider="",
                error="No AI provider initialized"
            )
        
        prompt = f"""As a chess fairplay expert, analyze these cheat detection results and explain what they mean:

Analysis Results:
{json.dumps(analysis_results, indent=2)}

Explain:
1. What the detection methods found
2. How confident we should be in these findings
3. What red flags (if any) stand out
4. Recommended next steps for investigation

Be objective and avoid false accusations. Always mention confidence levels and false positive risks."""
        
        return self.current_provider.generate_response(prompt, max_tokens=1500)
    
    def explain_opening_repertoire(self, dna_data: Dict) -> AIResponse:
        """Generate explanation for opening repertoire/DNA."""
        if not self.current_provider:
            return AIResponse(
                success=False,
                content="",
                model="",
                provider="",
                error="No AI provider initialized"
            )
        
        prompt = f"""As a chess coach, analyze this player's opening repertoire and provide insights:

Opening DNA Data:
{json.dumps(dna_data, indent=2)}

Provide:
1. Summary of their opening choices and philosophy
2. Strengths in their repertoire
3. Weaknesses or gaps
4. Recommendations for improvement
5. Notable patterns in their play

Be encouraging but honest about areas for improvement."""
        
        return self.current_provider.generate_response(prompt, max_tokens=1500)
    
    def compare_players_ai(self, player1_stats: Dict, player2_stats: Dict,
                          player1_name: str, player2_name: str) -> AIResponse:
        """Generate comparison between two players."""
        if not self.current_provider:
            return AIResponse(
                success=False,
                content="",
                model="",
                provider="",
                error="No AI provider initialized"
            )
        
        prompt = f"""As a chess analyst, compare these two players based on their statistics:

{player1_name} Statistics:
{json.dumps(player1_stats, indent=2)}

{player2_name} Statistics:
{json.dumps(player2_stats, indent=2)}

Provide:
1. Head-to-head comparison of key strengths
2. Difference in playing style
3. Who would have advantage in a match and why
4. Recommendations for {player1_name} to improve against {player2_name}

Be balanced and fair in your analysis."""
        
        return self.current_provider.generate_response(prompt, max_tokens=1500)


def create_ai_integration(provider: str, api_key: Optional[str] = None,
                         model: Optional[str] = None, **kwargs) -> Optional[AIIntegration]:
    """
    Factory function to create and initialize AI integration.
    
    Args:
        provider: Provider name ('openai', 'claude', 'ollama', 'deepseek')
        api_key: API key if required
        model: Model name
        **kwargs: Additional arguments
        
    Returns:
        Initialized AIIntegration or None if failed
        
    Example:
        ai = create_ai_integration('openai', api_key='sk-...')
        response = ai.explain_statistics('player_dna', stats_dict, 'hikaru')
        print(response.content)
    """
    ai = AIIntegration()
    if ai.initialize_provider(provider, api_key=api_key, model=model, **kwargs):
        return ai
    return None


# Convenience functions
def get_provider_info() -> Dict[str, Dict]:
    """Get information about all providers."""
    return {
        'openai': {
            'name': 'OpenAI',
            'models': ['gpt-4', 'gpt-4-turbo-preview', 'gpt-3.5-turbo'],
            'requires_api_key': True,
            'cost': 'Paid',
            'latency': 'Low-Medium',
            'description': 'Commercial API with powerful models'
        },
        'claude': {
            'name': 'Anthropic Claude',
            'models': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
            'requires_api_key': True,
            'cost': 'Paid',
            'latency': 'Low-Medium',
            'description': 'Strong reasoning and analysis capabilities'
        },
        'ollama': {
            'name': 'Ollama (Local)',
            'models': ['mistral', 'neural-chat', 'llama2', 'orca'],
            'requires_api_key': False,
            'cost': 'Free',
            'latency': 'Medium-High (depends on hardware)',
            'description': 'Run open-source models locally, no API key needed'
        },
        'deepseek': {
            'name': 'Deepseek',
            'models': ['deepseek-chat', 'deepseek-coder'],
            'requires_api_key': True,
            'cost': 'Paid',
            'latency': 'Low-Medium',
            'description': 'Fast API-based models from Deepseek'
        }
    }
