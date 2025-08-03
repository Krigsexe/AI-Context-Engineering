#!/usr/bin/env python3
"""
ODIN v6.0 - Autonomous AI Codebase Assistant
Setup configuration for pip installation
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "ODIN v6.0 - Autonomous AI Codebase Assistant"

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="odin-ai",
    version="6.0.0",
    description="ODIN v6.0 - Autonomous AI Codebase Assistant (Complete Edition)",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Make With Passion by Krigs",
    author_email="contact@makewithpassion.dev",
    url="https://github.com/Krigsexe/AI-Context-Engineering",
    license="MIT",
    packages=find_packages(exclude=['tests*', 'docs*']),
    include_package_data=True,
    package_data={
        'odin': [
            'schemas/*.json',
            'templates/*',
            'plugins/*',
        ],
    },
    install_requires=read_requirements(),
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'odin=odin.__main__:main',
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: System :: Systems Administration",
    ],
    keywords="ai assistant codebase automation development cli",
    project_urls={
        "Bug Reports": "https://github.com/Krigsexe/AI-Context-Engineering/issues",
        "Source": "https://github.com/Krigsexe/AI-Context-Engineering",
        "Documentation": "https://odin-ai.dev/docs",
    },
)
