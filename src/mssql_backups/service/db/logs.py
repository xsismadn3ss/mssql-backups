import typer

app = typer.Typer(help="Administrar logs", name="logs")


@app.command()
def reduce():
    """Reducir logs de la base de datos"""
    ...
