"""
Configuration module for managing settings.
"""

import os
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path
import json
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
load_dotenv()


@dataclass
class TranslatorConfig:
    """Configuration for the translation process."""
    source_lang: str = "en_US"
    target_lang: str = "es_ES"
    llm_provider: str = "openai"
    llm_model: Optional[str] = None
    temperature: float = 0.3
    batch_size: int = 10
    max_retries: int = 3
    api_key: Optional[str] = None
    output_suffix: str = "_translated"
    
    @classmethod
    def from_env(cls) -> 'TranslatorConfig':
        """Create a config instance from environment variables.
        
        Returns:
            TranslatorConfig instance with values from environment variables
        """
        return cls(
            source_lang=os.getenv("TS_TRANSLATOR_SOURCE_LANG", "en_US"),
            target_lang=os.getenv("TS_TRANSLATOR_TARGET_LANG", "es_ES"),
            llm_provider=os.getenv("TS_TRANSLATOR_LLM_PROVIDER", "openai"),
            llm_model=os.getenv("TS_TRANSLATOR_LLM_MODEL", None),
            temperature=float(os.getenv("TS_TRANSLATOR_TEMPERATURE", "0.3")),
            batch_size=int(os.getenv("TS_TRANSLATOR_BATCH_SIZE", "10")),
            max_retries=int(os.getenv("TS_TRANSLATOR_MAX_RETRIES", "3")),
            api_key=os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"),
            output_suffix=os.getenv("TS_TRANSLATOR_OUTPUT_SUFFIX", "_translated")
        )
    
    @classmethod
    def from_file(cls, config_path: str) -> 'TranslatorConfig':
        """Create a config instance from a JSON file.
        
        Args:
            config_path: Path to the JSON config file
            
        Returns:
            TranslatorConfig instance with values from the file
        """
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            return cls(**config_data)
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {e}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary.
        
        Returns:
            Dictionary representation of the config
        """
        return {
            "source_lang": self.source_lang,
            "target_lang": self.target_lang,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "temperature": self.temperature,
            "batch_size": self.batch_size,
            "max_retries": self.max_retries,
            "output_suffix": self.output_suffix
            # Note: We don't include API keys for security reasons
        }
    
    def to_file(self, config_path: str) -> None:
        """Save config to a JSON file.
        
        Args:
            config_path: Path to save the config file to
        """
        try:
            # Make sure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
                
            logger.debug(f"Config saved to {config_path}")
        except Exception as e:
            logger.error(f"Error saving config to {config_path}: {e}")
            raise
    
    def update(self, **kwargs) -> 'TranslatorConfig':
        """Update config with new values.
        
        Args:
            **kwargs: New values to update
            
        Returns:
            Updated TranslatorConfig instance
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                logger.warning(f"Unknown config option: {key}")
        
        return self


def setup_logging(level: int = logging.INFO) -> None:
    """Set up logging configuration.
    
    Args:
        level: Logging level
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ) 