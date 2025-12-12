# setup.py configuration for pip install
from setuptools import setup, find_packages

with open("README.MD", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="udos",
    version="1.2.22",
    author="Fred Porter",
    author_email="fred@udos.dev",
    description="uDOS - Offline-first Operating System for Survival Knowledge",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fredporter/uDOS",
    project_urls={
        "Bug Tracker": "https://github.com/fredporter/uDOS/issues",
        "Documentation": "https://github.com/fredporter/uDOS/wiki",
        "Source Code": "https://github.com/fredporter/uDOS",
    },
    packages=find_packages(include=["udos", "udos.*", "core", "core.*", "extensions", "extensions.*"]),
    package_data={
        'core': ['data/**/*'],
        'knowledge': ['**/*.md'],
        'extensions': ['assets/**/*', 'core/**/*', 'assistant/**/*'],
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
        # Ultra-minimal (8MB) - Core only
        "ultra": [],
        
        # Lite (16MB) - Core + Knowledge (DEFAULT)
        "lite": [],
        
        # Standard (32MB) - Core + Knowledge + AI + Graphics
        "standard": [
            "google-generativeai>=0.3.0",  # OK Assistant
        ],
        
        # Full (64MB) - Complete offline system + gameplay
        "full": [
            "google-generativeai>=0.3.0",
            "pillow>=10.0.0",  # Image processing
        ],
        
        # Enterprise (128MB+) - Everything including cloud/BI
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
        
        # Development tools
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
        ],
        
        # Legacy AI option (same as standard)
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
    package_data={
        "": [
            "knowledge/**/*.json",
            "knowledge/**/*.md",
            "data/**/*",
            "extensions/**/*",
        ],
        "udos": ["py.typed"],
    },
    zip_safe=False,
)
