"""
Constants module for translation-related configuration.
"""

# Base translation file paths and patterns
BASE_TRANSLATIONS_DIR = "translations"
BASE_TRANSLATION_FILE = f"{BASE_TRANSLATIONS_DIR}/lookpilot_en.ts"
TRANSLATION_OUTPUT_PATTERN = f"{BASE_TRANSLATIONS_DIR}/lookpilot_{{lang}}.ts"

# General context for translations that describes the overall application/domain
GENERAL_TRANSLATION_CONTEXT = """
This is a desktop application called LookPilot that provides eye and head tracking functionality.
It is a professional software tool used for:
- Camera control and configuration
- Eye tracking and gaze estimation (estimates where the user is looking on the screen)
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

# Translation quality guidelines that are added to every translation prompt
TRANSLATION_GUIDELINES = """
- Maintain consistent terminology throughout the interface
- Preserve any technical terms or proper nouns
- Keep the same level of formality as the source text
- Ensure translations fit the UI context (length, formatting)
- Preserve any placeholders and special characters
- Maintain the same tone and style as the original
- Adapt to the target language's writing system and character set
- Follow the target language's grammar rules and sentence structure
- Use appropriate formality levels and honorifics for the target language
- Apply standard technical terminology conventions for the target language
- Respect the target language's punctuation and formatting rules
- Ensure proper character encoding and rendering
"""

# Maximum length for translations (characters) to prevent UI overflow
MAX_TRANSLATION_LENGTH = 300

# Batch processing configuration
DEFAULT_BATCH_SIZE = 1000000  # Default to processing all strings at once
MAX_BATCH_SIZE = 1000000
MIN_BATCH_SIZE = 1

# Flag to indicate if we're using single batch mode by default
DEFAULT_SINGLE_BATCH = True 