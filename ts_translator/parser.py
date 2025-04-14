"""
Parser module for Qt .ts XML files.
"""

import logging
from lxml import etree
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TranslationUnit:
    """Represents a single translation unit from a .ts file."""
    context_name: str
    source_text: str
    comment: Optional[str]
    location: Optional[str]
    translation: Optional[str]
    translation_type: Optional[str]
    xml_element: etree._Element  # Reference to original XML element


class TSFileParser:
    """Parser for Qt .ts XML translation files."""
    
    def __init__(self, file_path: str):
        """Initialize the parser with a .ts file path.
        
        Args:
            file_path: Path to the .ts file to parse
        """
        self.file_path = file_path
        self.tree = None
        self.root = None
        self.translation_units: List[TranslationUnit] = []
        
    def parse(self) -> List[TranslationUnit]:
        """Parse the .ts file and extract all translatable content.
        
        Returns:
            List of TranslationUnit objects
        """
        try:
            self.tree = etree.parse(self.file_path)
            self.root = self.tree.getroot()
            self._extract_translation_units()
            return self.translation_units
        except Exception as e:
            logger.error(f"Error parsing TS file: {e}")
            raise
    
    def _extract_translation_units(self) -> None:
        """Extract all translation units from the parsed XML."""
        contexts = self.root.findall(".//context")
        
        for context in contexts:
            context_name = context.find("name").text
            messages = context.findall("message")
            
            for message in messages:
                source_elem = message.find("source")
                translation_elem = message.find("translation")
                comment_elem = message.find("comment")
                location_elem = message.find("location")
                
                source_text = source_elem.text if source_elem is not None and source_elem.text else ""
                
                # Extract translation if it exists
                translation = None
                translation_type = None
                if translation_elem is not None:
                    translation = translation_elem.text
                    translation_type = translation_elem.get("type")
                
                # Extract comment if it exists
                comment = None
                if comment_elem is not None and comment_elem.text:
                    comment = comment_elem.text
                
                # Extract location if it exists
                location = None
                if location_elem is not None:
                    filename = location_elem.get("filename", "")
                    line = location_elem.get("line", "")
                    location = f"{filename}:{line}" if filename and line else filename
                
                translation_unit = TranslationUnit(
                    context_name=context_name,
                    source_text=source_text,
                    comment=comment,
                    location=location,
                    translation=translation,
                    translation_type=translation_type,
                    xml_element=message
                )
                
                self.translation_units.append(translation_unit)
    
    def get_untranslated_units(self) -> List[TranslationUnit]:
        """Get only the translation units that need translation.
        
        Returns:
            List of untranslated TranslationUnit objects
        """
        return [
            unit for unit in self.translation_units
            if unit.translation is None 
            or unit.translation_type == "unfinished" 
            or not unit.translation
        ]

    def update_translations(self, translations: Dict[int, str]) -> None:
        """Update the XML tree with new translations.
        
        Args:
            translations: Dictionary mapping translation unit indices to translated text
        """
        for idx, translation_text in translations.items():
            if 0 <= idx < len(self.translation_units):
                unit = self.translation_units[idx]
                message_elem = unit.xml_element
                
                translation_elem = message_elem.find("translation")
                if translation_elem is None:
                    translation_elem = etree.SubElement(message_elem, "translation")
                
                translation_elem.text = translation_text
                
                # Remove the 'type' attribute if it was 'unfinished'
                if translation_elem.get("type") == "unfinished":
                    translation_elem.attrib.pop("type")
    
    def save(self, output_path: Optional[str] = None) -> None:
        """Save the updated XML tree to a file.
        
        Args:
            output_path: Path to save the file to. If None, overwrites the input file.
        """
        if self.tree is None:
            raise ValueError("No tree to save. Call parse() first.")
        
        path = output_path or self.file_path
        
        # Add XML declaration and doctype
        with open(path, 'wb') as f:
            f.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
            f.write(b'<!DOCTYPE TS>\n')
            self.tree.write(f, encoding="utf-8", pretty_print=True) 