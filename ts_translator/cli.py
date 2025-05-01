"""
Command-line interface for TS Translator.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Optional
import click
import re

from ts_translator.config import TranslatorConfig, setup_logging
from ts_translator.translator import TSTranslator
from ts_translator.llm_client import get_llm_client
from ts_translator.constants import (
    BASE_TRANSLATION_FILE,
    TRANSLATION_OUTPUT_PATTERN,
    DEFAULT_BATCH_SIZE
)

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.ts_translator_config.json")


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--config", "-c", default=None, help="Path to config file")
@click.pass_context
def cli(ctx, debug: bool, config: Optional[str]):
    """TS-Auto-Translate: Translate Qt .ts files using LLMs."""
    # Set up logging
    setup_logging(level=logging.DEBUG if debug else logging.INFO)
    logger.info("Starting TS-Auto-Translate")
    
    # Initialize config
    logger.info("Loading configuration...")
    if config and os.path.exists(config):
        logger.info(f"Loading config from file: {config}")
        translator_config = TranslatorConfig.from_file(config)
        logger.debug(f"Loaded config from {config}")
    else:
        logger.info("Using environment variables for configuration")
        translator_config = TranslatorConfig.from_env()
    
    ctx.ensure_object(dict)
    ctx.obj["config"] = translator_config
    logger.debug(f"Configuration loaded: {translator_config.to_dict()}")


@cli.command()
@click.argument("lang_code")
@click.option("--provider", "-p", help="LLM provider to use")
@click.option("--model", "-m", help="LLM model to use")
@click.option("--batch-size", "-b", type=int, help="Batch size for multi-batch mode")
@click.option("--multi-batch", is_flag=True, help="Use multiple smaller batches instead of single large batch")
@click.pass_context
def translate(
    ctx, 
    lang_code: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    batch_size: Optional[int] = None,
    multi_batch: bool = False
):
    """Translate the base English file to the specified language code (e.g. 'de' or 'de_DE')."""
    logger.info("Starting translation command")
    config: TranslatorConfig = ctx.obj["config"]
    
    # Validate base translation file exists
    if not os.path.exists(BASE_TRANSLATION_FILE):
        logger.error(f"Base translation file not found: {BASE_TRANSLATION_FILE}")
        raise click.FileError(BASE_TRANSLATION_FILE, hint="Base English translation file not found")
    
    # Process language code
    target_lang = lang_code.lower()
    if "_" not in target_lang:
        # Convert 'de' to 'de_DE' format
        target_lang = f"{target_lang}_{target_lang.upper()}"
    
    # Generate output path
    output = TRANSLATION_OUTPUT_PATTERN.format(lang=lang_code.lower())
    
    # Update config with command-line options
    update_dict = {
        "source_lang": "en_US",  # Always English source
        "target_lang": target_lang
    }
    
    if provider:
        update_dict["llm_provider"] = provider
    if model:
        update_dict["llm_model"] = model
    
    # Handle batch size configuration
    if multi_batch:
        logger.info("Multi-batch mode enabled")
        if batch_size:
            update_dict["batch_size"] = batch_size
            logger.info(f"Using specified batch size: {batch_size}")
        else:
            update_dict["batch_size"] = 10  # Default small batch size
            logger.info("Using default small batch size: 10")
    else:
        # Use single large batch (default behavior)
        update_dict["batch_size"] = DEFAULT_BATCH_SIZE
        logger.info("Using single batch mode (default)")
    
    logger.info("Updating configuration with command-line options")
    logger.debug(f"Updates: {update_dict}")
    config = config.update(**update_dict)
    
    logger.info(f"Input file: {BASE_TRANSLATION_FILE}")
    logger.info(f"Output file: {output}")
    logger.info(f"Source language: {config.source_lang}")
    logger.info(f"Target language: {config.target_lang}")
    logger.info(f"Using provider: {config.llm_provider}")
    logger.info(f"Using model: {config.llm_model or 'default'}")
    logger.info(f"Batch size: {config.batch_size}")
    
    # Create LLM client
    logger.info("Initializing LLM client")
    llm_client = get_llm_client(
        provider=config.llm_provider,
        model_name=config.llm_model,
        temperature=config.temperature
    )
    
    # Create translator
    logger.info("Creating translator instance")
    translator = TSTranslator(
        llm_client=llm_client,
        source_lang=config.source_lang,
        target_lang=config.target_lang,
        batch_size=config.batch_size,
        max_retries=config.max_retries
    )
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    # Translate file
    logger.info("Starting translation process")
    results = translator.translate_file(BASE_TRANSLATION_FILE, output)
    
    # Print results
    logger.info("Translation completed")
    logger.info(f"Total units: {results['total_units']}")
    logger.info(f"Translated: {results['translated']}")
    logger.info(f"Skipped: {results['skipped']}")
    logger.info(f"Errors: {results['errors']}")
    logger.info(f"Output saved to: {output}")
    
    if results['errors'] > 0:
        logger.error(f"Translation completed with {results['errors']} errors")
        sys.exit(1)
    
    click.echo(f"Translation completed successfully!")
    click.echo(f"Total units: {results['total_units']}")
    click.echo(f"Translated: {results['translated']}")
    click.echo(f"Skipped: {results['skipped']}")
    click.echo(f"Errors: {results['errors']}")
    click.echo(f"Output saved to: {output}")


@cli.command()
@click.option("--output", "-o", default=DEFAULT_CONFIG_PATH, help="Output path for config file")
@click.option("--target-lang", "-t", required=True, help="Target language code")
@click.option("--source-lang", "-s", default="en_US", help="Source language code")
@click.option("--provider", "-p", default="openai", help="LLM provider to use")
@click.option("--model", "-m", help="LLM model to use")
@click.option("--temperature", type=float, default=0.3, help="Temperature for generation")
@click.option("--batch-size", "-b", type=int, default=10, help="Batch size for translations")
@click.option("--max-retries", type=int, default=3, help="Max retries for failed translations")
@click.option("--output-suffix", default="_translated", help="Suffix for output files")
@click.pass_context
def init(
    ctx,
    output: str,
    target_lang: str,
    source_lang: str,
    provider: str,
    model: Optional[str],
    temperature: float,
    batch_size: int,
    max_retries: int,
    output_suffix: str
):
    """Initialize a configuration file."""
    logger.info("Initializing new configuration")
    logger.info(f"Output path: {output}")
    logger.info(f"Source language: {source_lang}")
    logger.info(f"Target language: {target_lang}")
    logger.info(f"Provider: {provider}")
    logger.info(f"Model: {model or 'default'}")
    logger.info(f"Temperature: {temperature}")
    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Max retries: {max_retries}")
    logger.info(f"Output suffix: {output_suffix}")
    
    # Create config
    config = TranslatorConfig(
        source_lang=source_lang,
        target_lang=target_lang,
        llm_provider=provider,
        llm_model=model,
        temperature=temperature,
        batch_size=batch_size,
        max_retries=max_retries,
        output_suffix=output_suffix
    )
    
    # Save config to file
    logger.info(f"Saving configuration to: {output}")
    config.to_file(output)
    logger.info("Configuration saved successfully")
    click.echo(f"Configuration saved to {output}")


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True))
@click.option("--output-dir", "-o", help="Output directory (default: input directory)")
@click.option("--recursive", "-r", is_flag=True, help="Search recursively in input directory")
@click.option("--target-lang", "-t", help="Target language code")
@click.pass_context
def batch(
    ctx,
    input_dir: str,
    output_dir: Optional[str] = None,
    recursive: bool = False,
    target_lang: Optional[str] = None
):
    """Translate all .ts files in a directory."""
    logger.info("Starting batch translation")
    config: TranslatorConfig = ctx.obj["config"]
    
    # Update config if target language is specified
    if target_lang:
        logger.info(f"Updating target language to: {target_lang}")
        config = config.update(target_lang=target_lang)
    
    # Determine output directory
    if not output_dir:
        output_dir = input_dir
    
    logger.info(f"Input directory: {input_dir}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Recursive search: {recursive}")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all .ts files
    input_path = Path(input_dir)
    pattern = "**/*.ts" if recursive else "*.ts"
    ts_files = list(input_path.glob(pattern))
    
    if not ts_files:
        logger.warning("No .ts files found in the specified directory")
        click.echo("No .ts files found in the specified directory.")
        return
    
    logger.info(f"Found {len(ts_files)} .ts files to translate")
    
    # Create LLM client
    logger.info("Initializing LLM client")
    llm_client = get_llm_client(
        provider=config.llm_provider,
        model_name=config.llm_model,
        temperature=config.temperature
    )
    
    # Create translator
    logger.info("Creating translator instance")
    translator = TSTranslator(
        llm_client=llm_client,
        source_lang=config.source_lang,
        target_lang=config.target_lang,
        batch_size=config.batch_size,
        max_retries=config.max_retries
    )
    
    # Translate each file
    total_translated = 0
    total_units = 0
    total_errors = 0
    
    for ts_file in ts_files:
        rel_path = ts_file.relative_to(input_path)
        output_file = Path(output_dir) / rel_path.with_name(f"{ts_file.stem}{config.output_suffix}{ts_file.suffix}")
        
        # Ensure output directory exists
        os.makedirs(output_file.parent, exist_ok=True)
        
        logger.info(f"Processing file: {ts_file}")
        logger.info(f"Output file: {output_file}")
        
        results = translator.translate_file(str(ts_file), str(output_file))
        
        total_translated += results["translated"]
        total_units += results["total_units"]
        total_errors += results["errors"]
        
        logger.info(f"File results - Translated: {results['translated']}, Total: {results['total_units']}, Errors: {results['errors']}")
        click.echo(f"  - Translated {results['translated']} of {results['total_units']} units")
    
    logger.info("Batch translation completed")
    logger.info(f"Total files processed: {len(ts_files)}")
    logger.info(f"Total units: {total_units}")
    logger.info(f"Total translated: {total_translated}")
    logger.info(f"Total errors: {total_errors}")
    
    if total_errors > 0:
        logger.error(f"Batch translation completed with {total_errors} errors")
        sys.exit(1)
    
    click.echo("\nBatch translation completed!")
    click.echo(f"Total files: {len(ts_files)}")
    click.echo(f"Total units: {total_units}")
    click.echo(f"Total translated: {total_translated}")
    click.echo(f"Total errors: {total_errors}")


if __name__ == "__main__":
    cli(obj={}) 