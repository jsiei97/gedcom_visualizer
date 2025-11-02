"""Setup script for GEDCOM Visualizer package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="gedcom-visualizer",
    version="0.1.0",
    description="Tools for parsing and visualizing GEDCOM genealogy files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="GEDCOM Visualizer Contributors",
    url="https://github.com/jsiei97/gedcom_visualizer",
    packages=find_packages(),
    install_requires=[
        "python-gedcom>=1.0.0",
        "sphinx>=7.0.0",
        "sphinx-rtd-theme>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "gedcom-list=gedcom_visualizer.list_search:main",
            "gedcom-generate=gedcom_visualizer.generate_asciidoc:main",
            "gedcom-convert=gedcom_visualizer.convert_to_pdf:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Sociology :: Genealogy",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
)
