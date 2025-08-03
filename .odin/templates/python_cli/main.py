#!/usr/bin/env python3
"""
Main CLI application using Typer
"""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Python CLI template using Typer")
console = Console()


@app.command()
def hello(
    name: str = typer.Argument(..., help="Your name"),
    uppercase: bool = typer.Option(False, "--uppercase", "-u", help="Make output uppercase"),
) -> None:
    """
    Say hello to someone.
    """
    greeting = f"Hello {name}!"
    if uppercase:
        greeting = greeting.upper()
    
    console.print(greeting, style="bold green")


@app.command()
def list_items(
    count: int = typer.Option(5, "--count", "-c", help="Number of items to show")
) -> None:
    """
    Display a list of sample items.
    """
    table = Table(title="Sample Items")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Status", style="green")

    for i in range(1, count + 1):
        table.add_row(str(i), f"Item {i}", "Active")
    
    console.print(table)


@app.command()
def version() -> None:
    """
    Show version information.
    """
    console.print("Python CLI Template v1.0.0", style="bold blue")


if __name__ == "__main__":
    app()
