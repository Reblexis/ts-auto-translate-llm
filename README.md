# TS-Auto-Translate-LLM

Automatic translation of Qt .ts files using LLM APIs.

## Overview

TS-Auto-Translate-LLM is a Python tool that uses Large Language Models (LLMs) to automatically translate Qt linguist (.ts) files. It leverages the capabilities of modern LLMs like GPT and Claude to provide high-quality translations for software localization.

## Features

- Translate any Qt .ts file to the target language
- Supports multiple LLM providers (OpenAI, Anthropic, etc.)
- Batch translate multiple files at once
- Configurable via command-line options, environment variables, or config files
- Progress tracking and detailed logging
- Preserves .ts file structure and metadata

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

You can configure TS-Auto-Translate-LLM in several ways:

### Environment Variables

```bash
# Required for OpenAI
export OPENAI_API_KEY=your_api_key

# Required for Anthropic
export ANTHROPIC_API_KEY=your_api_key

# Optional configuration
export TS_TRANSLATOR_SOURCE_LANG=en_US
export TS_TRANSLATOR_TARGET_LANG=es_ES
export TS_TRANSLATOR_LLM_PROVIDER=openai
export TS_TRANSLATOR_LLM_MODEL=gpt-3.5-turbo
export TS_TRANSLATOR_BATCH_SIZE=10
```

### Configuration File

Create a configuration file with the `init` command:

```bash
ts-translator init --target-lang fr_FR --provider openai --model gpt-4
```

This will create a configuration file at `~/.ts_translator_config.json` by default, which you can specify when running the tool:

```bash
ts-translator --config ~/.ts_translator_config.json translate my_file.ts
```

## Usage

### Single File Translation

```bash
# Basic usage
ts-translator translate path/to/input.ts

# Specify output path
ts-translator translate path/to/input.ts --output path/to/output.ts

# Specify target language
ts-translator translate path/to/input.ts --target-lang fr_FR

# Specify LLM provider and model
ts-translator translate path/to/input.ts --provider anthropic --model claude-3-sonnet-20240229
```

### Batch Translation

```bash
# Translate all .ts files in a directory
ts-translator batch path/to/directory

# Translate recursively
ts-translator batch path/to/directory --recursive

# Save to a different output directory
ts-translator batch path/to/directory --output-dir path/to/output/directory
```

## Example .ts File Format

The tool handles the standard Qt .ts file format. For example:

```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="en_US">
  <context>
    <name>AboutTab</name>
    <message>
      <location filename="../src/clearsight/ui/main_menu/about_tab.py" line="26" />
      <source>About LookPilot</source>
      <comment>Title of the About section</comment>
      <translation type="unfinished" />
    </message>
    <!-- More messages -->
  </context>
  <!-- More contexts -->
</TS>
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details. 