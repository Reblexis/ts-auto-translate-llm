from setuptools import setup, find_packages
import re

# Read version from package __init__.py
with open('ts_translator/__init__.py', 'r') as f:
    version = re.search(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read()).group(1)

# Read requirements from requirements.txt
with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f.readlines() if line.strip()]

setup(
    name="ts-auto-translate-llm",
    version=version,
    description="Automatic translation of Qt .ts files using LLM APIs",
    author="AI Developer",
    author_email="example@example.com",
    url="https://github.com/yourusername/ts-auto-translate-llm",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'ts-translator=ts_translator.cli:cli',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
) 