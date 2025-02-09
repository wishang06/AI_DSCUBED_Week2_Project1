from setuptools import setup, find_packages

setup(
    name="llmgine",
    version="0.1.0",
    package_dir={"": "src"},  # This tells setuptools that packages are under src/
    packages=find_packages(where="src"),  # This will find all packages
    entry_points={
        "console_scripts": [
            "llmgine=programs.cli_router:app",
        ],
    },
)
