# TS-Auto-Translate-LLM

Automatic translation of Qt .ts files using LLM APIs.

## Overview

TS-Auto-Translate-LLM is a Python tool that uses Large Language Models (LLMs) to automatically translate Qt linguist (.ts) files. It leverages the capabilities of modern LLMs like GPT-4.1-mini to provide high-quality translations for software localization to any language.

## Features

- Universal language support - translate to any language using ISO language codes
- Uses GPT-4.1-mini by default for high-quality translations
- Translates all strings in a single batch by default for consistency
- Supports multiple LLM providers (OpenAI, Anthropic)
- Preserves .ts file structure and metadata
- Detailed logging and progress tracking

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ts-auto-translate-llm.git
cd ts-auto-translate-llm

# Install the package
pip install -e .

# Or install directly from PyPI
pip install ts-auto-translate-llm
```

## Configuration

Configure TS-Auto-Translate-LLM using environment variables:

```bash
# Required for OpenAI (default provider)
export OPENAI_API_KEY=your_api_key

# Optional: for using Anthropic
export ANTHROPIC_API_KEY=your_api_key
```

## Usage

The tool expects the English source file to be at `translations/lookpilot_en.ts` and will generate translated files following the pattern `translations/lookpilot_LANG.ts`.

### Basic Usage

```bash
# Use simple language codes
ts-translator translate ja     # Japanese
ts-translator translate ko     # Korean
ts-translator translate ar     # Arabic
ts-translator translate hi     # Hindi

# Or use full language-region codes
ts-translator translate pt_BR  # Brazilian Portuguese
ts-translator translate zh_CN  # Simplified Chinese
ts-translator translate zh_TW  # Traditional Chinese
ts-translator translate en_GB  # British English
```

### Advanced Options

```bash
# Enable debug logging
ts-translator --debug translate ja

# Use a different LLM provider
ts-translator translate ko --provider anthropic

# Use a specific model
ts-translator translate ar --model claude-3-sonnet-20240229

# Use multi-batch mode instead of single batch (for memory-constrained environments)
ts-translator translate hi --multi-batch

# Use multi-batch mode with custom batch size
ts-translator translate zh_CN --multi-batch --batch-size 20
```

### Language Support

The tool supports translation to any language using standard language codes:
- Simple codes: `de`, `fr`, `ja`, `ko`, `zh`, etc.
- Full codes: `de_DE`, `fr_FR`, `pt_BR`, `zh_CN`, etc.

The LLM will automatically adapt to the target language's:
- Writing system and character set
- Grammar rules and sentence structure
- Formality levels and honorifics
- Technical terminology conventions

## Translation Features

- Intelligent adaptation to target language characteristics
- Preserves formatting and special characters
- Maintains consistent terminology
- Handles technical terms appropriately
- Ensures proper character encoding
- Validates translations for completeness and correctness
- Respects language-specific formatting conventions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details. 