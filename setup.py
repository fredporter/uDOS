# setup.py configuration for pip install
from setuptools import setup, find_packages
import json
from pathlib import Path

# Use simple description if README not found
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "uDOS - Offline-first Operating System for Survival Knowledge"

try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [
            line.strip() for line in fh if line.strip() and not line.startswith("#")
        ]
except FileNotFoundError:
    requirements = []

# Read version from core/version.json
version_file = Path("core/version.json")
if version_file.exists():
    with open(version_file, "r") as f:
        version_data = json.load(f)
        version = version_data.get("version", "1.0.0.0")
else:
    version = "1.0.0.0"

setup(
    name="udos",
    version=version,
    author="Fred Porter",
    author_email="fred@udos.dev",
    description="uDOS - Offline-first Operating System for Survival Knowledge",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fredporter/uDOS-dev",
    project_urls={
        "Bug Tracker": "https://github.com/fredporter/uDOS-dev/issues",
        "Documentation": "https://github.com/fredporter/uDOS-dev/wiki",
        "Source Code": "https://github.com/fredporter/uDOS-dev",
    },
    packages=find_packages(include=["core", "core.*", "public", "public.*"]),
    package_data={
        "core": ["**/*.json", "**/*.md"],
        "public": ["**/*.json", "**/*.md"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Shells",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        # Ultra-minimal (~8MB) - Core only, no knowledge, no extensions
        "ultra": [],
        # Lite (~16MB) - Core + Knowledge (DEFAULT) - NO EXTENSIONS
        # Excludes: extensions/, dev/, wiki/, memory/
        # Perfect for: Offline survival, minimal installs, embedded systems
        "lite": [],
        # Standard (~28MB) - Core + Knowledge + AI + Essential Extensions
        # Includes: extensions/assistant/ (OK Assistant)
        # Requires: Gemini API key for AI features
        "standard": [
            "google-generativeai>=0.3.0",  # OK Assistant
        ],
        # Full (~58MB) - Complete system + Gameplay + Graphics
        # Includes: extensions/play/, extensions/assets/fonts/
        # Features: XP system, map engine, ASCII graphics, font rendering
        "full": [
            "google-generativeai>=0.3.0",
            "pillow>=10.0.0",  # Image processing for graphics
        ],
        # Enterprise (~120MB+) - Everything including Cloud + BIZINTEL
        # Includes: extensions/cloud/, extensions/cloud/bizintel/
        # Features: Group sharing, tunneling, business intelligence, entity resolution
        "enterprise": [
            "google-generativeai>=0.3.0",
            "pillow>=10.0.0",
            "google-auth>=2.0.0",
            "google-auth-oauthlib>=1.0.0",
            "google-auth-httplib2>=0.1.0",
            "google-api-python-client>=2.0.0",
            "sqlalchemy>=2.0.0",  # BIZINTEL database
            "fuzzywuzzy>=0.18.0",  # Entity resolution
            "python-Levenshtein>=0.21.0",  # Fuzzy matching speedup
        ],
        # Development tools (not included in any tier)
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
        ],
        # Legacy AI option (alias for standard)
        "ai": [
            "google-generativeai>=0.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "udos=core.uDOS_main:main",
        ],
    },
    scripts=[
        "bin/udos",
    ],
    include_package_data=True,
    zip_safe=False,
)
