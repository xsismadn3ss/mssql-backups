from typing import Iterable

import readchar
from rich import box
from rich.console import Console
from rich.panel import Panel


def selector(options: list[str], title: str = "Opciones"):
    console = Console()

    if not options:
        return

    selected = None
    index = 0

    while True:
        console.clear()
        console.print(f"[bold]{title}[/]\n")
        console.print(
            Panel("Usa ⬆️ ⬇️ para navegar y ENTER para seleccionar", box=box.ROUNDED)
        )

        for i, option in enumerate(options):
            if index == i:
                console.print(f"[bold]|>[/] [bold cyan]{option}[/]")
            else:
                console.print(option)

        key = readchar.readkey()
        match key:
            case readchar.key.UP:
                index = (index - 1) % len(options)
            case readchar.key.DOWN:
                index = (index + 1) % len(options)
            case readchar.key.ESC:
                return None
            case readchar.key.ENTER:
                console.print(f"[bold green]Seleccionado: {options[index]}[/]")
                selected = options[index]
                return selected


def space_selector(options: list[str], title: str = "Opciones") -> Iterable[str]:
    console = Console()

    if not options:
        return []

    index = 0
    selected_options = set()

    while True:
        console.clear()
        console.print(f"[bold]{title}[/]\n")
        console.print(
            Panel(
                "Usa ⬆️ ⬇️ para navegar, espacio para seleccionar opciones y enter para confirmar",
                box=box.ROUNDED,
            )
        )

        for i, option in enumerate(options):
            checkbox = "(•)" if i in selected_options else "()"

            if index == i:
                console.print(f"[bold cyan]{checkbox} {option}[/]")
            else:
                console.print(f"{checkbox} {option}")

        key = readchar.readkey()
        match key:
            case readchar.key.UP:
                index = (index - 1) % len(options)
            case readchar.key.DOWN:
                index = (index + 1) % len(options)

            case readchar.key.SPACE:
                if index in selected_options:
                    selected_options.remove(index)
                else:
                    selected_options.add(index)

            case readchar.key.ESC:
                return []

            case readchar.key.ENTER:
                return [options[i] for i in selected_options]
