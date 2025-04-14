"""
Constants module for translation-related configuration.
"""

# General context for translations that describes the overall application/domain
GENERAL_TRANSLATION_CONTEXT = """
This is a desktop application called LookPilot that provides eye and head tracking functionality.
It is a professional software tool used for:
- Camera control and configuration
- Eye tracking and gaze estimation
- Head tracking for gaming and accessibility
- User interface customization and settings
- System feedback and diagnostics

The application has a modern GUI with multiple tabs/sections including:
- Camera settings and configuration
- Gaze estimation and calibration
- Gaming features and controls
- Interface customization
- User feedback and bug reporting
"""

# Language-specific context that can be added for particular target languages
LANGUAGE_SPECIFIC_CONTEXT = {
    "de_DE": """
    German translation should use formal 'Sie' form for user instructions and messages.
    Technical terms should use standard German computing/software terminology.
    Maintain consistent capitalization for nouns as per German grammar rules.
    """,
    "es_ES": """
    Spanish translation should use neutral Latin American Spanish.
    Use formal 'usted' form for user instructions and messages.
    Technical terms should be consistently translated across the interface.
    """,
    "fr_FR": """
    French translation should use formal 'vous' form for user instructions and messages.
    Follow French punctuation rules (spaces before/after punctuation marks).
    Use standard French computing terminology for technical terms.
    """
}

# Translation quality guidelines that are added to every translation prompt
TRANSLATION_GUIDELINES = """
- Maintain consistent terminology throughout the interface
- Preserve any technical terms or proper nouns
- Keep the same level of formality as the source text
- Ensure translations fit the UI context (length, formatting)
- Preserve any placeholders or special characters
- Maintain the same tone and style as the original
"""

# Special terms that should be consistently translated
GLOSSARY = {
    "de_DE": {
        "eye tracking": "Eye-Tracking",
        "head tracking": "Head-Tracking",
        "calibration": "Kalibrierung",
        "gaze estimation": "Blickerfassung",
        "virtual camera": "virtuelle Kamera",
        "settings": "Einstellungen",
        "feedback": "Feedback",
        "bug report": "Fehlerbericht"
    }
}

# Maximum length for translations (characters) to prevent UI overflow
MAX_TRANSLATION_LENGTH = 300

# Batch processing configuration
DEFAULT_BATCH_SIZE = 10
MAX_BATCH_SIZE = 50
MIN_BATCH_SIZE = 1 