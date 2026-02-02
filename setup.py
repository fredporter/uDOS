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
        # ============================================================
        # ENVIRONMENT PROFILES
        # ============================================================

        # Ultra-minimal (~8MB) - Core TUI only, no Wizard Server
        # Perfect for: Offline survival mode, embedded systems, minimal install
        "ultra": [],

        # Lite (~16MB) - Core TUI + Knowledge (DEFAULT)
        # Perfect for: Offline survival, no cloud features
        "lite": [],

        # Wizard Server (~45MB) - Core + Wizard APIs for cloud/local network
        # Needed if you want: Dashboard, APIs, OAuth, Gmail relay, GitHub integration
        "wizard": [
            "fastapi>=0.109.0",
            "uvicorn>=0.27.0",
            "python-multipart>=0.0.6",
            "qrcode>=7.4.2",
            "flask>=2.0.0",
            "flask-cors>=5.0.0",
            "flask-socketio>=5.0.0",
            "simple-websocket>=1.0.0",
            "aiohttp>=3.9.0",
            "hypercorn>=0.17.0",
            "markdown2>=2.4.0",
            "pygments>=2.10.0",
        ],

        # Standard (~28MB) - Core + Wizard + AI
        # Includes: Gemini API support for OK Assistant
        "standard": [
            "google-generativeai>=0.3.0",
            "fastapi>=0.109.0",
            "uvicorn>=0.27.0",
            "python-multipart>=0.0.6",
            "qrcode>=7.4.2",
            "flask>=2.0.0",
            "flask-cors>=5.0.0",
            "flask-socketio>=5.0.0",
            "simple-websocket>=1.0.0",
            "aiohttp>=3.9.0",
            "hypercorn>=0.17.0",
            "markdown2>=2.4.0",
            "pygments>=2.10.0",
        ],

        # Full (~58MB) - Complete system + Gameplay + Graphics
        # Includes: extensions/play/, extensions/assets/fonts/
        # Features: XP system, map engine, ASCII graphics, font rendering
        "full": [
            "google-generativeai>=0.3.0",
            "pillow>=10.0.0",
            "fastapi>=0.109.0",
            "uvicorn>=0.27.0",
            "python-multipart>=0.0.6",
            "qrcode>=7.4.2",
            "flask>=2.0.0",
            "flask-cors>=5.0.0",
            "flask-socketio>=5.0.0",
            "simple-websocket>=1.0.0",
            "aiohttp>=3.9.0",
            "hypercorn>=0.17.0",
            "markdown2>=2.4.0",
            "pygments>=2.10.0",
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
            "sqlalchemy>=2.0.0",
            "fuzzywuzzy>=0.18.0",
            "python-Levenshtein>=0.21.0",
            "fastapi>=0.109.0",
            "uvicorn>=0.27.0",
            "python-multipart>=0.0.6",
            "qrcode>=7.4.2",
            "flask>=2.0.0",
            "flask-cors>=5.0.0",
            "flask-socketio>=5.0.0",
            "simple-websocket>=1.0.0",
            "aiohttp>=3.9.0",
            "hypercorn>=0.17.0",
            "markdown2>=2.4.0",
            "pygments>=2.10.0",
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
