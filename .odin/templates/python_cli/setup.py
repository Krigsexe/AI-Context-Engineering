from setuptools import setup, find_packages

setup(
    name="python-cli-template",
    version="1.0.0",
    description="Python CLI template using Typer",
    author="ODIN v6.0",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "typer[all]>=0.9.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "mycli=main:app",
        ],
    },
    python_requires=">=3.8",
)
