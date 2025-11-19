# setup.py configuration for pip install
from setuptools import setup, find_packages

with open("README.MD", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="udos",
    version="1.0.27",
    author="Fred Porter",
    author_email="fred@udos.dev",
    description="uDOS - Smart Commands & Interactive System for Offline Survival",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fredporter/uDOS",
    project_urls={
        "Bug Tracker": "https://github.com/fredporter/uDOS/issues",
        "Documentation": "https://github.com/fredporter/uDOS/wiki",
        "Source Code": "https://github.com/fredporter/uDOS",
    },
    packages=find_packages(include=["core", "core.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
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
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
        ],
        "ai": [
            "google-generativeai>=0.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "udos=core.uDOS_main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": [
            "knowledge/**/*.json",
            "knowledge/**/*.md",
            "data/**/*",
            "extensions/**/*",
        ],
    },
    zip_safe=False,
)
