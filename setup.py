from setuptools import setup, find_packages
from setuptools.config.expand import entry_points

setup(
    name="llmgine",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "llmgine=src.programs.cli_router:app",
        ],
    },
)
