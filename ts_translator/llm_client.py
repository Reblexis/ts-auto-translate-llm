"""
LLM Client module for interfacing with various LLM providers.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.chat_models.base import BaseChatModel

# Import possible LLM providers
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from ts_translator.constants import (
    GENERAL_TRANSLATION_CONTEXT,
    TRANSLATION_GUIDELINES
)

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    """Base class for LLM clients."""
    
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str, context: Optional[str] = None) -> str:
        """Translate text from source language to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            context: Optional context for the translation
            
        Returns:
            Translated text
        """
        pass
    
    @abstractmethod
    def batch_translate(self, texts: List[Dict[str, Any]], source_lang: str, target_lang: str) -> List[str]:
        """Translate multiple texts in a batch.
        
        Args:
            texts: List of dictionaries containing text and context
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            List of translated texts
        """
        pass


class LangChainLLMClient(BaseLLMClient):
    """LLM client using LangChain for provider abstraction."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.3, provider: str = "openai"):
        """Initialize the LangChain LLM client.
        
        Args:
            model_name: Name of the LLM model to use
            temperature: Temperature for generation (0.0 to 1.0)
            provider: LLM provider to use ('openai', 'anthropic', etc.)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.provider = provider.lower()
        logger.info(f"Initializing LLM client with provider: {provider}")
        logger.info(f"Using model: {model_name}")
        logger.info(f"Temperature: {temperature}")
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self) -> BaseChatModel:
        """Initialize the appropriate LLM based on provider.
        
        Returns:
            Initialized LLM
        """
        if self.provider == "openai":
            logger.info("Setting up OpenAI chat model")
            return ChatOpenAI(
                model_name=self.model_name,
                temperature=self.temperature,
            )
            
        elif self.provider == "anthropic":
            logger.info("Setting up Anthropic chat model")
            return ChatAnthropic(
                model=self.model_name,
                temperature=self.temperature,
            )
            
        logger.error(f"Unsupported provider: {self.provider}")
        raise ValueError(f"Unsupported provider: {self.provider}")
    
    def translate(self, text: str, source_lang: str, target_lang: str, context: Optional[str] = None) -> str:
        """Translate text using the LLM.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            context: Optional context to help with translation
            
        Returns:
            Translated text
        """
        logger.debug(f"Translating single text from {source_lang} to {target_lang}")
        logger.debug(f"Source text: {text}")
        if context:
            logger.debug(f"Context: {context}")
            
        # Build system prompt with general context
        system_prompt = f"""You are a professional translator with expertise in software localization.
Translate the given text from {source_lang} to {target_lang}.

Application Context:
{GENERAL_TRANSLATION_CONTEXT}

Translation Guidelines:
{TRANSLATION_GUIDELINES}

Preserve any formatting and special characters.
Do not add any explanations or notes - only return the translated text."""

        human_content = f"Text to translate: {text}"
        if context:
            human_content += f"\nContext: {context}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_content)
        ]
        
        logger.debug("Sending translation request to LLM")
        response = self.llm.invoke(messages)
        translated_text = response.content.strip()
        logger.debug(f"Received translation: {translated_text}")
        
        if not translated_text:
            logger.error("Received empty translation")
            raise RuntimeError("Empty translation received from LLM")
            
        return translated_text
    
    def batch_translate(self, texts: List[Dict[str, Any]], source_lang: str, target_lang: str) -> List[str]:
        """Translate multiple texts in a batch.
        
        Args:
            texts: List of dictionaries with 'text' and optional 'context' keys
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            List of translated texts
        """
        logger.info(f"Starting batch translation of {len(texts)} texts")
        logger.info(f"Source language: {source_lang}")
        logger.info(f"Target language: {target_lang}")
        
        # Build system prompt with general context
        system_prompt = f"""You are a professional translator with expertise in software localization.
Translate the following texts from {source_lang} to {target_lang}.

Application Context:
{GENERAL_TRANSLATION_CONTEXT}

Translation Guidelines:
{TRANSLATION_GUIDELINES}

For each text, provide only the translation without explanations.
Preserve any formatting and special characters."""

        human_content = "Texts to translate:\n\n"
        for i, item in enumerate(texts, 1):
            text = item['text']
            context = item.get('context', '')
            context_str = f"\nContext: {context}" if context else ""
            human_content += f"#{i}: {text}{context_str}\n\n"
            logger.debug(f"Text #{i} to translate: {text}")
            if context:
                logger.debug(f"Context #{i}: {context}")
        
        human_content += f"Respond with one translation per line, numbered #1, #2, etc. Only provide the translations, no explanations."
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_content)
        ]
        
        logger.debug("Sending batch translation request to LLM")
        response = self.llm.invoke(messages)
        translations = self._parse_batch_response(response.content, len(texts))
        
        # Validate translations
        if len(translations) != len(texts):
            logger.error(f"Expected {len(texts)} translations, got {len(translations)}")
            raise RuntimeError("Incorrect number of translations received")
            
        for i, translation in enumerate(translations):
            if not translation:
                logger.error(f"Empty translation received for text #{i+1}")
                raise RuntimeError(f"Empty translation received for text #{i+1}")
            logger.debug(f"Translation #{i+1}: {translation}")
        
        logger.info(f"Successfully translated {len(translations)} texts")
        return translations
            
    @staticmethod
    def _parse_batch_response(response: str, expected_count: int) -> List[str]:
        """Parse the batch response from the LLM.
        
        Args:
            response: Raw response from the LLM
            expected_count: Expected number of translations
            
        Returns:
            List of translated texts
        """
        logger.debug("Parsing batch response")
        logger.debug(f"Raw response: {response}")
        
        lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
        results = []
        
        for line in lines:
            # Try to extract translations following the #N: format
            if line.startswith('#') and ':' in line:
                try:
                    num = int(line[1:line.index(':')])
                    if 1 <= num <= expected_count:
                        text = line[line.index(':') + 1:].strip()
                        while len(results) < num - 1:
                            results.append("")  # Pad with empty strings if numbers are skipped
                        results.append(text)
                except ValueError:
                    continue
        
        # If we didn't get enough translations using the numbered format,
        # fall back to using all non-empty lines
        if len(results) != expected_count:
            results = [line for line in lines if not line.startswith('#') or ':' not in line][:expected_count]
        
        # Validate we have the correct number of translations
        if len(results) != expected_count:
            logger.error(f"Expected {expected_count} translations, got {len(results)}")
            logger.error("Raw response lines:")
            for line in lines:
                logger.error(f"  {line}")
            raise RuntimeError(f"Expected {expected_count} translations, got {len(results)}")
        
        # Validate no empty translations
        for i, translation in enumerate(results):
            if not translation:
                logger.error(f"Empty translation received for text #{i+1}")
                raise RuntimeError(f"Empty translation received for text #{i+1}")
        
        logger.debug(f"Parsed {len(results)} translations")
        return results


def get_llm_client(provider: str = "openai", model_name: Optional[str] = None, temperature: float = 0.3) -> BaseLLMClient:
    """Factory function to get an LLM client based on provider.
    
    Args:
        provider: The LLM provider to use
        model_name: The model name to use (or None for default)
        temperature: Temperature for generation
        
    Returns:
        An LLM client instance
    """
    provider = provider.lower()
    logger.info(f"Creating LLM client for provider: {provider}")
    
    # Set default model names based on provider
    if model_name is None:
        if provider == "openai":
            model_name = "gpt-4.1-mini"
        elif provider == "anthropic":
            model_name = "claude-3-haiku-20240307"
        else:
            logger.error(f"Unsupported provider: {provider}")
            raise ValueError(f"Unsupported provider: {provider}")
    
    logger.info(f"Using model: {model_name}")
    return LangChainLLMClient(model_name=model_name, temperature=temperature, provider=provider) 