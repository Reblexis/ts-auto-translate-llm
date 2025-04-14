"""
Main translator module for handling .ts file translations.
"""

import logging
import os
from typing import Dict, List, Optional, Any, Tuple
from tqdm import tqdm

from ts_translator.parser import TSFileParser, TranslationUnit
from ts_translator.llm_client import BaseLLMClient, get_llm_client

logger = logging.getLogger(__name__)


class TSTranslator:
    """Main translator class for handling .ts file translations."""
    
    def __init__(
        self,
        llm_client: Optional[BaseLLMClient] = None,
        source_lang: str = "en_US",
        target_lang: str = "es_ES",
        batch_size: int = 10,
        max_retries: int = 3
    ):
        """Initialize the translator.
        
        Args:
            llm_client: LLM client to use for translations
            source_lang: Source language code
            target_lang: Target language code
            batch_size: How many strings to translate in a single batch
            max_retries: Maximum number of retries for failed translations
        """
        self.llm_client = llm_client or get_llm_client()
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.batch_size = batch_size
        self.max_retries = max_retries
    
    def translate_file(self, input_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Translate a .ts file.
        
        Args:
            input_path: Path to the input .ts file
            output_path: Path to save the translated .ts file (or None to overwrite)
            
        Returns:
            Dictionary with translation statistics
        """
        logger.info(f"Starting translation of file: {input_path}")
        logger.info(f"Source language: {self.source_lang}")
        logger.info(f"Target language: {self.target_lang}")
        logger.info(f"Using batch size: {self.batch_size}")
        
        # Parse the file
        logger.info("Parsing input file...")
        parser = TSFileParser(input_path)
        parser.parse()
        
        # Get units that need translation
        untranslated_units = parser.get_untranslated_units()
        total_units = len(parser.translation_units)
        untranslated_count = len(untranslated_units)
        
        logger.info(f"Found {total_units} total translation units")
        logger.info(f"Found {untranslated_count} units needing translation")
        
        if untranslated_count == 0:
            logger.info("No translations needed, file is already fully translated")
            return {
                "total_units": total_units,
                "translated": 0,
                "skipped": 0,
                "errors": 0
            }
        
        # Create a mapping of unit indices to be translated
        unit_indices = {}
        for i, unit in enumerate(parser.translation_units):
            if unit in untranslated_units:
                unit_indices[untranslated_units.index(unit)] = i
        
        # Translate in batches
        translations = {}
        errors = 0
        
        # Process in batches
        batches = self._create_batches(untranslated_units, self.batch_size)
        total_batches = len(batches)
        logger.info(f"Split translation into {total_batches} batches")
        
        with tqdm(total=untranslated_count, desc="Translating") as pbar:
            for batch_idx, batch in enumerate(batches, 1):
                logger.info(f"Processing batch {batch_idx}/{total_batches}")
                logger.info(f"Batch size: {len(batch)} units")
                
                batch_translations = self._translate_batch(batch)
                
                # Map translated texts back to the original indices
                for i, text in enumerate(batch_translations):
                    if not text:  # If translation is empty, stop processing
                        logger.error(f"Empty translation received for text: {batch[i].source_text}")
                        logger.error("Stopping translation process due to error")
                        raise RuntimeError("Empty translation received")
                        
                    batch_idx = untranslated_units.index(batch[i])
                    original_idx = unit_indices[batch_idx]
                    translations[original_idx] = text
                    logger.debug(f"Translated: {batch[i].source_text} -> {text}")
                
                pbar.update(len(batch))
                logger.info(f"Completed batch {batch_idx}/{total_batches}")
        
        # Update the translations in the XML
        logger.info("Updating XML with translations...")
        parser.update_translations(translations)
        
        # Save the translated file
        logger.info(f"Saving translated file to: {output_path or input_path}")
        parser.save(output_path)
        
        logger.info(f"Translation completed successfully")
        logger.info(f"Total units processed: {total_units}")
        logger.info(f"Units translated: {len(translations)}")
        
        return {
            "total_units": total_units,
            "translated": len(translations),
            "skipped": untranslated_count - len(translations),
            "errors": errors
        }
    
    def _create_batches(self, items: List[Any], batch_size: int) -> List[List[Any]]:
        """Create batches of items.
        
        Args:
            items: List of items to batch
            batch_size: Size of each batch
            
        Returns:
            List of batches
        """
        return [items[i:i+batch_size] for i in range(0, len(items), batch_size)]
    
    def _translate_batch(self, units: List[TranslationUnit]) -> List[str]:
        """Translate a batch of translation units.
        
        Args:
            units: List of translation units to translate
            
        Returns:
            List of translated texts
        """
        # Create batch data
        batch_data = []
        for unit in units:
            item = {
                'text': unit.source_text,
                'context': self._build_context(unit)
            }
            batch_data.append(item)
            logger.debug(f"Preparing translation for: {unit.source_text}")
            logger.debug(f"Context: {self._build_context(unit)}")
        
        # Translate with retries
        translations = []
        retries = 0
        
        while retries < self.max_retries:
            logger.info(f"Translation attempt {retries + 1}/{self.max_retries}")
            translations = self.llm_client.batch_translate(
                batch_data, 
                self.source_lang, 
                self.target_lang
            )
            
            # Validate translations
            if not translations or any(not t for t in translations):
                logger.error("Received empty translation in batch")
                retries += 1
                if retries == self.max_retries:
                    logger.error(f"All {self.max_retries} translation attempts failed")
                    raise RuntimeError("Maximum retry attempts reached with empty translations")
                continue
            
            logger.info(f"Successfully translated batch of {len(translations)} units")
            break
        
        return translations
    
    @staticmethod
    def _build_context(unit: TranslationUnit) -> str:
        """Build context information for translation.
        
        Args:
            unit: Translation unit to build context for
            
        Returns:
            Context string
        """
        context_parts = []
        
        if unit.context_name:
            context_parts.append(f"UI component: {unit.context_name}")
        
        if unit.comment:
            context_parts.append(f"Description: {unit.comment}")
            
        if unit.location:
            context_parts.append(f"Location: {unit.location}")
            
        return "; ".join(context_parts) 